# Hand-off: findings → work items

Do this only after the report exists and the user has said which findings they accept. The audit itself is
read-only; the change is *planning artifacts only*.

## 1. Choose the grouping

A change / ticket should be one reviewable, shippable unit. Don't dump every finding into one item.

- **One change per root cause or per cohesive refactor** (e.g. `introduce-order-state-machine`, `add-optimistic-locking-to-settings`).
- Merge findings only if they touch the same code and must land together.
- Keep High findings in their own changes so they can ship first.
- Confirm the grouping with the user in one short question if it is not obvious; otherwise state your grouping and proceed.

Kebab-case names, verb-first: `replace-status-switches-with-state`, `introduce-dto-layer-for-project-api`.

## 2a. OpenSpec path (when the repo uses it)

Invoke the repo's `openspec-propose` skill (or `/opsx:propose`) with a description built from the findings.
It creates `proposal.md`, `specs/**/spec.md` deltas, `design.md` (conditional) and `tasks.md`, and it runs the project
check (`openspec list --json` → `root`) — if there is no OpenSpec root, stop and ask; never `openspec init` unasked.
Read `openspec/config.yaml` `context:` — it carries the project's own architectural constraints and must shape the proposal.

Feed it, per change:

- **Why** (proposal): the finding's "Why it matters here" with `path:line` evidence and a link to the report section (`docs/pattern-compliance-<date>.md#f1-…`).
- **What changes** (proposal): the target pattern and the affected modules — stated as *behaviour-preserving refactor* unless the finding is a real bug (e.g. missing locking changes observable behaviour: a stale write now fails with 409).
- **Specs** (delta): only if externally observable behaviour changes (new error on stale write, new DTO shape). A pure internal refactor usually has **no spec delta** — say so in the proposal rather than inventing requirements, and check the schema's `instruction` for whether specs may be skipped.
- **Design**: the alternatives from the finding's "Trade-off / when to skip", the chosen approach, migration order, and risks (e.g. Spring proxy self-invocation, transaction boundary moves).
- **Tasks**: concrete, ordered, each small and independently verifiable. Include characterization tests *first* for refactors ("pin current behaviour of `X` with tests before moving logic"), then the structural change in the smallest steps, then removal of the old code. Reference real classes/paths from the audit; avoid generic "explore the codebase" tasks — the audit already did that.

## 2b. Plain tickets path (default when OpenSpec is absent)

Produce a short list the user can paste into GitHub Issues / Linear / Jira:

```markdown
### <kebab-or-readable-title>
**Severity:** High|Medium|Low  
**From audit:** docs/pattern-compliance-<date>.md#F1  
**Problem:** <one sentence + path:line>  
**Acceptance criteria:**
- [ ] …  
- [ ] Characterization tests for current behaviour of X  
- [ ] …  
**Out of scope:** <nearby Low findings deliberately left out>
```

Keep the same grouping rules. Do not invent story points or assignees.

## 3. Boundaries

- Refactoring findings must stay **behaviour-preserving** unless a task says otherwise; note that explicitly so implementation doesn't drift.
- Don't silently include Low findings just because they're nearby — list them under "Out of scope / follow-ups".
- After the artifacts / tickets are created, stop. Present the change names or ticket list and the next suggested command (e.g. `/openspec-apply-change`). Do not begin implementation.

## 4. Close the loop in the report

Append to the report under a `## Follow-up` heading: which findings were accepted → change/ticket name; which were
declined (and the reason, if the user gave one); which are deferred. This keeps the report a living record and
prevents the next audit from re-litigating decided items.
