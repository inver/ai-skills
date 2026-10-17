# Audits and validation

Research/access date: 2026-10-11. Use this for requested audits, release readiness, and the relevant verification steps
of implementation tasks. [sources.md](sources.md) records authoritative contracts; checklist choices below are
engineering recommendations.

## Establish scope and evidence

Identify whether the request covers a diff, feature, release readiness, or the whole plugin. For broad audits, map
descriptor entry points to service ownership, model reads/writes, UI callbacks, workers, and cleanup. State
products/builds and paths inspected. Do not claim whole-plugin coverage from a few classes.

Prioritize lost edits/undo, crashes/deadlocks, freezes, retained projects/workers, broken indexing behavior,
registrations/dependencies, and compatibility. Assess settings and user-facing consistency where relevant. Put style
preferences and architectural suggestions after confirmed functional risks.

Search leads include action updates, read/write/command APIs, scheduling, synchronous refresh, service constructors,
listener registration, bus connections, disposables, scopes/executors, broad catches, static project/editor references,
and internal API annotations. Trace callers and registration; a symbol's presence alone establishes no defect.

For each candidate finding establish:

- A reachable trigger and relevant input/lifecycle state.
- The actual thread, lock, modality, cancellation, or ownership contract.
- The resulting failure and user impact.
- Source location and supporting caller/descriptor evidence.
- The smallest viable correction and a way to verify it.

Unknown premises belong in investigation questions, not confirmed findings. Avoid duplicate findings with one root
cause.

## Report findings

Use the repository's severity convention if present; otherwise describe impact, reachability, and frequency. Give an
impact-focused title, file/line, trigger, mechanism, and remedy unless the user requests findings only. Separate
confirmed findings from optional improvements. A restart-only plugin is not automatically defective because it cannot
unload; background execution alone does not establish thread safety. A discouraged disposable parent is a contract
concern, but a claimed leak needs an ownership path and a lifecycle transition that actually leaves the resource alive.
Explain the difference, especially when restart-only behavior removes the unload scenario.

If nothing is confirmed, say so and identify coverage limits. Include performed and unperformed checks. Do not remediate
during an audit unless authorized.

## Select validation

Use existing module-qualified tasks and CI configuration. Validate failure mechanisms, not implementation details.

| Affected behavior       | Useful evidence                                                                                 |
|-------------------------|-------------------------------------------------------------------------------------------------|
| Document/PSI writes     | Unsaved buffers, writability failures, undo/redo, committed PSI when needed                     |
| Background work         | Cancellation, superseded input, project close, write contention, late UI publication            |
| Actions/indexes         | No-project context, state transitions, actual dumb-mode behavior, update-thread contract        |
| Resources/views         | Close/reopen cleanup, workers stopped, listeners removed, unload if supported                   |
| Compatibility/packaging | Actual archive, configured verifier matrix/reports, dependency descriptors                      |
| Responsiveness          | Measured callback duration, thread dumps/profile, realistic input scale                         |
| Kotlin analysis         | Target Kotlin plugin/K2 mode, unresolved code, indexing, session/pointer lifetime               |
| JSON/settings           | Round trips, missing/null/default values, annotation targets, old settings migration            |
| Optional integrations   | Plugin dependency installed, absent, disabled; registrations do not force class loading         |
| Split mode              | Monolithic and frontend/backend runs, correct module placement, latency and disconnect behavior |

Consult [platform-contracts.md](platform-contracts.md) for contracts and official sources. Fixture tests, builds, and
verifier reports provide complementary evidence. State which claims they support and what remains untested. Do not
publish, change IDE support ranges, or add broad suppressions incidentally to make checks pass.

## Plugin Verifier and release workflow

1. Discover tasks with the project's Gradle wrapper (for example, `./gradlew tasks --all`) and inspect CI. Use
   module-qualified task paths. Do not assume `check` invokes compatibility verification.
2. Confirm the resolved SDK, patched `since-build`/`until-build`, target products, Java/Kotlin bytecode/runtime
   constraints, and optional dependencies. Omitting an upper bound admits future builds; it is not evidence those builds
   were tested. [Build Number Ranges](https://plugins.jetbrains.com/docs/intellij/build-number-ranges.html).
3. Run relevant tests and build the distributable archive. Run available configuration/structure checks; these are
   distinct from binary verification. With 2.x, use `verifyPlugin`; legacy 1.x uses `runPluginVerifier`. Resolve other
   task names from the installed version: current 2.x docs use `verifyPluginProjectConfiguration`, while older examples
   use
   `verifyPluginConfiguration`. [Gradle tasks](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-tasks.html), [1.x migration](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-migration.html).
4. Configure a finite, explicit IDE matrix covering the minimum supported build, release-line boundaries affected by
   used APIs, and current supported product builds. For 2.x, inspect `intellijPlatform.pluginVerification.ides` and the
   resulting IDE list. Treat `recommended()` as a starting point to inspect, not automatic proof that every promised
   product/build was
   covered. [Verification configuration](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-extension.html#pluginverification).
5. Check every IDE's report, unresolved dependencies, internal/deprecated API findings, selected failure levels, and
   ignored-problem files. A successful task can reflect permissive failure policy or exclusions. Narrow unavoidable
   exclusions to a documented issue/build scope with an owner and follow-up; never suppress an entire platform namespace
   to obtain green CI. Record skipped tasks or download failures as unperformed
   verification. [Verifier](https://plugins.jetbrains.com/docs/intellij/verifying-plugin-compatibility.html), [task report/failure options](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-tasks.html#verifyplugin).
6. Run the affected sandbox scenarios: UI, settings persistence, project/view disposal, unload/reload when supported,
   and split mode if advertised. Archive CI reports with the tested plugin artifact, exact IDE builds, verifier/tool
   versions, commands, and limitations. Binary checks do not replace runtime
   evidence. [Testing Overview](https://plugins.jetbrains.com/docs/intellij/testing-plugins.html).

For a narrowly scoped edit, select checks proportional to the changed contract; use the full matrix for release
readiness or changes affecting compatibility, descriptors, dependencies, packaging, or public platform API use. A
documentation-only skill audit has no plugin binary to verify: report that distinction rather than claiming a verifier
pass.
