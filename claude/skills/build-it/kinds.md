# Task kind


The kind changes what each state must find and prove. `## Map` and `## Reference` are sections of `orient.md`.

**Feature** — new or changed behaviour in existing code.

- Orient: find the analogous implementations and the conventions the code already uses. Put them in `## Reference`.
- A mechanism is not a requirement. A status column, a timestamp, or a new table is a choice for `approach.md` or `decisions.yaml`, not a fact of the task.

**Bug** — the code does not do what it should.

- Orient: write the expected behaviour, the actual behaviour, and the conditions that reproduce it, before the trace. Ask the user for the expected behaviour only if the code, the tests, and the ticket cannot show it.
- Do not change a live system to get evidence. Logs from a different request or release are not evidence for this one.
- If the cause is not proven, the first plan step is an investigation: the question, 2 or 3 hypotheses, the experiment that tells them apart, and the stop condition. The fix steps come after it. The investigation ends when each hypothesis has a result. A fix is not its end condition.
- The fix needs a regression test that fails before the fix and passes after it. If no automated test is possible, write the manual procedure and the result you expect to see.

**Recovery** — the branch or working tree already holds unfinished work.

- Before any edit, record the starting state in `## Reference`: branch and base, tracked diff, untracked files, and the checks that pass and fail now.
- Do not stash, reset, discard, or rewrite work to get a clean baseline. Keep edits that are not part of the task.
- Orient: classify each part of the existing work as working, incomplete, incorrect, or uncertain, with evidence. A style you do not know is not evidence that the code is incorrect.
- Do not blame the unfinished work for a check that already failed at its base. Check the base first.
- Plan: say for each part whether we keep, fix, replace, or finish it. Add checks for the behaviour we keep, not only for new behaviour. A new green test does not cancel a failure in behaviour we keep.

**Foundation** — a new project, or a new service inside a repo, with no code to trace yet.

- Orient: there is no trace. In `## Map`, write the constraints instead: the runtime, where it deploys, who operates it, and the existing systems it must read from or write to. For each constraint, write the choice it forces or rules out. In `## Reference`, list the existing assets to reuse: templates, sibling services, shared libraries. The prediction questions ask what a constraint forces, not what the code does.
- A whole product is not one task. Cut the task to the smallest capability that runs end to end, from its entry point to its output. Put the other capabilities under "Out of scope" in `brief.md`.
- Investigate only the tool choices that are expensive to change: language, framework, datastore, deployment target. Each one is a decision gate. For each one, say what it costs to deploy, to maintain, and to migrate away from.
- Checks: a step may name a check that it creates, as `check: planned: <command>`. The step must create the check and run it before the step ends. No later step can depend on that check until then.
- A skeleton that runs is not a finished product. The wrap says which capabilities are still out of scope.

