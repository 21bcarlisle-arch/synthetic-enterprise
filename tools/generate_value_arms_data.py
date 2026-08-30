#!/usr/bin/env python3
"""Generate site/data/value_arms.json -- the baseline the published supplier has to beat.

REUSE: tools/generate_value_arms_data.py
CLASS: CUSTOM
INDEX: searched "value arms", "value_cycle_ab", "baseline", "arm comparison", "site data
       generator". Two near neighbours, both checked and neither reusable. (1)
       `tools/run_value_cycle_ab.py` PRODUCES the artefacts this reads -- it runs the arms and
       writes `docs/observability/value_cycle_ab_*.json`; extending it to publish a site feed
       would put a reader-facing surface inside a 25-minute simulation runner, so the read side
       stays separate exactly as `generate_book_growth_data` is separate from
       `live_population._resolve_campaign`. (2) `tools/generate_dashboard_data.py` publishes the
       run's own headline figures with the R14 basis machinery, but its subject is ONE run; this
       one's subject is THREE arms of a different run, on two clocks, plus a cross-check between
       them and the published run -- a different question, and folding it in would make the
       dashboard's basis parentage gate answer for a population it does not own. The shape
       followed here is `tools/generate_book_growth_data.py`: read one observability artefact,
       author the meanings, publish an absence with its reason, ride the publish cycle.

THE DEFECT IT SERVES
--------------------
The director's thesis contains the requirement in terms: *"there has to be a BASELINE to beat --
the same book run by a supplier applying flat rules with no per-customer view -- or 'it performed
well' means nothing."* That baseline was built (`decide_margin(arm=FLAT_RULES)`), the three-arm
A/B was run on the widened world, and the answer came back: **the advantage is the LEVEL, not the
SELECTION.** On 2026-08-28 a grep for `level_share_of_advantage`, `value_cycle_ab` and
`selection_gbp` across `site/`, `tools/generate_dashboard_data.py`, `saas/reporting/` and
`docs/reports/` returned exactly one file -- `site/data/delivery.json` -- and it carried a lane
claim, not a figure.

So the site published a profitable supplier at GBP 153,245 net and said nothing about the
flat-rules run that matches it. Publishing a profitable-looking supplier while withholding the
comparison that qualifies it is the closest thing to a misleading claim this project has, and the
remedy does not need anyone's permission: the reading is labelled PROVISIONAL, which keeps it
retractable and therefore outside the four reserved classes (`background/one_way_door.py`).

WHAT IT PUBLISHES, AND ON WHICH CLOCK (R14)
-------------------------------------------
Two clocks, because the run has two and they disagree by GBP 39,962.17 -- the difference between
the flat-rate bad-debt provision frozen at the end of the settlement loop and the arrears model's
realised write-offs, which `run_phase4c_on_phase2b` writes back into the rows afterwards:

  settled-realised     summed from the world's own mutated settlement records. This is the clock
                       `run_output_latest.json` publishes, so the control arm's realised net IS
                       the headline the rest of the site carries. ALL THREE arms are on it, and
                       so is the level-vs-selection split.

  settled-provisioned  the frozen pre-arrears scalars, kept per arm as `provisioned_net_gbp`. The
                       SAME run, read the superseded way, so the difference between the two
                       panels is the clock and nothing else.

A reader who meets one number without the other cannot tell which supplier the site is
publishing. Both, or neither.

BOTH PANELS ARE ONE RUN, AND THE ROUTING IS BY DECLARED LABEL (2026-08-28)
--------------------------------------------------------------------------
Until the A/B tool was repaired, `level_vs_selection` was computed on the provisioned clock and
the level arm's realised net could not be recovered at all, so this file published the level arm
as permanently absent and stamped `settled-provisioned` on the split. The repair moved that block
to the realised clock WITHOUT changing its key or its shape -- so both of those readings silently
became wrong, one publishing an absence that was no longer true and one publishing a clock label
that was no longer true. Neither would have failed; they would just have lied.

So no panel here infers a clock from WHICH block it read. Every clock is taken from the label the
artefact puts on the figure, and a block whose label is not the one the panel is for is withheld
with its reason rather than re-stamped. The two arms the split and the bridge share are required
to agree to the penny before the third is shown, because a disagreement of that kind is a clock
difference and not a rounding one.

The headline sentence is derived from the restated figures' own SIGNS for the same reason: it was
a hardcoded claim that the advantage is the level and not the choosing, which would have survived
any run that said otherwise (R12).

DERIVED, NEVER TYPED (SITE_CONSTITUTION rule 3: the site is a RENDERING, never an author)
------------------------------------------------------------------------------------------
Every figure is read out of `docs/observability/value_cycle_ab_s1_three_arm.json` and
`docs/observability/value_cycle_ab_s1_noise_floor.json`. The prose is authored here (as
`generate_book_growth_data.BINDING_MEANING` authors its meanings); no number is. The world
commit is deliberately NOT published: the artefact does not carry one, and a sha copied from a
staging document is provenance this file cannot verify.

FAIL-CLOSED (R15)
-----------------
A missing, malformed or incomplete artefact yields `available: false` WITH the reason. It never
yields a zero, an empty arm list or a spread of 0.0 -- "the selection leg is worth nothing" and
"we could not read the file" are the two readings this feed exists to keep apart, and a fail-open
default would render them identically. The error bar is the same: a noise floor that did not run
is `error_bar.available: false`, never `stdev: 0`, because a spread of zero is the one value that
would make an indistinguishable result look decisive.

A DIRECTION IS A CLAIM, AND IT IS EARNED AGAINST THE FLOOR (2026-08-29)
-----------------------------------------------------------------------
The headline composed a DIRECTION unconditionally. Given a contrast it would say which way it
went -- and the error bar three paragraphs below said, correctly, that the same figure moves
further than that across three re-runs which changed nothing but a dice roll. Two true blocks
making one false page: the sign of every contrast on this run flips with a seed draw, and the
sentence a reader met stated it as a finding.

So `_resolvable` now gates every directional clause on the contrast's OWN measured seed spread,
and a contrast inside its floor gets its SIZE, its BOUND, and the sentence that this book cannot
resolve the sign -- plus what would (a larger settled book; not more seeds, which re-measure the
spread rather than shrink it). The withdrawn sentence is kept in `withdrawn_claim` and rendered
beside the new reading rather than deleted, because a correction a reader cannot see is one they
cannot check.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Every contrast this run produced is inside its
floor, so today the page says "we cannot tell". The day the book is large enough for a contrast to
clear its spread, the direction comes back in the same publish with nobody editing a string --
and `test_a_contrast_outside_its_seed_spread_gets_its_direction_back` is the leg that proves the
gate is not just a machine for printing "we cannot tell". A control pinned to today's answer
would go red exactly when the instrument got good enough to earn a sign, which is backwards.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
THREE_ARM_PATH = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"
NOISE_FLOOR_PATH = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor.json"
#: The floor cut into the half a larger settled book buys down and the half it cannot. Read to
#: decide whether the REMEDY this page names beside its refusal is true; absent, the page says so
#: rather than defaulting to the encouraging branch.
DECOMPOSITION_PATH = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_floor_decomposition.json")
#: The run whose figures the rest of the site publishes -- read ONLY to check whether the
#: baseline arm and the published supplier are the same run, never to fill an arm.
RUN_OUTPUT_PATH = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "data" / "value_arms.json"

#: What each arm IS, in the words a reader who does not work in energy can use. The third is the
#: control that makes the question answerable at all: without it, "the per-customer arm earned
#: more" cannot be told apart from "the per-customer arm charged more".
ARM_MEANING = {
    "control": {
        "name": "Flat rules",
        "role": "the baseline",
        "what": "One margin for every household, £2.00/MWh, set without looking at the customer. "
                "This is the supplier whose figures the rest of this site publishes.",
    },
    "value": {
        "name": "Per-customer",
        "role": "the arm under test",
        "what": "A margin chosen household by household from what the company can infer about "
                "each one -- the decision engine the whole thesis rests on.",
    },
    "level": {
        "name": "Flat at the same level",
        "role": "the control that splits the answer",
        "what": "One margin for every household again, but set at the level the per-customer arm "
                "actually charged. It prices the same renewals through the same guards under the "
                "same lawful ceiling. Anything it earns came from the PRICE LEVEL and not from "
                "choosing per customer.",
    },
}

#: The two clocks this run has, in a reader's words. Named here rather than restated per figure.
CLOCK_MEANING = {
    "settled-realised": "Summed from the world's own settlement records after the arrears model "
                        "wrote back what customers actually failed to pay. This is the clock the "
                        "rest of this site publishes.",
    "settled-provisioned": "The same run, before that write-back, using the company's flat-rate "
                           "bad-debt assumption. Superseded within the run itself.",
}

PROVISIONAL_NOTE = (
    "PROVISIONAL. This is one run of each arm on one world, and the error bar below is wider than "
    "the effect it is measuring. It is published because withholding it while publishing the "
    "profitable-looking half would be the misleading choice, not because it is settled."
)

#: R12, in the artefact's own voice. A selection leg worth nothing is a COMPLETE ANSWER.
NOT_A_TARGET = (
    "A selection leg worth nothing is a complete answer, not a cue to tune the arm until it wins. "
    "The margin is a diagnostic here and never a target: an arm that loses to its own baseline is "
    "the result this comparison was built to be able to return."
)


def _f(value):
    """A float, or None. A string, a bool or a non-finite is NOT a figure -- it is a defect, and
    returning None makes the caller publish an absence rather than render `NaN` at a reader."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    v = float(value)
    return None if v != v or v in (float("inf"), float("-inf")) else v


def _arm(key: str, net_gbp, advantage_gbp=None, absent_reason: str | None = None) -> dict:
    meaning = ARM_MEANING[key]
    return {
        "key": key,
        "name": meaning["name"],
        "role": meaning["role"],
        "what": meaning["what"],
        "net_gbp": net_gbp,
        "advantage_gbp": advantage_gbp,
        "absent_reason": absent_reason,
    }


#: How close the A/B's control arm and the published run's own net margin must be before the feed
#: is allowed to say they are the same supplier. Both are summed from settlement records in
#: pounds, so anything above a penny is a different quantity and not a rounding difference.
SAME_SUPPLIER_TOLERANCE_GBP = 0.01


#: The figure the SITE publishes for the company. Not `run_output_latest.json` -- that is a run
#: artefact any pass can overwrite, including an A/B arm. This is the file the dashboard renders
#: from, so it is what a reader actually meets.
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"


def _published_dashboard_net():
    """`portfolio.net_margin_gbp` from the site's own dashboard feed, or None if unreadable.

    None is not a pass: the caller only uses this to REFUSE, so an unreadable dashboard leaves the
    original comparison in place rather than silently clearing it. That is deliberate -- this
    check's job is to catch a subject mismatch it can PROVE, and inventing one from a missing file
    would be the opposite failure.
    """
    try:
        loaded = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(loaded, dict):
        return None
    return _f(((loaded.get("portfolio") or {}) if isinstance(loaded.get("portfolio"), dict)
               else {}).get("net_margin_gbp"))


def _is_the_published_supplier(control_net, published_run: dict | None) -> dict:
    """Is the A/B's flat-rules control arm the same supplier the rest of this site publishes?

    CHECKED, NEVER ASSERTED. "The supplier on this site IS the baseline arm" is the sentence that
    makes this whole comparison land, and it is exactly the sentence that rots silently: the site
    republishes on every run, and the day a run moves off the control arm's world the claim
    becomes false with nothing to catch it. So it is recomputed here from the published run's own
    `total_net_gbp` every publish, and it renders as a NEGATIVE -- naming both figures and the gap
    -- the moment the two stop matching. Same shape as
    `generate_dashboard_data._check_front_door_segment_claim`, which guards the front door's
    hand-authored segment sentence the same way and for the same reason.
    """
    published = _f((published_run or {}).get("total_net_gbp"))
    if control_net is None or published is None:
        return {"checked": False, "same_supplier": None, "published_run_net_gbp": published,
                "statement": ("The published run's own net margin could not be read, so this feed "
                              "does not claim any relationship between it and the baseline arm.")}

    # IS THE SUBJECT EVEN THE FIGURE THE SITE PUBLISHES? Added 2026-08-28, after a concurrent lane
    # raised the independence failure and the evidence corrected its premise. Two facts, both
    # verified: `run_output_latest.json` is written by `simulation.run_phase4c_on_phase2b`, which is
    # the same entry point the A/B calls once per arm -- so an A/B pass can make this check compare
    # its own output against itself. And the figure the SITE actually publishes for the company is
    # `site/data/dashboard.json`'s `portfolio.net_margin_gbp`, fetched live at 153,244.79 while
    # `run_output_latest.json` at HEAD read 1,529,288.58.
    #
    # So when the two disagree, the file this check reads is NOT the figure the site publishes, and
    # the sentence below cannot be made either way. It is WITHHELD with both numbers rather than
    # answered from the wrong one -- which is the fail-closed form of "I do not know which run is
    # published". Deciding which one SHOULD be published is the publish lane's, not this
    # generator's, and this refusal does not decide it.
    dashboard_net = _published_dashboard_net()
    if dashboard_net is not None and abs(dashboard_net - published) > SAME_SUPPLIER_TOLERANCE_GBP:
        return {
            "checked": False,
            "same_supplier": None,
            "published_run_net_gbp": published,
            "dashboard_net_gbp": dashboard_net,
            "statement": (
                "This feed cannot say whether the baseline arm is the supplier the site publishes. "
                "The run artefact it reads reports £{p:,.2f} and the figure the site actually "
                "publishes for the company reports £{d:,.2f} -- a gap of £{g:,.2f} -- so the two "
                "are not the same run and the claim is withheld rather than answered from "
                "whichever one is nearer."
            ).format(p=published, d=dashboard_net, g=abs(dashboard_net - published)),
        }

    gap = published - control_net
    same = abs(gap) <= SAME_SUPPLIER_TOLERANCE_GBP
    return {
        "checked": True,
        "same_supplier": same,
        "published_run_net_gbp": published,
        "gap_gbp": gap,
        "statement": (
            "The net margin this site publishes for the company is the same figure, to the penny, "
            "as the flat-rules baseline arm below. The supplier on the front of this site IS the "
            "baseline."
            if same else
            "The published run's net margin (£{p:,.2f}) is NOT the baseline arm's (£{c:,.2f}) -- "
            "they differ by £{g:,.2f}. The comparison below is between three arms of one A/B run "
            "and is no longer a statement about the supplier this site publishes elsewhere."
        ).format(p=published, c=control_net, g=abs(gap)),
    }


def _realised(three_arm: dict, published_run: dict | None) -> dict:
    """The three arms on the site's own clock -- the level arm included, when the run supports it.

    WHERE THE LEVEL ARM'S REALISED NET COMES FROM, AND WHY NOT THE BRIDGE (2026-08-28).
    `gross_to_net_bridge` walks the control and value arms only, and that is by design: its job
    is to decompose ONE contrast into named cost lines. So this used to publish the level arm as
    permanently absent. That absence was correct against the pre-repair artefact and is now
    STALE: `run_value_cycle_ab._arm_block` sums `total_net_gbp` from `phase2b.all_records` for
    EVERY arm, after the arrears engine has mutated them, and `level_vs_selection` carries that
    sum for all three arms under an explicit `clock` of its own. The level arm's realised net is
    recoverable; it simply lives in a different block from the one this function first looked in.

    ROUTED BY THE ARTEFACT'S DECLARED CLOCK, NEVER BY POSITION. The same block was on
    `settled-provisioned` before the repair and is on `settled-realised` after it, with no change
    of key or shape -- so a generator that assumed a clock by which block it read would publish
    provisioned figures under a realised heading the day the tool changed. It reads the label.

    WHAT THE CROSS-CHECK PROVES AND WHAT IT DOES NOT. `level_vs_selection` and the bridge reach
    the two arms they SHARE by different code paths, so requiring them to agree to the penny
    catches the failure that actually matters here -- one of them being on the other clock, which
    would show up as the GBP 39,962.17 bad-debt gap, not as a rounding difference. It does not
    prove either is correct: both sum the same `net_margin_gbp` field, so a defect in that field
    is invisible to it. Stated rather than implied, because a check that is quoted as more than
    it is becomes the tautology it was written to avoid (R15).
    """
    bridge = three_arm.get("gross_to_net_bridge") or {}
    control = _f((bridge.get("control_arm") or {}).get("net_margin_gbp"))
    value = _f((bridge.get("value_arm") or {}).get("net_margin_gbp"))
    delta = _f(bridge.get("net_delta_gbp"))
    if control is None or value is None or delta is None:
        return {"available": False,
                "reason": "the artefact carries no gross-to-net bridge, so no arm can be put on "
                          "the realised clock"}

    level_net, level_adv, level_absent = _level_on_the_realised_clock(
        three_arm, control, value)
    return {
        "available": True,
        "clock": "settled-realised",
        "clock_means": CLOCK_MEANING["settled-realised"],
        "arms": [
            _arm("control", control),
            _arm("value", value, advantage_gbp=delta),
            _arm("level", level_net, advantage_gbp=level_adv, absent_reason=level_absent),
        ],
        "split": _split_on_the_realised_clock(three_arm),
        "is_the_published_supplier": _is_the_published_supplier(control, published_run),
    }


def _level_on_the_realised_clock(three_arm: dict, bridge_control, bridge_value):
    """`(net_gbp, advantage_gbp, absent_reason)` for the level arm. Absence always carries why."""
    lvs = three_arm.get("level_vs_selection") or {}
    if not lvs.get("available"):
        return None, None, (
            "This run produced no level-vs-selection split, so there is no third arm to show. "
            "Re-run the A/B with --level-arm.")
    clock = lvs.get("clock")
    if clock != "settled-realised":
        return None, None, (
            "Not on this clock. The run's level-vs-selection split declares itself as {!r}, so "
            "its level-arm figure belongs beside the superseded pair below and is not shown "
            "here. It is left blank rather than re-labelled.".format(clock or "unlabelled"))
    level = _f(lvs.get("level_arm_net_gbp"))
    split_control = _f(lvs.get("control_net_gbp"))
    split_value = _f(lvs.get("value_arm_net_gbp"))
    if level is None or split_control is None or split_value is None:
        return None, None, (
            "The split declares the realised clock but does not carry all three arms' net "
            "margins, so the level arm is withheld rather than part-published.")
    for name, from_split, from_bridge in (("control", split_control, bridge_control),
                                          ("per-customer", split_value, bridge_value)):
        if abs(from_split - from_bridge) > SAME_SUPPLIER_TOLERANCE_GBP:
            return None, None, (
                "Withheld: the run's two realised reads of the {} arm disagree by £{:,.2f} "
                "(£{:,.2f} in the level-vs-selection split against £{:,.2f} in the gross-to-net "
                "bridge). A gap of that size is a clock difference, not rounding, and the level "
                "arm is not shown while the two arms it is measured against do not "
                "agree.".format(name, abs(from_split - from_bridge), from_split, from_bridge))
    return level, _f(lvs.get("level_advantage_gbp")), None


def _split_on_the_realised_clock(three_arm: dict) -> dict:
    """The restated level-vs-selection reading: what the choosing was worth, on the site's clock."""
    lvs = three_arm.get("level_vs_selection") or {}
    if not lvs.get("available") or lvs.get("clock") != "settled-realised":
        return {"available": False,
                "reason": "the run's level-vs-selection split is not on the realised clock, so "
                          "the restated reading is published under the superseded pair instead"}
    selection = _f(lvs.get("selection_gbp"))
    if selection is None:
        return {"available": False,
                "reason": "the split carries no selection figure"}
    return {
        "available": True,
        "clock": "settled-realised",
        "selection_gbp": selection,
        # WHAT THE PER-CUSTOMER ARM ITSELF EARNED AGAINST FLAT RULES. Surfaced 2026-08-28: the
        # headline opened with "earned more than flat rules" as a CONSTANT, which was false on the
        # run of that afternoon (the arm earned GBP 4,724 LESS). The figure was in the artefact and
        # this block did not carry it, so the sentence had nothing to be derived from.
        "value_advantage_gbp": _f(lvs.get("value_advantage_gbp")),
        "level_advantage_gbp": _f(lvs.get("level_advantage_gbp")),
        "level_share_of_advantage": _f(lvs.get("level_share_of_advantage")),
        "share_undefined_reason": lvs.get("share_undefined_reason"),
        "level_gbp_per_mwh": _f(lvs.get("level_gbp_per_mwh")),
        "why_this_clock": lvs.get("why_this_clock"),
        "how_to_read_this": lvs.get("how_to_read_this"),
    }


#: Where each arm's SUPERSEDED net margin lives in the artefact, per arm block. `_arm_block`
#: keeps the frozen pre-arrears scalar under its own name rather than deleting it, precisely so
#: this panel can be built from the SAME RUN as the realised one.
_PROVISIONED_NET_KEY = "provisioned_net_gbp"


def _provisioned(three_arm: dict) -> dict:
    """The same three arms, same run, on the clock the run superseded inside itself.

    WHY THIS IS BUILT FROM THE ARM BLOCKS AND NOT FROM `level_vs_selection` (2026-08-28).
    It used to read the split and stamp `settled-provisioned` on it. That was true of the
    pre-repair artefact and became a LIE at the moment the tool was repaired: the split is now
    computed on the realised clock and carries `clock: settled-realised`, so this panel would
    have relabelled realised figures as provisioned and published the relabelling on a live page
    -- the same clock-mixing defect the repair existed to remove, reintroduced one layer further
    out. Nothing about the block's key or shape changes when its clock does, so position cannot
    be the routing rule; the declared label is.

    Both panels are therefore the SAME RUN read two ways. That matters more than it looks: it
    means the difference between them is the CLOCK and nothing else. A reader comparing the
    restated figure against a number from a previous run would be reading the clock change and
    run-to-run drift added together, with no way to tell which is which -- and on this
    instrument the drift is not small next to the effect.
    """
    blocks = {key: three_arm.get("{}_arm".format(key)) or {}
              for key in ("control", "value", "level")}
    nets = {key: _f(block.get(_PROVISIONED_NET_KEY)) for key, block in blocks.items()}
    missing = sorted(key for key, net in nets.items() if net is None)
    if missing:
        return {"available": False,
                "reason": ("the run's {} arm block carries no `{}`, so the superseded clock "
                           "cannot be shown for all three arms and is withheld rather than "
                           "part-published".format("/".join(missing), _PROVISIONED_NET_KEY))}
    # The block's own label for the figure being read, checked rather than assumed -- the same
    # rule this function exists to enforce, applied to itself.
    mislabelled = sorted(
        key for key, block in blocks.items()
        if (block.get("clocks") or {}).get(_PROVISIONED_NET_KEY) not in (None,
                                                                         "settled-provisioned"))
    if mislabelled:
        return {"available": False,
                "reason": ("the {} arm block labels `{}` with a clock other than "
                           "settled-provisioned, so this panel would misname it".format(
                               "/".join(mislabelled), _PROVISIONED_NET_KEY))}

    control, value, level = nets["control"], nets["value"], nets["level"]
    value_adv = value - control
    level_adv = level - control
    selection = value_adv - level_adv
    # Undefined rather than infinite, on the same rule and threshold `level_vs_selection` uses:
    # a share of an advantage near zero is a divide by a rounding error dressed as a percentage.
    share = level_adv / value_adv if abs(value_adv) > 1.0 else None
    shape = three_arm.get("level_arm_decision_shape") or {}
    return {
        "available": True,
        "clock": "settled-provisioned",
        "clock_means": CLOCK_MEANING["settled-provisioned"],
        "arms": [
            _arm("control", control),
            _arm("value", value, advantage_gbp=value_adv),
            _arm("level", level, advantage_gbp=level_adv),
        ],
        "selection_gbp": selection,
        "level_share_of_advantage": share,
        "share_undefined_reason": (
            None if share is not None else
            "the per-customer arm's advantage is under £1 on this clock -- a share of it "
            "would be noise"),
        "level_gbp_per_mwh": _f((three_arm.get("level_vs_selection") or {}).get(
            "level_gbp_per_mwh")),
        "control_gbp_per_mwh": _f(shape.get("control_margin_gbp_per_mwh")),
        # NO SPREAD HAS EVER BEEN MEASURED ON THIS CLOCK, so the figure beside it is a size and
        # never a direction. A CONSTANT, and said to be one: `run_value_cycle_ab` builds its noise
        # floor by re-reading `level_vs_selection` per seed (tools/run_value_cycle_ab.py:2535),
        # which declares `settled-realised`, so there is no artefact anywhere in this repo that
        # could bound a provisioned contrast. Deriving it would be a branch nothing can reach --
        # a constant verdict wearing a computation's clothes (R15). What makes this conditional is
        # a floor run on the superseded clock; until one exists, the honest form is to say so.
        "no_spread_on_this_clock": (
            "No seed spread has ever been measured on this superseded clock, so the figure above "
            "is a SIZE and not a direction: nothing here says the choosing was worth more or less "
            "than nothing. The bounded reading is the realised one, in the headline."),
        "superseded_note": (
            "This is the clock the run superseded inside itself: the company's flat-rate "
            "bad-debt assumption, frozen at the end of the settlement loop, before the arrears "
            "model wrote back what customers actually failed to pay. It is shown because "
            "deleting it would leave a reader unable to tell how much of the headline moved "
            "when the clock was corrected -- and because it is the more flattering of the two, "
            "which is the reason to publish it beside the other rather than instead of it."),
    }


def _staleness_caveat(floor: dict, three_arm: dict) -> str | None:
    """Say, from the two artefacts' own stamps, whether the error bar predates the point estimate.

    DERIVED, NOT WRITTEN DOWN, and that is the whole repair. The caveat that stood here was a
    hand-authored sentence naming the 2026-08-28 clock repair -- true when it was typed and
    unable to notice anything that happened afterwards. On 2026-08-28 something did: the world
    gained a competitor that DEFENDS (`simulation/competitor_reference.py`, 08:25), and the
    three-arm run was re-taken against it while the noise floor was not. A seed spread measured
    in a market that could not react is not an error bar on a point estimate measured in one that
    can, and no amount of clock-labelling says so.

    The test is a comparison of timestamps, so it stays true whatever the next world change is.
    """
    floor_at = (floor or {}).get("generated_at")
    point_at = (three_arm or {}).get("generated_at")
    if not floor_at or not point_at:
        # An artefact with no stamp cannot be shown to be current, and unknown provenance on a
        # published error bar reads as fine unless someone says otherwise (FAIL-SILENT).
        return ("One of these two runs carries no timestamp, so this feed cannot show that the "
                "error bar and the point estimate describe the same world. Read the spread as a "
                "scale statement about the instrument, not as a confidence interval.")
    if floor_at >= point_at:
        return None
    return (
        "THE ERROR BAR IS OLDER THAN THE FIGURE IT BOUNDS. The seed spread was measured on the run "
        "of {floor_at} and the point estimate on the run of {point_at}. Anything that changed the "
        "world between those two runs is inside the point estimate and outside the spread -- and "
        "something did, on 2026-08-28: the market gained the ability to DEFEND against a company "
        "that undercuts it. A spread measured where nothing could react is not a confidence "
        "interval on a figure measured where it can. Read it as the size of this instrument's seed "
        "sensitivity; re-running the noise floor on the current world is owed work."
    ).format(floor_at=floor_at, point_at=point_at)


def _error_bar(floor: dict, point_estimate, three_arm: dict | None = None,
               point_clock: str | None = None) -> dict:
    """The seed spread on the selection leg -- the reason the point estimate cannot be quoted bare.

    NEVER fails open to a spread of zero: a spread of zero is the one value that would make an
    indistinguishable result read as a decisive one.

    THE POINT IT BOUNDS IS THE REALISED ONE, AND IT USED NOT TO BE (2026-08-29, second pass).
    `build` handed this function the PROVISIONED selection leg while every row the spread is
    computed from is read out of `level_vs_selection`, which declares `settled-realised`. Two
    correct figures whose ratio is not a quantity -- the shape this project publishes wrong most
    often -- and the file already said so three functions up: `_provisioned.no_spread_on_this_clock`
    states in terms that no spread has ever been measured on the superseded clock. One file, two
    functions, opposite answers.

    It was not academic. On the 2026-08-29 run the page published `ratio` 5.69 and
    `point_estimate_inside_the_measured_band: True` -- "the point estimate sits inside that band"
    -- off the provisioned +£453. The realised +£1,815.79 that the headline actually states is
    OUTSIDE the same band (-£4,273.97 to +£872.96) at a ratio of 1.42. The flattering answer, on
    the reassuring side, under the sentence a reader trusts most.

    So the caller passes the figure the HEADLINE states together with the clock it declares, and
    both are republished here as `bounds_figure_gbp`/`bounds_figure_clock`. That pair is what makes
    the pairing checkable from the artefact instead of from this docstring: a reader, and
    `test_the_error_bar_bounds_the_FIGURE_THE_HEADLINE_STATES`, can reconcile it against
    `realised.split.selection_gbp` without knowing anything about which function passed what.
    """
    spread = (floor or {}).get("selection_gbp_spread") or {}
    stdev = _f(spread.get("stdev"))
    lo, hi = _f(spread.get("min")), _f(spread.get("max"))
    n = spread.get("n")
    if stdev is None or lo is None or hi is None or not isinstance(n, int) or n < 2:
        return {"available": False,
                "reason": "no noise floor has been run for this reading, so the point estimate "
                          "is published without a measured spread"}
    seeds = [s for s in (floor.get("seeds") or []) if isinstance(s, dict)]
    draws = [s.get("elasticity_draws") for s in seeds]
    ratio = (abs(stdev / point_estimate)
             if point_estimate not in (None, 0) else None)
    # Whether the figure this spread is published beside is even inside the range the spread was
    # measured over. `None` when either end is missing -- an unknown relationship must not read
    # as a comfortable one.
    inside = (None if lo is None or hi is None or point_estimate is None
              else bool(lo <= point_estimate <= hi))
    return {
        "available": True,
        "seeds": n,
        "passes": n * len(ARM_MEANING),
        "what_was_re_drawn": (
            "The same three arms re-run on the same world once per seed, with only the "
            "per-household price-sensitivity draw changed. Nothing about the company moved."),
        "mean_gbp": _f(spread.get("mean")),
        "stdev_gbp": stdev,
        "min_gbp": lo,
        "max_gbp": hi,
        "sem_gbp": _f(floor.get("selection_sem_gbp")),
        "distinguishable_from_zero": bool(floor.get("selection_distinguishable_from_zero")),
        "spread_to_point_estimate_ratio": ratio,
        # WHICH FIGURE THIS IS A BAR ON, published rather than left to the reader to infer from
        # position. Republished as a pair so the pairing is RECONCILABLE against
        # `realised.split.selection_gbp` on the surface -- the check that would have caught this
        # block bounding the provisioned leg while the headline stated the realised one.
        "bounds_figure_gbp": point_estimate,
        "bounds_figure_clock": point_clock,
        # WHICH READING THIS BOUNDS. The noise floor is its own set of runs, and if it does not
        # declare a clock this feed will not choose one for it: it is paired with the panel whose
        # figure it was computed alongside, and said to be a scale statement about the instrument
        # rather than a confidence interval on the restated headline.
        "clock": floor.get("clock"),
        # NAMES WHAT WOULD EMPTY IT (2026-08-29). The floor's producer was withholding the label,
        # not this feed -- `run_value_cycle_ab.noise_floor` now carries the clock its own split
        # declares, per seed and reconciled across them. The artefact on disk predates that, so
        # this caveat stands until the next `--noise-floor` run and then clears itself. Left
        # standing rather than blanked: a caveat removed before the run that answers it is the
        # feed asserting a fact about an artefact it has not seen.
        "clock_caveat": (
            None if floor.get("clock") else
            "This noise floor carries no clock label of its own, so it is paired with the panel "
            "it was measured beside rather than with the restated figure. Its producer has "
            "labelled the floor since this one was taken; the next noise-floor run empties this."),
        # DERIVED from the two runs' own stamps -- see `_staleness_caveat`. Separate from the
        # clock caveat because they are different failures: one is a basis label, the other is a
        # different WORLD, and a reader shown only the first would take the spread for current.
        "staleness_caveat": _staleness_caveat(floor, three_arm or {}),
        "elasticity_draws_min": min(draws) if draws and all(
            isinstance(d, int) for d in draws) else None,
        # No range restated here: the surface renders the min and max in its own sentence, and a
        # second copy of the same two figures is where a rounding convention drifts between them.
        # DERIVED, because the sentence that stood here asserted "the point estimate sits inside
        # that band" as a fact about a reading it could not see. On 2026-08-28 it stopped being
        # true -- the selection leg moved to -GBP 5,224 against a measured band of -3,705 to
        # +5,076 -- and the surface would have gone on saying it. The generator's own live-state
        # test caught it (`test_the_selection_leg_and_its_error_bar_are_published_together`),
        # which is the control working; keeping the sentence would have been the defect.
        "point_estimate_inside_the_measured_band": inside,
        # THREE BRANCHES, BECAUSE THERE ARE THREE STATES. `inside` is a tri-state -- True, False,
        # and None for "no figure on this spread's clock to place" -- and until 2026-08-29 this
        # was a two-branch ternary, so None fell through the falsy edge and published "the point
        # estimate now sits OUTSIDE the band" about a point estimate that did not exist. An
        # unknown rendered as a measured fact, in the fail-open direction, on the one sentence
        # this block exists to get right (R15: unknown must never read as an answer).
        "reading": (
            "The point estimate sits inside that band and so does zero, so this instrument cannot "
            "yet resolve a selection effect of the size it is measuring -- in either direction. "
            "That is a finding about the INSTRUMENT and not about the pricing arm, and it is not "
            "a cue to re-run until a seed agrees."
            if inside is True else
            "The point estimate now sits OUTSIDE the band this spread was measured over, so the "
            "spread is not a bound on it and nothing here resolves the selection effect either "
            "way. An estimate that has left its own error bar's range needs the error bar "
            "re-measured, not read as having escaped it -- which is the direction the reading "
            "would drift if this sentence were fixed rather than derived."
            if inside is False else
            "There is no figure on this spread's own clock to place inside or outside it, so "
            "nothing here resolves the selection effect either way. What is published below is "
            "the size of this instrument's seed sensitivity and NOT a bound on any number on this "
            "page -- the spread is measured on the settled-realised clock, and this run's "
            "level-vs-selection split does not declare that clock, so pairing the two would be "
            "the clock mix this feed refuses everywhere else."),
    }



#: The contrasts the noise floor re-measures once per seed, and therefore the only ones this feed
#: can bound. A contrast the floor does not carry gets NO bound and therefore NO direction -- never
#: a neighbour's, because a spread measured on one quantity is not a bound on another. On the
#: 2026-08-29 floor these three differ by more than 2.5x (+-990, +-2,511, +-2,578 on the same three
#: seeds), so borrowing would have licensed a direction the borrowed-from figure never earned.
_BOUNDED_CONTRASTS = ("value_advantage_gbp", "level_advantage_gbp", "selection_gbp")

#: The half of the remedy that is ARITHMETIC and needs no evidence: more seeds estimate this
#: spread again, they do not shrink it. True of any error bar, so it is stated unconditionally.
MORE_SEEDS_WOULD_NOT = (
    "More seeds would not resolve it: re-drawing the dice measures this spread again, it does not "
    "shrink it.")

#: The half that is a CLAIM ABOUT WHERE THE SPREAD COMES FROM, and was published as fact for a day
#: before anyone measured it. The floor re-draws elasticity for ~2,050 households and the arm
#: priced 20 renewals, so the spread has two sources with OPPOSITE remedies: the priced
#: households' own draw (shrinks as ~1/sqrt(n), so a larger settled book buys it down) and the
#: rest of the book's churn cascade landing in the same net (does not shrink with the priced count
#: at all, so a larger book buys nothing). `run_value_cycle_ab.decompose_floor` measures which,
#: from two extra floor legs that partition one call stream. Until it has, this page says what has
#: NOT been established rather than picking the encouraging branch -- a remedy is a claim, and an
#: unmeasured one beside a refusal is the second wrong sentence in the same paragraph.
WHAT_WOULD_RESOLVE_IT_UNKNOWN = (
    "What WOULD resolve it has not been established: this spread has not been separated into the "
    "priced households' own draw, which a larger settled book shrinks, and the rest of the book's "
    "churn cascade, which no book size touches.")


def _how_narrowly_the_split_cleared(decomposition: dict) -> str:
    """The sample size and the DISTANCE, printed beside any price the page states.

    THE DEFECT THIS EXISTS FOR. `share_is_decisive` is a threshold crossing, and a reader shown
    only the price cannot tell a rout from a photo finish. The split that first reached this branch
    cleared its own bar by 0.005 -- 0.1550 against 0.150 -- on three seeds, two degrees of freedom
    a side. Publishing "it takes about 86 priced renewals" from that, with no distance beside it,
    states a resolution the instrument did not buy.

    FAIL CLOSED ON A MISSING MARGIN. An artefact written before the producer carried
    `share_margin_over_threshold` gets the seed count and an explicit silence about the distance --
    never a confident sentence by omission, which is how the absent key would otherwise read.
    """
    seeds = decomposition.get("seeds")
    margin = decomposition.get("share_margin_over_threshold")
    bar = decomposition.get("share_decisive_bar")
    if not isinstance(margin, (int, float)) or not isinstance(bar, (int, float)):
        return ("Read that price as a direction and not a settled figure: it rests on a split "
                "measured on {} seeds, and how far that split cleared its own threshold was not "
                "recorded.".format(seeds if seeds is not None else "too few"))
    return ("Read that price as a direction and not a settled figure: the split behind it is {} "
            "seeds, and it clears the margin it has to beat by {:.3f} against a bar of {:.2f} -- "
            "wide enough to name a direction, not wide enough to call the number settled."
            .format(seeds, margin, bar))


def _is_the_lever_reachable(decomposition: dict) -> str:
    """Whether "a larger settled book" is a lever this world can actually pull.

    THE DEFECT THIS EXISTS FOR. "More renewals actually priced by the arm" reads as a book-SIZE
    remedy, and on 2026-08-30 the producer measured that all ten priced accounts were the
    hand-authored static roster and not one was a drawn household -- so acquisition adds renewals
    that stop at `product_not_upliftable` and households to the churn cascade, buying zero priced
    decisions and enlarging the half of the floor no book size shrinks. The price was true and the
    lever named beside it was not. `where_the_priced_decisions_come_from` had measured this and
    sat unread in the artefact while the page composed the sentence it refutes.

    KEYED TO THE PROVENANCE, NOT TO TODAY'S ROSTER. Feed it a book where the arm priced a drawn
    household and the caveat must go -- otherwise it would still be printed the day the product
    ships and the remedy becomes reachable, which is a control asserting the world stays broken.
    FAIL CLOSED on a missing count: an artefact written before the producer carried the provenance
    gets an explicit silence, never a reachable-by-omission reading.
    """
    provenance = decomposition.get("where_the_priced_decisions_come_from")
    if not isinstance(provenance, dict):
        return ("Which accounts that growth would have to come from was not recorded, so whether "
                "it is reachable by growing the book is not established here.")
    drawn = provenance.get("of_those_drawn")
    priced_accounts = provenance.get("accounts_the_arm_priced")
    if not isinstance(drawn, int) or not priced_accounts:
        return ("Which accounts that growth would have to come from was not recorded, so whether "
                "it is reachable by growing the book is not established here.")
    if drawn:
        return ("{} of the {} accounts the arm priced are drawn households, so acquisition does "
                "reach this arm and the growth above is a book-size lever."
                .format(drawn, len(priced_accounts)))
    return ("But that growth is NOT reachable by acquiring customers: all {} accounts the arm "
            "priced are the founding roster and not one is a household this world drew, because "
            "drawn households' renewals stop for want of a standard-variable product to be moved "
            "off. Buying more of them adds churn cascade -- the half of the floor no book size "
            "shrinks -- and no priced decisions at all. The lever is a PRODUCT, not a size."
            .format(len(priced_accounts)))


def _priced_against_which_floor(decomposition: dict) -> str:
    """The price restated against the bound the page actually shows, when the legs undershot it.

    THE DEFECT THIS EXISTS FOR. The producer prices the remedy on the two legs' summed variance,
    and the reconciliation ratio says how far that is from the undecomposed floor the page prints
    as its +- figure. On 2026-08-30 that was 0.66x -- inside the published 0.3-3.0 tolerance, and
    a factor of 1.5 in the price: 1.33x this book against the legs' total, 2.02x against the bound
    a reader is shown. Quoting the smaller alone lets a tolerance the artefact prints as noise
    arrive at the reader as a cheaper remedy, which is fail-open in the flattering direction.

    SILENT WHEN THE LEGS RECONCILE. At a ratio of 1.0 the two prices are the same number and a
    sentence explaining that they differ would be noise -- so this fires on the DISCREPANCY, not
    unconditionally, and a repair that made the legs sum properly removes it on its own.
    """
    on_published = decomposition.get("times_this_book_on_the_published_floor")
    decisions = decomposition.get("priced_decisions_needed_on_the_published_floor")
    ratio = decomposition.get("reconciliation_ratio")
    if not isinstance(on_published, (int, float)) or not isinstance(decisions, int):
        return ""
    if not isinstance(ratio, (int, float)) or abs(ratio - 1.0) < 0.1:
        return ""
    return ("That price is against the two legs' own total, which came to {:.2f}x the +-figure "
            "this page states -- within what three seeds alone produce, and still a real "
            "difference to anyone acting on it. Against the published bound the same arithmetic "
            "asks for about {:,} priced renewals, and that is the number to plan on."
            .format(ratio, decisions))


def _what_would_resolve_it(decomposition: dict | None) -> str:
    """The remedy sentence, DERIVED from the measured split of the floor -- or the refusal.

    THE PROPERTY, NOT TODAY'S WORDING. The clause claiming a larger settled book is the remedy
    appears when, and only when, the decomposition says the priced households' half is the one
    that dominates -- specifically when the rest-of-book half ALONE comes in under the contrast,
    which is the page's own resolution rule applied to the floor that survives an infinite book.
    Feed this a split where the priced side dominates and the clause must appear; feed it one
    where it does not and the clause must be absent. That is what
    `test_the_remedy_clause_follows_the_decomposition_not_the_wording` mutates, and it is keyed
    that way because a control pinned to the sentence goes red when the page becomes more honest.

    THREE BRANCHES AND NOT TWO. "Not measured" is not "measured and negative": the first says
    nothing about the remedy, the second says the remedy is false. Collapsing them would let a
    missing artefact publish a finding.
    """
    if not (decomposition or {}).get("available"):
        return WHAT_WOULD_RESOLVE_IT_UNKNOWN + " " + MORE_SEEDS_WOULD_NOT
    # A SPLIT TOO CLOSE TO ITS OWN THRESHOLD TO CALL IS NOT A CALL. Three seeds give each variance
    # two degrees of freedom, and the producer says whether the split cleared that.
    if not decomposition.get("share_is_decisive"):
        return ("The spread HAS now been split -- {:.0%} of it is the priced households' own draw "
                "and the rest is the wider book's churn cascade -- but at {} seeds that split is "
                "too close to the {:.0%} it would have to clear to say whether a larger settled "
                "book would resolve this at all. ".format(
                    decomposition.get("priced_share_of_variance") or 0.0,
                    decomposition.get("seeds"),
                    decomposition.get("share_at_which_a_bigger_book_could_resolve_it") or 0.0)
                + MORE_SEEDS_WOULD_NOT)
    if decomposition.get("larger_settled_book_would_resolve_it"):
        needed = decomposition.get("priced_decisions_needed")
        priced = decomposition.get("priced_decisions")
        return ("What would resolve it is a larger SETTLED BOOK -- more renewals actually priced "
                "by the arm -- and the price is now measured: {:.0%} of this spread is the priced "
                "households' own draw, so it takes about {:,} priced renewals against this book's "
                "{} to bring the bar under the gap. ".format(
                    decomposition.get("priced_share_of_variance") or 0.0, needed, priced)
                + " ".join(p for p in (_priced_against_which_floor(decomposition),
                                       _is_the_lever_reachable(decomposition),
                                       _how_narrowly_the_split_cleared(decomposition),
                                       MORE_SEEDS_WOULD_NOT) if p))
    return ("A larger settled book would not resolve it either, and that is the finding: only "
            "{:.0%} of this spread is the priced households' own draw. The rest is the wider "
            "book's churn cascade landing in the same net, which does not shrink however many "
            "renewals the arm prices -- on its own it is £{:,.0f} against a £{:,.0f} gap. This "
            "comparison cannot be resolved at any book this world can legitimately produce, so "
            "what is needed is a different instrument and not a bigger sample. ".format(
                decomposition.get("priced_share_of_variance") or 0.0,
                decomposition.get("irreducible_sd_gbp") or 0.0,
                abs(decomposition.get("contrast_gbp") or 0.0))
            + MORE_SEEDS_WOULD_NOT)

#: EVERY SENTENCE THIS PAGE HAS WITHDRAWN, newest first, in the words it was published in and kept
#: beside the reading that replaced it. Not deleted: a correction a reader cannot see is one they
#: cannot check, and this page's whole claim on anyone's trust is that it publishes the
#: unflattering direction -- which is worth nothing if it can also un-publish one silently.
#:
#: A LIST, AND IT BECAME ONE THE SECOND TIME (2026-08-29). It was a single dict, which is the shape
#: that quietly overwrites the first correction with the second and leaves a page claiming to keep
#: its record while keeping one entry of it.
WITHDRAWN_CLAIMS = [{
    "withdrawn_on": "2026-08-30",
    "the_words": ("Below 0.50 means the company's own belief about who will leave ranks customers "
                  "worse than a coin flip. An estimator that cannot rank cannot select "
                  "profitably, so the selection result and the belief result corroborate each "
                  "other rather than merely coexisting."),
    "why": ("It made a corroboration argument out of an unbounded figure, and it was a CONSTANT "
            "string, so the page read 0.4653 and 0.13 as the same finding when one sits a third "
            "of a null standard deviation from 0.5 and the other 2.8 of them. Three things are "
            "wrong with it. (1) No bound: on 10 departures a signal carrying no information at "
            "all scores anywhere from 0.20 to 0.80, and the same estimator has scored 0.646, "
            "0.672, 0.465, 0.465 and 0.130 across five runs in four days. (2) The subject is "
            "misnamed: `believed_p_retain` is the retention the arm expected AT THE PRICE IT "
            "CHOSE -- a median £60/MWh against the control's £2 -- not the company's belief about "
            "who will leave. Graded independently over 708 renewals on 2026-08-30, the "
            "company-side estimate scores 0.534 and the world's own churn model 0.660, against an "
            "oracle ceiling of 0.762. (3) The two results are not independent: five of the ten "
            "accounts the arm priced left under the value arm and did NOT leave under the "
            "control, so the selection result and the belief result share a cause rather than "
            "corroborating each other. What replaces it is composed from the figure's own exact "
            "null interval and states the endogeneity at any sample size."),
    "note": ("WITHDRAWN 2026-08-30: this page previously said the belief result and the selection "
             "result “corroborate each other rather than merely coexisting”. They are not "
             "independent — five of the ten accounts the arm priced were driven out by the arm's "
             "own price rise, so both results have one cause — and the figure was published with "
             "no interval on a population of ten departures. What stands in its place carries the "
             "sample, the exact null, and what the figure is actually a belief about."),
}, {
    "withdrawn_on": "2026-08-29",
    "the_words": ("What would resolve it is a larger SETTLED BOOK -- more renewals actually "
                  "priced by the arm -- and not more seeds: re-drawing the dice measures this "
                  "spread again, it does not shrink it."),
    "why": ("The second half is arithmetic and stands. The FIRST half named a remedy nobody had "
            "measured. The floor it qualifies re-draws price sensitivity for about 2,050 "
            "households while the arm priced 20 renewals, so the spread has two possible sources "
            "with OPPOSITE remedies -- the priced households' own draw, which a larger settled "
            "book shrinks, and the rest of the book's churn cascade, which no book size touches. "
            "The page asserted the first without separating them, one day after withdrawing a "
            "different sentence for asserting a direction its evidence could not carry. What "
            "replaces it is derived from a measured split of the floor, and says so when there "
            "is no split to derive it from."),
    "note": ("WITHDRAWN 2026-08-29: this page previously said the way to resolve the comparison "
             "was “a larger SETTLED BOOK”. That named a remedy nobody had measured — the spread "
             "it qualifies has two sources with opposite remedies, and they had not been "
             "separated. What stands in its place is derived from the split, or says plainly "
             "that no split has been run."),
}, {
    "withdrawn_on": "2026-08-29",
    "the_words": ("On this evidence the advantage is the price level, and the per-customer "
                  "choosing is worth less than nothing."),
    "why": ("It stated a sign the evidence could not carry. That run's selection leg was "
            "-£9,627 and the same figure moved across a range of £8,781 when three re-runs "
            "changed nothing but the per-household price-sensitivity draw -- so 'worth less than "
            "nothing' was a seed result reported as a finding. The claim is not reversed here and "
            "nothing replaces it with the opposite: it is withdrawn, and what stands in its place "
            "is the size, the bound, and the fact that a book this small cannot resolve the sign."),
    "note": ("WITHDRAWN 2026-08-29: this page previously said “on this evidence the advantage "
             "is the price level, and the per-customer choosing is worth less than nothing”. "
             "That sentence stated a direction smaller than its own error bar. It is withdrawn, "
             "not reversed: the reading above is what the evidence supports."),
}]


def _withdrawn() -> dict:
    """The withdrawal block the page renders: the newest correction, with every earlier one kept.

    THE RENDERED `note` IS THE WHOLE RECORD, joined, and that is the point. The surface prints one
    string; if only the newest note reached it, the second correction would erase the first from
    the page while the feed still carried it, and a reader would see a page that had corrected
    itself once. `also_withdrawn` carries the earlier entries structurally for anything that wants
    to render them apart.
    """
    newest, *older = WITHDRAWN_CLAIMS
    return dict(newest,
                note=" ".join(claim["note"] for claim in WITHDRAWN_CLAIMS),
                also_withdrawn=older,
                withdrawals=len(WITHDRAWN_CLAIMS))


def _seed_spreads(floor: dict | None) -> dict:
    """Per-contrast seed spread, DERIVED from the noise floor's own per-seed rows.

    WHY DERIVED HERE AND NOT READ. The producer publishes a spread block for exactly one of the
    three contrasts (`selection_gbp_spread`). The other two are in the seed rows and nowhere else,
    and the headline makes a directional claim about both -- so either this file computes them or
    two of the three claims go out unbounded. It computes them, on the same footing as
    `_provisioned`, which already derives every contrast in its panel from the artefact's own
    scalars.

    RECONCILED, NEVER TRUSTED. The one contrast the producer DOES publish a spread for is
    recomputed here and required to match it. A derivation that cannot reproduce the single figure
    it can be checked against has no business bounding the other two, so a disagreement withholds
    ALL THREE rather than the one that failed -- the same shape as the split-versus-bridge check
    above, and for the same reason: the failure it is looking for (reading the wrong rows, or a
    seeds list that is not the one the spread was computed over) would not confine itself to one
    key. A floor carrying no published spread at all is the same refusal: nothing to check against.
    """
    seeds = [s for s in ((floor or {}).get("seeds") or []) if isinstance(s, dict)]
    if len(seeds) < 2:
        return {"available": False,
                "reason": ("no noise floor with two or more seeds has been run for this reading, "
                           "so no contrast on this page carries a measured spread")}
    contrasts = {}
    for key in _BOUNDED_CONTRASTS:
        values = [_f(seed.get(key)) for seed in seeds]
        if any(value is None for value in values):
            continue
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
        contrasts[key] = {"n": len(values), "stdev_gbp": variance ** 0.5, "mean_gbp": mean,
                          "min_gbp": min(values), "max_gbp": max(values)}

    published = _f(((floor or {}).get("selection_gbp_spread") or {}).get("stdev"))
    derived = (contrasts.get("selection_gbp") or {}).get("stdev_gbp")
    if published is None or derived is None:
        return {"available": False,
                "reason": ("the noise floor publishes no `selection_gbp_spread` to check this "
                           "feed's own reading of its seed rows against, so no contrast is "
                           "bounded from them")}
    if abs(published - derived) > SAME_SUPPLIER_TOLERANCE_GBP:
        return {"available": False,
                "reason": ("this feed's reading of the floor's seed rows gives a selection spread "
                           "of £{:,.2f} where the floor itself publishes £{:,.2f}, so it is not "
                           "reading the rows that spread was measured over and no contrast is "
                           "bounded from them".format(derived, published))}
    return {
        "available": True,
        "seeds": len(seeds),
        "what_was_re_drawn": (
            "The same three arms re-run on the same world once per seed, with only the "
            "per-household price-sensitivity draw changed. Nothing about the company moved."),
        "rule": ("A contrast smaller than the spread the SAME contrast shows across those seeds "
                 "cannot have its DIRECTION stated on this page. The rule is the floor "
                 "artefact's own: if the spread is wider than the figure, the instrument cannot "
                 "resolve the question being asked of it."),
        "contrasts": contrasts,
    }


def _spread_for(spreads: dict | None, key: str):
    """The measured spread for one contrast, or None. None is never a licence to state a sign."""
    if not (spreads or {}).get("available"):
        return None
    return ((spreads or {}).get("contrasts") or {}).get(key)


def _resolvable(value, spread) -> bool | None:
    """Is this contrast bigger than the spread the SAME contrast shows across re-draws?

    `None` means UNKNOWN -- no measured spread -- and every caller treats unknown exactly as it
    treats "no", because the one thing this gate exists to stop is a direction stated by default.

    The comparison is `>` and not `>=` on purpose: a contrast exactly equal to its own spread
    fails it. That is the fail-CLOSED direction of the strict inequality, checked because the
    opposite one is a shape this project has shipped before (R15).
    """
    value, stdev = _f(value), _f((spread or {}).get("stdev_gbp"))
    if value is None or stdev is None:
        return None
    return abs(value) > stdev


#: The funnel stages that are DELIBERATE SCOPE rather than a gap in the world. Named here, not
#: inferred from the stage name, because "is this exclusion by design" is a judgement and a
#: judgement that lives in a regex drifts silently.
_SCOPE_BY_DESIGN = {
    "acquisition_term": "term 0 has no prior term to price against",
    "not_the_arms_commodity": "the arm is fitted to electricity and has never been fitted to gas",
}


def _exclusions(funnel: dict) -> list[dict]:
    """Every non-zero funnel stage that is not `priced`, with whether it is scope or a gap."""
    out = []
    for stage in (funnel.get("stages") or []):
        if not isinstance(stage, dict) or stage.get("stage") == "priced":
            continue
        count = stage.get("count") or 0
        if not count:
            continue
        out.append({
            "stage": stage.get("stage"),
            "count": count,
            "share_of_renewals_offered": stage.get("share_of_renewals_offered"),
            "by_design": stage.get("stage") in _SCOPE_BY_DESIGN,
            "why": _SCOPE_BY_DESIGN.get(stage.get("stage")) or stage.get("means"),
        })
    return sorted(out, key=lambda s: -s["count"])


def _attribution_sentence(exclusions: list[dict], offered) -> str:
    """One sentence saying how the unpriced renewals split between scope and gap. Derived."""
    if not exclusions:
        return "The funnel reports no exclusions, so nothing can be attributed."
    design = sum(e["count"] for e in exclusions if e["by_design"])
    gap = sum(e["count"] for e in exclusions if not e["by_design"])
    total = design + gap
    if not total:
        return "The funnel reports no exclusions, so nothing can be attributed."
    return (
        "Of the {total:,} renewals the arm did not price, {design:,} are DELIBERATE SCOPE "
        "({design_pct:.0f}%) -- {reasons} -- and {gap:,} ({gap_pct:.0f}%) are the product-label "
        "gap in the drawn book. So the surface is small by design AND by plumbing, and design is "
        "the larger half."
    ).format(
        total=total, design=design, gap=gap,
        design_pct=100.0 * design / total, gap_pct=100.0 * gap / total,
        reasons="; ".join(sorted(_SCOPE_BY_DESIGN.values())))


def _skill_drop_out(method_skill: dict) -> dict:
    """The 20 → 6 funnel, read off the run and NEVER recomputed here.

    WHY IT FAILS CLOSED RATHER THAN INFERRING THE GAP. `decision_shape.priced` minus
    `decisions_scored` is available on every artefact ever produced, and subtracting them here
    would give a number that looks exactly like this block with none of its content: it would say
    fourteen decisions dropped and could not say ONE of them was a failed join rather than an
    eligibility rule. That distinction is the whole reason the block exists, it can only be made
    where the log and the settled records are both in hand, and a second arithmetic source for one
    figure is the shape this file's own clock and denominator defects both had.

    So an artefact produced before `method_skill.drop_out` existed reports the ABSENCE and names
    the run that would fix it. It does NOT publish a bare 14.

    AND IT REFUSES A FUNNEL THAT DOES NOT ADD UP, rather than passing the producer's own failure
    through as a reading: `reconciles: false` upstream means the accounting is broken, and a
    broken account of the gap is worse on this page than an admitted absence.
    """
    drop = (method_skill or {}).get("drop_out") or {}
    if not drop.get("available"):
        return {
            "available": False,
            "reason": (
                "the run that produced this artefact predates the drop-out funnel, so the page "
                "can say how many decisions were scored but not why the rest were not. It is "
                "withheld until a run carries `method_skill.drop_out`."),
        }
    if not drop.get("reconciles"):
        return {
            "available": False,
            "reason": (
                "the run's own drop-out does not reconcile against the decisions it logged ("
                + str(drop.get("reconciliation") or "no reconciliation was reported")
                + "), so the funnel is withheld. An account of the gap that does not add up is "
                  "not evidence about the gap."),
        }
    by_class = drop.get("dropped_by_class") or {}
    reasons = drop.get("dropped_by_reason") or {}
    meanings = drop.get("what_each_reason_means") or {}
    return {
        "available": True,
        "priced_decisions": drop.get("priced_decisions"),
        "decisions_scored": drop.get("decisions_scored"),
        # ONE ROW PER REASON THAT ACTUALLY FIRED, largest first, each carrying the class that says
        # whether it is ours to widen. Reasons at zero are dropped from the page and kept in the
        # artefact: a reader wants the funnel, a reviewer wants the whole table.
        "by_reason": [
            {"reason": reason, "count": count,
             "class": (meanings.get(reason) or {}).get("class"),
             "means": (meanings.get(reason) or {}).get("means")}
            for reason, count in sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))
            if count and reason != "declined"
        ],
        "declined": reasons.get("declined"),
        "by_class": by_class,
        "what_each_class_means": drop.get("what_each_class_means"),
        # THE ANSWER, as a boolean a reader can check against the counts beside it rather than as
        # a sentence they have to take on trust.
        "the_sample_can_be_widened_from_this_book": bool(
            by_class.get("join") or by_class.get("coverage")),
        "reconciliation": drop.get("reconciliation"),
        "reading": drop.get("reading"),
    }


def _method_skill(three_arm: dict) -> dict:
    """A48's figure, and NEVER without the interval a random signal produces.

    FAIL-CLOSED ON A MISSING BOUND, which is the whole design. The first live reading was
    concordance 0.6136 on twelve decisions against a published null of exactly 0.5 -- a value a
    random signal reaches about one run in six. Publishing the point estimate without its spread
    would be the fourth time on 2026-08-28 that two correct figures went out with a relationship
    that is not a quantity, and this surface has already carried three of them.

    So: no `null_spread`, no number. An artefact produced before the spread existed reports the
    ABSENCE and says which run would fix it, rather than showing a bare 0.614 that reads as a
    result. The alternative -- recomputing the spread here from the artefact's own n and tie
    counts -- was rejected: it is arithmetically identical and creates a SECOND source for one
    figure, which is the shape this file's own clock and denominator defects both had.
    """
    ms = (three_arm or {}).get("method_skill") or {}
    if not ms.get("available"):
        return {"available": False,
                "reason": (ms.get("reason")
                           or "this run carried no method-skill reading")}
    spread = ms.get("null_spread") or {}
    if not spread.get("available"):
        return {
            "available": False,
            "withheld": True,
            "concordance_withheld": _f(ms.get("concordance")),
            "reason": (
                "the run that produced this artefact predates the null spread, so the figure "
                "would go out with a point null of 0.5 and no interval. It is withheld until a "
                "run carries `method_skill.null_spread`: " + str(
                    spread.get("reason") or "the spread is absent")),
        }
    return {
        "available": True,
        "concordance": _f(ms.get("concordance")),
        "null_point": _f(ms.get("null_constant_signal_concordance")),
        "null_95_low": _f((spread.get("null_95_interval") or [None, None])[0]),
        "null_95_high": _f((spread.get("null_95_interval") or [None, None])[1]),
        "p_two_sided": _f(spread.get("p_two_sided")),
        "inside_the_null": spread.get("observed_inside_the_null_interval"),
        "decisions_scored": ms.get("decisions_scored"),
        "accounts": ms.get("accounts"),
        # THE FUNNEL BETWEEN THE TWO COUNTS THIS PAGE SHOWS. `decisions.value_arm_priced` says 20
        # and `decisions_scored` says 6, a few hundred pixels apart, and until 2026-08-30 nothing
        # on the surface said why -- so the page implied the concordance rested on the 20.
        "drop_out": _skill_drop_out(ms),
        "churn_auc_for_contrast": _f(
            ((three_arm or {}).get("belief_vs_outcome") or {}).get("discrimination_auc")),
        # THE CONTRAST FIGURE CARRIES ITS OWN NULL, for the same reason the concordance beside it
        # does. This line published a bare 0.130 against a bounded 0.333 -- one number a reader
        # could weigh and one they could not, side by side, in a sentence inviting the comparison.
        "churn_auc_null": _auc_null(
            (((three_arm or {}).get("belief_vs_outcome") or {}).get("auc_population") or {})
            .get("retained"),
            (((three_arm or {}).get("belief_vs_outcome") or {}).get("auc_population") or {})
            .get("left"),
            ((three_arm or {}).get("belief_vs_outcome") or {}).get("discrimination_auc")),
        "what_it_is": (
            "Does the arm's own per-customer price rank the value JOINTLY created -- what the "
            "household kept plus what we kept, over what the household would have paid on the "
            "published default tariff? 0.5 is no information. Below 0.5 is a company ranking "
            "confidently and using the ranking to extract."),
        "reading": spread.get("reading"),
    }


#: WHAT THE HOUSEHOLD-SIDE FIGURE DOES NOT COVER, stated on the page beside the number rather
#: than owed to a design document. The mission names three currencies -- money, time and carbon --
#: and this figure reaches exactly one of them. Written out per currency because "money only" is
#: the kind of caveat a reader skims; "carbon is designed and never measured, time does not exist
#: anywhere in this project" is not.
HOUSEHOLD_EXCLUSIONS = [
    {"currency": "money", "state": "measured",
     "what": "What each household paid us over the settled periods that had a published default "
             "tariff to compare against, at its own metered volumes."},
    {"currency": "carbon", "state": "designed, never measured",
     "what": "A three-ledger carbon design exists (customer, portfolio, grid) and nothing "
             "instruments what a household's carbon actually did. No tonne below is counted "
             "because none is computed."},
    {"currency": "time", "state": "absent",
     "what": "No measure of a household's time, effort or hassle exists anywhere in this "
             "project -- not thinly built, absent. It is on the record as the one thing the "
             "mission asks for that has never been started."},
]

#: The one thing this figure is most likely to be read as, and is not. Same sentence the module
#: that computes it leads with, kept in the reader's words here.
HOUSEHOLD_IS_NOT = (
    "This is not value CREATED. Creation is a comparison of COSTS -- a supplier whose costs match "
    "the incumbent's and prices below it has moved margin to the household rather than made "
    "anything -- and a rival's costs are not observable to us. What is measured is how a surplus "
    "was SPLIT; the size of that surplus is not measured at all."
)

#: R12 again, on the household leg specifically. Publishing a figure is the moment it becomes
#: temptingly steerable, so the guard is named on the surface that publishes it.
HOUSEHOLD_NOT_A_TARGET = (
    "A diagnostic, not a target. Nothing in the company reads this figure and no decision is "
    "steered by it: a test bars every company organ, world module and pricing draw from importing "
    "it, and names what would release that -- a director decision on the two-sided objective."
)

#: Artefact arm key -> the key the arms panels already use. The two panels above key their arms
#: `control`/`value`/`level`; the run artefact keys them `*_arm`. Mapped in one place so the
#: renderer can put a household figure on the SAME ROW as the net margin it belongs beside, which
#: is the whole point of publishing it here rather than on a page of its own.
_HOUSEHOLD_ARM_KEYS = {"control_arm": "control", "value_arm": "value", "level_arm": "level"}


def _household(three_arm: dict) -> dict:
    """The household's side of each arm, in pounds -- the other column of the same comparison.

    WHY IT IS HERE AND NOT ON A PAGE OF ITS OWN. The mission's claim is that value is created and
    THEN shared, so every decision has two sides. Two sides on two pages is not that claim: a
    reader who meets our net margin on one surface and a household saving on another cannot tell
    whether an arm earned more BY creating more or BY keeping more of the same surplus. Same row,
    or the claim is not made.

    FAIL-CLOSED, and the absence names the run that fixes it (R15). A run whose artefact predates
    `household_side` reports the absence rather than a zero. That direction matters: a household
    saving of GBP 0 is the exact reading "we charged them the default tariff and shared nothing"
    produces, so a fail-open zero here would publish the worst possible answer as though it had
    been measured. `available: false` with a reason cannot be mistaken for it.

    NO ARM IS FILLED FROM ANOTHER. Each arm reads its own block; an arm the run did not execute is
    absent on this side too, exactly as it is on the company side.
    """
    blocks = (three_arm or {}).get("household_side")
    if not isinstance(blocks, dict) or not blocks:
        return {
            "available": False,
            "reason": (
                "the run that produced this artefact predates the household side, so no figure "
                "for what customers kept exists for these arms. It is published as soon as a run "
                "carries `household_side`: re-run `python3 -m tools.run_value_cycle_ab "
                "--level-arm`."),
            "excludes": HOUSEHOLD_EXCLUSIONS,
            "what_this_is_not": HOUSEHOLD_IS_NOT,
            "not_a_target": HOUSEHOLD_NOT_A_TARGET,
        }
    arms, basis = [], None
    for artefact_key, arm_key in _HOUSEHOLD_ARM_KEYS.items():
        side = blocks.get(artefact_key)
        if not isinstance(side, dict):
            continue
        meaning = ARM_MEANING[arm_key]
        if not side.get("available"):
            arms.append({"key": arm_key, "name": meaning["name"], "role": meaning["role"],
                         "household_saving_gbp": None,
                         "absent_reason": side.get("reason") or "this arm reported no household "
                                                                "side and gave no reason"})
            continue
        basis = basis or side.get("basis")
        arms.append({
            "key": arm_key,
            "name": meaning["name"],
            "role": meaning["role"],
            "household_saving_gbp": _f(side.get("household_saving_gbp")),
            "household_saving_pct_of_counterfactual": _f(
                side.get("household_saving_pct_of_counterfactual")),
            "paid_gbp": _f(side.get("paid_gbp")),
            "counterfactual_gbp": _f(side.get("counterfactual_gbp")),
            "household_share_of_the_split_pct": _f(
                side.get("household_share_of_the_split_pct")),
            # HOW MUCH OF THE BOOK THE COMPARISON REACHES. Gas before 2019 has no published
            # default tariff, so the early years are partly uncovered and the pounds above are
            # over the covered part only. Published rather than divided out.
            "coverage_pct": _f(side.get("coverage_pct")),
            "customer_years": side.get("customer_years"),
            "absent_reason": None,
        })
    if not any(a["household_saving_gbp"] is not None for a in arms):
        return {
            "available": False,
            "reason": ("the run carries a household side but no arm produced a figure, so nothing "
                       "is shown rather than a partial column"),
            "arms": arms,
            "excludes": HOUSEHOLD_EXCLUSIONS,
            "what_this_is_not": HOUSEHOLD_IS_NOT,
            "not_a_target": HOUSEHOLD_NOT_A_TARGET,
        }
    return {
        "available": True,
        "clock": "settled-realised",
        "basis": basis,
        "arms": arms,
        "what_it_is": (
            "What the households on each arm's book kept: what they would have paid on the "
            "published default tariff at their own metered volumes, less what they actually paid "
            "us. Charging a household the default tariff shows exactly nothing kept -- not a "
            "small number, zero -- which is what makes this column able to say that a price rise "
            "moved value rather than made it."),
        "excludes": HOUSEHOLD_EXCLUSIONS,
        "what_this_is_not": HOUSEHOLD_IS_NOT,
        "not_a_target": HOUSEHOLD_NOT_A_TARGET,
    }


#: The world's id scheme for an account the company did NOT start with: `PROS-*` is won by the
#: acquisition funnel, `SYN-*` is drawn by the curriculum. Used only as the FALLBACK, when the
#: artefact predates `renewal_funnel.*.by_account_class` -- that block classifies on the world's
#: own `acquisition_type` field and is preferred wherever it exists, because a prefix test reads
#: a renamed id as a founder account and says nothing about having done so.
_WON_OR_DRAWN_ID_PREFIXES: tuple[str, ...] = ("PROS-", "SYN-")
#: The classes in `by_account_class` that mean "the company did not start with this account".
_WON_OR_DRAWN_CLASSES: tuple[str, ...] = ("won_by_the_funnel", "drawn_by_the_curriculum")


def _who_the_method_has_priced(funnel: dict) -> dict:
    """Whether the method has ever priced a customer the company FOUND, and if not, why not.

    THE ENTERPRISE-VALUE CLAIM IS THAT THE ADVANTAGE COMES FROM INFERENCE OVER THE CUSTOMERS THE
    METHOD FINDS, and until 2026-08-30 no published surface could say whether it had ever priced
    one. The page already said the priced accounts are "one of the nine hand-seeded customers";
    what it did not say is the complement -- that the 90 accounts the acquisition funnel has won
    and the 69 the curriculum drew have never had a single renewal reach the arm, and that this
    is a GATE rather than a book size.

    DERIVED AND FAIL-CLOSED IN BOTH DIRECTIONS. The verdict is computed from the artefact's own
    two fields, not asserted: the moment one won or drawn account is priced, the structural
    sentence is unreachable and the page says the gate is passable instead. A conclusion that
    cannot change when the evidence changes is not a reading of the evidence, which is the defect
    `_headline_reading` was repaired for on this same page.
    """
    priced_accounts = [str(a) for a in (funnel.get("accounts_the_arm_priced") or [])]
    offered = funnel.get("accounts_the_world_offered_a_renewal")
    by_class = funnel.get("by_account_class") or {}
    if not priced_accounts or not isinstance(offered, int) or offered <= 0:
        return {
            "available": False,
            "reason": ("this run's funnel names no priced accounts, or no account denominator, "
                       "so nothing can be said about whose customers the method reached."),
        }
    if by_class.get("available"):
        classified = by_class.get("priced_accounts_by_class") or {}
        won_priced = sorted(account for name in _WON_OR_DRAWN_CLASSES
                            for account in (classified.get(name) or []))
        basis = "the world's own `acquisition_type`, via `renewal_funnel.by_account_class`"
    else:
        won_priced = sorted(a for a in priced_accounts
                            if a.startswith(_WON_OR_DRAWN_ID_PREFIXES))
        basis = ("the account id scheme (`PROS-*` won, `SYN-*` drawn), because this artefact "
                 "predates `by_account_class`")
    labels = funnel.get("product_not_upliftable_by_tariff_type") or {}
    unlabelled = labels.get("None") if isinstance(labels, dict) else None
    never_reached = offered - len(priced_accounts)

    # THE PREMISE, MEASURED RATHER THAN ASSERTED. The structural sentence turns on a claim about
    # the WORLD'S RECORDS -- that it renders `tariff_type = None` for every account it won or
    # drew -- and until 2026-08-30 that clause was a hardcoded string with nothing behind it. A
    # run's stage totals cannot establish it: `product_not_upliftable = 662` is consistent with
    # "this book happens to be unlabelled" and with "no book can be labelled", which are the two
    # readings the sentence exists to separate. `renewal_funnel.product_label_by_account_class`
    # counts the guard's own input off the roster the run bound.
    #
    # FAIL-CLOSED AND IN THE UNFLATTERING DIRECTION: a census that says a found account CAN reach
    # the gate demotes the verdict to `unresolved`, because at that point "structural" is refuted
    # by the roster whatever the stage totals still look like. An ABSENT census leaves the older
    # reading alone rather than silently upgrading it -- it is the state of every artefact
    # produced before this block existed.
    census = funnel.get("product_label_by_account_class") or {}
    gate_reachable = census.get("a_found_account_can_reach_the_product_gate")
    measured = census.get("available") is True and isinstance(gate_reachable, bool)

    if measured and gate_reachable and not won_priced:
        return {
            "available": True,
            "verdict": "unresolved",
            "priced_accounts": priced_accounts,
            "accounts_the_world_offered_a_renewal": offered,
            "accounts_never_reached_by_the_arm": never_reached,
            "won_or_drawn_accounts_priced": 0,
            "classification_basis": basis,
            "premise_basis": "measured on the roster this run bound",
            "sentence": (
                "The method has priced none of the {rest} accounts the company won or drew, and "
                "this run cannot call that a gate: the world DOES label some of the products it "
                "found ({names}), so a household the arm could price exists and none was. What "
                "limits this reading is the book, or something upstream of the product gate, and "
                "this surface will not name which without measuring it."
            ).format(rest=never_reached,
                     names=", ".join(census.get("found_accounts_the_guard_would_admit") or [])
                     or "count not published"),
            "what_is_owed": (
                "A funnel decomposition on the accounts the guard WOULD admit, to find which "
                "later stage refuses them. The structural reading is withdrawn, not weakened."),
        }

    if won_priced:
        verdict = "reached"
        sentence = (
            "The method has priced {n} account{s} the company found rather than started with "
            "({names}). The gate that used to refuse every won household is passable, so what "
            "limits this experiment now is book size, not eligibility."
        ).format(n=len(won_priced), s="" if len(won_priced) == 1 else "s",
                 names=", ".join(won_priced))
    elif isinstance(unlabelled, int) and unlabelled > 0 and len(labels) == 1:
        verdict = "structural"
        sentence = (
            "THE METHOD HAS NEVER PRICED A CUSTOMER THE COMPANY WON. Every renewal it priced "
            "belongs to one of {priced} accounts the company was founded with; the other {rest} "
            "accounts the world offered a renewal to have never had one reach the arm. That is a "
            "GATE, not a book size: all {unlabelled:,} renewals refused at the product gate carry "
            "`tariff_type = None`, which is what the world renders for every account it won or "
            "drew, while the founding accounts omit the field and take the `\"fixed\"` default -- "
            "and the arm admits only `fixed` and `pass_through` "
            "(`UPLIFTABLE_TARIFF_TYPES`, company/crm/customer_profitability.py, applied at "
            "company/pricing/value_based_renewal.py). No number of won households changes what "
            "that guard reads, so there is no book size at which the first one is priced."
        ).format(priced=len(priced_accounts), rest=never_reached, unlabelled=unlabelled)
    else:
        verdict = "unresolved"
        sentence = (
            "The method has priced none of the {rest} accounts the company won or drew, but this "
            "run's product gate refuses renewals under more than one label ({labels}), so this "
            "surface does not claim a single cause for it."
        ).format(rest=never_reached,
                 labels=", ".join(sorted(str(k) for k in labels)) or "none recorded")
    return {
        "available": True,
        "verdict": verdict,
        "priced_accounts": priced_accounts,
        "accounts_the_world_offered_a_renewal": offered,
        "accounts_never_reached_by_the_arm": never_reached,
        "won_or_drawn_accounts_priced": len(won_priced),
        "classification_basis": basis,
        # WHERE THE "no book size opens it" CLAUSE GETS ITS AUTHORITY. Published beside the
        # sentence rather than folded into it, because "measured on this run's roster" and
        # "argued from the code path" are different strengths of the same claim and a reader
        # deciding whether to spend a curriculum change on it needs to know which one they have.
        "premise_basis": (
            "measured on the roster this run bound: {n} of the accounts it won or drew carry an "
            "electricity product the guard would admit"
            .format(n=len(census.get("found_accounts_the_guard_would_admit") or []))
            if measured else
            "argued from the code path, not measured -- this artefact predates "
            "`renewal_funnel.product_label_by_account_class`"),
        "sentence": sentence,
        "what_is_owed": (
            "Not a relaxed guard. The world has no standard-variable product, so a won "
            "household's product was never decided rather than forgotten; the repair is that "
            "product, drawn from the published domestic fixed/SVT split, and it makes the "
            "in-scope surface SMALLER as a share of the book, not bigger "
            "(docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md, settled 2026-08-28)."),
    }


#: EVERY RUN THAT HAS MEASURED THE BELIEF'S RANK STATISTIC, newest first, each naming the artefact
#: it is read out of. Recorded here because the page published 0.13 as a fact about the company and
#: the SAME estimator, unchanged, has scored 0.646, 0.672, 0.465 and 0.465 in the four days before
#: it -- and no artefact on disk says so, because each run only ever publishes its own figure.
#:
#: `tests/tools/test_generate_value_arms_data.py::test_the_auc_history_matches_the_artefacts_it_cites`
#: re-reads each `artefact` that still exists and refuses if the figure recorded here has drifted
#: from it. An entry whose artefact has been archived stands as a dated record with its provenance
#: named; it is never silently repaired to whatever the newest run happens to say.
#:
#: `believed` and `realised` are `belief_vs_outcome.mean_believed_p_retain` and
#: `.realised_retention_rate` from the same artefact. They are carried because the LEVEL is what
#: refutes a label flip and the AUC is not: an inverted outcome label leaves the rank statistic's
#: DIRECTION wrong but moves the realised retention rate to its complement, so the two columns
#: together can be asked a question the AUC column alone cannot answer (`_polarity_check`).
AUC_RUN_HISTORY = [
    {"artefact": "docs/observability/value_cycle_ab_s1_three_arm.json", "on": "2026-08-29",
     "auc": 0.13, "scored": 20, "retained": 10, "left": 10, "median_margin": 60.0,
     "believed": 0.47876, "realised": 0.5},
    {"artefact": "docs/observability/value_cycle_ab_chase_off_2026-08-28.json", "on": "2026-08-28",
     "auc": 0.4652777777777778, "scored": 25, "retained": 16, "left": 9, "median_margin": 44.5,
     "believed": 0.562632, "realised": 0.64},
    {"artefact": "docs/observability/value_cycle_ab_resi_renewal_fixed.json", "on": "2026-08-27",
     "auc": 0.4652777777777778, "scored": 25, "retained": 16, "left": 9, "median_margin": 44.5,
     "believed": 0.562632, "realised": 0.64},
    {"artefact": "docs/observability/value_cycle_ab_resi_only.json", "on": "2026-08-26",
     "auc": 0.671875, "scored": 20, "retained": 16, "left": 4, "median_margin": 57.75,
     "believed": 0.78823, "realised": 0.8},
    {"artefact": "docs/observability/value_cycle_ab.json", "on": "2026-08-26",
     "auc": 0.6462585034013606, "scored": 28, "retained": 21, "left": 7, "median_margin": 60.0,
     "believed": 0.7041607142857143, "realised": 0.75},
]

#: How far a label flip must move a run's realised retention rate before that run is allowed to
#: speak to the polarity question. The flip sends a realised rate `r` to `1 - r`, a shift of
#: `|1 - 2r|`; at `r = 0.5` the shift is ZERO and the run is level-invariant under the very
#: transformation being tested. A margin rather than a strict `> 0` because the defect this guards
#: against makes the two sides EQUAL, and a strict inequality passes on 1e-16 of floating noise.
_POLARITY_SHIFT_MARGIN = 0.10

#: Above this many ordered pairs the exact null is not enumerated and the normal approximation is
#: used instead. The AUC populations this page has ever carried are 28 pairs at the largest, so the
#: exact branch is the live one; the cap exists so a bigger book cannot wedge a page render.
_EXACT_NULL_PAIR_CAP = 4000


def _auc_null(retained: int, left: int, observed: float | None) -> dict:
    """What a signal carrying NO information scores on a population this size, and where 0.13 sits.

    THE FIGURE WENT OUT UNBOUNDED. `discrimination_auc` was published with a reading that called
    it "worse than a coin flip" and nothing beside it said what a coin flip's own spread is on ten
    departures. The null sd of an AUC at 10-vs-10 is 0.132 -- so "0.13 against 0.50" is a distance
    of 2.8 null standard deviations, and "0.4653 against 0.50" is a distance of one THIRD of one.
    The page was reading the same distance from the same null in two directions.

    EXACT, NOT NORMAL, WHERE IT CAN BE. The Mann-Whitney null is enumerated by the usual recurrence
    over rank sums, because at n=10 the normal approximation's tail is exactly where the claim
    lives. Ties are not modelled: they can only move a count toward 0.5, so an interval computed
    without them is the WIDER one and the p-value the LARGER one -- the conservative direction, and
    it is stated rather than left for a reader to assume it went the other way.

    Returns `available: False` rather than a default when either outcome class is empty: a bound
    that could not be computed and a bound that came out wide must not render identically.
    """
    obs = _f(observed)
    if not isinstance(retained, int) or not isinstance(left, int) or retained < 1 or left < 1:
        return {"available": False,
                "reason": "one outcome class is empty, so no rank statistic and no null exist"}
    pairs = retained * left
    if obs is None:
        return {"available": False,
                "reason": "this run published no `discrimination_auc` to bound"}
    if pairs > _EXACT_NULL_PAIR_CAP:
        return {"available": False,
                "reason": ("the population is larger than the exact null this page enumerates "
                           "({} ordered pairs); no bound is published rather than a "
                           "normal-approximation one wearing an exact one's clothes".format(pairs))}

    # P(U = u) under the null, by the standard Mann-Whitney recurrence
    # `c(u; m, n) = c(u - n; m-1, n) + c(u; m, n-1)`, built iteratively so recursion depth cannot
    # be the limit. THE FIRST DRAFT OF THIS LOOP WAS WRONG and printing it at the real population
    # is what caught it: it gave every stayer an independent win count, which enumerates
    # (left+1)**retained arrangements and not C(retained+left, retained) -- 25,937,424,601 instead
    # of 184,756 at 10-vs-10, and a null interval of 0.30..0.70 instead of 0.24..0.76. The total is
    # asserted against the binomial coefficient below for exactly that reason: a null distribution
    # that is merely plausible is the shape that makes a bound look earned when it is not.
    table = [[[1] for _ in range(left + 1)] for _ in range(retained + 1)]
    for i in range(1, retained + 1):
        for j in range(1, left + 1):
            shifted, same = table[i - 1][j], table[i][j - 1]
            out = [0] * (i * j + 1)
            for u, c in enumerate(same):
                out[u] += c
            for u, c in enumerate(shifted):
                out[u + j] += c
            table[i][j] = out
    counts = table[retained][left]
    total = sum(counts)
    if total != math.comb(retained + left, retained):
        return {"available": False,
                "reason": ("the exact null enumerated {} arrangements where there are {}; the "
                           "bound is withheld rather than published from a distribution that "
                           "does not sum to the population it claims"
                           .format(total, math.comb(retained + left, retained)))}
    cumulative, running = [], 0
    for c in counts:
        running += c
        cumulative.append(running / total)

    u_obs = obs * pairs
    below = cumulative[min(int(u_obs), pairs)]
    at_or_above = 1.0 - (cumulative[max(int(u_obs) - 1, 0)] if u_obs >= 1 else 0.0)
    p_two_sided = min(1.0, 2.0 * min(below, at_or_above))
    lo = next(u for u in range(pairs + 1) if cumulative[u] > 0.025)
    hi = next(u for u in range(pairs, -1, -1) if 1.0 - cumulative[u - 1] > 0.025) if pairs else 0
    return {
        "available": True,
        "retained": retained,
        "left": left,
        "ordered_pairs": pairs,
        "null_point": 0.5,
        "null_95_low": lo / pairs,
        "null_95_high": hi / pairs,
        "p_two_sided": p_two_sided,
        "inside_the_null": lo / pairs <= obs <= hi / pairs,
        "basis": ("exact Mann-Whitney null over all {} arrangements of {} retained and {} departed "
                  "renewals; ties are not modelled, which widens the interval and enlarges the "
                  "p-value rather than shrinking either".format(total, retained, left)),
    }


def _polarity_check(history: list) -> dict:
    """Is 0.13 a flipped outcome label? ANSWERED FROM THE RUNS, not asserted in a docstring.

    WHY THIS IS COMPUTED AND NOT WRITTEN DOWN. The polarity branch was closed in prose by three
    legs, and only one of them reached the artefact: the grader's 0.6596 and 0.534 coming out
    ABOVE 0.5. That leg is the WEAKEST of the three for this figure, because
    `tools/grade_renewal_churn_belief.py::rank_auc` is a SEPARATE implementation grading a
    DIFFERENT belief on a DIFFERENT population -- a sign error living in
    `run_value_cycle_ab.belief_vs_outcome` would leave the grader entirely unaffected. A reader
    given only that leg is being asked to accept a conclusion whose reasons are not on the page.

    THE LEG THAT ACTUALLY BEARS ON THIS ESTIMATOR IS THE LEVEL, and the five runs in
    `AUC_RUN_HISTORY` all come out of the one code path. Flipping the outcome label sends a run's
    realised retention rate `r` to `1 - r` while leaving `mean_believed_p_retain` alone, so for
    each run there are two distances to compare: the one the artefact reports, and the one it
    would report under the flip. A flipped estimator would show the SECOND small and the first
    large. Every run where the flip moves anything shows the opposite.

    AND THE SUBJECT RUN CANNOT VOTE, which is the part the prose version got wrong. The
    2026-08-29 run scored exactly 10 retentions against 10 departures, so `r = 0.5`, `1 - r = 0.5`
    and its level gap is IDENTICAL under the flip -- it is invariant under the transformation
    being tested and carries no evidence about it either way. The refutation is carried by the
    runs that CAN discriminate and reaches 0.13 only because they share its code path. That is a
    weaker claim than "this run's labels are right" and it is the one the evidence supports, so it
    is what the field says (R15: a refusal must name a cause the checker actually observed).

    Fails CLOSED. A history that cannot discriminate returns `refuted: False` with the reason,
    never a default that reads like a pass.
    """
    rows = []
    for run in history or []:
        believed, realised = _f(run.get("believed")), _f(run.get("realised"))
        if believed is None or realised is None:
            continue
        shift = abs(1.0 - 2.0 * realised)
        level_gap = abs(believed - realised)
        flipped_gap = abs(believed - (1.0 - realised))
        rows.append({
            "on": run.get("on"),
            "artefact": run.get("artefact"),
            "auc": _f(run.get("auc")),
            "mean_believed_p_retain": believed,
            "realised_retention_rate": realised,
            "level_gap_as_published": level_gap,
            "level_gap_under_a_flipped_label": flipped_gap,
            "the_flip_moves_this_run_by": shift,
            "can_discriminate": shift >= _POLARITY_SHIFT_MARGIN,
            "favours_the_published_label": flipped_gap > level_gap,
        })

    voting = [r for r in rows if r["can_discriminate"]]
    silent = [r for r in rows if not r["can_discriminate"]]
    against = [r for r in voting if not r["favours_the_published_label"]]
    refuted = bool(voting) and not against

    if not rows:
        reason = "no run in the history carries the believed/realised pair this check needs"
    elif not voting:
        reason = ("every run in the history sits within {:.2f} of a 50/50 outcome split, so a "
                  "flipped label would move none of them and the level carries no evidence "
                  "either way".format(_POLARITY_SHIFT_MARGIN / 2))
    elif against:
        reason = ("{} of {} runs that can discriminate sit CLOSER to the flipped label than to "
                  "the published one. The polarity branch is NOT closed and the reading beside "
                  "this figure must not say it is.".format(len(against), len(voting)))
    else:
        reason = (
            "on all {v} runs whose outcome split is far enough from 50/50 for a flip to move "
            "anything, the believed retention sits within {near:.3f} of the realised rate and "
            "would sit {far:.3f} from it under a flipped label -- so the estimator's labels are "
            "the right way round. The 2026-08-29 run that scored {auc} is NOT one of the {v}: "
            "its outcome split is exactly even, which makes it invariant under the flip, so this "
            "leg reaches it through the shared code path rather than through its own "
            "numbers.".format(
                v=len(voting),
                near=max(r["level_gap_as_published"] for r in voting),
                far=min(r["level_gap_under_a_flipped_label"] for r in voting),
                auc=", ".join("{:.2f}".format(r["auc"]) for r in silent if r["auc"] is not None)
                    or "below the null"))

    return {
        "available": bool(rows),
        "refuted": refuted,
        "question": ("would an inverted outcome label in `belief_vs_outcome` produce this "
                     "figure? The rank statistic cannot say -- 0.13 is 0.87 flipped and both are "
                     "self-consistent -- but the LEVEL can, on any run whose outcomes are not an "
                     "even split."),
        "runs_that_can_discriminate": len(voting),
        "runs_that_cannot": len(silent),
        "shift_margin": _POLARITY_SHIFT_MARGIN,
        "reason": reason,
        "by_run": rows,
    }


def _belief_buckets(belief: dict) -> dict:
    """The believed-versus-realised table 0.13 is made of, at the granularity this run CAN carry.

    WHY THIS EXISTS. The page tells the reader the belief "ranked customers BACKWARDS" and then
    hands them a scalar. `_departures` is the check they should have -- which renewals -- and it
    is UNAVAILABLE on every artefact written before 2026-08-30, so on today's run the sentence is
    an assertion with nothing under it. `belief_vs_outcome.by_believed_bucket` has been in the
    artefact all along: four bands of believed retention with the realised rate in each. It is not
    the same evidence as the named departures and does not replace them, but it is the mechanism
    -- a reader can see the reversal instead of taking it on trust.

    IT DOES NOT SETTLE POLARITY, AND SAYS SO. Under a flipped outcome label this table reads
    monotone the RIGHT way and would look better than any belief on this page, so a reader who met
    it alone could reasonably conclude the labels are inverted. That is exactly the alternative
    `_polarity_check` closes on the LEVEL. Publishing the flipped column beside the real one is
    what stops this block quietly arguing the opposite of the one beside it.

    RECONCILED, NOT RESTATED (R15 contradiction check). The buckets' counts and `auc_population`
    tally the same 20 decisions by different routes. A run whose buckets do not sum to
    `retained + left` is describing a population the rank statistic was not computed over, and the
    table is withheld whole rather than published as a partial one -- the same refusal
    `_departures` makes against `matched_sample`, and for the same reason: a subset that renders
    is worse than an absence that explains itself.
    """
    rows = (belief or {}).get("by_believed_bucket")
    population = (belief or {}).get("auc_population") or {}
    scored = sum(v for v in (population.get("retained"), population.get("left"))
                 if isinstance(v, int))
    if not isinstance(rows, list) or not rows:
        return {"available": False,
                "reason": ("this artefact publishes no `belief_vs_outcome.by_believed_bucket`, so "
                           "the believed-versus-realised table behind this figure cannot be shown")}
    buckets = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        realised = _f(row.get("realised_retention_rate"))
        buckets.append({
            "believed_from": _f(row.get("believed_from")),
            "believed_to": _f(row.get("believed_to")),
            "n": row.get("n"),
            "mean_believed_p_retain": _f(row.get("mean_believed_p_retain")),
            "realised_retention_rate": realised,
            "realised_retention_rate_under_a_flipped_label":
                (None if realised is None else 1.0 - realised),
        })
    counted = sum(b["n"] for b in buckets if isinstance(b["n"], int))
    if not scored or counted != scored:
        return {"available": False,
                "reason": ("the believed-retention buckets count {} decisions and the rank "
                           "statistic's own population counts {}, so the two are not describing "
                           "one book and the table is withheld rather than published as a "
                           "slice".format(counted, scored or "none"))}
    return {
        "available": True,
        "scored": counted,
        "agrees_with_auc_population": True,
        "buckets": buckets,
        "reading": (
            "Read down the two rate columns. The band the arm was LEAST confident of keeping is "
            "the band that mostly stayed, and the renewals it was most confident of kept none of "
            "them -- that reversal IS the score, and it is what the figure above asserts. This "
            "table cannot tell you the labels are the right way round: flip them and it reads "
            "monotone the right way and looks better than any belief on this page, which is why "
            "the sign question is settled on the LEVEL beside it and not here. Every band is "
            "single-digit; nothing in this table carries a bound of its own."),
    }


def _departures(belief: dict) -> dict:
    """The renewals the AUC's positive class is made of, named -- or a stated absence.

    R15 FAIL-OPEN, the half-population shape. `matched_sample` is the first ten scored rows and
    has been in this artefact since the statistic was written; reading it as the population would
    let the page list "the departures" and name a slice, which is the version of this defect that
    LOOKS answered. `scored_decisions` is the whole list or it is not there.
    """
    rows = (belief or {}).get("scored_decisions")
    population = (belief or {}).get("auc_population") or {}
    left = population.get("left")
    if not isinstance(rows, list) or not rows:
        return {
            "available": False,
            "reason": ("this run predates `belief_vs_outcome.scored_decisions` (added 2026-08-30), "
                       "so the artefact carries only the first ten scored rows and the departures "
                       "behind this figure cannot be listed from it. The accounts the arm's own "
                       "price drove out ARE named above; the per-renewal list ships with the next "
                       "A/B run."),
        }
    departed = [r for r in rows if isinstance(r, dict) and r.get("retained") is False]
    return {
        "available": True,
        "count": len(departed),
        # THE CONTRADICTION CHECK, not a restatement. Two fields count this population by
        # different routes -- the rank statistic's own tally and the row list -- and a disagreement
        # means one of them is describing a book the other is not.
        "agrees_with_auc_population": (None if left is None else len(departed) == left),
        "departures": sorted(
            ({"account": r.get("account"), "term_start": r.get("term_start"),
              "believed_p_retain": _f(r.get("believed_p_retain")),
              "chosen_margin_gbp_per_mwh": _f(r.get("chosen_margin_gbp_per_mwh"))}
             for r in departed),
            key=lambda r: (str(r["account"]), str(r["term_start"]))),
    }


def _auc_attribution(three_arm: dict, belief: dict, priced_accounts: list) -> dict:
    """WHAT 0.13 IS. Attributed from the artefact and the grader, not argued.

    The figure moved from 0.4653 to 0.13 with nothing on the page attributing the move, and it was
    framed as corroborating the selection result. Three candidates were put to it, and the answer
    is the third with a mechanism the artefact itself carries:

      * A POLARITY OR LABEL DEFECT -- 0.13 is 0.87 inverted, and a strongly wrong estimator is the
        classic signature of a comparison taken against the wrong side of the outcome label.
        REFUTED THREE WAYS. (a) The chain reads right: `value_based_renewal._score` sets
        `p_stay = max(0.0, 1.0 - p_leave)`, `renewal_rate_chain` logs it as `believed_p_retain`,
        and `run_value_cycle_ab.belief_vs_outcome` ranks the STAYERS' scores above the LEAVERS',
        so a higher believed retention among the customers who stayed scores above 0.5. (b) The
        LEVEL would not survive an inversion, and this leg is now COMPUTED rather than asserted --
        see `_polarity_check`, published beside this block. It is the leg that bears on this
        estimator, because all five runs come out of this one code path. It also carries the
        caveat the prose version of it got wrong: the 2026-08-29 run's outcomes are an exactly
        even 10/10 split, so its own level is INVARIANT under the flip and it cannot vote on the
        question -- the three runs that can, do, unanimously. (c) The same rank statistic, run on
        2026-08-30 by `tools/grade_renewal_churn_belief.py` over the live run's 708 renewals,
        returns 0.6596 for `saas.churn_model.build_churn_risk` and 0.534 for the company-side
        `company_churn_estimate`. This leg CORROBORATES and does not decide: it is a separate
        implementation on a separate population, which a sign error in `belief_vs_outcome` would
        not touch.
      * AN INSTRUMENT DEFECT -- the population is simply unrankable, in which case a low AUC says
        nothing. REFUTED by the same grader run: the ORACLE CEILING, the world's own fully-adjusted
        `realized_churn_probability` graded by the same statistic, is 0.7618. The book ranks.
      * THE POPULATION. This is the answer, and it is not "small sample" on its own. 20 decisions
        sit on 10 accounts, all of them founding accounts, and FIVE of those ten appear in this
        run's own `churn_roster_diff.only_in_value_arm` -- accounts that left under the value arm
        and did NOT leave under the control. Half the positive class the belief is being graded
        against was manufactured by the arm's own price rise, at a median margin of 60.00 GBP/MWh
        against the control's 2.00. `believed_p_retain` is not a free-standing forecast of who
        will leave: it is the retention the arm expected AT THE PRICE IT CHOSE, scored against
        departures that price caused, on a book that same price thinned.

    R12: this block is a diagnostic about a diagnostic. Nothing here is a target and no constant
    moves from it.
    """
    belief = belief or {}
    population = belief.get("auc_population") or {}
    bound = _auc_null(population.get("retained"), population.get("left"),
                      belief.get("discrimination_auc"))
    roster = ((three_arm or {}).get("churn_roster_diff") or {}).get("only_in_value_arm") or []
    only_value = sorted({str(row.get("account")) for row in roster
                         if isinstance(row, dict) and row.get("account")})
    priced = sorted({str(a) for a in (priced_accounts or [])})
    caused = sorted(set(only_value) & set(priced))
    shape = (three_arm or {}).get("decision_shape") or {}
    return {
        "available": bound.get("available", False),
        "verdict": "the population, and the population is endogenous to the arm's own price",
        "null_bound": bound,
        # THE MECHANISM, NAMED IN ACCOUNTS THIS RUN CAN BE CHECKED AGAINST. Not "the sample is
        # small" -- that is true of every figure on this page and explains nothing about the
        # DIRECTION. These are the priced accounts whose departure the arm itself produced.
        "priced_accounts_the_arm_itself_drove_out": caused,
        # WHICH DEPARTURES, by name, when the run carries them. Every artefact produced before
        # 2026-08-30 publishes `matched_sample` -- the FIRST TEN scored rows -- and nothing else,
        # so the departures behind this AUC cannot be listed from it. Publishing the ten rows it
        # does have would be worse than publishing none: a reader would take a slice of the
        # population for the population. So this is an ABSENCE with the reason on it, and
        # `run_value_cycle_ab.belief_vs_outcome.scored_decisions` makes the next A/B run carry the
        # whole list.
        "the_departures": _departures(belief),
        # THE MECHANISM AT THE GRANULARITY THIS RUN HAS. `the_departures` is unavailable on every
        # artefact before 2026-08-30, which leaves "it ranked customers backwards" as a scalar the
        # reader must take on trust. The bucket table has always been in the artefact and shows
        # the reversal directly -- with the flipped column beside it, so it cannot be read as
        # settling the sign question that `polarity_check` settles on the level.
        "by_believed_bucket": _belief_buckets(belief),
        "priced_accounts": len(priced),
        "value_arm_only_churners": only_value,
        "median_margin_gbp_per_mwh": _f(shape.get("median_margin_gbp_per_mwh")),
        "control_margin_gbp_per_mwh": _f(shape.get("control_margin_gbp_per_mwh")),
        "history": AUC_RUN_HISTORY,
        # THE POLARITY LEG THAT BEARS ON THIS ESTIMATOR, COMPUTED. Until 2026-08-30 the polarity
        # branch was closed in the artefact by the grader alone -- a different implementation on a
        # different population, which a sign error in THIS estimator would not touch. The level
        # comparison across the runs that share this code path is the leg that does, and it now
        # ships as arithmetic a reader can check rather than as a sentence in a docstring.
        "polarity_check": _polarity_check(AUC_RUN_HISTORY),
        "independent_grade": {
            "graded_on": "2026-08-30",
            "tool": "tools/grade_renewal_churn_belief.py",
            "run_output": "docs/reports/run_output_latest.json",
            "renewals": 708,
            "accounts": 134,
            "bill_shock_model_auc": 0.6596,
            "company_churn_estimate_auc": 0.534,
            "oracle_ceiling_auc": 0.7618,
            "what_it_settles": (
                "The oracle ceiling at 0.7618 says this book IS rankable, so a low AUC is a "
                "statement about a belief and not about an unrankable population -- that is the "
                "instrument-defect branch closed, and this grader run is what closes it. The two "
                "graded beliefs at 0.6596 and 0.534 sit ABOVE a coin flip, which is CORROBORATING "
                "and not decisive on polarity: `tools/grade_renewal_churn_belief.py::rank_auc` is "
                "a separate implementation grading a different belief, so a sign error inside "
                "`run_value_cycle_ab.belief_vs_outcome` would leave these two figures untouched. "
                "The polarity branch is closed by `polarity_check` beside this block, which "
                "compares the level across the runs that share that estimator's code path. All "
                "three figures here are measured on a different run from the 0.13 -- 708 renewals "
                "over 134 accounts against 20 over 10 -- so none is a replacement figure for it, "
                "and none is quoted here as one."),
        },
        "reading": (
            "0.13 is not a sign error and not a broken instrument. It is what the arm's own "
            "retention belief scores on 20 decisions across 10 founding accounts, five of which "
            "the arm's price rise itself drove out. The quantity is not 'does this company know "
            "who will leave' -- it is 'did the arm predict who would survive the price it chose', "
            "graded on departures that choice caused."),
    }


def _auc_reading(belief: dict, attribution: dict) -> str:
    """The sentence a reader meets beside the figure, GATED ON THE FIGURE'S OWN BOUND.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. The reading this replaces was a constant string
    -- "Below 0.50 means the company's own belief ... ranks customers worse than a coin flip" --
    which meant the page read 0.4653 and 0.13 as the same finding when one sits a third of a null
    standard deviation from 0.5 and the other 2.8 of them, and would have read 0.49 the same way
    too. It composes from the interval instead, so a run whose book is finally large enough to
    earn a direction gets one with nobody editing a string, and a run that is not does not.

    AND THE ENDOGENEITY CLAUSE IS NOT GATED, because it is not a fact about the sample size. Half
    this population's departures were produced by the arm's own price rise; that stays true at any
    n, and a bigger book makes it a bigger problem rather than a smaller one.
    """
    bound = (attribution or {}).get("null_bound") or {}
    caused = (attribution or {}).get("priced_accounts_the_arm_itself_drove_out") or []
    priced = (attribution or {}).get("priced_accounts")
    observed = _f((belief or {}).get("discrimination_auc"))
    population = (belief or {}).get("auc_population") or {}

    endogeneity = ""
    if caused and priced:
        endogeneity = (
            " AND THE POPULATION IS NOT INDEPENDENT OF THE THING BEING GRADED: {n} of the {p} "
            "accounts this arm priced ({who}) left under the value arm and did NOT leave under "
            "the control, so the arm's own price rise -- a median {m} GBP/MWh against the "
            "control's {c} -- manufactured part of the very outcome the belief is scored against. "
            "`believed_p_retain` is the retention the arm expected AT THE PRICE IT CHOSE, not a "
            "free-standing forecast of who would leave.".format(
                n=len(caused), p=priced, who=", ".join(caused),
                m=attribution.get("median_margin_gbp_per_mwh"),
                c=attribution.get("control_margin_gbp_per_mwh")))

    if not bound.get("available"):
        return ("This figure is published WITHOUT a bound on this run ({}), so no direction is "
                "read from it here.{}".format(bound.get("reason", "reason not recorded"),
                                              endogeneity))

    head = ("Measured on {left} departures and {ret} retentions -- {n} decisions on {a} accounts. "
            "A signal carrying no information at all scores between {lo:.2f} and {hi:.2f} on a "
            "population this size (exact null, two-sided 95%).".format(
                left=bound["left"], ret=bound["retained"],
                n=(population.get("retained") or 0) + (population.get("left") or 0),
                a=priced if isinstance(priced, int) else "an unrecorded number of",
                lo=bound["null_95_low"], hi=bound["null_95_high"]))

    if bound.get("inside_the_null"):
        body = (" The observed value is INSIDE that interval, so this run does not distinguish "
                "the belief from a coin flip in either direction. That is a statement about how "
                "few decisions there are, not about the belief.")
    elif observed is not None and observed < 0.5:
        body = (" The observed value is OUTSIDE it and below the null (two-sided p {p:.3f}), so on "
                "this population the belief ranked customers BACKWARDS -- the renewals it was most "
                "confident of keeping are the ones that left.".format(p=bound["p_two_sided"]))
    else:
        body = (" The observed value is OUTSIDE it and above the null (two-sided p {p:.3f}), so on "
                "this population the belief carried real information about who "
                "stays.".format(p=bound["p_two_sided"]))
    return head + body + endogeneity


def _decisions(three_arm: dict) -> dict:
    """How many decisions the whole reading rests on, and how concentrated they are.

    The account names are read out of the artefact's own decision sample rather than restated
    from the design note that measured them, so this block cannot claim a population the run did
    not have.
    """
    shape = three_arm.get("decision_shape") or {}
    level_shape = three_arm.get("level_arm_decision_shape") or {}
    belief = three_arm.get("belief_vs_outcome") or {}
    bound = three_arm.get("bound_attribution") or {}
    credibility = three_arm.get("control_credibility") or {}
    book = (three_arm.get("book_identity") or {}).get("control_arm") or {}

    sample = [row for row in (belief.get("matched_sample") or [])
              + (belief.get("unmatched_sample") or []) if isinstance(row, dict)]
    accounts = sorted({str(row.get("account")).split("_")[0] for row in sample
                       if row.get("account")})

    priced = shape.get("priced")
    funnel = ((three_arm.get("renewal_funnel") or {}).get("value_arm") or {})
    offered = funnel.get("renewals_the_world_offered")
    exclusions = _exclusions(funnel)
    who = _who_the_method_has_priced(funnel)
    attribution = _auc_attribution(three_arm, belief, who.get("priced_accounts"))
    return {
        "available": isinstance(priced, int),
        "value_arm_priced": priced,
        "level_arm_priced": level_shape.get("priced"),
        "book_accounts_settled": book.get("billing_accounts_settled_in_window"),
        # THE DENOMINATOR IS RENEWALS, NOT ACCOUNTS, AND THE DIFFERENCE IS SIXFOLD.
        # This surface published "25 renewals ... out of a book of 210 settled accounts" until
        # 2026-08-28: a renewal numerator over an account denominator, which reads as ~12% of the
        # book when the arm in fact priced 2.07% of the renewals the world offered. The artefact
        # has carried `renewal_funnel.value_arm.renewals_the_world_offered` all along; nothing
        # read it. The account count stays, because how CONCENTRATED the decisions are is a
        # separate and also-true fact -- it just is not the coverage.
        "renewals_the_world_offered": offered,
        "priced_share_of_renewals_offered": funnel.get("priced_share_of_renewals_offered"),
        "why_the_rest_were_not_priced": exclusions,
        # HOW CONCENTRATED, which is a different fact from how much is COVERED and is why both
        # are published. Dropped by the 2026-08-28 denominator edit and caught by rendering the
        # panel rather than by reading the diff -- the page said "one of 0 ()".
        "accounts_named_in_the_decision_sample": accounts,
        # WHOSE customers those decisions are, which is a different question from how many there
        # are and is the one the enterprise-value claim turns on.
        "who_the_method_has_priced": who,
        "concentration_note": (
            "Every account the artefact names among its own scored decisions is one of the nine "
            "hand-seeded customers. WHY THE SURFACE IS SMALL, corrected 2026-08-28: this note "
            "used to name ONE eligibility guard -- the drawn population carrying no product "
            "label -- and conclude the surface was small by PLUMBING and not by design. The "
            "funnel says otherwise. " + _attribution_sentence(exclusions, offered) + " Giving "
            "the drawn population a product is a change to the baseline world, which R13 says is "
            "decided on fidelity evidence and never because it would make this experiment "
            "bigger."),
        "discrimination_auc": _f(belief.get("discrimination_auc")),
        # THE SAMPLE THE RANK STATISTIC IS COMPUTED OVER, published beside it. An AUC on
        # single-digit departures is a number with no bound, and this figure went out for four
        # days with a reading that called it "worse than a coin flip" and no interval to say what
        # a coin flip's own spread is on ten of them.
        "auc_population": {
            "retained": (belief.get("auc_population") or {}).get("retained"),
            "left": (belief.get("auc_population") or {}).get("left"),
            "scored_decisions": belief.get("priced_and_scored"),
            "accounts": len(accounts),
        },
        "auc_attribution": attribution,
        "auc_reading": _auc_reading(belief, attribution),
        "decided_by_a_bound": bound.get("decided_by_the_lawful_ceiling"),
        "bound_note": (
            "Some of the arm's prices were set by the lawful price cap rather than by anything "
            "about the customer. A win that came from a bound is not a win that came from "
            "inference."),
        "control_as_share_of_regulated_allowance": credibility.get("control_as_share_of_allowance"),
        "control_credibility_note": credibility.get("what_it_means"),
    }


#: Real dates the reaction probe is driven at, one per era of the record the arms run on: a
#: pre-crisis year, the 2022 spike, and the current cap regime. Three, not one, because a world
#: that reacts in a normal year and not in a crisis is a different claim from one that always
#: reacts, and a single date could not tell them apart.
_REACTION_PROBE_DATES = ("2019-04-01", "2022-04-01", "2024-04-01")

#: How far the reference must move before the move counts as a reaction, as a fraction of the cap.
#: NOT `!= 0`: a strict inequality between two floats is satisfied by 1e-16, so a world whose
#: rival is switched off but whose arithmetic rounds differently would read as a world that
#: competes (R15 -- the strict-inequality shape). Half a percent of the cap is roughly GBP 1/MWh,
#: which is a price move a household could actually be offered.
_REACTION_MATERIAL_PCT = 0.005


def _market_reaction(dates=_REACTION_PROBE_DATES) -> dict:
    """Whether the world these arms ran in could react to either of them -- PROBED, not asserted.

    THE DEFECT IT SERVES. The page compares two internal pricing policies and, until now, said
    nothing about whether anything in the world could answer either of them. The director wrote
    the bound himself in correction C2 (2026-08-28): *"'Beating the flat baseline' compares two
    internal policies in a market that could not react to either. That is a valid internal
    comparison and it is not evidence about a supplier's performance."* A comparison published
    without it invites exactly the reading it cannot support.

    WHY THIS IS PROBED AND NOT TYPED, which is the whole design. C2's sentence was true when it
    was written at 08:00 and was HALF FALSE by 08:25, when `simulation/competitor_reference.py`
    landed and gave the market the ability to defend. A hand-authored bound would now be
    publishing a correction to a defect that had already been half fixed -- understating the world
    on a page whose entire job is not to overstate it. So the two legs are established by driving
    the world's own reference function at real dates and reading what comes back:

      * DEFENDS -- undercut the market and does the reference follow the company down?
      * CONTESTS THE CEILING -- price above the cap and does the reference move at all?

    Measured 2026-08-28 at all three dates: undercutting by 10% leaves the company at -5.3%
    against the reference one quarter later (it defends), and pricing 20% above the cap returns
    the cap byte-identically (nothing contests it). That is the world `competitor_reference`'s own
    docstring describes: "This module is the defence leg. The ceiling leg is next."

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. When the ceiling leg lands, this probe returns
    `contests_the_ceiling=True` and the published sentence changes with it, in the same publish,
    with nobody editing a string. A bound pinned to today's answer would go stale in the
    flattering direction -- the page would keep apologising for a world that had stopped needing
    it -- and that is the failure this project has had repeatedly.

    FAILS CLOSED. If the probe cannot be run at all, the block says the world's reaction could not
    be established and the page still bounds the comparison. "We cannot tell" is a result; what it
    may never do is fall through to silence, which reads as a comparison that needs no bound.
    """
    try:
        from simulation.competitor_reference import (
            competitor_reference_rate_gbp_per_mwh as reference,
        )
        from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh as cap_rate

        legs = []
        for date_str in dates:
            cap = cap_rate(date_str)
            if not cap or cap <= 0:
                raise ValueError("no published cap for {}".format(date_str))
            # The unobserved reference: what the rival charges before it has seen this company at
            # all. Every measurement taken before the competitor landed was against this number,
            # so it is the right null to read both legs against.
            unobserved = reference(date_str, company_rate_gbp_per_mwh=None)
            undercut = reference(date_str, company_rate_gbp_per_mwh=cap * 0.9)
            over = reference(date_str, company_rate_gbp_per_mwh=cap * 1.2)
            if None in (unobserved, undercut, over) or unobserved <= 0:
                raise ValueError("the reference is unavailable at {}".format(date_str))
            legs.append({
                "date": date_str,
                "cap_gbp_per_mwh": round(float(cap), 2),
                "followed_a_10pct_undercut_to": round(float(undercut), 2),
                "answered_a_20pct_overcharge_with": round(float(over), 2),
                # What the company's -10% advantage has DECAYED to by the time the rival has
                # re-priced once. This is the number the defence leg is worth.
                "residual_advantage_pct": round(
                    (cap * 0.9 - undercut) / undercut * 100.0, 1),
                "defends": (unobserved - undercut) / unobserved > _REACTION_MATERIAL_PCT,
                "contests_the_ceiling":
                    abs(over - unobserved) / unobserved > _REACTION_MATERIAL_PCT,
            })
    except Exception as exc:  # noqa: BLE001 -- any failure here is "cannot establish", not "fine"
        return {
            "available": False,
            "reason": "the world's competitive reference could not be driven ({})".format(exc),
            "statement": (
                "WHETHER THE WORLD COULD ANSWER EITHER ARM COULD NOT BE ESTABLISHED for this "
                "publish, so read the comparison as an internal one. It says which of two "
                "in-house pricing policies earned more on this book; on its own it is not "
                "evidence about how this supplier would fare against real competitors."),
        }

    # ALL, not ANY, on both legs. A world that defends in a normal year and not in a crisis has
    # not got a competitor in it, it has got one sometimes -- and reporting that as "the market
    # defends" is the more flattering reading of the two.
    defends = bool(legs) and all(leg["defends"] for leg in legs)
    contests = bool(legs) and all(leg["contests_the_ceiling"] for leg in legs)
    decay = min((leg["residual_advantage_pct"] for leg in legs), default=None)

    return {
        "available": True,
        "defends": defends,
        "contests_the_ceiling": contests,
        "probed_at_dates": list(dates),
        "legs": legs,
        "statement": _reaction_sentence(defends, contests, decay),
    }


def _reaction_sentence(defends: bool, contests: bool, decay) -> str:
    """The bound a reader meets, COMPOSED from the probe's two legs and never from a date.

    Each clause is emitted only on the branch that earned it, so the page cannot say the market
    could not react while the probe says it defends -- which is precisely the sentence that would
    have shipped had this been typed out of C2 this morning.
    """
    opening = ("These are two of our own pricing policies, run through the same world. "
               "What that world could do about either of them is the bound on the comparison")
    if not defends and not contests:
        return (opening + ": nothing. No rival undercuts this company, none defends against it "
                "and none targets its book, so both arms were scored against an opponent that "
                "could not move. That is a valid comparison BETWEEN THE TWO POLICIES and it is "
                "not evidence about how this supplier would fare against real competitors.")
    # "half of one" is only true when exactly one leg holds. Printing all four branches at real
    # inputs before shipping is what caught this: the both-legs-true sentence read "it is
    # currently half of one" and then described a world that reacts on both.
    parts = [opening + (", and it is currently half of one." if defends != contests
                        else ", and the world can answer both.")]
    if defends:
        parts.append(
            "The market DOES defend: undercut it and the rival follows the price down within a "
            "quarter"
            + ("" if decay is None else
               ", so a 10% price advantage is worth {:+.1f}% by the time it has re-priced once"
               .format(decay))
            + ". A price advantage decays here instead of persisting.")
    else:
        parts.append("Nothing in the world defends: undercut the market and the rival does not "
                     "follow, so a price advantage persists for free.")
    if contests:
        parts.append("The ceiling is contested too: pricing above the cap moves the reference, "
                     "so charging more costs something.")
    else:
        parts.append(
            "Nothing contests the ceiling: at or above the published cap the reference does not "
            "move at all, so over-pricing still carries no competitive consequence in this world "
            "and no rival targets this book. An arm that earns by charging more is reading that "
            "absence correctly, which is a fact about the world and not a result about the arm.")
    parts.append("Read the comparison as an internal one.")
    return " ".join(parts)


def build(three_arm: dict | None, floor: dict | None,
          published_run: dict | None = None, decomposition: dict | None = None) -> dict:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    base = {
        "generated_at": now,
        "what_this_is": (
            "The same book and the same world, run once per pricing arm, scored on what actually "
            "happened. No figure here is anything the company believed."),
        "provisional": True,
        "provisional_note": PROVISIONAL_NOTE,
        "not_a_target": NOT_A_TARGET,
        "sources": [
            "docs/observability/value_cycle_ab_s1_three_arm.json",
            "docs/observability/value_cycle_ab_s1_noise_floor.json",
            "docs/observability/value_cycle_ab_floor_decomposition.json",
        ],
    }
    if not isinstance(three_arm, dict) or not three_arm:
        return dict(base, available=False, reason=(
            "The three-arm A/B artefact could not be read, so no comparison is shown rather than "
            "a partial one."))

    realised = _realised(three_arm, published_run)
    provisioned = _provisioned(three_arm)
    if not realised["available"] and not provisioned["available"]:
        return dict(base, available=False, reason=(
            "The A/B artefact carries neither a realised bridge nor a level-vs-selection split, "
            "so there is nothing to compare: " + realised.get("reason", "")))

    # THE FIGURE THE ERROR BAR IS A BAR ON, and it is the REALISED one. This line read
    # `provisioned.get("selection_gbp")` until 2026-08-29 while every row the floor's spread is
    # computed from comes out of `level_vs_selection`, which declares `settled-realised` -- so the
    # published ratio divided a realised spread by a provisioned estimate, and the "sits inside
    # that band" sentence answered about a figure the headline does not state. The two clocks are
    # £39,962.17 apart on this run, which is larger than every contrast on the page.
    #
    # `_split_on_the_realised_clock` returns available ONLY when the split declares
    # settled-realised, so taking the point from there makes the clock match a property of where
    # the figure came from rather than a claim made here. A run whose split is on another clock
    # yields None and the block says it has nothing to place -- it does not reach for the
    # provisioned figure, because a spread on one clock is not a bound on a figure from another.
    split = realised.get("split") or {}
    point = split.get("selection_gbp") if split.get("available") else None
    point_clock = split.get("clock") if split.get("available") else None
    # THE BOUND EVERY DIRECTIONAL CLAUSE OF THE HEADLINE IS GATED ON. Published in the same
    # payload as the sentence it gates so a reader can check the gate rather than take it, and so
    # the surface can never render a direction whose bound is not on the page with it.
    spreads = _seed_spreads(floor)
    return dict(
        base,
        available=True,
        contrast_bounds=spreads,
        # THE EVIDENCE UNDER THE REMEDY SENTENCE, in the same payload as the sentence, for the
        # reason `contrast_bounds` is: the page names a remedy beside its refusal, and a remedy is
        # a claim. A reader who wants to disagree with it needs the split it was derived from, not
        # a paraphrase of it. `available: false` is published too -- "not measured" is a state a
        # reader is entitled to see, and it is the state the page was in when it asserted one.
        floor_decomposition=(decomposition if isinstance(decomposition, dict)
                             else {"available": False,
                                   "why_not": ("no floor decomposition artefact was readable, so "
                                               "this page states no remedy")}),
        withdrawn_claim=_withdrawn(),
        run_generated_at=three_arm.get("generated_at"),
        book=(three_arm.get("book_identity") or {}).get("control_arm") or {},
        realised=realised,
        provisioned=provisioned,
        error_bar=_error_bar(floor, point, three_arm, point_clock),
        # THE BOUND ON THE WHOLE COMPARISON, and it is published in the same payload as the
        # figures it bounds so the two can never be deployed apart. Probed from the world's own
        # reference function rather than written down -- see `_market_reaction`.
        market_reaction=_market_reaction(),
        method_skill=_method_skill(three_arm),
        # THE OTHER SIDE OF THE ARMS ABOVE. Published in the same payload as the net margins,
        # keyed by the same arm keys, so the surface can render one row per arm with both
        # columns on it -- see `_household`.
        household=_household(three_arm),
        decisions=_decisions(three_arm),
        headline=(
            # The prefix is CONDITIONAL on the check below, and it is the whole reason the check
            # exists: this sentence is a claim about the supplier the rest of the site publishes,
            # so it may only be made while the published run and the baseline arm are the same run.
            ("The comparison below is against the very supplier this site publishes. " if
             (realised.get("is_the_published_supplier") or {}).get("same_supplier") else "")
            + _headline_reading(realised, provisioned, spreads, decomposition)
            + _coverage_clause(three_arm)),
    )


def _coverage_clause(three_arm: dict) -> str:
    """The bound, IN the headline rather than three paragraphs below it.

    A reader who meets "GBP 159,423 against GBP 154,699" first and the coverage later has already
    formed the impression. The funnel says the per-customer arm priced 25 of the 1,209 renewals
    the world offered -- 2.07% -- so the whole comparison is those decisions and what they cascade
    into, and that belongs in the same breath as the numbers.

    DERIVED, and SILENT when it cannot be derived: a run whose artefact carries no funnel gets no
    clause rather than a guessed one. An invented coverage sentence would be worse than none,
    because it is the sentence a reader would trust most.
    """
    funnel = ((three_arm or {}).get("renewal_funnel") or {}).get("value_arm") or {}
    priced = funnel.get("priced")
    offered = funnel.get("renewals_the_world_offered")
    share = funnel.get("priced_share_of_renewals_offered")
    if not isinstance(priced, int) or not isinstance(offered, int) or offered <= 0:
        return ""
    pct = (share * 100.0) if isinstance(share, (int, float)) else (100.0 * priced / offered)
    return (" Read all of it against its size: the per-customer arm priced {priced} of the "
            "{offered:,} renewals the world offered, {pct:.2f}% of them, so every figure here is "
            "those decisions and what they cascade into."
            ).format(priced=priced, offered=offered, pct=pct)


def _headline_reading(realised: dict, provisioned: dict, spreads: dict | None = None,
                      decomposition: dict | None = None) -> str:
    """The sentence the page leads with, DERIVED from the restated figures' own signs.

    THIS SENTENCE USED TO BE A CONSTANT (2026-08-28). It asserted that the level arm "earned as
    much or more again, so on this evidence the advantage is the price level and not the
    per-customer choosing" -- which was the honest reading of the run it was written against, and
    would have gone on being published word-for-word whatever the next run returned. A conclusion
    that cannot change when its evidence changes is not a reading of the evidence, and this is
    the one page on the site whose whole purpose is to be able to return an unflattering answer
    (R12). So the direction of the claim is now computed, and the losing case has a sentence.

    THE FLOOR IS ONLY HANDED TO THE READING IT WAS MEASURED ON (2026-08-29). Every seed contrast
    the noise floor carries is on the settled-realised clock, so the superseded fallback below
    gets NO bound -- and no bound means no direction, never a free one. Handing the realised
    spread to a provisioned figure would be the clock-mixing defect this file's two panels exist
    to keep apart, committed in the one place it would be hardest to see.
    """
    split = (realised.get("split") or {}) if realised.get("available") else {}
    if not split.get("available"):
        fallback = provisioned if provisioned.get("available") else {}
        selection = _f(fallback.get("selection_gbp"))
        if selection is None:
            return ("The arms ran, but this run did not produce a level-versus-selection "
                    "reading, so no claim is made about where any advantage came from.")
        clock_note = (" This is on the superseded clock -- see the panels below.")
        return _selection_sentence(selection, _f(fallback.get("level_share_of_advantage")),
                                   _f(fallback.get("value_advantage_gbp")), None,
                                   decomposition) + clock_note
    return _selection_sentence(split.get("selection_gbp"),
                               split.get("level_share_of_advantage"),
                               split.get("value_advantage_gbp"),
                               spreads, decomposition)


def _selection_sentence(selection, share, advantage=None, spreads=None,
                        decomposition=None) -> str:
    """What the per-customer CHOOSING was worth -- with a DIRECTION only when the figure is bigger
    than the spread the same figure shows across seeds, and its SIZE and BOUND when it is not."""
    selection = _f(selection)
    if selection is None:
        return ("The arms ran, but the value of the per-customer choosing could not be read, so "
                "no claim is made about it.")
    advantage_spread = _spread_for(spreads, "value_advantage_gbp")
    selection_spread = _spread_for(spreads, "selection_gbp")

    # THE SHARE IS A RATIO OF TWO CONTRASTS, AND ITS DENOMINATOR IS THE ARM'S OWN ADVANTAGE. When
    # that advantage is inside its own noise the share is a rounding error dressed as a
    # percentage -- on the 2026-08-29 run, -199% off a GBP 607 denominator whose seed spread is
    # +-GBP 990. The split already withholds it below GBP 1; this withholds it below the spread
    # actually measured for it, which is the bound that applies. Said out loud before dividing.
    share_clause = ("" if _f(share) is None
                    or _resolvable(advantage, advantage_spread) is not True else
                    " The price level accounts for {:.0%} of the per-customer arm's "
                    "advantage.".format(_f(share)))
    # THE FIRST CLAUSE IS DERIVED TOO, AND IT WAS NOT (2026-08-28). Both branches used to open
    # "earned more than flat rules" as a CONSTANT -- true of the run they were written against,
    # and FALSE on the run of 2026-08-28T12:37Z, where the per-customer arm earned GBP 4,724 LESS
    # than flat rules while the published headline said it earned more. The selection direction
    # had been made derived for exactly this reason and the arm-vs-control direction was left
    # behind, which is a half-finished repair rather than an oversight of a different kind.
    opening = _arm_vs_control_clause(advantage, advantage_spread)

    # NO DIRECTION WITHOUT A CONTRAST THAT EARNED ONE. Unknown is treated exactly as inside: a
    # missing spread is not evidence that the sign is safe to state.
    if _resolvable(selection, selection_spread) is not True:
        body = _cannot_resolve(
            selection, selection_spread,
            ("Once one flat margin at the same price LEVEL is given credit for what a level "
             "alone would have earned, £{:,.0f} separates the two").format(abs(selection)),
            "whether the per-customer choosing is worth anything at all, in either direction")
    elif selection < 0:
        body = ("Running it through ONE flat margin at the same price LEVEL earned "
                "£{:,.0f} more than the per-customer engine did{}. On this evidence the advantage "
                "is the price level, and the per-customer choosing is worth less than "
                "nothing.".format(abs(selection), _clears_its_floor(selection_spread)))
    else:
        body = ("Once one flat margin at the same price LEVEL is given credit for what a level "
                "alone would have earned, £{:,.0f} is left{}. On this evidence the choosing "
                "itself carried part of it.".format(selection,
                                                    _clears_its_floor(selection_spread)))

    # ONCE, AND ONLY WHEN SOMETHING WAS WITHHELD. A remedy printed beside a claim that WAS
    # resolved would read as an apology for a figure that earned its sign.
    # A contrast the run never reported is not a book-size problem, so it does not summon the
    # book-size remedy -- only a figure that EXISTS and did not clear its floor does.
    withheld = any(_f(value) is not None and _resolvable(value, spread) is not True
                   for value, spread in ((advantage, advantage_spread),
                                         (selection, selection_spread)))
    return "{} {}{}{}".format(
        opening, body, share_clause,
        " " + _what_would_resolve_it(decomposition).strip() if withheld else "")


def _cannot_resolve(value, spread, size_clause: str, what: str) -> str:
    """The sentence a contrast inside its own floor gets: the SIZE, the BOUND, and the refusal to
    state a sign. On the surface, never in a footnote.

    The REMEDY is not appended here. Both clauses of the headline can be withheld on the same run
    -- both were on 2026-08-29 -- and a remedy stapled to each printed the same forty words twice
    in one paragraph, which is how a sentence a reader needs becomes one they skip. The caller
    states it once, and only when something was actually withheld.

    THE REFUSAL NAMES ITS REASON, and the two reasons are different repairs. A contrast measured
    against a spread it does not clear is a book too small to answer the question; a contrast with
    no spread beside it at all is a floor nobody has run. Collapsing them would send the next
    reader to re-run seeds when what is owed is a bigger book, or the reverse.
    """
    if _f((spread or {}).get("stdev_gbp")) is None:
        return ("{size}. No seed spread has been measured for that contrast on this clock, so its "
                "DIRECTION is not stated here: on a comparison this size an unbounded sign is a "
                "coin toss reported as a finding.".format(size=size_clause))
    return ("{size} -- INSIDE the ±£{stdev:,.0f} that the same figure moves across {n} re-runs "
            "which changed nothing about the company but the per-household price-sensitivity "
            "draw. So this book CANNOT RESOLVE {what}.").format(
        size=size_clause, stdev=_f(spread.get("stdev_gbp")), n=spread.get("n"), what=what)


def _clears_its_floor(spread) -> str:
    """The bound, stated on the branch that DID earn its direction too -- a sign published without
    the spread it beat is the same unbounded figure, just one that happened to be large."""
    stdev = _f((spread or {}).get("stdev_gbp"))
    if stdev is None:
        return ""
    return ", clearing the ±£{:,.0f} this figure moves across {} seed re-draws".format(
        stdev, (spread or {}).get("n"))


def _arm_vs_control_clause(advantage, spread=None) -> str:
    """Did the per-customer arm beat flat rules, or not? Stated in the direction it came out --
    and ONLY when the gap is bigger than the gap seeds alone produce.

    UNKNOWN IS ITS OWN CASE. A run that cannot supply the arm's own advantage gets a sentence
    saying so, never the winning one by default -- defaulting to "earned more" is precisely the
    defect this function exists to close. A run that supplies it inside its own noise now gets a
    third: the size, the bound, and no sign. On 2026-08-29 that is £607 against a ±£990 seed
    spread, and "the per-customer engine earned £607 MORE" would have been a dice roll on the page.
    """
    advantage = _f(advantage)
    if advantage is None:
        return ("This run did not report what the per-customer decision engine earned against "
                "flat rules, so no claim is made about it.")
    # An exact tie is stated before the gate, because it is the one reading that names no
    # direction at all -- gating it would leave this branch unreachable, which is how a composer
    # grows a case nothing can ever print.
    if advantage == 0:
        return ("Running the same book through the per-customer decision engine earned exactly "
                "what flat rules did.")
    if _resolvable(advantage, spread) is not True:
        return _cannot_resolve(
            advantage, spread,
            ("Running the same book through the per-customer decision engine came out £{:,.0f} "
             "from flat rules").format(abs(advantage)),
            "which of the two earned more")
    if advantage > 0:
        return ("Running the same book through the per-customer decision engine earned "
                "£{:,.0f} MORE than flat rules{}.".format(advantage, _clears_its_floor(spread)))
    return ("Running the same book through the per-customer decision engine earned "
            "£{:,.0f} LESS than flat rules{}.".format(abs(advantage), _clears_its_floor(spread)))


def _read(path: Path):
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return loaded if isinstance(loaded, dict) else None


def generate(out_path: Path | None = None, three_arm_path: Path | None = None,
             noise_floor_path: Path | None = None,
             published_run_path: Path | None = None,
             decomposition_path: Path | None = None) -> dict:
    data = build(_read(THREE_ARM_PATH if three_arm_path is None else three_arm_path),
                 _read(NOISE_FLOOR_PATH if noise_floor_path is None else noise_floor_path),
                 _read(RUN_OUTPUT_PATH if published_run_path is None else published_run_path),
                 _read(DECOMPOSITION_PATH if decomposition_path is None
                       else decomposition_path))
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    d = generate()
    print("wrote {} (available={}, realised={}, error bar={})".format(
        OUT_PATH, d["available"],
        (d.get("realised") or {}).get("available"),
        (d.get("error_bar") or {}).get("available")))
