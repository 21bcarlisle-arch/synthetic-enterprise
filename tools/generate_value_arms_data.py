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
                       the headline the rest of the site carries. Only two arms are on it: the
                       artefact's gross-to-net bridge walks control and value, never the level
                       arm, so the level arm's realised net is NOT RECOVERABLE from this run and
                       is published as absent with its reason -- never inferred, never omitted.

  settled-provisioned  the frozen scalars. The level-vs-selection split is computed on these, so
                       it is published on these, labelled superseded, with the artefact's own
                       statement that the split does not survive restatement unchanged.

A reader who meets one number without the other cannot tell which supplier the site is
publishing. Both, or neither.

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
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
THREE_ARM_PATH = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"
NOISE_FLOOR_PATH = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor.json"
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
    """The two arms the artefact's gross-to-net bridge actually walked, on the site's own clock.

    The level arm is absent here and that absence is PUBLISHED. `gross_to_net_bridge` sums the
    control and value arms from the mutated rows and never the level arm, so its realised net
    cannot be recovered from this file. Deriving it from the frozen scalar would silently mix the
    two clocks -- the exact defect the artefact was repaired for on 2026-08-28.
    """
    bridge = three_arm.get("gross_to_net_bridge") or {}
    control = _f((bridge.get("control_arm") or {}).get("net_margin_gbp"))
    value = _f((bridge.get("value_arm") or {}).get("net_margin_gbp"))
    delta = _f(bridge.get("net_delta_gbp"))
    if control is None or value is None or delta is None:
        return {"available": False,
                "reason": "the artefact carries no gross-to-net bridge, so no arm can be put on "
                          "the realised clock"}
    return {
        "available": True,
        "clock": "settled-realised",
        "clock_means": CLOCK_MEANING["settled-realised"],
        "arms": [
            _arm("control", control),
            _arm("value", value, advantage_gbp=delta),
            _arm("level", None, absent_reason=(
                "Not recoverable on this clock. The run's gross-to-net bridge walks the control "
                "and per-customer arms only, so the level arm's realised bad debt was never "
                "summed. It is left blank rather than filled from the superseded figure.")),
        ],
        "is_the_published_supplier": _is_the_published_supplier(control, published_run),
    }


def _provisioned(three_arm: dict) -> dict:
    """The three-arm split, on the clock it was computed on, carrying its own supersession."""
    lvs = three_arm.get("level_vs_selection") or {}
    if not lvs.get("available"):
        return {"available": False,
                "reason": "the run did not produce a level-vs-selection split ({})".format(
                    lvs.get("share_undefined_reason") or "no reason given")}
    control = _f(lvs.get("control_net_gbp"))
    value = _f(lvs.get("value_arm_net_gbp"))
    level = _f(lvs.get("level_arm_net_gbp"))
    value_adv = _f(lvs.get("value_advantage_gbp"))
    level_adv = _f(lvs.get("level_advantage_gbp"))
    selection = _f(lvs.get("selection_gbp"))
    share = _f(lvs.get("level_share_of_advantage"))
    if None in (control, value, level, value_adv, level_adv, selection):
        return {"available": False,
                "reason": "the level-vs-selection block is incomplete, so the split is withheld "
                          "rather than part-published"}
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
        "level_gbp_per_mwh": _f(lvs.get("level_gbp_per_mwh")),
        "control_gbp_per_mwh": _f(shape.get("control_margin_gbp_per_mwh")),
        "superseded_note": (
            "This split is on the clock the run superseded inside itself. Restating it on the "
            "realised clock drops the per-customer arm's advantage from £{va:,.0f} to the "
            "realised figure above, so the level share does not survive the restatement "
            "unchanged -- and the level arm's realised net is not recoverable from this run, so "
            "the restated share cannot be computed from it either. It is published as it was "
            "measured, labelled, rather than quietly re-based.".format(va=value_adv)),
    }


def _error_bar(floor: dict, point_estimate) -> dict:
    """The seed spread on the selection leg -- the reason the point estimate cannot be quoted bare.

    NEVER fails open to a spread of zero: a spread of zero is the one value that would make an
    indistinguishable result read as a decisive one.
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
        "elasticity_draws_min": min(draws) if draws and all(
            isinstance(d, int) for d in draws) else None,
        # No range restated here: the surface renders the min and max in its own sentence, and a
        # second copy of the same two figures is where a rounding convention drifts between them.
        "reading": (
            "The point estimate sits inside that band and so does zero, so this instrument cannot "
            "yet resolve a selection effect of the size it is measuring -- in either direction. "
            "That is a finding about the INSTRUMENT and not about the pricing arm, and it is not "
            "a cue to re-run until a seed agrees."),
    }


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
    return {
        "available": isinstance(priced, int),
        "value_arm_priced": priced,
        "level_arm_priced": level_shape.get("priced"),
        "book_accounts_settled": book.get("billing_accounts_settled_in_window"),
        "accounts_named_in_the_decision_sample": accounts,
        "concentration_note": (
            "Every account the artefact names among its own scored decisions is one of the nine "
            "hand-seeded customers. The drawn population is refused by one eligibility guard: it "
            "carries no product label, and the arm correctly declines to re-price a product it "
            "cannot name. So the surface is small by PLUMBING, not by design -- and giving the "
            "drawn population a product is a change to the baseline world, which R13 says is "
            "decided on fidelity evidence and never because it would make this experiment "
            "bigger."),
        "discrimination_auc": _f(belief.get("discrimination_auc")),
        "auc_reading": (
            "Below 0.50 means the company's own belief about who will leave ranks customers worse "
            "than a coin flip. An estimator that cannot rank cannot select profitably, so the "
            "selection result and the belief result corroborate each other rather than merely "
            "coexisting."),
        "decided_by_a_bound": bound.get("decided_by_the_lawful_ceiling"),
        "bound_note": (
            "Some of the arm's prices were set by the lawful price cap rather than by anything "
            "about the customer. A win that came from a bound is not a win that came from "
            "inference."),
        "control_as_share_of_regulated_allowance": credibility.get("control_as_share_of_allowance"),
        "control_credibility_note": credibility.get("what_it_means"),
    }


def build(three_arm: dict | None, floor: dict | None,
          published_run: dict | None = None) -> dict:
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

    point = provisioned.get("selection_gbp") if provisioned["available"] else None
    return dict(
        base,
        available=True,
        run_generated_at=three_arm.get("generated_at"),
        book=(three_arm.get("book_identity") or {}).get("control_arm") or {},
        realised=realised,
        provisioned=provisioned,
        error_bar=_error_bar(floor, point),
        decisions=_decisions(three_arm),
        headline=(
            # The prefix is CONDITIONAL on the check below, and it is the whole reason the check
            # exists: this sentence is a claim about the supplier the rest of the site publishes,
            # so it may only be made while the published run and the baseline arm are the same run.
            ("The comparison below is against the very supplier this site publishes. " if
             (realised.get("is_the_published_supplier") or {}).get("same_supplier") else "")
            + "Running the same book through the per-customer decision engine earned more -- and "
            "running it through one flat margin at the same LEVEL earned as much or more again, "
            "so on this evidence the advantage is the price level and not the per-customer "
            "choosing."),
    )


def _read(path: Path):
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return loaded if isinstance(loaded, dict) else None


def generate(out_path: Path | None = None, three_arm_path: Path | None = None,
             noise_floor_path: Path | None = None,
             published_run_path: Path | None = None) -> dict:
    data = build(_read(THREE_ARM_PATH if three_arm_path is None else three_arm_path),
                 _read(NOISE_FLOOR_PATH if noise_floor_path is None else noise_floor_path),
                 _read(RUN_OUTPUT_PATH if published_run_path is None else published_run_path))
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
