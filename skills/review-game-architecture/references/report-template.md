# Report template

Save as `docs/game-architecture-<YYYY-MM-DD>.md` (or
`docs/game-architecture-<scope>-<YYYY-MM-DD>.md` when reviewing one module or
backend). Keep it skimmable: a busy reader should get the verdict from the
first screen and the priorities from the second. Delete any section that would
be empty rather than writing "N/A".

````markdown
# Game architecture review — <scope>

- **Date:** <YYYY-MM-DD> · **Commit:** <short sha> · **Scope:** <paths/vertical slices reviewed> · **Out of scope:** <generated code, tests, unreviewed modules>
- **Stack:** <languages, build tools, rendering backends, engine/framework>
- **Skill version:** 1.1.0

## Project understanding

<goal, target platforms/hardware, tech stack, module/data flow, current
capabilities. Keep this short — the roadmap carries the detail.>

## Scope, assumptions, and questions

- **Inspected:** <files, specs, CI configs, vertical slices>
- **Checks run:** <build, tests, profiler captures, static analysis — and their limits>
- **Unknowns:** <performance budgets, content scale, team capacity, deadlines>
- **Assumptions:** <explicitly labeled, each with what it depends on>
- **Clarifying questions:** <at most five; mark which block the roadmap>

## Assessment

### Architecture and modules
<dependency direction/cycles, ownership, lifecycle, ECS/service boundaries,
threading, platform coupling — with evidence>

### Rendering and API abstraction
<implemented vs planned backends, capabilities/fallback, command/resource
ownership, synchronization, render graph fit>

### Shaders, materials, passes, GPU
<compilation/variants, binding layouts, precision/color space, pass
dependencies, culling/batching, bandwidth, allocations, readbacks>

### Editor and content workflow
<undo/persistence, import/reimport, asset identity, errors, iteration time,
runtime parity, UI/render thread work>

### CPU/GPU profiling
<representative workloads, frame-time tails, allocations/GC, simulation,
submission vs execution, memory/stalls>

### Builds, platforms, delivery
<toolchains, native loading/ABI, shader artifacts, incremental builds, CI
coverage, reproducible packaging/distribution>

### Quality and maintainability
<tests at useful seams, graphics validation, cancellation/errors, API
contracts, documentation accuracy>

### Debt, risk, scalability
<concrete failure modes, content/team growth limits, migration cost, release
blockers, support burden>

## Well applied

<What is done well, with `path:line`. Short: name, where, one clause on why it
fits. These are as informative as the defects — they show the team's intended
style and prevent "fixing" sound design.>

## Prioritized roadmap

| ID | Priority | Phase | Action and evidence | Rationale | Expected impact | Effort | Risk: implementation / unresolved | Dependencies | Success metric |
|---|---|---|---|---|---|---|---|---|---|

## Immediate next steps

<smallest useful actions and decisions, referencing roadmap IDs rather than
duplicating recommendation details.>

## Method and limits

- **Vertical slices sampled:** <asset import → ... → disposal; scene load → ... → runtime; shader source → ... → execution>
- **Unreviewed areas:** <paths skipped or sampled rather than read exhaustively>
- **Evidence labels:** <observed fact / inference / unverified hypothesis, with confidence>
- **Citations verified:** <n>/<n> resolve against current code; re-read before finalizing>
- **External sources:** <official docs checked against repository versions>
- **Execution budget:** <e.g. "top 8 findings; 3 vertical slices fully read">
````

## Style rules for findings

- Title states the *problem*, not the area alone: "Import path uploads
  textures on the UI thread — Editor/content workflow", not "Editor workflow".
- Evidence beats adjectives. `path:line` for every claim; no "seems",
  "appears", "probably" in a finding marked Confirmed.
- One root cause per finding. Group locations; don't list the same smell ten
  times.
- The recommendation must be executable by a developer without re-deriving your
  analysis: say what to change and where.
- Priority reflects consequence, not area prestige: a missing synchronization
  on a contended resource is High; a missing render graph is Medium unless the
  pass count justifies it.
- Calibrate to context: a small prototype engine does not warrant a full render
  graph recommendation regardless of the catalog.
- Never invent measured values. If the baseline is unknown, say so and make
  establishing it the first milestone.