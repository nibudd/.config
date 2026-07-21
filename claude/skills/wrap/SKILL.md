---
name: wrap
description: End-of-session wrap-up — reflect on the session and save anything worth remembering to memory, then hand off to /clear. Run this manually right before clearing context.
---

Wrap up this session before I clear context.

1. **Reflect.** Review what happened this session and identify anything worth persisting to memory. Consider each type:
   - **user** — new facts about me (role, preferences, expertise).
   - **feedback** — guidance or corrections I gave about how you should work, and the *why*.
   - **project** — ongoing work, goals, or constraints not derivable from the code or git history (convert relative dates to absolute).
   - **reference** — external resources (URLs, dashboards, tickets) worth keeping.

2. **Filter hard — be skeptical.** Do NOT save:
   - Anything the repo, git history, or CLAUDE.md already records.
   - Anything that only mattered to this one conversation.
   - A duplicate of an existing memory — update that file instead.
   If nothing clears the bar, say so plainly. An empty wrap-up is a fine outcome, not a failure.

3. **Propose, then save.** List the candidate memories (name, type, one-line content) and wait for my approval or edits before writing anything. For everything approved, follow my memory guidelines exactly: one fact per file with frontmatter, a one-line pointer added to MEMORY.md, related memories linked with `[[name]]`.

4. **Hand off.** Once memories are saved (or we agree there are none), remind me to run `/clear` — you cannot clear context yourself, so the actual wipe is mine to trigger.
