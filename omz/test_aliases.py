import subprocess
from pathlib import Path

import pytest

ALIASES = Path(__file__).parent / "aliases.zsh"
STUBBED = ["brew", "sudo", "claude", "gcloud"]

COMMON = ["claude update"]
DARWIN = ["brew update", "brew upgrade --no-ask"]
LINUX = ["sudo apt update", "sudo apt upgrade -y"]
GCLOUD = ["gcloud components update"]
GCLOUD_DARWIN = ["gcloud components update-macos-python"]


def run_update(tmp_path, ostype, stubs):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "log"
    for name in stubs:
        stub = bin_dir / name
        stub.write_text(f'#!/bin/sh\necho "{name} $*" >> "{log}"\n')
        stub.chmod(0o755)
    script = f"OSTYPE={ostype}; source {ALIASES}; update"
    subprocess.run(
        ["zsh", "-c", script],
        env={"PATH": f"{bin_dir}:/usr/bin:/bin"},
        check=True,
        capture_output=True,
    )
    return log.read_text().splitlines() if log.exists() else []


@pytest.mark.parametrize("has_gcloud", [True, False])
@pytest.mark.parametrize(
    "ostype,os_commands,gcloud_commands",
    [
        ("darwin24.0", DARWIN, GCLOUD + GCLOUD_DARWIN),
        ("linux-gnu", LINUX, GCLOUD),
    ],
)
def test_update(tmp_path, ostype, os_commands, gcloud_commands, has_gcloud):
    stubs = [s for s in STUBBED if has_gcloud or s != "gcloud"]
    ran = run_update(tmp_path, ostype, stubs)
    expected = os_commands + COMMON + (gcloud_commands if has_gcloud else [])
    assert ran == expected
