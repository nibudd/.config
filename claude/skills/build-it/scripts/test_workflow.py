import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import workflow
from workflow import Brief, Decisions, Plan, Review, State, TransitionError

BI = Path(__file__).resolve().parent / "bi.py"

BRIEF = """# Task

## Acceptance
- A01: export runs nightly
- A02: export skips archived rows

## Open questions
- Q01 [open]: should deleted rows export?
- Q02 [resolved]: which bucket?
- Q03 [accepted]: nightly means 02:00 UTC
"""


def step(n: int = 1, **overrides):
    return {"n": n, "acceptance": ["A01"], "decisions": [], "check": {"kind": "command", "run": "true"}, **overrides}


@pytest.mark.parametrize(
    ("ticket", "repo", "branch", "expected"),
    [
        ("PROG-1013", "platform", "PROG-1013/port-metrics", "PROG-1013"),
        (None, "platform", "PROG-1013/port-metrics", "platform_PROG-1013_port-metrics"),
        (None, ".config", "main", "config_main"),
        (None, "api", "a/b/c", "api_a_b_c"),
    ],
)
def test_derive_key(ticket, repo, branch, expected):
    assert workflow.derive_key(ticket, repo, branch) == expected


@pytest.mark.parametrize(
    ("existing", "prefix", "expected"),
    [
        ([], "A", "A01"),
        (["A01", "A02", "D07"], "A", "A03"),
        (["A01", "A03"], "A", "A04"),
        (["A01", "D07"], "D", "D08"),
        (["A09"], "A", "A10"),
        (["A99"], "A", "A100"),
        (["Q01"], "F", "F01"),
    ],
)
def test_next_id(existing, prefix, expected):
    assert workflow.next_id(existing, prefix) == expected


@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        (["src/app.py"], "low"),
        (["src/app.py", "infra/terraform/main.tf"], "high"),
        (["db/migrations/0001.py"], "high"),
        ([], "low"),
    ],
)
def test_tier_floor(paths, expected):
    sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
    from code_checks import glob_match

    assert workflow.tier_floor(paths, workflow.DEFAULT_OWNED_PATHS, glob_match) == expected


@pytest.mark.parametrize(("source", "guard"), list(workflow.TRANSITIONS))
def test_every_transition_lands_in_a_known_state(source, guard):
    state = {"state": source, "return_stack": ["design"], "tier": "low", "steps_since_gate": 0}
    result = workflow.transition(state, guard)
    assert result.state["state"] in workflow.STATES
    assert result.state["log"][-1] == {"from": source, "guard": guard, "to": result.state["state"]}


@pytest.mark.parametrize(
    ("source", "guard", "stack", "expected_state", "expected_stack"),
    [
        ("design", "new_criterion", [], "requirements", ["design"]),
        ("requirements", "return", ["design"], "design", []),
        ("design", "gap", [], "orient", ["design"]),
        ("orient", "return", ["design"], "design", []),
        ("implement", "gate", [], "design", ["implement"]),
        ("design", "return", ["implement"], "implement", []),
        ("design", "new_criterion", ["implement"], "requirements", ["implement", "design"]),
        ("requirements", "return", ["implement", "design"], "design", ["implement"]),
        ("design", "gap", ["implement"], "orient", ["implement", "design"]),
        ("design", "approach_changed", ["implement"], "direct", []),
        ("direct", "new_decision", [], "design", []),
        ("requirements", "ready", [], "orient", []),
    ],
)
def test_return_stack(source, guard, stack, expected_state, expected_stack):
    result = workflow.transition({"state": source, "return_stack": stack}, guard)
    assert (result.state["state"], result.state["return_stack"]) == (expected_state, expected_stack)


def test_nested_return_comes_back_to_implement():
    path = [("implement", "gate"), ("design", "new_criterion"), ("requirements", "return"), ("design", "return")]
    state = {"state": "implement", "return_stack": []}
    for source, guard in path:
        assert state["state"] == source
        state = workflow.transition(state, guard).state
    assert (state["state"], state["return_stack"]) == ("implement", [])


@pytest.mark.parametrize(("stack", "expected"), [([], None), (["implement"], "implement"), (["implement", "design"], "design")])
def test_return_to_is_the_top_of_the_stack(stack, expected):
    assert workflow.return_to({"return_stack": stack}) == expected


@pytest.mark.parametrize(
    ("state", "guard", "message"),
    [
        ({"state": "orient"}, "approved", "no guard 'approved' from 'orient'"),
        ({"state": "requirements", "return_stack": []}, "return", "needs a non-empty return_stack"),
        ({"state": "review", "tier": "standard"}, "carried", "only at the low tier"),
        ({"state": "done"}, "next_step", "no guard"),
    ],
)
def test_transition_rejects(state, guard, message):
    with pytest.raises(TransitionError, match=message):
        workflow.transition(state, guard)


@pytest.mark.parametrize(
    ("count", "guard", "expected_count", "summarize"),
    [
        (0, "next_step", 1, False),
        (4, "next_step", 5, True),
        (5, "summarized", 0, False),
        (3, "gate", 0, False),
        (3, "done", 3, False),
    ],
)
def test_steps_since_gate(count, guard, expected_count, summarize):
    result = workflow.transition({"state": "implement", "steps_since_gate": count}, guard)
    assert (result.state["steps_since_gate"], result.summarize) == (expected_count, summarize)


def test_record_baseline():
    plan = {
        "steps": [
            step(1),
            step(2, check={"kind": "command", "run": "false"}),
            step(3, check={"kind": "new_test", "name": "t"}),
            step(4, check={"kind": "planned", "run": "make smoke"}),
            step(5, check={"kind": "none", "reason": "docs only"}),
        ]
    }
    result = workflow.record_baseline(plan, {1: True, 2: False})
    assert [s["baseline"] for s in result["steps"]] == ["pass", "fail", "new", "planned", None]


def test_brief_ids():
    brief = Brief(BRIEF)
    assert brief.defined_ids() == {"A01", "A02", "Q01", "Q02", "Q03"}
    assert brief.questions() == {"Q01": "open", "Q02": "resolved", "Q03": "accepted"}


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        ([Brief(BRIEF)], []),
        ([Brief("- Q03 [maybe]: x")], ["brief.md: Q03 has status 'maybe'"]),
        ([Brief("- A1: too short")], ["brief.md: malformed ID line: - A1: too short"]),
        ([Brief("- Q04: no status")], ["brief.md: malformed ID line: - Q04: no status"]),
    ],
)
def test_brief_problems(files, expected):
    assert workflow.validate(files) == expected


@pytest.mark.parametrize("status", workflow.DECISION_STATUSES)
def test_every_decision_status_may_serve_a_criterion(status):
    files = [Brief(BRIEF), Decisions([{"id": "D01", "status": status, "serves": ["A01"]}])]
    assert workflow.validate(files) == []


@pytest.mark.parametrize(
    ("decisions", "expected"),
    [
        ([{"id": "D01", "status": "proposed", "serves": ["Q01"]}], []),
        ([{"id": "D01", "status": "delegated", "serves": ["Q01"]}], []),
        ([{"id": "D01", "status": "agreed", "serves": ["Q01"]}], ["decisions.yaml: D01 is agreed but serves open question Q01"]),
        ([{"id": "D01", "status": "agreed", "serves": ["Q02"]}], []),
        ([{"id": "D01", "status": "agreed", "serves": ["Q03"]}], []),
        ([{"id": "D01", "status": "agreed", "serves": ["A09"]}], ["decisions.yaml: D01 serves unknown A09"]),
        ([{"id": "D01", "status": "owner", "serves": []}], ["decisions.yaml: D01 has status 'owner'"]),
        ([{"id": "D01", "status": "agreed"}, {"id": "D01", "status": "agreed"}], ["decisions.yaml: duplicate D01"]),
        ([{"id": "D01", "status": "agreed", "serves": []}], []),
    ],
)
def test_decision_problems(decisions, expected):
    assert workflow.validate([Brief(BRIEF), Decisions(decisions)]) == expected


@pytest.mark.parametrize(
    ("steps", "expected"),
    [
        ([step()], []),
        ([step(acceptance=[], acceptance_none="pure rename")], []),
        ([step(acceptance=[])], ["plan.yaml: step 1 cites no acceptance ID and gives no acceptance_none reason"]),
        ([step(acceptance=["A09"])], ["plan.yaml: step 1 cites unknown A09"]),
        ([step(acceptance=["Q01"])], ["plan.yaml: step 1 cites open question Q01"]),
        ([step(acceptance=["Q02"])], []),
        ([step(decisions=["D01"])], ["plan.yaml: step 1 cites unknown D01"]),
        ([step(check={"kind": "maybe"})], ["plan.yaml: step 1 has check kind 'maybe'"]),
        ([step(check={"kind": "command"})], ["plan.yaml: step 1 has a command check with no run command"]),
        ([step(check={"kind": "planned"})], ["plan.yaml: step 1 has a planned check with no run command"]),
        ([step(check={"kind": "none"})], ["plan.yaml: step 1 has check kind 'none' with no reason"]),
        ([step(check={"kind": "new_test", "name": "t"})], []),
        ([step(baseline="green")], ["plan.yaml: step 1 has baseline 'green'"]),
        ([step(1), step(1)], ["plan.yaml step: duplicate 1"]),
    ],
)
def test_plan_problems(steps, expected):
    assert workflow.validate([Brief(BRIEF), Plan({"steps": steps})]) == expected


def test_review_duplicate_findings():
    review = Review({"rounds": [{"findings": [{"id": "F01"}]}, {"findings": [{"id": "F01"}]}]})
    assert workflow.validate([review]) == ["review.yaml: duplicate F01"]


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ({"state": "plan", "kind": "bug", "tier": "high"}, []),
        ({"state": "intake"}, ["state.yaml: state is 'intake'"]),
        ({"state": None, "prs": [{"number": 12}]}, []),
        ({"state": "plan", "return_stack": ["implement", "nowhere"]}, ["state.yaml: return_stack holds 'nowhere'"]),
        ({"state": "plan", "kind": "chore"}, ["state.yaml: kind is 'chore'"]),
        ({"state": "plan", "tier": "medium"}, ["state.yaml: tier is 'medium'"]),
        ({"state": "design", "waiting_on": "Q01"}, []),
        ({"state": "design", "waiting_on": "Q02"}, ["state.yaml: waiting_on Q02 is not an open question"]),
        ({"state": "design", "waiting_on": "Q09"}, ["state.yaml: waiting_on Q09 is not an open question"]),
    ],
)
def test_state_problems(state, expected):
    assert workflow.validate([Brief(BRIEF), State(state)]) == expected


def test_deleting_a_cited_criterion_fails():
    brief_without_a02 = BRIEF.replace("- A02: export skips archived rows\n", "")
    files = [Brief(brief_without_a02), Plan({"steps": [step(acceptance=["A02"])]})]
    assert workflow.validate(files) == ["plan.yaml: step 1 cites unknown A02"]


@pytest.fixture
def repo(tmp_path):
    path = tmp_path / "platform"
    path.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "PROG-1013/port-metrics", str(path)], check=True)
    return path


def bi(work_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "BI_WORK_ROOT": str(work_root)}
    return subprocess.run([sys.executable, str(BI), *args], capture_output=True, text=True, env=env)


def test_cli_round_trip(tmp_path, repo):
    work = tmp_path / "work"
    init = bi(work, "init", "--repo", str(repo), "--kind", "feature")
    assert init.returncode == 0, init.stderr
    key = json.loads(init.stdout)["key"]
    assert key == "platform_PROG-1013_port-metrics"
    task = work / key
    assert sorted(p.name for p in task.iterdir()) == sorted(p.name for p in (BI.parent.parent / "templates").iterdir())
    assert bi(work, "validate", key).stdout.strip() == "ok"
    assert bi(work, "next-id", key, "A").stdout.strip() == "A01"
    (task / "brief.md").write_text(BRIEF)
    assert bi(work, "next-id", key, "A").stdout.strip() == "A03"

    open_question = bi(work, "transition", key, "ready")
    assert open_question.returncode == 1 and "Q01 is still open" in open_question.stderr
    (task / "brief.md").write_text(BRIEF.replace("Q01 [open]", "Q01 [resolved]"))
    moved = bi(work, "transition", key, "ready")
    assert json.loads(moved.stdout) == {"state": "orient", "return_to": None, "summarize": False}
    (task / "brief.md").write_text(BRIEF)
    state = yaml.safe_load((task / "state.yaml").read_text())
    assert state["repos"] == [{"path": str(repo.resolve()), "branch": "PROG-1013/port-metrics"}]

    (task / "decisions.yaml").write_text(yaml.safe_dump([{"id": "D01", "status": "agreed", "serves": ["Q01"]}]))
    blocked = bi(work, "transition", key, "understood")
    assert blocked.returncode == 1
    assert "D01 is agreed but serves open question Q01" in blocked.stderr

    assert bi(work, "init", "--repo", str(repo)).returncode == 1


def test_cli_baseline(tmp_path, repo):
    work = tmp_path / "work"
    key = json.loads(bi(work, "init", "--repo", str(repo)).stdout)["key"]
    plan = {"steps": [step(1, check={"kind": "command", "run": "true", "cwd": str(repo)}), step(2, check={"kind": "command", "run": "false", "cwd": str(repo)})]}
    (work / key / "plan.yaml").write_text(yaml.safe_dump(plan))
    bi(work, "baseline", key)
    steps = yaml.safe_load((work / key / "plan.yaml").read_text())["steps"]
    assert [s["baseline"] for s in steps] == ["pass", "fail"]


@pytest.mark.parametrize(
    ("name", "value", "error"),
    [
        *[("kind", kind, None) for kind in workflow.KINDS],
        *[("tier", tier, None) for tier in workflow.TIERS],
        ("waiting_on", "Q01", None),
        ("waiting_on", None, None),
        ("kind", "chore", "kind must be one of"),
        ("tier", "medium", "tier must be one of"),
        ("state", "wrap", "cannot set 'state'"),
    ],
)
def test_set_field(name, value, error):
    if error:
        with pytest.raises(TransitionError, match=error):
            workflow.set_field({"state": "plan"}, name, value)
    else:
        assert workflow.set_field({"state": "plan"}, name, value)[name] == value


def test_cli_set(tmp_path, repo):
    work = tmp_path / "work"
    key = json.loads(bi(work, "init", "--repo", str(repo)).stdout)["key"]
    (work / key / "brief.md").write_text(BRIEF)
    assert bi(work, "set", key, "tier", "high").returncode == 0
    assert bi(work, "set", key, "waiting_on", "Q02").returncode == 1
    assert yaml.safe_load((work / key / "state.yaml").read_text())["waiting_on"] is None
    assert bi(work, "set", key, "waiting_on", "Q01").returncode == 0
    state = yaml.safe_load((work / key / "state.yaml").read_text())
    assert (state["tier"], state["waiting_on"]) == ("high", "Q01")


def test_cli_init_adopts_a_state_file_without_a_state(tmp_path, repo):
    work = tmp_path / "work"
    task = work / "platform_PROG-1013_port-metrics"
    task.mkdir(parents=True)
    (task / "state.yaml").write_text(yaml.safe_dump({"state": None, "prs": [{"number": 7}]}))
    assert bi(work, "init", "--repo", str(repo)).returncode == 0
    state = yaml.safe_load((task / "state.yaml").read_text())
    assert (state["state"], state["prs"]) == ("requirements", [{"number": 7}])


@pytest.mark.parametrize(
    ("state", "guard", "files", "expected"),
    [
        ({"state": "requirements"}, "ready", [Brief(BRIEF)], ["brief.md: Q01 is still open"]),
        ({"state": "requirements"}, "ready", [Brief(BRIEF.replace("Q01 [open]", "Q01 [resolved]"))], []),
        ({"state": "requirements", "return_stack": ["design"]}, "return", [Brief(BRIEF)], []),
        ({"state": "design"}, "decided", [Decisions([{"id": "D01", "status": "proposed"}])], ["decisions.yaml: D01 is still proposed"]),
        ({"state": "design", "return_stack": ["implement"]}, "return", [Decisions([{"id": "D01", "status": "proposed"}])], ["decisions.yaml: D01 is still proposed"]),
        ({"state": "design"}, "decided", [Decisions([{"id": "D01", "status": "agreed"}, {"id": "D02", "status": "delegated"}])], []),
        ({"state": "design"}, "gap", [Decisions([{"id": "D01", "status": "proposed"}])], []),
        ({"state": "design", "return_stack": ["implement"]}, "decided", [State({})], ["state.yaml: return_stack is not empty; use 'return' to go back to implement"]),
        ({"state": "plan"}, "approved", [Brief(BRIEF), Decisions([{"id": "D01", "status": "proposed"}])], []),
    ],
)
def test_exit_problems(state, guard, files, expected):
    assert workflow.exit_problems(files, state, guard) == expected


AGENTS = Path.home() / ".claude" / "agents"
GUARD_BULLET = re.compile(r"^\s*- `(\w+)`")


def agent_guards() -> set[str]:
    guards = set()
    for path in AGENTS.glob("bi-*.md"):
        in_guards = False
        for line in path.read_text().splitlines():
            if re.match(r"^\s*-?\s*Guards?:", line):
                in_guards = True
                guards.update(re.findall(r"`(\w+)`", line.split(":", 1)[1]))
                continue
            if in_guards and (m := GUARD_BULLET.match(line)):
                guards.add(m.group(1))
            elif in_guards and line.strip() and not line.startswith(" "):
                in_guards = False
    return guards


def test_agent_guards_match_the_transition_table():
    table = {g for _, g in workflow.TRANSITIONS}
    dispatcher_only = {"summarized"}
    assert agent_guards() == table - dispatcher_only


@pytest.mark.parametrize("name", ["decisions.yaml", "plan.yaml", "review.yaml", "state.yaml"])
def test_templates_parse(name):
    yaml.safe_load((BI.parent.parent / "templates" / name).read_text())


def test_cli_rejects_old_task_and_detached_head(tmp_path, repo):
    work = tmp_path / "work"
    old = work / "platform_PROG-1013_port-metrics"
    old.mkdir(parents=True)
    (old / "worklog.md").write_text("# old")
    refused = bi(work, "init", "--repo", str(repo))
    assert refused.returncode == 1 and "build-it-v1" in refused.stderr

    (repo / "f").write_text("x")
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@e", "commit", "-qm", "c", "--allow-empty"], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--detach"], check=True)
    detached = bi(work, "init", "--repo", str(repo))
    assert detached.returncode == 1 and "detached" in detached.stderr


def test_cli_transition_without_a_task(tmp_path):
    result = bi(tmp_path, "transition", "nothing-here", "ready")
    assert result.returncode == 1 and "bi.py init" in result.stderr


def test_cli_reports_invalid_yaml(tmp_path, repo):
    work = tmp_path / "work"
    key = json.loads(bi(work, "init", "--repo", str(repo)).stdout)["key"]
    (work / key / "decisions.yaml").write_text("[]\n- id: D01\n")
    result = bi(work, "validate", key)
    assert result.returncode == 1 and "decisions.yaml is not valid YAML" in result.stderr
