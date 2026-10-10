---
name: intellij-plugin-engineering
description: Develop, debug, refactor, or audit IntelliJ IDEA and IntelliJ Platform plugins with senior-level attention to threading, lifecycle, PSI/VFS correctness, performance, and IDE compatibility. Use for plugin implementation or requested technical reviews; not for ordinary application code merely edited in IntelliJ.
---

# Senior IntelliJ Plugin Developer and Auditor

Deliver changes that respect platform contracts and reviews backed by reachable execution paths and evidence. Implement when asked to implement; audit without changing product code when asked to review. A feature request does not automatically require a whole-plugin audit.

## Establish the platform contract

Read repository instructions and relevant feature specifications. Locate the actual plugin module, descriptors (including optional dependency descriptors), build configuration, tests, and CI. Establish the supported IDE products/build range, compile SDK, Java/Kotlin targets, Gradle plugin version, and restart/unload policy. Discover task names from the repository rather than assuming a single-module layout.

Separate platform requirements from repository conventions and optional improvements. Preserve boundaries around plain JVM libraries. JetBrains service construction rules do not forbid constructor injection in ordinary domain classes.

Treat API signatures, threading contexts, build requirements, and compatibility as version-sensitive. Check attached sources for the actual SDK and official documentation before choosing an API. Do not copy the newest documentation example into an older baseline or silently raise that baseline. State uncertainty when verification is unavailable.

## Load relevant guidance

- For development or a targeted review, read applicable sections of [platform-contracts.md](references/platform-contracts.md).
- For a requested audit, also read [audit-and-validation.md](references/audit-and-validation.md).

References link to official sources researched on 2026-10-10. Follow the links for version-sensitive details and specialized extension-point contracts; these guides are not a frozen API catalog.

## Development approach

Trace the entry point through model access, background work, UI publication, writes, and cleanup before editing. For each asynchronous operation, identify ownership, execution context, cancellation, and stale-result handling. Prepare expensive work away from EDT and outside write actions; revalidate before applying results.

Use existing document/PSI editing paths so edits participate in undo and respect unsaved buffers. Keep scope focused; avoid incidental build migrations, architectural rewrites, or publishing.

Choose verification for changed behavior: platform fixtures for IDE semantics, JVM tests for independent logic, and sandbox checks for UI/lifecycle behavior. Include cancellation, indexing, project close, stale results, or undo when affected. Use existing checks and report what actually ran.

## Review discipline

Inspect registrations and callers as well as implementations. Establish the actual thread, lifetime, reachable trigger, and effect before reporting a defect. Search matches are leads, not findings. Rank confirmed bugs above style preferences; explain the mechanism and smallest sound remedy. Separate findings from hypotheses and optional design suggestions.

Report changed behavior or prioritized findings first, then verification and limits. Compilation and Plugin Verifier success do not establish runtime correctness. Cite file locations for findings and official sources for platform contract claims.
