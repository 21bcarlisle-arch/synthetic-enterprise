"""Regression test for docs/staging/BILL_CORRECTNESS_ADDENDUM.md Defect 1
(director-found, 2026-07-08): C6 (a real SME account, correctly billed at
20% business VAT and ~28 MWh/yr -- both consistent with its true segment)
rendered on the customer portal as "Household / Residential".

Root cause: site/customers/index.html's fuelBadges()/renderHousehold() had
a binary I&C-vs-everything-else badge check and an unconditional "Household"
label, so the real "SME" segment value silently fell into the Residential
branch. customer_sample.json's segment field, and the VAT/consumption
figures derived from it (saas/non_commodity.py), were already correct --
this was a pure render-layer bug, not a data or billing-calculation bug.

No `node` available this session (see test_billing_tab_fix.py for the
established substitute pattern this test follows): a static guard that
every real segment value is listed explicitly (so a new segment can't
silently fall through to Residential again), plus a faithful Python port
of segmentInfo() executed against every account in the live customer
sample, asserting label/badge agree with the true segment for every one,
not just C6.
"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
CUSTOMER_SAMPLE = PROJECT / "site" / "data" / "customer_sample.json"

# The two STATIC guards that read site/customers/index.html were removed 2026-08-22: that page was
# deleted by the director's ruling in 03dd8c49e (2026-08-20) and no site HTML carries SEGMENT_BADGE
# or the hh-label markup now. NOTE THE COST HONESTLY -- those two were the half of this file that
# checked the PAGE agreed with the port below, so the "kept in sync so this test breaks if the two
# diverge" promise in _segment_info's docstring no longer has a second side to diverge from. The
# port is now a specification of segment labelling with no renderer to contradict it, and the live
# check that remains is that every sampled account's segment resolves to a consistent label.


def _segment_info(segment):
    """Python port of segmentInfo()'s SEGMENT_BADGE lookup from the former
    site/customers/index.html. The page is gone (03dd8c49e); this is now the
    sole statement of the mapping rather than a mirror of one."""
    table = {"I&C": ("bi", "I&C"), "SME": ("bs", "SME"), "resi": ("br", "Residential")}
    return table.get(segment, table["resi"])


def test_every_sampled_account_gets_a_label_consistent_with_its_true_segment():
    """The actual sweep BILL_CORRECTNESS_ADDENDUM.md asks for ("not just
    C6"): every account in the live customer sample must render a badge
    that matches its true segment field, and only the true resi segment may
    show "Household" -- SME and I&C must show "Business"."""
    data = json.loads(CUSTOMER_SAMPLE.read_text())
    customers = data["customers"]
    assert customers, "customer_sample.json has no accounts to sweep"

    checked_segments = set()
    for account_id, record in customers.items():
        segment = record.get("segment")
        assert segment is not None, f"{account_id} has no segment field"
        checked_segments.add(segment)
        _, badge_label = _segment_info(segment)
        household_label = "Household" if badge_label == "Residential" else "Business"

        if segment == "resi":
            assert badge_label == "Residential" and household_label == "Household", account_id
        else:
            # SME and I&C (and any future non-domestic segment we don't yet
            # know about) must never render as Residential/Household.
            assert badge_label != "Residential", (
                f"{account_id} has segment {segment!r} but would render "
                "with the Residential badge"
            )
            assert household_label == "Business", account_id

    # The specific defect: C6 is a real SME account.
    assert customers["C6"]["segment"] == "SME"
    assert "SME" in checked_segments, "sample no longer contains any SME account -- sweep is vacuous"
