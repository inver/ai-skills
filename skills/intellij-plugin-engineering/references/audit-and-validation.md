# Audits and validation

## Establish scope and evidence

Identify whether the request covers a diff, feature, release readiness, or the whole plugin. For broad audits, map descriptor entry points to service ownership, model reads/writes, UI callbacks, workers, and cleanup. State products/builds and paths inspected. Do not claim whole-plugin coverage from a few classes.

Prioritize lost edits/undo, crashes/deadlocks, freezes, retained projects/workers, broken indexing behavior, registrations/dependencies, and compatibility. Assess settings and user-facing consistency where relevant. Put style preferences and architectural suggestions after confirmed functional risks.

Search leads include action updates, read/write/command APIs, scheduling, synchronous refresh, service constructors, listener registration, bus connections, disposables, scopes/executors, broad catches, static project/editor references, and internal API annotations. Trace callers and registration; a symbol's presence alone establishes no defect.

For each candidate finding establish:

- A reachable trigger and relevant input/lifecycle state.
- The actual thread, lock, modality, cancellation, or ownership contract.
- The resulting failure and user impact.
- Source location and supporting caller/descriptor evidence.
- The smallest viable correction and a way to verify it.

Unknown premises belong in investigation questions, not confirmed findings. Avoid duplicate findings with one root cause.

## Report findings

Use the repository's severity convention if present; otherwise describe impact, reachability, and frequency. Give an impact-focused title, file/line, trigger, mechanism, and remedy unless the user requests findings only. Separate confirmed findings from optional improvements. A restart-only plugin is not automatically defective because it cannot unload; background execution alone does not establish thread safety. A discouraged disposable parent is a contract concern, but a claimed leak needs an ownership path and a lifecycle transition that actually leaves the resource alive. Explain the difference, especially when restart-only behavior removes the unload scenario.

If nothing is confirmed, say so and identify coverage limits. Include performed and unperformed checks. Do not remediate during an audit unless authorized.

## Select validation

Use existing module-qualified tasks and CI configuration. Validate failure mechanisms, not implementation details.

| Affected behavior | Useful evidence |
| --- | --- |
| Document/PSI writes | Unsaved buffers, writability failures, undo/redo, committed PSI when needed |
| Background work | Cancellation, superseded input, project close, write contention, late UI publication |
| Actions/indexes | No-project context, state transitions, actual dumb-mode behavior, update-thread contract |
| Resources/views | Close/reopen cleanup, workers stopped, listeners removed, unload if supported |
| Compatibility/packaging | Actual archive, configured verifier matrix/reports, dependency descriptors |
| Responsiveness | Measured callback duration, thread dumps/profile, realistic input scale |

Consult [platform-contracts.md](platform-contracts.md) for contracts and official sources. Fixture tests, builds, and verifier reports provide complementary evidence. State which claims they support and what remains untested. Do not publish, change IDE support ranges, or add broad suppressions incidentally to make checks pass.
