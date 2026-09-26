# Report template

Save as `docs/pattern-compliance-<YYYY-MM-DD>.md` (or `docs/pattern-compliance-<scope>-<YYYY-MM-DD>.md` when
auditing one module). Keep it skimmable: a busy reader should get the verdict from the first screen and the
priorities from the second. Delete any section that would be empty rather than writing "N/A".

Optionally also emit a companion JSON file with the same findings for tooling (schema at the bottom).

````markdown
# Pattern compliance report — <scope>

- **Date:** <YYYY-MM-DD> · **Commit:** <short sha> · **Scope:** <paths audited> · **Out of scope:** <generated code, tests, …>
- **Catalogs:** GoF (23 patterns) · Fowler PEAA · (optional) modern mapping · OpenAPI contract when present
- **Stack:** <languages, frameworks, persistence, UI>
- **Skill version:** 1.3.0

## Summary

<3–5 sentences: overall verdict, the 2–3 findings that matter most, and the overall shape of the code
("Data Mapper over JPA with Transaction-Script services; sound layering, weakest at the API boundary").>

| Severity | Count |
|---|---|
| High | n |
| Medium | n |
| Low | n |

## Architecture profile (PEAA)

| Concern | What the code does | Evidence |
|---|---|---|
| Domain logic | Transaction Script / Domain Model / mixed | `path:line` |
| Service Layer | present / absent / pass-through | |
| Data source | Data Mapper (JPA/Prisma/…) / Active Record / Gateway | |
| Repository / Query Object | | |
| Presentation | Front Controller + Page Controllers; thin/fat | |
| Distribution | DTOs? Remote Facade? Gateways to external systems? | |
| API contract (OpenAPI) | none / contract-first / code-first · FE client: generated (orval/…) | hand-rolled | n/a · drift notes | path to spec + codegen config |
| Concurrency | `@Version` / tokens? none? | |
| Transactions (Unit of Work) | owned by … | |

## Findings

Ordered by severity, then by value/cost. One block per finding.

### F1 — <short title> · <Pattern name> (<GoF|PEAA|Modern>) · **<Verdict>** · <High|Medium|Low> · <Confirmed|Likely>

- **Where:** `path/File.java:42`, `path/Other.java:118` (max 5; "+N more" if the list is long)
- **What the code does:** <one or two sentences, paraphrasing or quoting the key lines>
- **Why it matters here:** <the concrete cost in this codebase — who edits it, what breaks, how often it changes>
- **Recommendation:** <the target pattern + the smallest first step, proportionate to the code>
- **Trade-off / when to skip:** <honest downside or the condition under which this isn't worth doing>

<!-- Verdict ∈ Misapplied | Missing | Over-engineered | Anti-pattern -->

## Well applied

Patterns used correctly, with `path:line`. Short: name, where, one clause on why it fits. These are as
informative as the defects — they show the team's intended style and prevent "fixing" sound design.

## Deliberately not recommended

Patterns considered and rejected, each with the absent force ("No Visitor: the element hierarchy is stable and
there is a single operation."; "No Domain Model: services are thin CRUD orchestration, Transaction Script is the
honest fit.").

## Method and limits

- How leads were gathered (`scan_candidates.py` v1.1, regex-based, strongest on Java/Kotlin/TS/Python) and what was read in full vs sampled.
- Cross-checks run (`references/cross-checks.md`) and which produced findings.
- Citations verified with `check_citations.py`: <n>/<n> resolve. (Existence of the line only; the claims were re-read separately.)
- Paths/languages skipped. Anything the reader should verify (Likely findings).
- Documented decisions in the repo that explain apparent deviations.
- Execution budget applied: <e.g. "top 12 findings; 4 vertical slices fully read">.

## Appendix — lower-priority items

| # | Pattern | Where | Note |
|---|---|---|---|
````

## Style rules for findings

- Title states the *problem*, not the pattern name alone: "Order status switch duplicated in 4 places — State", not "State".
- Evidence beats adjectives. `path:line` for every claim; no "seems", "appears", "probably" in a finding marked Confirmed.
- One root cause per finding. Group locations; don't list the same smell ten times.
- The recommendation must be executable by a developer without re-deriving your analysis: say which type to introduce or move, and where.
- Severity reflects consequence, not pattern prestige: a missing optimistic lock on a contended row is High; a missing Builder is Low.
- Calibrate to context: a one-file utility does not warrant an Abstract Factory recommendation regardless of the catalog.

## Optional JSON companion schema

```json
{
  "meta": {
    "date": "YYYY-MM-DD",
    "commit": "abc1234",
    "scope": ["src/main"],
    "stack": ["Java", "Spring Boot", "JPA"],
    "skillVersion": "1.1.0"
  },
  "summary": {
    "verdict": "…",
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "architectureProfile": { },
  "findings": [
    {
      "id": "F1",
      "title": "…",
      "pattern": "State",
      "catalog": "GoF",
      "verdict": "Missing",
      "severity": "High",
      "confidence": "Confirmed",
      "locations": ["src/OrderService.java:42"],
      "why": "…",
      "recommendation": "…",
      "tradeoff": "…"
    }
  ],
  "wellApplied": [],
  "deliberatelyNotRecommended": []
}
```
