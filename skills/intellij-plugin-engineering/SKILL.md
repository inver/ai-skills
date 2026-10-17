---
name: intellij-plugin-engineering
description: Develop, debug, refactor, or audit IntelliJ IDEA and IntelliJ Platform plugins with senior-level attention to threading, lifecycle, PSI/VFS correctness, performance, and IDE compatibility. Use for plugin implementation or requested technical reviews; not for ordinary application code merely edited in IntelliJ.
license: Apache 2.0
compatibility: opencode
metadata:
  version: "1.0.0"
  tags:
    - kotlin
    - intelliji-plugin
  changelog: >
---

# Senior IntelliJ Plugin Developer and Auditor

Deliver changes that respect platform contracts and reviews backed by reachable execution paths and evidence. Implement
when asked to implement; audit without changing product code when asked to review. A feature request does not
automatically require a whole-plugin audit.

## Establish the platform contract

Read repository instructions and relevant feature specifications. Locate plugin modules, all descriptors, build
configuration, tests, and CI. Record the following before selecting APIs:

| Contract        | Check                                                                                                           |
|-----------------|-----------------------------------------------------------------------------------------------------------------|
| Target IDE      | Product, edition/distribution, exact version/build, required and optional plugins                               |
| Support range   | Minimum `since-build`, explicit `until-build` or open-ended policy; inspect the patched distribution descriptor |
| Compile SDK     | Resolved SDK build and matching attached sources or release tag; distinguish this from the support floor        |
| Kotlin and Java | Kotlin Gradle plugin, language/API level, JVM target/toolchain, IDE runtime and bundled libraries               |
| Build tooling   | IntelliJ Platform Gradle Plugin version and IDs, wrapper version, module-qualified tasks and CI                 |
| Runtime layout  | Classic or split plugin, registration ownership, restart/unload policy                                          |

Use [build ranges](https://plugins.jetbrains.com/docs/intellij/build-number-ranges.html)
and [Gradle requirements](https://plugins.jetbrains.com/docs/intellij/tools-intellij-platform-gradle-plugin.html) for
these checks. Discover task names rather than assuming a single-module layout. Prefer compiling against the minimum
supported SDK; compiling against a newer one requires evidence that used APIs exist throughout the declared range.

Separate platform requirements from repository conventions and optional improvements. Preserve boundaries around plain
JVM libraries. JetBrains service construction rules do not forbid constructor injection in ordinary domain classes.

Treat API signatures, threading contexts, build requirements, and compatibility as version-sensitive. Check attached
sources for the actual SDK and official documentation before choosing an API. Do not copy the newest documentation
example into an older baseline or silently raise that baseline. State uncertainty when verification is unavailable.

## Load relevant guidance

- For development or a targeted review, read applicable sections
  of [platform-contracts.md](references/platform-contracts.md).
- For Kotlin implementation, Kotlin code analysis, or JSON DTOs,
  read [kotlin-and-serialization.md](references/kotlin-and-serialization.md).
- For module/dependency changes or remote development, read [architecture.md](references/architecture.md).
- For a requested audit or release verification, read [audit-and-validation.md](references/audit-and-validation.md). Use
  its verifier workflow for compatibility-affecting development too.

Research date: **2026-10-11**. [sources.md](references/sources.md) records URLs, access dates, and the release source
baseline. Recheck official SDK pages and their version notes against the project's resolved SDK and minimum build;
current docs and `master` source are not proof of availability in an older target. Record unresolved differences instead
of inventing signatures or extension-point IDs.

## Development approach

Trace the entry point through model access, background work, UI publication, writes, and cleanup before editing. For
each asynchronous operation, identify ownership, execution context, cancellation, and stale-result handling. Prepare
expensive work away from EDT and outside write actions; revalidate before applying results.

Use existing document/PSI editing paths so edits participate in undo and respect unsaved buffers. Keep scope focused;
avoid incidental build migrations, architectural rewrites, or publishing.

For Kotlin, check the [platform constraints](references/kotlin-and-serialization.md#kotlin-platform-constraints): Kotlin
2.x is recommended for 2024.3+ and required for 2025.1+; platform-managed implementations use classes. Distinguish
syntax PSI from semantic Analysis API usage. Keep JSON DTO rules separate from platform settings persistence.

Choose [architecture](references/architecture.md) by execution needs. Multiple Gradle projects do not imply Plugin Model
V2. The experimental modular format is for remote-development splitting, not a default migration for ordinary plugins.

Choose verification for changed behavior: platform fixtures for IDE semantics, JVM tests for independent logic, and
sandbox checks for UI/lifecycle behavior. Include cancellation, indexing, project close, stale results, or undo when
affected. Use existing checks and report what actually ran.

## Pre-flight checklist

Before declaring a plugin-modifying task done, record evidence or a reason a check is inapplicable:

- **Public API boundary:** symbols exist in the target SDK and support floor; inspect internal, deprecated,
  experimental, and removal annotations. Document any justified existing exception and public alternative.
- **Registration:** descriptors, service scopes, dependency declarations, optional integrations, and packaged classes
  agree; split modules load on the intended side.
- **Threading:** callback thread, read/write access, modality, indexing constraints, cancellation, and stale-result
  handling are established.
- **Disposal:** listeners, workers, UI resources, and caches have owners; project/view close and unload behavior match
  the declared policy.
- **Compatibility:** inspect the built archive and support range; run relevant tests and the configured Plugin Verifier
  matrix for compatibility-affecting changes or release readiness. Inspect per-IDE reports and exclusions, not only the
  task exit code.

Report blocked or unperformed checks explicitly. Completion of an edit does not establish release readiness when
required verification remains unavailable.

## Review discipline

Inspect registrations and callers as well as implementations. Establish the actual thread, lifetime, reachable trigger,
and effect before reporting a defect. Search matches are leads, not findings. Rank confirmed bugs above style
preferences; explain the mechanism and smallest sound remedy. Separate findings from hypotheses and optional design
suggestions.

Report changed behavior or prioritized findings first, then verification and limits. Compilation and Plugin Verifier
success do not establish runtime correctness. Cite file locations for findings and official sources for platform
contract claims.
