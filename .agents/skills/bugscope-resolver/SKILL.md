---
name: bugscope-resolver
description: >-
  Execute an existing BugScope plan: run its verification steps, apply the fix strictly inside the plan's declared scope, and stop if the hypothesis is disproved. Use this whenever the user says to apply, execute, run, or carry out a bug plan, mentions .bugscope or a plan-<id>.md file, or says to go ahead and fix the bug that was just diagnosed. Prefer it over fixing a bug freehand whenever a plan file exists, because it is what keeps the diff inside what the user already approved. Do not use it to diagnose a bug that has no plan yet - run bugscope-finder for that.
license: MIT
---

# BugScope Resolver

Execute a `bugscope-finder` plan faithfully — verify first, fix inside the declared scope,
and stop when the diagnosis turns out to be wrong.

## Why this exists

This is deliberately not a second diagnostician. Its value is being predictable: the plan
says what will change, a human approved it, and the diff matches. An executor that "improves
things while it's in there" destroys exactly that guarantee.

So the discipline is narrower than usual. Verify before changing. Stay inside the scope. When
evidence contradicts the plan, stop and say so instead of improvising. **Stopping early with
a falsified hypothesis and clean evidence is a successful run**, not a failed one — it is the
outcome that saves the most time.

## Step 1 — Load the plan and gate on its status

Look in `.bugscope/` for `plan-*.md`. Several → list them with `bug_id`, `status` and a
one-line summary and ask which; the newest is not reliably the one they mean. None → tell the
user to run `bugscope-finder` first, and do not diagnose it yourself.

| `status` | Action |
|---|---|
| `ready` | Proceed. |
| `draft` | Stop. The finder would not stand behind this. Show the open questions and ask them to re-run the finder, or to confirm explicitly. |
| `needs-evidence` | Stop. The plan lists what it needs; get that first. |
| `in-progress` | Something already claimed this. Show the Verification log so far and ask. |
| `resolved` | Stop and ask — re-running risks undoing a fix. A returning bug deserves a fresh plan. |
| `invalidated` | Stop. That hypothesis is already disproved; re-run the finder, which will read the log and rule out what died. |

Set `status: in-progress` before starting, so a second agent — or you tomorrow — sees it is
claimed. Read `references/plan-schema.md` if a section is unclear. Plans are hand-editable, so
expect wording to vary; what must be there is the frontmatter and the confirms/refutes lines.

## Step 2 — Record the baseline, then verify

Run the project's test command **before touching anything** and note the result. If the suite
is already red, say so now: "the tests pass" means much less afterwards, and you need to know
which failures were yours.

Then run the plan's Verification steps in order, before touching what the plan means to fix.
They are cheap-first on purpose — most plans die on step 1 for the price of reading ten lines.

Record in the plan's **Verification log**: what you did, what you actually observed (quote the
code or output, not your reading of it), and a verdict of `CONFIRMED` / `REFUTED` /
`INCONCLUSIVE` against that step's own confirms/refutes lines.

`INCONCLUSIVE` is a real answer: the step could not distinguish the cases. Say what would make
it decisive rather than rounding it up because the rest of the plan looks right.

## Step 3 — The gate

**Any step REFUTES H1 →** stop. Do not fix anything and do not fall back to H2 on your own
initiative. Set `status: invalidated`, leave the disproving evidence in the log, and tell the
user what you expected, what you found, and that the finder should run again. Recommending H2
as the next thing to test is fine; acting on it is not.

The reason to stop rather than pivot: the user approved a *scope* along with a hypothesis. A
different hypothesis implies a different scope, which they have not seen. Switching silently
hands them a diff they never agreed to.

**All steps INCONCLUSIVE →** stop as well. Report what blocked verification; applying a fix
now is guessing with someone's codebase.

**H1 confirmed →** continue.

## Step 4 — Apply the fix

Inside **Allowed scope** only, and as small as the confirmed mechanism allows.

- Do not rename, reformat or reorganize anything you are not fixing.
- Do not fix the *other* bug you noticed — note it in the Resolution log; it needs its own plan.
- Do not add dependencies or change public interfaces unless the plan says so.

**If the fix cannot be made inside the allowed scope, stop and ask.** That means the plan's
scope was wrong, and only the user can widen it. Explain what you found, name the file you
would need, and wait. Reaching outside the scope silently is the one failure this skill must
not have: the moment it happens, the plan stops describing the diff and the approval means
nothing.

If the criteria call for a regression test, write it **before** the fix and confirm it fails
for the right reason. A regression test that never failed is decoration.

## Step 5 — Verify scope, then the success criteria

Check that what you changed is what the plan allowed. This skill bundles a script for it —
`scripts/check_scope.py`, alongside this SKILL.md, so give it the path this file was loaded
from, not a path relative to the project:

```bash
python3 <this-skill-dir>/scripts/check_scope.py .bugscope/plan-<bug_id>.md
```

It compares `git status` against the plan's Allowed and Forbidden lists and exits non-zero on
a violation or an undeclared file. Add `--repo <dir>` when the plan belongs to a subproject
of a larger repository. Where you cannot run scripts at all, do the same comparison by hand
against `git status --porcelain`. Either way, a file you touched that the plan does not
mention is a finding to report, not something to quietly leave in.

Then work the Success criteria one at a time, running the project's real commands and pasting
the actual output. If one fails, fix it within scope and re-run. If it cannot be met inside
scope, say so — never edit the criteria to match the result you got.

## Step 6 — Report

Set `status: resolved` and fill the **Resolution log**: what was verified, every file changed
with the hypothesis it traces to, the before/after of the success criteria with real output,
and anything you noticed but deliberately left alone. `references/plan-schema.md` has a worked
example.

Then summarize the same thing in chat, tied to the plan's numbering so the user can read the
diff against the document they approved. If a changed file does not trace to a hypothesis, say
why it was needed — that is the honest version of a scope overrun, and far better than a
silent one.

When nobody is available to answer (a coding agent running unattended on an issue or PR), do
not block and do not guess: record the question in the plan, say it in the PR or issue
comment, and stop at the point where the answer was needed.

---

## Platform notes — Claude Code

Install by copying this skill's folder into `.claude/skills/` (this project) or
`~/.claude/skills/` (every project), or install the `bugscope` plugin from the marketplace
manifest at the repository root.

Files under `references/` are loaded on demand: read them with the Read tool at the point
this document points you at them, not upfront. That is what keeps the always-resident cost
of the skill small.

Ask for it by name when you want it explicitly — "use bugscope-finder on this crash".
