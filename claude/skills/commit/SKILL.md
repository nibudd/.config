---
name: commit
description: Draft a commit message for staged work, wait for the user's approval or correction, then commit
allowed-tools: Bash
---

Commit the currently staged changes. Draft the message first, wait for the user to approve or correct it, then create the commit.

## Step 1: Inspect staged work

In parallel, run:
- `git status` (no `-uall`) to see staged vs. unstaged vs. untracked
- `git diff --staged` to see exactly what will be committed
- `git log -n 10 --oneline` to match this repo's commit message style

If nothing is staged, tell the user and stop. Do not stage files yourself and do not commit unstaged or untracked work.

If staged files look like they may contain secrets (`.env`, `credentials.json`, private keys, tokens in diffs), flag it before drafting and ask whether to proceed.

## Step 2: Draft the message

Analyze only the staged diff and draft a message:
- Match the style (tense, capitalization, prefix conventions like `feat:`/`fix:`, subject length) of recent commits in this repo
- Keep the subject concise (~50 chars, hard cap 72) and focus on the *why* rather than restating the diff
- Use "add" for wholly new features, "update" for enhancements, "fix" for bug fixes, "refactor" for behavior-preserving changes, etc.
- Add a body only if the change needs context that isn't obvious from the diff
- Do NOT include a `Co-Authored-By` trailer

Present the drafted message to the user in a fenced block and ask them to approve, edit, or reject it. Keep surrounding prose minimal — the user wants to see the message, not commentary.

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
