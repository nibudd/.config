---
name: workflow-review
description: Analyze recent Claude Code session history and suggest workflow improvements
allowed-tools: Read Bash Grep Glob WebSearch WebFetch
disable-model-invocation: true
---

Review the user's recent Claude Code usage and suggest workflow improvements.

Steps:

0. **Pick up where the last review left off.** Look for previous reviews at `~/.claude-work/workflow-review/workflow-review-*.md` and read the most recent one's status section. Report on anything still outstanding **before** proposing anything new — a deferred item that's now unblocked usually beats a fresh idea. Note whether whatever it was waiting on has actually happened.
1. Take into account any comments/suggestions i have from $ARGUMENTS
1. Read `~/.claude/history.jsonl` to understand recent session patterns (tools used, common tasks, repeated prompts, errors encountered, types of questions or tasks I spend extra time on)
2. Check what's currently configured:
   - `~/.claude/settings.json` for hooks and settings
   - `~/.claude/skills/` for installed skills
   - `~/.claude.json` for MCP servers
   - `~/.claude/CLAUDE.md` for directives
3. Look for patterns like:
   - Repetitive tasks that could become a skill or command
   - Manual steps that could be automated with hooks
   - Frequent questions about libraries that would benefit from an MCP server
   - Recurring corrections or preferences not yet captured in CLAUDE.md
   - Permission prompts that could be pre-allowed in settings
4. Research external sources for ideas I might be missing:
   - Search the web for current suggestions, new ideas, and recommendations on Claude Code / agentic-coding workflows, prompting, and productivity practices.
   - Review the official Claude Code documentation (https://docs.claude.com/en/docs/claude-code) for features, commands, hooks, settings, or integrations that exist but I'm not currently using — cross-reference against what step 2 found is configured.
   - Prefer recent, reputable sources; note when a suggested feature depends on a Claude Code version newer than mine.
5. Suggest concrete improvements:
   - Specific skills, hooks, or MCPs to add (with examples)
   - Claude Code features/commands I'm not using yet that fit my patterns
   - CLAUDE.md directives to add or refine
   - Settings changes
   - Process changes the user could make themselves

Keep suggestions actionable and prioritized. Focus on the highest-impact improvements first. Separate "capture what I already do" changes from "new ideas worth trying" so I can tell which are safe vs. experimental.

Write the review to `~/.claude-work/workflow-review/workflow-review-<YYYY-MM-DD>.md` — a fixed key rather than a ticket, since these reviews form one continuous series regardless of where the session is running — and always with a status section at the end recording what's done, what's outstanding, and what each outstanding item is waiting on. Step 0 of the next review reads it. Keep that section current as items land.
