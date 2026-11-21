import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

LAYOUTS = Path(__file__).resolve().parent / "layouts"


class Side(Enum):
    LEFT = "left"
    RIGHT = "right"

    @property
    def nvim_before(self) -> bool:
        return self is Side.RIGHT


@dataclass(frozen=True)
class Layout:
    name: str
    claude_side: Side
    claude_percent: int

    @classmethod
    def from_json(cls, name: str, text: str) -> "Layout":
        claude: dict[str, Any] = json.loads(text)["tmux"]["claude"]
        return cls(name=name, claude_side=Side(claude["side"]), claude_percent=claude["percent"])

    @classmethod
    def load(cls, name: str, directory: Path = LAYOUTS) -> "Layout":
        return cls.from_json(name, (directory / f"{name}.json").read_text())

    @property
    def nvim_percent(self) -> int:
        return 100 - self.claude_percent

    @property
    def nvim_before(self) -> bool:
        return self.claude_side.nvim_before
