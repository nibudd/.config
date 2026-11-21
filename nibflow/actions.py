import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from layout import Layout
from lookup import Task, match

LIST_WINDOWS_FORMAT = "#{window_id}\t#{@nibflow_task}"
WINDOW_NAME = "nibflow"


@dataclass(frozen=True)
class Window:
    id: str
    task: str | None

    @classmethod
    def from_list_windows_line(cls, line: str) -> "Window":
        window_id, _, task = line.rstrip("\n").partition("\t")
        return cls(id=window_id, task=task or None)


class Action(ABC):
    @property
    @abstractmethod
    def tmux_invocations(self) -> list[list[str]]: ...

    @property
    @abstractmethod
    def message(self) -> str: ...

    @property
    @abstractmethod
    def exit_code(self) -> int: ...


def pane_command(argv: list[str]) -> str:
    return f"{shlex.join(argv)}; exec $SHELL"


@dataclass(frozen=True)
class Open(Action):
    task: Task
    layout: Layout
    nibflow_dir: Path

    @property
    def claude_command(self) -> str:
        return pane_command(["claude"])

    @property
    def nvim_command(self) -> str:
        return pane_command(["nvim", "-c", f"set rtp+={self.nibflow_dir}", "-c", "lua require('nibflow').start()"])

    @property
    def split_flags(self) -> str:
        return "-hbd" if self.layout.nvim_before else "-hd"

    @property
    def tmux_invocations(self) -> list[list[str]]:
        start = str(self.task.start_directory)
        return [
            [
                "new-window", "-n", WINDOW_NAME, "-c", start, self.claude_command, ";",
                "set-option", "-w", "@nibflow_task", self.task.key, ";",
                "set-option", "-w", "@nibflow_layout", self.layout.name, ";",
                "split-window", self.split_flags, "-l", f"{self.layout.nvim_percent}%", "-c", start, self.nvim_command,
            ]
        ]  # fmt: skip

    @property
    def message(self) -> str:
        return ""

    @property
    def exit_code(self) -> int:
        return 0


@dataclass(frozen=True)
class Select(Action):
    window: Window
    other_key: str | None = None

    @property
    def tmux_invocations(self) -> list[list[str]]:
        return [["select-window", "-t", self.window.id]]

    @property
    def message(self) -> str:
        if self.other_key is None:
            return ""
        return (
            f"TODO: Update Prose nibflow: the window holds {self.window.task}; "
            f"switching to {self.other_key} is not available yet"
        )

    @property
    def exit_code(self) -> int:
        return 0


class Refusal(Enum):
    NOT_IN_TMUX = "TODO: Update Prose nibflow: not inside tmux"
    NO_REPO = "TODO: Update Prose nibflow: not on a branch of a git repo; pass a task key"
    NO_MATCH = "TODO: Update Prose nibflow: no task matches this repo and branch; pass a task key"
    MANY_MATCHES = "TODO: Update Prose nibflow: more than one task matches ({}); pass a task key"
    UNKNOWN_KEY = "TODO: Update Prose nibflow: no state.yaml for task {}"
    MISSING_START = "TODO: Update Prose nibflow: start directory {} does not exist"


@dataclass(frozen=True)
class Refuse(Action):
    refusal: Refusal
    details: tuple[str, ...] = ()

    @property
    def tmux_invocations(self) -> list[list[str]]:
        return []

    @property
    def message(self) -> str:
        return self.refusal.value.format(", ".join(self.details))

    @property
    def exit_code(self) -> int:
        return 1


class Resolution(ABC):
    @property
    @abstractmethod
    def wanted_key(self) -> str | None: ...

    @abstractmethod
    def to_action(self, layout: Layout, nibflow_dir: Path) -> Action: ...


@dataclass(frozen=True)
class Resolved(Resolution):
    task: Task

    @property
    def wanted_key(self) -> str | None:
        return self.task.key

    def to_action(self, layout: Layout, nibflow_dir: Path) -> Action:
        if not self.task.start_directory_exists:
            return Refuse(Refusal.MISSING_START, (str(self.task.start_directory),))
        return Open(self.task, layout, nibflow_dir)


@dataclass(frozen=True)
class Unresolved(Resolution):
    refuse: Refuse
    key: str | None = None

    @property
    def wanted_key(self) -> str | None:
        return self.key

    def to_action(self, layout: Layout, nibflow_dir: Path) -> Action:
        return self.refuse


def resolve_task(toplevel: Path | None, branch: str | None, key: str | None, tasks: list[Task]) -> Resolution:
    if key is not None:
        by_key = [task for task in tasks if task.key == key]
        return Resolved(by_key[0]) if by_key else Unresolved(Refuse(Refusal.UNKNOWN_KEY, (key,)), key)
    if toplevel is None or branch is None:
        return Unresolved(Refuse(Refusal.NO_REPO))
    found = match(tasks, toplevel, branch)
    if not found:
        return Unresolved(Refuse(Refusal.NO_MATCH))
    if len(found) > 1:
        return Unresolved(Refuse(Refusal.MANY_MATCHES, tuple(task.key for task in found)))
    return Resolved(found[0])


def select_existing(window: Window, wanted: str | None) -> Select:
    return Select(window, None if wanted in (None, window.task) else wanted)


def decide(
    *,
    in_tmux: bool,
    toplevel: Path | None,
    branch: str | None,
    key: str | None,
    tasks: list[Task],
    windows: list[Window],
    layout: Layout,
    nibflow_dir: Path,
) -> Action:
    if not in_tmux:
        return Refuse(Refusal.NOT_IN_TMUX)
    resolution = resolve_task(toplevel, branch, key, tasks)
    existing = next((window for window in windows if window.task is not None), None)
    if existing is not None:
        return select_existing(existing, resolution.wanted_key)
    return resolution.to_action(layout, nibflow_dir)
