---
name: make-pr
description: Plan how the current branch's commits split into PRs. Summarize each PR so the user can write its title and body. Then push the branches and open the PRs as drafts with the user's text.
allowed-tools: Bash Read Grep Glob Skill
disable-model-invocation: true
---

Open PRs for the work on the current branch. Plan the split first, summarize each PR for me, wait for my approval and my prose, then push and create them as drafts.

The unit here is a **reviewable PR**, not a commit. One PR usually holds several commits. Commits are the changelog; PRs are the review surface.

**You do not write the title or the body.** I do. See the moratorium in my CLAUDE.md — your job is the split, the mechanics, and a summary I write from.

## Step 1: Inspect

In parallel, run:

- `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` for the base branch, and `git rev-parse --abbrev-ref HEAD` for the current one
- `git log --oneline <base>..HEAD` — the commits in play
- `git diff --stat <base>...HEAD` — the size and shape
- `gh pr list --head <current-branch> --state all` — whether a PR already exists
- `git status` — uncommitted work
- `git diff <base>...HEAD | grep -n 'TODO: Update Comment'` — prose in the diff still waiting on me

Stop if: I'm on the default branch, there are no commits ahead of base, or `gh` isn't authenticated (`gh auth status`).

**Stop if a `TODO: Update Comment` marker survives anywhere in the diff.** List each one with its `file:line` and the drafted text beside it, then wait. Add whatever you flagged as stale or AI-written while you worked to the same list. I rewrite them and commit before any PR goes up.

Never commit, stage, or stash anything. If there's uncommitted work, say what it is and that it won't be included, then continue.

If a PR already exists for this branch, don't open a second one — summarize it the same way and offer to replace its body with text I give you.

Flag possible secrets in the diff (`.env`, `credentials.json`, keys, tokens) before summarizing, and ask before pushing anything.

**Read the worklog** at `~/.claude-work/<key>/worklog.md` if one exists (key derivation is in my CLAUDE.md). Its `## Decisions` section is the raw material for the *Why* — it's the part the diff can't show. If there's no worklog, get the Why from the commit bodies and our conversation.

## Step 2: Plan the split

Group the commits into PRs. Each PR is one structurally or functionally related change.

**You may only split at existing commit boundaries.** No rebasing, reordering, cherry-picking, or history rewriting. That means every group must be a **contiguous run** of commits, and each new branch is just a pointer at the last commit of its group — nothing is rewritten.

If the natural grouping isn't contiguous — related commits are interleaved with unrelated ones — you can't get there without a reorder. Say so, show the coarser grouping that *is* possible, and let me decide whether to accept it or authorize a rebase.

If I authorize a rebase, anything **outside the ticket's original scope** — drive-by fixes, unrelated cleanups, tooling or config changes picked up along the way — goes at the **end** of the chain, never the start. The in-scope work is what needs review and merge; it shouldn't sit behind a PR nobody asked for. Order the in-scope groups by the rules below, then append the out-of-scope ones.

### When to split

Signals a PR is too big:

- more than ~400 lines of hand-written change (exclude lockfiles and generated output from the count — and if a generated file dominates the diff, say so in the summary with the real hand-written number)
- the honest *What* needs an "and", or more than ~5 points
- it mixes concerns a reviewer would judge with different eyes — new logic vs. infra vs. docs

### When not to split

- **A change and its tests** stay together, always.
- **A change and the config that makes it safe** stay together. If two edits are only correct when applied at once, splitting them re-arms the trap they defuse — that's worse than a big PR. Tell me they're together and why, so I can say it in the body.
- A rename and its call sites.

### Chain order

Order so every PR is independently mergeable and leaves the default branch working: additions first, then the change that activates them. Call out explicitly which PR is the one that changes production behaviour — usually exactly one, and it's the one that needs the real review.

Out-of-scope work comes last, after every in-scope PR — only reachable with a rebase, per above.

Base of PR 1 is the repo's default branch. Base of PR *n* is the head branch of PR *n−1*.

### Branch names

Reuse the current branch's ticket prefix verbatim, including its casing, then a short dash-separated name: `prog-1048/bq-store`, `PROG-1013/port-metrics`. Short and descriptive — no dates, no author, no `-v2`.

The last group's head branch is the **current branch** — reuse it rather than creating a duplicate at the same commit. Create branches for the earlier groups with `git branch <name> <sha>` at each group's last commit.

## Step 3: Summarize each PR for me to write from

Write no title and no body. For each PR in the split, give me a summary I write the real text from.

Each summary covers:

- **What the PR accomplishes** — 3 to 5 points, one line each. Name behaviour and structure, not paths, except where a path is the clearest way to say it. Never write a file-by-file or commit-by-commit walkthrough. The diff tab is right there.
- **Why** — one or two sentences. What was broken or missing, or what this unblocks. If the PR doesn't change production behaviour yet, say so.
- **What a reviewer would otherwise get wrong** — a load-bearing ordering constraint, a rejected alternative, or an accepted risk. A generated file that inflates the diff counts too. Omit this by default. At most 3 points when it earns a place.

Across the whole set, name once which PR changes production behaviour.

Give me the **prefix** and the **ticket** too. Both are derivable facts rather than prose, so you pick them. Take the prefix from what the PR does, not from the branch name: `feat` for a new capability, then `fix`, `refactor` for behaviour-preserving, `perf`, `docs`, `test`, `build`, `ci`, `chore`. Take the ticket from the branch prefix, upper-cased. If the worklog or commits name a different ticket than the branch does, ask which is right rather than guessing. The subject line itself is mine.

Run each summary through the `asd-ste100` skill in **STE-flavored** mode before you show it. Write it to the scratchpad and lint it:

```
python3 ~/.claude/skills/asd-ste100/scripts/ste-lint.py <scratchpad>/pr-<n>.md
```

Fix every hard violation unless the fix costs a fact, a hedge or a scope qualifier. Keep whatever terms the codebase uses. Show me the simplified summary alone — not the draft beside it, and no account of what the pass changed.

## Step 4: Gate — present and stop

Show, compactly:

| # | branch | base | title | commits | ~lines |
|---|--------|------|-------|---------:|-------:|

Leave the title cell empty. I fill it. Then each summary in full. Then **STOP and wait**.

Two things wait on me here. Push nothing until I approve the split, and open no PR until I hand you a title and a body. When I do, use them exactly as written — don't reformat them, don't extend them, and don't run them through the linter.

## Step 5: Execute

Once I've approved the split and given you my titles and bodies, work **bottom-up** through the chain:

1. `git push -u origin <branch>` for that group's branch.
2. Write my body to a file in the session scratchpad and create the PR with `--body-file` — cleaner than a heredoc and it can't be mangled by backticks or `$(...)` in the body:

```
gh pr create --draft --base <base-branch> --head <head-branch> \
  --title "<my title>" --body-file <scratchpad>/pr-<n>.md
```

All PRs open as **drafts**. I mark them ready myself.

3. Once every PR exists, do one pass of `gh pr edit <number> --body-file <...>` to fill the real PR numbers into the stacked line. Skip this for a single PR.

You may add the stacked line — `<N> of <M>. Stacked: #12 → **this** → #14.` — to my body without asking. It is a set of identifiers rather than prose. Add it only when there's more than one PR, and put it at the top. Everything else in the body stays exactly as I wrote it.

Never add `Generated with Claude Code`, `Co-Authored-By`, or any other Claude or Anthropic attribution, to a title or a body, in any repo, for any reason.

Then report the PR URLs, one line each, and record them in the worklog under a `## PRs` section (`- #<n> <title> — <url>`) so they survive a context clear.

If a push is rejected or `gh pr create` fails, stop and show the error. Don't force-push, and don't retry with `--force` or a different branch name without asking.
