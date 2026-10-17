---
name: review-game-editor-product
description: >
  Conduct structured product reviews of game editor software.
  Evaluates editor-specific UX ergonomics (viewport navigation,
  scene hierarchy management, asset pipeline friction, iteration
  speed, undo/redo depth, dockable panel management) alongside
  general product criteria. Produces evidence-grounded
  recommendations with a comparison framework anchored in
  real editors (Unity, Godot, Unreal, GameMaker, Construct 3,
  GDevelop). Use for reviewing any game editor, whether
  commercial, open-source, or internal.
license: Apache 2.0
compatibility: opencode
metadata:
  version: "1.0.0"
  tags:
    - game developing
    - scene editor
    - game editor
  changelog: >
---

# Game Editor Product Review

Advise product and engineering leadership with practical decisions grounded in the editor's audience, maturity, and
constraints. Apply experienced product-management and game-design judgment without claiming personal employment history.
Review the product; do not implement changes unless separately requested.

## Context and evidence

Establish the product vision, primary creators and skill levels, 2D/3D and publishing targets, maturity, existing
workflow, business model, team capacity, and constraints from supplied context. Inspect local instructions,
representative project materials, screenshots, demos, metrics, and feedback. Distinguish implemented behavior from
plans.

Record the reviewed build/version, OS, input devices, display configuration, project scale, and review method. State
which interactions were directly inspected and which were unavailable. A screenshot can establish visible layout, not
usability; code or documentation can establish capability, not adoption, performance, or demand.

For each material finding, record an evidence ID, source location, observation or claim, scope, and confidence with its
reason. Separate direct observations, vendor documentation, independent evaluations, user reports, assumptions, and
hypotheses. Confidence in a documented capability is not confidence in its usefulness to this audience. Do not invent
research, benchmarks, metrics, revenue, capacity, or competitor capabilities.

For web evidence, cite the specific URL, publication/update date (or “not stated”), access date, product/version, and
evidence type. Prefer current primary documentation for capabilities and commercial terms. Use independent evaluations
and user reports to identify friction; record their task, audience, version, and limitations. A report of a bug does not
establish its prevalence or continued presence. Missing documentation means unknown, not absent. Separate stable
features from preview, beta, experimental, plugin-provided, and planned capabilities. Keep Unity Editor distinct from
Unity Studio, and Unreal Engine distinct from UEFN.

If missing information could change positioning or priority, ask at most five focused clarifying questions. Continue
independent analysis with labeled assumptions and conditional advice. If the user requests a report without an
interview, put those questions in the report and proceed. Do not make every unknown a blocker.

## Decision criteria

Evaluate usability, power, speed, extensibility, collaboration, learning curve, ecosystem, retention, and business
viability through creation → testing → iteration → sharing/publishing → return to work. Establish the audience's
essential outcomes before comparing feature counts. Assess these editor-specific dimensions:

| Dimension                    | Evaluate through the creator's task                                                                                                                                                                                |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Viewport and workspace       | Navigation, selection, gizmos, snapping, local/world space, 2D/3D clarity, panel recovery, keyboard workflows, and accessibility.                                                                                  |
| Scene organization and reuse | Search/filter, nesting, reparenting, bulk edits, visibility/locking, reusable instances, overrides, references, and behavior at representative project scale.                                                      |
| Asset pipeline               | Import/reimport/export, IDs and references after move/rename, dependencies, actionable errors, external-tool round trips, licenses, and package/plugin compatibility.                                              |
| Iteration and diagnostics    | Cold/warm startup, edit-to-visible-result time, asset import, script compile/reload, entering play, debugging, build/deploy, and editor/runtime consistency.                                                       |
| Trust and recovery           | Undo scope and transaction grouping, redo, save/reopen, autosave/crash recovery, migration, backups, and recovery from failed imports or extensions.                                                               |
| Collaboration                | Asynchronous version control, diffs/merges/locks, review and permissions, cloud dependency, live co-editing conflict/undo semantics, and offline/reconnection behavior. Runtime multiplayer is a separate concern. |
| Reach and viability          | Supported authoring hardware/platforms, export restrictions, accessibility, learning resources, switching costs, operating costs, and sustainable support.                                                         |

Mark irrelevant dimensions N/A with a reason; a focused 2D editor does not need 3D or co-editing to receive a positive
assessment. Treat project integrity as a foundation even without explicit feature requests. Tie technical risks to lost
work, slow iteration, broken projects, or blocked publishing without turning this into an architecture audit.

Choose representative tasks: a new creator's first meaningful result, a returning creator's edit-test-save loop, and a
recovery or team handoff where relevant. Use the ergonomics checklist below. When hands-on access is unavailable,
provide test procedures and unknowns instead of pass/fail verdicts.

For timings, define start/end events, hardware, build, project size, language, target platform, cache state, and
repetitions. Separate startup, import, compile, reload, play, and deployment. Report completion/errors/assistance
alongside elapsed time; never compare unmatched projects as an engine ranking. Check whether live edits persist, reset
state, or require a restart. An opening-to-placement target such as 60 seconds is a proposed usability hypothesis, not
an industry benchmark or activation definition. Preserve an explicit user-specified target as a requirement while
separately assessing its feasibility and empirical justification.

Prioritize foundations, activation, retention, and then speculative expansion. Recommend marketplaces, collaboration, AI
features, and monetization only when audience need and capacity justify them. For AI-assisted editing, assess reviewable
changes, undo, scope control, correctness in the running game, provenance, data handling, latency/cost, and a manual
fallback. Measure accepted useful results including correction time, not generated output volume. For cloud workflows,
assess ownership/export, availability, permissions, service costs, and recovery. Do not infer that an emerging feature
is necessary because a competitor advertises it.

## Recommendation contract

Assign stable IDs. Put complete entries in the roadmap; other sections reference those IDs. A finding alone need not
become a recommendation. Every recommendation includes these six fields:

| Field                | Required content                                                                                                                                                                                                                                                   |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Problem              | Affected creator and task, observed friction or labeled hypothesis, evidence IDs, and confidence with its basis.                                                                                                                                                   |
| Proposed change      | Concrete behavior, experiment, or deliverable; minimum useful scope; acceptance condition; and exclusions needed to prevent scope creep.                                                                                                                           |
| User/business impact | Expected creator outcome and causal link to activation, retention, publishing, cost, or revenue where relevant. Separate expected impact from measured impact.                                                                                                     |
| Effort/risk          | Estimate and basis, or unknown plus a sizing step; dependencies and suggested responsible role. Address project/scene/asset migration, extension compatibility, editor/runtime divergence, and recovery/rollback when relevant; mark non-applicable risks briefly. |
| Priority             | Unique rank and Now/Next/Later, rationale against the primary bottleneck, prerequisites, and what is deferred. Now is a decision order, not a delivery promise.                                                                                                    |
| Success metric       | Event/outcome, population and denominator, measurement window, collection method, baseline or baseline-collection plan, proposed target/decision rule, and quality guardrail. State what result triggers proceed, revise, or stop.                                 |

Label effort and targets as estimates. Do not invent numeric thresholds when a baseline study or bounded acceptance test
is the appropriate next step. Prefer ranked Now/Next/Later when reach and confidence data are unavailable; if using
RICE, explain scales, reach window, inputs, and uncertainty. Keep project-integrity failures visible rather than
averaging them away in an aggregate score.

## Competitive differentiation framework

Compare alternatives serving the same creator job, including the current manual workflow or “do nothing.” Choose
comparators by audience, authoring platform, 2D/3D scope, team workflow, publishing destination, and switching
constraints. Use the reference seeds below only when relevant; do not force every editor into every review.

Screen these ten dimensions: editor UX/UI; scene/level editing; iteration; asset pipeline; scripting/extensibility;
collaboration; onboarding; ecosystem; pricing/licensing; target audience. Expand decision-relevant dimensions and mark
others N/A with a reason; provide full coverage when requested. Split wide tables if necessary. Use this record for
decision-relevant comparisons:

| Creator job / dimension | Required outcome and importance | Alternative and version | Documented capability / delivery status | Observed task result or unknown | Evidence type, URL/date, confidence | Constraint, switching cost, and product implication |
|-------------------------|---------------------------------|-------------------------|-----------------------------------------|---------------------------------|-------------------------------------|-----------------------------------------------------|

Use documented, observed, reported, unknown, or N/A explicitly. Do not score unknown as zero or rank products by feature
count. If weights help, explain their audience-based rationale and test whether reasonable changes alter the
recommendation. Distinguish availability from quality, beginner onboarding from expert throughput, and built-in
capability from a paid plugin or external service. Evaluate documentation by completing a version-matched task, not by
counting pages; evaluate ecosystem relevance and maintenance, not unsupported popularity claims.

For pricing, identify currency, billing period, per-seat versus per-product basis, revenue/funding thresholds and their
windows, commercial/export rights, royalty exclusions, and service/plugin costs as relevant. Verify terms at review
time; free engine licensing does not imply zero production cost. Treat vendor pricing summaries as inputs, not a
substitute for applicable terms.

**Parity versus wedge:**

1. Protect foundations: reliable edits, save/recovery, and essential workflow access are product-quality obligations; do
   not wait for creators to request them by name.
2. Recommend minimum sufficient parity when a missing outcome blocks the primary workflow or switching. Support this
   with observed failures, credible workflow evidence, or corroborated feedback. Compare building, integrating, and
   using an existing workaround; include ongoing support cost. Do not require copying a competitor's entire
   implementation.
3. Recommend a wedge when an underserved job, demonstrated team strength, and plausible adoption/switching benefit
   align. Specify the outcome to outperform and what broader capability will be deferred. Competitor expense alone does
   not establish demand for a wedge.
4. If need, advantage, or capacity is uncertain, recommend a bounded validation or sizing task with a decision gate.
   Minimum parity and a differentiated workflow can coexist. State evidence, opportunity cost, and the rejected
   alternative.

### Comparison seeds

These are research starting points, not a current ranking. Vendor sources below were consulted on 2026-10-10; undated
manuals have no verified publication date. Recheck versions and terms when making a recommendation. Build the
ten-dimension comparison above from fresh evidence.

| Alternative / source                                                                                                                               | Relevant comparison                                                                                | Limitation to preserve                                                                                                  |
|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| [Unity Editor 6.3 play-mode configuration](https://docs.unity3d.com/6000.3/Documentation/Manual/configurable-enter-play-mode.html), undated manual | Test iteration with domain/scene reload settings and reusable-object workflows.                    | Reload settings affect state reset; do not infer universal C# hot reload or attach Unity Studio claims to Unity Editor. |
| [Godot 4.6 release](https://godotengine.org/releases/4.6/), released 2026-01-26                                                                    | Compare scene-oriented creation, workspace flexibility, and creator iteration.                     | Documented UX changes do not establish usability superiority or measured speed.                                         |
| [Unreal Engine 5.6 release](https://www.unrealengine.com/news/unreal-engine-5-6-is-now-available), 2025-06-03                                      | Compare demanding 3D authoring, viewport tools, content organization, and target-device iteration. | Preserve beta/experimental labels; UEFN is a separate comparison.                                                       |
| [GameMaker features](https://gamemaker.io/en/features), undated                                                                                    | Compare focused 2D creation and transitions between visual and textual scripting.                  | Validate fit for the specific creator; “beginner” does not establish low learning cost.                                 |
| [Construct 2025 review](https://www.construct.net/en/blogs/construct-official-blog-1/construct-2025-year-review-1898), 2025-12-19                  | Compare browser authoring, event/code workflows, asset discovery, and workspace use.               | Browser delivery, cloud saves, and live co-editing are different capabilities.                                          |

Add Roblox Studio for platform publishing or shared creation, GDevelop for event-driven authoring, or another specialist
only when it matches the job; verify its capabilities rather than inferring them from its category.

## Editor ergonomics checklist

Record task, observed/documented status, pass/partial/fail/unknown/N/A, evidence, consequence, and follow-up. A
documented feature alone cannot pass a usability test. Use representative project copies for destructive/recovery tests
and disclose untested cases.

| Area                        | Test or observation                                                                                                                                                                                                                                                                    |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| First run and return        | From a defined start state, create/open a project, place content, test a meaningful result, save, close, and resume. Separate installation/login/import from ready-editor placement; record assistance. Inspect samples, empty states, contextual help, and version-matched tutorials. |
| Viewport                    | Select overlapping/hidden objects, frame selection, pan/orbit/zoom, transform precisely, snap, switch coordinate modes, and distinguish editor camera from game camera. Test mouse/trackpad and relevant 2D/3D modes.                                                                  |
| Hierarchy and reuse         | Find an object in a representative large scene, reparent safely, edit several objects, lock/hide, create an instance, inspect/apply/revert overrides, and follow a broken reference.                                                                                                   |
| Panels and focus            | Dock/float/resize, maximize or reduce distractions, save/restore layouts, reconnect monitors, and recover off-screen panels. Inspect inspector behavior when selection or mode changes.                                                                                                |
| Shortcuts and accessibility | Discover/remap commands; check conflicts, focus visibility/order, non-US layouts, keyboard-only task paths, text scaling, contrast, non-color cues, and assistive-technology support where testable. Theme availability alone does not prove accessibility.                            |
| Undo and recovery           | Undo/redo transforms, property edits, deletion/reparenting, bulk actions, and supported asset changes; test transaction grouping and history boundaries across save/play/import. Check what cannot be undone, whether that is communicated, and whether backup recovery works.         |
| Assets and iteration        | Import, rename/move, reimport, resolve missing dependencies, test changed scripts/assets, read errors, and deploy a representative build. Record state preservation, stalls, failures, and editor/runtime mismatches.                                                                  |
| Collaboration, if relevant  | Have two users edit conflicting content, resolve it, undo locally, disconnect/reconnect, and recover a prior version. Distinguish live object changes, save-time asset sync, version control, cloud storage, and runtime multiplayer.                                                  |

## Report format

Return the Markdown review in the following order, with Clarifying questions first when needed. Honor an explicit
user-requested format. Keep unsupported sections brief and label unknown/N/A rather than padding them.

1. **Executive summary** — Up to five supported findings and five ranked recommendations linked to IDs; state the
   primary audience, bottleneck, and decision.
2. **Understanding & assumptions** — Scope, audience, success criteria, build/environment, evidence coverage, review
   limitations, and assumptions.
3. **Current-state assessment** — Evidence-backed strengths, weaknesses, opportunities, and threats; distinguish
   confidence and uncertainty.
4. **Target users & jobs-to-be-done** — Rank the primary audience; label inferred personas; describe actual tasks,
   constraints, and pain points.
5. **Core loops** — Creation, testing, iteration, publishing, and return-to-work; identify external/unsupported steps
   and handoffs.
6. **Feature audit** — Feature, existing/planned status, keep/improve/add/remove verdict, rationale/evidence, priority,
   and recommendation ID. Keep means no recommended change.
7. **UX/UI & onboarding** — Report representative tasks and checklist results, including first run, discoverability,
   viewport/hierarchy, shortcuts, panels, accessibility, undo/recovery, and measured or unknown iteration times.
8. **Technical/product risks** — Integrity, performance/scalability, migrations, extensions, editor/runtime divergence,
   platform and service dependencies, with creator/business consequences.
9. **Ecosystem & community** — Relevant assets, templates, plugins, docs, tutorials, support, and collaboration needs;
   distinguish availability from quality and maintenance.
10. **Competitive differentiation** — Use the ten-dimension framework, cited versioned comparison, parity/wedge
    decision, switching costs, and explicit non-goals.
11. **Monetization & business model** — Applicable pricing/terms, costs to serve/support, and evidence of willingness to
    pay; label unknown or premature commercial assumptions.
12. **Prioritized roadmap** — Complete six-field recommendation entries with stable IDs, ranks, dependencies, and
    deferrals.
13. **Metrics & KPIs** — Define meaningful creator outcomes, events, denominators, cohorts/windows, collection methods,
    baselines, and guardrails. Opening an editor is not activation; saving is not publishing. Distinguish voluntary
    return from recovery after crashes.
14. **Open questions** — Remaining uncertainties, how to resolve them, and which decisions they block.
15. **Recommended next steps** — Roles, deliverables, and decision gates tied to recommendation IDs. Use a conditional
    30/60/90-day plan only when capacity supports it or the user requests one; otherwise use Now/Next/Later without
    delivery promises.

Before returning, verify source-to-claim support, product/version boundaries, recommendation completeness, consistent
priorities, and feasibility against stated capacity. Label estimates and unknowns; no recommendation may appear only in
a summary without a complete roadmap entry.

## Glossary

- **Viewport:** Interactive view of authored 2D/3D content; distinguish it from the runtime camera's output.
- **Hierarchy / scene tree / outliner:** Displays scene objects and relationships; organization, transform parenting,
  and ownership can have different semantics.
- **Node (Godot):** A scene building block. A saved scene can be instantiated within another scene.
- **Prefab (Unity):** Reusable GameObject configuration with instance overrides; verify nesting and override behavior in
  the reviewed version.
- **Blueprint (Unreal):** Visual scripting system; a Blueprint Class defines a class that can be instantiated. It is not
  a semantic synonym for a Unity Prefab or Godot scene.
- **GDScript / GML / event sheet:** Respectively Godot's scripting language, GameMaker Language, and a condition/action
  authoring structure used by tools such as Construct. These are distinct programming models.
- **Reimport / live reload / hot reload:** Respectively rebuilding imported data and vendor-specific mechanisms for
  applying changes. Specify asset versus code, supported language/platform, state preservation, and restart
  requirements; names alone do not establish equivalence.
- **Play-in-editor (PIE):** Testing through editor-managed play; viewport, separate-window, and process modes vary. It
  does not prove packaged-build equivalence.
- **Undo depth and scope:** Depth is retained history capacity; scope is which operations/state are reversible. Neither
  establishes recovery reliability by itself.
- **Co-editing / version control / runtime multiplayer:** Shared authoring, change history and integration, and players
  sharing a running game. Evaluate each separately.
