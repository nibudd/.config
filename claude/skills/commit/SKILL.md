---
name: commit
description: Draft a commit message for staged work, wait for the user's approval or correction, then commit
allowed-tools: Bash
disable-model-invocation: true
---

Commit the currently staged changes. Draft the message first, wait for the user to approve or correct it, then create the commit.

## Step 1: Inspect staged work

In parallel, run:
- `git status` (no `-uall`) to see staged vs. unstaged vs. untracked
- `git diff --staged` to see exactly what will be committed
- `git log -n 10 --oneline` to pick up this repo's *conventions* — mood, capitalization, and whether it uses `feat:`/`fix:` prefixes

If nothing is staged, tell the user and stop. Do not stage files yourself and do not commit unstaged or untracked work.

If staged files look like they may contain secrets (`.env`, `credentials.json`, private keys, tokens in diffs), flag it before drafting and ask whether to proceed.

## Step 2: Draft the message

Analyze only the staged diff. Follow this repo's conventions from step 1, but do **not** infer subject length from history — apply the limits below regardless of what recent commits look like.

### Subject — hard constraints

These commits are not the final record. The user squash-merges, and GitHub collects the branch's commit messages into the squash body under the PR title — so **each subject becomes one changelog line on `main`** and has to stand on its own there, without the branch context.

- **60 characters max**, excluding any ticket or PR reference. A limit, not a target to approach.
- **One clause.** If the subject needs an "and", that is the signal it is really two commits — see "when the subject won't fit" below.
- **Name the effect, not the edit.** The diff already shows which methods moved; the subject says what is now true.
  - ❌ `Rename method to find_and_save_matching_event_participants and update SQL execution for filter event participations`
  - ✅ `Read filter participants from precomputed metrics`
- Imperative mood, no trailing period.
- Use "add" for wholly new features, "update" for enhancements, "fix" for bug fixes, "refactor" for behavior-preserving changes, etc.

### Ticket and PR references — don't add them

Do not prefix the subject with a Jira key (`PROG-123:`) or append a PR number (`(#365)`), even when recent history shows both:

- the ticket reference belongs on the **PR title**, which becomes the squash subject on `main`
- GitHub appends `(#NNN)` itself on squash merge

### Body — default to none

Most commits need no body at all — and bodies are collected into the squash body too, so a verbose one compounds there. Add one **only** to record something the diff cannot show:

- a rejected alternative and why
- a non-obvious constraint or failure mode that motivated the approach
- a gotcha that will bite the next reader

**Hard cap: 3 bullets, 2 lines each.** If it doesn't fit, the surplus is not commit-message material.

**Never** put these in a body:

- a narration of what changed — the diff shows it
- a list of the tests added, or test-repair notes
- `Bugs:` / `Tests:` / `Changes:` sections, or any heading
- process commentary ("follow-up fixes", "repair the tests the port broke")

A one-line rejected alternative earns its place; a review narrative does not. Once a body grows sections, test lists, or paragraph prose, it has become a review report — and that belongs in the review conversation and the task's plan notes, **not** in `git log`.

### Trailers

**NEVER** add `Co-Authored-By`, `Generated with`, or any other Claude/Anthropic attribution trailer. Not on any commit, in any repo, for any reason.

### When the subject won't fit

If no honest ≤60-char single-clause subject exists, the staged work is bundling unrelated changes. Do not stretch the subject and do not restage anything yourself. Say so, and show the split you'd make:

> This looks like two commits: (1) `Fix hour_bucket wrapping across UTC midnight`, (2) `Cover hourly bucketing with a SQLMesh model test`. Want me to draft them separately, or commit as one?

Then let the user decide.

### Present it

Show the drafted message in a fenced block and ask the user to approve, edit, or reject. Keep surrounding prose minimal — they want to see the message, not commentary.

## Step 3: Wait for approval

Stop and wait for the user's response. Do not commit until they approve. If they correct the message, use their corrected version verbatim. If they reject, stop without committing.

## Step 4: Commit

Once approved, create the commit with the approved message via a HEREDOC so formatting is preserved:

```
git commit -m "$(cat <<'EOF'
<approved message here>
EOF
)"
```

Then run `git status` to confirm the commit succeeded.

If a pre-commit hook fails: the commit did NOT happen. Fix the underlying issue, re-stage as needed, and create a NEW commit. Do not use `--amend` (that would modify the previous commit) and do not use `--no-verify` to skip hooks.
