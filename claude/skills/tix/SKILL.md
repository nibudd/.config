---
name: tix
description: Use for personal tickets in nibudd/.claude-work. A personal ticket is a task for a side project or a personal project, for example the build-it TUI or the home Plex server. Use it to create, find, claim, update, comment on, or close one. Also use it when the user asks what to work on next in a personal project. Do not use for Jira tickets.
---

# Personal tickets (tix)

Personal tickets are GitHub issues in the private repo `nibudd/.claude-work`. The `tix` CLI reads and writes them and checks each label value before the write. A GitHub Action on the repo also repairs labels after every change.

## Find the CLI

Use the first command that exists:

1. `~/.claude-work/bin/tix` (a local machine).
2. `bin/tix` at the root of a `nibudd/.claude-work` checkout (a cloud session on that repo).
3. If neither exists, use `gh` with the rules in "Fallback without tix".

`tix` needs `gh` with access to the repo. It works from any directory.

## Labels

Each open ticket has exactly one label for each prefix:

| Prefix | Values |
|---|---|
| `project:` | Get the current list with `gh label list -R nibudd/.claude-work --search project:`. Examples: `tui`, `plex`. |
| `priority:` | `high`, `med`, `low` |
| `author:` | `nibudd` when the user wrote the ticket text. `agent` when you wrote it. |
| `status:` | `to-do`, `in-progress`. Only open tickets have a status. |

A closed ticket has no `status:` label. The close reason gives the result: "completed" means done, and "not planned" means scrapped.

Do not create a new label. If a ticket needs a project that does not exist, ask the user.

## Commands

Read:

```sh
tix list                                  # open tickets
tix list --project tui --status to-do --json
tix list --priority high --json
tix list --state closed --search "plex transcode"
tix show 12 --json                        # body and comments
```

Use `--json` when you parse the output.

Write:

```sh
tix new --title "Add a task picker" --project tui --priority med --author agent --body-file /path/to/body.md
tix set 12 status in-progress             # claim the ticket before you start work
tix set 12 priority high                  # also: project, author
tix comment 12 "Picker works. The filter is still slow with 500 tasks."
tix done 12 --comment "Merged in the config repo."
tix scrap 12 --comment "The user does not need this now."
tix reopen 12                             # sets status:to-do
```

`tix new` requires all of `--title`, `--project`, `--priority`, `--author`, and one of `--body` or `--body-file`. It sets `status:to-do` and prints the issue URL.

## Exit codes

- `0`: The command succeeded.
- `2`: A label value is not valid. The error message lists the valid values. Use one of them, or ask the user.
- `1`: The `gh` command failed. The error message contains the `gh` error.

## Work procedure

1. Before you start work on a ticket, run `tix set <n> status in-progress`.
2. When you find a fact that the next person needs, add a comment. Examples: a blocker, a decision, a test result.
3. When the work is complete and verified, run `tix done <n> --comment "<result>"`.
4. If the user cancels the work, run `tix scrap <n> --comment "<reason>"`.
5. Do not close a ticket that the user did not ask you to work on.

## Fallback without tix

Use `gh` with `-R nibudd/.claude-work` and obey the same label rules:

```sh
gh issue create -R nibudd/.claude-work --title "..." --body "..." \
  --label project:tui --label priority:med --label author:agent --label status:to-do
gh issue edit 12 -R nibudd/.claude-work --remove-label status:to-do --add-label status:in-progress
gh issue close 12 -R nibudd/.claude-work --reason completed --comment "..."
gh issue close 12 -R nibudd/.claude-work --reason "not planned" --comment "..."
gh issue list -R nibudd/.claude-work --label project:tui --json number,title,labels
```

If you add a label with the same prefix as an existing label, the Action removes the old label. If you omit `project:`, `priority:`, or `author:`, the Action adds a comment that names the missing prefix. Then add the label.
