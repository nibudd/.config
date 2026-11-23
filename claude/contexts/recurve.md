# Recurve

- Secrets follow `~/dev/docs/ADR/ADR-015_standardized_app-based_secret_access.md` and `~/dev/docs/ADR/ADR-019-secret-management-environments.md` — read both before designing anything that touches secrets. Store secrets in Google Secret Manager in the environment-scoped projects `recurve-secrets-production` / `recurve-secrets-staging`, never co-locating environments and never in `oee-secrets` (retiring). Get them to apps as **Terraform-generated env vars** (`env.value_source.secret_key_ref`), not via the Secret Manager client library; only the Terraform/CI service account gets read access, per-secret, and app service accounts get none. Exception: a service that must reload config mid-run may use the library. Neither ADR mandates a bulk migration, but new secrets always go to the new stores and existing ones move when you touch that service — so flag the migration rather than extending the old pattern

## Jira tickets

- **Ticket state follows the subtask tree.** Don't scrap a ticket unless every subtask is scrapped. Don't mark a parent Done unless every subtask is Done or scrapped, with at least one Done — otherwise it's scrapped, not done. When a subtask's work is real but belongs elsewhere, move it before closing the parent rather than absorbing it
- **A new ticket is created with an auto-generated subtask.** When I'm creating subtasks on it too, repurpose that one as the first of them — retitle and rewrite it in place — rather than leaving it sitting there and creating a full set alongside it. If I don't need to create subtasks, leave the auto-generated subtask as-is.
- **Atlassian MCP reads truncate at about five issues**, whatever `maxResults` says, and `fields` does not narrow them. Query 4–6 keys at a time, and list subtasks with `parent = KEY` rather than `parentEpic`. `transitionJiraIssue` rejects an assignee, so assign with `editJiraIssue` first. PROG transition ids: To Do 11, In Progress 21, In Review 31, Done 41, Scrapped 2, On Hold 42

## Jira descriptions and comments

I write both. You gather and summarize, per the moratorium. These rules say what belongs in the summary you hand me. Size it to what I write from it. A comment lands at 40–80 words, so don't hand me three paragraphs for one.

**For a description**, give me the problem or goal in one sentence. Then the conditions someone could check the finished work against, one per line. Each one is an outcome a person can observe. Then any constraint, schema, interface shape or external dependency that would change what someone builds. Leave out background, motivation and history. Leave out the implementation sequence, since naming the files or the steps freezes a plan before I decide it. Leave out whatever the epic or parent ticket already holds, and name that ticket instead.

**For a comment**, give me what happened and the one thing still open. Round the numbers and drop the identifiers — "refused it with a 503, no retry within 45min", not exact Zulu timestamps, transaction ids, byte counts or hashes. Never round below what you actually observed: where the observation window *is* the finding, 45 minutes of polling does not become "15min". Name the mechanism in a reader's terms rather than the implementation's — "a 'respond with <status_code>' env var" beats "`FORCE_STATUS`, merged in repo#14". Keep method, rationale and process out. They live in the description or the worklog.

**In both**, keep the identifiers that survive — ticket keys, file paths, endpoints, table and field names, env var names — and drop the ones that rot: line numbers, commit shas, branch names.

Post my text unchanged once I hand it back. Link every ticket reference as `<site>/browse/<KEY>` rather than leaving a bare key in prose. Use Jira's issue link for a real relationship — blocks, is blocked by, relates to — rather than naming it in the text. Progress, findings and status changes go in a comment. A description stays the record of what was asked and changes only when the requirements do. When I edit a description, I write the comment that goes with it.
