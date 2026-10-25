"""A run on run_output_latest.json is always named by a run_complete marker.

The defect: on 25 Oct a hand-launched full run was copied onto latest by hand, no marker named it,
and every publish route -- the publisher, the held-run offer, the re-arm -- requires latest to equal
a marker's `JSON:` file, so the run was invisible to all of them. `sim_runner.promote_run` is now the
one writer of latest and writes the marker in the same call; `--promote` is the door for a run made
outside the loop. Each test names the defect it catches.
"""
import filecmp
from pathlib import Path

import pytest

from background import sim_runner

HEADER = '{"generated_at":"2026-10-25T13:31:26Z","producing_commit":{"commit":"b2bc3d8da5","resolved_at":"x"}}'


def _json_line(marker: Path) -> Path:
    # Parsed as background_worker.held_marker_to_offer parses it.
    return next(Path(line[6:].strip()) for line in marker.read_text().splitlines()
                if line.startswith("JSON: "))


def _run(tmp_path, name="run_output_b2bc3d8da5_20261025T1230Z.json", body=HEADER):
    reports = tmp_path / "reports"
    reports.mkdir(exist_ok=True)
    run = reports / name
    run.write_text(body)
    return reports, run


def test_a_hand_promoted_run_puts_latest_and_a_marker_naming_it(tmp_path):
    """Catches: promoting by hand writes latest with no marker (the 25 Oct state), or a marker whose
    JSON line or Git line is not the run's -- the held-run offer would then refuse it as a mix."""
    reports, run = _run(tmp_path)
    marker = sim_runner.promote_by_hand(run, reports_dir=reports, staging_dir=tmp_path / "staging")
    assert marker.parent == tmp_path / "staging" and marker.name.startswith("run_complete_")
    assert filecmp.cmp(_json_line(marker), reports / "run_output_latest.json", shallow=False)
    assert "Git: b2bc3d8da5\n" in marker.read_text()


@pytest.mark.parametrize("name,body,why", [
    ("run_output_latest.json", HEADER, "not a timestamped run_output"),
    ("run_output_x_20261025T1230Z.json", '{"generated_at":"x"}', "names no producing_commit"),
])
def test_promotion_refuses_by_name_and_leaves_latest_alone(tmp_path, name, body, why):
    """Catches: a guessed `Git:` line (the publisher's code admission reads it) or promoting latest
    onto itself; a refusal must name its reason and write nothing."""
    reports, run = _run(tmp_path, name, body)
    (reports / "run_output_latest.json").write_text(body) if name != "run_output_latest.json" else None
    before = (reports / "run_output_latest.json").read_bytes()
    with pytest.raises(SystemExit, match=why):
        sim_runner.promote_by_hand(run, reports_dir=reports, staging_dir=tmp_path / "staging")
    assert (reports / "run_output_latest.json").read_bytes() == before
    assert not (tmp_path / "staging").exists()


def test_the_loop_writes_latest_only_through_promote_run():
    """Catches: a second writer of latest growing back in sim_runner beside the one that writes the
    marker. Read from the source, because the loop shells out to a whole run."""
    src = Path(sim_runner.__file__).read_text()
    assert src.count('"run_output_latest.json").write_bytes(') == 1
    body = src[src.index("def run_simulation("):src.index("def promote_run(")]
    assert "promote_run(" in body and "write_bytes(" not in body
