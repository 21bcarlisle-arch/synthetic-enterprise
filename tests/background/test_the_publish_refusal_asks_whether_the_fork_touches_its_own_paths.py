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


def _arrange(monkeypatch, *, ahead, arriving, stranded=0):
    """A tree `ahead` commits behind origin, with `arriving` the paths origin is bringing.

    `arriving=None` is git declining to answer, which is a different fact from `arriving=[]`.

    `stranded` PINS THE THIRD WINDOW, and its absence is what wedged the publish path for 13
    consecutive cycles from 2026-09-17T12:40. `_unabsorbed_publish_commits` arrived inside this
    refusal after this file was written and reads the real repository -- `git rev-list --count
    FETCH_HEAD..HEAD`. Under a fixture that pins only the other two windows there is no
    `FETCH_HEAD`, so it returned `None` on every leg, every publish-expecting assertion here went
    red, and the publish gate refused the whole tree on a `test_regression` that was an artefact
    of this fixture rather than a fault in the guard. A window a guard reads is a window its
    fixture must pin: the two that were pinned were pinned for exactly this reason, and the third
    was simply not noticed.

    `stranded=0` is the ordinary tree (nothing of ours is stranded on this side of the fork) and
    it is the DEFAULT so that legs about the collision branch stay about the collision branch.
    The legs that are about the ceiling itself set it explicitly, and
    `test_both_sides_of_the_new_branch_are_reachable` asserts over all three of its answers, so
    the default cannot quietly become the only value this file ever measures.
    """
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: ahead)
    import background.origin_reconcile as rec
    monkeypatch.setattr(rec, "_arriving_paths", lambda project: arriving)

    def _stranded(publish_paths):
        # ASSERTED, NOT IGNORED. A stub spelled `lambda *_: stranded` keeps passing when the
        # subject's signature moves underneath it -- the shape that leaves a mutation ungraded --
        # so the stub requires the caller to still be handing it this commit's paths.
        assert publish_paths, "the ceiling was asked about no paths at all"
        return stranded

    monkeypatch.setattr(prc, "_unabsorbed_publish_commits", _stranded)


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

    # AND THE SAME QUESTION OF THE CEILING THAT ARRIVED INSIDE THE PUBLISHING BRANCH. It can only
    # be reached once disjointness is established, so its three answers are a partition INSIDE the
    # `refuses is None` leg above -- and a ceiling that answered "refuse" to all three would leave
    # every assertion above untouched while the publish path stayed shut, which is precisely the
    # 13-cycle wedge this file was red for.
    answers = {}
    for label, stranded in (("clear", 0), ("stacked", 2), ("unreadable", None)):
        _arrange(monkeypatch, ahead=6, arriving=["tools/x.py"], stranded=stranded)
        answers[label] = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    assert answers["clear"] is None, (
        "a disjoint commit with NOTHING of ours stranded on this side of the fork was still "
        "refused -- the ceiling has swallowed the branch it was added inside: {!r}".format(
            answers["clear"])
    )
    assert answers["stacked"] is not None and answers["unreadable"] is not None, (
        "the ceiling admitted a second unpushable copy, or admitted one it could not count: "
        "{!r}".format(answers)
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


def test_a_second_unpushable_copy_of_the_publish_surface_refuses_and_says_how_many(monkeypatch):
    """The ceiling on the admission above: one stranded copy is a bet, two is a measurement.

    The first disjoint publish bets that `origin_reconcile` absorbs it on the next cadence. A
    SECOND commit writing the same surface on the unpushable side of the fork is evidence the
    cadence is not running -- the 2026-09-01 shape, which had recurred four commits deep before
    anyone looked. A refusal that did not carry the count would send the reader back to
    `rev-list` to rediscover it.

    MUTATION: drop the `if stranded:` branch and this fires -- the stack is admitted.
    """
    _arrange(monkeypatch, ahead=6, arriving=["tools/x.py"], stranded=2)

    refusal = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    assert refusal is not None, "a second unpushable copy of the publish surface was created"
    assert "2 commit(s) here ALREADY write" in refusal, (
        "the refusal did not say how many copies are already stranded, so the reader cannot tell "
        "a first bet from a stack: {!r}".format(refusal)
    )


def test_a_stranded_count_that_could_not_be_read_refuses_rather_than_guessing(monkeypatch):
    """FAIL-CLOSED, and the leg the 13-cycle wedge was the live instance of.

    `None` from the ceiling is "git would not answer", and the least defensible moment to create
    another unpushable copy is the one where we cannot tell whether the last one is still
    stranded. This is the branch the unpinned fixture drove EVERY leg of this file down.

    MUTATION: read `None` as zero -- `if stranded:` alone, without the `is None` test above it --
    and this fires.
    """
    _arrange(monkeypatch, ahead=6, arriving=["tools/x.py"], stranded=None)

    refusal = prc._divergence_refusal(_paths("site/data/dashboard.json"))

    assert refusal is not None, (
        "an uncountable stranded set published: `None` was read as zero, which is the fail-open "
        "the whole function is written against"
    )
    assert "could NOT be established" in refusal, (
        "the refusal did not distinguish an uncountable set from a counted stack, so a git "
        "outage and a real stack read the same: {!r}".format(refusal)
    )


# ── the ceiling's own git read, which had no control at all ─────────────────────────────────────

def _repo_with_a_publish_commit(tmp_path):
    """A real repository holding one commit that writes `site/data/dashboard.json`.

    A REAL REPOSITORY RATHER THAN A STUBBED `subprocess.run`, because the defect this function
    shipped with was entirely about what git does when the ref it names is absent -- and a stub
    that returns whatever the test wants cannot be wrong about that. See `_no_FETCH_HEAD` below,
    which is the wedge's own condition and only a real repo can produce it.
    """
    import subprocess as sp
    repo = tmp_path / "repo"
    (repo / "site" / "data").mkdir(parents=True)
    (repo / "site" / "data" / "dashboard.json").write_text("{}\n", encoding="utf-8")
    sp.run(["git", "init", "-q", "."], cwd=repo, check=True)
    sp.run(["git", "add", "-A"], cwd=repo, check=True)
    sp.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base"],
           cwd=repo, check=True)
    base = sp.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True,
                  check=True).stdout.strip()
    (repo / "site" / "data" / "dashboard.json").write_text('{"a": 1}\n', encoding="utf-8")
    sp.run(["git", "add", "-A"], cwd=repo, check=True)
    sp.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "publish"],
           cwd=repo, check=True)
    return repo, base


def test_the_ceiling_counts_the_commits_that_actually_write_the_surface(tmp_path, monkeypatch):
    """One publish commit ahead of the fetched ref counts ONE, and an unrelated one counts none.

    Both halves in one control, because a count that always returned 1 -- or always 0 -- would
    pass either half alone. MUTATION: drop the `-- <paths>` pathspec from the rev-list and the
    unrelated commit is counted, which fires the second assertion.
    """
    repo, base = _repo_with_a_publish_commit(tmp_path)
    (repo / ".git" / "FETCH_HEAD").write_text(
        "{}\t\tbranch 'main' of origin\n".format(base), encoding="utf-8")
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    assert prc._unabsorbed_publish_commits(
        [str(repo / "site" / "data" / "dashboard.json")]) == 1

    assert prc._unabsorbed_publish_commits([str(repo / "docs" / "status" / "LATEST.md")]) == 0, (
        "a path this commit does not write was counted, so the ceiling bounds a different "
        "surface from the one the admission is about"
    )


def test_a_missing_FETCH_HEAD_is_NOT_established_and_never_zero(tmp_path, monkeypatch):
    """THE WEDGE'S OWN CONDITION, measured on a real repository.

    `git rev-list FETCH_HEAD..HEAD` exits non-zero when nothing has been fetched. That must be
    `None` -- "we could not count" -- and never `0`, because zero is the one answer that lets a
    commit through. The caller's `stranded is None` branch is the consumer side of this and
    `test_a_stranded_count_that_could_not_be_read_refuses_rather_than_guessing` grades it.

    MUTATION: `return 0` on the non-zero returncode and this fires.
    """
    repo, _ = _repo_with_a_publish_commit(tmp_path)
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    assert prc._unabsorbed_publish_commits(
        [str(repo / "site" / "data" / "dashboard.json")]) is None, (
        "a repository that has never fetched reported a countable zero, which reads as 'nothing "
        "is stranded' -- the answer that admits the commit"
    )


def test_a_path_outside_the_repo_makes_the_ceiling_uncountable_rather_than_empty(
        tmp_path, monkeypatch):
    """An unmatchable path cannot shrink the surface the count is taken over.

    Same defect shape as the collision intersection one screen up, on the other consumer of
    `_our_publish_paths`: silently dropping a path leaves a SMALLER surface, over which fewer
    commits are counted, which is the direction that admits.

    MUTATION: `return None` -> `continue` in `_our_publish_paths` and this fires.
    """
    repo, base = _repo_with_a_publish_commit(tmp_path)
    (repo / ".git" / "FETCH_HEAD").write_text(
        "{}\t\tbranch 'main' of origin\n".format(base), encoding="utf-8")
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)

    assert prc._unabsorbed_publish_commits(["/tmp/not-in-this-repo.json"]) is None
    assert prc._unabsorbed_publish_commits([]) is None, (
        "an empty pathspec counted a surface, and `rev-list -- ` with no paths is the whole "
        "history rather than nothing"
    )


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
