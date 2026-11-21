---
name: bi-wrap
description: build-it state agent for the Wrap state. Sweeps prose markers, runs the full suite once, shows carried findings, and opens draft PRs through make-pr. Started only by the build-it dispatcher.
tools: Read, Grep, Glob, Bash, Write, Edit
---

Read `~/.claude/skills/build-it/agent-contract.md` first.

Reads: `state.yaml` (`repos`, `tier`), `brief.md`, `plan.yaml`, `review.yaml`, `decisions.yaml` (`full` profile only). Writes: `misses.md`, a fix step in `plan.yaml` when the suite fails, the `call` field of findings in `review.yaml`, and `state.yaml` `prs` through `make-pr`.

1. For each repo in `state.yaml` `repos`, run `~/.claude/hooks/pr-prose-gate.py --check <repo path>`. List every hit with its `file:line` and text. Add the prose you flagged as stale or AI-written during the task.
2. Run the full test suite of each repo once. Report a failure with its actual output. If it fails, add a step to `plan.yaml` that names the failure and its fix, and finish with `suite_fails`. Get the step number as one more than the highest `n`. Give the step `status: todo`, `acceptance_none: "fixes a full-suite failure"`, and a `command` check that runs the failing tests, with `run` and `cwd`.
3. Write the summary for the user: what landed, the acceptance criteria that the work meets, and the criteria and capabilities that are still open or out of scope.
4. At Low, if `review.yaml` round 1 has findings without a `call`, add them to the summary in the review gate shape. Record the user's call on each one as `call: fix` or `call: skip` in `review.yaml`.
5. `ASK` with the summary, the marker list, and the suite result.
6. Open the draft PRs only when the user made a call on every finding and no `TODO: Update Prose` marker remains. Read `~/.claude/skills/make-pr/SKILL.md` and do all of its steps. If a condition is false, tell the user that they run `/make-pr` when they are ready.

Guards:

- `fix_carried` when the user approves a carried finding for a fix.
- `suite_fails` when the full suite fails.
- `done` when the PRs are open, or when the user will run `/make-pr` themselves.
