import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from actions import Action, Open, Refusal, Refuse, Select, Window, decide
from layout import LAYOUTS, Layout, Side
from lookup import Repo, Task, branch_from_git_output, find_tasks, match, work_root

LAYOUT_NAMES = sorted(path.stem for path in LAYOUTS.glob("*.json"))


def layout_text(side: str, percent: int) -> str:
    return json.dumps(
        {
            "tmux": {"claude": {"side": side, "percent": percent}},
            "nvim": {"split": "row", "children": [{"view": "overview"}]},
        }
    )


@pytest.mark.parametrize("side", list(Side))
def test_layout_from_json(side: Side) -> None:
    layout = Layout.from_json("example", layout_text(side.value, 30))

    assert layout == Layout(name="example", claude_side=side, claude_percent=30)


@pytest.mark.parametrize(
    ("side", "nvim_before"),
    [(Side.LEFT, False), (Side.RIGHT, True)],
)
def test_side_nvim_before(side: Side, nvim_before: bool) -> None:
    assert side.nvim_before is nvim_before


@pytest.mark.parametrize("side", list(Side))
@pytest.mark.parametrize(("claude_percent", "nvim_percent"), [(40, 60), (25, 75)])
def test_layout_derives_nvim_split(side: Side, claude_percent: int, nvim_percent: int) -> None:
    layout = Layout(name="example", claude_side=side, claude_percent=claude_percent)

    assert (layout.nvim_percent, layout.nvim_before) == (nvim_percent, side.nvim_before)


def test_layouts_directory_is_not_empty() -> None:
    assert LAYOUT_NAMES


@pytest.mark.parametrize("name", LAYOUT_NAMES)
def test_layout_file_loads(name: str) -> None:
    layout = Layout.load(name)

    assert layout.name == name
    assert 0 < layout.nvim_percent < 100


def repo_entry(path: Path | str | None, branch: str | None) -> dict[str, Any]:
    return {"path": None if path is None else str(path), "branch": branch}


def write_state(work_root: Path, key: str, content: str | bytes) -> Path:
    directory = work_root / key
    directory.mkdir(parents=True)
    state_file = directory / "state.yaml"
    if isinstance(content, bytes):
        state_file.write_bytes(content)
    else:
        state_file.write_text(content)
    return directory


def task(key: str, *repos: dict[str, Any], state: str = "implement") -> Task:
    return Task.from_state(Path("/work") / key, {"key": key, "state": state, "repos": list(repos)})


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "repos" / "example"
    (path / "src" / "deep").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "feature", str(path)], check=True)
    return path


@pytest.mark.parametrize(
    ("tasks", "branch", "expected"),
    [
        pytest.param([("A-1", "feature")], "feature", ["A-1"], id="one match"),
        pytest.param([("A-1", "other")], "feature", [], id="branch differs"),
        pytest.param([("A-1", "feature"), ("B-2", "feature")], "feature", ["A-1", "B-2"], id="two matches"),
        pytest.param([("A-1", None)], "feature", [], id="entry branch null"),
        pytest.param([("A-1", "feature")], None, [], id="no branch"),
        pytest.param([], "feature", [], id="no tasks"),
    ],
)
def test_match(repo: Path, tasks: list[tuple[str, str | None]], branch: str | None, expected: list[str]) -> None:
    found = match([task(key, repo_entry(repo, entry_branch)) for key, entry_branch in tasks], repo, branch)

    assert [t.key for t in found] == expected


@pytest.mark.parametrize(
    "entry",
    [
        pytest.param({"branch": "feature"}, id="no path"),
        pytest.param({"path": "/elsewhere/example"}, id="no branch"),
        pytest.param({}, id="empty entry"),
    ],
)
def test_match_ignores_incomplete_entry(repo: Path, entry: dict[str, Any]) -> None:
    assert match([task("A-1", entry)], repo, "feature") == []


def test_match_ignores_other_path(repo: Path, tmp_path: Path) -> None:
    assert match([task("A-1", repo_entry(tmp_path / "other", "feature"))], repo, "feature") == []


def test_match_includes_done_task(repo: Path) -> None:
    assert [t.key for t in match([task("A-1", repo_entry(repo, "feature"), state="done")], repo, "feature")] == ["A-1"]


def test_match_any_repo_of_a_task(repo: Path, tmp_path: Path) -> None:
    tasks = [task("A-1", repo_entry(tmp_path / "other", "feature"), repo_entry(repo, "feature"))]

    assert [t.key for t in match(tasks, repo, "feature")] == ["A-1"]


def git_toplevel_from(directory: Path) -> Path:
    output = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=directory, capture_output=True, text=True, check=True
    ).stdout
    return Path(output.strip())


def test_match_from_subdirectory(repo: Path) -> None:
    toplevel = git_toplevel_from(repo / "src" / "deep")

    assert [t.key for t in match([task("A-1", repo_entry(repo, "feature"))], toplevel, "feature")] == ["A-1"]


def test_match_from_symlinked_directory(repo: Path, tmp_path: Path) -> None:
    link = tmp_path / "link"
    link.symlink_to(repo)
    toplevel = git_toplevel_from(link / "src" / "deep")

    assert [t.key for t in match([task("A-1", repo_entry(repo, "feature"))], toplevel, "feature")] == ["A-1"]


@pytest.mark.parametrize(
    ("output", "expected"),
    [("feature\n", "feature"), ("team/feature", "team/feature"), ("", None), ("\n", None)],
)
def test_branch_from_git_output(output: str, expected: str | None) -> None:
    assert branch_from_git_output(output) == expected


@pytest.mark.parametrize(
    ("repos", "expected"),
    [
        pytest.param(["repo"], "repo", id="first repo"),
        pytest.param(["repo", "other"], "repo", id="first of two repos"),
        pytest.param([None, "repo"], "repo", id="first entry has no path"),
        pytest.param([], "task", id="no repos"),
        pytest.param(["missing"], "missing", id="repo path missing"),
    ],
)
def test_task_start_directory(tmp_path: Path, repos: list[str | None], expected: str) -> None:
    places = {"repo": tmp_path / "repo", "other": tmp_path / "other", "task": tmp_path / "A-1", "missing": tmp_path / "gone"}
    for name in ("repo", "other", "task"):
        places[name].mkdir()
    entries = [repo_entry(None if name is None else places[name], "feature") for name in repos]

    found = Task.from_state(places["task"], {"repos": entries})

    assert (found.start_directory, found.start_directory_exists) == (places[expected], expected != "missing")


def test_find_tasks_reads_each_state(tmp_path: Path) -> None:
    write_state(tmp_path, "A-1", "key: A-1\nrepos:\n- path: /repos/example\n  branch: feature\n")
    write_state(tmp_path, "B-2", "key: B-2\n")
    (tmp_path / "notes").mkdir()

    tasks = find_tasks(tmp_path)

    assert [(t.key, t.repos) for t in tasks] == [
        ("A-1", (Repo(Path("/repos/example"), Path("/repos/example").resolve(), "feature"),)),
        ("B-2", ()),
    ]


def state_on(key: str, path: Path) -> str:
    return yaml.safe_dump({"key": key, "repos": [repo_entry(path, "feature")]})


def test_find_tasks_reads_non_ascii_utf8(tmp_path: Path, repo: Path) -> None:
    write_state(tmp_path, "A-1", (state_on("A-1", repo) + "title: café über straße\n").encode())

    assert [t.key for t in match(find_tasks(tmp_path), repo, "feature")] == ["A-1"]


def test_find_tasks_resolves_symlinked_repo(tmp_path: Path, repo: Path) -> None:
    link = tmp_path / "link"
    link.symlink_to(repo)
    write_state(tmp_path / "work", "A-1", state_on("A-1", link))

    tasks = find_tasks(tmp_path / "work")

    assert [t.key for t in match(tasks, repo, "feature")] == ["A-1"]
    assert (tasks[0].repos[0].resolved_path, tasks[0].start_directory) == (repo, link)


@pytest.mark.parametrize(
    "bad_bytes",
    [
        pytest.param(b"key: [unclosed\n", id="invalid yaml"),
        pytest.param(b"- a list\n", id="not a mapping"),
        pytest.param(b"", id="empty"),
        pytest.param(b"repos: not-a-list\n", id="repos not a list"),
        pytest.param(b"repos:\n- just-a-string\n", id="repo entry not a mapping"),
        pytest.param(b"repos:\n- path: 5\n  branch: feature\n", id="repo path not a string"),
        pytest.param(b"repos:\n- path: [a, b]\n  branch: feature\n", id="repo path a list"),
        pytest.param(b'repos:\n- path: "/x\\0"\n  branch: feature\n', id="repo path has a NUL"),
        pytest.param(b'repos:\n- path: ""\n  branch: feature\n', id="repo path empty"),
        pytest.param(b"repos:\n- path: .\n  branch: feature\n", id="repo path relative"),
        pytest.param(b'repos:\n- path: "/x\\ud800"\n  branch: feature\n', id="repo path has a lone surrogate"),
        pytest.param(b"key: \xff\xfe\nrepos:\n- path: /x\n  branch: feature\n", id="not utf-8"),
    ],
)
def test_find_tasks_isolates_bad_file(
    tmp_path: Path, repo: Path, capsys: pytest.CaptureFixture[str], bad_bytes: bytes
) -> None:
    root = tmp_path / "work"
    write_state(root, "A-1", state_on("A-1", repo))
    bad = write_state(root, "B-2", bad_bytes)
    write_state(root, "C-3", state_on("C-3", repo))

    assert_skipped_only(root, repo, capsys, bad)


def test_find_tasks_skips_unreadable_file(tmp_path: Path, repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "work"
    write_state(root, "A-1", state_on("A-1", repo))
    bad = root / "B-2"
    (bad / "state.yaml").mkdir(parents=True)
    write_state(root, "C-3", state_on("C-3", repo))

    assert_skipped_only(root, repo, capsys, bad)


def assert_skipped_only(root: Path, repo: Path, capsys: pytest.CaptureFixture[str], bad: Path) -> None:
    tasks = match(find_tasks(root), repo, "feature")

    assert [t.key for t in tasks] == ["A-1", "C-3"]
    warnings = capsys.readouterr().err.splitlines()
    assert len(warnings) == 1
    assert str(bad / "state.yaml") in warnings[0]


@pytest.mark.parametrize(
    ("environ", "expected"),
    [({"BI_WORK_ROOT": "/elsewhere/work"}, Path("/elsewhere/work")), ({}, Path.home() / ".claude-work")],
)
def test_work_root(environ: dict[str, str], expected: Path) -> None:
    assert work_root(environ) == expected


NIBFLOW_DIR = Path("/opt/nibflow")
LARGE = Layout(name="large", claude_side=Side.RIGHT, claude_percent=40)


@pytest.fixture
def work(tmp_path: Path, repo: Path) -> dict[str, Any]:
    gone = tmp_path / "gone"
    tasks = [
        Task.from_state(tmp_path / "A-1", {"repos": [repo_entry(repo, "feature")]}),
        Task.from_state(tmp_path / "B-2", {"repos": [repo_entry(repo, "shared")]}),
        Task.from_state(tmp_path / "C-3", {"repos": [repo_entry(repo, "shared")]}),
        Task.from_state(tmp_path / "D-4", {"repos": [repo_entry(gone, "lost")]}),
    ]
    return {"repo": repo, "tasks": tasks}


def decide_in(work: dict[str, Any], **overrides: Any) -> Action:
    inputs: dict[str, Any] = {
        "in_tmux": True,
        "toplevel": work["repo"],
        "branch": "feature",
        "key": None,
        "tasks": work["tasks"],
        "windows": [],
        "layout": LARGE,
        "nibflow_dir": NIBFLOW_DIR,
    }
    return decide(**(inputs | overrides))


@pytest.mark.parametrize(
    ("overrides", "refusal", "details"),
    [
        pytest.param({"in_tmux": False}, Refusal.NOT_IN_TMUX, (), id="not in tmux"),
        pytest.param({"in_tmux": False, "key": "A-1"}, Refusal.NOT_IN_TMUX, (), id="not in tmux with key"),
        pytest.param({"branch": "nothing"}, Refusal.NO_MATCH, (), id="no match"),
        pytest.param({"branch": "shared"}, Refusal.MANY_MATCHES, ("B-2", "C-3"), id="more than one match"),
        pytest.param({"toplevel": None, "branch": None}, Refusal.NO_REPO, (), id="outside git"),
        pytest.param({"branch": None}, Refusal.NO_REPO, (), id="detached head"),
        pytest.param({"key": "Z-9"}, Refusal.UNKNOWN_KEY, ("Z-9",), id="key with no state"),
        pytest.param({"key": "D-4"}, Refusal.MISSING_START, ("gone",), id="start directory missing"),
    ],
)
def test_refusals(work: dict[str, Any], overrides: dict[str, Any], refusal: Refusal, details: tuple[str, ...]) -> None:
    action = decide_in(work, **overrides)

    assert isinstance(action, Refuse)
    shown = tuple(Path(d).name if refusal is Refusal.MISSING_START else d for d in action.details)
    assert (action.refusal, shown, action.exit_code, action.tmux_invocations) == (refusal, details, 1, [])


def test_refusal_message_lists_matching_keys(work: dict[str, Any]) -> None:
    message = decide_in(work, branch="shared").message

    assert "B-2" in message and "C-3" in message


@pytest.mark.parametrize(
    ("overrides", "other_key"),
    [
        pytest.param({}, None, id="found task is the window task"),
        pytest.param({"key": "A-1"}, None, id="given key is the window task"),
        pytest.param({"key": "B-2"}, "B-2", id="given key differs"),
        pytest.param({"key": "Z-9"}, "Z-9", id="given key has no state"),
        pytest.param({"toplevel": None, "branch": None}, None, id="outside git"),
        pytest.param({"branch": "nothing"}, None, id="no match"),
        pytest.param({"branch": "shared"}, None, id="more than one match"),
        pytest.param({"branch": "lost", "toplevel": Path("/elsewhere")}, None, id="other repo no match"),
    ],
)
def test_select_note(work: dict[str, Any], overrides: dict[str, Any], other_key: str | None) -> None:
    window = Window(id="@7", task="A-1")
    windows = [Window(id="@1", task=None), window]

    action = decide_in(work, windows=windows, **overrides)

    assert action == Select(window, other_key)
    assert (action.tmux_invocations, action.exit_code) == ([["select-window", "-t", "@7"]], 0)
    assert bool(action.message) is (other_key is not None)


def test_select_found_task_differs(work: dict[str, Any]) -> None:
    window = Window(id="@7", task="B-2")

    assert decide_in(work, windows=[window]) == Select(window, "A-1")


def test_window_without_task_is_not_selected(work: dict[str, Any]) -> None:
    assert isinstance(decide_in(work, windows=[Window(id="@1", task=None)]), Open)


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        pytest.param("@3\tA-1\n", Window("@3", "A-1"), id="task"),
        pytest.param("@3\t\n", Window("@3", None), id="empty task"),
        pytest.param("@3\t", Window("@3", None), id="empty task no newline"),
        pytest.param("@12\tteam_feature-x", Window("@12", "team_feature-x"), id="non-ticket key"),
    ],
)
def test_window_from_list_windows_line(line: str, expected: Window) -> None:
    assert Window.from_list_windows_line(line) == expected


@pytest.mark.parametrize(
    ("side", "flags"),
    [(Side.RIGHT, "-hbd"), (Side.LEFT, "-hd")],
)
def test_open_arguments(work: dict[str, Any], side: Side, flags: str) -> None:
    layout = Layout(name="large", claude_side=side, claude_percent=40)
    start = str(work["repo"])

    action = decide_in(work, layout=layout)

    assert isinstance(action, Open)
    assert (action.message, action.exit_code) == ("", 0)
    assert action.tmux_invocations == [
        [
            "new-window", "-n", "nibflow", "-c", start, "claude; exec $SHELL", ";",
            "set-option", "-w", "@nibflow_task", "A-1", ";",
            "set-option", "-w", "@nibflow_layout", "large", ";",
            "split-window", flags, "-l", "60%", "-c", start,
            "nvim -c 'set rtp+=/opt/nibflow' -c 'lua require('\"'\"'nibflow'\"'\"').start()'; exec $SHELL",
        ]
    ]  # fmt: skip


def test_open_by_key_from_anywhere(work: dict[str, Any]) -> None:
    action = decide_in(work, toplevel=None, branch=None, key="A-1")

    assert isinstance(action, Open) and action.task.key == "A-1"


def test_open_sets_options_before_split(work: dict[str, Any]) -> None:
    (invocation,) = decide_in(work).tmux_invocations
    commands = [part[0] for part in split_chain(invocation)]

    assert commands == ["new-window", "set-option", "set-option", "split-window"]


def split_chain(invocation: list[str]) -> list[list[str]]:
    chain: list[list[str]] = [[]]
    for argument in invocation:
        if argument == ";":
            chain.append([])
        else:
            chain[-1].append(argument)
    return chain


@pytest.mark.parametrize("action", ["open", "select", "refuse"])
def test_no_status_option(work: dict[str, Any], action: str) -> None:
    overrides: dict[str, Any] = {
        "open": {},
        "select": {"windows": [Window("@7", "A-1")]},
        "refuse": {"branch": "nothing"},
    }[action]

    arguments = [a for invocation in decide_in(work, **overrides).tmux_invocations for a in invocation]

    assert not [a for a in arguments if a.startswith("status")]


NVIM_SCRIPT = """
local function check()
  local layout = vim.json.decode(table.concat(vim.fn.readfile(vim.env.NIBFLOW_LAYOUT), "\\n"))
  require("nibflow.layout").build(layout, vim.env.NIBFLOW_KEY)
  local windows = {}
  for _, win in ipairs(vim.api.nvim_tabpage_list_wins(0)) do
    windows[tostring(win)] = {
      width = vim.api.nvim_win_get_width(win),
      height = vim.api.nvim_win_get_height(win),
      fixwidth = vim.api.nvim_get_option_value("winfixwidth", { win = win }),
      fixheight = vim.api.nvim_get_option_value("winfixheight", { win = win }),
      text = table.concat(vim.api.nvim_buf_get_lines(vim.api.nvim_win_get_buf(win), 0, -1, false), "\\n"),
    }
  end
  vim.fn.writefile({ vim.json.encode({ layout = vim.fn.winlayout(), windows = windows }) }, vim.env.NIBFLOW_OUT)
end
local ok, err = xpcall(check, debug.traceback)
if not ok then
  io.stderr:write(err)
  vim.cmd("cquit 1")
end
vim.cmd("qall!")
"""

SYNTHETIC_TREE: dict[str, Any] = {
    "split": "col",
    "children": [
        {"view": "git"},
        {"split": "row", "cells": 10, "children": [{"view": "files", "percent": 30}, {"view": "overview"}]},
    ],
}

AXIS = {"row": "width", "col": "height"}


def built_layout(tmp_path: Path, tree: dict[str, Any], key: str) -> dict[str, Any]:
    layout_file, script, out = tmp_path / "layout.json", tmp_path / "check.lua", tmp_path / "out.json"
    layout_file.write_text(json.dumps({"nvim": tree}))
    script.write_text(NVIM_SCRIPT)
    subprocess.run(
        [
            "nvim",
            "--headless",
            "--clean",
            "--cmd",
            f"set rtp+={LAYOUTS.parent} columns=160 lines=48",
            "-c",
            f"luafile {script}",
        ],
        check=True,
        timeout=30,
        env={**os.environ, "NIBFLOW_LAYOUT": str(layout_file), "NIBFLOW_OUT": str(out), "NIBFLOW_KEY": key},
    )
    return json.loads(out.read_text())


def first_leaf(layout: list[Any]) -> str:
    return str(layout[1]) if layout[0] == "leaf" else first_leaf(layout[1][0])


def assert_matches(
    node: dict[str, Any], layout: list[Any], windows: dict[str, Any], key: str, fixed: frozenset[str] = frozenset()
) -> None:
    if "view" in node:
        assert layout[0] == "leaf"
        window = windows[str(layout[1])]
        assert node["view"] in window["text"] and key in window["text"]
        assert {dimension for dimension in AXIS.values() if window[f"fix{dimension}"]} == fixed
        return
    assert layout[0] == node["split"]
    assert len(layout[1]) == len(node["children"])
    dimension = AXIS[node["split"]]
    sizes = [windows[first_leaf(child)][dimension] for child in layout[1]]
    parent = sum(sizes) + len(sizes) - 1
    for child, size in zip(node["children"], sizes):
        if "cells" in child:
            assert size == child["cells"]
        if "percent" in child:
            assert abs(size - parent * child["percent"] / 100) <= 1
    for child, child_layout in zip(node["children"], layout[1]):
        child_fixed = fixed | {dimension} if "cells" in child else fixed
        assert_matches(child, child_layout, windows, key, child_fixed)


@pytest.mark.parametrize(
    "tree",
    [json.loads((LAYOUTS / f"{name}.json").read_text())["nvim"] for name in LAYOUT_NAMES] + [SYNTHETIC_TREE],
    ids=[*LAYOUT_NAMES, "synthetic"],
)
def test_nvim_builder(tmp_path: Path, tree: dict[str, Any]) -> None:
    key = "KEY-1"
    built = built_layout(tmp_path, tree, key)

    assert_matches(tree, built["layout"], built["windows"], key)


def test_entry_refuses_outside_tmux(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    environ = {name: value for name, value in os.environ.items() if not name.startswith("TMUX")}
    environ |= {
        "TMUX_TMPDIR": str(tmp_path / "tmux"),
        "BI_WORK_ROOT": str(tmp_path / "work"),
        "GIT_CEILING_DIRECTORIES": str(tmp_path),
    }

    result = subprocess.run(
        [str(LAYOUTS.parent / "nibflow")], cwd=outside, env=environ, capture_output=True, text=True
    )

    assert (result.returncode, result.stdout, result.stderr) == (1, "", Refuse(Refusal.NOT_IN_TMUX).message + "\n")
