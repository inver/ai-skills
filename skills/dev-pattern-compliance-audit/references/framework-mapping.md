# Patterns the framework already provides

Check this before reporting a pattern as **missing**. Using the framework's implementation is the *correct*
shape; hand-rolling it is the finding. Conversely, a framework feature can be *misused* into the opposite
pattern (e.g. `ApplicationContext.getBean` = Service Locator).

## Spring Boot / Spring Data / JPA (Java, Kotlin)

| You see                                                                 | It is                                                              | Notes                                                                               |
|-------------------------------------------------------------------------|--------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `@Component`/`@Service`/`@Bean`, constructor injection                  | Registry + Factory + Plugin replacement (DI container)             | Prefer constructor injection; field `@Autowired` hurts testability (Low)            |
| `@Scope("singleton")` (default)                                         | container-managed single instance (not the Singleton anti-pattern) | Beans must be stateless or thread-safe                                              |
| `List<X>`/`Map<String, X>` injection                                    | Strategy / Chain of Responsibility registry                        | The idiomatic replacement for `switch` on type                                      |
| `@Transactional`, `@Cacheable`, `@Async`, `@Retryable`, `@PreAuthorize` | Proxy + Decorator (AOP)                                            | Gotchas: self-invocation, `private`/`final` methods, transaction on the wrong layer |
| `@EventListener`, `ApplicationEventPublisher`                           | Observer                                                           | Check sync vs `@TransactionalEventListener` and failure handling                    |
| `JpaRepository`, `CrudRepository`, `@Repository`                        | Repository (over Data Mapper)                                      | Derived-query name sprawl → Specification/Query Object                              |
| `@Entity`, `EntityManager`, persistence context                         | Data Mapper + Unit of Work + Identity Map + Lazy Load              | Don't hand-roll these                                                               |
| `@Version`                                                              | Optimistic Offline Lock                                            | Absence on contended entities is the finding                                        |
| `@MappedSuperclass` `BaseEntity`                                        | Layer Supertype                                                    |                                                                                     |
| `@Embedded`/`@Embeddable`                                               | Embedded Value / Value Object                                      |                                                                                     |
| `@Inheritance`                                                          | Single/Class/Concrete Table Inheritance                            |                                                                                     |
| `Specification<T>`, Criteria API, QueryDSL                              | Query Object                                                       |                                                                                     |
| `DispatcherServlet`                                                     | Front Controller                                                   |                                                                                     |
| `@RestController` methods                                               | Page Controller                                                    |                                                                                     |
| `OncePerRequestFilter`, `SecurityFilterChain`, `HandlerInterceptor`     | Chain of Responsibility (+ Implicit-lock-style cross-cutting)      |                                                                                     |
| `@FeignClient`, `RestClient`, `WebClient`, `RestTemplate`               | Gateway (+ Proxy for Feign)                                        | Should sit behind one class per external system                                     |
| OpenAPI Generator models / records for API                              | Data Transfer Object                                               |                                                                                     |
| `@ConfigurationProperties` records                                      | Value Object + Plugin config                                       |                                                                                     |
| `@ConditionalOn…`, profiles, `ServiceLoader`                            | Plugin                                                             |                                                                                     |
| `MockMvc`/WireMock/fakes behind an interface                            | Service Stub                                                       |                                                                                     |
| Lombok `@Builder`, `@Value`, `record`                                   | Builder, Value Object                                              |                                                                                     |
| `@ControllerAdvice`                                                     | Chain/Interceptor for error mapping (cross-cutting)                |                                                                                     |
| `Optional`, sealed result types                                         | Special Case (Null Object)                                         | `return null` across layers is the finding                                          |
| Liquibase/Flyway                                                        | schema Metadata Mapping companion (evolutionary DB)                |                                                                                     |

## Java language features that replace GoF ceremony

| Classic pattern                           | Prefer in Java 21+                                                      |
|-------------------------------------------|-------------------------------------------------------------------------|
| Strategy, Command, simple Template Method | lambdas / method refs / functional interfaces                           |
| Visitor                                   | `sealed` interface + record patterns + exhaustive `switch`              |
| Singleton                                 | container bean, or `enum`                                               |
| State                                     | `enum` with per-constant behaviour, or sealed + records                 |
| Value Object / DTO                        | `record`                                                                |
| Builder                                   | `record` + compact constructor, or Lombok `@Builder` for many optionals |
| Iterator                                  | `Iterable`, `Stream`, generators                                        |
| Prototype                                 | copy constructors, `record` `with…` methods                             |

## Node / TypeScript (NestJS, Express, Prisma, TypeORM)

| You see                                              | It is                                                                       |
|------------------------------------------------------|-----------------------------------------------------------------------------|
| Express/Nest middleware pipeline / guards / interceptors | Chain of Responsibility                                                 |
| Nest providers/modules + DI, Awilix/tsyringe         | Registry/Plugin/Factory (container)                                         |
| Prisma client / TypeORM / Drizzle                    | Data Mapper (Prisma ≈ Query Object + Metadata Mapping via schema)           |
| `zod` / `class-validator` schemas, generated API types | DTO + validation                                                          |
| `EventEmitter`, RxJS, Nest `@EventPattern`           | Observer                                                                    |
| Discriminated unions + exhaustive `switch`           | State / Visitor / Special Case idiom                                        |
| module-level singleton export                        | Singleton (fine for stateless; finding if it holds mutable request state)   |
| Nest `@Controller` + service injection               | Page Controller + Service Layer                                             |
| Nest custom providers / `useFactory`                 | Factory / Abstract Factory                                                  |
| Prisma `$transaction`                                | Unit of Work (short-lived)                                                  |

## React / Next.js (front end)

| You see                                               | It is                                                                    |
|-------------------------------------------------------|--------------------------------------------------------------------------|
| React Router / Next.js App Router                     | Front Controller + Application Controller (client side)                  |
| Context providers                                     | Registry / dependency injection for the tree                             |
| Custom hooks / query libs (TanStack Query, SWR)       | Gateway + cache (Identity Map-like) + Observer                           |
| Reducers / XState / state machines                    | Command + State                                                          |
| Higher-order components / wrapper components          | Decorator                                                                |
| Compound components, render props                     | Strategy / Template Method                                               |
| Server Components that only fetch + compose           | thin Page Controller (good)                                              |
| Components holding fetch + business rules + JSX       | Page Controller doing everything — the anemic-controller finding for UIs |
| `useOptimistic` / server actions with revalidation    | offline-friendly update patterns (not classic PEAA, but relevant)        |

## Python (FastAPI, Django, Flask, SQLAlchemy)

| You see                                         | It is                                                                     |
|-------------------------------------------------|---------------------------------------------------------------------------|
| FastAPI `Depends`                               | DI / Registry / Factory; dependency chains ≈ Chain of Responsibility      |
| Pydantic models                                 | DTO + Value Object                                                        |
| SQLAlchemy `Session`                            | Unit of Work + Identity Map; declarative models = Data Mapper             |
| Django ORM models + `Manager`                   | Active Record (+ Table Data Gateway via Manager)                          |
| decorators, context managers                    | Decorator, Template Method (`__enter__`/`__exit__`)                       |
| module-level instance                           | Singleton                                                                 |
| `functools.singledispatch`, `dict` of callables | Strategy / Visitor idiom                                                  |
| FastAPI `APIRouter` + service functions         | Page Controller + Transaction Script / thin Service Layer                 |
| Alembic / Django migrations                     | evolutionary schema companion                                             |

## .NET (ASP.NET Core) — best-effort

| You see                          | It is                                      |
|----------------------------------|--------------------------------------------|
| Built-in DI (`IServiceCollection`) | Registry + Factory                       |
| `DbContext`                      | Unit of Work + Identity Map + Data Mapper  |
| EF Core repositories / specs     | Repository + Query Object                  |
| Middleware pipeline              | Chain of Responsibility                    |
| `IHttpClientFactory` + typed clients | Gateway + Factory                      |
| Records / `record struct`        | Value Object                               |

## Graph / workflow engines (langgraph, temporal, state machines, pipelines)

A node-per-class graph with a runner is a Mediator / Chain / State-machine hybrid implemented by the engine.
Judge the *nodes and routers* against GoF/PEAA (are routers pure functions? does a node do more than one job?
is state typed?), not the engine itself. Checkpointing is Memento.
