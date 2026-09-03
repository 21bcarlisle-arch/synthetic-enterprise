"""The opening direct-debit comparison must reach the RENDERED page, not just the feed.

THE DEFECT IT SERVES. `company/billing/annual_consumption_estimate.py` landed on 2026-09-02 and
displaced a flat rule that opened every account's standing direct debit at its first issued bill.
The publishes either side of it carried identical net margin, gross, capital, treasury start and
end, enterprise value, net after cost-to-serve and bills issued — and that was read as "the organ
does nothing". It was not. A two-arm run over one seed moves three of the 104 figures the run
publishes, mean first-year review variance falls from 333.8% to 21.2%, and the estimate ends year
one closer to square for 80 of 96 matched households. Every one of those figures had no reader:
`annual_dd_review`, `dd_balance_book`, `dd_level_collection_book` and
`dd3_held_credit_balance_sheet` are run-output keys that `site/` never opened. The project had
already written the diagnosis into its own published data — *"TWO ARTEFACT KEYS HAVE NO BUSINESS
READER"* — and left it there.

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE JSON. Following
`test_the_baseline_comparison_reaches_the_reader.py`: a feed carrying a figure proves nothing about
whether a reader meets it, and this project has spent a day with a corrected sentence in the tree,
in the code, and not on the screen, with nothing red. So this drives the REAL door through its own
boot path with `site/_live_harness.mjs` and asserts on what the page actually rendered.

R15 — the mutations, each run and reverted:
  * delete the `ddopen-paired` render -> `test_the_paired_result_reaches_the_reader_with_its_bound`
    reds. This is the one that matters most: it is the only statistic here that holds the
    population fixed, and the unpaired means beside it are over two different populations.
  * render `withBound` as the bare mean -> `test_no_mean_reaches_the_reader_without_its_bound` reds.
  * sum credit and debit into one mean -> `test_credit_and_debit_reach_the_reader_as_two_rows` reds.
  * drop the `ddopen-why` render -> `test_the_reader_is_told_why_no_headline_figure_moved` reds.
  * drop the `ddopen-refused` render -> `test_the_refusals_reach_the_reader_with_their_cause` reds.
The null rung is `test_an_unavailable_feed_renders_an_absence_and_never_a_zero`: it must stay green
through all five, because every one of them is about what a reader meets, not about the feed.
"""
from __future__ import annotations

import html as html_lib
import json
import re
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "capabilities" / "index.html"
FEED = SITE / "data" / "dd_opening_arms.json"
ARMS = SITE / "data" / "value_arms.json"
GROWTH = SITE / "data" / "book_growth.json"
CAPS = SITE / "data" / "capabilities_door.json"

#: Every element this section renders into, so a section that renders half of itself is a red
#: rather than a silently thinner page.
PANELS = ("ddopen-headline", "ddopen-why", "ddopen-amounts", "ddopen-drift",
          "ddopen-paired", "ddopen-refused", "ddopen-basis", "ddopen-note")


def _text(fragment: str) -> str:
    """What a READER sees: tags stripped and entities decoded. Asserting on raw innerHTML reports
    a correct page red, because the door escapes everything through `esc()` before assigning."""
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict) -> dict:
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    payload = {
        "../data/dd_opening_arms.json": feed,
        "../data/value_arms.json": json.loads(ARMS.read_text(encoding="utf-8")),
        "../data/book_growth.json": json.loads(GROWTH.read_text(encoding="utf-8")),
        "../data/capabilities_door.json": json.loads(CAPS.read_text(encoding="utf-8")),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(DOOR)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    # The harness REJECTS a url the caller did not supply, deliberately, so a page driven with a
    # feed missing runs its real error path rather than a vacuous one. Asserted here as well as
    # in the sibling door tests because a door that grows a fifth feed must red on this control
    # too, not only on theirs.
    assert not meta.get("unresolved"), (
        "the door asked for a feed this test did not supply ({}), so whatever it rendered is not "
        "what a browser would".format(meta.get("unresolved")))
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    rendered = {}
    for panel in PANELS:
        element = out.get(panel) or {}
        rendered[panel] = _text(element.get("innerHTML") or "") or _text(
            element.get("textContent") or "")
    return rendered


def _live_feed() -> dict:
    if not FEED.is_file():
        pytest.fail("site/data/dd_opening_arms.json is missing -- the published comparison has no "
                    "feed, reported as a failure and never skipped")
    return json.loads(FEED.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def live() -> dict:
    feed = _live_feed()
    if not feed.get("available"):
        pytest.fail("the published opening-DD comparison is unavailable ({}), so the door renders "
                    "no comparison and this control cannot run".format(feed.get("reason")))
    return _render(feed)


def _gbp(value: float) -> str:
    return ("-£" if value < 0 else "£") + "{:.2f}".format(abs(value))


def test_both_arms_opening_amounts_reach_the_rendered_page(live):
    """DEFECT: the page publishes the new rule's figure and not the one it displaced.

    A figure without the baseline it beat is the exact claim the director's thesis refuses:
    "it performed well" against nothing means nothing.
    """
    feed = _live_feed()
    oa = feed["opening_amount"]
    rendered = live["ddopen-amounts"]
    assert _gbp(oa["flat"]["mean_gbp"]) in rendered, (
        "the DISPLACED rule's opening amount is not on the page a reader opens")
    assert _gbp(oa["estimate"]["mean_gbp"]) in rendered, (
        "the estimate's opening amount is not on the page a reader opens")


def test_no_mean_reaches_the_reader_without_its_bound(live):
    """DEFECT: a point estimate published bare reads as a precision the sample has not earned."""
    feed = _live_feed()
    rendered = live["ddopen-amounts"]
    for arm in ("flat", "estimate"):
        low, high = feed["opening_amount"][arm]["ci95_gbp"]
        assert _gbp(low) in rendered and _gbp(high) in rendered, (
            "the {} arm's mean opening amount reaches the reader without the 95% interval its "
            "sample size earns".format(arm))


def test_credit_and_debit_reach_the_reader_as_two_rows(live):
    """DEFECT: netting the two into one average describes neither household.

    A household in credit is owed money by us; one in debit owes us. Different populations,
    different triggers, different remedies — CLAUDE.md's most expensive recurring shape.
    """
    feed = _live_feed()
    dr = feed["year_one_drift_matched"]
    rendered = live["ddopen-drift"]
    for arm in ("flat", "estimate"):
        assert _gbp(dr[arm]["in_credit"]["mean_gbp"]) in rendered, (
            "the {} arm's IN-CREDIT households do not reach the reader".format(arm))
        assert _gbp(dr[arm]["in_debit"]["mean_gbp"]) in rendered, (
            "the {} arm's IN-DEBIT households do not reach the reader".format(arm))
    assert "in credit" in rendered.lower() and "in debit" in rendered.lower(), (
        "the two populations are not named on the page, so a reader cannot tell which is which")


def test_the_paired_result_reaches_the_reader_with_its_bound(live):
    """DEFECT: the only population-matched statistic is the one that goes missing.

    The unpaired means beside it are over two different populations — the estimate arm refuses
    every pre-2019 account — so a page carrying only those attributes the refusal to the rule.
    """
    feed = _live_feed()
    dr = feed["year_one_drift_matched"]
    rendered = live["ddopen-paired"]
    assert str(dr["n_estimate_closer_to_zero"]) in rendered, (
        "how many households the estimate actually helped does not reach the reader")
    assert str(dr["n_matched_accounts"]) in rendered, (
        "the matched population size does not reach the reader, so the count above it is a "
        "fraction of nothing")
    low, high = dr["mean_change_in_abs_drift_ci95_gbp"]
    assert _gbp(abs(low)) in rendered and _gbp(abs(high)) in rendered, (
        "the paired improvement reaches the reader without its 95% interval")


def test_the_refusals_reach_the_reader_with_their_cause(live):
    """DEFECT: a fail-closed organ whose refusals are invisible reads as one with nothing to
    refuse. 82 accounts carry no direct debit at all, and a reader who cannot see that count
    reads the drift table as covering the whole book."""
    feed = _live_feed()
    rendered = live["ddopen-refused"]
    assert str(feed["refused"]["n"]) in rendered, (
        "the count of accounts the supplier refused to open does not reach the reader")
    assert "2019" in rendered, "the refusal reaches the reader without naming its cause"


def test_the_reader_is_told_why_no_headline_figure_moved(live):
    """DEFECT: a reader meets two identical net-margin figures and concludes the organ is inert.

    The published treasury is a running total of net margin, so no direct-debit arrangement can
    move it. Without that sentence this section contradicts every headline on the site.
    """
    rendered = live["ddopen-why"]
    assert "treasury" in rendered.lower(), (
        "the page does not tell the reader why the headline cash figure cannot move")
    assert rendered, "the explanation element rendered nothing at all"


def test_the_unreached_information_sources_reach_the_reader_as_zeros(live):
    """DEFECT: publishing only the source that WAS used hides that three of four are unreachable.

    SLC 27.15 orders four sources best-first. This book reaches exactly one, and a split that
    printed only the non-zero row would present a precedence as if it had been exercised.
    """
    rendered = live["ddopen-basis"]
    for phrase in ("meter reads", "customer told us", "typical values"):
        assert phrase in rendered, (
            "the unreached source '{}' is not named on the page, so its zero is invisible".format(
                phrase))


def test_the_money_on_this_page_carries_its_clock(live):
    """DEFECT: a financial figure published without its clock (R14). These come from issued bills,
    not settlement, so they cannot be reconciled against a settled-realised headline and a reader
    who tries will find a discrepancy that is not one."""
    feed = _live_feed()
    assert feed["clock"] in live["ddopen-note"], (
        "the section publishes money without naming the clock it is on")
    assert str(feed["n_bills"]) in live["ddopen-note"], (
        "the section does not state how much evidence it was measured over")


def test_an_unavailable_feed_renders_an_absence_and_never_a_zero():
    """THE NULL RUNG. An unavailable comparison must say so in words. A rendered £0, or an empty
    table, reads as "we ran it and found no difference" — the precise misreading that made this
    whole item necessary."""
    rendered = _render({"available": False, "reason": "no two-arm measurement for this publish"})
    assert "absent" in rendered["ddopen-note"].lower(), (
        "an unavailable comparison does not announce itself as absent")
    assert "no two-arm measurement for this publish" in rendered["ddopen-note"], (
        "the absence reaches the reader without the reason for it")
    for panel in ("ddopen-headline", "ddopen-amounts", "ddopen-drift", "ddopen-paired"):
        assert not rendered[panel], (
            "{} rendered content off an unavailable feed -- a figure with no measurement behind "
            "it is worse than no figure".format(panel))
