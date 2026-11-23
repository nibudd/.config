import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).with_name("pr-prose-gate.py")
_spec = importlib.util.spec_from_file_location("pr_prose_gate", HOOK)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo_with_marker(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "test")
    (tmp_path / "base.txt").write_text("base\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "app.py").write_text('raise ValueError("TODO: Update Prose bad input")\n')
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "add marker")
    return tmp_path


def run_hook(cwd, command):
    event = {"cwd": str(cwd), "tool_input": {"command": command}}
    return subprocess.run(
        [sys.executable, str(HOOK)], input=json.dumps(event), capture_output=True, text=True
    ).returncode


@pytest.mark.parametrize(
    "command",
    [
        'for d in */migrations; do echo "${d%/migrations}"; done',
        "cat >> notes.md <<'EOF'\nthe model's partition\nEOF",
        "git commit -m 'update the gh pr template'",
    ],
)
def test_non_pr_commands_pass(repo_with_marker, command):
    assert run_hook(repo_with_marker, command) == 0


@pytest.mark.parametrize(
    "command",
    [
        "gh pr create --draft --title t --body-file body.md",
        "gh pr ready 12",
        "cd . && gh pr create --draft",
    ],
)
def test_pr_commands_block_on_marker(repo_with_marker, command):
    assert run_hook(repo_with_marker, command) == 2


def run_check(repo):
    return subprocess.run([sys.executable, str(HOOK), "--check", str(repo)], capture_output=True, text=True)


def test_check_reports_file_and_line(repo_with_marker):
    (repo_with_marker / "app.py").write_text('x = 1\ny = 2\nraise ValueError("TODO: Update Prose bad input")\n')
    git(repo_with_marker, "commit", "-q", "-am", "move marker")
    result = run_check(repo_with_marker)
    assert result.returncode == 1
    assert result.stdout.strip() == 'app.py:3: prose marker: raise ValueError("TODO: Update Prose bad input")'


def test_check_passes_clean_branch(repo_with_marker):
    (repo_with_marker / "app.py").write_text("x = 1\n")
    git(repo_with_marker, "commit", "-q", "-am", "drop marker")
    result = run_check(repo_with_marker)
    assert (result.returncode, result.stdout.strip()) == (0, "ok")


@pytest.mark.parametrize(
    ("prefix", "number", "flagged"),
    [
        ("PROG", "1225", True),
        ("CO", "42", True),
        ("CW", "10", True),
        ("NF", "01", True),
        ("PROG", "12345", True),
        ("SHA", "256", False),
        ("UTF", "16", False),
        ("ISO", "8601", False),
        ("cw", "12", False),
        ("XPROG", "12", False),
    ],
)
def test_violations_flag_ticket_keys(prefix, number, flagged):
    found = list(gate.violations([("app.py", 1, f"# see {prefix}-{number}")]))
    assert bool(found) == flagged


def test_violations_skip_markdown():
    assert list(gate.violations([("notes.md", 1, "see " + "PROG" + "-1225")])) == []
