# Kotlin and serialization in plugins

Research/access date: 2026-10-11. Apply only to plugin implementation and its data boundaries; this is not a general
Kotlin/JVM guide. See [sources.md](sources.md) for version provenance.

## Kotlin platform constraints

- Kotlin 2.x is recommended for targets 2024.3+ and required for 2025.1+. Check the compiler, language/API levels, JVM
  target, and oldest supported IDE together.
- Use `class` for platform-managed services and descriptor implementations, not singleton `object`. Service singleton
  ownership belongs to the platform. A documented exception such as `FileType` does not create a general service
  exception.
- Keep extension companion objects limited to simple constants/loggers. This is not a ban on objects in independent
  domain code.
- Normally use the platform's Kotlin standard library, respecting the oldest supported runtime. Use the IDE's bundled
  coroutines; exclude competing transitive copies. Inspect dependency resolution and the packaged archive.

Source: [Configuring Kotlin Support](https://plugins.jetbrains.com/docs/intellij/using-kotlin.html).

## Analyzing Kotlin code

Writing a plugin in Kotlin does not itself require a dependency on the Kotlin IDE plugin. Accessing that plugin's
code-analysis APIs does: declare `org.jetbrains.kotlin` in the build and runtime descriptors where used. Analysis API is
available from 2024.2; K2 is the default from 2025.1. For integrations that depend on Kotlin, follow the documented K2
migration and compatibility declaration for the target
version. [IDEA/Kotlin integration](https://plugins.jetbrains.com/docs/intellij/idea.html), [K1 migration](https://kotlin.github.io/analysis-api/migrating-from-k1.html).

Use Kotlin PSI for syntax/tree operations. Use Analysis API for semantics such as inferred types, symbols, and resolved
calls; do not build new integrations on K1 compiler internals. Keep sessions and their symbols/types inside the owning
`analyze` block and read action. Export plain immutable results or supported pointers, restoring and revalidating them
in a new session. Verify exact API names against the bundled Kotlin plugin; current online examples may be
newer. [Analysis API fundamentals](https://kotlin.github.io/analysis-api/fundamentals.html).

## Jackson for plugin JSON boundaries

Use this section when an existing or required network/file JSON boundary uses Jackson. Do not add Jackson for ordinary
IDE settings: retain the [platform persistence contract](platform-contracts.md#persistent-settings). Platform Split Mode
RPC uses its own serialization contract; see [architecture.md](architecture.md).

**Require `jackson-module-kotlin` and register it on the actual mapper used for Kotlin DTOs.** Align Jackson artifacts
and confirm compatibility with the target Kotlin runtime, including reflection. Merely adding the dependency does not
configure a manually constructed mapper. Keep the project's chosen major line: Jackson 2 uses
`com.fasterxml.jackson.module`, whereas Jackson 3 uses `tools.jackson.module`; imports and configuration must
match. [Jackson 2 Kotlin module](https://github.com/FasterXML/jackson-module-kotlin/blob/2.21/README.md), [Jackson 3 Kotlin module](https://github.com/FasterXML/jackson-module-kotlin).

Prefer immutable constructor-based DTOs (`data class`, `val`, no exposed mutable collections) unless a strong project
convention requires otherwise. Treat this as an engineering default, not a platform instantiation rule. Do not add
setters or no-argument constructors to conceal a missing Kotlin module. Make required, nullable, and defaulted fields
deliberate. Test missing versus explicit `null` independently; module support does not make all null policies identical.
For Jackson 2, enable `FAIL_ON_NULL_FOR_PRIMITIVES` when explicit null must be rejected for non-null primitive
properties. [Jackson Kotlin caveats](https://github.com/FasterXML/jackson-module-kotlin/blob/2.21/README.md#caveats).

Choose annotation use-site targets for the Java element Jackson inspects: `@field:` for a backing field, `@get:` for a
getter, `@param:` for a constructor parameter. There is no universal “always use `@field:`” rule. For a renamed
immutable constructor property, matching `@param:JsonProperty("wire_name")` and `@get:JsonProperty("wire_name")`
explicitly address construction and serialization; verify both directions with the project's mapper. Do not apply a
field target to a computed property without a
field. [Kotlin annotation targets](https://kotlinlang.org/docs/annotations.html#annotation-use-site-targets), [JsonProperty contract](https://github.com/FasterXML/jackson-annotations/blob/3.x/src/main/java/com/fasterxml/jackson/annotation/JsonProperty.java).

Validate defaults, nullable values, primitive nulls, renamed fields, nested/generic DTOs, and schema migration where
relevant. Run a sandbox smoke test to detect packaged-library/classloader differences. Do not assume an IDE's private
bundled Jackson version is a supported plugin dependency; use
the [dependency and compatibility checks](platform-contracts.md#build-and-compatibility).
