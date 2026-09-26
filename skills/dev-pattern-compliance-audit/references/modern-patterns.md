# Modern pattern mapping (optional reference)

Use this **only** when the team's vocabulary is already DDD, Hexagonal/Ports & Adapters, or resilience-oriented.
Do **not** force these terms onto a classic Transaction-Script codebase. The fit test from SKILL.md still applies:
no force → no finding.

Map findings to the language the team already uses so recommendations land better.

---

## DDD tactical patterns ↔ GoF / PEAA

| DDD concept | Closest classic | When the force is real | Misuse signal |
|-------------|-----------------|------------------------|---------------|
| **Entity** | Domain Model object with identity | Stable identity + lifecycle/invariants | Anemic entity + all logic in services |
| **Value Object** | PEAA Value Object / Embedded Value | Immutable, equality by value (Money, Address, Email) | Mutable "value" objects; primitives for money/ids |
| **Aggregate** | Cluster of entities with a root | Consistency boundary that must be transactional | Multiple roots mutated in one transaction without clear ownership |
| **Domain Event** | Observer / Event notification | Something interesting happened that other parts react to | Events used as a hidden control-flow bus for what should be a direct call |
| **Repository** | PEAA Repository | Collection-like access to aggregates | Repository that leaks persistence types or contains business rules |
| **Factory** | GoF Factory Method / Abstract Factory | Complex creation or invariant enforcement at birth | Factory that is just `new X(args)` with no variation |
| **Specification** | Strategy + Query Object | Reusable, composable business rule / query predicate | Same rule duplicated as if/else in three places |
| **Domain Service** | Stateless operation that doesn't belong to one entity | Cross-entity rule that is still pure domain | "Domain service" that is actually an application service (I/O, transactions) |
| **Application Service** | PEAA Service Layer | Orchestrates use cases, transactions, security | Fat application service that owns business rules |

**Guidance:** Prefer the DDD name in the report title when the codebase already talks in DDD terms; still cite the classic force and evidence.

---

## Ports & Adapters / Hexagonal

| Concept | Classic counterpart | Force | Finding when missing or inverted |
|---------|---------------------|-------|----------------------------------|
| **Port** (inbound/outbound) | Separated Interface | Domain defines the contract; infrastructure implements | Domain imports concrete HTTP/DB/SDK types |
| **Adapter** | Adapter / Gateway | Translates between port and external technology | Foreign types/exceptions leak past the adapter |
| **Driving adapter** | Page Controller / Front Controller | Delivers requests into the application | Controllers contain business rules or open transactions |
| **Driven adapter** | Gateway / Repository impl | Talks to DB, queues, external APIs | Business logic inside the adapter |

A clean hexagonal layout is not mandatory. Report inversion (domain → infrastructure) as a High/Medium finding only when it causes real coupling pain.

---

## Resilience & distribution patterns

These sit on top of Gateway / Decorator / Proxy.

| Pattern | Force | Evidence / missing signal |
|---------|-------|---------------------------|
| **Circuit Breaker** | Protect the system from cascading failure of a dependency | Resilience4j / Polly / custom breaker; or repeated timeouts with no isolation |
| **Retry with backoff + jitter** | Transient faults | `@Retryable`, resilience libs; or naked retry loops / no jitter |
| **Bulkhead** | Limit concurrency so one slow dependency cannot starve others | Thread-pool / semaphore isolation; or shared unbounded executor |
| **Timeout** | Bound wait time | Explicit timeouts on HTTP/DB calls; or default infinite waits |
| **Idempotency key** | Safe retries of non-idempotent writes | `Idempotency-Key` header / clientRequestId; scanner lead `missing_idempotency` |
| **Outbox / transactional messaging** | Reliably publish events after a local write | Outbox table + poller; or "write local then fire-and-forget remote" races (see cross-check 4) |

Report these only when the force is visible (production incidents, dual-write races, missing timeouts on critical paths). Do not recommend a full resilience stack for a single-instance internal tool.

---

## CQRS / Event Sourcing (light)

| Idea | When it earns its place | Over-engineering signal |
|------|-------------------------|-------------------------|
| Separate read/write models | Very different read vs write shapes, heavy reporting, or independent scaling | Two models for a simple CRUD screen |
| Event-sourced aggregate | Need full audit trail, temporal queries, or complex rebuildable state | Event store for a settings table |

Most codebases never need these. Mention under *Deliberately not recommended* when the force is absent.

---

## How to use this file in the audit

1. Finish the PEAA + GoF pass first.
2. If the repo's docs, package names, or team language already use DDD / Hexagonal / "ports", rewrite finding titles and recommendations in that vocabulary.
3. Add at most 1–2 resilience findings when dual-write or timeout problems are concrete.
4. Never invent a DDD rewrite for an honest Transaction Script application.
