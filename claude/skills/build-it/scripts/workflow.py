from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

STATES = (
    "requirements",
    "orient",
    "design",
    "direct",
    "plan",
    "implement",
    "review",
    "fix",
    "wrap",
    "done",
)
KINDS = ("feature", "bug", "recovery", "foundation")
TIERS = ("low", "standard", "high")
DECISION_STATUSES = ("agreed", "proposed", "delegated")
QUESTION_STATUSES = ("open", "resolved", "accepted")
CHECK_KINDS = ("command", "new_test", "planned", "none")
BASELINES = ("pass", "fail", "new", "planned")
STEPS_BEFORE_SUMMARY = 5
STEP_STATUSES = ("todo", "done")
SETTABLE = {"kind": KINDS, "tier": TIERS, "waiting_on": None}

FINISHED = "finished"
# The guard that "finished" resolves to when the return stack is empty.
FORWARD = {"requirements": "ready", "orient": "understood", "design": "decided"}

RETURN = "<return>"

# (state, guard) -> (next state, state to push on the return stack on the way in)
TRANSITIONS: dict[tuple[str, str], tuple[str, str | None]] = {
    ("requirements", "ready"): ("orient", None),
    ("requirements", "return"): (RETURN, None),
    ("orient", "understood"): ("design", None),
    ("orient", "return"): (RETURN, None),
    ("design", "decided"): ("direct", None),
    ("design", "return"): (RETURN, None),
    ("design", "approach_changed"): ("direct", None),
    ("design", "new_criterion"): ("requirements", "design"),
    ("design", "gap"): ("orient", "design"),
    ("direct", "accepted"): ("plan", None),
    ("direct", "new_decision"): ("design", None),
    ("plan", "approved"): ("implement", None),
    ("plan", "contradicts"): ("direct", None),
    ("implement", "next_step"): ("implement", None),
    ("implement", "summarized"): ("implement", None),
    ("implement", "done"): ("review", None),
    ("implement", "gate"): ("design", "implement"),
    ("implement", "contradicts"): ("direct", None),
    ("review", "approved"): ("fix", None),
    ("review", "clean"): ("wrap", None),
    ("review", "carried"): ("wrap", None),
    ("fix", "clean"): ("wrap", None),
    ("fix", "survives"): ("direct", None),
    ("wrap", "fix_carried"): ("fix", None),
    ("wrap", "suite_fails"): ("implement", None),
    ("wrap", "done"): ("done", None),
}

DEFAULT_OWNED_PATHS = (
    "**/terraform/**",
    "**/*.tf",
    "**/migrations/**",
    ".github/workflows/**",
    "**/Dockerfile*",
    "**/docker-compose*.yml",
    "**/pyproject.toml",
    "**/package.json",
    "**/uv.lock",
    "**/poetry.lock",
    "**/package-lock.json",
    "**/*secret*",
    "**/*auth*/**",
    "**/*permission*",
)

ACCEPTANCE_LINE = re.compile(r"^- (A\d{2,}): \S")
QUESTION_LINE = re.compile(r"^- (Q\d{2,}) \[(\w+)\]: \S")
ID = re.compile(r"^([A-Z])(\d{2,})$")


class TransitionError(ValueError):
    pass


def derive_key(ticket: str | None, repo: str, branch: str) -> str:
    if ticket:
        return ticket
    return f"{repo.lstrip('.')}_{branch.replace('/', '_')}"


def next_id(existing: Iterable[str], prefix: str) -> str:
    numbers = [int(m.group(2)) for i in existing if (m := ID.match(i)) and m.group(1) == prefix]
    return f"{prefix}{max(numbers, default=0) + 1:02d}"


def tier_floor(paths: Iterable[str], owned: Iterable[str], match: Callable[[str, str], bool]) -> str:
    globs = list(owned)
    return "high" if any(match(g, p) for p in paths for g in globs) else "low"


@dataclass
class Transition:
    state: dict[str, Any]
    summarize: bool


def return_to(state: dict[str, Any]) -> str | None:
    stack = state.get("return_stack") or []
    return stack[-1] if stack else None


def resolve_guard(state: dict[str, Any], guard: str, files: Iterable[TaskFile]) -> str:
    if guard != FINISHED:
        return guard
    current = state.get("state")
    if current == "implement":
        return "next_step" if any(f.todo_steps() for f in files) else "done"
    if current not in FORWARD:
        raise TransitionError(f"guard 'finished' does not apply to {current!r}; name the guard")
    return "return" if return_to(state) else FORWARD[current]


def first_todo_step(files: Iterable[TaskFile]) -> int | None:
    steps = [n for f in files for n in f.todo_steps()]
    return min(steps) if steps else None


def transition(state: dict[str, Any], guard: str) -> Transition:
    current = state["state"]
    try:
        target, push = TRANSITIONS[(current, guard)]
    except KeyError:
        allowed = sorted(g for s, g in TRANSITIONS if s == current)
        raise TransitionError(f"no guard {guard!r} from {current!r}; allowed: {', '.join(allowed)}") from None
    if guard == "carried" and state.get("tier") != "low":
        raise TransitionError("findings are carried to the wrap only at the low tier")
    stack = list(state.get("return_stack") or [])
    if target == RETURN:
        if not stack:
            raise TransitionError(f"guard 'return' from {current!r} needs a non-empty return_stack")
        target = stack.pop()
    elif push:
        stack.append(push)
    if guard == "approach_changed":
        stack = []
    new = {**state, "return_stack": stack, "state": target}
    new["steps_since_gate"] = steps_after(state, guard)
    new["log"] = [*state.get("log", []), {"from": current, "guard": guard, "to": target}]
    return Transition(new, summarize=new["steps_since_gate"] >= STEPS_BEFORE_SUMMARY)


def set_field(state: dict[str, Any], name: str, value: str | None) -> dict[str, Any]:
    if name not in SETTABLE:
        raise TransitionError(f"cannot set {name!r}; settable: {', '.join(SETTABLE)}")
    allowed = SETTABLE[name]
    if allowed is not None and value not in allowed:
        raise TransitionError(f"{name} must be one of {', '.join(allowed)}")
    return {**state, name: value}


def steps_after(state: dict[str, Any], guard: str) -> int:
    count = state.get("steps_since_gate", 0)
    if guard == "next_step":
        return count + 1
    if guard in ("gate", "summarized"):
        return 0
    return count


def record_baseline(plan: dict[str, Any], results: dict[int, bool]) -> dict[str, Any]:
    steps = []
    for step in plan.get("steps") or []:
        kind = step.get("check", {}).get("kind")
        baseline = step.get("baseline")
        if step["n"] in results:
            baseline = "pass" if results[step["n"]] else "fail"
        elif kind == "new_test":
            baseline = "new"
        elif kind == "planned":
            baseline = "planned"
        steps.append({**step, "baseline": baseline})
    return {**plan, "steps": steps}


@dataclass
class TaskFile(ABC):
    data: Any

    @abstractmethod
    def defined_ids(self) -> set[str]: ...

    @abstractmethod
    def problems(self, known: set[str], questions: dict[str, str]) -> list[str]: ...

    def questions(self) -> dict[str, str]:
        return {}

    def exit_problems(self, state: dict[str, Any], guard: str) -> list[str]:
        return []

    def todo_steps(self) -> list[int]:
        return []


@dataclass
class Brief(TaskFile):
    data: str

    def acceptance(self) -> set[str]:
        return {m.group(1) for line in self.data.splitlines() if (m := ACCEPTANCE_LINE.match(line))}

    def questions(self) -> dict[str, str]:
        return {m.group(1): m.group(2) for line in self.data.splitlines() if (m := QUESTION_LINE.match(line))}

    def defined_ids(self) -> set[str]:
        return self.acceptance() | set(self.questions())

    def problems(self, known: set[str], questions: dict[str, str]) -> list[str]:
        found = [f"brief.md: {q} has status {s!r}" for q, s in self.questions().items() if s not in QUESTION_STATUSES]
        lines = self.data.splitlines()
        found += [f"brief.md: malformed ID line: {line}" for line in lines if re.match(r"^- [AQ]\d", line) and not (ACCEPTANCE_LINE.match(line) or QUESTION_LINE.match(line))]
        return found

    def exit_problems(self, state: dict[str, Any], guard: str) -> list[str]:
        if (state.get("state"), guard) != ("requirements", "ready"):
            return []
        return [f"brief.md: {q} is still open" for q, s in self.questions().items() if s == "open"]


@dataclass
class Decisions(TaskFile):
    data: list[dict[str, Any]] = field(default_factory=list)

    def defined_ids(self) -> set[str]:
        return {d.get("id") for d in self.data}

    def problems(self, known: set[str], questions: dict[str, str]) -> list[str]:
        found = duplicates("decisions.yaml", [d.get("id") for d in self.data])
        for d in self.data:
            name = f"decisions.yaml: {d.get('id')}"
            if d.get("status") not in DECISION_STATUSES:
                found.append(f"{name} has status {d.get('status')!r}")
            for cited in d.get("serves", []):
                if cited not in known:
                    found.append(f"{name} serves unknown {cited}")
                elif d.get("status") == "agreed" and questions.get(cited) == "open":
                    found.append(f"{name} is agreed but serves open question {cited}")
        return found

    def exit_problems(self, state: dict[str, Any], guard: str) -> list[str]:
        if state.get("state") != "design" or guard not in ("decided", "return"):
            return []
        return [f"decisions.yaml: {d.get('id')} is still proposed" for d in self.data if d.get("status") == "proposed"]


@dataclass
class Plan(TaskFile):
    data: dict[str, Any] = field(default_factory=dict)

    def defined_ids(self) -> set[str]:
        return set()

    def problems(self, known: set[str], questions: dict[str, str]) -> list[str]:
        steps = self.data.get("steps") or []
        found = duplicates("plan.yaml step", [s.get("n") for s in steps])
        for s in steps:
            name = f"plan.yaml: step {s.get('n')}"
            if type(s.get("n")) is not int:
                found.append(f"{name} has a step number that is not an integer")
            cited = s.get("acceptance", [])
            if not cited and not s.get("acceptance_none"):
                found.append(f"{name} cites no acceptance ID and gives no acceptance_none reason")
            found += [f"{name} cites unknown {a}" for a in cited if a not in known]
            found += [f"{name} cites open question {a}" for a in cited if questions.get(a) == "open"]
            found += [f"{name} cites unknown {d}" for d in s.get("decisions", []) if d not in known]
            check = s.get("check", {})
            if check.get("kind") not in CHECK_KINDS:
                found.append(f"{name} has check kind {check.get('kind')!r}")
            elif check.get("kind") in ("command", "planned") and not check.get("run"):
                found.append(f"{name} has a {check['kind']} check with no run command")
            elif check.get("kind") == "none" and not check.get("reason"):
                found.append(f"{name} has check kind 'none' with no reason")
            if s.get("baseline") not in (None, *BASELINES):
                found.append(f"{name} has baseline {s.get('baseline')!r}")
            if s.get("status", "todo") not in STEP_STATUSES:
                found.append(f"{name} has status {s.get('status')!r}")
            elif s.get("status") == "done" and not s.get("commit"):
                found.append(f"{name} is done but records no commit")
        return found

    def todo_steps(self) -> list[int]:
        steps = self.data.get("steps") or []
        return [s["n"] for s in steps if type(s.get("n")) is int and s.get("status", "todo") == "todo"]

    def exit_problems(self, state: dict[str, Any], guard: str) -> list[str]:
        if state.get("state") != "implement" or guard not in ("next_step", "done") or state.get("step") is None:
            return []
        step = next((s for s in self.data.get("steps") or [] if s.get("n") == state["step"]), None)
        if step is None:
            return [f"plan.yaml: step {state['step']} is missing; restore it or ask the user"]
        if step.get("status") != "done":
            return [f"plan.yaml: step {state['step']} is not marked done; set its status and commit"]
        return []


@dataclass
class Review(TaskFile):
    data: dict[str, Any] = field(default_factory=dict)

    def defined_ids(self) -> set[str]:
        return set(self.finding_ids())

    def finding_ids(self) -> list[str]:
        return [f.get("id") for r in self.data.get("rounds") or [] for f in r.get("findings") or []]

    def problems(self, known: set[str], questions: dict[str, str]) -> list[str]:
        ids = self.finding_ids()
        return duplicates("review.yaml", ids)


@dataclass
class State(TaskFile):
    data: dict[str, Any] = field(default_factory=dict)

    def defined_ids(self) -> set[str]:
        return set()

    def problems(self, known: set[str], questions: dict[str, str]) -> list[str]:
        found = []
        for name, allowed in (("state", (None, *STATES)), ("kind", (None, *KINDS)), ("tier", (None, *TIERS))):
            if self.data.get(name) not in allowed:
                found.append(f"state.yaml: {name} is {self.data.get(name)!r}")
        found += [f"state.yaml: return_stack holds {s!r}" for s in self.data.get("return_stack") or [] if s not in STATES]
        waiting = self.data.get("waiting_on")
        if waiting and questions.get(waiting) != "open":
            found.append(f"state.yaml: waiting_on {waiting} is not an open question")
        return found

    def exit_problems(self, state: dict[str, Any], guard: str) -> list[str]:
        if (state.get("state"), guard) == ("design", "decided") and return_to(state):
            return [f"state.yaml: return_stack is not empty; use 'return' to go back to {return_to(state)}"]
        return []


def duplicates(where: str, ids: list[Any]) -> list[str]:
    return [f"{where}: duplicate {i}" for i in sorted({i for i in ids if ids.count(i) > 1}, key=str)]


def validate(files: Iterable[TaskFile]) -> list[str]:
    files = list(files)
    known = set().union(*(f.defined_ids() for f in files))
    questions = {q: s for f in files for q, s in f.questions().items()}
    return [p for f in files for p in f.problems(known, questions)]


def exit_problems(files: Iterable[TaskFile], state: dict[str, Any], guard: str) -> list[str]:
    return [p for f in files for p in f.exit_problems(state, guard)]
