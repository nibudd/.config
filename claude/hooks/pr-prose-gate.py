#!/usr/bin/env python3
import json
import os
import re
import shlex
import subprocess
import sys

MARKER = "TODO: Update Prose"
TICKET_KEY = re.compile(r"\b(?:PROG|CO)-\d+\b")


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, check=True
    ).stdout


def repo_dir(cwd, command):
    tokens = shlex.split(command)
    if len(tokens) > 2 and tokens[0] == "cd" and tokens[2] in ("&&", ";"):
        return os.path.join(cwd, os.path.expanduser(tokens[1]))
    return cwd


def base_ref(repo):
    try:
        return git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
    except subprocess.CalledProcessError:
        return "origin/main"


def added_lines(repo, base):
    current = None
    for line in git(repo, "diff", "-U0", f"{base}...HEAD").splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("+") and current:
            yield current, line[1:]


def violations(lines):
    for path, text in lines:
        if MARKER in text:
            yield f"{path}: prose marker: {text.strip()}"
        elif not path.endswith(".md") and TICKET_KEY.search(text):
            yield f"{path}: ticket key: {text.strip()}"


def main():
    event = json.load(sys.stdin)
    repo = repo_dir(event["cwd"], event["tool_input"]["command"])
    if subprocess.run(["git", "-C", repo, "rev-parse"], capture_output=True).returncode:
        return 0
    found = list(violations(added_lines(repo, base_ref(repo))))
    if not found:
        return 0
    print(
        "PR blocked. The branch adds prose markers or ticket keys. "
        "List each hit below for the user. Do not remove a marker: the user "
        "rewrites marked prose. Strip a ticket key from prose you wrote. "
        "Flag a ticket key in prose the user wrote, and leave it.\n" + "\n".join(found),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
