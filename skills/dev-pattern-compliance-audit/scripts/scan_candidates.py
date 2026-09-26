#!/usr/bin/env python3
"""Regex-based lead scanner for the pattern-compliance-audit skill (v1.1).

Prints an inventory of *leads* -- places where a GoF / Fowler (PEAA) pattern, or a violation of one, is
plausible. It cannot tell a legitimate `switch` from a missing Strategy; every lead must be confirmed by
reading the code before it is reported as a finding.

Stdlib only. Primary support: Java, Kotlin, TypeScript/JavaScript (incl. TSX), Python.
Improved heuristics for NestJS, Prisma, FastAPI, Django, React.

Usage:
    scan_candidates.py <path> [--format md|json] [--exclude GLOB ...] [--max N] [--include-tests]
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from collections import Counter, defaultdict

EXTS = {".java", ".kt", ".ts", ".tsx", ".js", ".jsx", ".py"}
SKIP_DIRS = {
    ".git", "node_modules", "build", "target", "dist", "out", ".gradle", ".idea", "__pycache__",
    ".venv", "venv", ".next", "coverage", ".mypy_cache", ".pytest_cache", "generated",
    ".turbo", ".nuxt", "vendor", "Pods",
}
JVM = {".java", ".kt"}
JS = {".ts", ".tsx", ".js", ".jsx"}
PY = {".py"}

ROLE_SUFFIXES = [
    "Controller", "RestController", "Resource", "Service", "UseCase", "Handler", "Repository", "Dao", "DAO",
    "Mapper", "Assembler", "Converter", "Factory", "Builder", "Strategy", "Adapter", "Decorator", "Proxy",
    "Facade", "Gateway", "Client", "Provider", "Visitor", "Listener", "Observer", "Command", "Interceptor",
    "Filter", "Manager", "Registry", "Helper", "Util", "Utils", "Dto", "DTO", "Request", "Response",
    "Entity", "Config", "Configuration", "Properties", "Exception", "Validator", "Executor",
    "Runner", "Store", "Cache", "Template", "State", "Context", "Module", "Guard", "Pipe", "Middleware",
    "Resolver", "Interactor", "Presenter", "ViewModel",
]

CLASS_DECL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private|abstract|final|static|sealed|open|data)\s+)*"
    r"(class|interface|enum|record|object)\s+([A-Z]\w*)"
)
METHOD_DECL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private|static|final|abstract|synchronized|default)\s+)*"
    r"(?:<[^>]+>\s+)?[\w<>\[\],.? ]+?\s+(\w+)\s*\(([^)]*)\)\s*(?:throws [\w., ]+)?\s*\{"
)
KT_FUN = re.compile(
    r"^\s*(?:(?:public|private|protected|internal|override|open|suspend)\s+)*fun\s+(?:<[^>]+>\s+)?(\w+)\s*\(([^)]*)\)")
# TypeScript / JS class or function-ish
TS_CLASS = re.compile(r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+([A-Z]\w*)")
TS_FUNC = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(")
# Python
PY_CLASS = re.compile(r"^\s*class\s+(\w+)\s*[\(:]")
PY_DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(")


def is_test(path: str) -> bool:
    p = path.replace("\\", "/")
    name = os.path.basename(p)
    return (
            "/test/" in p or "/tests/" in p or "/__tests__/" in p or "/src/test" in p
            or name.endswith(("Test.java", "Tests.java", "IT.java", "Test.kt", ".test.ts", ".test.tsx",
                              ".spec.ts", ".spec.tsx", ".test.js", ".spec.js"))
            or name.startswith("test_") or name.endswith("_test.py") or name.endswith("_spec.py")
    )


def walk(root: str, excludes: list[str]):
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if os.path.splitext(fn)[1] not in EXTS:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root if os.path.isdir(root) else os.path.dirname(root))
            if any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(fn, g) for g in excludes):
                continue
            yield full


def read_lines(path: str) -> list[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def split_params(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


class Scan:
    def __init__(self, root: str, max_items: int):
        self.root = root
        self.max = max_items
        self.base = root if os.path.isdir(root) else os.path.dirname(root)
        self.leads: dict[str, dict] = {}
        self.stats: dict[str, object] = {}

    def add(self, check: str, hint: str, path: str, line: int, note: str = ""):
        entry = self.leads.setdefault(check, {"hint": hint, "items": []})
        if len(entry["items"]) >= self.max:
            return
        entry["items"].append({"file": os.path.relpath(path, self.base), "line": line, "note": note})


def estimate_complexity(lines: list[str], start: int, max_look: int = 120) -> int:
    """Very rough cyclomatic-ish score: branches + loops."""
    score = 1
    depth = 0
    for j in range(start - 1, min(len(lines), start - 1 + max_look)):
        cur = lines[j]
        depth += cur.count("{") - cur.count("}")
        if depth < 0:
            break
        score += len(re.findall(r"\b(if|else if|elif|case|for|while|catch|&&|\|\|)\b", cur))
        if depth == 0 and j > start:
            break
    return score


def scan(root: str, excludes: list[str], include_tests: bool, max_items: int) -> Scan:
    sc = Scan(root, max_items)
    files_by_ext: Counter = Counter()
    test_files = main_files = 0
    role_counts: Counter = Counter()
    role_examples: dict[str, list[str]] = defaultdict(list)
    interfaces: dict[str, tuple[str, int]] = {}
    impl_counts: Counter = Counter()
    test_impl_counts: Counter = Counter()
    versioned_bases: set[str] = set()
    entity_parents: list[tuple[str, str]] = []
    entity_total = entity_versioned = 0
    anemic_entities: list[tuple[str, int]] = []
    transactional_by_role: Counter = Counter()
    inventory: Counter = Counter()
    god_methods: list[tuple[str, int, str, int]] = []  # path, line, name, complexity

    for path in walk(root, excludes):
        ext = os.path.splitext(path)[1]
        test = is_test(path)
        if test:
            test_files += 1
            if not include_tests:
                if ext in JVM:
                    for m in re.finditer(r"\bimplements\s+([\w<>,.\s?]+?)\s*\{", "\n".join(read_lines(path))):
                        for n in split_params(m.group(1)):
                            test_impl_counts[re.sub(r"<.*", "", n).split(".")[-1].strip()] += 1
                continue
        else:
            main_files += 1
        files_by_ext[ext] += 1
        lines = read_lines(path)
        if not lines:
            continue
        text = "\n".join(lines)
        code = "\n".join(ln for ln in lines if not ln.lstrip().startswith(("*", "//", "/*", "#")))
        rel = path.replace("\\", "/")
        base = os.path.basename(path)
        is_jvm = ext in JVM
        is_js = ext in JS
        is_py = ext in PY

        # --- declared types, role suffixes, interfaces -------------------------------------------------
        declared = []
        for i, ln in enumerate(lines, 1):
            m = CLASS_DECL.match(ln) if is_jvm else None
            if not m and is_js:
                m = TS_CLASS.match(ln)
                if m:
                    declared.append(("class", m.group(1), i))
            if not m and is_py:
                m = PY_CLASS.match(ln)
                if m:
                    declared.append(("class", m.group(1), i))
            if m and is_jvm:
                kind, name = m.groups()
                declared.append((kind, name, i))
                for suf in ROLE_SUFFIXES:
                    if name.endswith(suf) and name != suf:
                        role_counts[suf] += 1
                        if len(role_examples[suf]) < 3:
                            role_examples[suf].append(name)
                        break
                if kind == "interface" and not test:
                    interfaces[name] = (path, i)
            elif m and (is_js or is_py):
                name = m.group(1) if is_js or is_py else None
                if name:
                    for suf in ROLE_SUFFIXES:
                        if name.endswith(suf) and name != suf:
                            role_counts[suf] += 1
                            if len(role_examples[suf]) < 3:
                                role_examples[suf].append(name)
                            break

        main_type = declared[0][1] if declared else base
        role = next((s for s in ROLE_SUFFIXES if main_type.endswith(s)), "")
        in_controller = (
                role in {"Controller", "RestController", "Resource", "Resolver"}
                or re.search(r"/(controller|web|rest|api|controllers)/", rel) is not None
                or (is_js and re.search(r"@(Controller|Resolver)\b", text))
                or (is_py and re.search(r"APIRouter|@router\.(get|post|put|delete|patch)", text))
        )
        in_service = (
                role in {"Service", "UseCase", "Manager", "Handler", "Interactor"}
                or "/service/" in rel or "/services/" in rel or "/usecase/" in rel
                or (is_js and re.search(r"@Injectable\b", text) and "Service" in main_type)
        )
        in_domain = re.search(r"/(domain|model|entity|entities)/", rel) is not None

        if is_jvm:
            for m in re.finditer(r"\bimplements\s+([\w<>,.\s?]+?)\s*\{", text):
                for n in split_params(m.group(1)):
                    impl_counts[re.sub(r"<.*", "", n).split(".")[-1].strip()] += 1
            for m in re.finditer(r"\b(?:class|object)\s+\w+[^{]*?:\s*([\w<>,.\s()]+?)\s*\{",
                                 text) if ext == ".kt" else []:
                for n in split_params(m.group(1)):
                    impl_counts[re.sub(r"[<(].*", "", n).strip()] += 1

        # --- Singleton shapes ---------------------------------------------------------------------------
        for i, ln in enumerate(lines, 1):
            if (
                    re.search(r"\bstatic\s+[\w<>\[\], ?]+\s+getInstance\s*\(", ln)
                    or re.search(r"\bgetInstance\s*\(\s*\)\s*[:{]", ln)
                    or (is_py and re.search(r"\b_instance\s*=\s*None", ln))
                    or re.search(r"private\s+static\s+(?:volatile\s+)?[\w<>]+\s+instance\b", ln)
                    or (is_js and re.search(r"\bstatic\s+#?instance\b", ln))
            ):
                sc.add(
                    "singleton",
                    "GoF Singleton: check for mutable state / hidden dependency; in DI apps prefer a container-managed bean",
                    path, i, ln.strip()[:100],
                )

        # --- type-driven branching (Strategy / State / Visitor / polymorphism candidates) ---------------
        inst = [i for i, ln in enumerate(lines, 1) if re.search(r"\binstanceof\b|\bisinstance\(|\btypeof\b", ln)]
        if len(inst) >= 3 and not test:
            sc.add(
                "type_branching",
                "instanceof/isinstance/typeof chains: missing polymorphism, Strategy, Visitor, or sealed-type switch",
                path, inst[0], f"{len(inst)} type checks in file",
            )
        for i, ln in enumerate(lines, 1):
            if re.search(r"\bswitch\s*\(", ln) and not is_py:
                depth, cases, j = 0, 0, i - 1
                started = False
                while j < len(lines) and j < i + 200:
                    cur = lines[j]
                    cases += len(re.findall(r"^\s*(?:case\s|default\b)", cur))
                    depth += cur.count("{") - cur.count("}")
                    if "{" in cur:
                        started = True
                    if started and depth <= 0:
                        break
                    j += 1
                if cases >= 5 and not test:
                    sc.add(
                        "type_branching",
                        "large switch: State / Strategy / registry-map / sealed-type candidate if it branches on a type or status and recurs",
                        path, i, f"switch with {cases} branches",
                    )
        chain, last = 0, -99
        for i, ln in enumerate(lines, 1):
            if re.search(r"\belse\s+if\b|\belif\b", ln):
                chain = chain + 1 if i - last <= 8 else 1
                last = i
                if chain == 4 and not test:
                    sc.add(
                        "type_branching",
                        "long if/else-if chain: Strategy / State / lookup-table candidate if it dispatches on a type/mode",
                        path, i, "4+ chained else-if",
                    )

        # --- collaborators built with `new` inside services/controllers ---------------------------------
        if (in_service or in_controller) and not test:
            for i, ln in enumerate(lines, 1):
                m = re.search(
                    r"\bnew\s+([A-Z]\w*(?:Service|Repository|Client|Gateway|Dao|DAO|Mapper|Factory|Manager|Provider|Executor))\s*\(",
                    ln,
                )
                if m:
                    sc.add(
                        "new_collaborators",
                        "hard-wired collaborator: use injection (Registry/Plugin/Separated Interface) so it can be swapped/stubbed",
                        path, i, m.group(1),
                    )
                # TS/JS: direct instantiation of collaborators
                if is_js and re.search(r"\bnew\s+[A-Z]\w*(?:Service|Repository|Client|Gateway|Mapper)\s*\(", ln):
                    sc.add(
                        "new_collaborators",
                        "hard-wired collaborator (TS/JS): prefer DI / factory / module provider",
                        path, i, ln.strip()[:80],
                    )

        # --- layering leaks ------------------------------------------------------------------------------
        if in_controller and not test:
            for i, ln in enumerate(lines, 1):
                if re.match(r"\s*import\s", ln) and re.search(
                        r"Repository\b|EntityManager|JdbcTemplate|\.entity\.|\.db\.|jakarta\.persistence|javax\.persistence|"
                        r"@prisma/client|typeorm|sqlalchemy|prisma\.|from\s+['\"]@prisma",
                        ln,
                ):
                    sc.add(
                        "layering_leak",
                        "PEAA: controller/handler touching persistence/entities -> Service Layer + DTO expected",
                        path, i, ln.strip()[:100],
                    )
                if "@Transactional" in ln:
                    sc.add(
                        "layering_leak",
                        "PEAA Unit of Work: transaction demarcated in controller; usually belongs to the service operation",
                        path, i, "@Transactional in controller",
                    )
        if in_domain and not test:
            for i, ln in enumerate(lines, 1):
                if re.match(r"\s*import\s", ln) and re.search(
                        r"springframework\.(web|http)|jakarta\.servlet|javax\.servlet|\.controller\.|\.web\.|"
                        r"express|fastify|@nestjs/common|fastapi|flask|django\.http",
                        ln,
                ):
                    sc.add(
                        "layering_leak",
                        "domain code depending on web layer; invert with Separated Interface / DTO",
                        path, i, ln.strip()[:100],
                    )

        # React / UI data access
        if is_js and re.search(r"/(components|pages|views|app)/", rel) and not test:
            for i, ln in enumerate(lines, 1):
                if re.search(r"\b(fetch|axios\.\w+|useSWR|useQuery)\s*\(", ln) and not re.search(r"use[A-Z]\w+\(", ln):
                    # crude: fetch inside component file that is not itself a custom hook
                    if not re.search(r"(use[A-Z]\w+|hooks/)", base):
                        sc.add(
                            "ui_data_access",
                            "React: data access inside a component; extract to a Gateway / custom hook (Page Controller doing everything)",
                            path, i, ln.strip()[:100],
                        )
                        break

        # NestJS specific
        if is_js and re.search(r"@nestjs/", text):
            if re.search(r"@Injectable\b", text) and re.search(r"prisma\.|PrismaService|TypeOrmModule",
                                                               text) and in_controller:
                sc.add(
                    "layering_leak",
                    "Nest: controller injecting Prisma/TypeORM directly — prefer a repository or service layer",
                    path, 1, "controller + direct ORM",
                )

        # --- @Transactional / transaction distribution -------------------------------------------------
        if is_jvm and "@Transactional" in code and not test:
            kind = "controller" if in_controller else "service" if in_service else "repository" if role == "Repository" else "other"
            transactional_by_role[kind] += code.count("@Transactional")

        # --- JPA / ORM entities: anemic / versioning ----------------------------------------------------
        if is_jvm and re.search(r"@Entity\b", text) and not test:
            entity_total += 1
            if re.search(r"@Version\b", code):
                entity_versioned += 1
            else:
                pm = re.search(r"\bextends\s+(\w+)", code)
                if pm:
                    entity_parents.append((path, pm.group(1)))
            behavior = 0
            for ln in lines:
                m = METHOD_DECL.match(ln) or KT_FUN.match(ln)
                if m:
                    name = m.group(1)
                    if name not in {"getId", "setId", "equals", "hashCode", "toString",
                                    "builder"} and not name.startswith(("get", "set", "is")):
                        behavior += 1
            if behavior <= 1 and entity_total:  # mostly accessors
                anemic_entities.append((path, 1))

        # Prisma models are schema-first; look for client usage patterns later
        if is_js and "prisma." in code and not test:
            inventory["prisma_usage"] += code.count("prisma.")

        # --- God file / god method -----------------------------------------------------------------------
        if not test and len(lines) > 500:
            sc.add(
                "god_file",
                "God Class / Blob candidate (>500 lines): consider extracting cohesive units",
                path, 1, f"{len(lines)} lines",
            )
        # God methods (rough complexity)
        if not test:
            for i, ln in enumerate(lines, 1):
                m = METHOD_DECL.match(ln) or KT_FUN.match(ln) or (TS_FUNC.match(ln) if is_js else None) or (
                    PY_DEF.match(ln) if is_py else None)
                if m:
                    name = m.group(1)
                    cx = estimate_complexity(lines, i)
                    if cx >= 15 or (len(lines) > 80 and name not in {"render", "main"}):
                        # only keep a few
                        if len(god_methods) < max_items:
                            god_methods.append((path, i, name, cx))
                            sc.add(
                                "god_method",
                                "High-complexity method (rough cyclomatic ≥15 or very long): candidate for Extract Method / Strategy / State",
                                path, i, f"{name} ~cx={cx}",
                            )

        # --- return null density -------------------------------------------------------------------------
        nulls = [i for i, ln in enumerate(lines, 1) if re.search(r"\breturn\s+null\b|\breturn\s+None\b", ln)]
        if len(nulls) >= 4 and not test:
            sc.add(
                "return_null",
                "Frequent return null/None: consider Optional / Special Case / Result type",
                path, nulls[0], f"{len(nulls)} occurrences",
            )

        # --- floating-point money -----------------------------------------------------------------------
        if not test and re.search(r"\b(double|float|BigDecimal|Decimal)\b.*(price|amount|money|balance|cost|fee)", text,
                                  re.I):
            for i, ln in enumerate(lines, 1):
                if re.search(r"\b(double|float)\b.*(price|amount|money|balance|cost|fee)", ln, re.I):
                    sc.add(
                        "floating_money",
                        "Floating-point used for money: prefer BigDecimal / Decimal / integer cents (Value Object)",
                        path, i, ln.strip()[:80],
                    )
                    break

        # --- lifecycle fields set from outside ----------------------------------------------------------
        if not test and re.search(r"\b(status|state|finishedAt|drained|completedAt|failedAt)\b", text, re.I):
            for i, ln in enumerate(lines, 1):
                if re.search(r"\.(setStatus|setState|status\s*=|state\s*=)\s*", ln) and in_service:
                    sc.add(
                        "lifecycle_outside_entity",
                        "Lifecycle/status mutated from outside the entity: candidate for intention-revealing methods on the entity (State / Domain Model light)",
                        path, i, ln.strip()[:80],
                    )
                    break

        # --- single-implementation interfaces (speculative generality) ----------------------------------
        # collected globally; analysed after the walk

        # --- missing idempotency on external writes (lead) ----------------------------------------------
        if (in_service or in_controller) and not test:
            if re.search(r"(post|put|patch|create|upsert|send|publish)\w*\s*\(", code, re.I) and re.search(
                    r"(RestTemplate|WebClient|fetch|axios|httpx|requests\.|HttpClient|Feign)", code
            ):
                if not re.search(r"idempoten|Idempotency-Key|idempotencyKey|clientRequestId", code, re.I):
                    sc.add(
                        "missing_idempotency",
                        "External write without visible idempotency key: risk of duplicates on retry",
                        path, 1, "external write path",
                    )

    # --- post-walk: single-impl interfaces --------------------------------------------------------------
    for iface, (ipath, iline) in interfaces.items():
        main_impls = impl_counts.get(iface, 0)
        test_impls = test_impl_counts.get(iface, 0)
        if main_impls == 1 and test_impls <= 1:
            sc.add(
                "single_impl_interface",
                "Interface with a single production implementation: possible speculative generality / over-engineering",
                ipath, iline, iface,
            )

    # --- stats ------------------------------------------------------------------------------------------
    sc.stats = {
        "main_files": main_files,
        "test_files": test_files,
        "files_by_ext": dict(files_by_ext),
        "role_counts": dict(role_counts.most_common(20)),
        "role_examples": {k: v for k, v in role_examples.items()},
        "entity_total": entity_total,
        "entity_versioned": entity_versioned,
        "transactional_by_role": dict(transactional_by_role),
        "inventory": dict(inventory),
        "anemic_entity_count": len(anemic_entities),
    }

    return sc


def format_md(sc: Scan) -> str:
    lines = ["# Pattern-compliance leads (scanner output)", ""]
    lines.append("**These are leads, not findings.** Confirm each by reading the code.")
    lines.append("")
    lines.append("## Stats")
    for k, v in sc.stats.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("## Leads")
    for check, data in sorted(sc.leads.items()):
        lines.append(f"### {check}")
        lines.append(f"_{data['hint']}_")
        lines.append("")
        for item in data["items"][:30]:
            note = f" — {item['note']}" if item["note"] else ""
            lines.append(f"- `{item['file']}:{item['line']}`{note}")
        if len(data["items"]) > 30:
            lines.append(f"- … +{len(data['items']) - 30} more")
        lines.append("")
    return "\n".join(lines)


def format_json(sc: Scan) -> str:
    return json.dumps({"stats": sc.stats, "leads": sc.leads}, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--max", type=int, default=40, help="max items per lead type")
    ap.add_argument("--include-tests", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(a.path):
        print(f"error: path not found: {a.path}", file=sys.stderr)
        return 2
    sc = scan(a.path, a.exclude, a.include_tests, a.max)
    if a.format == "json":
        print(format_json(sc))
    else:
        print(format_md(sc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
