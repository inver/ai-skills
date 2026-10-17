# Plugin architecture and remote development

Research/access date: 2026-10-11. Recheck experimental contracts against the selected IDE and Gradle plugin. The table
is a selection guide, not a migration mandate.

| Need                                   | Architecture decision                                                   |
|----------------------------------------|-------------------------------------------------------------------------|
| Ordinary local plugin                  | Keep a classic plugin; one Gradle project is sufficient                 |
| Separate domain code or integrations   | Multiple Gradle projects may still produce one classic plugin           |
| Remote-native frontend/backend feature | Use the experimental modular format and place code by process ownership |

## Gradle projects versus runtime modules

Separate build organization from runtime loading. Give subprojects their own `build.gradle.kts`, register them in
`settings.gradle.kts`, and keep SDK/toolchain/dependency decisions consistent. The 2.x tooling provides
`org.jetbrains.intellij.platform` for the distributing project and `org.jetbrains.intellij.platform.module` for platform
subprojects. Plain JVM libraries need not become platform modules. Packaging helpers have changed within 2.x: follow
documentation for the configured version, inspect the archive, and do not paste the latest DSL into an older
build. [Gradle subplugins](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin-plugins.html).

Bundled plugin presence depends on product/build. Declare compile dependencies and runtime dependencies separately. In a
classic plugin, use an optional dependency with its `config-file` descriptor to isolate optional registrations; keep
references to optional classes out of always-loaded entry points. Test with the dependency present, absent, and
disabled. A compile-only dependency does not make runtime loading
optional. [Plugin Dependencies](https://plugins.jetbrains.com/docs/intellij/plugin-dependencies.html).

## Plugin Model V2 is experimental

JetBrains requires Plugin Model V2 for the documented modular remote-development architecture and advises against
adopting it for other cases. It requires IntelliJ Platform Gradle Plugin 2.x. Do not equate this with “all plugins that
happen to run remotely must be rewritten”: several existing features already work through backend
execution. [Modular Plugins](https://plugins.jetbrains.com/docs/intellij/modular-plugins.html), [non-split features](https://plugins.jetbrains.com/docs/intellij/split-mode-and-remote-development.html#problems-with-non-split-plugins).

V2 declares content modules with separate classloaders and descriptors. Module XML belongs at its resource root, not
`META-INF`; class registrations move into module descriptors. Dependencies use `<dependencies>`, not classic
`<depends>`. Optional modules can be skipped when dependencies are unavailable; required modules make the whole plugin
unavailable. Confirm loading flags and descriptor schema on the target SDK, not by analogy with optional classic
descriptors. [Modular descriptor rules](https://plugins.jetbrains.com/docs/intellij/modular-plugins.html).

## Split-mode placement

- **Frontend:** UI and latency-sensitive editor interaction.
- **Backend:** PSI, VFS, indexes, project model, and project-local execution.
- **Shared:** transport DTOs and RPC interfaces, without backend-only or UI-only dependencies.

Module dependencies determine placement; in monolithic mode both sides run in one process. Preserve the communication
boundary in both modes. Platform RPC uses `kotlinx.serialization`, not Jackson. Do not pass PSI elements, projects, or
analysis sessions as transport DTOs; send serializable data/identifiers and resolve them on the owning
side. [Split Mode architecture](https://plugins.jetbrains.com/docs/intellij/split-mode-and-remote-development.html#split-mode-architecture).

Validate registration and packaging in monolithic and split sandboxes. Exercise delayed responses, cancellation,
disconnect/reconnect, and owner disposal where affected. Put whole-plugin tests where the root descriptor and all
content modules are on the test classpath; isolated module tests cannot establish complete registration correctness.
Follow the installed tooling's split launch/test
setup. [Split Mode testing](https://plugins.jetbrains.com/docs/intellij/split-mode-and-remote-development.html#running-tests-in-split-mode).
