"""The defect: seven modules each pinned `claude-opus-5` after the director's console moved to Opus
5.5, so every unattended turn ran on the older, dearer model and nothing noticed. `model_tier.OPUS`
is now the one place the Opus-tier model is named."""
from __future__ import annotations

import re
from pathlib import Path

from background import model_tier

BACKGROUND = Path(model_tier.__file__).parent
# worker_tick keeps a literal on purpose (its fallback for when model_tier cannot import);
# autonomous_runner is defunct and left to the mothball census.
ALLOWED = {"model_tier.py", "worker_tick.py", "autonomous_runner.py"}


def test_no_unattended_seat_names_an_opus_model_of_its_own():
    offenders = [p.name for p in sorted(BACKGROUND.glob("*.py"))
                 if p.name not in ALLOWED
                 and re.search(r'^\s*[A-Z_]*MODEL[A-Z_]*\s*=\s*"claude-opus', p.read_text(), re.M)]
    assert not offenders, f"these seats hold their own Opus model name instead of model_tier.OPUS: {offenders}"
    # Not vacuous: the scan does see the seats it governs.
    assert {"seat_executor.py", "delivery_seat.py", "worker_seat.py"} <= {p.name for p in BACKGROUND.glob("*.py")}


def test_the_tick_fallback_is_the_opus_tier():
    from background import worker_tick
    assert worker_tick.MODEL == model_tier.OPUS


def test_every_seat_reads_the_tier():
    from background import (
        build_executor,
        delivery_seat,
        director_twin,
        naive_organ,
        seat_executor,
        worker_seat,
    )
    got = {"seat_executor": seat_executor.MODEL, "delivery_seat": delivery_seat.MODEL,
           "worker_seat": worker_seat.MODEL, "build_executor": build_executor.MAIN_LOOP_MODEL,
           "naive_organ": naive_organ.ORGAN_MODEL, "director_twin": director_twin.TWIN_MODEL}
    assert set(got.values()) == {model_tier.OPUS}, got


def test_the_headless_prompts_carry_the_turn_ending_rule_and_the_attended_seat_does_not():
    from background import seat_executor, worker_tick
    assert model_tier.UNATTENDED_TURN_ENDS.strip()
    assert model_tier.UNATTENDED_TURN_ENDS in seat_executor.CHARTER
    assert model_tier.UNATTENDED_TURN_ENDS in worker_tick.WORKER_PREAMBLE
    assert worker_tick.WORKER_PREAMBLE.endswith("Drawn work follows.\n\n")
    worker_seat_src = (BACKGROUND / "worker_seat.py").read_text()
    assert "UNATTENDED_TURN_ENDS" not in worker_seat_src, "a person answers this seat; stopping to ask is right there"
