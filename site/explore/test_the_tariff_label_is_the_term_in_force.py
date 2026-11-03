"""The cast's tariff label is the term the bills record at the moment, and the storage slot shows heating.

Seventh cold read, N16: the customer's "Your tariff", the back office's "Tariff" and the renewal
message were read off "any renewal on record". A fix that rolled to the default tariff stayed
"Fixed" for years (SYN-2016-031 was told "Your fixed tariff is ending" four years into SVT), and a
joining fix showed as "Standard Variable". On the 0a6391d186 cast 2 of 21 billed moments agreed.

Graded against the household's own published bills (`term_tariff_type`), never against the
generator's reading of them, so a wrong reading in the generator cannot pass itself. Nothing here
names a household or a figure: those move with each run.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.generate_explore_cast import STORAGE_NIGHT_SHARE_FLOOR

HERE = Path(__file__).resolve().parent
FEED = HERE.parent / "data" / "explore_cast.json"
CUSTOMERS = HERE.parent / "data" / "customers"


def _accounts(hid: str) -> list[dict]:
    first = json.loads((CUSTOMERS / (hid + ".json")).read_text(encoding="utf-8"))
    out = [first]
    gid = (first.get("dual_fuel_combined") or {}).get("gas_account_id")
    if gid and (CUSTOMERS / (gid + ".json")).is_file():
        out.append(json.loads((CUSTOMERS / (gid + ".json")).read_text(encoding="utf-8")))
    return out


def _billed_term(accounts: list[dict], iso: str, before_renewal: bool) -> str | None:
    """The term every leg's bills record over `iso`, or None when no bill covers it, the legs differ,
    or a renewal on a leg falls inside its covering bill (the term changed mid-period). A renewal
    decision is made before that day's renewal, so a renewal ON `iso` changes nothing for it."""
    terms = set()
    for acc in accounts:
        cover = [i for i in acc.get("invoices") or [] if (i.get("document_type") or "bill") == "bill"
                 and (i.get("period_start") or i["date"]) <= iso <= (i.get("period_end") or i["date"])]
        if not cover:
            return None
        start = min(i.get("period_start") or i["date"] for i in cover)
        if any(e.get("type") == "renewed" and start < e["date"] and (e["date"] < iso or e["date"] == iso and not before_renewal)
               for e in acc.get("timeline") or []):
            return None
        terms |= {i.get("term_tariff_type") for i in cover}
    return terms.pop() if len(terms) == 1 and None not in terms else None


def _says(label: str | None) -> str | None:
    lab = (label or "").lower()
    return "fixed" if lab.startswith("fixed") else "svt" if lab.startswith("standard variable") else None


def disagreements(feed: dict) -> tuple[list[str], int]:
    """(every printed label that is not the billed term, how many billed moments were graded)."""
    bad, graded = [], 0
    for s in feed["slots"]:
        if not s.get("filled"):
            continue
        accounts = _accounts(s["household"])
        for m in s["moments"]:
            term = _billed_term(accounts, m["iso"], before_renewal=m["kind"] == "renewal_decision")
            if term is None:
                continue
            graded += 1
            office = next((r["v"] for r in m.get("supplier") or [] if r["k"] == "Tariff"), None)
            for side, label in (("customer", (m.get("portal") or {}).get("tariff")), ("back office", office)):
                if _says(label) != term:
                    bad.append("{} {} {}: the {} reads {!r}, the bills {}".format(
                        s["id"], s["household"], m["iso"], side, label, term))
            if m["kind"] == "renewal_decision" and "fixed tariff is ending" in (m.get("portal") or {}).get("message", "") \
                    and term != "fixed":
                bad.append("{} {} {}: told its fixed tariff is ending while billed on {}".format(
                    s["id"], s["household"], m["iso"], term))
    return bad, graded


@pytest.fixture(scope="module")
def feed() -> dict:
    assert FEED.is_file(), "the cast feed has never been generated (tools/generate_explore_cast.py)"
    return json.loads(FEED.read_text(encoding="utf-8"))


def test_every_printed_tariff_is_the_term_the_bills_record_at_that_moment(feed):
    """DEFECT: a label read off "a renewal is on record" (or any other proxy) instead of the term in
    force. The graded count is asserted first, so a check that grades nothing cannot pass."""
    bad, graded = disagreements(feed)
    assert graded > 0, "no cast moment has a bill covering it, so the label was never graded"
    assert not bad, "{} of the labels disagree with the billed term:\n".format(len(bad)) + "\n".join(bad)


def _actual_two_register(acc: dict, months=None) -> list[dict]:
    return [i for i in acc.get("invoices") or [] if len(i.get("registers") or []) > 1
            and i.get("read_type") == "A" and not i.get("catchup_applied")
            and (months is None or (i.get("period_start") or i["date"])[5:7] in months)]


def test_the_storage_slot_shows_a_home_whose_night_register_carries_its_heating(feed):
    """DEFECT: the slot filled on the meter alone (a two-register, profile class 2 home) at the
    average Economy 7 night split. An honestly empty slot names the failed checks instead."""
    slot = next(s for s in feed["slots"] if s["id"] == "storage_heating")
    if not slot["filled"]:
        assert slot.get("reason") and slot.get("failed_checks"), "an empty storage slot must name what it failed"
        return
    acc = next(a for a in _accounts(slot["household"]) if (a.get("commodity") or "electricity") == "electricity")
    bills = _actual_two_register(acc)
    assert _actual_two_register(acc, ("12", "01", "02")) and _actual_two_register(acc, ("06", "07", "08")), \
        "the slot's household has no actual-read winter and summer bill, so its night share is unmeasured"
    regs = [r for i in bills for r in i["registers"]]
    night = sum(r.get("consumption_kwh") or 0 for r in regs if (r.get("label") or "").lower() in ("night", "off-peak"))
    share = night / sum(r.get("consumption_kwh") or 0 for r in regs)
    assert share >= STORAGE_NIGHT_SHARE_FLOOR, "night share {:.0%} on actual reads".format(share)
    winter = [m for m in slot["moments"] if m.get("title") == "A winter bill"]
    assert winter and all("on an actual read" in m["story"] for m in winter), "the winter bill shown is not an actual read"
