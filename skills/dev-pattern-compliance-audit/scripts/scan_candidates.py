#!/usr/bin/env python3
"""Regex-based lead scanner for the pattern-compliance-audit skill.

Prints an inventory of *leads* -- places where a GoF / Fowler (PEAA) pattern, or a violation of one, is
plausible. It cannot tell a legitimate `switch` from a missing Strategy; every lead must be confirmed by
reading the code before it is reported as a finding.

Stdlib only. Covers Java, Kotlin, TypeScript/JavaScript (incl. TSX) and Python; the layering / persistence
heuristics are strongest for Java + Spring.

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
}
JVM = {".java", ".kt"}
JS = {".ts", ".tsx", ".js", ".jsx"}

ROLE_SUFFIXES = [
    "Controller", "RestController", "Resource", "Service", "UseCase", "Handler", "Repository", "Dao", "DAO",
    "Mapper", "Assembler", "Converter", "Factory", "Builder", "Strategy", "Adapter", "Decorator", "Proxy",
    "Facade", "Gateway", "Client", "Provider", "Visitor", "Listener", "Observer", "Command", "Interceptor",
    "Filter", "Manager", "Registry", "Helper", "Util", "Utils", "Dto", "DTO", "Request", "Response",
    "Entity", "Config", "Configuration", "Properties", "Exception", "Validator", "Handler", "Executor",
    "Runner", "Store", "Cache", "Template", "State", "Context",
]

CLASS_DECL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private|abstract|final|static|sealed|open|data)\s+)*"
    r"(class|interface|enum|record|object)\s+([A-Z]\w*)"
)
METHOD_DECL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private|static|final|abstract|synchronized|default)\s+)*"
    r"(?:<[^>]+>\s+)?[\w<>\[\],.? ]+?\s+(\w+)\s*\(([^)]*)\)\s*(?:throws [\w., ]+)?\s*\{"
)
KT_FUN = re.compile(r"^\s*(?:(?:public|private|protected|internal|override|open|suspend)\s+)*fun\s+(?:<[^>]+>\s+)?(\w+)\s*\(([^)]*)\)")


def is_test(path: str) -> bool:
    p = path.replace("\\", "/")
    name = os.path.basename(p)
    return (
        "/test/" in p or "/tests/" in p or "/__tests__/" in p or "/src/test" in p
        or name.endswith(("Test.java", "Tests.java", "IT.java", "Test.kt", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js"))
        or name.startswith("test_") or name.endswith("_test.py")
    )


def walk(root: str, excludes: list[str]):
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("sources")]
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
        entry["items"].append({"file": os.path.relpath(path, self.base), "line": line, "note": note})


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
        code = "\n".join(ln for ln in lines if not ln.lstrip().startswith(("*", "//", "/*")))
        rel = path.replace("\\", "/")
        base = os.path.basename(path)
        is_jvm = ext in JVM

        # --- declared types, role suffixes, interfaces -------------------------------------------------
        declared = []
        for i, ln in enumerate(lines, 1):
            m = CLASS_DECL.match(ln)
            if m:
                kind, name = m.groups()
                declared.append((kind, name, i))
                for suf in ROLE_SUFFIXES:
                    if name.endswith(suf) and name != suf:
                        role_counts[suf] += 1
                        if len(role_examples[suf]) < 3:
                            role_examples[suf].append(name)
                        break
                if kind == "interface" and is_jvm and not test:
                    interfaces[name] = (path, i)
        main_type = declared[0][1] if declared else base
        role = next((s for s in ROLE_SUFFIXES if main_type.endswith(s)), "")
        in_controller = role in {"Controller", "RestController", "Resource"} or re.search(r"/(controller|web|rest|api)/", rel) is not None
        in_service = role in {"Service", "UseCase", "Manager", "Handler"} or "/service/" in rel
        in_domain = re.search(r"/(domain|model|entity)/", rel) is not None

        if is_jvm:
            for m in re.finditer(r"\bimplements\s+([\w<>,.\s?]+?)\s*\{", text):
                for n in split_params(m.group(1)):
                    impl_counts[re.sub(r"<.*", "", n).split(".")[-1].strip()] += 1
            for m in re.finditer(r"\b(?:class|object)\s+\w+[^{]*?:\s*([\w<>,.\s()]+?)\s*\{", text) if ext == ".kt" else []:
                for n in split_params(m.group(1)):
                    impl_counts[re.sub(r"[<(].*", "", n).strip()] += 1

        # --- Singleton shapes ---------------------------------------------------------------------------
        for i, ln in enumerate(lines, 1):
            if re.search(r"\bstatic\s+[\w<>\[\], ?]+\s+getInstance\s*\(", ln) or re.search(r"\bgetInstance\s*\(\s*\)\s*[:{]", ln) or (
                ext == ".py" and re.search(r"\b_instance\s*=\s*None", ln)
            ) or re.search(r"private\s+static\s+(?:volatile\s+)?[\w<>]+\s+instance\b", ln):
                sc.add("singleton", "GoF Singleton: check for mutable state / hidden dependency; in DI apps prefer a container-managed bean",
                       path, i, ln.strip()[:100])

        # --- type-driven branching (Strategy / State / Visitor / polymorphism candidates) ---------------
        inst = [i for i, ln in enumerate(lines, 1) if re.search(r"\binstanceof\b|\bisinstance\(", ln)]
        if len(inst) >= 3 and not test:
            sc.add("type_branching", "instanceof/isinstance chains: missing polymorphism, Strategy, Visitor, or sealed-type switch",
                   path, inst[0], f"{len(inst)} type checks in file")
        for i, ln in enumerate(lines, 1):
            if re.search(r"\bswitch\s*\(", ln) and ext != ".py":
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
                    sc.add("type_branching", "large switch: State / Strategy / registry-map / sealed-type candidate if it branches on a type or status and recurs",
                           path, i, f"switch with {cases} branches")
        chain, last = 0, -99
        for i, ln in enumerate(lines, 1):
            if re.search(r"\belse\s+if\b|\belif\b", ln):
                chain = chain + 1 if i - last <= 8 else 1
                last = i
                if chain == 4 and not test:
                    sc.add("type_branching", "long if/else-if chain: Strategy / State / lookup-table candidate if it dispatches on a type/mode",
                           path, i, "4+ chained else-if")

        # --- collaborators built with `new` inside services/controllers ---------------------------------
        if (in_service or in_controller) and not test:
            for i, ln in enumerate(lines, 1):
                m = re.search(r"\bnew\s+([A-Z]\w*(?:Service|Repository|Client|Gateway|Dao|DAO|Mapper|Factory|Manager|Provider|Executor))\s*\(", ln)
                if m:
                    sc.add("new_collaborators", "hard-wired collaborator: use injection (Registry/Plugin/Separated Interface) so it can be swapped/stubbed",
                           path, i, m.group(1))

        # --- layering leaks ------------------------------------------------------------------------------
        if in_controller and not test:
            for i, ln in enumerate(lines, 1):
                if re.match(r"\s*import\s", ln) and re.search(
                    r"Repository\b|EntityManager|JdbcTemplate|\.entity\.|\.db\.|jakarta\.persistence|javax\.persistence|@prisma/client|typeorm|sqlalchemy", ln):
                    sc.add("layering_leak", "PEAA: controller touching persistence/entities -> Service Layer + DTO expected",
                           path, i, ln.strip()[:100])
                if "@Transactional" in ln:
                    sc.add("layering_leak", "PEAA Unit of Work: transaction demarcated in controller; usually belongs to the service operation",
                           path, i, "@Transactional in controller")
        if in_domain and not test:
            for i, ln in enumerate(lines, 1):
                if re.match(r"\s*import\s", ln) and re.search(r"springframework\.(web|http)|jakarta\.servlet|javax\.servlet|\.controller\.|\.web\.", ln):
                    sc.add("layering_leak", "domain code depending on web layer; invert with Separated Interface / DTO",
                           path, i, ln.strip()[:100])
        if ext in {".tsx", ".jsx"} and re.search(r"/(components|pages|views)/", rel) and not test:
            for i, ln in enumerate(lines, 1):
                if re.search(r"\b(fetch|axios\.\w+)\(", ln):
                    sc.add("ui_data_access", "React: data access inside a component; extract to a Gateway / hook (Page Controller doing everything)",
                           path, i, ln.strip()[:100])
                    break

        # --- @Transactional distribution -----------------------------------------------------------------
        if is_jvm and "@Transactional" in code and not test:
            kind = "controller" if in_controller else "service" if in_service else "repository" if role == "Repository" else "other"
            transactional_by_role[kind] += code.count("@Transactional")

        # --- JPA entities: anemic / versioning --------------------------------------------------------------
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
                if m and not re.match(r"(get|set|is|has|equals|hashCode|toString|builder|canEqual)", m.group(1)) and m.group(1) not in {"if", "for", "while", "switch", "catch", "synchronized", "return"}:
                    behavior += 1
            anemic_entities.append((path, behavior))

        # --- services mutating entity state from outside -------------------------------------------------
        if in_service and is_jvm and not test:
            sets = [i for i, ln in enumerate(lines, 1) if re.search(r"\b\w+\.set[A-Z]\w*\(", ln)]
            if len(sets) >= 8:
                sc.add("logic_outside_model", "PEAA Anemic Domain Model lead: service pokes entity setters; check whether the rules belong on the object",
                       path, sets[0], f"{len(sets)} setter calls")

        # --- lifecycle / state-machine fields written from outside the owning object -----------------------------
        # A CRUD app can still hold one object with a real state machine (status + counters + finished/drained
        # flags that must move together). Setting those fields from other classes is how the invariant ends up
        # enforced by convention only. This is per-object, so it fires even when the codebase as a whole is honest
        # Transaction Script.
        if is_jvm and not test and not in_domain:
            life = [i for i, ln in enumerate(lines, 1) if re.search(
                r"\b\w+\.set(?:Status|State|Phase|Stage|Finished\w*|Completed\w*|Failed\w*|Failures?\w*|\w*Failures|\w*Drained|\w*Attempts|\w*Retries|Terminal\w*|Error)\(", ln)]
            if len(life) >= 3:
                sc.add("lifecycle_outside_entity",
                       "PEAA Domain Model (per aggregate): lifecycle fields set from outside their object; if they must change together, an intention-revealing method on the entity enforces it. Ignore if these are DTO/mapper assignments",
                       path, life[0], f"{len(life)} lifecycle setter calls (lines {', '.join(map(str, life[:6]))})")

        # --- god files / long classes ------------------------------------------------------------------------
        if len(lines) > 500 and not test:
            sc.add("god_file", "God Class lead: >500 lines; look for unrelated responsibilities (Facade over extracted parts)",
                   path, 1, f"{len(lines)} lines")
        if is_jvm and not test:
            mcount = sum(1 for ln in lines if (METHOD_DECL.match(ln) or KT_FUN.match(ln)))
            if mcount > 25:
                sc.add("god_file", "God Class lead: many methods", path, 1, f"~{mcount} methods")

        # --- long parameter lists -----------------------------------------------------------------------------
        if is_jvm and not test:
            for i, ln in enumerate(lines, 1):
                m = METHOD_DECL.match(ln) or KT_FUN.match(ln)
                if m and len(split_params(m.group(2))) >= 6:
                    sc.add("long_params", "Builder / parameter object / Value Object lead (primitive obsession)",
                           path, i, f"{m.group(1)}: {len(split_params(m.group(2)))} params")

        # --- return null -------------------------------------------------------------------------------------------
        nulls = [i for i, ln in enumerate(lines, 1) if re.search(r"\breturn\s+null\s*;?\s*$", ln)] if ext in JVM | {".ts", ".tsx", ".js", ".jsx"} else []
        if len(nulls) >= 3 and not test:
            sc.add("null_returns", "PEAA Special Case / Optional / result type: null crossing method boundaries",
                   path, nulls[0], f"{len(nulls)} `return null`")

        # --- money as floating point ----------------------------------------------------------------------------
        if is_jvm and not test:
            for i, ln in enumerate(lines, 1):
                if re.search(r"\b(double|float|Double|Float)\s+\w*(price|amount|cost|total|balance|fee|salary|payment|tax)\w*", ln, re.I):
                    sc.add("money_float", "PEAA Money: floating point for currency; use BigDecimal/minor units + currency",
                           path, i, ln.strip()[:100])

        # --- service locator / static registry ------------------------------------------------------------------
        if not test and not re.search(r"Config(uration)?\b", main_type):
            for i, ln in enumerate(lines, 1):
                if re.search(r"\bgetBean\s*\(|ServiceLocator|SpringContext\.\w+\(|ApplicationContextHolder", ln):
                    sc.add("service_locator", "PEAA Registry / Service Locator in business code: prefer constructor injection",
                           path, i, ln.strip()[:100])

        # --- mutable static state ---------------------------------------------------------------------------------
        if is_jvm and not test:
            for i, ln in enumerate(lines, 1):
                if re.search(r"\b(?:private|protected|public)?\s*static\s+(?!final)(?!class)(?!void)[\w<>\[\], ?]+\s+\w+\s*(?:=|;)", ln) and \
                        "serialVersionUID" not in ln and "(" not in ln.split("=")[0]:
                    sc.add("static_mutable", "global mutable state: thread-safety + hidden coupling (Singleton-as-global)",
                           path, i, ln.strip()[:100])

        # --- pattern inventory (what IS used) -----------------------------------------------------------------------
        inv_rules = {
            "Builder (@Builder / builder())": r"@Builder\b|\bstatic\s+\w+\s+builder\s*\(",
            "Observer (events/listeners)": r"@EventListener|ApplicationEventPublisher|addListener\(|EventEmitter|@TransactionalEventListener",
            "Template Method (abstract base)": r"\babstract\s+class\b",
            "Proxy/Decorator via AOP (@Transactional/@Cacheable/@Async/@Retryable)": r"@Transactional|@Cacheable|@Async|@Retryable",
            "Gateway/Proxy (Feign/RestClient/WebClient)": r"@FeignClient|\bRestClient\b|\bWebClient\b|\bRestTemplate\b",
            "Optimistic lock (@Version)": r"@Version\b",
            "Sealed hierarchies / records (modern Value/State/Visitor)": r"\bsealed\s+(?:interface|class)\b|\brecord\s+\w+\s*\(",
            "Repository (Spring Data)": r"extends\s+(?:Jpa|Crud|PagingAndSorting)Repository",
            "Chain of Responsibility (filters/interceptors)": r"OncePerRequestFilter|HandlerInterceptor|FilterChain|SecurityFilterChain",
            "Strategy-by-DI (List<X>/Map<String,X> injection)": r"(?:List|Map<String,)\s*<?\s*[A-Z]\w*(?:Strategy|Handler|Provider|Processor)\b",
        }
        if is_jvm and re.search(r"@MappedSuperclass\b", code) and re.search(r"@Version\b", code):
            versioned_bases.add(main_type)
        if not test:
            for label, rx in inv_rules.items():
                if re.search(rx, code):
                    inventory[label] += 1

    # ---- finalise aggregate leads ------------------------------------------------------------------------------
    for name, (p, ln) in interfaces.items():
        n = impl_counts.get(name, 0)
        src = "".join(read_lines(p)[max(0, ln - 4):ln])
        if n == 1 and not re.search(r"FeignClient|extends\s+\w*Repository|@Mapper|@RestController|OpenAPI|Generated", src):
            td = test_impl_counts.get(name, 0)
            note = f"interface {name}: 1 implementation" + (f" + {td} test double(s) -> likely a real seam" if td else " and no test double")
            sc.add("single_impl_interface", "Speculative generality lead (or a legitimate port / Separated Interface; a test double is evidence the seam is used)",
                   p, ln, note)

    for _, parent in entity_parents:
        if parent in versioned_bases:
            entity_versioned += 1
    if entity_total:
        sc.stats["entities"] = {"total": entity_total, "with_@Version": entity_versioned}
        if entity_versioned < entity_total:
            sc.add("no_optimistic_lock", "PEAA Optimistic Offline Lock: entities without @Version -- confirm whether concurrent read-modify-write is possible",
                   sc.root, 0, f"{entity_total - entity_versioned} of {entity_total} entities have no @Version")
        anemic = [(p, b) for p, b in anemic_entities if b == 0]
        if anemic:
            sc.stats["entities_without_behaviour"] = f"{len(anemic)}/{entity_total}"
            for p, _ in anemic:
                sc.add("anemic_entity", "PEAA Anemic Domain Model lead: entity has accessors only -- an issue only if the domain is non-trivial and rules live in services",
                       p, 1, "no behaviour methods")
    if transactional_by_role:
        sc.stats["@Transactional by layer"] = dict(transactional_by_role)

    sc.stats["files"] = {"main": main_files, "test": test_files, "by_ext": dict(files_by_ext)}
    sc.stats["role_suffix_counts"] = {k: {"count": v, "examples": role_examples[k]} for k, v in role_counts.most_common()}
    sc.stats["pattern_inventory (files using)"] = dict(inventory.most_common())
    return sc


def render_md(sc: Scan) -> str:
    out = ["# Pattern lead scan", "", f"Root: `{sc.root}`", "",
           "> Leads only. Regex-based; confirm every item by reading the code before reporting it.", ""]
    files = sc.stats.get("files", {})
    out += ["## Inventory", "", f"- Files: {files.get('main', 0)} main, {files.get('test', 0)} test ({files.get('by_ext', {})})"]
    for k in ("entities", "entities_without_behaviour", "@Transactional by layer"):
        if k in sc.stats:
            out.append(f"- {k}: {sc.stats[k]}")
    out += ["", "### Role suffixes", ""]
    for k, v in sc.stats.get("role_suffix_counts", {}).items():
        out.append(f"- **{k}** x{v['count']} (e.g. {', '.join(v['examples'])})")
    out += ["", "### Patterns present (files using)", ""]
    for k, v in sc.stats.get("pattern_inventory (files using)", {}).items():
        out.append(f"- {k}: {v}")
    out += ["", "## Leads", ""]
    if not sc.leads:
        out.append("_none_")
    for check, entry in sorted(sc.leads.items(), key=lambda kv: -len(kv[1]["items"])):
        items = entry["items"]
        out += [f"### {check} ({len(items)})", "", f"_{entry['hint']}_", ""]
        for it in items[: sc.max]:
            loc = f"{it['file']}:{it['line']}" if it["line"] else it["file"]
            out.append(f"- `{loc}` {it['note']}")
        if len(items) > sc.max:
            out.append(f"- ... +{len(items) - sc.max} more (use --max or --format json)")
        out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="repo root, module dir, or single file")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    ap.add_argument("--exclude", action="append", default=[], help="glob (matched on relative path and file name); repeatable")
    ap.add_argument("--max", type=int, default=12, help="max items per check in md output (default 12)")
    ap.add_argument("--include-tests", action="store_true", help="also scan test sources (off by default)")
    a = ap.parse_args()
    if not os.path.exists(a.path):
        print(f"error: {a.path} does not exist", file=sys.stderr)
        return 2
    sc = scan(a.path, a.exclude, a.include_tests, a.max)
    if a.format == "json":
        json.dump({"root": sc.root, "stats": sc.stats, "leads": sc.leads}, sys.stdout, indent=2)
        print()
    else:
        print(render_md(sc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
