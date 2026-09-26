---
name: dev-pattern-compliance-audit
description: >
  Audit a codebase (or a module/path in it) against the Gang of Four design patterns
  (Design Patterns, 1994) and Martin Fowler's enterprise application patterns
  (Patterns of Enterprise Application Architecture) and produce an evidence-based
  compliance report with file:line references, optionally handed off as an OpenSpec
  change or plain tickets. Use whenever the user asks to check, review, audit, assess
  or "analyze" code for design-pattern compliance, GoF / Gang of Four patterns,
  Fowler / PEAA / enterprise patterns, Anemic Domain Model, Transaction Script vs
  Domain Model, Repository / Data Mapper / Unit of Work / Service Layer / DTO usage,
  misused or missing patterns, over-engineering with patterns, or wants an
  architecture-quality review framed in pattern terms — even if they only say
  "does this follow good patterns", "review the architecture of this module" or
  "what patterns are we using wrong".
license: Apache 2.0
metadata:
  version: "1.1.0"
  tags:
    - architecture
    - design-patterns
    - gof
    - peaa
    - code-review
    - audit
    - refactoring
  improved_from: "inver/ai-skills@main (dev-pattern-compliance-audit)"
  changelog: >
    1.1.0: Broadened scanner heuristics (TS/Nest/Prisma/FastAPI/React), added
    sampling/budget guidance, modern-pattern mapping, frontend cross-checks,
    optional JSON report, self-locating scripts, expanded framework mapping.
---

# Pattern Compliance Audit

Assess how well a codebase uses — and misuses — the two classic pattern catalogs:

- **GoF** (Gamma, Helm, Johnson, Vlissides): 23 object-level design patterns → `references/gof-catalog.md`
- **PEAA** (Fowler): enterprise application architecture patterns → `references/peaa-catalog.md`

Optional modern mapping (DDD tactical, Ports & Adapters, resilience) → `references/modern-patterns.md`.

The output is a report a tech lead can act on, and (if the user wants) an OpenSpec change
or plain ticket list that turns the accepted findings into work.

## The stance that makes the audit useful

"Compliance" here does **not** mean "uses as many patterns as possible". Patterns are answers to specific
forces; a pattern applied without its force is over-engineering, and Fowler himself says a Domain Model is not
always the right choice, a Service Layer is unnecessary for a single-interface app, and a Repository only pays off
with a complex domain or heavy querying. So judge every candidate with the **fit test**:

1. **Force** — is the problem the pattern solves actually present here (e.g. branching on a type code that keeps growing; the same query duplicated; two clients needing the same business operation)?
2. **Evidence** — can you point at code (`path:line`) that shows the force or the pattern?
3. **Cost/benefit** — would the fix be proportionate to the code's size and how often it changes?

Only report a finding when the force is real. A report that says "the codebase is mostly fine, here are 4 things
worth fixing and 6 patterns that are well applied" is more valuable — and more trusted — than a 60-item wish list.
Reporting what is *done well* also matters: it stops the team from "fixing" working design and shows the reader you
read the code instead of pattern-matching on names.

## Execution budget & sampling (new in 1.1)

For large codebases (> ~200 source files or monorepos):

1. **Always** run the scanner and produce the architecture profile (PEAA).
2. **Prioritise** High-severity leads and every lead that appears ≥ 3 times.
3. Read **all entry points** + **3–5 representative vertical slices** end-to-end.
4. Sample the rest; state clearly in the Method section what was fully read vs sampled.
5. Cap the main findings list at ~12–15; move the rest to the appendix.
6. Prefer depth on the 2–3 highest-value findings over breadth.

If the user asks for a "quick audit" or "fast pass", stop after the architecture profile + top 5 findings.

## Workflow

Create a todo per step. Resolve the skill directory first so scripts work from any cwd:

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || SKILL_DIR="$(dirname "$(realpath "$0")")"
# or simply: the directory that contains this SKILL.md
```

### 1. Scope

Establish what is being audited: whole repo, one module, or a path. If the user did not say, default to the
whole repo but tell them you will treat generated code, tests, build output and vendored dirs as out of scope.
Detect the stack (languages, frameworks, persistence, UI) from the build files — the stack decides which patterns
the *framework already provides* (see step 4) and so which "missing pattern" findings would be false positives.
Read the repo's own architecture docs (`AGENTS.md`, `CLAUDE.md`, `docs/`, ADRs) first; a documented, deliberate
deviation is not a defect, though it can still be reported as a known trade-off.

### 2. Gather leads with the scanner

```bash
python "$SKILL_DIR/scripts/scan_candidates.py" <repo-or-path> [--format md|json] [--exclude glob ...] [--max N]
```

It is a fast, regex-based inventory: role-suffix counts, Singleton shapes, `instanceof`/`switch` chains,
anemic entities, `new` of collaborators inside services, layering leaks, god files/methods, single-implementation
interfaces, `return null` density, floating-point money, lifecycle fields set from outside their object,
Nest/Prisma/FastAPI/React-specific signals, and more. **Its output is a list of leads, not findings** —
regexes cannot tell a legitimate `switch` from a missing Strategy. Every lead you report must be confirmed by
reading the code. The scanner exists so you spend your reading budget on the 30 places that matter instead of
skimming 800 files.

The scanner is strongest on Java/Kotlin/Spring, good on TypeScript/Nest/Prisma/React and Python/FastAPI/Django,
and best-effort elsewhere. State the bias in the report.

### 3. Map the architecture (PEAA first, top-down)

PEAA decisions are architectural and shape everything else, so settle them before hunting GoF patterns. Read the
entry points and one representative vertical slice end to end (controller → service → persistence → external call)
and decide, with evidence:

- **Domain logic style** — Transaction Script, Table Module, or Domain Model; and is there a Service Layer? Where do business rules actually live? Decide this **per entity, not once for the codebase**: an app that is honest Transaction Script over CRUD can still contain one object with a real state machine (a status plus counters and finished/drained flags that must move together, written from other classes). Judge each entity on its own force — "Transaction Script overall" is a profile, not permission to skip the entities that don't fit it. The scanner's `lifecycle_outside_entity` and `anemic_entity` leads point at these.
- **Data source style** — Active Record, Data Mapper (JPA/Hibernate/Prisma/TypeORM counts), Table/Row Data Gateway; Repository on top?
- **Presentation / distribution** — MVC/Front Controller/Page Controller, DTOs at the process boundary, Remote Facade, Gateway to external systems.
- **Concurrency & state** — offline locks (`@Version`, optimistic concurrency tokens), session state strategy, transaction boundaries (Unit of Work).
- **Base patterns** — Value Object/Money, Special Case, Layer Supertype, Separated Interface, Registry/Plugin.

Detailed "what to look for / how it goes wrong" for each is in `references/peaa-catalog.md`. Read the relevant
sections rather than the whole file when the codebase is large.

### 4. Credit what the framework already gives you

Before writing "missing X", check `references/framework-mapping.md`. Spring's container is a Registry/Plugin
replacement and a Factory; Spring Data / Prisma / TypeORM is a Repository; JPA is Data Mapper + Unit of Work +
Identity Map + Lazy Load; `@Transactional` is a Proxy/Decorator; Feign / Nest HttpModule is a Gateway + Proxy;
Lombok `@Builder` / records are Builder; the servlet/Express/Nest middleware chain is Chain of Responsibility;
React context is a Registry; and so on. Hand-rolling any of these is itself a finding (reinventing the framework);
*not* hand-rolling them is not.

### 5. Evaluate at class level (GoF) + modern mapping

Walk the leads from the scanner and the hot spots from step 3. For each candidate, classify it:

| Verdict | Meaning |
|---|---|
| **Well applied** | Pattern present, force present, implemented in the pattern's spirit |
| **Misapplied** | Pattern present but wrong (e.g. Singleton holding mutable request state, Decorator that changes the interface, Repository that leaks `Query`/`Session`) |
| **Missing** | Force present, no pattern; concrete cost visible (duplicated branching, shotgun edits) |
| **Over-engineered** | Pattern present, force absent (Factory around a constructor, interface + one impl + no seam needed) |
| **Anti-pattern** | A recognised named failure: Anemic Domain Model, God Class, Service Locator abuse, Singleton-as-global-state, Golden Hammer, … |

When the team's vocabulary is DDD / Hexagonal / resilience-oriented, also consult `references/modern-patterns.md`
and prefer the terminology the team already uses (still apply the same fit test).

### 6. Run the cross-checks

Judging each class alone misses the defects that come from a pattern being applied *here* but skipped *there*, or
from code disagreeing with the schema, the tests or its own comments. Work through `references/cross-checks.md`
(now includes frontend-oriented checks). These are cheap greps plus a read, and they have produced some of the
highest-value findings.

### 7. Verify, rate, and deduplicate

- Re-read the cited lines. Confirm the claim from code, not from a class name (`FooFactory` may not be a factory).
- **Run the citation check** on your draft before you finalise it:
  `python "$SKILL_DIR/scripts/check_citations.py" <report.md>`. It fails on any `path:line` (or range end) past the
  end of the file — line numbers recalled from memory are the most common way a report ends up wrong, and one bad
  citation makes the reader doubt the rest. Fix every hit by re-opening the file. It cannot tell whether the line
  says what you claim, so still re-read.
- Give each finding a **severity** — High (structural: wrong-layer business logic, data-loss risks like missing
  locking, persistence leaking into the API), Medium (maintainability drag with real change cost), Low (style /
  consistency) — and a **confidence** — Confirmed (read and reasoned) or Likely (strong signal, not fully traced).
  Never present a Likely as Confirmed.
- Merge symptoms with the same root cause into one finding. Ten `instanceof` chains are one missing-polymorphism
  finding with ten locations.
- Prefer a small number of high-value findings. If you have more than ~15, rank and keep the top; put the rest in
  an appendix table.

### 8. Write the report

Use `references/report-template.md`. Save it as `docs/pattern-compliance-<YYYY-MM-DD>.md` (create `docs/` if
absent; if the user asked for chat-only output, print it instead). Every finding has: pattern (catalog + name),
verdict, severity, confidence, `path:line` evidence, why it matters *for this code*, and a proportionate
recommendation that names the target pattern and the smallest first step. Include the **Well applied** and
**Deliberately not recommended** sections — the latter lists patterns you considered and rejected because the
force is absent, which pre-empts "why didn't you suggest X?". Scope each rejection: "no Domain Model *for CRUD
entities X, Y*" is fine, but a codebase-wide "no Domain Model" must not sit next to an entity you found with a real
state machine — report that entity as a finding and narrow the rejection.

Optionally also emit a machine-readable companion:

```bash
# after the markdown report is written
python "$SKILL_DIR/scripts/report_to_json.py" docs/pattern-compliance-....md > docs/pattern-compliance-....json
```

(or produce the JSON structure yourself following the schema in the template).

### 9. Offer the hand-off

Findings are a proposal, not a mandate. After the report, ask which findings the user accepts, then — only for
those — offer one of:

- OpenSpec change (follow `references/openspec-handoff.md`) if the repo uses OpenSpec / the `openspec-propose` skill;
- otherwise a plain list of GitHub/Linear/Jira-ready ticket titles + acceptance criteria derived from the findings.

Do not create a change, edit code, or refactor unprompted: the audit is read-only.

## Rules of thumb

- **Read before you claim.** A finding with no `path:line` and no quoted/paraphrased code is an opinion.
- **Architecture before objects.** Don't recommend Strategy in a class whose real problem is that the business logic lives in a controller.
- **Match the language's idiom.** Modern Java: sealed interfaces + pattern-matching `switch` often replace Visitor; lambdas replace many Strategy/Command/Template Method classes; records are Value Objects; enums implement Singleton and State. Recommending a class-heavy 1994 shape when a lambda does the job is a mistake. Same for TypeScript discriminated unions and Python `@singledispatch` / Protocol.
- **Respect documented decisions.** If the project's docs state a deliberate trade-off, cite it and only flag it if the stated reason no longer holds.
- **Look for what the honest style still leaves out.** Concluding "this is a fine Transaction Script app" is the start of the audit, not the end: the cross-checks and per-entity lifecycle check are where the real defects usually are.
- **Say what you did not check.** List skipped paths, unsupported languages, and anything you sampled rather than read exhaustively.
- **Be honest about the scanner.** It is regex-based and strongest on Java/Kotlin/TS/Python; state that in the report's method section.
- **Budget your reading.** On large codebases, depth on the highest-value findings beats exhaustive coverage.