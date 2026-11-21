import json

import pytest

from layout import LAYOUTS, Layout, Side

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
