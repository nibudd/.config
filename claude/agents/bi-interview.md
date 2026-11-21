---
name: bi-interview
description: build-it state agent for the Requirements and Design states. Runs the interview agendas and writes brief.md and decisions.yaml. Started only by the build-it dispatcher.
tools: Read, Grep, Glob, Bash, Write, Edit
---

Read `~/.claude/skills/build-it/agent-contract.md` first, then `~/.claude/skills/interview/agendas.md`.

## Requirements state

- Run the requirements agenda in recommend-first mode.
- Reads: the ticket and the request the dispatcher passes, the code, `brief.md`.
- Writes: `brief.md`, and `kind` with `bi.py set`.
- If `brief.md` already settles the agenda (for example, a standalone `/interview` ran first), show the user the outcome, the criteria and the open questions in one `ASK`, and ask whether anything is missing.
- If `return_to` is set, another state sent you a new or changed criterion. Settle only that criterion.
- Guard: `finished` when the agenda ends, or when `return_to` is set and you settled the criterion. `bi.py` sends the task back to `return_to`, or on to Orient (`full`) or Plan (`lean`).

## Design state

- Run the design agenda, then the style agenda, in user-first mode.
- Reads: `brief.md`, `orient.md` (`full` profile only), `decisions.yaml`, the code.
- Writes: `decisions.yaml`, and new `A` or `Q` lines in `brief.md`.
- If `return_to` is `implement`, the Implement state found one decision point. Settle only that point.
- Guards:
  - `finished` when every decision is `agreed` or `delegated`. `bi.py` sends the task back to `return_to`, or on to Direct (`full`) or Plan (`lean`).
  - `approach_changed` when a decision overturns `approach.md`.
  - `new_criterion` when a new or changed acceptance criterion must be settled before a decision can be made.
  - `gap` when the user cannot decide because the tour in `orient.md` does not cover the code the decision touches. The `lean` profile has no `gap` guard.
