---
name: build-review
description: Drive a task end-to-end through decompose -> implement -> verify -> commit per chunk, with adversarial review and decision gates. For drive-mode work where I learn by reviewing.
allowed-tools: Read Edit Write Bash Grep Glob Agent
disable-model-invocation: true
---

Drive the following task end to end. I (the user) learn by **reviewing** your work, so the point of this loop is a readable trail of small commits and recorded decisions — not to maximize speed, and not to stop after every chunk.

Task / plan:

$ARGUMENTS

Run the stages **serially** — one step at a time, no parallel implementation agents. Serial is easier to review and debug.

Honor my global CLAUDE.md throughout (functional-core/imperative-shell, simple designs, few mocks, parametrized tests, targeted test runs, context7 for library docs, owned-vs-delegated, and the four decision-gate triggers).

### 1. Decompose

Break the task into a dependency-ordered list of small steps. For each: the files it touches, whether it needs tests, a one-line difficulty note, and **whether it hits a decision gate**.

Then critique your own plan: where is this over-built? which steps could be merged or dropped without changing the outcome? is there a materially simpler approach? Cut what doesn't survive and note what you cut. Scope creep and unnecessary complexity are the failure modes I care most about — don't wait for me to ask.

Write the plan to the worklog (format below) so it survives a context clear.

Then delegate the plan to the **`plan-critic`** agent, **on a model other than the one you're running** — same rule and same reason as stage 4, and pass an explicit override or it inherits yours and shares your blind spots. Give it the task statement, the ticket text if there is one, and the plan verbatim. Its job is the one thing your own critique structurally cannot do: check the plan's change surface against the actual repository, rather than against the plan's own account of itself. Fold in what you agree with and carry the rest to the gate.

Then refute its findings the same way stage 4 refutes `diff-critic`'s: one **`refuter`** per finding, in a fresh context, in parallel, with the claim and nothing of the critic's reasoning. A plan finding predicts a consequence, but it rests on present-tense evidence a refuter can check — whether that consumer exists, whether that symbol is public, whether another step already covers it. A finding is real unless its refuter killed it with a concrete cited reason.

**Gate:** present the plan, what you cut and why, the surviving `plan-critic` findings, the refuted ones as one line each (claim + why it was killed, so I can overrule the filter), and the gate-flagged steps. Name the model you delegated to. Then STOP and wait for my "ok"/tweaks before implementing.

### 2. Implement, verify, and commit — per step

For each step in order:

1. Write or adjust tests first where it makes sense, then implement to pass them. One logical change, ~1–3 files. Don't merge steps.
2. Run the **targeted** tests for what you touched. **Never hand me a red chunk** — if it fails, fix it before moving on. If a test itself looks wrong, stop and flag it; never weaken, skip, or delete a test to make code pass.
3. Commit it using my `commit` skill's message rules (≤60-char single-clause subject, default to no body, no ticket/PR reference, no attribution trailer) — but **not** its approval step: inside this loop, draft the message and commit without waiting. Show me the message in your one-line summary. **Do not push.**
4. Update the worklog: tick the step, and record any non-obvious choice under Decisions.
5. Post **one line** saying what landed, and continue to the next step without waiting.

**If a step hits a decision gate** — two or more defensible answers, my owned areas, a public interface or contract, or hard to reverse — stop instead. Ask what I'd do first, then show your answer and reconcile. Resume once I've called it.

If five steps pass with no gate, stop and summarize anyway.

Since I squash-merge, each of these commit subjects becomes a changelog line on `main`. Make each one independently meaningful — no `fix merge conflicts`, no `wip`.

### 3. Worklog

Keep one per task at `~/.claude-work/<key>/worklog.md` — see my CLAUDE.md for how the key is derived. It's keyed by task, not by repo, so a change spanning an API and its frontend keeps a single worklog and a single decision record. Create it in stage 1, update it as you go, and read it first when resuming a task already in progress — it's the answer to "where are we?" without re-reading the diff.

Since the worklog no longer sits inside a repo, `## Repos` is what says where the work actually landed. List every repo the task touches with its branch, and add a repo the first time you touch it.

```markdown
# <task> — <key>

## Repos
- <repo path> @ <branch>

## Steps
- [x] 1. <step> — <commit sha>
- [ ] 2. <step>

## Decisions
- <what was chosen> — rejected: <alternative> (<why>)

## Open
- <question, blocked item, or thing I owe you an answer on>
```

Decisions is the part that matters. One line per non-obvious choice, **including the ones you didn't stop for** — that's what I read instead of sitting through gates, and it's still readable weeks later when the conversation is gone.

### 4. Review — adversarial, cross-model, independently refuted

Attack the diff, don't bless it. A clean review is a conclusion you reach by looking hard, not a starting assumption.

1. Delegate the full branch diff to the **`diff-critic`** agent, telling it what plan to judge the work against. Run it **on a model other than the one you're running** — pass an explicit model override, because without one it inherits yours and the review shares your blind spots. Pick a peer-tier model (Opus / Fable / Sonnet), not Haiku. Say in your summary which model you ran and which you delegated to.
2. For **each** finding it returns, spawn a **`refuter`** in a fresh context — one per finding, in parallel. Refuters must not see `diff-critic`'s reasoning; give them the claim and the code, nothing more.
3. A finding is real unless its refuter killed it **with a concrete cited reason** — a guard, contract, test, or misread at a named `file:line`. "Probably fine" is not a refutation.

**Gate:** present the surviving findings in full, the refuted ones as one line each (claim + why it was killed, so I can see what got filtered and overrule it), the branch diff, and the Decisions section. Then STOP. This is my main review surface — the decisions I didn't gate on land here. Wait for my call on which findings to fix.

### 5. Fix

Apply the findings I approved, then re-run the relevant tests. Commit the fixes as their own step (same rules as stage 2).

### 6. Wrap

Grep the branch diff for `TODO: Update Comment` first and list every hit with its `file:line` and the drafted text. Add whatever you flagged as stale or AI-written along the way to the same list. I rewrite them all before a PR goes up.

Then run the full suite once. Report failures with the actual output — don't paper over them. Summarize what landed, leave anything unresolved under Open in the worklog, and stop. **Do not push** — I review before anything goes upstream.

Throughout: prefer stopping at a gate over guessing. If you're unsure whether something is my call, it's my call.
