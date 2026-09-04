"""R15 on the ORDER of `guard_episode`'s two screens: the type refusal could not fire on a cold
state file, which is the only state a newly wired field is ever in.

THE NAMED DEFECT. `EpisodeFieldTypeError` exists for exactly one job, stated in the guard's own
docstring: it is "the only thing standing between 'wired this field in' and a no-op that reviews as
protection", and a misdeclared field is "a deterministic property of the call site that the first
test run surfaces". It was not surfaced on the first run. Both loops read the PRIOR, and `continue`d
on an unrecordable one, BEFORE they ever looked at the proposal's type:

    guard_episode({"t": None},  {"t": "banana"}, since_fields=("t",))    -> {"t": "banana"}
    guard_episode({},           {"t": "banana"}, since_fields=("t",))    -> {"t": "banana"}
    guard_episode({"t": 1.7e9}, {"t": "banana"}, since_fields=("t",))    -> RAISED
    guard_episode({"c": None},  {"c": "banana"}, streak_fields=("c",))   -> {"c": "banana"}

So the guard's reachability ran exactly backwards: SILENT while the field was new and unproven,
LOUD only once it had been working long enough to have a recorded prior. A field being wired in for
the first time has no key in the state file at all -- that is not an edge case for a new field, it
is the definition of one -- so the run that was supposed to surface the misdeclaration was
precisely the run that could not.

THE DECISION, because widening where a refusal fires is not free. The risk pre-committed against
was that a value ECHOED OFF DISK reaches a raise inside the failure path of the pipeline this guard
monitors -- the harm the module's whole fail direction exists to prevent. It was checked, not
argued: all four live `since_fields` carriers screen what they echo with this module's own
`recorded_instant_seconds`/`_is_episode_start` before proposing it, so no live call site can reach
`_refuse` with a data-dependent value on either path. `_check_proposal_is_orderable` carries the
carrier-by-carrier derivation and names the residual that remains.

Both directions, per R15:
  * FIRES  -- the refusal is now reachable on a cold prior, for both loops, and the whole partition
              of prior states is shown reachable rather than one leg of it (a guard that refused
              EVERY prior state would pass a leg-per-branch suite and is the trap this project has
              walked into three times).
  * SILENT -- the fail direction is untouched where it is load-bearing: a corrupt or absent PRIOR
              still degrades to the unguarded behaviour rather than crashing the pipeline, `None`
              and a non-positive epoch are still repairs and not refusals, and the low/high-water
              orderings still pick the same winners in the same representations.
"""
from __future__ import annotations

import pytest

from background.episode_monotonic import EpisodeFieldTypeError, guard_episode

SINCE = ("t",)
STREAK = ("c",)

GOOD = 1_700_000_000.0          # a 2026-era epoch: an instant something here could have recorded
EARLIER = 1_600_000_000.0
MISDECLARED = "banana"          # unorderable: not an epoch, not an ISO-8601 timestamp

# The partition of PRIOR states, by what the guard can make of it. The point of naming all four is
# that "cold" is not one state -- a field is absent before it is wired, `None` once it is declared
# and never set, `0` when a truncated write lands, and unorderable when the file is corrupt. Every
# one of them used to reach the same `continue`.
COLD_PRIORS = {
    "absent": {},
    "declared_but_null": {"t": None},
    "truncated_to_zero": {"t": 0},
    "corrupt": {"t": MISDECLARED},
}


@pytest.mark.parametrize("name", sorted(COLD_PRIORS))
def test_a_misdeclared_since_field_raises_on_every_cold_prior(name):
    """FIRES. This is the defect: each of these returned {"t": "banana"} silently."""
    with pytest.raises(EpisodeFieldTypeError) as exc:
        guard_episode(COLD_PRIORS[name], {"t": MISDECLARED}, since_fields=SINCE)
    assert "proposed" in str(exc.value) and "'t'" in str(exc.value)


def test_a_misdeclared_streak_field_raises_on_a_cold_prior():
    """FIRES, one loop over. The same inversion sat in `streak_fields` and is the same fix."""
    with pytest.raises(EpisodeFieldTypeError):
        guard_episode({"c": None}, {"c": MISDECLARED}, streak_fields=STREAK)


def test_the_two_values_that_read_as_a_1970_start_are_refused_when_the_prior_is_cold():
    """FIRES. `True` is an int and `NaN` arrives from a FILE (`json.loads` takes the bare token),
    and both used to be PERSISTED off a cold prior for the next hand-rolled isinstance test to
    find. The module already refused them on a warm prior; this is the other half."""
    for bad in (True, float("nan")):
        with pytest.raises(EpisodeFieldTypeError):
            guard_episode({"t": None}, {"t": bad}, since_fields=SINCE)


def test_the_refusal_does_not_fire_on_every_prior_state_it_is_asked_about():
    """REACHABILITY OVER THE WHOLE PARTITION, not a leg per branch.

    A guard that refused everything would pass every test above, and this project has entered that
    trap three times in one afternoon through three different doors. The control is one assertion
    over the partition: with an ORDERABLE proposal, every cold prior must still return, and the
    four of them must not all return the same thing -- which is what proves the prior screen
    survived the hoist rather than being short-circuited by it."""
    got = {name: guard_episode(prior, {"t": GOOD}, since_fields=SINCE)["t"]
           for name, prior in COLD_PRIORS.items()}
    assert got == {"absent": GOOD, "declared_but_null": GOOD,
                   "truncated_to_zero": GOOD, "corrupt": GOOD}
    warm = guard_episode({"t": EARLIER}, {"t": GOOD}, since_fields=SINCE)["t"]
    assert warm == EARLIER != GOOD     # the low-water pick still happens, so both paths are live


def test_a_corrupt_prior_still_degrades_and_never_raises():
    """SILENT, and this is the fail direction the whole module is built around: the guard may not
    crash the pipeline it monitors over a state file it cannot read. Only the CALLER'S proposal is
    a call-site property; the prior is data."""
    assert guard_episode({"t": MISDECLARED}, {"t": GOOD}, since_fields=SINCE)["t"] == GOOD
    assert guard_episode({"c": MISDECLARED}, {"c": 4}, streak_fields=STREAK)["c"] == 4


def test_the_repairs_are_still_repairs_and_not_refusals():
    """SILENT. `None` and a non-positive epoch assert "nobody recorded a start". Both are repaired
    on both sides of the prior screen, and neither may become a type error -- a proposal the guard
    CAN order is not a misdeclaration, whatever it says."""
    assert guard_episode({"t": None}, {"t": None}, since_fields=SINCE)["t"] is None
    assert guard_episode({"t": None}, {"t": 0}, since_fields=SINCE)["t"] is None
    assert guard_episode({"t": GOOD}, {"t": None}, since_fields=SINCE)["t"] == GOOD
    assert guard_episode({"t": GOOD}, {"t": 0}, since_fields=SINCE)["t"] == GOOD
    assert guard_episode({"c": 7}, {"c": None}, streak_fields=STREAK)["c"] == 7


def test_the_two_doors_that_skip_the_loops_entirely_still_skip_them():
    """SILENT. `episode_closed` and a non-Mapping prior return before either loop runs. The hoist
    must not have lifted the refusal above them -- an evidenced close is the caller's assertion and
    is allowed to write whatever it closed with."""
    assert guard_episode({"t": GOOD}, {"t": MISDECLARED},
                         since_fields=SINCE, episode_closed=True)["t"] == MISDECLARED
    assert guard_episode(None, {"t": MISDECLARED}, since_fields=SINCE)["t"] == MISDECLARED


def test_an_undeclared_field_is_never_type_checked():
    """SILENT. The guard repairs the fields it was told about and passes the rest through
    untouched. A hoisted check that screened the whole mapping would be a new refusal on data."""
    out = guard_episode({"t": None}, {"t": GOOD, "x": MISDECLARED}, since_fields=SINCE)
    assert out["x"] == MISDECLARED
