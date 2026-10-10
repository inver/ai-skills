# Platform contracts

Read relevant sections only. Synthesized from JetBrains documentation, researched 2026-10-10. Resolve version-sensitive details against the actual SDK and supported build range.

## Threading and modality

UI access belongs on EDT; model access requires the applicable platform read/write context. A thread or dispatcher alone does not establish every required lock. Avoid I/O, parsing, resolving, scans, or waiting for workers on EDT. Keep writes short and use platform scheduling with appropriate modality for model mutations; arbitrary Swing scheduling is insufficient.

Long background reads should allow pending writes and cooperate with cancellation. Restartable reads can execute repeatedly: keep irreversible side effects outside them. Recheck object validity after suspension, scheduling, or reacquiring access. Prefer immutable snapshots beyond the read boundary.

Source: [Threading Model](https://plugins.jetbrains.com/docs/intellij/threading-model.html).

## Cancellation and coroutine ownership

Propagate `ProcessCanceledException` and coroutine cancellation; do not log them as failures or turn them into successful empty results. Inspect broad catches and result wrappers. Long computation loops need context-appropriate cancellation checkpoints.

Source: [Background Processes](https://plugins.jetbrains.com/docs/intellij/background-processes.html).

Prefer platform-supported service coroutine scopes when suitable: they end with the service/container or plugin unload. Avoid `GlobalScope` and unowned scopes; never cancel a borrowed platform-wide scope. View operations may require a shorter owned child lifetime. Bound event-driven work and reject results whose input or owner changed.

Source: [Coroutine Scopes](https://plugins.jetbrains.com/docs/intellij/coroutine-scopes.html).

## Services and initialization

Choose application or project scope by ownership. Keep constructors cheap; defer work and dependent-service lookup until needed. Platform services do not support arbitrary constructor injection of other services; supported `Project` and `CoroutineScope` injection are distinct. Use final light services when their restrictions fit, and registered services for requirements such as overrides or public service interfaces. Avoid eager service lookup in static initialization or extension construction.

Source: [Services](https://plugins.jetbrains.com/docs/intellij/plugin-services.html).

## Disposal and retention

Give listeners, bus connections, timers, editors, processes, and caches the shortest suitable owner. Use plugin services or content/dialog disposables rather than `Project`/`Application` directly as parents, since those containers can outlive plugin unload. Implementing `Disposable` on a descriptor extension does not guarantee automatic cleanup. End a registered tree with `Disposer.dispose`, which handles children too. Investigate callbacks and external registries retaining closed views or plugin classes.

Source: [Disposer and Disposable](https://plugins.jetbrains.com/docs/intellij/disposers.html).

## Actions and indexing

Keep `AnAction.update()` fast and free of scans or I/O. Specify `getActionUpdateThread()` where supported: BGT updates can access model data but must not traverse Swing; EDT updates can inspect UI but must not query PSI/VFS/project models. Do not retain project/editor/event context in long-lived registered actions. Recompute enabled/visible state for every context, including no project. Mark an action dumb-aware only when its reachable behavior is safe without indexes; defer index-dependent work through supported smart-mode APIs.

Source: [Action System](https://plugins.jetbrains.com/docs/intellij/action-system.html).

## Documents and PSI edits

Distinguish document text, committed PSI, and disk content. Use documents for current unsaved text; synchronize PSI when required. User document changes require a command for undo and the applicable write context. Check writability, normalize newlines, and preserve unrelated content. Avoid long-lived document retention. Prefer repository editing abstractions that already enforce these contracts.

Source: [Documents](https://plugins.jetbrains.com/docs/intellij/documents.html).

## VFS synchronization

VFS is a cached snapshot and may lag external changes. Refresh the affected scope, preferably asynchronously. Do not initiate background refresh while holding a read lock; synchronous refresh adds blocking and deadlock risks. Await refresh completion before consuming externally generated files. VFS does not automatically apply project exclusions to traversals; apply the feature's scope explicitly. Keep event processing lightweight and coalesce repeated requests when appropriate.

Source: [Virtual File System](https://plugins.jetbrains.com/docs/intellij/virtual-file-system.html).

## PSI performance

PSI getters can traverse trees, allocate, or load ASTs. Avoid repeated getters and project-wide text/document loading. Prefer stubs, indexes/gists, and constrained scopes for repeated searches. Cache only with correct invalidation dependencies. Use AST-loading assertions or profiling for suspected loading regressions. Do not prescribe an index for a small bounded operation without evidence of need.

Source: [PSI Performance](https://plugins.jetbrains.com/docs/intellij/psi-performance.html).

## Persistent settings

Persist settings in appropriately scoped services using `PersistentStateComponent`, with deliberate storage and roaming behavior. Extensions should delegate persistence to services. Select mutable tracked state or immutable copy-on-write state according to the SDK; collection changes may need explicit modification tracking. Credentials require sensitive-data storage rather than plain settings XML. Preserve existing user settings and migration behavior.

Source: [Persisting State of Components](https://plugins.jetbrains.com/docs/intellij/persisting-state-of-components.html).

## Dynamic plugins

If unloading is intended, inspect extension-point dynamism, descriptor restrictions, and references outside the plugin classloader. Use smart PSI pointers where elements must survive relevant transitions. Verify unload/reload in a sandbox. Where native libraries or other justified constraints require restart, honor the declared restart policy instead of assuming every plugin must unload dynamically.

Source: [Dynamic Plugins](https://plugins.jetbrains.com/docs/intellij/dynamic-plugins.html).

## Build and compatibility

Prefer public supported APIs; assess internal, experimental, scheduled-for-removal, or obsolete APIs against supported targets. Check bundled/optional dependencies against descriptors and packaging, not only compile classpaths. Inspect archives for duplicated platform libraries and unintended artifacts.

Plugin Verifier checks binary compatibility against selected IDE builds. Verify representative builds/products across the declared range and inspect reports. This does not prove responsiveness, semantic correctness, or leak freedom.

Source: [Verifying Plugin Compatibility](https://plugins.jetbrains.com/docs/intellij/verifying-plugin-compatibility.html).

For Gradle IntelliJ Platform Plugin 2.x, use documentation matching the configured version. Discover tasks; distinguish `verifyPlugin` from older 1.x `runPluginVerifier`. Consult current requirements for planned migrations; do not freeze Java/Gradle minimums in the skill or upgrade unrelated tooling.

Source: [IntelliJ Platform Gradle Plugin](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin.html).

## Testing

Prefer platform model/fixture tests with real PSI, documents, services, and VFS for IDE behavior. Use independent unit tests for domain algorithms. Headless tests do not verify Swing; use sandbox/integration checks when UI correctness matters. Match fixture weight to need and release owned resources during teardown.

Source: [Testing Overview](https://plugins.jetbrains.com/docs/intellij/testing-plugins.html).
