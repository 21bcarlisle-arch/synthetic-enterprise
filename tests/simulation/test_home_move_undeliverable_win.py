"""A won home-mover with no successor supply point must not suppress the market
replacement — WORKER_FINDING_A_WON_HOME_MOVER_WITH_NO_SUCCESSOR_SUPPLY_POINT_
SUPPRESSES_THE_REPLACEMENT_TOO_2026-08-14.md (BLOCKING, lane W2_customer_generator).

The defect: `if event["home_move_won"]: ... elif mandate_permits_replacement(): ...`
takes the OUTER branch on a win, finds no successor to activate, does nothing, and
never reaches the `elif`. The account is lost with neither a successor nor a market
replacement — so for the 7 of 13 billing accounts with no successor point, WINNING
the home-mover was strictly worse for the company than losing it.

R15 — what each control is mutated against, and what its own named defect is:

* the helper controls fail if `home_move_disposition` is rewritten to key on the win
  roll alone (`ACTIVATE if home_move_won else GO_TO_MARKET`);
* the POPULATION control fails if the affected set is empty — i.e. it is what stops
  the two above from being vacuous fixture algebra about a state the roster cannot
  reach;
* the CALL-SITE control fails if `run_phase2b` is reverted to the if/elif chain. It
  is behavioural, not source-shaped: it runs the real sim over a truncated window,
  forces one real account to churn with a win, and asserts the company was observed
  ASKING the growth desk for a replacement. A source-text assertion would pass on any
  rewrite that reads right and behaves wrong.

The call-site controls assert on `decide_acquisition` being CALLED, not on an
acquisition being WON: the defect suppresses the going-to-market, and whether that
market attempt then wins is a separate roll this test has no business pinning.
"""
import pytest

import simulation.run_phase2b as rp
from saas.customers import CUSTOMERS, SUCCESSOR_CUSTOMERS
from simulation.customer_events import (
    HOME_MOVE_ACTIVATE_SUCCESSOR,
    HOME_MOVE_GO_TO_MARKET,
    home_move_disposition,
)
from simulation.household import household_of

# Short enough to keep the two forced runs cheap; the window is only the stage on
# which the forced churn happens, so its own event history is irrelevant.
FORCED_RUN_END = "2017-12-31"


# ---------------------------------------------------------------------------
# The rule itself
# ---------------------------------------------------------------------------

def test_an_undeliverable_win_disposes_to_market():
    """The finding's exact state: won the mover, no successor point to activate."""
    assert home_move_disposition(True, None) == HOME_MOVE_GO_TO_MARKET


def test_a_deliverable_win_activates_the_successor():
    assert home_move_disposition(True, "C1_2") == HOME_MOVE_ACTIVATE_SUCCESSOR


def test_a_lost_home_mover_goes_to_market_even_where_a_successor_exists():
    """A successor point on the book must not manufacture a win that was not rolled."""
    assert home_move_disposition(False, "C1_2") == HOME_MOVE_GO_TO_MARKET


# ---------------------------------------------------------------------------
# The population — measured off the live roster, not asserted
# ---------------------------------------------------------------------------

def _accounts_without_successor() -> list[str]:
    with_successor = {
        c["successor_of"] for c in SUCCESSOR_CUSTOMERS if c["commodity"] == "electricity"
    }
    accounts = sorted({household_of(c["customer_id"]) for c in CUSTOMERS})
    return [a for a in accounts if a not in with_successor]


def test_the_affected_population_is_non_empty_on_the_live_roster():
    """Without this, the two controls above are algebra about an unreachable state.

    Measured 2026-08-14: 7 of 13 billing accounts (C7, C8, C9, C_IC1..C_IC4) have no
    successor supply point, and the curriculum's drawn SYN-* points have none either,
    so activating the population draw only widens this set.
    """
    affected = _accounts_without_successor()
    assert affected, (
        "every billing account now has a successor supply point — if that is a real "
        "roster change rather than a broken measurement, this whole class is closed "
        "and these controls should be retired deliberately, not left passing vacuously"
    )
    for account in affected:
        assert home_move_disposition(True, rp.SUCCESSOR_MAP.get(account)) == (
            HOME_MOVE_GO_TO_MARKET
        )


# ---------------------------------------------------------------------------
# The call site — behavioural, over a real (truncated) run
# ---------------------------------------------------------------------------

@pytest.fixture
def restore_acquired_book():
    """`run_phase2b` appends won acquisitions to a module-level list; a forced churn
    must not leak a customer into every later test in the session."""
    before = list(rp.ACQUIRED_CUSTOMERS)
    yield
    rp.ACQUIRED_CUSTOMERS[:] = before


def _force_one_churn_with_a_win(monkeypatch, candidates) -> dict:
    """Turn the FIRST real lifecycle event of any account in `candidates` into a churn that won
    the home-mover, and hold every OTHER account to a renewal for the window. Returns a dict whose
    `"account"` names the one forced, or None if no candidate reached a lifecycle event.

    A SET, NOT ONE ID (2026-09-30). The successor leg forced `next(iter(SUCCESSOR_MAP))`, which is
    C1, and once C1 stopped reaching a lifecycle event before `FORCED_RUN_END` the force never
    fired and the test measured an empty window. Any successor-bearing account is the subject,
    so the first one the world reaches is forced and the test reads which it was.

    THE SOLE-CHURN PREMISE IS NOW ENFORCED RATHER THAN INHERITED (2026-08-27). This used to
    leave other accounts' events untouched, and the tests below rely on "the forced churn is the
    only one in this window, so any market approach is its" — an attribution that was true only
    because the world happened to produce no other churn in it.

    It stopped being true when the renewal schedule was repaired: `roll_lifecycle_event` was
    returning None for every account whose anniversary fell on the 1st of a month rather than
    the 31st, so six of the nine seed accounts could never leave at renewal. With that fixed C6
    churns naturally in this window, `churned_billing_accounts` became `['C6', 'C7']`, and the
    attribution silently stopped holding.

    A premise a test depends on should be established by the test, not borrowed from a world
    that is free to change. Suppressing other churn is not a weakening: the subject here is what
    happens to ONE won home-mover with no successor, and another account leaving at the same
    time is noise that makes the market approach unattributable.
    """
    real_roll = rp.roll_lifecycle_event
    candidates = set(candidates)
    forced = {"account": None}

    def wrapper(cid, term_start_str, *args, **kwargs):
        event = real_roll(cid, term_start_str, *args, **kwargs)
        if event is None:
            return None
        if forced["account"] is None and event["customer_id"] in candidates:
            event["event_type"] = "churned"
            event["home_move_won"] = True
            forced["account"] = event["customer_id"]
        elif event["customer_id"] != forced["account"]:
            # Hold everyone else on supply, so the only churn in the window is the forced one.
            event["event_type"] = "renewed"
            event["home_move_won"] = False
        return event

    monkeypatch.setattr(rp, "roll_lifecycle_event", wrapper)
    return forced


def _lifecycle_churns(result: dict) -> list[str]:
    """The accounts that left through `roll_lifecycle_event` -- the route the hold above governs.

    NOT `churned_billing_accounts`. That is the union of every departure route, and since C1b's
    SVT-inertia departures (`_svt_departures`, `DEPARTURE_OCCASION_SVT_SEGMENT`) it also holds
    accounts leaving an SVT stint, which no lifecycle event decides and this hold cannot reach:
    on 2026-09-30 it read `['C7', 'PROS-2016-0003', ...]`, nine accounts, for one forced churn.
    Those departures never go to market -- the only `decide_acquisition` call is in the lifecycle
    branch -- so they cannot pollute the spy, and the attribution rests on this list alone.
    """
    assert result["churned_billing_accounts"], "no departure at all -- the forced churn never ran"
    return sorted(
        e["customer_id"] for e in result["customer_events"] if e.get("event_type") == "churned"
    )


def _spy_on_going_to_market(monkeypatch) -> list:
    real_decide = rp.decide_acquisition
    calls: list = []

    def wrapper(*args, **kwargs):
        calls.append(kwargs or args)
        return real_decide(*args, **kwargs)

    monkeypatch.setattr(rp, "decide_acquisition", wrapper)
    return calls


def test_a_won_home_mover_with_no_successor_still_goes_to_market(
    monkeypatch, restore_acquired_book
):
    """The BLOCKING defect, run end to end. Reverting the call site to the if/elif
    chain leaves `went_to_market` empty and reds this test."""
    account = _accounts_without_successor()[0]
    assert rp.SUCCESSOR_MAP.get(account) is None, "fixture chose an account that HAS a successor"

    forced = _force_one_churn_with_a_win(monkeypatch, [account])
    went_to_market = _spy_on_going_to_market(monkeypatch)
    result = rp.main(report_end=FORCED_RUN_END)

    assert forced["account"] == account, f"{account} reached no lifecycle event in the window"
    # The forced churn is the only LIFECYCLE churn in this window, and that branch holds the
    # only `decide_acquisition` call, so any market approach is its.
    assert _lifecycle_churns(result) == [account]
    assert went_to_market, (
        f"{account} won its home-mover, had no successor supply point to activate, and "
        f"the company was never asked whether to replace it — the win suppressed the "
        f"replacement, which is the finding"
    )
    assert result["won_successor_activations"] == {}, (
        "no successor point exists for this account, so nothing may have been activated"
    )
    undelivered = [
        e for e in result["customer_events"] if e.get("home_move_win_undelivered")
    ]
    assert [e["customer_id"] for e in undelivered] == [account], (
        "the shortfall of the realised win rate against its parameter must be recorded "
        "on the event, not left silent"
    )


def test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market(
    monkeypatch, restore_acquired_book
):
    """The other direction: the repair must not turn every win into a market approach."""
    forced = _force_one_churn_with_a_win(monkeypatch, rp.SUCCESSOR_MAP)
    went_to_market = _spy_on_going_to_market(monkeypatch)
    result = rp.main(report_end=FORCED_RUN_END)

    account = forced["account"]
    assert account is not None, (
        f"no successor-bearing account {sorted(rp.SUCCESSOR_MAP)} reached a lifecycle event "
        f"before {FORCED_RUN_END} -- the force never fired and every leg below is vacuous"
    )
    successor_id = rp.SUCCESSOR_MAP[account]
    assert _lifecycle_churns(result) == [account]
    assert successor_id in result["won_successor_activations"]
    assert not went_to_market, (
        f"{account}'s home-move win was delivered as {successor_id}; the company must "
        f"not also have gone to market for the same property"
    )
    assert not [e for e in result["customer_events"] if e.get("home_move_win_undelivered")]
