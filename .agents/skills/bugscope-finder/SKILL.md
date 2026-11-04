---
name: bugscope-finder
description: >-
  Diagnose a bug report and write a scoped, falsifiable execution plan to .bugscope/ before any code changes. Use this whenever the user reports something broken - a button or control that does nothing, a wrong or stale value, a stack trace or error log, a failing endpoint, a screenshot of a visual glitch, a bug issue or ticket - or asks to investigate, triage, root-cause, reproduce, or scope a defect. Use it even when the fix looks obvious, and even when the user asks you to just fix it, because the written plan is what keeps the fix from sprawling and what bugscope-resolver later executes. Not for adding features, refactoring, or reviewing code.
license: MIT
---

# BugScope Finder

Turn a bug report into a written, scoped, falsifiable plan — and stop there.

## Why this exists

The failure mode this guards against is not "the agent can't find the bug". It is the agent
that finds *a* bug, fixes it in the same breath, touches nine files on the way, and leaves
you unable to tell which change was the fix. Diagnosis and execution interleave, and the
reasoning evaporates.

So this skill only diagnoses. It writes down what it believes, why, what would prove it
wrong, and which files a fix may touch. `bugscope-resolver` executes that document. The plan
is a file on disk so a human can read it and argue with it before any source changes.

**Hard boundary: do not modify source code.** The only files written are under `.bugscope/`.
Adding a log line "just to check" is a source change — put it in Verification steps. Even a
one-character fix gets a plan; that minute is what makes the change reviewable.

## Phase 0 — Detect the project

Read `references/project-detection.md` and follow it. It carries the file-to-stack tables and
the monorepo and no-config fallbacks.

Do this even when the stack looks obvious. What matters most is not the language, it is the
project's **own test and build commands**, which the Success criteria must reuse verbatim to
be worth anything.

## Phase 1 — Read the evidence, then reproduce it

State what the evidence *shows* before saying what it means. This isn't ceremony: it is what
stops a vivid phrase in a report ("it's caching wrong") from short-circuiting the whole
investigation into confirming that phrase.

**Screenshots: describe first, diagnose second.** Write out what is on screen — control
states, error text, what is missing that should be there — then reason. A screenshot usually
carries evidence the reporter never mentioned.

**Stack traces:** the top frame is where it surfaced, not necessarily where it broke.

**Then reproduce, before believing anything.** Find the cheapest way to observe the failure
yourself — a command, a request, a two-line script, a browser probe — and record it in the
plan's Reproduction section. Until something fails in front of you, you are diagnosing a
report rather than a defect, and reports are wrong often enough to matter. If nothing can be
reproduced, that *is* the finding: write the plan with `status: needs-evidence` and list the
specific commands or data you need from the user. That beats a confident plan built on a
symptom nobody has seen twice.

**If it used to work,** check the history of the suspect area (`git log`, `git blame` on the
suspect lines, `git bisect` when a good commit is known). A matching commit is frequently the
entire diagnosis.

## Phase 2 — Localize

Use the Phase 0 conventions to decide where to look, then read real code. Trace the path the
data or event actually takes. If you cannot explain how the code produces the *specific*
symptom reported, you have found something interesting, not the cause.

## Phase 3 — Form falsifiable hypotheses

One to three, best first. Each needs a **mechanism** (the causal chain, specific enough for
someone else to check), a **prediction** (what must be true if it holds), and a **falsifier**
(what would disprove it).

The falsifier is load-bearing: it is what lets the resolver notice it is wrong and stop,
rather than quietly inventing a different fix while you assume the plan is being followed.

Calibrate confidence honestly — the resolver's behaviour depends on this number being real:

| | |
|---|---|
| `high` | You have read code that plainly produces this exact symptom, and can point at the line. |
| `medium` | The mechanism fits all the evidence but rests on an unchecked assumption. |
| `low` | You have a direction, not a cause. |

If the best hypothesis is `low`, set `status: draft` and keep the verification steps purely
diagnostic. Look actively for why your leading hypothesis might be wrong; a surviving
competitor belongs in the plan as H2.

## Phase 4 — Write the plan

Read `references/plan-schema.md` for the schema and a worked example, then write
`<repo-root>/.bugscope/plan-<bug_id>.md`. Three sections decide whether it is worth anything:

**Scope.** Allowed scope is the minimum set of paths that could hold the fix for H1 — not
everything you might plausibly need. Forbidden scope names the tempting things and says *why*:
the generated file someone will want to hand-edit, the shared utility with a wide blast
radius, the unrelated mess next door. A reason makes the boundary hold; a bare list gets
rationalized around. Note the blast radius of what you are proposing to change — who else
calls it — because that is usually what turns a small fix into an incident.

**Success criteria.** Observable, and checkable by someone who did not write the fix. "Login
works" is not one; "clicking Sign in issues `POST /api/auth/login` and a failure shows an
error" is. Use the project's real test command. **If no test covers this bug, require one.**
That is the normal case, not the exception — a suite that is green while the bug is live
cannot tell anyone the fix worked.

## Finish

Do not fix the bug. Report briefly: the one-line hypothesis and its confidence, the plan
path, what the resolver may touch, and any open question that would change the diagnosis.
Then hand off. If the user asks you to just fix it, write the plan first and let the resolver
execute it, so diagnosis and diff stay separable.

---

## Platform notes — Claude Code

Install by copying this skill's folder into `.claude/skills/` (this project) or
`~/.claude/skills/` (every project), or install the `bugscope` plugin from the marketplace
manifest at the repository root.

Files under `references/` are loaded on demand: read them with the Read tool at the point
this document points you at them, not upfront. That is what keeps the always-resident cost
of the skill small.

Ask for it by name when you want it explicitly — "use bugscope-finder on this crash".
