# Source register

All sources below were accessed **2026-10-11**. Dates here describe research, not a promise that moving documentation
remains unchanged. Rule citations appear next to the relevant guidance; engineering recommendations (test selection, DTO
immutability, scope control) are distinguished from platform requirements.

## Version provenance

The [JetBrains stable release feed](https://data.services.jetbrains.com/products/releases?code=IIU&latest=true&type=release)
returned IntelliJ IDEA **2026.2.3**, build **262.10968.63**, released 2026-09-16. The source checks below use
`idea/262.10968.63`, not `master`. This is the research baseline, not a minimum version imposed on plugins using this
skill. The repository contains documentation rather than a plugin build, so it supplies no compile SDK or executable
compatibility matrix.

The release feed was rechecked on **2026-10-16** after session recovery and returned the same stable version/build.
Other source access dates remain 2026-10-11; they have not been relabeled as newly researched.

SDK documentation is rolling documentation. The Gradle subplugin/tasks pages reviewed describe 2.19.0-era tooling; use a
project's configured version when selecting DSL and task names. Kotlin and Jackson documentation can likewise describe
newer APIs than the target IDE bundles.

## Official documentation

Each row has access date **2026-10-11**.

| Source                                                                                                                                             | Claims checked                                                             |
|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| [Threading Model](https://plugins.jetbrains.com/docs/intellij/threading-model.html)                                                                | EDT, model locks, modality, coroutine preference, restartable reads        |
| [Background Processes](https://plugins.jetbrains.com/docs/intellij/background-processes.html)                                                      | Cancellation propagation and checkpoints                                   |
| [Coroutine Scopes](https://plugins.jetbrains.com/docs/intellij/coroutine-scopes.html)                                                              | Service ownership; deprecated container scope accessors                    |
| [Services](https://plugins.jetbrains.com/docs/intellij/plugin-services.html)                                                                       | Constructor restrictions, final light services, registration, roaming      |
| [Disposer and Disposable](https://plugins.jetbrains.com/docs/intellij/disposers.html)                                                              | Service/extension cleanup, parent lifetime, listener ownership             |
| [Action System](https://plugins.jetbrains.com/docs/intellij/action-system.html)                                                                    | Update threading, UI/model separation, action retention                    |
| [Documents](https://plugins.jetbrains.com/docs/intellij/documents.html)                                                                            | Unsaved text, commands, writability, document lifetime                     |
| [Virtual File System](https://plugins.jetbrains.com/docs/intellij/virtual-file-system.html)                                                        | Snapshot, refresh locking/completion, excluded files                       |
| [PSI Performance](https://plugins.jetbrains.com/docs/intellij/psi-performance.html)                                                                | Getter costs, AST loading, caches and invalidation                         |
| [Persisting State](https://plugins.jetbrains.com/docs/intellij/persisting-state-of-components.html)                                                | Service persistence, tracked/copy-on-write state, XML                      |
| [Dynamic Plugins](https://plugins.jetbrains.com/docs/intellij/dynamic-plugins.html)                                                                | Restart policy, extension dynamism, service overrides, retention           |
| [Testing Overview](https://plugins.jetbrains.com/docs/intellij/testing-plugins.html)                                                               | Real platform fixtures, model tests versus UI tests                        |
| [Configuring Kotlin Support](https://plugins.jetbrains.com/docs/intellij/using-kotlin.html)                                                        | Kotlin 2.x floors, class/object, companions, bundled libraries             |
| [IDEA / Kotlin Plugin](https://plugins.jetbrains.com/docs/intellij/idea.html)                                                                      | Kotlin plugin dependency, Analysis API availability and K2                 |
| [Analysis API Fundamentals](https://kotlin.github.io/analysis-api/fundamentals.html)                                                               | Syntax/semantics separation, read access, session lifetime, pointers       |
| [Migrating from K1](https://kotlin.github.io/analysis-api/migrating-from-k1.html)                                                                  | Compiler internals versus Analysis API and compatibility declaration       |
| [Modular Plugins (Experimental)](https://plugins.jetbrains.com/docs/intellij/modular-plugins.html)                                                 | V2 applicability, Gradle 2.x, module descriptors/classloaders              |
| [Split Mode and Remote Development](https://plugins.jetbrains.com/docs/intellij/split-mode-and-remote-development.html)                            | Process placement, monolithic behavior, RPC serialization, tests           |
| [Plugin Dependencies](https://plugins.jetbrains.com/docs/intellij/plugin-dependencies.html)                                                        | Build/runtime declarations, optional descriptors, bundled plugins          |
| [Build Number Ranges](https://plugins.jetbrains.com/docs/intellij/build-number-ranges.html)                                                        | Support bounds and version/bytecode compatibility                          |
| [Verifying Plugin Compatibility](https://plugins.jetbrains.com/docs/intellij/verifying-plugin-compatibility.html)                                  | Binary verifier scope and inspections                                      |
| [Internal API Migration](https://plugins.jetbrains.com/docs/intellij/api-internal.html)                                                            | Internal markers and public replacement policy                             |
| [Incompatible API Changes](https://plugins.jetbrains.com/docs/intellij/api-changes-list.html)                                                      | Version-specific migration lookup                                          |
| [2026 API Changes](https://plugins.jetbrains.com/docs/intellij/api-changes-list-2026.html)                                                         | Current baseline changes; internal/experimental changes may be omitted     |
| [Gradle Plugin 2.x](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin.html)                                        | Tooling requirements and version-sensitive setup                           |
| [Gradle Subplugins](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-plugins.html)                                | Independent module builds and version-sensitive packaging                  |
| [Gradle Tasks](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-tasks.html)                                       | Build, structure/configuration checks, verifier reports and failure policy |
| [Gradle Platform Extension](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-extension.html)                      | Explicit verifier IDE matrix and configuration                             |
| [Gradle 1.x Migration](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-migration.html)                           | `runPluginVerifier` to `verifyPlugin` naming                               |
| [Jackson Kotlin module, 2.21 branch](https://github.com/FasterXML/jackson-module-kotlin/blob/2.21/README.md)                                       | Constructor DTOs, module registration, runtime compatibility, null caveats |
| [Jackson Kotlin module, 3.x](https://github.com/FasterXML/jackson-module-kotlin)                                                                   | Jackson 3 coordinates/imports and module registration                      |
| [Kotlin Annotations](https://kotlinlang.org/docs/annotations.html)                                                                                 | Field/getter/constructor use-site targets                                  |
| [Jackson JsonProperty](https://github.com/FasterXML/jackson-annotations/blob/3.x/src/main/java/com/fasterxml/jackson/annotation/JsonProperty.java) | Property naming and supported annotation elements                          |

## IntelliJ Community source inspection

All links are pinned to **idea/262.10968.63**, accessed **2026-10-11**. Implementation classes are evidence about
platform behavior, not recommended dependencies for plugin code. Check member-level annotations; a supported class can
contain internal or deprecated methods.

| Release source                                                                                                                                                                                                          | Evidence inspected                                                                                        |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| [Application.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/core-api/src/com/intellij/openapi/application/Application.java)                                                      | Read/write context, modality-aware scheduling; obsolete helpers are not recommended                       |
| [AnAction.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/editor-ui-api/src/com/intellij/openapi/actionSystem/AnAction.java)                                                      | `update`, `getActionUpdateThread`; inspect overrides rather than assume a universal default               |
| [Service.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/core-api/src/com/intellij/openapi/components/Service.java)                                                               | Final light-service class, application/project levels                                                     |
| [ComponentManagerImpl.kt](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/service-container/src/com/intellij/serviceContainer/ComponentManagerImpl.kt)                                  | Service disposal on unload; per-instance child/intersection scope ownership; internal implementation only |
| [Disposable.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/util/src/com/intellij/openapi/Disposable.java)                                                                        | Cleanup interface                                                                                         |
| [Disposer.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/util/src/com/intellij/openapi/util/Disposer.java)                                                                       | Child registration/disposal; registration against a disposed owner                                        |
| [ProcessCanceledException.kt](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/util/base/multiplatform/src/com/intellij/openapi/progress/ProcessCanceledException.kt)                    | Cancellation control flow; rethrow instead of logging/swallowing                                          |
| [VirtualFile.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/core-api/src/com/intellij/openapi/vfs/VirtualFile.java)                                                              | Validity, refresh completion, synchronous refresh read-lock warning                                       |
| [PsiElement.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/core-api/src/com/intellij/psi/PsiElement.java)                                                                        | PSI access/validity surface; performance guidance comes from SDK documentation                            |
| [PsiDocumentManager.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/core-api/src/com/intellij/psi/PsiDocumentManager.java)                                                        | Document commit distinction and delayed publication contracts                                             |
| [WriteCommandAction.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/core-api/src/com/intellij/openapi/command/WriteCommandAction.java)                                            | Command/write integration; no new blanket API recipe prescribed                                           |
| [SmartPsiElementPointer.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/core-api/src/com/intellij/psi/SmartPsiElementPointer.java)                                                | Reparse survival and nullable resolution                                                                  |
| [PersistentStateComponent.java](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/projectModel-api/src/com/intellij/openapi/components/PersistentStateComponent.java)                     | Persistence/initialization lifecycle, non-sensitive state                                                 |
| [SimplePersistentStateComponent.kt](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/projectModel-api/src/com/intellij/openapi/components/SimplePersistentStateComponent.kt)             | Tracked BaseState persistence                                                                             |
| [BaseState.kt](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/projectModel-api/src/com/intellij/openapi/components/BaseState.kt)                                                       | Modification tracking and collection caveats                                                              |
| [SerializablePersistentStateComponent.kt](https://github.com/JetBrains/intellij-community/blob/idea/262.10968.63/platform/projectModel-api/src/com/intellij/openapi/components/SerializablePersistentStateComponent.kt) | Public/protected update path, retry purity, internal `setState`                                           |

## Structural comparisons, not platform authority

- [Prihod/jetbrains-plugin-development-skill](https://github.com/Prihod/jetbrains-plugin-development-skill),
  especially [its entrypoint](https://github.com/Prihod/jetbrains-plugin-development-skill/blob/main/SKILL.md): useful
  target-detection and source-versus-SDK checks plus topic routing. Accessed 2026-10-11. No frozen toolchain table or
  blanket implementation rules imported.
- [Kotlin/kotlin-agent-skills](https://github.com/Kotlin/kotlin-agent-skills),
  especially [Java-to-Kotlin skill](https://github.com/Kotlin/kotlin-agent-skills/blob/main/skills/kotlin-tooling-java-to-kotlin/SKILL.md):
  useful conditional reference loading and annotation/behavior verification. Accessed 2026-10-11. General application
  framework conventions are not IntelliJ service contracts.

Neither comparison repository substitutes for official platform or library contracts. Guidance was synthesized for this
skill rather than copied wholesale.
