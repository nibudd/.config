#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

import workflow
from workflow import Brief, Decisions, Plan, Review, State, TaskFile, TransitionError

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
HOOKS = HERE.parents[2] / "hooks"


def work_root() -> Path:
    return Path(os.environ.get("BI_WORK_ROOT", Path.home() / ".claude-work"))


def task_dir(key: str) -> Path:
    return work_root() / key


def read_yaml(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return yaml.safe_load(path.read_text()) or default
    except yaml.YAMLError as error:
        raise SystemExit(f"{path} is not valid YAML. Rewrite the whole file as valid YAML.\n{error}") from None


def write_yaml(path: Path, data: Any) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def load(directory: Path, state: dict[str, Any] | None = None) -> list[TaskFile]:
    brief = directory / "brief.md"
    if state is None:
        state = read_yaml(directory / "state.yaml", {"state": "requirements"})
    return [
        Brief(brief.read_text() if brief.exists() else ""),
        Decisions(read_yaml(directory / "decisions.yaml", [])),
        Plan(read_yaml(directory / "plan.yaml", {})),
        Review(read_yaml(directory / "review.yaml", {})),
        State(state),
    ]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def cmd_init(args: argparse.Namespace) -> int:
    repo = Path(git(Path(args.repo), "rev-parse", "--show-toplevel"))
    branch = git(repo, "branch", "--show-current")
    if not args.ticket and not branch:
        print("HEAD is detached, so no branch names the task. Check out a branch or pass --ticket.", file=sys.stderr)
        return 1
    key = workflow.derive_key(args.ticket, repo.name, branch)
    directory = task_dir(key)
    if (directory / "worklog.md").exists():
        print(f"{directory} holds an old task with a worklog.md. Use /build-it-v1 for it.", file=sys.stderr)
        return 1
    if read_yaml(directory / "state.yaml", {}).get("state"):
        print(f"{directory} already holds a task; resume it instead", file=sys.stderr)
        return 1
    directory.mkdir(parents=True, exist_ok=True)
    for template in TEMPLATES.iterdir():
        target = directory / template.name
        if not target.exists():
            shutil.copyfile(template, target)
    existing = {k: v for k, v in read_yaml(directory / "state.yaml", {}).items() if v is not None}
    state = {**read_yaml(TEMPLATES / "state.yaml", {}), **existing}
    here = {"path": str(repo), "branch": branch}
    state.update(key=key, kind=args.kind, repos=[*[r for r in state.get("repos", []) if r != here], here])
    write_yaml(directory / "state.yaml", state)
    print(json.dumps({"key": key, "dir": str(directory)}))
    return 0


def cmd_next_id(args: argparse.Namespace) -> int:
    ids = set().union(*(f.defined_ids() for f in load(task_dir(args.key))))
    print(workflow.next_id(ids, args.prefix))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    problems = workflow.validate(load(task_dir(args.key)))
    print("\n".join(problems) or "ok")
    return 1 if problems else 0


def cmd_transition(args: argparse.Namespace) -> int:
    directory = task_dir(args.key)
    state = read_yaml(directory / "state.yaml", {})
    if not state.get("state"):
        print(f"{directory}/state.yaml has no state. Run `bi.py init` first.", file=sys.stderr)
        return 1
    files = load(directory, state)
    try:
        guard = workflow.resolve_guard(state, args.guard, files)
    except TransitionError as error:
        print(error, file=sys.stderr)
        return 1
    problems = workflow.validate(files) + workflow.exit_problems(files, state, guard)
    if problems:
        print("Fix these before the transition:\n" + "\n".join(problems), file=sys.stderr)
        return 1
    try:
        result = workflow.transition(state, guard)
    except TransitionError as error:
        print(error, file=sys.stderr)
        return 1
    new = {**result.state, "step": workflow.first_todo_step(files) if result.state["state"] == "implement" else None}
    write_yaml(directory / "state.yaml", new)
    print(json.dumps({"guard": guard, "state": new["state"], "return_to": workflow.return_to(new), "step": new["step"], "summarize": result.summarize}))
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    path = task_dir(args.key) / "state.yaml"
    value = None if args.value in ("null", "none", "") else args.value
    try:
        state = workflow.set_field(read_yaml(path, {}), args.field, value)
    except TransitionError as error:
        print(error, file=sys.stderr)
        return 1
    problems = workflow.validate(load(task_dir(args.key), state))
    if problems:
        print("Not set:\n" + "\n".join(problems), file=sys.stderr)
        return 1
    write_yaml(path, state)
    print("ok")
    return 0


def cmd_baseline(args: argparse.Namespace) -> int:
    path = task_dir(args.key) / "plan.yaml"
    plan = read_yaml(path, {})
    results = {}
    for step in plan.get("steps") or []:
        check = step.get("check", {})
        if check.get("kind") == "command":
            cwd = Path(os.path.expanduser(check.get("cwd", ".")))
            run = subprocess.run(check["run"], shell=True, cwd=cwd, capture_output=True, text=True)
            results[step["n"]] = run.returncode == 0
            print(f"step {step['n']}: {'pass' if run.returncode == 0 else 'fail'}: {check['run']}")
    write_yaml(path, workflow.record_baseline(plan, results))
    return 0


def cmd_tier_floor(args: argparse.Namespace) -> int:
    sys.path.insert(0, str(HOOKS))
    from code_checks import glob_match

    directory = task_dir(args.key)
    state = read_yaml(directory / "state.yaml", {})
    owned = list(workflow.DEFAULT_OWNED_PATHS)
    for repo in state.get("repos", []):
        profile = Path(repo["path"]) / ".claude" / "repo-profile.local.json"
        if profile.exists():
            owned += json.loads(profile.read_text()).get("owned_paths", [])
    paths = [f for s in read_yaml(directory / "plan.yaml", {}).get("steps") or [] for f in s.get("files", [])]
    print(workflow.tier_floor(paths, owned, glob_match))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="bi.py")
    sub = parser.add_subparsers(required=True)
    init = sub.add_parser("init")
    init.add_argument("--repo", default=".")
    init.add_argument("--ticket")
    init.add_argument("--kind", choices=workflow.KINDS)
    init.set_defaults(func=cmd_init)
    for name, func in (("validate", cmd_validate), ("baseline", cmd_baseline), ("tier-floor", cmd_tier_floor)):
        p = sub.add_parser(name)
        p.add_argument("key")
        p.set_defaults(func=func)
    nxt = sub.add_parser("next-id")
    nxt.add_argument("key")
    nxt.add_argument("prefix", choices=["A", "Q", "D", "F"])
    nxt.set_defaults(func=cmd_next_id)
    setter = sub.add_parser("set")
    setter.add_argument("key")
    setter.add_argument("field", choices=sorted(workflow.SETTABLE))
    setter.add_argument("value")
    setter.set_defaults(func=cmd_set)
    trans = sub.add_parser("transition")
    trans.add_argument("key")
    trans.add_argument("guard")
    trans.set_defaults(func=cmd_transition)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
