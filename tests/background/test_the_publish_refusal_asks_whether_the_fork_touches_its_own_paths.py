"""`behind_origin` must refuse a COLLISION, not a STATE.

THE DEFECT THIS FILE IS ABOUT (delivery seat, 2026-09-16). `_divergence_refusal` refused every
publish commit on `ahead > 0` alone. Measured on the tree that produced this file: the publish path
had recorded `last_clean_publish: null`, `episode_clean_publishes: 0`, `episode_failures: 38` and
145.8 hours dark, the named cause of the last two cycles was `behind_origin` -- and origin's 6
incoming commits touched 19 paths, of which **zero** were under `site/`, `docs/reports/` or
`docs/status/`. The commit that was refused could not have conflicted with the fork it was refused
for, and `origin_reconcile` -- which now closes that fork unattended on the deadman cadence -- would
have absorbed it without a judgement call.

WHAT MUST STILL REFUSE, because this narrows the guard rather than removing it: a fork that DOES
touch this commit's own paths, and -- the one that decides whether this is a repair or a fail-open
-- a fork whose incoming paths could not be READ. `_publish_surface_collisions` returns `[]` for
"disjoint" and `None` for "could not look", and the whole value of this change rests on the caller
never confusing them. `test_an_unreadable_remote_still_refuses` is that control.
"""

import background.process_run_complete as prc

PROJECT = prc.PROJECT_DIR


def _paths(*relative):
    """Absolute publish paths, the shape `_commit_pathspec` hands the refusal."""
    return [str(PROJECT / rel) for rel in relative]


def _arrange(monkeypatch, *, ahead, arriving):
    """A tree `ahead` commits behind origin, with `arriving` the paths origin is bringing.

    `arriving=None` is git declining to answer, which is a different fact from `arriving=[]`.
    """
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: ahead)
    import background.origin_reconcile as rec
    monkeypatch.setattr(rec, "_arriving_paths", lambda project: arriving)


# ── the partition, asserted whole before any leg is asserted alone ──────────────────────────────

def test_both_sides_of_the_new_branch_are_reachable(monkeypatch):
    """R15 reachability, over the WHOLE partition rather than a leg at a time.

    A `_divergence_refusal` that refused everything would pass every "does it refuse correctly"
    test in this file, and this project has entered that trap three times in one afternoon through
    three different doors. One control, both answers, so a guard that cannot publish is red here.
    """
    _arrange(monkeypatch, ahead=6, arriving=["tools/x.py"])
    refuses = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    _arrange(monkeypatch, ahead=6, arriving=["site/data/dashboard.json"])
    collides = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    assert refuses is None and collides is not None, (
        "the branch is one-sided: publishes={!r}, refuses={!r} -- a refusal that can only ever "
        "say one of the two is not measuring anything".format(refuses, collides)
    )


# ── the repair ──────────────────────────────────────────────────────────────────────────────────

def test_a_fork_that_touches_none_of_this_commits_paths_publishes(monkeypatch):
    """THE named defect, on the real recorded shape: origin ahead, publish surface untouched.

    MUTATION: drop the `collisions is not None and not collisions` branch from
    `_divergence_refusal` and this fires -- which is the 145.8-hour wedge, restored.
    """
    _arrange(monkeypatch, ahead=6, arriving=[
        "background/process_run_complete.py", "background/supervisor.py",
        "tools/couple_value_based_pricing.py", "docs/staging/SEAT_FINDING_X.md",
    ])

    assert prc._divergence_refusal(_paths(
        "site/data/dashboard.json", "site/data/publish_provenance.json",
        "docs/reports/run_output_latest.json", "docs/status/LATEST.md",
    )) is None, "a fork sharing no path with this commit still blocked the publish"


def test_a_fork_that_does_touch_them_still_refuses_and_names_the_paths(monkeypatch):
    """The condition the 2026-09-01 incident was actually about, and it must still refuse.

    That incident's retries were poisonous because they re-committed the SAME publish surface
    origin was moving underneath them. A refusal that named no path cost three re-derivations by
    hand, so the colliding paths are named here rather than left to the reader.
    """
    _arrange(monkeypatch, ahead=2, arriving=[
        "site/data/dashboard.json", "background/supervisor.py",
    ])

    refusal = prc._divergence_refusal(_paths(
        "site/data/dashboard.json", "docs/status/LATEST.md"))

    assert refusal is not None, "a fork ON this commit's own publish surface was allowed through"
    assert "site/data/dashboard.json" in refusal, (
        "the refusal did not name the colliding path, so the reader has to rediscover it: "
        "{!r}".format(refusal)
    )
    assert "background/supervisor.py" not in refusal, (
        "the refusal named an incoming path this commit does NOT write -- that is the whole "
        "class of over-wide refusal this change exists to end"
    )


# ── the control that decides whether this is a repair or a fail-open ────────────────────────────

def test_an_unreadable_remote_still_refuses(monkeypatch):
    """FAIL-CLOSED. `None` is "I could not look" and must never read as "nothing collides".

    This is the single assertion the change stands or falls on. `paths_blocking_fast_forward`
    already carries the sentence -- *"nothing collides" is a finding, "I could not look" is not,
    and a verdict that renders them the same is how a fail-open reads as a clean bill* -- and this
    is the consumer side of it.

    MUTATION: write the branch as `if not collisions:` and this fires.
    """
    _arrange(monkeypatch, ahead=4, arriving=None)

    refusal = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    assert refusal is not None, (
        "an unreadable remote published: `None` from `_publish_surface_collisions` was read as "
        "disjoint, which turns a fail-closed guard into a fail-open one"
    )
    assert "NOT ESTABLISHED" in refusal, (
        "the refusal did not distinguish 'no overlap could be established' from a real overlap, "
        "so a reader cannot tell a git outage from a genuine collision: {!r}".format(refusal)
    )


def test_a_caller_that_names_no_paths_refuses_on_the_state_alone(monkeypatch):
    """No pathspec is no BASIS for a disjointness claim, and `[]` would answer it about nothing.

    Both the empty list and the default `None` arrive here. Neither may publish: the intersection
    of the arriving set with nothing is empty for a reason that has nothing to do with the fork.
    """
    _arrange(monkeypatch, ahead=3, arriving=["tools/x.py"])

    assert prc._divergence_refusal([]) is not None, (
        "an empty pathspec published: the empty intersection was read as disjointness"
    )
    assert prc._divergence_refusal() is not None, (
        "a caller that passed no paths published -- every unconverted call site would silently "
        "lose the guard"
    )


def test_a_path_outside_the_repo_refuses_rather_than_reading_as_disjoint(monkeypatch):
    """An unmatchable path is silently absent from the intersection, which reads as 'no overlap'.

    THE MIX IS THE WHOLE TEST, and the first draft of it was worthless. Written with the outside
    path ALONE, `ours` came out empty and the refusal came from the `if not ours` guard one line
    below -- so mutating the `ValueError` branch from `return None` to `continue` left this green,
    and the control was passing for a reason that had nothing to do with its subject. Establishing
    which of the two it was (R15: a mutation that does not fire is a missing test or an
    equivalence) showed it was a MISSING TEST: with one unmatchable path beside one real one,
    `continue` drops the unmatchable path, the survivor does not collide, and the publish goes out
    on a comparison that quietly lost a member.

    MUTATION: `return None` -> `continue` in `_publish_surface_collisions` and this fires.
    """
    _arrange(monkeypatch, ahead=3, arriving=["site/data/dashboard.json"])

    assert prc._divergence_refusal([
        "/tmp/not-in-this-repo.json",
        str(PROJECT / "docs/status/LATEST.md"),
    ]) is not None, (
        "a path outside the repo was dropped from the comparison and the paths that remained "
        "read as disjoint -- the intersection must not be able to shrink silently"
    )


# ── the capped field the refusal has to fit inside ──────────────────────────────────────────────

def test_the_advance_attribution_survives_the_cause_file_cap(monkeypatch):
    """A sentence added to the FRONT of a capped diagnostic evicts the one at the BACK.

    MEASURED 2026-09-16, and this control exists because the first draft of the collision clause
    did exactly that. `publish_cause.write_cause` keeps `evidence[:600]`. This refusal was already
    620 characters at the ahead-count alone -- 450 of them the standing "Reconcile first / Do NOT
    run `surgical_land`" prose that is identical on every refusal and diagnoses nothing -- leaving
    150 for `_why_not`, which is the only part that tells a reader whether they are looking at a
    hot origin or a real fork. A 131-character clause on the front left 19, and four controls in
    `test_the_publisher_dropped_a_cycle_after_a_single_lost_race_it_could_have_re_run` went red.

    KEYED TO THE PROPERTY, NOT TO TODAY'S LENGTHS. It asserts the headroom a caller needs is
    still there, so it goes red when the refusal grows -- whoever grows it, at whichever end, and
    whether or not they are thinking about this field. Pinning it to "the clause is <= 60 chars"
    would pass while the boilerplate crept up underneath it, which is the same defect one level
    out.

    MUTATION: restore the long clause (or pad the boilerplate) and this fires.
    """
    import background.publish_cause as pc

    _arrange(monkeypatch, ahead=9, arriving=None)
    refusal = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    _arrange(monkeypatch, ahead=9, arriving=["site/data/dashboard.json"])
    collided = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    # What `git_commit_push` appends after the refusal, at its shortest useful length: the reader
    # has to be able to tell a lost race from a real fork, and that verdict is the LAST thing in.
    attribution = " -- and the mechanical advance was attempted before this refusal: " \
                  "the fast-forward SUCCEEDED and origin moved again anyway"

    for label, evidence in (("unreadable", refusal), ("collision", collided)):
        assert evidence is not None, label
        kept = (evidence + attribution)[:600]
        assert "SUCCEEDED" in kept, (
            "the {} refusal is long enough that `publish_cause`'s 600-character cap drops the "
            "advance attribution off the end -- the refusal keeps its standing advice and loses "
            "its diagnosis. Refusal is {} chars; the cap leaves {} for the attribution, which "
            "needs {}.".format(label, len(evidence), 600 - len(evidence), len(attribution))
        )

    assert pc.__doc__ is not None  # the cap being asserted is this module's, named not assumed


# ── the two sets must stay the same set ─────────────────────────────────────────────────────────

def test_the_refusal_and_the_landing_name_one_pathspec():
    """The disjointness verdict is only about this commit while both sides use one tuple.

    Re-typed at the two sites they would drift, and a verdict measured over a different path set
    than the commit writes is not a verdict about that commit. MUTATION: inline either literal and
    this fires.
    """
    source = (PROJECT / "background" / "process_run_complete.py").read_text()

    assert source.count("_commit_pathspec(files, PUBLISH_EXTRA_RELATIVE)") >= 3, (
        "the refusal sites and the landing site no longer share one pathspec expression, so the "
        "set reasoned about can drift from the set committed"
    )
    assert source.count('"docs/design/maturity_map_closed.yaml"') == 1, (
        "the extra-paths tuple is written out more than once, which is the drift this constant "
        "exists to prevent"
    )
