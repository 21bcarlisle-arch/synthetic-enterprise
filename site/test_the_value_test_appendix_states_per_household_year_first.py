"""The appendix's value-test panels state each value-test figure per household per year FIRST.

Director's addendum of 13 Nov, item 1: "every value-test figure on the site is stated per household
per year first". `#arms-legs-first` and `#arms-redraw` are over the same run as
`current_world.per_household_year`, so they share its denominator. The defect named here is either
panel leading with a book total again, or printing a total in the per-year place when the feed
carries no per-year figure. `#arms-headline` and `#arms-split` are over ANOTHER run's book and
lead with that run's own `run_per_household_year`; `#arms-errorbar`'s seed family counts no
household-years, so it names that absence first.
"""
from __future__ import annotations

import copy
import html as html_lib
import json
import re
import subprocess
from pathlib import Path

import pytest
from test_the_published_bytes_reader import (
    published_file,
    published_json,
    refuse_working_tree_reads,
)

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/value_arms.json"
PANELS = ("arms-legs-first", "arms-redraw", "arms-headline", "arms-split", "arms-errorbar")
OTHER_FEEDS = ("dd_opening_arms", "engagement_separation", "billing_accuracy", "book_growth",
               "capabilities_door")


def test_this_control_never_reads_a_working_tree_copy_of_its_own_subjects():
    refuse_working_tree_reads(__file__, (DOOR_REL, FEED_REL)
                              + tuple("site/data/{}.json".format(n) for n in OTHER_FEEDS))


def _render(feed: dict) -> dict:
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- an unavailable check is a FAILED check")
    payload = {"../data/value_arms.json": feed}
    for name in OTHER_FEEDS:
        payload["../data/{}.json".format(name)] = published_json("site/data/{}.json".format(name))
    proc = subprocess.run(["node", str(HARNESS), str(published_file(DOOR_REL))],
                          input=json.dumps(payload), capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved") and not meta.get("scriptError"), meta
    return {k: re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ",
                                                            (out.get(k) or {}).get("innerHTML") or "")))
            for k in PANELS}


def _per_year(v: float) -> str:
    return ("+" if v > 0 else ("−" if v < 0 else "")) + "£{:.2f}".format(abs(v))


def test_both_panels_lead_with_the_per_household_year_figure_and_name_the_denominator():
    """MUTATION: render `signed(leg.figure_gbp)` before the per-year figure in `legsFirst` -> the
    ordering assert reds; drop the per-year line from a `redrawBand` cell -> the band assert reds;
    drop the denominator sentence -> the 1,831 assert reds."""
    feed = published_json(FEED_REL)
    phy = feed["current_world"]["per_household_year"]
    assert phy["available"], "the published feed states no per-household-year block to render"
    shown = _render(feed)
    legs, band = shown["arms-legs-first"], shown["arms-redraw"]
    choosing = _per_year(phy["choosing"]["gbp_per_household_year"])
    total = "£{:,}".format(round(abs(feed["current_world"]["selection_leg"]["figure_gbp"])))
    assert choosing + " per household per year" in legs
    assert legs.index(choosing) < legs.index(total), "the book total leads the per-year figure"
    years = "{:,}".format(phy["household_years"])
    assert years + " household-years" in legs and years + " household-years" in band
    for key in ("whole_advantage", "choosing", "price_level"):
        row = phy[key]
        assert _per_year(row["gbp_per_household_year"]) + "/yr" in band, key
        if row["redraw_band"]["available"]:
            assert _per_year(row["redraw_band"]["redraw_mean_per_household_year"]) + "/yr" in band


def test_a_feed_without_the_per_year_block_names_the_absence_and_never_promotes_the_total():
    """The partition's other side, reachable from the same feed. MUTATION: fall back to the total
    in the per-year place when the block is absent -> 'no per-household-year figure' is missing."""
    feed = copy.deepcopy(published_json(FEED_REL))
    feed["current_world"]["per_household_year"] = {"available": False, "why_not": "test: absent"}
    shown = _render(feed)
    assert "no per-household-year figure (test: absent)" in shown["arms-legs-first"]
    assert "no per-year figure" in shown["arms-redraw"]
    assert "/yr" not in shown["arms-redraw"]


def test_the_headline_run_panels_lead_with_their_own_runs_denominator_not_the_current_worlds():
    """MUTATION: divide the headline run by the current world's 1,831 -> the 1,029 assert reds;
    move the lead under the table in `#arms-split` -> the ordering assert reds; drop the error
    bar's named absence -> its assert reds."""
    feed = published_json(FEED_REL)
    rp = feed["run_per_household_year"]
    assert rp["available"] and rp["household_years"] != feed["current_world"][
        "per_household_year"]["household_years"], "the two books must be told apart"
    shown = _render(feed)
    years = "{:,} household-years".format(rp["household_years"])
    for panel in ("arms-headline", "arms-split"):
        assert "PER HOUSEHOLD PER YEAR, FIRST" in shown[panel] and years in shown[panel], panel
    assert "£{:.2f} per household per year".format(rp["realised"]["selection_size"]) in shown[
        "arms-headline"]
    split = shown["arms-split"]
    assert split.index("PER HOUSEHOLD PER YEAR, FIRST") < split.index("What we kept")
    assert "No per-household-year figure" in shown["arms-errorbar"]
    assert feed["error_bar_per_household_year"]["available"] is False


def test_a_headline_run_without_household_years_names_the_absence_in_the_per_year_place():
    feed = copy.deepcopy(published_json(FEED_REL))
    feed["run_per_household_year"] = {"available": False, "why_not": "test: uncounted"}
    shown = _render(feed)
    for panel in ("arms-headline", "arms-split"):
        assert "no per-household-year figure is stated for this run — test: uncounted" in shown[
            panel], panel
