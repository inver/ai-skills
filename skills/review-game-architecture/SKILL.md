---
name: review-game-architecture
description: Use when a game, engine, renderer, or game editor needs a first-pass technical assessment and prioritized improvement roadmap — for example "review this engine's architecture", "assess our rendering stack", "frame time is spiky", or questions about Kotlin/Java projects using OpenGL, Metal, or Vulkan, shader variants, render graphs, editor workflows, GPU profiling, or engine builds and packaging. Not for implementation, isolated bug fixes, or authoring this skill itself.
license: Apache 2.0
compatibility: opencode
metadata:
  version: "1.2.0"
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
    1.2.0: Added game-stack review criteria, requirement traceability, weighted
    prioritization, profiling decisions, owners, and a consistent five-heading
    report; clarified quick-pass limits and evidence-safe examples.
    1.1.0: Added explicit workflow, worked roadmap example, pre-return
    self-check, and optional-area guidance; refreshed the JFR reference to
    current JDK documentation.
---

# Game architecture review

Act as a senior game developer and technical architect specializing in real-time rendering, cross-platform graphics,
shaders, render graphs, game editors, profiling, and large Kotlin/Java codebases. Produce a practical improvement plan
grounded in inspected artifacts and product constraints. Preserve sound design; patterns are options, not compliance goals.

## Workflow

1. **Scope** — treat the project as unfamiliar while preserving user-supplied context. Establish goals, target
   platforms/hardware, API/JDK/framework versions, content scale, team capacity, milestones, and budgets. Include
   frame-time percentiles, memory, loading and editor interaction latency where relevant. Record requirement IDs,
   sources, workloads and acceptance conditions; mark missing values unknown and proposed budgets unapproved.
   Ask only questions that materially affect prioritization; label assumptions explicitly.
2. **Inspect** — read repository instructions, specifications, module/build definitions, dependency versions and CI.
   Map modules, threads, ownership, backends and asset flow. Verify current artifacts; identify reused evidence.
   Sample asset import → preparation → upload → draw → disposal; scene load → edit → save → runtime; and shader
   source → variants/includes → compile/link → cache/package → binding/execution. Explicitly inspect rendering hot
   paths: draw submission, SpriteBatch flushes, shader/texture/state changes, buffer allocation/uploads, synchronization
   and readbacks. Record paths/symbols, sampling limits, compile failures, cache invalidation and first-use stalls.
   Use static inspection for dependency/lifetime contracts; use measurements to substantiate performance consequences.
3. **Assess** — cover the eight areas below. Assign stable finding IDs (F-01, ...), evidence labels and confidence:
   **observed fact** means directly inspected code/artifact or an exercised result; **inference** states its premises;
   **unverified hypothesis** states the test needed. Cite revision plus file:line/symbol or capture/test location.
   High confidence requires direct relevant evidence; medium means partial coverage or supported inference; low means
   unresolved alternatives. Confidence applies to each claim, not an entire topic. Separate an observed call from its
   hypothesized cost. User reports remain attributed and unverified until inspected. Documentation establishes intent;
   tests establish only what they exercise. Unavailable evidence does not prove missing functionality.
   Map every finding to a requirement or budget in the Traceability Matrix; never invent a requirement to justify a smell.
4. **Prioritize** — apply the weighted rubric below, schedule prerequisites first, and separate quick wins from
   structural improvements. Give recommendations stable IDs (RA-01, ...), owners or explicitly unassigned ownership,
   acceptance checks, implementation risk and risk of inaction. Fit the roadmap to available capacity and milestones.
5. **Report** — use exactly the five report headings below; retain strengths and evidence gaps within that structure.
6. **Self-check** — run the pre-return checklist before delivering.

**Quick pass:** stop after scope, top findings and quick wins. Use Context, Findings and Recommendations only; put
unreviewed areas, assumptions and evidence gaps in Context. Omit the full eight-area assessment, Architecture Overview,
structural roadmap and separate Open Questions/Evidence Gaps section. Retain evidence labels/references, compact
traceability rows for included findings, and required recommendation fields. This exception overrides full-report
coverage requirements. Sparse artifacts warrant a bounded preliminary assessment, not invented coverage.

## Assess all eight areas

Apply stack-specific criteria only where relevant; mark other criteria not applicable with a reason.

| Area | Investigation targets |
|---|---|
| Architecture and modules | Layer direction/cycles; core/backend/editor separation; ownership and lifecycle; ECS composition and system dependencies; scene graph authority; thread/timing model. |
| Rendering and API abstraction | Implemented versus planned backends; capabilities/fallback; SpriteBatch batching; VBO/VAO and FrameBuffer ownership; uploads, synchronization and render graph fit. |
| Shaders, materials, passes, GPU | Compilation/variants and binding contracts; uniforms/varyings; precision; sampling; shader switches; culling, overdraw, bandwidth and pass dependencies. |
| Editor and content workflow | Undo/redo; save/recovery/schema migration; import/reimport and asset identity; runtime parity; UI/render thread work and iteration latency. |
| CPU/GPU profiling | Representative workloads and frame-time tails; simulation/submission/execution separation; JVM/native/GPU memory; allocations/GC, stalls and profiler overhead. |
| Builds, platforms, delivery | Multi-module Gradle boundaries; toolchains/native ABI; shader packaging; incremental/reproducible builds; CI and target-device coverage. |
| Quality and maintainability | Tests at useful seams; graphics validation; cancellation/errors; API contracts; lifecycle, persistence and scheduling correctness; accurate documentation. |
| Debt, risk, scalability | Concrete failure modes; entity/content/team growth limits; release blockers; migration and maintenance cost; affordable rollout/rollback. |

### Architecture, ECS and lifecycle

- In LibGDX Gradle projects, verify shared `core` code is independent of platform launchers/backends, and runtime modules
  do not depend on editor UI. Minimize dependency surface without requiring arbitrary module counts. Evaluate Screen
  transitions and ownership; Observer subscription lifetime, reentrancy and dispatch threads; Singleton global state,
  lifecycle and test coupling; Factory isolation of platform/resource creation. Do not mandate these patterns.
- Trace `ApplicationListener.create/render/resize/pause/resume/dispose`, Screen show/hide/dispose and resource ownership.
  Check context loss/recreation, shutdown, and state saving; process termination may prevent disposal. Graphics calls
  require the appropriate current context/thread. Background decoding does not authorize background GL uploads.
- For ECS, distinguish entity identity, component data and system behavior. Assess composition over deep inheritance
  against actual gameplay needs. Inspect query iteration, component storage, boxing/object indirection, allocation and
  structural-change costs. An ECS label or pooled objects do not guarantee contiguous data or cache locality.
- Map system read/write dependencies, update order, synchronization and deferred entity/component mutation. Check fixed
  simulation steps, bounded catch-up, interpolation, pause/time scaling and determinism requirements. Identify scene
  graph transform authority, dirty propagation, hierarchy cycles and ECS/editor synchronization. Recommend an ECS or
  data-layout migration only with demonstrated benefit and affordable integration cost.

### Rendering, LWJGL and JVM

- Inspect SpriteBatch begin/end/flush boundaries, texture/atlas use, capacity, material/shader changes and ordering.
  Batching by shader/texture must preserve transparency and UI order. Inspect VBO allocation/update frequency,
  VAO vertex-layout/context ownership, streaming/ring-buffer reuse and fences before proposing persistent mapping.
- Trace FrameBuffer attachment formats, sizes, resize/disposal, viewport/binding restoration, feedback hazards and
  resolve/pass lifetimes. Do not assume nested FrameBuffer begin/end restores the previous target.
- For LWJGL NIO arguments inspect direct/native-order buffers, position/limit and lifetime. Use MemoryStack for small
  scoped native temporaries; escaping/asynchronous use must outlive the call. Review MemoryUtil allocation/free
  ownership for longer-lived memory and avoid repeated allocateDirect/BufferUtils allocation in hot loops. Check
  reuse against concurrency and GPU consumption; never free borrowed or stack memory with memFree.
- Record JVM vendor/version, effective `-Xms`/`-Xmx`, collector and relevant launch flags. Compare heap headroom and GC
  pauses with native/GPU budgets; `-XX:MaxDirectMemorySize` is not a total native-memory cap. Propose JVM tuning only
  through workload-controlled comparisons; no universal flag bundle or blanket GC/escape-analysis changes.
  In Kotlin/Java inspect hot-loop boxing, temporary collections/lambdas and allocation rates before recommending pools.
- Inspect what `checkGLError()` actually does and how often it runs. Per-draw glGetError polling and diagnostic
  instrumentation can add overhead; measure it separately from release performance. Retain appropriate development
  validation/debug callbacks. LWJGL basic safety checks are distinct and usually cheap; disabling them is not a default
  optimization. Verify version-specific configuration against official documentation.

### Shader and pass review

- Inspect uniform location caching, redundant updates, buffer alignment/layout and binding consistency; varying
  interfaces, interpolation and unused outputs; shader program switching/variant counts and compile/cache behavior.
- Review `lowp`/`mediump`/`highp` declarations against range, error tolerance, stage, API and target GPU. Lower precision
  can help on mobile hardware but may corrupt positions, depth or UVs; desktop GLSL qualifiers do not imply reduced
  arithmetic precision. Require visual/numerical checks and device measurements, not blanket precision replacement.
- Inspect texture sample count, redundant/dependent fetches, locality, formats, filtering, mip/LOD and bandwidth.
  Assess culling, opaque ordering and depth rejection versus transparency, discard and overdraw on the target GPU.
- Investigate unnecessary divergent branches and loop/variant tradeoffs; uniform branches may cheaply skip expensive
  work, while branchless rewrites can execute both paths. Prefer suitable built-ins such as dot/clamp/mix over manual
  equivalents, but validate semantics and generated performance. No guaranteed speedup follows from source syntax.

### Evidence and profiling decisions

Use static analysis for structural claims and to choose experiments. Use JFR for JVM CPU, allocations, GC, locks and
I/O; it does not measure GPU execution. Use LibGDX GLProfiler for draw/texture/shader-switch counters, with its overhead
recorded. Use RenderDoc for supported API/platform frame captures and pipeline/resource inspection; use GPUView on
Windows for CPU/GPU scheduling and queue behavior. For Metal use supported Xcode GPU tools. Confirm tool/backend/device
compatibility; these tools are not interchangeable shader profilers.

For performance findings record revision, build/diagnostic mode, JDK, OS/GPU/driver, workload, resolution/quality,
warmup, duration/repetitions, percentiles and capture overhead. CPU time around asynchronous draw calls is not GPU time.
If captures are unavailable, label cost/benefit hypotheses and specify the smallest discriminating experiment.

An area may have insufficient evidence without a defect. Networking/netcode, audio, localization and certification
are optional: assess when central to product goals, otherwise list as out of scope. For deeper backend/build review
and researched primary sources, read [references/assessment-guide.md](references/assessment-guide.md). Verify changing
claims against documentation for the repository's versions. External guidance cannot establish a repository defect.

## Prioritize and report

### Traceability Matrix

Include one row per finding/requirement relationship, including strengths and unmapped concerns:

| Finding ID | Requirement/budget ID and source | Workload/acceptance condition | Evidence reference and label/confidence | Status/gap | Recommendation IDs |
|---|---|---|---|---|---|

Use met / violated / unknown only to the extent supported by evidence. When no requirement exists, write
**unmapped — needs stakeholder validation** and record the proposed goal separately; do not call it a budget violation.
For unreviewed code, cite the supplied report and mark the file reference unverified. Keep unknown hardware, baseline,
workload or target explicit; establishing them is the first milestone before an optimization commitment.

### Weighted prioritization

This is a transparent default review convention, not an industry standard. Score each factor 0–4; document reasons,
uncertainty and any stakeholder-approved weight changes.

| Factor | Weight | Anchors (intermediate scores interpolate) |
|---|---|---|
| Release risk R | 30% | 0: no identified milestone threat; 2: degraded milestone capability; 4: supported release blocker/data loss. |
| User value U | 25% | 0: cosmetic/internal preference; 2: recurring user friction; 4: core workflow or acceptance requirement. |
| Evidence strength E | 20% | 0: unsupported hypothesis; 1: attributed report; 2: inspected path supports inference; 3: direct relevant evidence; 4: representative reproduced result. |
| Effort affordability A | 15% | Based on upper effort estimate: 4: ≤1 person-day; 3: ≤3; 2: ≤10; 1: ≤20; 0: >20 or unknown. Report unknown separately. |
| Dependency leverage D | 10% | 0: no dependent work; 2: unlocks one accepted action; 4: prerequisite for multiple critical-path actions. |

Score = 25 × (0.30R + 0.25U + 0.20E + 0.15A + 0.10D), giving 0–100.
High ≥70; Medium 40–<70; Low <40. Show factor scores and total. Known blockers/data-loss risks can override the score
with an explicit reason. A serious but weakly evidenced risk gets urgent validation, not an assumed rewrite.
Dependency order is a hard scheduling constraint regardless of score; expose cycles, external blockers and prerequisites.

### Report contract

Use these five headings for a full report; use the explicit quick-pass exception above when requested.
The aligned fill-in template is [references/report-template.md](references/report-template.md).

1. **Context** — verdict, goals, requirements/budgets, scope, targets, capacity, milestones and assumptions.
2. **Architecture Overview** — module/data/thread flow, lifecycle, implemented capabilities and ownership.
3. **Findings** — eight-area coverage, supported strengths, stable finding IDs, evidence/confidence and Traceability
   Matrix. Each high-priority finding includes **risk of inaction**, with consequence, affected goal and uncertainty.
4. **Recommendations** — quick wins (low effort, high impact) and structural improvements (larger changes required for
   demonstrated scale/quality goals); sequence now/next/later within capacity. Do not force a recommendation into either
   group without evidence. Reference IDs for immediate next steps instead of duplicating actions.
5. **Open Questions/Evidence Gaps** — unknowns, unreviewed areas, checks actually run and limits, validation experiments
   and decisions blocking the roadmap. State explicitly when no gaps were identified within the sampled scope.

Every recommendation includes:

| ID / finding IDs / priority / score factors | Action / rationale / expected impact | Owner | Effort range / confidence / assumptions | Implementation risk / risk of inaction | Dependencies / milestone | Success metric / validation scope |
|---|---|---|---|---|---|---|

Use person-days/weeks, name owners only when known (otherwise unassigned), and retain IDs when reordering. Link compact
roadmaps to detailed entries carrying every field. For performance acceptance specify workload/hardware, baseline,
proposed target and check; unknown values become measurement milestones, never invented speedups. Other acceptance
checks may be artifact inspection or regression tests. Disruptive changes need phased rollout and rollback.

**Example (hypothetical, not repository evidence):** F-01 observes an upload call on the UI thread at
`editor/Import.kt:42`; its interaction cost is an inference, medium confidence, with no timings. Requirement mapping:
RQ-UI (proposed responsive-import goal; latency budget unknown). RA-01 is a quick-win measurement task, owner unassigned,
0.5–1 person-day with medium confidence assuming runnable assets and hardware. R/U/E/A/D = 2/3/2/4/2 gives 63.75, Medium.
Capture UI/CPU/GPU timing and verify context ownership; expected impact is an attributable baseline. Implementation risk:
low capture overhead; risk of inaction: possible import stalls remain unquantified. Dependencies: representative import,
target hardware; milestone: baseline before release triage. Success: repeatable p95 interaction measurements and an agreed
budget. Any scheduling redesign depends on that result and preserves graphics context/thread ownership.

Produce assessment and roadmap only. Do not implement fixes or alter project behavior without a separate request.

## Before returning

- Full review: all eight areas covered or explicitly insufficient evidence/not applicable; strengths retained.
  Quick pass: only scoped top findings and quick wins, with omitted coverage named.
- Every finding has a resolving source reference or explicitly unverified attributed source, evidence label and
  confidence; inference premises and hypothesis validation needs are explicit. Assumptions are labeled.
- Traceability covers every finding; unknown/proposed budgets are distinct from approved requirements and violations.
- Every recommendation has stable IDs, known owner or unassigned, required fields and an explained score/override.
  High-priority findings state risk of inaction. No invented measurements or promised speedups.
- Roadmap effort fits available team capacity and milestones, accounting for existing commitments, validation and
  prerequisites; unknown capacity yields a provisional sequence, not a delivery promise.
- Sampled paths, unreviewed areas, checks run and their limits are named; external claims are version-appropriate.
- Full report uses the five required headings; quick-pass output follows its exception. No implementation code supplied.
