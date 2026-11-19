# State agent contract

Every `bi-*` agent follows this contract. Read it before you start.

## Your input

The dispatcher gives you:

- `key`: the task key. The task files are in `~/.claude-work/<key>/`.
- `state`: the state you run in. One agent can serve more than one state.
- `return_to`: the state the task goes back to after your state, or `null`.
- `kind` and `tier`, when they are set.
- Other values that your agent definition names, for example a step number or critic models.

## Files and IDs

- Read only the files that your agent definition names. Other agents own the other files.
- Use the CLI `~/.claude/skills/build-it/scripts/bi.py`. Call it by its full path.
- Get each new ID from `bi.py next-id <key> <A|Q|D|F>`. Do not choose an ID yourself.
- Do not renumber an ID. Do not delete an ID that another file cites. `bi.py validate <key>` reports a deleted ID that a file still cites.
- Change `kind`, `tier` or `waiting_on` only with `bi.py set <key> <field> <value>`. Do not edit `state.yaml` yourself.
- Write the user's words verbatim where a file says "verbatim". Write all other text in STE-flavored style: short sentences, active voice, one idea per sentence.

## Acceptance criteria and questions

- An acceptance criterion is a line `- A01: <observable outcome>` under `## Acceptance` in `brief.md`.
- An open question is a line `- Q01 [open]: <question>` under `## Open questions`. Its status is `open`, `resolved` or `accepted`.
- You can find a new acceptance criterion in any state. If the user stated it, add it as an `A` line. If it needs confirmation from the user or from colleagues, add it as a `Q` line with status `open`.
- When the task must wait for colleagues to answer a question, run `bi.py set <key> waiting_on Q<n>` and stop with `ASK`. Tell the user what the question is and who must answer it.

## Decisions

- A decision is an entry in `decisions.yaml`. The template shows its fields.
- `agreed` means the user accepted this specific decision in words. An acknowledgement of a long message, or silence, is not agreement.
- `proposed` means you suggested it and the user did not accept it yet. `delegated` means the user told you to decide.
- An `agreed` decision can serve only `A` IDs. A `proposed` or `delegated` decision can serve a `Q` ID that waits on confirmation.
- Record what was rejected and why, in `rejected`.

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

The guard must be one that your agent definition lists for your state. Do not run `bi.py transition` yourself. The dispatcher runs it.
