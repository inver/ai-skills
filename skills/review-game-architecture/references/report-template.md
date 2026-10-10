# Report template

Return Markdown. If a saved report is requested, use the requested path or
`docs/game-architecture-<scope>-<YYYY-MM-DD>.md`. Keep the verdict and priorities easy to scan.
For a quick pass use only Context, Findings and Recommendations; put omissions/questions in Context,
include only top findings and quick wins, and keep compact traceability and recommendation fields.

````markdown
# Game architecture review — <scope>

## Context

- **Date / commit / skill version:** <date> / <revision> / 1.2.0
- **Verdict / goals:** <bounded assessment>
- **Targets / stack:** <hardware, OS, API, framework and JDK versions>
- **Scope / mode:** <full or quick; inspected paths and vertical slices>
- **Requirements / budgets:** <IDs, sources, workload, acceptance condition; unknown or proposed when needed>
- **Capacity / milestones:** <available effort, existing commitments, deadlines; unknown when unavailable>
- **Assumptions:** <explicitly labeled>
- **Quick-pass omissions / gaps:** <required for quick pass; remove this bullet for full review>

## Architecture Overview

<Module dependencies, core/backend/editor separation, data/asset flow, ECS/scene graph authority,
thread/timing model, lifecycle and resource ownership; distinguish planned from implemented capabilities.>

## Findings

<Cover the eight areas: architecture/modules; rendering/API; shaders/materials/passes/GPU;
editor/content; CPU/GPU profiling; builds/platforms/delivery; quality/maintainability; debt/risk/scalability.
Retain supported strengths; mark insufficient evidence and inapplicable areas rather than inventing defects.>

### F-01 — <concrete finding or supported strength>

- **Area / priority:** <area / priority with rationale>
- **Evidence / confidence:** <observed fact, inference or unverified hypothesis; high/medium/low and why>
- **Source:** <revision, file:line/symbol or capture/test location; attribute unverified user reports>
- **Consequence / premises:** <affected product goal; distinguish observed behavior from unmeasured cost>
- **Risk of inaction:** <required for high priority; consequence and uncertainty>
- **Validation needed:** <smallest check, or existing relevant evidence and limits>

### Traceability Matrix

| Finding ID | Requirement/budget ID and source | Workload/acceptance condition | Evidence reference and label/confidence | Status/gap | Recommendation IDs |
|---|---|---|---|---|---|
| <F-ID> | <approved ID or unmapped — needs stakeholder validation> | <condition or unknown> | <reference, label, confidence> | <met/violated/unknown with limits> | <RA-ID or none> |

## Recommendations

### Quick wins

<Low-effort actions with high expected impact, including bounded validation that unlocks a decision.>

| ID / finding IDs / priority / score factors | Action / rationale / expected impact | Owner | Effort range / confidence / assumptions | Implementation risk / risk of inaction | Dependencies / milestone | Success metric / validation scope |
|---|---|---|---|---|---|---|

### Structural improvements

<Only justified larger changes; use the same fields. Omit this subsection for quick passes or when none are justified.>

### Sequence and immediate next steps

<Reference RA IDs in dependency order; show R/U/E/A/D scores, weighted totals and any priority overrides.
Fit upper effort estimates and validation into available capacity. Unknown capacity means provisional sequencing.
For disruptive changes include rollout/rollback; keep measurements and budget agreement ahead of optimization commitments.>

## Open Questions/Evidence Gaps

- **Questions / blocking decisions:** <owner if known>
- **Inspected slices / unreviewed areas:** <specific paths and coverage limits>
- **Checks actually run:** <commands/captures/results and limits; none if none>
- **Missing evidence / experiments:** <hardware, baselines, budgets, representative workloads>
- **Source verification:** <repository citations checked; version-appropriate official sources>
````

## Style rules for findings

- One root cause per finding; group locations. Keep recommendation IDs stable when reordering.
- Evidence supports the stated claim, not a stronger implied claim. Static call sites do not establish measured cost.
- Preserve the skill's three evidence labels; do not introduce an ambiguous “Confirmed” status.
- Missing ECS, render graphs or a named design pattern is not itself a defect. Tie changes to product requirements.
- Specify review/roadmap actions and acceptance checks without writing implementation code.
- Avoid prescribing a GPU upload thread before establishing context ownership and synchronization.
