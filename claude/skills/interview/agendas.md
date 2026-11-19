# Interview agendas

Two callers use these agendas: the `/interview` skill and the `bi-interview` agent inside `/build-it`. The caller says which agendas to run and in which mode.

## Rules for every agenda

- Investigate first. Read the ticket, the code, and the task files before each question. Ask the user only what the code, the tests, the ticket and the user's CLAUDE.md cannot answer. Do not assume. Verify.
- Keep the whole agenda in your context, but ask one question per turn.
- Give one purpose per turn. Say the consequence that the answer changes. Then ask, and stop.
- Answer a question from the user before you continue the agenda.
- Push back when the evidence contradicts a premise. Cite `file:line`.
- Save to the task files at each decision boundary, not after each message. Keep `## Interview cursor` in `brief.md` current: the active question, the referents in play, and unfinished topics. Clear it when the agendas end.

## Modes

- **Recommend first** (`/interview`): lead each question with your recommended answer and its reason, so the user accepts or corrects it. If you have no lean, say so and give the trade-off.
- **User first** (`/build-it`): for the design and style agendas, ask what the user would do before you show options. Then show each option with its consequence. Then give your recommendation and its reason. Then reconcile. The requirements agenda always uses recommend-first.

## Requirements agenda

Goal: the user and you agree on what "done" means before anyone designs.

Settle these, in this order:

1. The outcome: one paragraph under `## Outcome` in `brief.md`.
2. The task kind: feature, bug, recovery or foundation (`~/.claude/skills/build-it/kinds.md`). Set it with `bi.py set <key> kind <kind>`. Give the user the reason in one line.
3. The acceptance criteria. Each one is an outcome that a person can observe. Write each as `- A01: …` under `## Acceptance`. Get IDs from `bi.py next-id <key> A`.
4. The boundaries: what is in scope and what is out of scope, under `## Boundaries`.
5. The integration expectations: which systems, consumers or people the outcome touches.

Write each uncertainty as `- Q01 [open]: …` under `## Open questions`. A criterion that needs a colleague's confirmation starts as a question.

The agenda ends when the outcome, the criteria, the boundaries and the integration expectations are clear enough to design. Each question is `resolved` or `accepted` (accepted means the user accepts the stated assumption). Do not chase zero assumptions.

## Design agenda

Goal: the user sees every decision point in the solution, and understands each decision before it is made. The user's main risk is a decision they did not know they were making.

1. Read `brief.md` and, if it exists, `orient.md`.
2. Find the decision points. A decision point is a place in the solution where two or more defensible choices exist. Include points the user may not know exist: data shape, ownership of a responsibility, error and retry behaviour, where state lives, the seam between modules, what a test pins.
3. Show the user the list of decision points first, one line each, before you ask about any of them. Ask whether the list misses one.
4. For each point, name the software design pattern that fits (for example Strategy, Adapter, Repository, State, Template Method), or say that no named pattern fits. Say what the pattern costs and what not using it costs.
5. Settle the points one at a time. Record each as an entry in `decisions.yaml` with `point`, `choice`, `pattern`, `consequence`, `rejected` and `serves`.
6. A decision that depends on an unconfirmed criterion serves its `Q` ID and stays `proposed`.

Do not write the approach. The user writes it in the next state from these decisions.

## Style agenda

Goal: the code looks the way the user wants it to look.

1. Read the user's CLAUDE.md first. It answers most style questions. Do not ask what it already answers.
2. Ask about what is still open for this task: names of new types and functions, module layout, the shape of errors, the shape of tests.
3. Record each answer as a decision in `decisions.yaml` with `point: style`.
