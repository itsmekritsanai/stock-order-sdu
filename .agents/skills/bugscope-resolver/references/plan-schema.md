# Plan schema

The plan file is the only contract between `bugscope-finder` and `bugscope-resolver`.
It lives on disk — not in conversation memory — so a human can read it, edit it, reject it,
or hand it to a different agent on a different day.

## Location and naming

```
<repo-root>/.bugscope/plan-<bug_id>.md
```

`bug_id` is a short kebab-case slug derived from the report (`login-button-noop`,
`issue-142-order-total`). One file per bug. Never overwrite a plan belonging to a
different bug — a stale plan that gets silently reused is how a fix ends up in the
wrong file.

Suggest adding `.bugscope/` to `.gitignore` unless the team wants plans reviewed in PRs.
Both choices are defensible; ask rather than deciding for them.

## Frontmatter fields

| Field | Values | Meaning |
|---|---|---|
| `schema` | `1` | Schema version, so a future change to this document does not silently reinterpret old plans. |
| `bug_id` | kebab-case slug | Identity of the bug. Matches the filename. |
| `status` | `draft` \| `needs-evidence` \| `ready` \| `in-progress` \| `resolved` \| `invalidated` | Lifecycle. See below. |
| `confidence` | `high` \| `medium` \| `low` | Confidence in the **top** hypothesis, H1. |
| `project_stack` | free text | What Phase 0 detected, plus the evidence for it. |
| `created` | `YYYY-MM-DD` | When the plan was written. |
| `source` | free text | Where the report came from (issue URL, chat, screenshot filename). |

### Status lifecycle

```
draft ─────────► ready ──► in-progress ──► resolved
needs-evidence ─┘               │
  │                             └──► invalidated ──► (back to bugscope-finder)
  └──► (user supplies what the plan asks for)
```

- `draft` — the finder could not reach a hypothesis it is willing to act on. The resolver
  must refuse to execute a `draft` plan and say why.
- `needs-evidence` — the finder could not reproduce the failure, or is missing something only
  the user can supply. Distinct from `draft` on purpose: `draft` means "I am unsure",
  `needs-evidence` means "here is the exact thing I need from you". The plan lists it.
- `ready` — the finder stands behind H1. The resolver may proceed.
- `in-progress` — the resolver claimed the plan. Prevents two agents racing on one bug.
- `resolved` — fix applied and success criteria verified.
- `invalidated` — verification falsified H1. The plan is now evidence, not instructions.
  Re-run `bugscope-finder`, which reads the Verification log and rules out what died.

## Body sections

Every section below is required. An empty section is a signal that the diagnosis is not
finished — do not paper over it with "N/A".

````markdown
---
schema: 1
bug_id: login-button-noop
status: ready
confidence: high
project_stack: Angular 17 + TypeScript (from angular.json, package.json, .claude/CLAUDE.md)
created: 2026-08-25
source: user report + screenshot login-error.png
---

## Summary

**Observed:** clicking "Sign in" with valid credentials does nothing — no network request,
no error, the form stays as-is.
**Expected:** a POST to `/api/auth/login` and navigation to `/dashboard`.
**Scope of impact:** every user, every browser. Blocks all authenticated flows.

## Evidence

- Report: "the login button doesn't do anything, no spinner, nothing in the console"
- Screenshot `login-error.png`: login form, both fields filled, button enabled and
  visually in default (not disabled, not loading) state. No error text anywhere.
- Devtools Network tab (from report): empty on click.

Record what the evidence *shows*, not what you conclude from it. Conclusions go under
Hypotheses, where they can be attacked.

## Hypotheses

Ordered, most likely first. Each one needs a falsifiable prediction — a hypothesis you
cannot imagine disproving is a guess wearing a lab coat.

### H1 — `login()` returns a cold Observable that is never subscribed (confidence: high)

**Mechanism:** `AuthService.login()` returns `this.http.post(...)`. Angular's `HttpClient`
observables are cold: no subscriber, no request. `LoginComponent.onSubmit()` calls
`this.auth.login(...)` and discards the return value, so nothing ever fires.

**Predicts:** `onSubmit()` contains a call to `auth.login` with no `.subscribe(`, no
`await firstValueFrom(`, and no `| async` binding on the result.

**Would be falsified by:** finding a `.subscribe()` on that call path, or seeing the POST
in the network log.

### H2 — Click handler not bound in the template (confidence: low)

**Mechanism:** the button sits outside `<form>` or uses `type="button"` with no `(click)`.

**Predicts:** the template has no `(ngSubmit)` or `(click)` reaching `onSubmit`.

**Would be falsified by:** finding the binding present and correctly named.

## Suspect files

- `src/app/auth/login.component.ts:34` — `onSubmit()`, the discarded call [H1]
- `src/app/auth/auth.service.ts:18` — `login()` return type [H1]
- `src/app/auth/login.component.html:12` — submit binding [H2]

Always `path:line`. A path without a line means the localization step was skipped.

## Verification steps

Ordered, cheap-first, and **read-only or reversible**. These run before any fix.
Each step says what confirms and what refutes, so the resolver can tell the difference
without re-deriving the diagnosis.

1. [H1] Read `login.component.ts:30-40`.
   - Confirms H1 if: `this.auth.login(...)` appears with no subscription on the result.
   - Refutes H1 if: the result is subscribed, awaited, or returned to an `async` pipe.
2. [H1] Read `auth.service.ts:14-22` and confirm `login()` returns `Observable<...>`
   rather than a `Promise` or a fired-off request.
   - Refutes H1 if: the service already subscribes internally (e.g. `.pipe(tap()).subscribe()`).
3. [H2] Read `login.component.html` and confirm the submit binding exists and names
   `onSubmit`.

## Allowed scope

The only paths the resolver may modify. Keep them as literal paths or globs on their own —
`scripts/check_scope.py` reads these two lists to verify the resulting diff.

- `src/app/auth/login.component.ts`
- `src/app/auth/auth.service.ts`

**Blast radius:** `AuthService.login()` has one caller (`LoginComponent`); `ApiClient.post()`
has eleven across the app, which is why the fix belongs in the component and not in the
client.

## Forbidden scope

Explicitly out of bounds, with the reason — a reason makes the boundary hold up when the
resolver finds something tempting:

- `src/app/auth/login.component.html` — H1 does not implicate the template; changing markup
  here would mask the real defect.
- Any file under `src/app/shared/` — shared code, blast radius beyond this bug.
- `package.json`, lockfiles, CI config — no dependency or pipeline changes for this bug.
- Unrelated lint/format/refactor cleanups anywhere. The diff should be readable as one idea.

## Success criteria

Observable and checkable by someone who did not write the fix:

- [ ] Clicking "Sign in" with valid credentials issues `POST /api/auth/login`.
- [ ] A failed login surfaces an error message instead of failing silently.
- [ ] `npm test -- --include='**/login.component.spec.ts'` passes.
- [ ] `npm run lint` is clean.

## Verification log

*Filled in by bugscope-resolver. Left empty by the finder.*

## Resolution log

*Filled in by bugscope-resolver. Left empty by the finder.*
````

## Notes for whoever edits a plan by hand

Editing the plan is expected and supported — it is a document, not a machine format.
The two things worth keeping intact:

- **Frontmatter keys**, because the resolver gates on `status` and reports `confidence`.
- **The confirms/refutes lines** in Verification steps, because they are what lets the
  resolver stop instead of improvise when the diagnosis turns out to be wrong.
- **The scope bullets**, because `scripts/check_scope.py` parses them. Prose bullets are fine
  and are skipped; a path or glob must be the first thing on the line, ideally in backticks.

Widening Allowed scope is the user's call, never the resolver's. Widening it *is* the
supported way to unblock a fix that turns out to need a file the plan did not anticipate.
