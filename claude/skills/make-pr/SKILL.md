---
name: make-pr
description: Turn the current branch's commits into one PR, or a chain of stacked PRs when the work should be split. Drafts titles and descriptions, waits for approval, then pushes and opens them as drafts.
allowed-tools: Bash Read Grep Glob Skill
disable-model-invocation: true
---

Open PRs for the work on the current branch. Plan the split first, wait for my approval, then push and create them as drafts.

The unit here is a **reviewable PR**, not a commit. One PR usually holds several commits. Commits are the changelog; PRs are the review surface.

## Step 1: Inspect

In parallel, run:

- `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` for the base branch, and `git rev-parse --abbrev-ref HEAD` for the current one
- `git log --oneline <base>..HEAD` — the commits in play
- `git diff --stat <base>...HEAD` — the size and shape
- `gh pr list --head <current-branch> --state all` — whether a PR already exists
- `git status` — uncommitted work

Stop if: I'm on the default branch, there are no commits ahead of base, or `gh` isn't authenticated (`gh auth status`).

Never commit, stage, or stash anything. If there's uncommitted work, say what it is and that it won't be included, then continue.

If a PR already exists for this branch, don't open a second one — offer to rewrite its body instead.

Flag possible secrets in the diff (`.env`, `credentials.json`, keys, tokens) before drafting, and ask before pushing anything.

**Read the worklog** at `~/.claude-work/<key>/worklog.md` if one exists (key derivation is in my CLAUDE.md). Its `## Decisions` section is the raw material for the *Why* — it's the part the diff can't show. If there's no worklog, get the Why from the commit bodies and our conversation.

## Step 2: Plan the split

Group the commits into PRs. Each PR is one structurally or functionally related change.

**You may only split at existing commit boundaries.** No rebasing, reordering, cherry-picking, or history rewriting. That means every group must be a **contiguous run** of commits, and each new branch is just a pointer at the last commit of its group — nothing is rewritten.

If the natural grouping isn't contiguous — related commits are interleaved with unrelated ones — you can't get there without a reorder. Say so, show the coarser grouping that *is* possible, and let me decide whether to accept it or authorize a rebase.

If I authorize a rebase, anything **outside the ticket's original scope** — drive-by fixes, unrelated cleanups, tooling or config changes picked up along the way — goes at the **end** of the chain, never the start. The in-scope work is what needs review and merge; it shouldn't sit behind a PR nobody asked for. Order the in-scope groups by the rules below, then append the out-of-scope ones.

### When to split

Signals a PR is too big:

- more than ~400 lines of hand-written change (exclude lockfiles and generated output from the count — and if a generated file dominates the diff, say so in *Notes* with the real hand-written number)
- the honest *What* needs an "and", or more than ~5 points
- it mixes concerns a reviewer would judge with different eyes — new logic vs. infra vs. docs

### When not to split

- **A change and its tests** stay together, always.
- **A change and the config that makes it safe** stay together. If two edits are only correct when applied at once, splitting them re-arms the trap they defuse — that's worse than a big PR. Say in the body why they're together.
- A rename and its call sites.

### Chain order

Order so every PR is independently mergeable and leaves the default branch working: additions first, then the change that activates them. Call out explicitly which PR is the one that changes production behaviour — usually exactly one, and it's the one that needs the real review.

Out-of-scope work comes last, after every in-scope PR — only reachable with a rebase, per above.

Base of PR 1 is the repo's default branch. Base of PR *n* is the head branch of PR *n−1*.

### Branch names

Reuse the current branch's ticket prefix verbatim, including its casing, then a short dash-separated name: `prog-1048/bq-store`, `PROG-1013/port-metrics`. Short and descriptive — no dates, no author, no `-v2`.

The last group's head branch is the **current branch** — reuse it rather than creating a duplicate at the same commit. Create branches for the earlier groups with `git branch <name> <sha>` at each group's last commit.

## Step 3: Draft titles

Format: `<prefix>: <TICKET> <subject>`

```
feat: PROG-1046 add the ShareMyData callback capture service
fix: PROG-973 stop leaking program names in DR breadcrumbs
refactor: PROG-1013 read filter participants from precomputed metrics
```

- **Prefix** from what the PR does, not from the branch name: `feat` (new capability), `fix`, `refactor` (behaviour-preserving), `perf`, `docs`, `test`, `build`, `ci`, `chore`.
- **Ticket** from the branch prefix, upper-cased. If the worklog or commits name a different ticket than the branch does, ask which is right rather than guessing.
- **Subject**: ≤60 characters, one clause, imperative, no trailing period. Derive it from the branch name but rewrite it to **name the effect, not the edit** — same rule as my `commit` skill, and for the same reason: I squash-merge, so this title becomes a changelog line on `main` and has to stand alone there.
- Don't append `(#NNN)` — GitHub does that on squash merge.

## Step 4: Draft descriptions

Keep them short. The reviewer's attention is the scarce resource, and a long description spends it before they reach the diff.

```markdown
<N> of <M>. Stacked: #12 → **this** → #14.

# What
- <what was done — 3 to 5 points, one line each>

# Why
<one or two sentences>
```

- **Stacked line** only when there's more than one PR. Single PR: omit it entirely.
- **What** — a handful of points describing *what was done*. Not a file-by-file walkthrough; the diff tab is right there. Name behaviour and structure, not paths, except where a path is the clearest way to say it.
- **Why** — a sentence or two. What was broken or missing, or what this unblocks. If the PR doesn't change production behaviour yet, say so here in a clause.
- **Notes** — a third `# Notes` section is allowed but **default to omitting it**. Add it only for something a reviewer would otherwise get wrong: a load-bearing ordering constraint, a rejected alternative, an accepted risk, a generated-file line count. Hard cap 3 bullets, one line each. Additional context to an absolute minimum.

Never include:

- a file-by-file or commit-by-commit narration — GitHub shows both
- an inventory of the tests added, or a test-plan checklist
- `Generated with Claude Code`, `Co-Authored-By`, or any other Claude/Anthropic attribution
- headings beyond What / Why / Notes, and no emoji headers
- process commentary about how the work went

### Simplify before the gate

Run the drafted titles and bodies through the `asd-ste100` skill in **STE-flavored** mode. A PR body is explanatory prose for a reviewer, so apply the structural rules and drop the one-word-one-meaning lockdown.

Write each body to the scratchpad first and lint it mechanically:

```
python3 ~/.claude/skills/asd-ste100/scripts/ste-lint.py <scratchpad>/pr-<n>.md
```

Fix every hard violation unless the fix costs a fact, a hedge or a scope qualifier. Keep the reviewer's own terms for anything the codebase names.

Show me the simplified body at the gate. Do not show the draft and the rewrite together, and do not report what the pass changed.

## Step 5: Gate — present and stop

Show, compactly:

| # | branch | base | title | commits | ~lines |
|---|--------|------|-------|---------:|-------:|

Then each drafted body in full, in a fenced block. Then **STOP and wait**.

This is a decision gate: pushing branches and opening PRs is outward-facing and awkward to undo. Don't push anything until I approve. If I correct a title or body, use my version verbatim.

## Step 6: Execute

Once approved, working **bottom-up** through the chain:

1. `git push -u origin <branch>` for that group's branch.
2. Write the body to a file in the session scratchpad and create the PR with `--body-file` — cleaner than a heredoc and it can't be mangled by backticks or `$(...)` in the body:

```
gh pr create --draft --base <base-branch> --head <head-branch> \
  --title "<title>" --body-file <scratchpad>/pr-<n>.md
```

All PRs open as **drafts**. I mark them ready myself.

3. Once every PR exists, do one pass of `gh pr edit <number> --body-file <...>` to fill the real PR numbers into the stacked line. Skip this for a single PR.

Then report the PR URLs, one line each, and record them in the worklog under a `## PRs` section (`- #<n> <title> — <url>`) so they survive a context clear.

If a push is rejected or `gh pr create` fails, stop and show the error. Don't force-push, and don't retry with `--force` or a different branch name without asking.
