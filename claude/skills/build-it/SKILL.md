---
name: build-it
description: Drive a task end-to-end through orient -> direct -> plan -> implement -> review per chunk, with review effort scaled to a risk tier and decision gates. For drive-mode work where I learn the code first, set the approach, and then review.
allowed-tools: Read Edit Write Bash Grep Glob Agent
disable-model-invocation: true
---

Drive the following task end to end. I (the user) stay current with the code by **learning it before you plan** and by **setting the approach myself**. You then execute, and I review where the risk is. The point of this loop is that I understand the change before it exists — not to maximize speed, and not to stop after every chunk.

Task / plan:

$ARGUMENTS

Run the stages **serially** — one step at a time, no parallel implementation agents. Serial is easier to review and debug.

Honor my global CLAUDE.md throughout (functional-core/imperative-shell, simple designs, few mocks, parametrized tests, targeted test runs, context7 for library docs, owned-vs-delegated, and the four decision-gate triggers).

### 1. Orient

Teach me the code this task touches before anyone proposes a solution. I learn the code when I make predictions and check them, not when I read a list of facts. Do not propose an approach, and do not rank options. That framing is mine to make in stage 2. Write each section below to the worklog (format in *Worklog*), so that it survives a context clear.

**1a. Get my guess.** State the change that the task requires in one sentence. Then ask me where I think the change lands and what it touches. STOP until I answer. Copy my answer verbatim into `## Guess`.

**1b. Write the tour to `## Map`.** Read the code first. Then write the tour in this order:

1. The *seam*: the one location where the change lands, with `file:line`.
2. A trace of one concrete example through the code. Use a real request or record with real field values. Give 4 to 7 numbered stops in execution order. For each stop, write:
   - `file:line`
   - what the code does to the example at this stop
   - why the code has this shape. Find the reason in `git log -L`, `git blame`, and the PR that added the code (`gh pr view`). If no source gives the reason, start the text with `inferred:`.
   - what can go wrong at this stop for this task
3. A comparison with `## Guess`, in one or two sentences: what my guess got right, and what it got wrong.

Do not put every fact in the trace. The trace holds only what the example passes through.

**1c. Write the inventory to `## Reference`.** Cite `file:line` for each item:

- **every consumer** of the data and contracts that the change touches. Search field names, column names, and dict keys, not only type names.
- the constraints already in place: invariants, conventions, tests that pin behaviour, and owned paths (see *Risk tier*)
- surprises: dead code, duplicated rules, a test that doesn't test what its name says

Add a Mermaid `flowchart` to `## Map` when the trace crosses three or more modules, or when a contract you touch has more than two consumers. Put the diagram above the stops. Label each node with its stop number and name. Draw each consumer from `## Reference` as a branch from the stop that writes the contract. Write one line that states the encoding before the diagram, and give the diagram a legend that lists every colour and line style. Do not draw a diagram when neither condition holds.

Open the worklog in my browser with a live preview, so that I can read the tour while I answer. Run this command once, in the background, after you write `## Map`:

```
nohup nvim --headless --listen "${TMPDIR}build-it-<key>.sock" ~/.claude-work/<key>/worklog.md -c "luafile ~/.claude/skills/build-it/preview.lua" >/dev/null 2>&1 &
```

The preview reloads each time you write the worklog, until stage 8 stops it. If the socket already exists, a preview for this task is running: do not start a second one. If the command fails, tell me in one line and continue without the preview.

**1d. Check my understanding.** Ask me 2 or 3 prediction questions. Each question asks what the code does in a case that the trace did not show. Examples: a null value at a stop, or a consumer that breaks when a field changes its name. Do not give the answers. STOP until I answer.

Check each answer against the code, and cite `file:line`. For each wrong or partial answer, add the missing fact to `## Map` at the stop where it belongs. Then ask one new question about that gap. If I ask questions of my own, answer them and add to `## Map` what the tour missed. Go to stage 2 only when I answer all the open questions correctly.

### 2. Direct

I write the approach first, in my own words. Wait for it — don't offer a draft, a list of options, or a hint about which way you'd go.

When I've written it:

1. Copy it verbatim into the worklog under `## Approach`.
2. Critique it as a skeptical co-developer: where it misses a consumer from `## Reference`, where it's over-built, where a materially simpler approach exists, and which decision-gate triggers it hits. Back each point with `file:line` evidence.
3. Reconcile with me. If I change the approach, replace `## Approach` with my new text, and record what we rejected under `## Decisions`.

The approach is where I enforce architecture. Don't reinterpret it during planning or implementation. If the code proves it wrong, stop and say so.

### 3. Plan

Break my approach into a dependency-ordered list of small steps. For each: the files it touches, whether it needs tests, a one-line difficulty note, and **whether it hits a decision gate**.

Then critique your own plan: where is this over-built? which steps could be merged or dropped without changing the outcome? Cut what doesn't survive and note what you cut. Scope creep and unnecessary complexity are the failure modes I care most about — don't wait for me to ask.

Assign the **risk tier** (next section) and give its reason in one line. Write the plan and the tier to the worklog.

**Standard and High only:** delegate the plan to the **`plan-critic`** agent, **on a model other than the one you're running** — pass an explicit override or it inherits yours and shares your blind spots. Give it the task statement, the ticket text if there is one, `## Approach`, and the plan verbatim. Then refute its findings: one **`refuter`** per finding, in a fresh context, in parallel, with the claim and nothing of the critic's reasoning. A finding is real unless its refuter killed it with a concrete cited reason.

**Gate (Standard and High):** present the tier and its reason on one line, the plan, what you cut and why, the surviving `plan-critic` findings, the refuted ones as one line each (claim + why it was killed, so I can overrule the filter), and the gate-flagged steps. Give each gate-flagged step the gate shape from my CLAUDE.md: the question in one sentence that ends in `?`, each option in one or two sentences, then your recommendation and its reason in one sentence. Name the model you delegated to. Then STOP and wait for my "ok"/tweaks before implementing.

**Low:** post the tier, its reason, and the plan, then continue without waiting. Stop only if a step is gate-flagged. I can overrule the tier at any point.

### Risk tier

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

The tier can go **up** mid-task without asking — say so in one line and apply the higher tier's review from that point. It never goes **down** without my say.

What each tier changes:

| | Low | Standard | High |
|---|---|---|---|
| `plan-critic` and plan gate | skipped | yes | yes |
| `diff-critic` | once, default effort | once, default effort | two critics on two different models other than yours, high effort |
| Review gate | folded into the wrap | its own stop | its own stop |
| Steps on owned paths | — | — | each one is a decision gate |

### 4. Implement, verify, and commit — per step

For each step in order:

1. Write or adjust tests first where it makes sense, then implement to pass them. One logical change, ~1–3 files. Don't merge steps.
2. Run the **targeted** tests for what you touched. My hooks format each file you edit, and lint and typecheck your changed lines when you stop. Fix what they report; don't run those tools again by hand. **Never hand me a red chunk** — if it fails, fix it before moving on. If a test itself looks wrong, stop and flag it; never weaken, skip, or delete a test to make code pass.
3. Commit it using my `commit` skill's message rules (≤60-char single-clause subject, default to no body, no ticket/PR reference, no attribution trailer) — but **not** its approval step: inside this loop, draft the message and commit without waiting. Show me the message in your one-line summary. **Do not push.**
4. Update the worklog: tick the step, and record any non-obvious choice under Decisions.
5. Post **one line** saying what landed, and continue to the next step without waiting.

**If a step hits a decision gate** — two or more defensible answers, my owned areas, a public interface or contract, or hard to reverse — stop instead. Number each open item and use the gate shape from my CLAUDE.md: the question in one sentence that ends in `?`, each option in one or two sentences, then your recommendation and its reason in one sentence. Ask what I'd do first, then show your answer and reconcile. Resume once I've called it.

If a step's code contradicts `## Approach`, stop and say how. Don't route around it.

If five steps pass with no gate, stop and summarize anyway.

Since I squash-merge, each of these commit subjects becomes a changelog line on `main`. Make each one independently meaningful — no `fix merge conflicts`, no `wip`.

### 5. Worklog

Keep one per task at `~/.claude-work/<key>/worklog.md` — see my CLAUDE.md for how the key is derived. It's keyed by task, not by repo, so a change spanning an API and its frontend keeps a single worklog and a single decision record. Create it in stage 1, update it as you go, and read it first when resuming a task already in progress — it's the answer to "where are we?" without re-reading the diff.

Since the worklog no longer sits inside a repo, `## Repos` is what says where the work actually landed. List every repo the task touches with its branch, and add a repo the first time you touch it.

```markdown
# <task> — <key>

## Repos
- <repo path> @ <branch>

## Guess
<my words, verbatim>

## Map
Seam: <where the change lands> — `file:line`
Example: <the request or record the trace follows>

1. <stop name> — `file:line` — <what the code does to the example> — why: <reason, or "inferred: …"> — risk: <what can go wrong for this task>

Guess vs. trace: <what my guess got right and wrong>

## Reference
- Consumer: <who reads the data or contract> — `file:line`
- Constraint: <invariant, convention, pinning test, or owned path> — `file:line`
- Surprise: <dead code, duplicated rule, misleading test> — `file:line`

## Approach
<my words, verbatim>

## Tier
<Low | Standard | High> — <reason>

## Steps
- [x] 1. <step> — <commit sha>
- [ ] 2. <step>

## Decisions
- <what was chosen> — rejected: <alternative> (<why>)

## Open
- <question, blocked item, or thing I owe you an answer on>

## Misses
- <defect class review missed> — `file:line` — <which stage should have caught it>

## PR draft
<title>

# What
- <effect of the change>

# Why
<what was broken or missing, or what this unblocks>
```

Record a line under `## Misses` whenever a defect gets past a review stage: I overrule a refuted finding, I find a defect the critics didn't raise, or a later stage or the hooks catch one an earlier stage passed. Name it as a class, not as a single line. `/workflow-review` reads these to improve the critics.

Decisions is the part that matters for review. One line per non-obvious choice, **including the ones you didn't stop for** — that's what I read instead of sitting through gates, and it's still readable weeks later when the conversation is gone.

### 6. Review — adversarial, cross-model, independently refuted

Attack the diff, don't bless it. A clean review is a conclusion you reach by looking hard, not a starting assumption.

1. Delegate the full branch diff to the **`diff-critic`** agent, telling it to judge the work against `## Approach` and the plan. Run it **on a model other than the one you're running** — pass an explicit model override, because without one it inherits yours and the review shares your blind spots. Pick a peer-tier model (Opus / Fable / Sonnet), not Haiku. At High, run two critics on two different models other than yours, both at high effort, and merge their findings before refuting. Say in your summary which model you ran and which you delegated to.
2. For **each** finding, spawn a **`refuter`** in a fresh context — one per finding, in parallel. Refuters must not see the critic's reasoning; give them the claim and the code, nothing more.
3. A finding is real unless its refuter killed it **with a concrete cited reason** — a guard, contract, test, or misread at a named `file:line`. "Probably fine" is not a refutation.

**Gate (Standard and High):** present the surviving findings, numbered. For each one, say what is wrong in one or two sentences, then the fix you propose in one sentence. Then present the refuted ones as one line each (claim + why it was killed, so I can see what got filtered and overrule it), the branch diff, and the Decisions section. Then STOP. Wait for my call on which findings to fix.

**Low:** carry the findings into the wrap in the same shape, and don't stop here.

### 7. Fix and re-review the fixes

Apply the findings I approved, then re-run the relevant tests. Commit the fixes as their own step (same rules as stage 4).

Then review **only the fix commits**: one `diff-critic` run on that range, on the same model as stage 6, with the approved findings as the plan to judge against. Refute its findings as in stage 6. This round runs **once**. If a finding survives it, don't fix it in a loop — bring it to me as a question about the approach, because two rounds that miss the same area usually mean the approach is wrong there.

### 8. Wrap

Grep the branch diff for `TODO: Update Prose` first and list every hit with its `file:line` and the drafted text. Add whatever you flagged as stale or AI-written along the way to the same list. I rewrite them all before a PR goes up.

Then run the full suite once. Report failures with the actual output — don't paper over them. Summarize what landed — at Low, followed by the review findings from stage 6 in the gate shape, and wait for my call on them. Leave anything unresolved under Open in the worklog. Open holds only what needs a decision or is blocked. An option we rejected goes under Decisions, never under Open or in the summary.

Then draft the material that I write the PR description from. Use the rules in Step 3 and Step 4 of my `make-pr` skill (`~/.claude/skills/make-pr/SKILL.md`). The draft has a title, `# What` with 3 to 5 bullets, and `# Why` in one or two sentences. Add `# Notes` only when it passes the test in that skill. Omit the stacked line. Each bullet states one effect of the change. A bullet does not name a commit or a test, and it names a file only when that file is the effect. Take the Why from `## Decisions`. Write the draft to the worklog under `## PR draft`, and show it in the summary. Then stop. **Do not push, and do not open a PR** — I review before anything goes upstream.

Stop the worklog preview from stage 1, if it runs: `nvim --server "${TMPDIR}build-it-<key>.sock" --remote-send '<C-\><C-n>:qa!<CR>'`.

Throughout: prefer stopping at a gate over guessing. If you're unsure whether something is my call, it's my call.
