"""NO_ORPHAN_PUBLISHED_ARTEFACT -- an artefact on the publish path must belong to
the population the publish path currently claims.

WORKER_FINDING_THE_PRINTED_FOOTING_CONTROL_RUNS_ON_A_SMALLER_POPULATION_THAN_THE_PAGE
(2026-08-12) reported that `PRINTED_BILL_FOOTS_EXACTLY` sees 0/1557 invoices failing in
`site/state/billing_ledger.json` while 30/1682 fail in `site/data/customers/*.json`, and
proposed pointing the footing control at the second path as well.

That diagnosis was checked and does not hold, which is why this guard is shaped the way
it is rather than as a second footing check:

* `PRINTED_BILL_FOOTS_EXACTLY` is a PRODUCTION-TIME gate
  (`company/billing/pre_bill_validation.py`), not a file auditor. There is nothing to
  "point at another file" -- no code re-produces the 30 records, so re-running the
  control over them could only ever report, never repair.
* `tools/generate_invoice_data.py` -- the module the finding named -- sources every
  printed figure from the ledger (which foots 0/1557) and iterates only
  `run_output_latest.json::per_customer_lifetime`. All three offending accounts are
  absent from it, so that code path never executes for the 30 records. Adding
  quantisation there would have fixed nothing while closing the finding.

The actual defect is ORPHANED PUBLISHED STATE. `C1_2`/`C2_2`/`C5_2` are successor
accounts (`saas/customers.py::SUCCESSOR_CUSTOMERS`) that activate only when the
predecessor churns and we win the home-mover competition. They activated in earlier runs
and not in this one. `tools/generate_customer_data.generate()` wrote a file per account
in the population and never removed the file of an account that left, so the artefacts
persisted -- unrefreshed for 33-35 days against 2026-08-11 for live accounts, and
returning HTTP 200 on poesys.net -- still holding invoice amounts from the era when
`generate_invoice_data` fabricated them (its own docstring) by splitting lifetime revenue
across a seasonal weight curve. That fabricator rounded components and total
independently, which is precisely the defect `PRINTED_BILL_FOOTS_EXACTLY` exists to catch
and had eliminated everywhere it could see.

So the failing sub-population was not merely unchecked, it was UNREACHABLE BY
REGENERATION: stale bytes with no live producer. A footing check over a wider path list
would have turned the 30 red without ever being able to make them green, and the next
conditionally-activated entity would have reproduced the whole shape. This guard states
the rule the population needs instead -- nothing is served that the publish path does not
currently claim -- so the class fails automatically (R10) rather than the instance.

R15: the mutation is `test_mutation_an_orphan_artefact_fires`, which restores an orphan
and asserts THIS test's own subject rejects it.
"""
import json
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"
INDEX = CUSTOMERS_DIR / "_index.json"

# The publish path carried 18 accounts when this guard was written. The floor is a
# vacuity guard, not a pin: it fails if the index collapses to a handful of accounts
# and every assertion below goes quietly true on an empty set.
_MIN_PUBLISHED_ACCOUNTS = 10


def _published_index():
    """The account set the publish path currently claims. Fails CLOSED: an absent or
    malformed index is a FAILED check, not a skipped one (R15 FAIL-SILENT)."""
    assert INDEX.exists(), f"no published index at {INDEX} -- cannot audit the publish path"
    try:
        index = json.loads(INDEX.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AssertionError(
            f"published index is unreadable ({exc}) -- an unreadable index is a failed check"
        ) from exc
    assert isinstance(index, list) and all(isinstance(a, str) for a in index), (
        f"published index is not a list of account ids: {type(index).__name__}"
    )
    return index


def _artefact_files():
    return [p for p in sorted(CUSTOMERS_DIR.glob("*.json")) if p.name != "_index.json"]


def test_the_index_is_a_real_population():
    """Vacuity guard for every assertion below."""
    index = _published_index()
    assert len(index) >= _MIN_PUBLISHED_ACCOUNTS, (
        f"published index holds only {len(index)} accounts -- below the {_MIN_PUBLISHED_ACCOUNTS} "
        "floor, so the orphan assertions below would be near-vacuous"
    )
    assert len(set(index)) == len(index), f"published index repeats an account: {index}"


def test_no_artefact_is_served_outside_the_published_population():
    """The finding's 30 non-footing invoices all lived in files this assertion rejects."""
    claimed = set(_published_index())
    files = _artefact_files()
    assert files, "no per-account artefacts on disk -- the assertion below would be vacuous"
    orphans = sorted(p.stem for p in files if p.stem not in claimed)
    assert not orphans, (
        f"{len(orphans)} artefact(s) on the publish path belong to no account the index claims: "
        f"{orphans}. These are served (HTTP 200) but no longer regenerated, so their contents "
        "freeze at whatever the last run that contained them produced."
    )


def test_every_claimed_account_has_its_artefact():
    """The other direction: an index entry with no file is a 404 on a linked account."""
    claimed = set(_published_index())
    present = {p.stem for p in _artefact_files()}
    missing = sorted(claimed - present)
    assert not missing, f"index claims {missing} but no artefact is published for them"


def test_mutation_an_orphan_artefact_fires(tmp_path, monkeypatch):
    """R15: restore an orphan of exactly the observed shape and prove the guard rejects it.

    Uses the module's own subject resolution against a scratch directory so the real
    publish path is never mutated (a mutation that has to write the shared tree is a
    mutation that can lose a concurrent lane's work).
    """
    scratch = tmp_path / "customers"
    scratch.mkdir()
    (scratch / "_index.json").write_text(json.dumps([f"C{i}" for i in range(1, 13)]))
    for i in range(1, 13):
        (scratch / f"C{i}.json").write_text(json.dumps({"account_id": f"C{i}", "invoices": []}))

    monkeypatch.setitem(globals(), "CUSTOMERS_DIR", scratch)
    monkeypatch.setitem(globals(), "INDEX", scratch / "_index.json")

    # Unmutated: the guard passes on a coherent publish path.
    test_no_artefact_is_served_outside_the_published_population()

    # Mutated: C2_2 is the finding's own orphan -- a departed successor account whose
    # file was never retired.
    (scratch / "C2_2.json").write_text(json.dumps({
        "account_id": "C2_2",
        "invoices": [{"id": "C2_2-INV248", "commodity_amount_gbp": 19.36,
                      "standing_charge_gbp": 0.27, "non_commodity_amount_gbp": 3.81,
                      "vat_gbp": 1.17, "amount_gbp": 24.62}],
    }))
    with pytest.raises(AssertionError, match="belong to no account the index claims"):
        test_no_artefact_is_served_outside_the_published_population()


def test_mutation_a_missing_artefact_fires(tmp_path, monkeypatch):
    """R15 for the other direction."""
    scratch = tmp_path / "customers"
    scratch.mkdir()
    (scratch / "_index.json").write_text(json.dumps([f"C{i}" for i in range(1, 13)]))
    for i in range(1, 12):  # C12 deliberately absent
        (scratch / f"C{i}.json").write_text(json.dumps({"account_id": f"C{i}"}))

    monkeypatch.setitem(globals(), "CUSTOMERS_DIR", scratch)
    monkeypatch.setitem(globals(), "INDEX", scratch / "_index.json")

    with pytest.raises(AssertionError, match="no artefact is published"):
        test_every_claimed_account_has_its_artefact()


def test_mutation_a_missing_index_fails_closed(tmp_path, monkeypatch):
    """R15 FAIL-SILENT: an unavailable check is a FAILED check, never a pass."""
    scratch = tmp_path / "customers"
    scratch.mkdir()
    monkeypatch.setitem(globals(), "CUSTOMERS_DIR", scratch)
    monkeypatch.setitem(globals(), "INDEX", scratch / "_index.json")

    with pytest.raises(AssertionError, match="no published index"):
        test_no_artefact_is_served_outside_the_published_population()

    (scratch / "_index.json").write_text("{not json")
    with pytest.raises(AssertionError, match="unreadable"):
        test_no_artefact_is_served_outside_the_published_population()
