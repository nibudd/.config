---
name: recheck
description: Review work the user wrote, and keep the findings numbered across rounds. Use the first time on a target, then again after each round of fixes. The target is a Google Doc URL, a Jira key, a PR number, a path, or nothing for the working tree.
disable-model-invocation: true
---

Review work that I wrote. Keep one numbered list of findings for the target, and update that list on each round. Do not start a new list.

Target and notes from me:

$ARGUMENTS

### 1. Find the target and its findings file

1. Identify the target from the arguments:
   - A `docs.google.com` URL: read it with the Google Drive connector. Read the tab that the URL names.
   - A Jira key: read the issue, its description, and its acceptance criteria.
   - A PR number: read the PR diff.
   - A path: read that file or directory.
   - No target: read the working-tree diff against the merge base with the default branch, staged and unstaged.
2. Derive the work key from my CLAUDE.md rules (the ticket key, else `<repo>_<branch>`).
3. The findings file is `~/.claude-work/<key>/recheck-<slug>.md`. The slug is short and names the target, for example `design-doc`, `PROG-1314`, `pr-45`, or `working-tree`.
4. If the file exists, this is a later round. Go to step 3. If the file does not exist, this is the first round. Go to step 2.

### 2. First round

1. Read the target completely.
2. Read the context that the target must agree with: the worklog `## Decisions`, the ticket, and any facts summary that you gave me in this session. For prose, this context is the source of truth for the facts.
3. Find the problems. For code, look for bugs, missed cases, missing tests, and conflicts with the design. For prose, look for missing facts, wrong facts, a changed meaning, and text that a reader cannot follow.
4. Write the findings file in the format below. Number the findings `1`, `2`, `3`, and so on. Every finding starts with status `open`.

### 3. Later round

1. Read the findings file.
2. Read the target completely again. Do not trust my notes as proof of a fix. Use them only to know where to look.
3. Give each earlier finding one status:
   - `resolved`: the target no longer has the problem.
   - `open`: the problem is still there. Add one sentence that says what remains.
   - `declined`: I said that I will not change it, in this round or an earlier one. Record my reason if I gave one.
4. Find new problems, including problems that my fixes caused. Give each new finding the next number after the highest number in the file.
5. Update the findings file.

Rules for both rounds:

- Never renumber a finding. Never reuse a number.
- Never raise a `declined` finding again. Do not mention it in the reply.
- Do not write replacement prose for text that I wrote. Point at the location and say what is wrong or missing. I write the fix.
- Do not write the code fix. Say what is wrong and what the fix must do, in one sentence. Write the code only if I ask.
- Do not make findings about style preferences that my CLAUDE.md does not state.

### Findings file format

```markdown
# Recheck — <target>

Target: <URL, key, PR, or path>

| # | Status | Round | Location | Finding |
|---|---|---|---|---|
| 1 | resolved | 1 | §Parser | The parser section does not say which timestamp ranks the duplicate rows. |
| 2 | open | 1 | `src/pipeline_main.py:199` | The `/dlq` handler does not catch `ArchiveError`, so a failed upload returns 500 with no log line. Still open: the catch is there, but the log line is missing. |
| 3 | declined | 2 | AC 3 | AC 3 names the Terraform account as the reader. Declined: the user keeps AC 3 as written. |
```

Each finding is one or two sentences. The `Round` column is the round that found it.

### Reply

Reply in this order, and say nothing more:

1. The round number.
2. The resolved findings, as one line of numbers: `Resolved: 1, 4, 5.`
3. Each `open` finding and each new finding, with its number, its location, and one or two sentences.
4. If no finding is open, say that the target is clear.
