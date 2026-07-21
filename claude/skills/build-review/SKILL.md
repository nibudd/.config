---
name: build-review
description: Drive a task end-to-end through a serial decompose -> implement -> verify -> adversarial review -> fix -> commit loop, with human review gates. For drive-mode work where I learn by reviewing.
allowed-tools: Read Edit Write Bash Grep Glob Agent
---

Drive the following task end to end. I (the user) learn by **reviewing** your work, so the point of this loop is to produce small, reviewable increments with strong self-review — not to maximize speed.

Task / plan:

$ARGUMENTS

Run these stages **serially** — one task at a time, no parallel agents. This is deliberate: serial is easier to review and debug. (Parallelism is a later upgrade, not the default.)

Honor my global CLAUDE.md throughout (functional-core/imperative-shell, simple designs, few mocks, parametrized tests, targeted test runs, context7 for library docs, owned-vs-delegated).

### 1. Decompose
Break the task into a dependency-ordered list of small steps. For each: the files it touches, whether it needs tests, and a one-line difficulty note. If there's no agreed plan yet, or a step touches one of my *owned* areas (architecture, error/retry/idempotency, anything I operate), say so.
**Gate:** present the list and STOP. Wait for my "ok"/tweaks before implementing.

### 2. Implement (per step, serial)
For each step in order:
- Write or adjust the tests first where it makes sense (follow my testing preferences). Then implement to pass them.
- Keep each step to one logical change (~1-3 files). Don't merge steps.
- Never weaken, skip, or delete a test to make code pass. If a test looks wrong, stop and flag it — don't route around it.

### 3. Verify
Run the **targeted** tests for what you touched (not the full suite each time). At the end of all steps, run the full suite once. Report failures with the actual output — don't paper over them.

### 4. Review (adversarial, cross-model, refutation-checked)
Attack the diff, don't bless it. A clean review is a conclusion you reach by looking hard, not a starting assumption.
- Launch a **review subagent on a different model than you're running** (e.g. if you're on Opus, run it on Sonnet) to avoid shared blind spots. Give it the diff and have it look from four angles:
  1. **Bugs this change introduced.**
  2. **Latent bugs it exposed** (pre-existing problems the change surfaces).
  3. **Where the plan / design was wrong.**
  4. **Weak or missing test coverage** (would a test actually catch a regression here?).
- Then, for **each** finding, run a second check whose only job is to **disprove** it. Default to "refuted" when uncertain. Only findings that survive refutation are real.
**Gate:** present the surviving findings AND the diff for me to review myself, and STOP. This is my learning surface — give me a short rationale for the non-obvious choices you made and the alternatives you rejected. Wait for my call on which findings to fix.

### 5. Fix
Apply the confirmed findings I approved, then re-run the relevant tests (and the full suite if the fix was broad).

### 6. Commit
Draft one clean commit message and follow my `commit` skill's norms (wait for my approval, no `Co-Authored-By` trailer). Make **one** commit. **Do not push** — I review before anything goes upstream.
**Gate:** show the message, wait for approval, commit, stop.

Throughout: prefer stopping at a gate over guessing. If you're unsure whether something is my call, it's my call.
