---
name: interview
description: Interview the user about requirements, design decisions and code style before implementing a task. Writes brief.md and decisions.yaml under the task key.
---

Interview me about the following task:

$ARGUMENTS

I want to be very opinionated about everything technical: what "done" means, the decisions in the solution and the patterns they use, and how the code looks.

1. Read `~/.claude/skills/interview/agendas.md`. Use **recommend-first** mode.
2. Find the task directory. Derive the key from my CLAUDE.md rule. Unless `~/.claude-work/<key>/state.yaml` already has a `state`, run `~/.claude/skills/build-it/scripts/bi.py init --repo . [--ticket <KEY>]`. It prints the key and creates the task files.
3. Run the requirements agenda, then the design agenda, then the style agenda. If the arguments name only some agendas, run only those.
4. Ask one question at a time.
5. Run `bi.py validate <key>` at the end and fix what it reports. Then tell me in one line which files you wrote and which questions are still open.

A later `/build-it <key>` reads these files. It skips the requirements and design work that is already done.
