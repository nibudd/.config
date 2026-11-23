import io
import json
import subprocess
from pathlib import Path

import pytest

import code_checks
from code_checks import Check, added_ranges, glob_match


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        ("**/*.py", "a.py", True),
        ("**/*.py", "src/pkg/a.py", True),
        ("**/*.py", "a.pyc", False),
        ("src/*.py", "src/pkg/a.py", False),
        ("app/**/*.py", "app/manage.py", True),
        ("app/**/*.py", "other/manage.py", False),
        ("src/**/*.{ts,vue}", "src/components/A.vue", True),
        ("src/**/*.{ts,vue}", "src/main.ts", True),
        ("src/**/*.{ts,vue}", "src/main.js", False),
        ("**/terraform/**", "infra/terraform/main.tf", True),
        ("**/*auth*/**", "app/sso_auth/views.py", True),
        ("file?.txt", "file1.txt", True),
        ("file?.txt", "file/.txt", False),
    ],
)
def test_glob_match(pattern, path, expected):
    assert glob_match(pattern, path) is expected


def test_added_ranges_collects_new_side_hunks_and_skips_deletions():
    diff = "\n".join(
        [
            "diff --git a/a.py b/a.py",
            "--- a/a.py",
            "+++ b/a.py",
            "@@ -3,0 +4,2 @@",
            "@@ -10 +12 @@",
            "@@ -20,3 +23,0 @@",
            "diff --git a/gone.py b/gone.py",
            "--- a/gone.py",
            "+++ /dev/null",
            "@@ -1,5 +0,0 @@",
        ]
    )
    assert added_ranges(diff) == {"a.py": [(4, 5), (12, 12)]}


def test_ranged_format_runs_once_per_hunk_bottom_up():
    check = Check(glob="**/*.py", cwd="svc", format=["fmt --range={start}-{end} --stop={stop} {file}", "sort {file}"])
    assert check.format_commands("svc/pkg/a b.py", [(4, 5), (20, 22)]) == [
        "fmt --range=20-22 --stop=23 'pkg/a b.py'",
        "fmt --range=4-5 --stop=6 'pkg/a b.py'",
        "sort 'pkg/a b.py'",
    ]


def test_report_commands_pass_files_relative_to_cwd():
    check = Check(glob="**/*.py", cwd="svc", lint=["lint {files}"], typecheck=["types"])
    assert check.report_commands(["svc/a.py", "svc/b/c.py"]) == ["lint a.py b/c.py", "types"]


@pytest.mark.parametrize(
    "output_line",
    [
        "pkg/a.py:7:1: I001 Import block is un-sorted",
        "pkg/a.py:7: error: Incompatible types",
        "pkg/a.py(7,3): error TS2322: Type mismatch",
        "  {repo}/svc/pkg/a.py:7:5 - error: Bad",
    ],
)
def test_findings_keep_only_changed_lines(tmp_path, output_line):
    check = Check(glob="**/*.py", cwd="svc")
    changed = {"svc/pkg/a.py": {7}}
    kept = output_line.format(repo=tmp_path)
    unchanged = kept.replace(":7", ":8").replace("(7,", "(8,")
    output = "\n".join([kept, unchanged, "Found 2 errors in 1 file"])
    assert check.findings(completed(output), tmp_path, changed) == [kept.strip()]


def test_eslint_json_findings_use_absolute_paths(tmp_path):
    check = Check(glob="src/**/*.ts", cwd="web", output="eslint-json")
    output = json.dumps(
        [
            {
                "filePath": str(tmp_path / "web/src/a.ts"),
                "messages": [
                    {"line": 3, "message": "Missing semicolon", "ruleId": "semi"},
                    {"line": 9, "message": "Unused var", "ruleId": "no-unused-vars"},
                ],
            }
        ]
    )
    found = check.findings(completed(output, stderr="level=warning compose"), tmp_path, {"web/src/a.ts": {3}})
    assert found == [f"{tmp_path}/web/src/a.ts:3: Missing semicolon (semi)"]


def completed(stdout, returncode=0, stderr=""):
    return subprocess.CompletedProcess("cmd", returncode, stdout=stdout, stderr=stderr)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "test")
    (tmp_path / "a.py").write_text("one\ntwo\nthree\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "base")
    (tmp_path / "a.py").write_text("one\nTWO\nthree\n")
    (tmp_path / ".git/info/exclude").write_text(".claude/\n")
    profile = tmp_path / code_checks.PROFILE
    profile.parent.mkdir()
    profile.write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "glob": "**/*.py",
                        "format": ["echo {start}-{end} {file} >> ../format.log"],
                        "lint": ["printf 'a.py:1: old\\na.py:2: new\\n'"],
                    }
                ]
            }
        )
    )
    monkeypatch.setattr(code_checks, "STATE_DIR", tmp_path.parent / "state")
    return tmp_path


def run_main(monkeypatch, capsys, event):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(event)))
    assert code_checks.main() == 0
    return capsys.readouterr().out


def test_edit_formats_the_changed_range_of_the_edited_file(repo, monkeypatch, capsys):
    event = {"hook_event_name": "PostToolUse", "tool_input": {"file_path": str(repo / "a.py")}}
    assert run_main(monkeypatch, capsys, event) == ""
    assert (repo.parent / "format.log").read_text() == "2-2 a.py\n"


def test_stop_blocks_with_findings_on_changed_lines_only(repo, monkeypatch, capsys):
    out = json.loads(run_main(monkeypatch, capsys, {"hook_event_name": "Stop", "cwd": str(repo)}))
    assert out["decision"] == "block"
    assert out["reason"].endswith("\na.py:2: new")


def test_stop_does_nothing_when_already_continuing(repo, monkeypatch, capsys):
    event = {"hook_event_name": "Stop", "cwd": str(repo), "stop_hook_active": True}
    assert run_main(monkeypatch, capsys, event) == ""


def test_stop_ignores_repos_without_a_profile(repo, monkeypatch, capsys):
    (repo / code_checks.PROFILE).unlink()
    assert run_main(monkeypatch, capsys, {"hook_event_name": "Stop", "cwd": str(repo)}) == ""


def test_untracked_files_count_as_wholly_changed(repo):
    (repo / "new.py").write_text("x\ny\n")
    assert code_checks.changed_ranges(Path(repo))["new.py"] == [(1, 2)]


@pytest.mark.parametrize(
    ("returncode", "output", "expected"),
    [
        (0, "", []),
        (1, "a.py:2: new\na.py:3: old", ["a.py:2: new"]),
        (1, "a.py:3: old", []),
        (126, "bad interpreter", ["$ lint exited 126 without reporting a location:\nbad interpreter"]),
    ],
)
def test_report_flags_a_tool_that_fails_without_locations(tmp_path, returncode, output, expected):
    result = completed(output, returncode)
    assert Check(glob="*").report("lint", result, tmp_path, {"a.py": {2}}) == expected


def test_stop_skips_a_worktree_it_already_checked_this_session(repo, monkeypatch, capsys):
    event = {"hook_event_name": "Stop", "cwd": str(repo), "session_id": "s1"}
    assert run_main(monkeypatch, capsys, event) != ""
    assert run_main(monkeypatch, capsys, event) == ""
    (repo / "a.py").write_text("one\nTWO\nTHREE\n")
    assert run_main(monkeypatch, capsys, event) != ""


@pytest.mark.parametrize(
    ("content", "code", "out"),
    [("one\nTWO\nthree\n", 1, "a.py:2: new"), ("one\ntwo\nthree\n", 0, "ok")],
)
def test_check_worktree_reports_findings_on_uncommitted_lines(repo, capsys, content, code, out):
    (repo / "a.py").write_text(content)
    assert code_checks.check_worktree(repo) == code
    assert capsys.readouterr().out.strip() == out
