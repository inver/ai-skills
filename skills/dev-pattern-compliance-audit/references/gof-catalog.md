# GoF catalog — audit reference

The 23 patterns from *Design Patterns: Elements of Reusable Object-Oriented Software* (1994). For each: the
**force** (when it earns its place), **evidence** to look for in code, and **misuse** signals. Use the fit test
from SKILL.md: no force → no finding. The "Modern idiom" notes matter because in Java 21+/Kotlin/TypeScript many
patterns collapse into a lambda, record, enum or sealed type.

Contents: [Creational](#creational) · [Structural](#structural) · [Behavioral](#behavioral) · [Cross-cutting anti-patterns](#cross-cutting-anti-patterns)

---

## Creational

### Factory Method
- **Intent:** let a subclass (or a method) decide which concrete class to instantiate; callers depend on the product interface.
- **Force:** creation logic varies by context/type, callers should not know concrete classes, or creation needs a name/validation.
- **Evidence:** `createX(...)`/`of(...)`/`from(...)` returning an interface; abstract `create*` hook in a base class.
- **Missing signal:** the same `if/switch` on a type/enum picking `new ConcreteX()` repeated in several places.
- **Misuse:** a factory whose only body is `return new X(args)` with no variation (over-engineered); a factory returning a concrete class so nothing is decoupled.
- **Modern idiom:** static factory methods, `Map<Type, Supplier<X>>`, or DI of `List<X>` and selecting by `supports()`.

### Abstract Factory
- **Intent:** create *families* of related objects without naming concrete classes.
- **Force:** several products must be consistent with each other (e.g. per-provider client + parser + auth), swapped as a set.
- **Evidence:** a factory interface with 2+ `createX`/`createY` methods and 2+ implementations.
- **Misuse:** one product type only (that is Factory Method); families that never vary.

### Builder
- **Intent:** construct a complex object step by step; separate construction from representation.
- **Force:** many optional parameters, invariants that must hold at `build()`, or immutable objects with 5+ fields.
- **Evidence:** `builder()`/`Builder` classes, Lombok `@Builder`, record + compact constructor validation.
- **Missing signal:** constructors with 6+ positional params of the same type; telescoping constructors; setter-heavy mutable construction of what should be immutable.
- **Misuse:** builder for a 2-field object; builder that allows building an invalid object.

### Prototype
- **Intent:** create objects by cloning a prototype instance.
- **Force:** construction is expensive or class is only known at runtime; need copies with small variations.
- **Evidence:** `clone()`, copy constructors, `withX(...)` copy-on-write, `toBuilder()`.
- **Misuse:** shallow `clone()` sharing mutable state; `Cloneable` in new Java code (prefer copy constructors/records).

### Singleton
- **Intent:** exactly one instance with a global access point.
- **Force:** rarely genuine; a truly process-wide resource (e.g. a shared executor) — and even then a container-managed single bean is better than a hand-rolled Singleton.
- **Evidence:** `private` constructor + `static getInstance()`; static mutable fields; enum with one constant.
- **Misuse (frequent finding):** hand-rolled `getInstance()` in a Spring/DI app (hidden dependency, untestable, order-of-init bugs); Singleton holding mutable per-request/per-user state (thread-safety bug — High); double-checked locking without `volatile`; static utility holder used as a service locator.
- **Not a finding:** Spring's default singleton *scope* — that is the container managing lifecycle, which is the recommended shape.

---

## Structural

### Adapter
- **Intent:** convert one interface into another clients expect.
- **Force:** integrating a third-party/legacy API whose shape differs from your domain's port.
- **Evidence:** class named `*Adapter`/`*Client` implementing your interface and delegating to a foreign API; mapping between foreign and domain types at one seam.
- **Missing signal:** foreign SDK types (and their exceptions) leaking through several layers.
- **Misuse:** adapter that just renames methods 1:1 with no isolation benefit; adapter with business logic.
- **Relationship:** PEAA *Gateway* is the same idea at the system boundary.

### Bridge
- **Intent:** decouple an abstraction from its implementation so both vary independently.
- **Force:** two orthogonal dimensions of variation (e.g. notification *kind* × delivery *channel*) that would otherwise multiply subclasses.
- **Evidence:** an abstraction holding a reference to an implementor interface; composition instead of a class-per-combination.
- **Missing signal:** class explosion like `EmailAlertSender`, `SmsAlertSender`, `EmailReportSender`, `SmsReportSender`.
- **Misuse:** speculative bridge with one implementor.

### Composite
- **Intent:** treat individual objects and trees of them uniformly.
- **Force:** recursive part-whole structures (menus, file trees, expression trees, graph nodes with sub-graphs).
- **Evidence:** node type containing `List<SameInterface>`; uniform `operation()` over leaf and container.
- **Missing signal:** `if (x instanceof Group) { for ... }` special-casing in every consumer.

### Decorator
- **Intent:** add responsibilities to an object dynamically by wrapping it with the same interface.
- **Force:** optional, stackable behaviours (caching, retry, logging, metrics, auth) around a core operation.
- **Evidence:** class implementing interface X *and* holding an X; Spring AOP / `@Transactional` / `@Cacheable`; `Retrying*`, `Caching*`, `Logging*` wrappers.
- **Missing signal:** the same cross-cutting boilerplate (try/log/retry/metrics) copy-pasted around many methods.
- **Misuse:** a "decorator" that changes the interface or hides required behaviour; deep decorator stacks where order matters but is implicit.

### Facade
- **Intent:** a simple interface over a complex subsystem.
- **Force:** clients repeatedly orchestrate the same 4–5 subsystem calls; want a narrow entry point to a module.
- **Evidence:** `*Facade`, application/service classes that hide a subsystem; PEAA *Service Layer* and *Remote Facade* are the enterprise cousins.
- **Misuse:** facade that becomes a God Class re-exporting every subsystem method; facade that clients bypass.

### Flyweight
- **Intent:** share fine-grained immutable objects to save memory.
- **Force:** very many (10⁵+) objects with mostly shared intrinsic state — measured memory pressure.
- **Evidence:** interned/cached instances, `valueOf` caches, string/enum pools.
- **Misuse:** premature; mutable "shared" objects (bug). Rarely relevant in business apps — do not report as *missing* without a measured problem.

### Proxy
- **Intent:** a surrogate controlling access to another object (remote, virtual/lazy, protection, caching).
- **Force:** lazy loading, access control, remote calls that should look local, cross-cutting via dynamic proxies.
- **Evidence:** JDK dynamic proxy / CGLIB / Spring AOP, Feign clients, JPA lazy proxies, `Supplier`-based lazy holders.
- **Misuse / gotcha:** self-invocation bypassing a Spring proxy (`this.transactionalMethod()` silently not transactional — Medium/High); lazy proxy escaping the session (`LazyInitializationException`).

---

## Behavioral

### Chain of Responsibility
- **Intent:** pass a request along handlers until one handles it.
- **Force:** an ordered, extensible pipeline of independent handlers (validation, auth, filters, middleware).
- **Evidence:** servlet/Spring Security filter chain, `Handler.setNext`, list of `Interceptor`s iterated in order.
- **Missing signal:** one method with a long sequence of `if (rule1) ... if (rule2) ...` gates that grows per requirement.
- **Misuse:** handlers that all must run (that is a pipeline/Template Method); no defined behaviour when nobody handles.

### Command
- **Intent:** encapsulate a request as an object (queue, undo, log, retry, schedule).
- **Force:** requests must be queued, logged, retried, undone, or serialized.
- **Evidence:** `*Command`/`*Task`/`Runnable`/`Callable` objects, job/message payloads with an `execute`/handler, CQRS command handlers.
- **Misuse:** a Command class per trivial method call with no queuing/undo need; lambdas suffice.

### Interpreter
- **Intent:** represent a grammar and interpret sentences in it.
- **Force:** a small, stable DSL/rule language evaluated at runtime (filters, rules, expressions).
- **Evidence:** AST node classes with `evaluate(context)`; SpEL/rule-engine wrappers.
- **Misuse:** hand-rolled parser for something a library handles; grammar too large for this pattern. Rare — usually just note where present.

### Iterator
- **Intent:** sequential access to a collection without exposing its structure.
- **Force:** custom traversal of a non-trivial structure; lazy/streaming sequences.
- **Evidence:** `Iterable`/`Iterator`/`Stream`/generators; cursor/paging abstractions.
- **Misuse:** exposing internal mutable collections (`getItems()` returning the live list) instead of an iterator/unmodifiable view. Built into every modern language — flag only misuse.

### Mediator
- **Intent:** centralise how a set of objects interact so they don't reference each other.
- **Force:** many-to-many coupling among peers (UI form widgets, workflow steps).
- **Evidence:** a coordinator/orchestrator that peers talk to; event bus; a workflow engine (this includes graph/state-machine runners).
- **Misuse:** mediator becoming a God Class that owns all logic; peers still calling each other directly as well.

### Memento
- **Intent:** capture and restore an object's state without breaking encapsulation.
- **Force:** undo, checkpoints, transactional rollback, resumable workflows.
- **Evidence:** snapshot/checkpoint objects, immutable state copies, event-sourced replay.
- **Misuse:** snapshots that expose/leak internals; mutable snapshots.

### Observer
- **Intent:** notify dependents when a subject changes (publish/subscribe).
- **Force:** one-to-many change notification with loose coupling.
- **Evidence:** `ApplicationEventPublisher`/`@EventListener`, listeners lists, reactive streams, React state subscriptions.
- **Misuse:** listeners that mutate the subject (cycles); synchronous listeners doing slow IO inside the publisher's transaction; listener leaks (never unregistered); hidden control flow via events for what should be a direct call.

### State
- **Intent:** an object alters its behaviour when its state changes; state-specific logic in state objects.
- **Force:** an entity with a real lifecycle where behaviour and allowed transitions depend on status.
- **Evidence:** state enum with behaviour, `State` interface + implementations, state-machine libs.
- **Missing signal:** `switch (status)` / `if (status == X)` repeated across many methods; transitions validated ad hoc in several places (illegal transitions possible).
- **Modern idiom:** enum with abstract methods, or sealed interface + records; a transition table.

### Strategy
- **Intent:** interchangeable algorithms behind one interface, chosen at runtime.
- **Force:** several ways to do one thing, selected by config/type/context, and the set grows.
- **Evidence:** interface + N implementations selected via DI/map/enum; comparators; lambdas passed as behaviour.
- **Missing signal:** `switch`/`instanceof`/`if-else` chains on a type or mode flag that are edited whenever a variant is added (violates Open/Closed).
- **Misuse:** interface with one implementation and no second on the horizon; strategy selected with the same chain it was meant to remove.
- **Modern idiom:** functional interface/lambda; `Map<Key, Handler>` built from DI.

### Template Method
- **Intent:** define an algorithm skeleton in a base class; subclasses fill in steps.
- **Force:** several variants share the same overall sequence with differing steps (retry loop, pre/post hooks, import pipelines).
- **Evidence:** abstract base class with a `final` skeleton method calling `abstract`/hook methods; PEAA *Layer Supertype* often hosts these.
- **Misuse:** inheritance used purely for code reuse (prefer composition/Strategy); base class with many hooks that subclasses must know call order for (fragile base class); `protected` mutable state shared with subclasses.

### Visitor
- **Intent:** add operations to a closed class hierarchy without modifying it (double dispatch).
- **Force:** stable element types, frequently added operations (compilers, AST/report/export walkers).
- **Evidence:** `accept(Visitor)` / `visit(X)` overloads.
- **Modern idiom:** sealed types + pattern-matching `switch` give exhaustiveness checks with far less ceremony — recommend that over a classic Visitor in Java 21+.
- **Misuse:** visitor over a hierarchy that keeps gaining new element types (each addition touches every visitor).

---

## Cross-cutting anti-patterns

Named failures worth reporting (each still needs `path:line` evidence and the fit test):

| Anti-pattern | Signal | Usual fix |
|---|---|---|
| God Class / Blob | >~500 lines, >~20 methods, many unrelated collaborators | Extract cohesive classes; Facade over the result if a single entry point is needed |
| Shotgun surgery | Adding a variant means editing N files | Strategy / State / polymorphism / registry |
| Primitive obsession | Strings/ints/doubles carrying domain meaning (ids, money, emails, ranges) | Value Object (PEAA), Money |
| Feature envy | Method mostly uses another object's data | Move the method to that object |
| Service Locator abuse | `ctx.getBean(...)` / static registry lookups in business code | Constructor injection |
| Speculative generality | Interfaces/abstract classes/factories with one impl and no seam need | Delete the indirection |
| Golden hammer | The same pattern applied everywhere regardless of force | Remove where force is absent |
| Deep inheritance / fragile base class | 3+ levels, overrides depending on parent call order | Composition + Strategy |
