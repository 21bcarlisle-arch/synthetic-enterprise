#!/usr/bin/env python3
"""The floor under the size-term contrast: the same seed, both beliefs, and the PAIRED difference.

REUSE: tools/size_term_paired_floor.py
CLASS: PATTERN-REUSE
INDEX: searched "noise floor", "floor", "seed", "spread", "paired", "contrast", "size", "arm",
       "ab", "redraw". `tools/run_value_cycle_ab.noise_floor` is the pattern taken WHOLE and the
       machinery is IMPORTED rather than copied -- `_churn_roll_redraw_patch`, `CHURN_ROLL_MODULE`,
       `CHURN_ROLL_SYMBOL`, `distance_to_a_sign`, `sems_to_state_a_sign` and
       `floor_run_headroom_refusal` are all called from there, so a change to the bar or to the
       redraw stream moves this file with it and cannot leave two spellings of one rule.
       It is NOT a mode of that file for one reason that is about the subject and not about size:
       `noise_floor` measures the spread of ONE configuration's reading, and every guard in it --
       the `all`/`only`/`except` partition, the `except`-leg complement refusal, the family
       reconciliation in `fold_noise_floor_family` -- is built around families that share a
       configuration. This measures a DIFFERENCE BETWEEN two configurations at a shared seed, whose
       fail-silent shape is a different one (the rebind reaching no call site, not the roster
       matching no call site) and whose pooling rules are not the same. Folding it in would have
       put a second meaning on `seeds` inside a file whose own artefacts are pooled by that key.
       `tools/run_frozen_baseline.py` was read: it is two arms at ONE seed and states so.
       The per-leg peak is `tools/scale_probe_10k._vm_hwm_bytes` IMPORTED, not a third reading of
       `/proc/self/status`: that file already carries the reason VmHWM is the right question and a
       point-in-time VmRSS the wrong one, and two spellings of a high-water mark is how the two
       drift apart.

WHY THIS EXISTS
---------------
`fc390b918` (2026-09-23) gave the churn belief a household-size term and published the arms table
before and after it, one seed each:

    net margin advantage   14,074 -> 13,440   (-634)
    GROSS margin adv.      -9,299 -> +12,152  (+21,450)
    enterprise value        6,143 ->   7,642  (+1,499)
    bad debt               -7,508 ->      -3  (+7,505)

and refused to call the -634 a change. That refusal was right and had nothing behind it. This
supplies what it needed.

THE RULER HAS TO BE PAIRED, AND THE ONE ON DISK IS NOT. Every floor in `docs/observability/`
measures the spread of `value_advantage_gbp` across seeds WITHIN one configuration -- the marginal
noise on a single reading, 1,457-3,453 GBP of standard deviation across the `all`-mode families.
The -634 is a difference of two readings taken at the SAME seed, and whatever seed noise those two
readings share cancels out of it. Grading a paired contrast against a marginal spread is the wrong
ruler and it under-claims: it would call 634 unresolvable by arithmetic that never looked at the
pairing. So this takes the same seed list through both configurations and reports the spread of the
per-seed DIFFERENCE.

THE ONE VARIABLE, AND WHY IT IS NOT TWO TREES. `SIZE_REFERENCE_KWH_ELEC` and `SIZE_REFERENCE_KWH_GAS`
are rebound to 0.0, which drives `estimate_churn_probability`'s guard

    if segment == "resi" and annual_consumption_kwh > 0 and size_reference_kwh > 0:

to its `else` branch and hands every household `size_scale = 1.0` -- which IS blind, and is what the
pre-`fc390b918` tree computed. The published comparison moved a whole commit; this moves two floats,
at one tree, with one `producing_commit` for both legs.

THE REBIND MUST BE OBSERVED TO BITE, PER LEG, OR THIS RAISES. The references are rebound to a float
subclass that counts its own `>` comparisons and records the ratios taken against it. Because the
guard short-circuits, a counted comparison is EXACTLY a call at which the size term would have
applied. Zero of them on the blind leg means the rebind reached no call site, both legs ran the same
world, and the "floor" would read zero -- the most flattering answer available and a measurement of
nothing. Fewer than two distinct scales on the seeing leg means the belief is flat across this book
and there is no contrast to floor. Both refuse.

THE WITNESS IS INSIDE THE MECHANISM AND NOT A WRAPPER, and that is load-bearing rather than tidy.
Five modules bind `estimate_churn_probability` with `from ... import`, so a counter wrapped around
the module attribute would miss them and read zero for the flattering reason -- the defect wearing
the shape of the guard that is supposed to catch it.

WHY `churn_roll` AND NOT `elasticity`. The re-drawn quantity is the renewal dice every billing
account takes, priced or not, keyed `Random("floor{seed}_{account}_{term}")`. Two properties, and
the second is the whole design: every account HAS one (the elasticity draw sits behind an offered
rate and only priced households reach it), and the key is per-(account, term) rather than positional,
so the same account at the same term gets the SAME roll under both configurations. That is common
random numbers, and it is what can make the paired difference tighter than the marginal spread
rather than merely a second name for it. Whether it actually does is a question this run answers and
does not assume -- the size term changes the belief, which changes prices, which changes who stays,
so the two legs' books diverge downstream and the cancellation may be destroyed. The artefact
publishes `pairing_bought` for exactly that reason.

WHAT IT REFUSES TO DO. It states no verdict on a row whose family is too small to earn one, and the
bar is `t(n-1)` through `run_value_cycle_ab.distance_to_a_sign`, never a constant. An unresolvable
row is published as unresolvable; it is not a cue to draw until a seed agrees (R12).

ONE LEG PER PROCESS, AND WHY THAT IS THE SHAPE RATHER THAN ONE PAIR. The first run of this tool ran
the whole family -- both configurations, every seed -- in a single process, peaked at 7,878 MB, and
was OOM-killed at 1h 26m having written NOTHING. Two separate things were wrong with that shape and
only one of them is the seeds. A pair holds BOTH configurations' retained state at once, which is
the 1,478 MB by which `PAIRED_FLOOR_RUN_PEAK_MB` exceeds a single-configuration
`FLOOR_RUN_PEAK_MB`; so running one PAIR per process would still carry two worlds and cap the peak
at nothing lower than what already died. The unit that caps the peak at ONE configuration's is the
LEG, so the leg is the unit this spawns.

Each leg runs in its own process, writes a shard, and exits -- so the peak is one leg's, an OOM
costs ONE leg rather than the family, and a killed run leaves every completed leg on disk to be
resumed rather than re-run. The orchestrator holds no simulation state at all: it spawns, waits,
reads shards, and rebuilds the whole artefact from the pairs it can assemble after every pair, which
is what `run()` already did and what `build_report` needs no change to support.

WHAT A LEG'S PEAK ACTUALLY IS, MEASURED 2026-09-23 -- AND THE BOUND IT REPLACED WAS TOO LOW, NOT TOO
HIGH. This paragraph used to say the leg's peak was not established, that the only number in hand
was the 7,878 MB the PAIR reached, and that since a leg is contained in the pair that ran it, that
figure was a sound UPPER BOUND and an unknown OVERestimate. The containment step is valid; its input
was not. 7,878 was the MemoryPeak of a pair the OOM killer took at 1h 26m, so that pair never
reached its own peak and 7,878 was a FLOOR on its requirement -- which bounds nothing from above.
Four legs have now run to completion and recorded their own `VmHWM`: 7,989.7, 8,094.1, 8,291.8 and
8,280.6 MB. Every one of them EXCEEDS the bound they were admitted against, by up to 491.8 MB, in
the direction that OOM-kills. `PAIRED_FLOOR_LEG_PEAK_MB` is now 8,400 -- measured, and set from the
cgroup's 8,361.1 MB rather than the leg's 8,291.8 because the cgroup is what does the killing and
the orchestrator shares it. The correction is kept beside the claim it replaces because the shape --
a conservative-sounding bound derived from a truncated measurement -- is the reusable lesson, and it
read exactly like caution.

Run:  python3 -m tools.size_term_paired_floor --seeds 5101,5102,5103,5104,5105
      python3 -m tools.size_term_paired_floor --report docs/observability/<artefact>.json
      python3 -m tools.size_term_paired_floor --leg-only 5101 --configuration blind   (one process)
"""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from tools.run_value_cycle_ab import (
    CHURN_ROLL_MODULE,
    CHURN_ROLL_SYMBOL,
    PAIRED_FLOOR_LEG_PEAK_MB,
    PROJECT_DIR,
    _churn_roll_redraw_patch,
    distance_to_a_sign,
    floor_run_headroom_refusal,
    run_value_cycle_ab,
)
from tools.scale_probe_10k import _vm_hwm_bytes

CHURN_MODEL_MODULE = "company.crm.churn_model"

#: The two names the blind leg rebinds. Both, not one: a run whose gas leg still scaled and whose
#: electricity leg did not would be a THIRD configuration wearing the blind label.
SIZE_REFERENCE_NAMES = ("SIZE_REFERENCE_KWH_ELEC", "SIZE_REFERENCE_KWH_GAS")

#: The rows of `realised_delta` this floors. All of them, because the published table is all of
#: them: a floor under the headline alone would leave the composition claim -- the 21,450 gross
#: margin swing that is the commit's actual finding -- standing on the same single seed the headline
#: was withdrawn for.
DELTA_ROWS = (
    "net_margin_gbp",
    "gross_margin_gbp",
    "enterprise_value_gbp",
    "bad_debt_gbp",
    "accounts_at_end",
    "churned_accounts",
)

#: What `fc390b918` published, at one seed, for the rows it tabulated. Carried here so the artefact
#: can set the floor against the claim rather than leaving a reader to fetch the commit. These are
#: the MOVE (seeing minus blind), which is the quantity this floors.
PUBLISHED_ONE_SEED_MOVE_GBP = {
    "net_margin_gbp": -634.0,
    "gross_margin_gbp": 21450.0,
    "enterprise_value_gbp": 1499.0,
    "bad_debt_gbp": 7505.0,
}

OUTPUT_PATH = PROJECT_DIR / "docs" / "observability" / "value_cycle_size_term_paired_floor.json"


class _WitnessedReference(float):
    """A reference consumption that counts the calls at which the size term reached it.

    `estimate_churn_probability` asks `size_reference_kwh > 0` only AFTER `segment == "resi"` and
    `annual_consumption_kwh > 0` have both held, so a counted comparison is exactly a call at which
    the size term applies under the seeing configuration and would have applied under the blind one.
    That short-circuit is what makes a `__gt__` counter a census of the term's reach rather than a
    census of every churn estimate this run took.

    `__rtruediv__` records the ratio so the seeing leg can show the belief actually VARIES across
    the book. A term that reached 400 call sites and returned the same scale at all of them is flat
    in everything but name, and the contrast it produces is zero for a reason no seed count fixes.
    It returns a plain `float` so nothing downstream carries this type.
    """

    def __new__(cls, value: float, tally: dict):
        obj = float.__new__(cls, value)
        obj._tally = tally
        return obj

    def __gt__(self, other):
        self._tally["reached"] += 1
        return float(self) > other

    def __rtruediv__(self, other):
        ratio = other / float(self)
        self._tally["scales"].add(round(ratio, 6))
        return ratio


def _install_references(module, blind: bool, originals: dict) -> dict:
    """Bind the witnessed references for one leg and hand back its tally.

    The blind leg's references are 0.0, which is not a magic number: it is the value that makes the
    guard above false, and the guard's `else` branch is the documented "unknown consumption gets the
    unscaled response" path that the pre-size-term code took for every household.
    """
    tally = {"reached": 0, "scales": set()}
    for name in SIZE_REFERENCE_NAMES:
        setattr(module, name, _WitnessedReference(0.0 if blind else originals[name], tally))
    return tally


def _restore_references(module, originals: dict) -> None:
    for name in SIZE_REFERENCE_NAMES:
        setattr(module, name, originals[name])


def _assert_the_variable_bit(seed: int | None, blind: bool, tally: dict, calls: dict) -> None:
    """THE WITNESS, BOTH DIRECTIONS, BEFORE ANY NUMBER LEAVES A LEG.

    Both directions because one is not enough. A leg where the rebind reached nothing produces a
    spread of ZERO and reads as a perfectly resolved contrast; a leg where the rebind reached only
    half the fuels produces a healthy NON-zero spread and reads as a clean one. A guard on either
    alone passes the other, and only one of the two looks broken.
    """
    if tally["reached"] == 0:
        raise AssertionError(
            "{} leg at seed {}: the rebound size references were never compared, so the size term "
            "reached NO call site this pass and the blind and seeing legs ran the same world. Their "
            "difference would be zero by construction -- the most flattering answer available and a "
            "measurement of nothing. Re-resolve `{}.{}` before trusting any figure here.".format(
                "blind" if blind else "seeing", seed, CHURN_MODEL_MODULE, SIZE_REFERENCE_NAMES[0]))
    if blind and tally["scales"]:
        raise AssertionError(
            "blind leg at seed {}: {} scale ratio(s) were taken against a reference that is "
            "supposed to be zero, so this leg is not blind. It is a third configuration wearing "
            "the blind label.".format(seed, len(tally["scales"])))
    if not blind and len(tally["scales"]) < 2:
        raise AssertionError(
            "seeing leg at seed {}: the size term returned {} distinct scale(s) over {} reached "
            "call(s). A belief that is flat across the book is blind in everything but name, and "
            "the contrast this floors would be zero for a reason no seed count fixes.".format(
                seed, len(tally["scales"]), tally["reached"]))
    if seed is not None and calls["redrawn"] == 0:
        raise AssertionError(
            "{} leg at seed {}: the churn-roll patch re-rolled NO account over {} call(s), so this "
            "seed ran the base world and its contribution to the spread is zero by construction."
            .format("blind" if blind else "seeing", seed, calls["n"]))


def _one_leg(seed: int | None, blind: bool, report_end: str | None, runner) -> dict:
    """One configuration, one seed, one pass -- with both witnesses asserted before it returns.

    `seed is None` is the RECONCILIATION leg: the production roll, nothing re-drawn. It is the only
    reading directly comparable to the numbers `fc390b918` published, and it runs before any seed
    for that reason -- a rebind that does not reproduce the published blind figure is not the switch
    the commit made, and every paired difference after it would be floor-ing a different contrast.
    """
    churn = importlib.import_module(CHURN_MODEL_MODULE)
    originals = {name: float(getattr(churn, name)) for name in SIZE_REFERENCE_NAMES}
    draw = importlib.import_module(CHURN_ROLL_MODULE)
    real_roll = getattr(draw, CHURN_ROLL_SYMBOL, None)
    if real_roll is None:
        raise AssertionError(
            "`{}` has no attribute `{}` to re-roll. Refusing to run: a floor that silently stopped "
            "re-drawing would return two identical worlds and a spread of zero.".format(
                CHURN_ROLL_MODULE, CHURN_ROLL_SYMBOL))

    calls = {"n": 0, "redrawn": 0, "held": 0, "ids": set()}
    tally = _install_references(churn, blind, originals)
    patched = (_churn_roll_redraw_patch(real_roll, int(seed), lambda _cid: True, calls)
               if seed is not None else None)
    if patched is not None:
        setattr(draw, CHURN_ROLL_SYMBOL, patched)
    started = time.monotonic()
    try:
        result = runner(report_end)
    finally:
        if patched is not None:
            setattr(draw, CHURN_ROLL_SYMBOL, real_roll)
        _restore_references(churn, originals)
    elapsed = time.monotonic() - started

    _assert_the_variable_bit(seed, blind, tally, calls)

    delta = dict(result.get("realised_delta") or {})
    funnel = ((result.get("renewal_funnel") or {}).get("value_arm") or {})
    priced = [a for a in (funnel.get("accounts_the_arm_priced") or []) if isinstance(a, str)]
    return {
        "seed": seed,
        "configuration": "blind" if blind else "seeing",
        "elapsed_s": round(elapsed, 1),
        #: THIS PROCESS'S HIGH-WATER MARK, WHICH IS THE POINT OF RUNNING ONE LEG IN IT. This is the
        #: reading that replaced the admission price with a measurement on 2026-09-23 -- and it
        #: raised it, because the bound it replaced came from an OOM-killed pair that never reached
        #: its own peak (see `PAIRED_FLOOR_LEG_PEAK_MB`). In the in-process test path it is the
        #: harness's own footprint and means nothing, which is why it is published per leg beside
        #: the leg's elapsed time rather than folded into a single family-level number.
        "peak_rss_mb": round(_vm_hwm_bytes() / (1024 * 1024), 1),
        "realised_delta": {row: delta.get(row) for row in DELTA_ROWS},
        "accounts_the_arm_priced": len(priced),
        "size_term_reached_calls": tally["reached"],
        "size_term_distinct_scales": len(tally["scales"]),
        "size_term_scale_range": ([min(tally["scales"]), max(tally["scales"])]
                                  if tally["scales"] else None),
        "churn_rolls": calls["n"],
        "churn_rolls_redrawn": calls["redrawn"],
        "accounts_rerolled": len(calls["ids"]),
        "book_identity": (result.get("book_identity") or {}).get("control_arm"),
    }


def _leg_name(seed: int | None, blind: bool) -> str:
    """The shard's identity, and it is keyed by BOTH coordinates on purpose.

    A shard named for its seed alone would have the blind and seeing legs of one seed overwrite each
    other, and the pair assembled from it would be a leg differenced against ITSELF -- every row
    exactly zero, the flattering answer, arrived at by measuring nothing. That is the same
    fail-silent shape `_assert_the_variable_bit` exists for, reached through the filesystem instead
    of through the rebind, so it is keyed out here rather than guarded downstream.
    """
    return "{}_{}".format("base" if seed is None else seed, "blind" if blind else "seeing")


def _shard_path(leg_dir: Path, seed: int | None, blind: bool) -> Path:
    return leg_dir / "leg_{}.json".format(_leg_name(seed, blind))


def leg_dir_for(out: Path) -> Path:
    """Derived from the artefact, never a constant: the tests' `tmp_path` isolation depends on it."""
    return out.parent / "{}_legs".format(out.stem)


def run_leg_to_shard(seed: int | None, blind: bool, report_end: str | None, leg_dir: Path,
                     runner=None) -> dict:
    """Run ONE leg in THIS process, write its shard, return it. The unit a process is spawned for."""
    runner = runner or (lambda report_end: run_value_cycle_ab(report_end=report_end,
                                                              level_arm=False))
    leg = _one_leg(seed, blind, report_end, runner)
    leg_dir.mkdir(parents=True, exist_ok=True)
    path = _shard_path(leg_dir, seed, blind)
    path.write_text(json.dumps(leg, indent=2, default=str), encoding="utf-8")
    return leg


def _spawn_leg(seed: int | None, blind: bool, report_end: str | None, leg_dir: Path) -> None:
    """Run one leg in a CHILD PROCESS and wait for it, so its peak dies with it.

    Blocking, and deliberately not a detached session or a transient unit: the orchestrator must
    stay the thing that knows whether a leg finished, and a leg that outlived its parent would be
    invisible to the headroom census the next leg runs. `tools/launch_shape_census` reads this
    shape and it is not a launch.
    """
    argv = [sys.executable, "-m", "tools.size_term_paired_floor",
            "--leg-only", "base" if seed is None else str(seed),
            "--configuration", "blind" if blind else "seeing",
            "--leg-dir", str(leg_dir)]
    if report_end:
        argv += ["--end-year", report_end.split("-")[0]]
    completed = subprocess.run(argv, cwd=PROJECT_DIR, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            "the {} leg at seed {} exited {}. Its shard was NOT written, so this pair is absent "
            "from the artefact rather than wrong in it; every leg already on disk is still usable "
            "and re-running this command resumes from them.".format(
                "blind" if blind else "seeing", seed, completed.returncode))


def _load_leg(leg_dir: Path, seed: int | None, blind: bool) -> dict | None:
    path = _shard_path(leg_dir, seed, blind)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _pair(seed: int | None, report_end: str | None, runner, leg_dir: Path,
          leg_executor=None) -> dict:
    """Both legs at ONE seed, blind first, and the per-row difference between them.

    Blind first on purpose: it is the leg whose witness can only refuse (`scales` must be empty), so
    a rebind that failed to take costs one pass to find out rather than two.

    A leg whose shard is already on disk is NOT re-run. That is what makes a killed family resumable
    rather than repeatable, and it is the only reason writing shards buys anything over holding the
    legs in memory.
    """
    legs = {}
    for blind in (True, False):
        existing = _load_leg(leg_dir, seed, blind)
        if existing is None:
            leg_executor(seed, blind, report_end, leg_dir)
            existing = _load_leg(leg_dir, seed, blind)
            if existing is None:
                raise RuntimeError(
                    "the {} leg at seed {} reported success and left no shard at {}. Refusing to "
                    "assemble a pair from a leg that did not write.".format(
                        "blind" if blind else "seeing", seed, _shard_path(leg_dir, seed, blind)))
        legs[blind] = existing
    blind, seeing = legs[True], legs[False]
    differences = {}
    for row in DELTA_ROWS:
        b, s = blind["realised_delta"].get(row), seeing["realised_delta"].get(row)
        differences[row] = None if (b is None or s is None) else (s - b)
    return {
        "seed": seed,
        "blind": blind,
        "seeing": seeing,
        "difference_seeing_minus_blind": differences,
        #: NOT A REFUSAL. The two legs' books are EXPECTED to diverge -- the size term changes the
        #: belief, which changes prices, which changes who stays -- and a run that forced them to
        #: agree would have switched nothing. It is recorded because it is the direct measure of how
        #: much common randomness survives the arm's own feedback, which is the whole question
        #: behind whether pairing buys anything here.
        "books_agree": blind["book_identity"] == seeing["book_identity"],
        "priced_move": seeing["accounts_the_arm_priced"] - blind["accounts_the_arm_priced"],
    }


def summarise(pairs: list[dict]) -> dict:
    """Per row: the paired mean, its spread, and the bar this family's own size earns.

    `distance_to_a_sign` is imported rather than re-derived, so the bar here is the same `t(n-1)`
    every other floor in this repository is graded at and cannot drift away from it.
    """
    seeded = [p for p in pairs if p["seed"] is not None]
    rows = {}
    for row in DELTA_ROWS:
        values = [p["difference_seeing_minus_blind"].get(row) for p in seeded]
        values = [v for v in values if v is not None]
        n = len(values)
        if n < 2:
            rows[row] = {
                "n": n,
                "unavailable_because": (
                    "a spread needs at least two paired seeds; this family has {}. One pair is a "
                    "reading, not a floor, and reporting it would restate the very single-seed "
                    "figure this run exists to put a bound under.".format(n)),
            }
            continue
        mean = sum(values) / n
        stdev = (sum((v - mean) ** 2 for v in values) / (n - 1)) ** 0.5
        verdict = distance_to_a_sign(mean, stdev, n)
        positives = sum(1 for v in values if v > 0)
        published = PUBLISHED_ONE_SEED_MOVE_GBP.get(row)
        rows[row] = {
            "n": n,
            "paired_mean": mean,
            "paired_stdev": stdev,
            "paired_sem": stdev / (n ** 0.5),
            "min": min(values),
            "max": max(values),
            "seeds_positive": positives,
            "seeds_negative": n - positives,
            #: THE SIGN STABILITY IS PUBLISHED BESIDE THE VERDICT AND IS NOT THE SAME QUESTION. A
            #: family can fail to state a sign while every seed agrees on one (a small mean with a
            #: tiny sd still fails at small n), and it can state one while a third of its seeds
            #: disagree. A reader deciding whether to act on the move wants both.
            "sign_is_unanimous": positives in (0, n),
            "distance_to_a_sign": verdict,
            "published_one_seed_move": published,
            #: WHERE THE PUBLISHED SINGLE READING SITS IN THIS FAMILY'S OWN SPREAD. Not a p-value
            #: and not a verdict on the published figure -- it is the answer to "was that one seed
            #: a typical draw", which is the question the -634 actually raised.
            "published_move_in_sems": (
                None if (published is None or stdev == 0)
                else (published - mean) / (stdev / (n ** 0.5))),
        }
    return rows


def _pairing_bought(pairs: list[dict], rows: dict) -> dict:
    """Did common random numbers survive the arm's own feedback, per row -- measured, not assumed.

    The claim pairing rests on is that `sd(seeing - blind)` is SMALLER than `sqrt(2) * sd(leg)`, the
    value it would take if the two legs' noise were independent. If it is not smaller, the pairing
    that made the published comparison look like a clean one-variable read did not survive the size
    term's own downstream effect on who stays, and no seed budget closes a 634 GBP move.

    Both leg spreads are computed from THIS family rather than from the artefacts on disk, because
    those were drawn on a different redraw key and a different tree and their sd is not this
    instrument's.
    """
    seeded = [p for p in pairs if p["seed"] is not None]
    out = {}
    for row in DELTA_ROWS:
        legs = []
        for side in ("blind", "seeing"):
            values = [p[side]["realised_delta"].get(row) for p in seeded]
            values = [v for v in values if v is not None]
            if len(values) < 2:
                legs = []
                break
            mean = sum(values) / len(values)
            legs.append((sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** 0.5)
        summary = rows.get(row) or {}
        paired_sd = summary.get("paired_stdev")
        if not legs or paired_sd is None:
            out[row] = {"unavailable_because": "fewer than two paired seeds carry this row"}
            continue
        independent = ((legs[0] ** 2 + legs[1] ** 2) ** 0.5)
        out[row] = {
            "blind_leg_stdev": legs[0],
            "seeing_leg_stdev": legs[1],
            "stdev_if_the_legs_were_independent": independent,
            "paired_stdev": paired_sd,
            "ratio_paired_to_independent": (None if independent == 0 else paired_sd / independent),
            "pairing_reduced_the_spread": (independent > 0 and paired_sd < independent),
        }
    return out


def _producing_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_DIR,
                              capture_output=True, text=True, timeout=30).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def build_report(pairs: list[dict], report_end: str | None, commit: str | None) -> dict:
    rows = summarise(pairs)
    return {
        "what_this_is": (
            "The floor under the size-term contrast. The same churn-roll seed is taken through the "
            "belief BLIND to household size and the belief SEEING it, and the spread reported is "
            "the spread of the per-seed DIFFERENCE. It is not comparable to the `value_advantage` "
            "spreads in the noise-floor artefacts: those are the marginal noise on one reading and "
            "this is the noise on a paired contrast."),
        "how_to_read_this": (
            "Read `distance_to_a_sign` per row, not the mean. A row that cannot state a sign says "
            "this book cannot resolve that move -- including, if it comes to it, the gross-margin "
            "swing the size-term commit's finding rests on. `pairing_bought` says whether the "
            "shared seed actually cancelled anything: if `pairing_reduced_the_spread` is false, the "
            "two legs' worlds diverged far enough downstream that the pairing is decorative and the "
            "marginal spread is the honest bound."),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "producing_commit": commit,
        "report_end": report_end,
        "the_one_variable": {
            "names_rebound": list(SIZE_REFERENCE_NAMES),
            "module": CHURN_MODEL_MODULE,
            "blind_value": 0.0,
            "why_zero": (
                "it drives `estimate_churn_probability`'s `size_reference_kwh > 0` guard false, "
                "which is the documented path every household took before fc390b918"),
            "redraw_key": "churn_roll",
            "redraw_symbol": "{}.{}".format(CHURN_ROLL_MODULE, CHURN_ROLL_SYMBOL),
            "both_legs_are_one_tree": True,
        },
        "reconciliation_leg": next((p for p in pairs if p["seed"] is None), None),
        "seeds": [p for p in pairs if p["seed"] is not None],
        "paired_difference": rows,
        "pairing_bought": _pairing_bought(pairs, rows),
        #: WHAT A LEG ACTUALLY COST, which is the quantity `PAIRED_FLOOR_LEG_PEAK_MB` is currently
        #: only BOUNDED by. Published as the observed max across legs so the next session can
        #: replace that bound with a measurement rather than inherit an overestimate. `None` while
        #: no leg has recorded one -- an honest gap, not a zero.
        "leg_peak_rss_mb": _observed_leg_peak(pairs),
    }


def _observed_leg_peak(pairs: list[dict]) -> dict:
    peaks = [leg["peak_rss_mb"] for p in pairs for leg in (p["blind"], p["seeing"])
             if leg.get("peak_rss_mb") is not None]
    observed_max = max(peaks) if peaks else None
    #: THE READING IS TWO-DIRECTIONAL, AND THAT IS THE DEFECT THIS CARRIES A SCAR FROM. Until
    #: 2026-09-23 it said only that a materially-lower observation meant the bound was loose and
    #: should be LOWERED. It had no sentence for the case that occurred -- every leg coming in
    #: ABOVE the price it was admitted against -- so the instrument built to replace the bound was
    #: structurally unable to report the one answer that mattered, and a field that cannot express
    #: an outcome agrees with every other one. `exceeds_admission_price` is the leg that can fail.
    exceeds = (observed_max is not None and observed_max > PAIRED_FLOOR_LEG_PEAK_MB)
    return {
        "admission_price_used_mb": PAIRED_FLOOR_LEG_PEAK_MB,
        "observed_max_mb": observed_max,
        "observed_min_mb": min(peaks) if peaks else None,
        "legs_weighed": len(peaks),
        "exceeds_admission_price": exceeds if peaks else None,
        "verdict": (
            "NO LEG WEIGHED -- an honest gap, not a zero" if not peaks else
            "UNDER-PRICED: a leg reached {:.1f} MB against an admission price of {:.1f}. The guard "
            "is admitting legs this machine may not hold, which is the direction that OOM-kills, "
            "and `PAIRED_FLOOR_LEG_PEAK_MB` must be RAISED past the cgroup peak of the unit that "
            "ran them -- not past this figure, which omits the orchestrator sharing that cgroup."
            .format(observed_max, PAIRED_FLOOR_LEG_PEAK_MB) if exceeds else
            "LOOSE: no leg came within 10% of the {:.1f} MB admission price, so it refuses runs "
            "this machine would have finished and should be lowered to the measurement."
            .format(PAIRED_FLOOR_LEG_PEAK_MB) if observed_max < 0.9 * PAIRED_FLOOR_LEG_PEAK_MB else
            "PRICED: the admission price sits above every leg weighed and within 10% of the "
            "largest, so it neither admits a leg it cannot hold nor refuses one it could."),
        "how_to_read_this": (
            "`admission_price_used_mb` is `PAIRED_FLOOR_LEG_PEAK_MB`, the price a leg is admitted "
            "at. Read `verdict`, not the numbers: it is stated over ALL THREE states because the "
            "first version of this field could only say 'loose', which is not what happened. "
            "`legs_weighed` bounds all of it -- these are the legs on disk, not the family. These "
            "figures are meaningless for legs run in-process by a test harness."),
    }


def run(seeds: list[int], report_end: str | None = None, out: Path = OUTPUT_PATH,
        runner=None, include_reconciliation: bool = True, leg_dir: Path | None = None,
        leg_executor=None) -> dict:
    """Orchestrate the family, writing the artefact after EVERY pair. Runs NO leg in this process.

    Incremental on purpose. A floor leg on this machine runs for hours and the recorded failure mode
    is an OOM kill that writes nothing and reads exactly like a run still going. A partial family on
    disk is a usable family; a killed whole one is nothing at all.

    THE FORK ON `runner` IS REAL AND IS NOT A TEST BACKDOOR. With no runner this spawns one CHILD
    PROCESS PER LEG, which is the production shape and the whole point of the file: the peak dies
    with the child. A test cannot afford three decade passes per leg, so an injected `runner` runs
    the legs in-process instead -- exercising the same shards, the same resume, the same assembly,
    with only the process boundary stubbed. That boundary is controlled separately by asserting the
    argv `_spawn_leg` builds, because a control that stubbed the spawn AND checked the spawn would
    be proving the stub.
    """
    leg_dir = leg_dir if leg_dir is not None else leg_dir_for(out)
    if leg_executor is None:
        leg_executor = (
            _spawn_leg if runner is None
            else (lambda s, b, re_, ld: run_leg_to_shard(s, b, re_, ld, runner=runner)))
    commit = _producing_commit()
    out.parent.mkdir(parents=True, exist_ok=True)
    pairs: list[dict] = []
    todo: list[int | None] = ([None] if include_reconciliation else []) + list(seeds)
    for index, seed in enumerate(todo, start=1):
        pairs.append(_pair(seed, report_end, runner, leg_dir, leg_executor))
        report = build_report(pairs, report_end, commit)
        out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        latest = pairs[-1]
        print("[size_term_paired_floor] {}/{} seed={} d_net={} d_gross={} books_agree={} "
              "wrote {}".format(
                  index, len(todo), seed,
                  _fmt(latest["difference_seeing_minus_blind"].get("net_margin_gbp")),
                  _fmt(latest["difference_seeing_minus_blind"].get("gross_margin_gbp")),
                  latest["books_agree"], out), flush=True)
    return build_report(pairs, report_end, commit)


def _fmt(value) -> str:
    return "n/a" if value is None else "{:+,.0f}".format(value)


def print_report(report: dict) -> None:
    print("size-term paired floor -- {} seed pair(s), {} window".format(
        len(report.get("seeds") or []), report.get("report_end") or "full"))
    reconciliation = report.get("reconciliation_leg")
    if reconciliation:
        print("  reconciliation (production roll, nothing re-drawn):")
        for row in ("net_margin_gbp", "gross_margin_gbp"):
            print("    {:<22} blind {:>12} seeing {:>12} move {:>12}".format(
                row,
                _fmt(reconciliation["blind"]["realised_delta"].get(row)),
                _fmt(reconciliation["seeing"]["realised_delta"].get(row)),
                _fmt(reconciliation["difference_seeing_minus_blind"].get(row))))
    for row, summary in (report.get("paired_difference") or {}).items():
        if summary.get("unavailable_because"):
            print("  {:<22} {}".format(row, summary["unavailable_because"]))
            continue
        verdict = summary.get("distance_to_a_sign") or {}
        bought = (report.get("pairing_bought") or {}).get(row) or {}
        print("  {:<22} mean {:>12} sd {:>12} n={:<3} sems {:>6} bar {:>6} sign: {:<3} "
              "unanimous={} paired<independent={}".format(
                  row, _fmt(summary["paired_mean"]), _fmt(summary["paired_stdev"]), summary["n"],
                  _round(verdict.get("sems_from_zero")), _round(verdict.get("sems_needed")),
                  "yes" if verdict.get("distinguishable") else "NO",
                  summary.get("sign_is_unanimous"), bought.get("pairing_reduced_the_spread")))


def _round(value) -> str:
    return "n/a" if value is None else "{:.2f}".format(value)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", help="comma-separated churn-roll seeds, e.g. 5101,5102,5103")
    ap.add_argument("--end-year", help="truncate the window, e.g. 2019 (a DIFFERENT instrument: "
                                       "the published move is a full-window figure)")
    ap.add_argument("--out", type=Path, default=OUTPUT_PATH)
    ap.add_argument("--leg-dir", type=Path,
                    help="where per-leg shards live; defaults beside --out. A leg already "
                         "sharded here is NOT re-run, which is how a killed family resumes.")
    ap.add_argument("--leg-only", metavar="SEED|base",
                    help="LEG MODE: run exactly ONE leg in this process, write its shard and "
                         "exit. This is what the orchestrator spawns, and what caps the peak at "
                         "one configuration's. `base` is the reconciliation leg.")
    ap.add_argument("--configuration", choices=("blind", "seeing"),
                    help="which configuration --leg-only runs")
    ap.add_argument("--report", type=Path,
                    help="REPORT mode: re-print an artefact already on disk. Runs nothing.")
    ap.add_argument("--no-reconciliation", action="store_true",
                    help="skip the production-roll leg. Only for a continuation run whose "
                         "reconciliation is already on disk -- it is the only leg comparable to "
                         "the figures fc390b918 published.")
    ap.add_argument("--ignore-headroom", action="store_true",
                    help="start even when this machine cannot be shown to hold the measured peak")
    args = ap.parse_args(argv)

    if args.report:
        print_report(json.loads(args.report.read_text(encoding="utf-8")))
        return 0

    report_end = f"{args.end_year}-12-31" if args.end_year else None
    leg_dir = args.leg_dir if args.leg_dir is not None else leg_dir_for(args.out)

    if args.leg_only:
        if not args.configuration:
            ap.error("--configuration is required with --leg-only: a leg that did not say which "
                     "belief it ran cannot be paired with anything")
        # THE LEG IS WHAT COSTS, so the leg is what is priced -- and it is re-asked here, in the
        # child, rather than inherited from the parent's check. A leg admitted an hour ago against
        # an idle guest is not admitted now if another family started beside it.
        refusal = floor_run_headroom_refusal(own_peak_mb=PAIRED_FLOOR_LEG_PEAK_MB)
        if refusal and not args.ignore_headroom:
            print("size-term paired floor leg REFUSED -- {}".format(refusal))
            return 2
        seed = None if args.leg_only == "base" else int(args.leg_only)
        leg = run_leg_to_shard(seed, args.configuration == "blind", report_end, leg_dir)
        print("[size_term_paired_floor] leg seed={} {} elapsed={}s peak_rss={} MB wrote {}".format(
            seed, leg["configuration"], leg["elapsed_s"], leg["peak_rss_mb"],
            _shard_path(leg_dir, seed, args.configuration == "blind")), flush=True)
        return 0

    if not args.seeds:
        ap.error("--seeds is required unless --report or --leg-only is given")
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    if len(seeds) < 2:
        raise SystemExit(
            "a paired floor needs at least two seeds; got {}. One pair is a reading, not a "
            "spread, and it would restate the single-seed figure this exists to bound."
            .format(len(seeds)))

    # NO HEADROOM CHECK HERE, AND THAT IS THE CHANGE RATHER THAN AN OMISSION. This process now
    # spawns legs and holds no simulation state, so pricing it at a floor leg's peak would charge
    # the guest twice for one leg -- the orchestrator at 7,800 MB and its own child at 7,800 MB --
    # and refuse a family this machine can comfortably hold. Each leg re-asks the question for
    # itself in `--leg-only` above, immediately before it is the thing spending the memory, which
    # is also the only place that can see a rival leg that started since the family began.
    report = run(seeds, report_end=report_end, out=args.out, leg_dir=leg_dir,
                 include_reconciliation=not args.no_reconciliation)
    print_report(report)
    print("  wrote {}".format(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
