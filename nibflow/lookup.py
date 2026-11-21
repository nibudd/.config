import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class InvalidState(ValueError):
    pass


def work_root(environ: Mapping[str, str] = os.environ) -> Path:
    return Path(environ.get("BI_WORK_ROOT", Path.home() / ".claude-work"))


def branch_from_git_output(output: str) -> str | None:
    return output.strip() or None


@dataclass(frozen=True)
class Repo:
    path: Path | None
    branch: str | None

    @classmethod
    def from_entry(cls, entry: Any) -> "Repo":
        if not isinstance(entry, dict):
            raise InvalidState("TODO: Update Prose a repos entry is not a mapping")
        path = entry.get("path")
        return cls(path=None if path is None else Path(path), branch=entry.get("branch"))

    def matches(self, toplevel: Path, branch: str) -> bool:
        return self.path is not None and self.branch == branch and self.path.resolve() == toplevel.resolve()


@dataclass(frozen=True)
class Task:
    key: str
    directory: Path
    repos: tuple[Repo, ...]
    start_directory: Path
    start_directory_exists: bool

    @classmethod
    def from_state(cls, directory: Path, state: Any) -> "Task":
        if not isinstance(state, dict):
            raise InvalidState("TODO: Update Prose the state is not a mapping")
        entries = state.get("repos") or []
        if not isinstance(entries, list):
            raise InvalidState("TODO: Update Prose repos is not a list")
        repos = tuple(Repo.from_entry(entry) for entry in entries)
        start = next((repo.path for repo in repos if repo.path is not None), directory)
        return cls(
            key=directory.name,
            directory=directory,
            repos=repos,
            start_directory=start,
            start_directory_exists=start.is_dir(),
        )

    def matches(self, toplevel: Path, branch: str) -> bool:
        return any(repo.matches(toplevel, branch) for repo in self.repos)


def find_tasks(root: Path) -> list[Task]:
    tasks = []
    for state_file in sorted(root.glob("*/state.yaml")):
        try:
            tasks.append(Task.from_state(state_file.parent, yaml.safe_load(state_file.read_text())))
        except (yaml.YAMLError, InvalidState) as error:
            reason = " ".join(str(error).split())
            print(f"TODO: Update Prose nibflow: skipped {state_file}: {reason}", file=sys.stderr)
    return tasks


def match(tasks: list[Task], toplevel: Path, branch: str | None) -> list[Task]:
    if branch is None:
        return []
    return [task for task in tasks if task.matches(toplevel, branch)]
