# State agent contract

Every `bi-*` agent follows this contract. Read it before you start.

## Your input

The dispatcher gives you:

- `key`: the task key. The task files are in `~/.claude-work/<key>/`.
- `state`: the state you run in. One agent can serve more than one state.
- `return_to`: the state the task goes back to after your state, or `null`. It is the last entry of `return_stack` in `state.yaml`.
- `kind` and `tier`, when they are set.
- `profile`: `full` or `lean`. Null means `full`. Your agent definition says what changes in `lean`.
- Other values that your agent definition names, for example a mode or critic models.

## Files and IDs

- Read only the files that your agent definition names. Other agents own the other files.
- Use the CLI `~/.claude/skills/build-it/scripts/bi.py`. Call it by its full path.
- `decisions.yaml` is a top-level YAML list. `plan.yaml` holds a top-level `steps:` list, and `review.yaml` a top-level `rounds:` list. The templates hold only comments, so write the top-level key with the first entry.
- Get each new ID from `bi.py next-id <key> <A|Q|D|F>`. Do not choose an ID yourself.
- Do not renumber an ID. Do not delete an ID that another file cites. `bi.py validate <key>` reports a deleted ID that a file still cites.
- Change `kind` or `tier` only with `bi.py set <key> <field> <value>`. Do not edit `state.yaml` yourself.
- Write the user's words verbatim where a file says "verbatim". Write all other text in STE-flavored style: short sentences, active voice, one idea per sentence.

## Acceptance criteria and questions

- An acceptance criterion is a line `- A01: <observable outcome>` under `## Acceptance` in `brief.md`.
- An open question is a line `- Q01 [open]: <question>` under `## Open questions`. Its status is `open`, `resolved` or `accepted`.
- You can find a new acceptance criterion in any state. If the user stated it, add it as an `A` line. If it needs confirmation from the user or from colleagues, add it as a `Q` line with status `open`.
- When the task must wait for colleagues to answer a question, follow *Waiting* below.

## Decisions

- A decision is an entry in `decisions.yaml`. The template shows its fields.
- `agreed` means the user accepted this specific decision in words. An acknowledgement of a long message, or silence, is not agreement.
- `proposed` means you suggested it and the user did not accept it yet. `delegated` means the user told you to decide.
- An `agreed` decision cannot serve an `open` question. It can serve an `A` ID, or a `Q` ID that is `resolved` or `accepted`. A `proposed` or `delegated` decision can serve an `open` question.
- `bi.py transition` refuses `finished` from Design while a decision is `proposed`, and from Requirements while a question is `open` and nothing waits on the return stack.
- Record what was rejected and why, in `rejected`.
- In the `lean` profile, the user delegated the decisions. Give each new decision the status `delegated`. Record a decision only when a reviewer can choose differently. Do not record a choice that the brief, the code or a convention forces. Keep each entry to its choice, one reason, and its `rejected` options.

## Waiting

When the task cannot continue until colleagues answer a question:

1. Write your progress under `## Interview cursor` in `brief.md`. Start the entry with your state name. Say what you were doing, what you settled, and what the answer to the question unblocks.
2. End your turn with output in this form, and nothing before it:

```
WAIT Q<n>
<the question, and who must answer it>
```

The dispatcher records `waiting_on` and stops the task. If `Q<n>` is not an open question, it sends you the error. When the answer arrives, a new agent starts in your state.

When you start, read `## Interview cursor` in `brief.md`. If it holds an entry for your state, continue from it, and delete the entry when you no longer need it.

## Talking to the user

You cannot talk to the user directly. The dispatcher relays for you.

When you need the user, end your turn with output in this form, and nothing before it:

```
ASK
<the text for the user>
```

The dispatcher shows that text to the user verbatim. Then it sends you the user's reply, and you continue with your context. Ask one question per turn unless your agent definition says otherwise.

Write text for the user in the user's `colleague` output style: complete sentences, the conclusion first, no filler. At a decision gate, use the gate shape in the user's CLAUDE.md: number each item, give the question in one sentence that ends in `?`, each option in one or two sentences, then a recommendation and its reason in one sentence.

## Finishing

When the work of your state is done:

1. Run `bi.py validate <key>`. Fix each problem it reports.
2. End your turn with output in this form, and nothing before it:

```
DONE <guard>
<at most five lines for the dispatcher: what you wrote and what is still open>
```

The guard must be one that your agent definition lists for your state. Use `finished` where your definition lists it: `bi.py` works out where the task goes from the return stack and the plan, so you do not choose between going forward and going back. Do not run `bi.py transition` yourself. The dispatcher runs it.
