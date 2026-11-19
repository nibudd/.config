# Risk tier


The tier is set by **what the change touches**, not by how hard the task feels. It sets how much review the change gets.

**High** if any of these holds:

- a step touches an **owned path** (below)
- it changes a **public interface or contract** — endpoint shape, DB schema, exported signature with callers outside the change, a message or file format another system reads
- it is **hard to reverse** — migration, data backfill, new dependency
- it changes **error, retry, or idempotency behaviour**, or **secrets, IAM, or permissions**

**Low** only if every one of these holds:

- no High trigger
- it is mechanical, glue, test-only, tooling, or a behaviour-preserving refactor
- it changes no production behaviour a user or another system could observe

**Standard** is everything else.

Owned paths are the union of these defaults and the `owned_paths` list in the repo's `.claude/repo-profile.local.json`, if it exists. Match the globs against repo-relative paths.

- `**/terraform/**`, `**/*.tf`
- `**/migrations/**`
- `.github/workflows/**`, `**/Dockerfile*`, `**/docker-compose*.yml`
- `**/pyproject.toml`, `**/package.json`, `**/uv.lock`, `**/poetry.lock`, `**/package-lock.json`
- `**/*secret*`, `**/*auth*/**`, `**/*permission*`

The tier can go **up** mid-task without asking — say so in one line and apply the higher tier's review from that point. It never goes **down** unless the user says so. Change it with `bi.py set <key> tier <tier>`.

What each tier changes:

| | Low | Standard | High |
|---|---|---|---|
| `plan-critic` and plan gate | skipped | yes | yes |
| `diff-critic` | once, default effort | once, default effort | two critics on two different models other than yours, high effort |
| Review gate | folded into the wrap | its own stop | its own stop |
| Steps on owned paths | — | — | each one is a decision gate |

