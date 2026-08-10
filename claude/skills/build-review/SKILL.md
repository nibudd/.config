---
name: build-review
description: Drive a task end-to-end through decompose -> implement -> verify -> commit per chunk, with adversarial review and decision gates. For drive-mode work where I learn by reviewing.
allowed-tools: Read Edit Write Bash Grep Glob Agent
---

Drive the following task end to end. I (the user) learn by **reviewing** your work, so the point of this loop is a readable trail of small commits and recorded decisions — not to maximize speed, and not to stop after every chunk.

Task / plan:

$ARGUMENTS

Run the stages **serially** — one step at a time, no parallel implementation agents. Serial is easier to review and debug.

Honor my global CLAUDE.md throughout (functional-core/imperative-shell, simple designs, few mocks, parametrized tests, targeted test runs, context7 for library docs, owned-vs-delegated, and the four decision-gate triggers).

### 1. Decompose

Break the task into a dependency-ordered list of small steps. For each: the files it touches, whether it needs tests, a one-line difficulty note, and **whether it hits a decision gate**.

Then critique your own plan before showing it to me: where is this over-built? which steps could be merged or dropped without changing the outcome? is there a materially simpler approach? Report what you cut and why. Scope creep and unnecessary complexity are the failure modes I care most about — don't wait for me to ask.

Write the plan to the worklog (format below) so it survives a context clear.

**Gate:** present the list, the critique, and the gate-flagged steps, then STOP. Wait for my "ok"/tweaks before implementing.

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

Keep one file per branch at `~/.claude/worklog/<repo>-<branch>.md`. Create it in stage 1, update it as you go, and read it first when resuming a task already in progress — it's the answer to "where are we?" without re-reading the diff.

```markdown
# <task> — <branch>

## Steps
- [x] 1. <step> — <commit sha>
- [ ] 2. <step>

## Decisions
- <what was chosen> — rejected: <alternative> (<why>)

## Open
- <question, blocked item, or thing I owe you an answer on>
```

Decisions is the part that matters. One line per non-obvious choice, **including the ones you didn't stop for** — that's what I read instead of sitting through gates, and it's still readable weeks later when the conversation is gone.

### 4. Review — adversarial, cross-model, refutation-checked

Attack the diff, don't bless it. A clean review is a conclusion you reach by looking hard, not a starting assumption.

- Launch a review subagent **on a different model than you're running** (e.g. if you're on Opus, run it on Sonnet) to avoid shared blind spots. Give it the full branch diff and four angles:
  1. **Bugs this change introduced.**
  2. **Latent bugs it exposed** — pre-existing problems the change surfaces.
  3. **Where the plan or design was wrong.**
  4. **Weak or missing test coverage** — would a test actually catch a regression here?
- Then, for **each** finding, run a second check whose only job is to **disprove** it. Default to "refuted" when uncertain. Only findings that survive refutation are real.

**Gate:** present the surviving findings, the branch diff, and the Decisions section, then STOP. This is my main review surface — the decisions I didn't gate on land here. Wait for my call on which findings to fix.

### 5. Fix

Apply the findings I approved, then re-run the relevant tests. Commit the fixes as their own step (same rules as stage 2).

### 6. Wrap

Run the full suite once. Report failures with the actual output — don't paper over them. Summarize what landed, leave anything unresolved under Open in the worklog, and stop. **Do not push** — I review before anything goes upstream.

Throughout: prefer stopping at a gate over guessing. If you're unsure whether something is my call, it's my call.
