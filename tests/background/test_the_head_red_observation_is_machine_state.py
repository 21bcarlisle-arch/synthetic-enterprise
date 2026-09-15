"""The head-red observation is machine state, and ABSENT may never read as GREEN.

THE DEFECT (2026-09-10). `docs/observability/head_red_observed.json` and the register rendered
from it were tracked. Their only committed run row was the 2026-09-02 ENOSPC/tmpfs wreck — 830
red, `OSError x760`, `"passed": null` — so every isolated worktree, clean HEAD extract and fresh
checkout read `drawable() == 830` while the shared tree read 43.

THE TRAP IN THE OBVIOUS FIX, and the reason this file exists rather than a `.gitignore` line
alone. `load_observed()` returns `{"runs": [], "tests": {}}` for a missing store, `owed()` then
returns `[]`, `drawable()` returns `[]`, and `staging_rooms._with_the_head_red_register` DROPS the
register from the queue when `drawable()` is empty. Measured before the change: with the store
moved aside, the register was absent from a 314-item queue and nothing anywhere named the
absence. So a bare untrack would have converted a false 830 into a false ZERO — and
`load_observed`'s own docstring says that is "the failure that would matter".

Both directions are asserted here on purpose. A test that only checked "830 is gone" passes just
as well on the fail-open bug it would have introduced.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from background import head_red_register as reg

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent


def _store(runs, tests):
    return {"runs": list(runs), "tests": dict(tests)}


# ── the decision: the LIVE store is untracked, and the acceptance list stays tracked ─────────
def _tracked(relpath: str) -> bool:
    return subprocess.run(["git", "ls-files", "--error-unmatch", relpath],
                          cwd=PROJECT_DIR, capture_output=True, text=True).returncode == 0


def test_the_live_observation_store_is_untracked_and_ignored():
    """MUTATION: `git add -f docs/observability/.head_red_observed.json` and this fails.

    Keyed to the PROPERTY (is it in the index) rather than to a count, so it goes green the moment
    the file is untracked and stays red for as long as it is not.
    """
    rel = str(reg.OBSERVED_PATH.relative_to(PROJECT_DIR))
    assert not _tracked(rel), (
        f"{rel} is tracked. It is machine state: written unattended on every census run, "
        "truncated to a rolling window by `del runs[:-MAX_RUNS_KEPT]`, and true of exactly one "
        "machine at one HEAD on one night. Committing it publishes one night as established fact "
        "to every other checkout — which is how the 830-row ENOSPC wreck got its authority."
    )
    check = subprocess.run(["git", "check-ignore", "-q", rel], cwd=PROJECT_DIR)
    assert check.returncode == 0, f"{rel} must be gitignored, not merely absent from the index"


def test_nothing_writes_the_legacy_tracked_path_any_more():
    """The legacy path is READ-ONLY on its way out, and this is the leg that keeps it that way.

    It is deliberately still tracked and deliberately untouched: the shared tree holds it dirty,
    and a commit deleting a dirty-held path makes `git pull` ABORT rather than delete — measured
    in a scratch clone. So the exit is a later two-step on the shared tree, not a delete here.

    MUTATION: point `save_observed`/`write_register` back at `LEGACY_OBSERVED_PATH` and this
    fails — which is what would silently re-commit a machine's night into everyone's checkout.
    """
    import inspect
    for fn in (reg.save_observed, reg.record, reg.write_register):
        src = inspect.getsource(fn)
        assert "LEGACY_OBSERVED_PATH" not in src, (
            f"{fn.__name__} must not reach the legacy path; it is read-only"
        )
    assert reg.OBSERVED_PATH != reg.LEGACY_OBSERVED_PATH


def test_the_legacy_wreck_is_refused_but_a_real_legacy_store_is_adopted(tmp_path, monkeypatch):
    """THE ONE RULE THAT HAS TO GIVE OPPOSITE ANSWERS IN THE TWO TREES, so both are asserted.

    A test that only checked the wreck is refused would pass just as well on a fallback that
    refuses everything — which would abandon the shared tree's nine runs of ages and reset every
    `runs_red` to 1, destroying the signal the doorbell clause exists to carry.

    MUTATION: drop the `_is_credible` filter (adopt any legacy store) and the first half fails.
    MUTATION: remove the legacy fallback entirely and the second half fails.
    """
    monkeypatch.setattr(reg, "OBSERVED_PATH", tmp_path / "absent.json")

    wreck = {"runs": [{"at": "2026-09-02T04:30:02+00:00", "head": "ec2e0b1a4", "red": 830,
                       "passed": None, "causes": {"OSError": 760}}],
             "tests": {f"t{i}.py::x": {"currently_red": True, "runs_red": 1} for i in range(830)}}
    legacy = tmp_path / "legacy.json"
    legacy.write_text(json.dumps(wreck))
    monkeypatch.setattr(reg, "LEGACY_OBSERVED_PATH", legacy)
    assert reg.summary(reg.load_observed())["owed"] == 0, "the 830-row wreck must not be adopted"
    assert reg.observation_state(reg.load_observed()) == reg.UNOBSERVED

    good = dict(wreck)
    good["runs"] = wreck["runs"] + [{"at": "2026-09-10T03:46:53+00:00", "head": "dceedff0f",
                                     "red": 1, "passed": 33697, "causes": {}}]
    good["tests"] = {"t0.py::x": {"currently_red": True, "runs_red": 10,
                                  "first_seen": "2026-09-02T13:18:33+00:00"}}
    legacy.write_text(json.dumps(good))
    adopted = reg.summary(reg.load_observed())
    assert adopted["state"] == reg.OBSERVED and adopted["owed"] == 1
    assert adopted["worst_runs"] == 10, "the ages are the whole reason the fallback exists"


def test_the_acceptance_list_IS_tracked_because_a_person_writes_it():
    """The other half of the split, and the leg that stops this being "untrack the noisy files".

    MUTATION: untrack `head_red_baseline.json` too and this fails. Only the machine's observation
    is state; what a person has DECIDED to live with is a property of the tree.
    """
    out = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "docs/observability/head_red_baseline.json"],
        cwd=PROJECT_DIR, capture_output=True, text=True)
    assert out.returncode == 0, (
        "the acceptance list must stay tracked: a machine may write what it saw, only a person "
        "may write what is forgiven"
    )


# ── the fail-open leg: absent is UNOBSERVED, and UNOBSERVED is not green ─────────────────────
def test_an_absent_store_reads_UNOBSERVED_and_not_green(tmp_path, monkeypatch):
    """THE ONE THAT MATTERS. MUTATION: make `observation_state` return OBSERVED unconditionally
    (or delete the UNOBSERVED branch from `doorbell_clause`) and this fails.

    Zero-owed-because-unobserved and zero-owed-because-green are both zero and mean opposite
    things. Before 2026-09-10 only `render()` could tell them apart, so the DRAW and the DOORBELL
    — the two things that actually decide whether a person looks — were blind to the difference.
    """
    # BOTH paths, or this test measures the tree it runs in rather than the code. Patching only
    # OBSERVED_PATH leaves the legacy fallback pointing at the real file, which is the wreck here
    # (refused, so green by luck) and a credible nine-run store on the shared tree (adopted, so
    # RED there). A control whose colour depends on which worktree ran it is not a control.
    monkeypatch.setattr(reg, "OBSERVED_PATH", tmp_path / "absent.json")
    monkeypatch.setattr(reg, "LEGACY_OBSERVED_PATH", tmp_path / "also-absent.json")
    store = reg.load_observed()

    assert reg.observation_state(store) == reg.UNOBSERVED
    info = reg.summary(store, accepted=set())
    assert info["state"] == reg.UNOBSERVED
    assert info["owed"] == 0, "an unobserved tree owes nothing — it has not been told anything"

    clause = reg.doorbell_clause(info)
    assert clause, "an unobserved tree must SAY SO; silence here is the fail-open"
    assert "NOT a claim that HEAD is green" in clause
    assert "NO CENSUS HAS RUN" in clause


def test_an_observed_green_tree_is_SILENT_and_that_is_the_only_silent_case():
    """The partition's other end, and the control over the whole partition rather than a leg each.

    A doorbell that speaks on every state is the 139-name blob again. MUTATION: return a clause
    for the observed-and-green case and this fails.
    """
    observed_green = reg.summary(
        _store([{"at": "2026-09-10T03:00:00+00:00", "head": "abc", "red": 0, "passed": 33697}], {}),
        accepted=set())
    assert observed_green["state"] == reg.OBSERVED
    assert reg.doorbell_clause(observed_green) is None, (
        "a census that ran and found nothing owed is the one case where saying nothing is TRUE"
    )

    # and the partition is genuinely reachable in all three states, not just the flattering one
    unobserved = reg.summary(_store([], {}), accepted=set())
    owed_state = reg.summary(
        _store([{"at": "2026-09-10T03:00:00+00:00", "head": "abc", "red": 1, "passed": 9}],
               {"t.py::x": {"currently_red": True, "runs_red": 4, "first_seen": "2026-09-02"}}),
        accepted=set())
    assert (unobserved["state"] == reg.UNOBSERVED
            and observed_green["state"] == reg.OBSERVED
            and owed_state["owed"] == 1), "all three states must be reachable"


# ── the doorbell carries the COUNT and the AGE, which render() computed and dropped ──────────
def test_the_doorbell_clause_names_the_owed_count_and_the_longest_standing_age():
    """MUTATION: drop `worst_runs` from `doorbell_clause` and this fails.

    The register was surfaced ~3,421 times as the 7th name in a 139-name comma-joined blob and
    drew nobody. A bare filename carries no count, no age and no severity; "43 owed" and "43
    owed, one red for 9 consecutive nightly runs" are different facts and only the second argues
    for itself.
    """
    info = reg.summary(
        _store([{"at": "2026-09-10T03:46:53+00:00", "head": "dceedff0f", "red": 43,
                 "passed": 33697}],
               {"tests/a.py::old": {"currently_red": True, "runs_red": 9,
                                    "first_seen": "2026-09-02T13:18:33+00:00"},
                "tests/b.py::new": {"currently_red": True, "runs_red": 1,
                                    "first_seen": "2026-09-10T03:46:53+00:00"}}),
        accepted=set())

    assert info["owed"] == 2
    assert info["worst_runs"] == 9, "the age must be the LONGEST-standing, not the newest"
    assert info["worst_node"] == "tests/a.py::old"

    clause = reg.doorbell_clause(info)
    assert "2 owed" in clause
    assert "9 consecutive census run(s)" in clause
    assert "2026-09-02" in clause, "the age needs its origin date, not just a run count"
    assert reg.REGISTER_NAME in clause, "a reader must be able to find the document"


def test_the_supervisor_doorbell_lifts_the_register_out_of_the_blob(monkeypatch):
    """The wiring leg. Calling the clause builder directly is blind to whether the DOORBELL uses it.

    MUTATION: revert `find_work` to `', '.join(staged)` and this fails.
    """
    from background import supervisor

    staged = ["AAA_FINDING.md", reg.REGISTER_NAME, "ZZZ_FINDING.md"]
    monkeypatch.setattr(reg, "doorbell_clause", lambda info=None: "REGISTER_CLAUSE_SENTINEL")

    out = supervisor._differentiated_staging(staged)

    assert out.startswith("REGISTER_CLAUSE_SENTINEL; "), (
        "the clause must LEAD and sit outside the comma-join: position 6 of 132 was the bug, and "
        "a clause with commas of its own placed inside the join is just three more list entries"
    )
    assert reg.REGISTER_NAME not in out, (
        "the register must not ALSO appear as a bare name — that is the furniture it was"
    )
    assert "AAA_FINDING.md" in out and "ZZZ_FINDING.md" in out, "everything else still surfaces"


def test_find_work_actually_routes_the_staged_list_through_the_differentiator():
    """THE WIRING LEG PROPER. The two tests above call `_differentiated_staging` directly, so they
    are blind to whether `find_work` — the only caller that reaches a reader — uses it at all.
    Reverting that one line to `', '.join(staged)` leaves both of them green.

    Asked over the AST rather than by substring: a mention of the name in a comment or docstring
    is not a call, and this must fail when the CALL goes.

    MUTATION: revert `find_work`'s join to `', '.join(staged)` and this fails.
    """
    import ast
    import inspect

    from background import supervisor

    tree = ast.parse(inspect.getsource(supervisor.find_work))
    called = {
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "_differentiated_staging" in called, (
        "find_work must CALL the differentiator; the staged blob is the only surface a reader "
        "sees, and a clause nothing renders is the 3,421 silent surfacings again"
    )


def test_the_unobserved_clause_reaches_the_doorbell_even_though_the_queue_drops_the_register(
        monkeypatch):
    """The fail-open leg AT THE WIRING, which is where the bare untrack would have gone silent.

    `staging_rooms` drops the register from the queue when `drawable()` is empty, so on an
    unobserved tree the name is not in `staged` at all. If the doorbell only ever reformatted a
    name that was present, it would say nothing — the false zero.

    MUTATION: build the clause only when `REGISTER_NAME in staged` and this fails.
    """
    from background import supervisor

    monkeypatch.setattr(reg, "doorbell_clause", lambda info=None: "UNOBSERVED_SENTINEL")
    out = supervisor._differentiated_staging(["AAA_FINDING.md"])

    assert out.startswith("UNOBSERVED_SENTINEL; "), (
        "the absence of the register from the queue is exactly when the doorbell must speak"
    )


# ── and the register document itself says which state it is in ───────────────────────────────
def test_the_rendered_register_names_the_unobserved_state_without_claiming_green():
    """MUTATION: restore the old "No census has run yet" stub and this still passes on the first
    two asserts — so the third is the one carrying the change: a fresh checkout must be told WHY
    the file is empty and what to run, or the next reader re-commits it.
    """
    text = reg.render(_store([], {}), accepted=set())
    assert "UNOBSERVED" in text
    assert "NOT a claim that HEAD is green" in text
    assert "not tracked" in text and "head_green_census" in text


def test_the_draw_no_longer_reads_the_tracked_bytes_at_all():
    """THE ITEM'S ACTUAL SUBJECT, keyed to the property rather than to the number 830.

    The two tracked files disagreed with each other: the JSON (committed 2026-09-02) said 830 and
    the register rendered FROM it (committed 2026-09-05) said 21. A derived file and its source
    cannot disagree when both are generated together, so the drift is itself the proof they were
    being committed independently, by hand, at different times.

    What a clean checkout must now read is neither of those numbers: it must read UNOBSERVED. This
    asserts over whatever the tracked bytes happen to say, so it keeps working when they are
    finally removed — rather than pinning today's answer.

    MUTATION: restore `OBSERVED_PATH` to the legacy tracked path and this fails.
    """
    committed = subprocess.run(
        ["git", "show", f"HEAD:{reg.LEGACY_OBSERVED_PATH.relative_to(PROJECT_DIR)}"],
        cwd=PROJECT_DIR, capture_output=True, text=True)
    if committed.returncode != 0:
        pytest.skip("legacy path already removed — this test's subject is gone, which is the goal")

    at_head = json.loads(committed.stdout)
    assert not reg._is_credible(at_head), (
        "the committed store must never be credible: it is a hand transcription with no pass "
        "count, and adopting it is what made every clean worktree read 830"
    )
    # and the register the DRAW reads is keyed to the live store, not to those bytes
    assert reg.OBSERVED_PATH != reg.LEGACY_OBSERVED_PATH


def test_the_committed_wreck_row_would_now_be_refused():
    """The row that caused all this is unwritable today — proving the untrack is not the only
    control and this cannot recur through the nightly path.

    MUTATION: allow `passed=None` through `record()` and this fails.
    """
    with pytest.raises(reg.UnobservedRunRefused):
        reg.record(["a::x"], head_sha="ec2e0b1a4", passed=None, store=_store([], {}))

    # sanity: the same row WITH its pass count is accepted, so the refusal is about the missing
    # field and not about the call shape
    ok = reg.record(["a::x"], head_sha="ec2e0b1a4", passed=830, store=_store([], {}))
    assert ok["runs"][-1]["passed"] == 830


def test_json_still_parses_where_it_exists():
    """Belt-and-braces: untracking must not have corrupted a live store on a machine that has one."""
    p = Path(reg.OBSERVED_PATH)
    if not p.exists():
        pytest.skip("no observation on this tree — the expected state in a fresh checkout")
    assert isinstance(json.loads(p.read_text()), dict)
