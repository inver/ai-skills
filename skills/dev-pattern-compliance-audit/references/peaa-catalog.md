# PEAA catalog — audit reference

Martin Fowler, *Patterns of Enterprise Application Architecture* (2002); catalog online at
<https://martinfowler.com/eaaCatalog/>. One-line intents below are Fowler's own. For each group: how to decide,
evidence to look for, and how it goes wrong.

PEAA choices are **architectural**: settle Domain Logic and Data Source style first (they constrain the rest), and
judge consistency — a codebase that mixes Active Record entities with a Data Mapper layer, or Domain Model
rhetoric with Transaction Script reality, has a finding even if each piece is fine alone.

Contents: [1 Domain Logic](#1-domain-logic) · [2 Data Source](#2-data-source-architectural) · [3 O/R Behavioral](#3-object-relational-behavioral) · [4 O/R Structural](#4-object-relational-structural) · [5 O/R Metadata / Repository](#5-object-relational-metadata-mapping) · [6 Web Presentation](#6-web-presentation) · [7 Distribution](#7-distribution) · [8 Offline Concurrency](#8-offline-concurrency) · [9 Session State](#9-session-state) · [10 Base Patterns](#10-base-patterns)

---

## 1. Domain Logic

Decide which of these the codebase *actually* uses by looking at where `if`s about business rules live —
not at package names.

| Pattern | Fowler's intent | Fits when |
|---|---|---|
| **Transaction Script** | Organizes business logic by procedures where each procedure handles a single request from the presentation. | Simple logic, few rules, CRUD-ish; low duplication. Perfectly legitimate. |
| **Domain Model** | An object model of the domain that incorporates both behavior and data. | Complex, changing rules; many interacting concepts; logic that would otherwise be duplicated. |
| **Table Module** | A single instance that handles the business logic for all rows in a database table or view. | Table-oriented platforms (record sets) — rare on the JVM. |
| **Service Layer** | Defines an application's boundary with a layer of services that establishes a set of available operations. | Multiple clients (UI, API, jobs, messaging) need the same operations/transactions. Unnecessary for a single-interface app with little shared logic. |

**Evidence:** entities with only fields/accessors + `*Service` classes doing all calculations/validation ⇒ Transaction Script wearing a Domain Model costume.

**Anti-pattern — Anemic Domain Model** (Fowler bliki): domain objects "little more than bags of getters and setters"
while services hold all the logic; "all of the costs of a domain model, without any of the benefits". Report it only
when **both** hold: (a) the domain is non-trivial (rules that vary, invariants, state transitions), and (b) the
logic in services is the kind that belongs with the data (validation of the object's own invariants, derived values,
state transitions). If the app is honest Transaction Script over simple CRUD, the fix is *not* "add a domain model" —
say so and record it under *Deliberately not recommended*. **Apply this per entity, not once per codebase**: even in
an honest CRUD app, look for the entity that has a lifecycle — a `status`/`state` field plus counters and
finished/drained/terminal flags, written from services or workers via setters, where several fields must change
together (e.g. "after N failures: status=FAILED, finishedAt=now, drained=true"). That is real state-machine logic
whose invariant is currently enforced by convention only, and it is the one place a rich object earns its keep. The
proportionate fix is 3–4 intention-revealing methods on that entity (`start(...)`, `applyStatus(...)`,
`recordFailure(cap)`, `markDrained()`), not a Domain Model rewrite; say so, and keep the rejection of the rewrite
scoped to the CRUD entities. Services should stay thin coordinators (transactions,
security, orchestration), not hold rules.

**Other ways it goes wrong:**
- Business logic in controllers/handlers/React components (High): rules unreachable from other clients, untestable without the web stack.
- Service Layer that just forwards to a repository (pass-through), or a fat service that is a God Class.
- Domain objects that depend on presentation or persistence frameworks (JSON annotations aside, look for web/HTTP types or `EntityManager` inside domain code).
- Transaction boundaries scattered across controllers/repositories instead of at the service operation.

## 2. Data Source (architectural)

| Pattern | Fowler's intent |
|---|---|
| **Table Data Gateway** | An object that acts as a gateway to a database table. One instance handles all the rows in the table. |
| **Row Data Gateway** | An object that acts as a gateway to a single record in a data source. There is one instance per row. |
| **Active Record** | An object that wraps a row in a database table or view, encapsulates the database access, and adds domain logic. |
| **Data Mapper** | A layer of mappers that moves data between objects and a database while keeping them independent. |

- **Fits:** Active Record for simple domains where objects ≈ tables; Data Mapper (JPA/Hibernate/MyBatis) when the domain model diverges from the schema.
- **Evidence:** JPA `@Entity` + `EntityManager`/Spring Data = Data Mapper (framework-provided). Entities with `save()`/`find()` on themselves = Active Record. `JdbcTemplate` + hand SQL per table class = Table Data Gateway.
- **Goes wrong:** mixing styles for the same concept; entities carrying JSON/HTTP/UI annotations *and* rules (three responsibilities); SQL strings scattered through services; Active Record with complex domain logic (fatten-the-table coupling).

## 3. Object-Relational Behavioral

| Pattern | Fowler's intent |
|---|---|
| **Unit of Work** | Maintains a list of objects affected by a business transaction and coordinates the writing out of changes. |
| **Identity Map** | Ensures that each object gets loaded only once by keeping every loaded object in a map. |
| **Lazy Load** | An object that doesn't contain all of the data you need but knows how to get it. |

- JPA persistence context = Unit of Work + Identity Map; lazy associations/proxies = Lazy Load. Credit them; don't recommend hand-rolling.
- **Goes wrong:** manual `save()` after every mutation inside a transaction (fighting the Unit of Work); N+1 queries from unplanned lazy loading (Medium — cite the loop); `LazyInitializationException` workarounds like open-session-in-view papering over unclear boundaries; long-lived detached entities used as DTOs; hand-rolled caches that duplicate the Identity Map inconsistently.

## 4. Object-Relational Structural

Identity Field, Foreign Key Mapping, Association Table Mapping, Dependent Mapping, Embedded Value, Serialized LOB,
Single Table / Class Table / Concrete Table Inheritance, Inheritance Mappers.

- ORMs implement these via annotations (`@Id`, `@ManyToOne`, `@JoinTable`, `@Embedded`, `@Lob`/JSON columns, `@Inheritance(strategy=…)`).
- **Look for:** inheritance strategy chosen with reason (Single Table = fast/sparse columns; Class Table = normalised/joins; Concrete = no polymorphic queries); `@Embedded` used for true value objects (Money, Address) instead of scattering columns; JSON/serialized blobs holding data that is queried or joined (Serialized LOB misuse).
- **Goes wrong:** business identity used as primary key (mutable natural keys); `equals/hashCode` on entities based on all fields or on generated id before persist; bidirectional associations with no owner side.

## 5. Object-Relational Metadata Mapping

| Pattern | Fowler's intent |
|---|---|
| **Metadata Mapping** | Holds details of object-relational mapping in metadata. |
| **Query Object** | An object that represents a database query. |
| **Repository** | Mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects. |

- **Repository fits** when the domain is complex and querying is heavy; it sits *above* Data Mapper. Spring Data `*Repository` interfaces satisfy it.
- **Query Object** = Criteria API / Specification / QueryDSL / a filter object translated to a query.
- **Goes wrong:** repository methods exposing persistence types (`Session`, `Query`, `ResultSet`, `Page` in the domain API is fine, `EntityManager` is not); repository containing business rules; controllers/services building raw SQL/JPQL strings; one repository method per report shape (`findByAAndBAndCOrderByD…`) where a Specification/Query Object would collapse them; "repository" per table rather than per aggregate root (only relevant with a real Domain Model).

## 6. Web Presentation

| Pattern | Fowler's intent |
|---|---|
| **Model View Controller** | Splits user interface interaction into three distinct roles. |
| **Page Controller** | An object that handles a request for a specific page or action on a Web site. |
| **Front Controller** | A controller that handles all requests for a Web site. |
| **Template View** | Renders information into HTML by embedding markers in an HTML page. |
| **Transform View** | A view that processes domain data element by element and transforms it into HTML. |
| **Two Step View** | Turns domain data into HTML in two steps: logical page formation then HTML rendering. |
| **Application Controller** | A centralized point for handling screen navigation and the flow of an application. |

- Spring MVC `DispatcherServlet` = Front Controller; `@Controller`/`@RestController` methods = Page Controllers; Thymeleaf/JSP = Template View; React Router = Front Controller + Application Controller on the client; React components = view + (with hooks) presenter.
- **Goes wrong:** controllers containing business rules, transaction management, or persistence (thin-controller violation); views/components computing domain values; controllers returning persistence entities (see DTO); duplicated request-parsing/validation across controllers instead of shared binding/validation; multi-step wizard flow logic smeared across screens (missing Application Controller / state machine).
- For SPAs, apply the same roles to the client: data fetching + caching in hooks/services, no business rules in JSX, routing centralised.

## 7. Distribution

| Pattern | Fowler's intent |
|---|---|
| **Remote Facade** | Provides a coarse-grained facade on fine-grained objects to improve efficiency over a network. |
| **Data Transfer Object** | An object that carries data between processes in order to reduce the number of method calls. |

- **DTO fits** at every process boundary (REST, messaging, RPC). Contract-first generated models (OpenAPI Generator) are DTOs by construction — credit them.
- **Goes wrong:** persistence entities serialised directly to clients (schema coupling, lazy-loading and over-posting/mass-assignment risk — Medium/High); DTOs carrying behaviour; DTO ⇄ domain mapping duplicated inline in many places instead of one assembler/mapper; chatty fine-grained remote calls in a loop (missing Remote Facade); a "DTO" shared between two services' internal models so they can't evolve independently.

## 8. Offline Concurrency

| Pattern | Fowler's intent |
|---|---|
| **Optimistic Offline Lock** | Prevents conflicts between concurrent business transactions by detecting a conflict and rolling back. |
| **Pessimistic Offline Lock** | Prevents conflicts between concurrent business transactions by allowing only one business transaction at a time. |
| **Coarse-Grained Lock** | Locks a set of related objects with a single lock. |
| **Implicit Lock** | Allows framework or layer supertype code to acquire offline locks. |

- **Evidence:** `@Version`, `If-Match`/ETag handling, `SELECT … FOR UPDATE`, advisory locks, per-key mutex maps.
- **Missing signal (High when data loss is possible):** read-modify-write of shared rows across requests (edit screens, counters, status transitions, settings) with no `@Version`/conditional update ⇒ lost updates. Confirm the concurrent-writer scenario before rating High.
- **Goes wrong:** optimistic lock exceptions swallowed or blindly retried; pessimistic locks held across user think-time or remote calls; in-process locks used where multiple instances run (a JVM `synchronized`/`ReentrantLock` does not protect across replicas — say whether the deployment is single-instance).

## 9. Session State

Client Session State · Server Session State · Database Session State.

- **Look for:** where per-user/conversation state lives — JWT/cookies (client), HTTP session/in-memory map (server), DB rows.
- **Goes wrong:** server session state in memory in a service that scales horizontally (sticky-session dependency); large or sensitive state in client tokens; in-memory flows lost on restart with no acknowledgement (note as a known trade-off if documented).

## 10. Base Patterns

| Pattern | Fowler's intent | What to check |
|---|---|---|
| **Gateway** | An object that encapsulates access to an external system or resource. | External HTTP/SDK calls behind one class per system; foreign types/exceptions don't leak past it. Missing = `RestTemplate`/`fetch` calls sprinkled in business code. |
| **Service Stub** | Removes dependence upon problematic services during testing. | Tests for code touching external systems use a stub/fake behind the Gateway interface. |
| **Record Set** | An in-memory representation of tabular data. | `ResultSet`/`Map<String,Object>`/`Row` passed through layers instead of typed objects (Medium). |
| **Mapper** | An object that sets up a communication between two independent objects. | One mapper per boundary; not duplicated inline mapping. |
| **Layer Supertype** | A type that acts as the supertype for all types in its layer. | `BaseEntity` (id, version, audit) is good; a base class accumulating unrelated helpers is not. |
| **Separated Interface** | Defines an interface in a separate package from its implementation. | Ports the domain owns, implemented in infrastructure; dependency points inward. Missing = domain importing infrastructure packages. Over-applied = an interface for every class. |
| **Registry** | A well-known object that other objects can use to find common objects and services. | Prefer DI. Static registries/service locators in business code are a finding. |
| **Value Object** | A small simple object whose equality isn't based on identity. | Records/immutable classes with value `equals`. Missing = primitive obsession (ids, emails, ranges, currencies as raw `String`/`double`). |
| **Money** | Represents a monetary value. | `BigDecimal` + currency (or minor units as `long`), never `float`/`double`; no rounding scattered across code. |
| **Special Case** | A subclass that provides special behavior for particular cases. | Null-object/`Optional`/result types instead of `return null` + caller null checks (Medium if nulls cross layers). |
| **Plugin** | Links classes during configuration rather than compilation. | DI configuration, `ServiceLoader`, Spring profiles/conditional beans picking implementations by config — credit them. |

---

## Quick decision aid: what PEAA architecture is this codebase?

1. Where do rules for *one* entity's invariants/derived values live? (entity → Domain Model; service → Transaction Script.)
2. How does data reach objects? (`@Entity`+repo → Data Mapper; `entity.save()` → Active Record; SQL in classes → Gateway.)
3. What does the API expose? (DTOs vs entities.)
4. What guards concurrent edits? (`@Version`/ETag vs nothing.)
5. Who owns transactions? (service operation vs controller vs nobody.)

Write the answers into the report's "Architecture profile" section; the findings then read as deviations from
the profile the team *chose*, which is far more persuasive than deviations from an abstract ideal.
