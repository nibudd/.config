---
name: build-it
description: Drive a task end to end as a state machine — requirements, orient, design, direct, plan, implement, review, fix, wrap — with one subagent per state and task files in ~/.claude-work/<key>/. For drive-mode work where I learn the code first, set the approach, and then review.
allowed-tools: Read Bash Agent SendMessage
disable-model-invocation: true
---

Run the following task as the `build-it` state machine:

$ARGUMENTS

You are the dispatcher. You start one subagent per state, relay between me and that subagent, and move the task between states. You do not do the work of a state yourself. Keep your context small: read only `state.yaml` and the summaries that the subagents return. Do not read the other task files, the code, or the diff.

Tools:

- `BI=~/.claude/skills/build-it/scripts/bi.py`. Call it by its full path.
- `~/.claude/skills/build-it/scripts/preview.sh start|stop <key>` controls the live preview of `orient.md`.

## 1. Find or start the task

1. Derive the key from my CLAUDE.md rule: the ticket if I name one, else `<repo>_<branch>`.
2. If `~/.claude-work/<key>/worklog.md` exists, it is an old task. Tell me to use `/build-it-v1` for it, and stop.
3. If `~/.claude-work/<key>/state.yaml` exists and its `state` is set, resume the task from that state. Tell me the state in one line.
4. Otherwise, run `$BI init --repo . [--ticket <KEY>]`. It prints the key and creates the task files from the templates.
5. If the task touches more than one repo, tell me. The `repos` list in `state.yaml` is the record of every repo and branch.

## 2. The loop

Repeat until the state is `done`:

1. Read `state.yaml`. If `waiting_on` is set, tell me which question the task waits on, and stop. When the answer arrives, I clear it with `$BI set <key> waiting_on null` and resume with `/build-it <key>`.
2. Start the agent for the state (table below) with the Agent tool. Give it `key`, `state`, `return_to` (the last entry of `return_stack`, or null), `kind`, `tier`, and the extra values in the table. Give it my task text only in the Requirements state.
3. Read the agent's final output.
   - If it starts with `ASK`, show me the text after the `ASK` line verbatim, with nothing added, and end your turn. When I reply, send my reply verbatim to the same agent with `SendMessage`. Then repeat step 3 with its next output.
   - If it starts with `WAIT Q<n>`, run `$BI set <key> waiting_on Q<n>`. If that fails, send the error to the same agent with `SendMessage` and repeat step 3. If it succeeds, tell me which question the task waits on and who must answer it, and stop.
   - If it starts with `DONE <guard>`, run `$BI transition <key> <guard>`. For `finished`, the output names the guard it resolved to. Post one line: the old state, that guard, the new state, and the agent's summary in one sentence.
4. If `transition` fails, send its error to the same agent with `SendMessage` once, and ask it to fix the files or choose another guard. If it fails again, show me the error and stop. Do not edit task files yourself.
5. If `transition` returns `"summarize": true`, five steps passed with no gate. Post a summary of those five steps from the agents' summaries, and wait for me. Then run `$BI transition <key> summarized` and continue.

| State | Agent | Extra values |
|---|---|---|
| requirements | `bi-interview` | my task text and ticket |
| orient | `bi-orient` | — |
| design | `bi-interview` | — |
| direct | `bi-direct` | — |
| plan | `bi-plan` | `critic_models` with two models |
| implement | `bi-implement` | `mode: step` |
| review | `bi-review` | `round: 1`, `critic_models` |
| fix | `bi-implement`, then `bi-review` | `mode: fix`. Then `round: 2`, the fix commit range from the implement summary, `critic_models` |
| wrap | `bi-wrap` | — |

Start a new agent for each Implement step, so that each step starts with a clean context.

In the Fix state, `bi-implement` finishes with `DONE finished`. Do not run a transition for it. Start `bi-review` for round 2, and run the transition on the guard that `bi-review` returns.

## 3. Critic models

`critic_models` must not contain the model you run on. Pick peer-tier models (Opus, Fable, Sonnet), never Haiku. For Plan, always give two different models, because the tier is not known until `bi-plan` sets it. For Review and Fix, give one model at Low and Standard, and two different models at High. Tell me which model you run on and which models the critics run on, once per task.

## 4. Preview

When the task enters Orient for the first time, run `preview.sh start <key>`. When the task reaches `done`, run `preview.sh stop <key>`. If the preview fails to start, tell me in one line and continue.

## 5. Rules

- Do not answer an agent's question for me. Do not shorten, reword or summarise an `ASK` text.
- Do not skip a state or choose a guard yourself. Only an agent's `DONE` line or my explicit instruction picks a guard. If I tell you to move the task, run the transition with the guard I name, and say which guard you used.
- If an agent stops without an `ASK` or a `DONE` line, send it one message that asks it to finish under its contract. If it fails again, tell me and stop.
- If I am unsure whether something is my call, it is my call.

Reference files for the agents: `agent-contract.md`, `kinds.md`, `tiers.md`, and `~/.claude/skills/interview/agendas.md`.
