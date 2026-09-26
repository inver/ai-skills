# Cross-checks: where a pattern is half-applied

Most of the costly defects an audit finds are not "pattern X is missing" but "pattern X is applied here and
skipped there", or "the code says one thing and the schema / config / docs say another". They are invisible if
you judge each class alone, so after the pattern pass, run these checks. Each one comes from a PEAA or GoF
pattern whose value depends on being applied *everywhere*. Confirm each hit by reading the code, then report it
as an ordinary finding (severity by consequence).

Contents:
1. Gateway applied consistently
2. Invariant vs. database constraint
3. Soft delete vs. cascade and background jobs
4. Remote side effect vs. local write order
5. Locking that never reaches the client
6. One rule, several homes
7. Comment / test / docs vs. code
8. Frontend data-fetch consistency
9. Client-side business rules leakage
10. OpenAPI contract fidelity (1.2)

---

## 1. Gateway applied consistently

*Pattern: Gateway (PEAA), Decorator/Proxy (GoF).* A gateway that maps errors, timeouts or auth in one wrapper is
only as good as its weakest call site.

- **Check:** list every call site of each external client (Feign/`RestClient`/SDK/`fetch`/axios/httpx). For each, is it going through
  the shared wrapper / error decoder / retry policy, or calling the client raw?
  `grep -rn "<clientField>\." src` vs `grep -rn "<WrapperClass>\." src`, then diff the two lists.
- **Finding when:** some paths wrap and others don't. Typical consequence: an outage yields a 503 on one endpoint and a
  generic 500 on another; or a timeout policy applies to reads but not to the write that matters.
- **Fix shape:** apply the mapping once at the gateway (a decorating client, or an error decoder) instead of per call site.

## 2. Invariant vs. database constraint

*Pattern: Unit of Work / Optimistic Offline Lock (PEAA).* "At most one X", "unique per Y" enforced only by a
check-then-write in code is a race under concurrency.

- **Check:** for each invariant stated in code or comments ("only one default", "one active per type", "name is
  unique"), find the matching unique index / constraint in the migrations (`db/changelog`, `migrations/`, `*.sql`, Prisma schema).
  Look at bulk-update methods (`@Modifying`, `UPDATE ... SET`, Prisma `updateMany`) that maintain the invariant: they bypass `@Version`.
- **Finding when:** the invariant has no constraint, especially when a sibling invariant does have one (inconsistency
  is the tell). Severity depends on whether two writers can actually overlap; say what you assumed about deployment.
- **Fix shape:** partial unique index, or an upsert keyed on the natural key. Removing an unused flag also counts.

## 3. Soft delete vs. cascade and background jobs

*Pattern: Dependent Mapping / aggregate boundary (PEAA).* A soft delete is an UPDATE, so database
`ON DELETE CASCADE` never fires, and children stay live.

- **Check:** does the entity/base class use `@SoftDelete`/`deleted` flags / Prisma `deletedAt`? If yes, look at the schema's FK cascades and
  at what the delete method touches. Then check scheduled jobs / pollers / queues: do they filter by a *live parent*,
  or keep processing children of deleted parents?
- **Finding when:** children remain reachable or keep being processed after their parent is deleted, or comments
  claim they are "purged".
- **Fix shape:** soft-delete children in the same operation, filter by live parent, or document runs-as-history and fix the comments.

## 4. Remote side effect vs. local write order

*Pattern: Unit of Work, Gateway.* If a method calls a remote system and then writes locally, any local failure
leaves an orphan on the remote side; the reverse order leaves a dangling local row.

- **Check:** in each service method that both calls a gateway and saves an entity, which comes first? What happens
  if the second step fails, or the caller retries?
- **Finding when:** the ordering can leave orphans and there is no idempotency key, recovery path or compensating step.
  Note when the code already handles a specific race (e.g. duplicate-key recovery) — credit that.
- **Fix shape:** persist a PENDING row first, an outbox, or an idempotent create keyed by a client-generated id.

## 5. Locking that never reaches the client

*Pattern: Optimistic Offline Lock (PEAA).* `@Version` / concurrency token only protects overlapping transactions. If the version is not
in the API response and not accepted on update, two operators editing over minutes still get last-write-wins.

- **Check:** is the version field (or an ETag/`If-Match`) present in response DTOs and update requests? Do update
  endpoints replace whole collections (delete-all + re-insert) so versions never accumulate?
- **Finding when:** `@Version` exists but is not surfaced *and* the app has more than one possible concurrent editor.
  Single-operator deployments: rate Low and ask for the policy to be written down.

## 6. One rule, several homes

*Pattern: Strategy / Specification / Service Layer.* The same business rule, or the same error message, typed in
two places will drift.

- **Check:** grep for distinctive rule phrases and error strings across the repo; look for validation duplicated
  between controller, service, and generated `@NotNull`/bean-validation / zod / Pydantic annotations.
- **Finding when:** the same rule (or message) appears twice, especially when one copy hard-codes a list (types,
  states) that a Strategy/enum already owns.
- **Fix shape:** move the rule to the object that owns the variation (a method on the strategy/entity) and call it from both places.

## 7. Comment / test / docs vs. code

Not a pattern, but it is where audits find real bugs cheaply, because a value written down in two places is often wrong in one.

- **Check:** for constants that matter (base URLs, timeouts, limits, defaults, feature flags), compare the code with
  the nearest comment, the test that asserts it, and the project docs (`AGENTS.md`, `docs/`). Also look for URL
  concatenation where the base already ends with the path segment being appended (`/v1beta` + `/v1beta/models`).
- **Finding when:** they disagree. Say which one you believe is right and why; if unsure, report both locations.

## 8. Frontend data-fetch consistency (new)

*Pattern: Gateway + Identity Map / cache (client-side).* Multiple components fetching the same resource with different
keys, stale-time, or error handling produce inconsistent UI and wasted requests.

- **Check:** list distinct `useQuery` / `useSWR` / `fetch` call sites for the same REST path or resource. Compare cache keys,
  `staleTime`, retry policy, and whether a shared custom hook or query-key factory exists.
- **Finding when:** the same resource is fetched under two different keys or with divergent policies, or every page
  re-implements the same loading/error UI instead of a shared boundary.
- **Fix shape:** one custom hook (or query-key factory) per resource; shared error/loading boundaries.

## 9. Client-side business rules leakage (new)

*Pattern: Domain logic belongs on the server (or in a shared package), not in JSX / view models that only one client uses.*

- **Check:** search components, hooks, and client stores for calculations that enforce business invariants
  (discount eligibility, status transition rules, price derivations, permission matrices that duplicate the backend).
- **Finding when:** the same rule also exists on the server (drift risk) *or* exists only on the client (security /
  consistency risk for any other client).
- **Fix shape:** move the rule to the shared domain / service layer; keep the client as a thin renderer of already-decided state.
  Pure presentation helpers (formatting, sorting for display) are fine and should not be reported.

## 10. OpenAPI contract fidelity (1.2+) and frontend generation axiom (1.3)

*Pattern: Remote Facade + DTO (PEAA); Gateway for generated clients.* The published OpenAPI document and the
runtime handlers / consumers must describe the same boundary. On TS/JS frontends, the default Gateway is
**generated from the spec** (see `openapi-contract.md` §3b).

- **Check:**
  1. Locate the published or committed spec (`openapi.yaml`, exported `/openapi.json`, etc.) and any codegen config
     (`orval.config.*`, `openapi-ts.config.*`, `openapitools.json`, package scripts `generate:api`).
  2. Sample 5–10 operations: path + method exist in both spec and controllers (and vice versa for public routes).
  3. For one write and one read: required fields, enums, and nullability match the bound types / response mappers.
  4. Documented error status codes vs `@ControllerAdvice` / Nest filters / FastAPI exception handlers.
  5. If generated clients exist, confirm call sites use them rather than parallel hand-rolled `fetch`/SDK wrappers.
  6. Ensure persistence entities are not the OpenAPI schema unless explicitly accepted.
  7. **Frontend:** If OpenAPI + TS/JS SPA/BFF exist, is there a generated client? Are feature modules still
     calling hand-rolled axios/fetch to the same base URL?
- **Finding when:** path or schema drift; dual source of truth; generated client ignored; entities as API models;
  OpenAPI + frontend without generation; dual generated + hand-rolled clients for the same paths.
- **Fix shape:** single publish pipeline; add orval/openapi-typescript + CI generate; openapi-diff/spectral;
  route SPA traffic through the generated Gateway. See `references/openapi-contract.md`.
