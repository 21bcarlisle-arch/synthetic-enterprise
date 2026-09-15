"""THE DEFECT: one `world_identity` digest, `39a192ce04c1eda8`, spanned two different home stocks.

The departure part is right about what it names and could not have moved -- `_published_departure_
rates` is the observed switching record and does not know what houses this world holds. The failure
was that the composed dict is stamped `world_identity` on every run artefact, so "same digest" read
as "same world", and `docs/design/blind_envelope_arms_2026-09-11.json` named it as the sole warrant
that five books were comparable. Filed as
`SEAT_FINDING_THE_WORLD_IDENTITY_DIGEST_IS_BLIND_TO_THE_HOME_STOCK_2026-09-15.md`.

WHAT IS CONTROLLED HERE IS THE PROPERTY AND NOT TODAY'S DIGEST. No test below names a digest value.
A control pinned to `35f8efe8ff02f245` would go red the next time the stock legitimately improves and
stay green if the probe stopped seeing the homes at all, which is backwards. What is asserted is:
*two worlds that differ only in their homes must get different home digests, and the same departure
digest* -- the second half being the evidence the failing case is REAL and not a story.

TWO STOCKS AND NOT A MOCK. `net_new_acquisition.STOCK_FROM_FITTED_JOINT` gates the live draw against
the pre-2026-09-10 one, and both paths are still built and still work. The 09-11 arms were measured
on the second; this tree runs the first. So the two populations this test separates are the two
populations that actually produced the incident, not a fixture invented to make a digest move.
"""

from __future__ import annotations

import pytest

from simulation.departure_level_anchor import world_level_identity
from simulation.world_home_identity import home_stock_identity


@pytest.fixture(scope="module")
def two_worlds():
    """The live home stock and the pre-2026-09-10 one, as identities.

    Module-scoped because each probe is a real draw through the whole chain. It is cheap -- the
    measurement that made this instrument affordable at all -- but it is not free, and three tests
    asking the same two questions should ask them once.
    """
    return home_stock_identity(), home_stock_identity(from_fitted_joint=False)


def test_two_worlds_that_differ_only_in_their_homes_get_different_home_digests(two_worlds):
    """THE DEFECT: the identity could not tell the 09-11 houses from this tree's houses.

    This is the whole instrument. If it passes with the probe removed, the probe is not measuring
    the homes; mutation-proven by returning a constant from `_probe_vectors`, which reds it.
    """
    live, previous = two_worlds
    assert live["digest"] != previous["digest"], (
        "the live home stock and the pre-2026-09-10 one produced the same home digest, so this "
        "instrument cannot tell apart the two populations it was built for"
    )


def test_the_departure_digest_cannot_tell_those_same_two_worlds_apart():
    """THE DEFECT THIS NAMES IS THE ORIGINAL ONE, and asserting it is what makes the test above
    mean something.

    A home digest that differs across two worlds proves nothing on its own -- it could be differing
    because the worlds differ in some way the OLD digest already caught, in which case the widening
    bought nothing. What the incident needs established is that the departure part is BLIND here:
    the same value on both sides. That is the failing case the control must be shown able to reach,
    and it is reached by construction rather than by a fixture, because `world_level_identity`'s
    departure half takes no stock parameter at all and physically cannot vary with it.
    """
    departure = world_level_identity()["digest"]
    # Re-read inside the other stock's world. Nothing here can change the departure digest, which
    # is exactly the claim: the assertion is that the blindness is real and not merely alleged.
    from simulation import net_new_acquisition as nna

    original = nna.STOCK_FROM_FITTED_JOINT
    try:
        nna.STOCK_FROM_FITTED_JOINT = not original
        under_the_other_stock = world_level_identity()["digest"]
    finally:
        nna.STOCK_FROM_FITTED_JOINT = original

    assert departure == under_the_other_stock, (
        "the departure digest moved when the housing stock was swapped -- if that is now true the "
        "finding this test records has been overtaken and the home part may be redundant, which is "
        "a thing to establish before this assertion is simply flipped"
    )
    # And the home part, over the same swap, does not agree with itself. Asserted HERE as well as
    # above because the pair is the finding: blind on one side, sighted on the other, same swap.
    assert home_stock_identity()["digest"] != home_stock_identity(from_fitted_joint=False)["digest"]


def test_the_home_digest_is_stable_when_nothing_about_the_homes_changed(two_worlds):
    """THE DEFECT: a digest that moves for no reason is a digest every reader learns to ignore.

    The failing shape is a probe that picks up wall-clock, a dict iteration order or an unseeded
    draw. Any of those makes every comparison report "different world" and the instrument becomes
    noise -- which is worse than the blindness it replaced, because it looks like it is working.
    """
    live, _ = two_worlds
    assert live["digest"] == home_stock_identity()["digest"]


def test_each_part_of_the_identity_says_what_it_does_not_cover():
    """THE DEFECT: the original digest said what it covered and never what it did not, and the gap
    between its NAME and its coverage is the entire incident.

    Keyed to the property -- that each part names the other as its own limit -- and not to the
    prose, so a rewording that keeps the duty passes and a rewording that drops it reds. A part
    whose limits section does not mention the other half is a part a reader can take for the whole.
    """
    identity = world_level_identity()
    homes = identity["homes"]

    departure_limit = identity["what_this_does_not_cover"].lower()
    assert "home" in departure_limit, (
        "the departure part does not name the homes as its limit, so a reader is told what it "
        "covers and never what it leaves out -- which is how one digest came to span two stocks"
    )

    home_limit = homes["what_this_does_not_cover"].lower()
    assert "departure" in home_limit, (
        "the home part does not name the departure level as its limit"
    )
    assert homes["what_this_identifies"] != identity["what_this_identifies"], (
        "both parts identify themselves with the same sentence, so neither is saying in its own "
        "words what it covers"
    )


def test_the_composed_identity_still_answers_the_departure_question_unchanged():
    """THE DEFECT: eighteen places compare `world_identity.digest`, and a widening that moved or
    renamed that field would silently restate every one of their verdicts.

    So the top-level `digest` must still be the DEPARTURE digest and nothing else -- the home part
    is additive, under its own key. Mutation-proven by folding the home digest into the top-level
    canonical string, which reds this.
    """
    import hashlib
    import json

    identity = world_level_identity()
    canonical = json.dumps(
        {str(y): f"{v:.6f}" for y, v in sorted(identity["anchors"].items())},
        sort_keys=True, separators=(",", ":"),
    )
    assert identity["digest"] == hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16], (
        "the top-level digest is no longer the departure anchors' digest, so every filed artefact "
        "that carries one is now incomparable with the live world for a reason that is not a "
        "change in the world"
    )
    assert identity["homes"]["digest"] != identity["digest"]
