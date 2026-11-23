#!/usr/bin/env python3
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROFILE = Path(".claude/repo-profile.local.json")
STATE_DIR = Path(os.environ.get("TMPDIR", "/tmp")) / "claude-code-checks"
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
LOCATED_LINE = re.compile(r"^\s*(?P<path>[^\s:(]+)(?::(?P<line>\d+)|\((?P<paren_line>\d+),\d+\))")


def glob_regex(pattern: str) -> re.Pattern[str]:
    parts = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            parts.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            parts.append(".*")
            i += 2
        elif pattern[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            parts.append("[^/]")
            i += 1
        elif pattern[i] == "{" and (close := pattern.find("}", i)) > i:
            options = pattern[i + 1 : close].split(",")
            parts.append("(?:" + "|".join(re.escape(o) for o in options) + ")")
            i = close + 1
        else:
            parts.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(parts) + r"\Z")


def glob_match(pattern: str, path: str) -> bool:
    return bool(glob_regex(pattern).match(path))


def added_ranges(diff: str) -> dict[str, list[tuple[int, int]]]:
    ranges: dict[str, list[tuple[int, int]]] = {}
    current = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else None
        elif current and (match := HUNK.match(line)):
            start, count = int(match[1]), int(match[2] or 1)
            if count:
                ranges.setdefault(current, []).append((start, start + count - 1))
    return ranges


def lines_in(ranges: list[tuple[int, int]]) -> set[int]:
    return {n for start, end in ranges for n in range(start, end + 1)}


Result = subprocess.CompletedProcess[str]


class OutputParser(ABC):
    @abstractmethod
    def locations(self, result: Result) -> list[tuple[str, int, str]]: ...


class LineParser(OutputParser):
    def locations(self, result: Result) -> list[tuple[str, int, str]]:
        found = []
        for text in (result.stdout + result.stderr).splitlines():
            if match := LOCATED_LINE.match(text):
                line = match["line"] or match["paren_line"]
                found.append((match["path"], int(line), text.strip()))
        return found


class EslintJsonParser(OutputParser):
    def locations(self, result: Result) -> list[tuple[str, int, str]]:
        try:
            results = json.loads(result.stdout)
        except json.JSONDecodeError:
            return []
        return [
            (
                result["filePath"],
                message.get("line", 0),
                f"{result['filePath']}:{message.get('line', 0)}: {message['message']} ({message.get('ruleId')})",
            )
            for result in results
            for message in result["messages"]
        ]


PARSERS: dict[str, OutputParser] = {"lines": LineParser(), "eslint-json": EslintJsonParser()}


@dataclass
class Check:
    glob: str
    cwd: str = "."
    format: list[str] = field(default_factory=list)
    lint: list[str] = field(default_factory=list)
    typecheck: list[str] = field(default_factory=list)
    output: str = "lines"

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Check":
        return cls(**data)

    def covers(self, repo_path: str) -> bool:
        return glob_match(self.glob, repo_path)

    def relative_to_cwd(self, repo_path: str) -> str:
        return os.path.relpath(repo_path, self.cwd)

    def format_commands(self, repo_path: str, ranges: list[tuple[int, int]]) -> list[str]:
        file = shlex.quote(self.relative_to_cwd(repo_path))
        commands = []
        for template in self.format:
            if "{start}" in template:
                for start, end in sorted(ranges, reverse=True):
                    commands.append(template.format(file=file, start=start, end=end, stop=end + 1))
            else:
                commands.append(template.format(file=file))
        return commands

    def report_commands(self, repo_paths: list[str]) -> list[str]:
        files = " ".join(shlex.quote(self.relative_to_cwd(p)) for p in repo_paths)
        return [template.format(files=files) for template in self.lint + self.typecheck]

    def findings(self, result: Result, repo: Path, changed: dict[str, set[int]]) -> list[str]:
        found = []
        for path, line, text in PARSERS[self.output].locations(result):
            repo_path = os.path.relpath(os.path.normpath(repo / self.cwd / path), repo)
            if line in changed.get(repo_path, set()):
                found.append(text)
        return found

    def report(self, command: str, result: Result, repo: Path, changed: dict[str, set[int]]) -> list[str]:
        if result.returncode and not PARSERS[self.output].locations(result):
            output = (result.stdout + result.stderr).strip()[-2000:]
            return [f"$ {command} exited {result.returncode} without reporting a location:\n{output}"]
        return self.findings(result, repo, changed)


def checks_for(profile: dict[str, Any]) -> list[Check]:
    return [Check.from_json(c) for c in profile.get("checks", [])]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def repo_root(start: Path) -> Path | None:
    try:
        return Path(git(start, "rev-parse", "--show-toplevel").strip())
    except (subprocess.CalledProcessError, NotADirectoryError, FileNotFoundError):
        return None


def changed_ranges(repo: Path) -> dict[str, list[tuple[int, int]]]:
    ranges = added_ranges(git(repo, "diff", "-U0", "--no-color", "HEAD"))
    for path in git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
        try:
            count = len((repo / path).read_text().splitlines())
        except (UnicodeDecodeError, OSError):
            continue
        if count:
            ranges[path] = [(1, count)]
    return ranges


def worktree_fingerprint(repo: Path, ranges: dict[str, list[tuple[int, int]]]) -> str:
    digest = hashlib.sha256(git(repo, "diff", "--no-color", "HEAD").encode())
    for path in sorted(ranges):
        try:
            digest.update(path.encode() + (repo / path).read_bytes())
        except OSError:
            continue
    return digest.hexdigest()


def run(command: str, cwd: Path) -> Result:
    return subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)


def load_profile(repo: Path) -> dict[str, Any]:
    try:
        return json.loads((repo / PROFILE).read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def on_edit(event: dict[str, Any]) -> int:
    file_path = Path(event["tool_input"]["file_path"])
    repo = repo_root(file_path.parent)
    if repo is None:
        return 0
    repo_path = os.path.relpath(file_path.resolve(), repo.resolve())
    ranges = changed_ranges(repo).get(repo_path)
    if not ranges:
        return 0
    failures = []
    for check in checks_for(load_profile(repo)):
        if not check.covers(repo_path):
            continue
        for command in check.format_commands(repo_path, ranges):
            result = run(command, repo / check.cwd)
            if result.returncode:
                failures.append(f"$ {command}\n{(result.stderr or result.stdout).strip()}")
    if failures:
        context = "The formatter failed on this file:\n" + "\n".join(failures)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))
    return 0


def report_findings(repo: Path, checks: list[Check], ranges: dict[str, list[tuple[int, int]]]) -> list[str]:
    changed = {path: lines_in(r) for path, r in ranges.items()}
    found = []
    for check in checks:
        paths = sorted(p for p in ranges if check.covers(p) and (repo / p).exists())
        if not paths:
            continue
        for command in check.report_commands(paths):
            result = run(command, repo / check.cwd)
            found.extend(check.report(command, result, repo, changed))
    return found


def check_worktree(start: Path) -> int:
    repo = repo_root(start)
    if repo is None:
        print("not a git repository")
        return 1
    found = report_findings(repo, checks_for(load_profile(repo)), changed_ranges(repo))
    print("\n".join(found) or "ok")
    return 1 if found else 0


def on_stop(event: dict[str, Any]) -> int:
    if event.get("stop_hook_active"):
        return 0
    repo = repo_root(Path(event["cwd"]))
    if repo is None:
        return 0
    checks = checks_for(load_profile(repo))
    if not checks:
        return 0
    ranges = changed_ranges(repo)
    state = STATE_DIR / f"{event.get('session_id', 'none')}-{hashlib.sha256(str(repo).encode()).hexdigest()[:12]}"
    fingerprint = worktree_fingerprint(repo, ranges)
    if state.exists() and state.read_text() == fingerprint:
        return 0
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state.write_text(fingerprint)
    found = report_findings(repo, checks, ranges)
    if not found:
        return 0
    reason = "Lint and typecheck found problems on lines you changed. Fix them, or tell the user why one cannot be fixed:\n"
    print(json.dumps({"decision": "block", "reason": reason + "\n".join(found)}))
    return 0


def main() -> int:
    event = json.load(sys.stdin)
    if event.get("hook_event_name") == "Stop":
        return on_stop(event)
    return on_edit(event)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        sys.exit(check_worktree(Path(sys.argv[2] if len(sys.argv) > 2 else ".")))
    sys.exit(main())
