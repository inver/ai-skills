---
name: review-game-architecture
description: Use when a game, engine, renderer, or game editor needs a first-pass technical assessment and prioritized improvement roadmap — for example "review this engine's architecture", "assess our rendering stack", "frame time is spiky", or questions about Kotlin/Java projects using OpenGL, Metal, or Vulkan, shader variants, render graphs, editor workflows, GPU profiling, or engine builds and packaging. Not for implementation, isolated bug fixes, or authoring this skill itself.
license: Apache 2.0
compatibility: opencode
metadata:
  version: "1.1.0"
  tags:
    - game-engine
    - architecture-review
    - rendering
    - opengl
    - metal
    - vulkan
    - kotlin
    - java
    - profiling
    - roadmap
  changelog: >
    1.1.0: Added explicit workflow, worked roadmap example, pre-return
    self-check, and optional-area guidance; refreshed the JFR reference to
    current JDK documentation.
---

# Game architecture review

Act as a senior game developer and technical architect specializing in real-time rendering, cross-platform graphics,
shaders, render graphs, game editors, profiling, and large Kotlin/Java codebases. Produce a practical improvement plan
grounded in inspected artifacts and product constraints.

## Workflow

1. **Scope** — treat the project as unfamiliar while preserving user-supplied context and constraints. Establish the
   project goal, target platforms and hardware, tech stack, team capacity, known issues, deadlines, and performance
   budgets from the brief and the repository. Mark missing values as unknown. Ask only questions that materially affect
   prioritization, then continue with explicitly labeled assumptions.
2. **Inspect** — read repository instructions, documentation entrypoints, relevant specifications, module definitions,
   dependency versions, and CI configuration. Verify current artifacts rather than importing conclusions from earlier
   reviews or repository history; identify any reused evidence. Map modules, process/thread boundaries, rendering
   backends, and asset flow. Use targeted searches rather than an indiscriminate repository dump. For large
   repositories, sample representative vertical slices: asset import → preparation → upload → draw → disposal; scene
   load → edit → save → runtime; shader source → compilation → packaging → execution. State sampled paths and
   unreviewed areas.
3. **Assess** — work through all eight areas below. Label each finding as an observed fact, inference, or unverified
   hypothesis, with file/symbol references and confidence. Documentation establishes intent; source establishes
   implementation; test results establish only what was exercised. Distinguish unavailable evidence from absent
   functionality, and report checks actually run and their limits.
4. **Prioritize** — rank recommendations by release risk, user value, evidence strength, effort, and dependencies;
   schedule prerequisites first. Separate implementation risk from the risk of leaving the issue unresolved. Respect
   local invariants and balance scope against team capacity and milestones.
5. **Report** — produce the five-heading report below with stable recommendation IDs.
6. **Self-check** — run the pre-return checklist before delivering.

If the user asks for a quick pass, stop after scope, the top findings, and the roadmap's quick wins, and say what was
not reviewed. Sparse artifacts warrant a bounded preliminary assessment plus a list of evidence needed to deepen it.

## Assess all eight areas

| Area                            | Investigation targets                                                                                                                |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Architecture and modules        | Dependency direction/cycles, ownership, lifecycle, ECS/service boundaries, threading, platform coupling                              |
| Rendering and API abstraction   | Implemented versus planned backends, capabilities/fallback, command/resource ownership, synchronization, render graph fit            |
| Shaders, materials, passes, GPU | Compilation/variants, binding layouts, precision/color space, pass dependencies, culling/batching, bandwidth, allocations, readbacks |
| Editor and content workflow     | Undo/persistence, import/reimport, asset identity, errors, iteration time, runtime parity, UI/render thread work                   |
| CPU/GPU profiling               | Representative workloads, frame-time tails, allocations/GC, simulation, submission versus execution, memory/stalls                   |
| Builds, platforms, delivery     | Toolchains, native loading/ABI, shader artifacts, incremental builds, CI coverage, reproducible packaging/distribution               |
| Quality and maintainability     | Tests at useful seams, graphics validation, cancellation/errors, API contracts, documentation accuracy                               |
| Debt, risk, scalability         | Concrete failure modes, content/team growth limits, migration cost, release blockers, support burden                                 |

An area may be marked insufficient evidence without inventing a defect or recommendation. Networking/netcode, audio,
localization, and platform certification are not part of the default eight: assess them when central to the project's
goals, and state them as out of scope otherwise. For deeper graphics or JVM/build analysis, read
[references/assessment-guide.md](references/assessment-guide.md). Verify time-sensitive API/tool claims against official
documentation appropriate to repository versions and link supporting sources. External guidance cannot establish a
repository defect.

## Prioritize and report

Return Markdown with these headings (a fill-in template is at
[references/report-template.md](references/report-template.md); delete empty sections rather than
writing "N/A"):

1. **Project understanding** — goals, stack, module/data flow, current capabilities.
2. **Scope, assumptions, and questions** — inspected artifacts, omissions, checks, unknowns.
3. **Assessment** — all eight areas, including strengths and evidence limitations.
4. **Well applied** — what is done well, with references; this shows the team's intended style and
   prevents "fixing" sound design.
5. **Prioritized roadmap** — quick wins, medium-term improvements, long-term architectural changes.
6. **Immediate next steps** — smallest useful actions and decisions needed to start, referencing roadmap IDs rather than
   duplicating recommendation details.
7. **Method and limits** — sampled vertical slices, unreviewed areas, evidence labels, checks run.

Assign stable recommendation IDs. Every recommendation needs these fields:

| ID / priority / phase | Action and evidence | Rationale | Expected impact | Effort | Risk: implementation / unresolved issue | Dependencies | Success metric |
|-----------------------|---------------------|-----------|-----------------|--------|-----------------------------------------|--------------|----------------|

Use effort ranges in person-days/weeks, with assumptions, confidence, and validation scope. Explain priority using
release risk, user value, evidence strength, effort, and dependencies; schedule prerequisites first. Separate
implementation risk from the risk of leaving the issue unresolved. A compact roadmap may link to detailed
recommendations retaining every field.

**Example entry (compact):**

> **RA-03** — *Medium, medium-term* — Move texture uploads off the UI thread during asset import. Evidence (observed):
> `editor/EditorPanel.kt` uploads decoded textures on the Swing event thread; no timing data exists. Rationale: uploads
> block input handling; impact is hypothesized, not measured. Expected impact: attributable p95 editor latency during
> large imports. Effort: 2–4 person-days, assuming a profiling hook. Risk: implementation low; unresolved — import-time
> freezes continue. Dependencies: disposable assets, representative hardware. Success metric: repeatable CPU/GPU traces
> and p95 interaction delay against an agreed budget; establishing that baseline is the first milestone, so no speedup
> is claimed yet.

For performance recommendations specify workload, hardware, baseline, proposed target, and acceptance check. If the
baseline is unknown, establishing it is the first milestone; do not invent measured values or promise speedups. For
other recommendations use relevant acceptance checks, such as artifact inspection or a regression test. Backend
migrations and render graphs require demonstrated benefit, platform need, and affordable maintenance. Include phased
rollout and rollback for disruptive changes.

Respect local invariants and balance scope against team capacity and milestones. Produce analysis and planning; write
implementation code or alter project behavior only when separately requested.

## Before returning

- All eight areas addressed, or explicitly marked insufficient evidence — no invented defects.
- Every recommendation carries all required fields and a stable ID; compact roadmaps may link to full entries.
- No invented measurements; unknown baselines are stated, with establishing them as the first milestone.
- Findings labeled fact / inference / hypothesis with references; checks actually run and their limits stated.
- Priorities consistent with stated capacity and milestones; prerequisites scheduled first.
- Sampled paths and unreviewed areas named; external claims verified against version-appropriate sources.
