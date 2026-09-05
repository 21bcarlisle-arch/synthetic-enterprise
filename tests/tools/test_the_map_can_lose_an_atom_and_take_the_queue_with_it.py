"""THE DEFECT: every control over the maturity map is written `for atom in atoms` — the five facet
checks, the level gate's own comparison, the draw, the coherence gate — so the map IS the subject
set, and an atom deleted from it is the subject of none of them.

Measured on the live tree 2026-09-05, before this rung existed: 175 of 314 atoms are named by
nothing in `depends_on`/`couples_with`/`blocked_on`; deleting one returned ZERO violations from all
five facet checks. The map's protection was the ACCIDENT of an atom being referenced.

AND IT HAD ALREADY FALLEN. Walking all 1,023 committed revisions of both halves: the union shrank
in three commits, losing 22 atoms. Twenty are argued at length in the commit that removed them;
`D6a_ageing_gap_metric_reshape` and `D6b_ambiguous_remittance_misdating` went in a commit titled
"C15: floor derive_supply_start at the account's own first observable" which does not mention
either of them. From the map alone the two cases are indistinguishable, which is the argument for
refusing rather than reporting.

Third in the family — `removed_dispositions()` on the alarm census (`dc5fcbbc8`), `removed_claims()`
on the canon register (`605ec3995`), `register_low_water.removed_rows()` the shared mechanism
(`6f4e6b1f4`). This file proves the WIRING separately from the rung, because a control that calls
the shared helper survives mutation of the caller.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import level_promotion_gate as g  # noqa: E402

MAP_AT_HEAD = "- id: A_kept\n  level_current: 1\n  level_target: 2\n" \
              "- id: B_leaf\n  level_current: 1\n  level_target: 2\n"
MAP_MINUS_B = "- id: A_kept\n  level_current: 1\n  level_target: 2\n"


def _run(**over):
    """The rung over an INJECTED baseline. Injected rather than read from git so every leg tests
    the control and not this repository's commit history — a leg keyed to today's map goes red the
    day the map legitimately changes and green forever if the rung stops working."""
    kwargs = dict(
        old_map_text=MAP_AT_HEAD,
        new_map_text=MAP_AT_HEAD,
        old_retired_text=None,
        new_retired_text=None,
        head_tracks_map=True,
        head_tracks_retired=False,
        staged_tracks_retired=False,
    )
    kwargs.update(over)
    return g.low_water_failures(**kwargs)


# ── RUNG 1: an atom that left the map ────────────────────────────────────────────────────────

def test_an_atom_deleted_from_the_map_is_refused():
    """The measured defect itself: the leaf that vanished has to be named by something."""
    out = _run(new_map_text=MAP_MINUS_B)
    assert len(out) == 1 and "B_leaf" in out[0]


def test_an_atom_retired_with_a_reason_is_allowed_through():
    """Not a rung that refuses everything. An atom CAN honestly be abolished — 20 of the 22 that
    have gone were — and the escape hatch has to work or the first honest pruning pass routes
    round the control."""
    assert _run(new_map_text=MAP_MINUS_B,
                new_retired_text="B_leaf: superseded by A_kept, no dependent outside its own set",
                staged_tracks_retired=True) == []


def test_the_rung_can_both_fire_and_clear_over_one_baseline():
    """ONE control over the whole partition. Two legs that each pass alone are also both passed by
    a rung that refuses everything and by one that refuses nothing; this is the assertion neither
    survives. CLAUDE.md's rare-branch rule applied to the branch nobody exercises."""
    two_gone = "- id: A_kept\n  level_current: 1\n  level_target: 2\n"
    base = MAP_AT_HEAD + "- id: C_leaf\n  level_current: 1\n  level_target: 2\n"
    out = g.low_water_failures(
        old_map_text=base, new_map_text=two_gone,
        old_retired_text=None, new_retired_text="B_leaf: folded into A_kept",
        head_tracks_map=True, head_tracks_retired=False, staged_tracks_retired=True)
    assert len(out) == 1 and "C_leaf" in out[0] and "B_leaf" not in out[0]


def test_a_retirement_reason_of_none_does_not_clear_the_refusal():
    """`str(None)` is "None", which is truthy. An explicit YAML null asserts nothing and must not
    read as a reason — the slip that was live in three census rungs until 2026-09-05."""
    assert _run(new_map_text=MAP_MINUS_B, new_retired_text="B_leaf:\n",
                staged_tracks_retired=True) != []


def test_a_refile_between_the_halves_is_not_a_removal():
    """The map is TWO files and `refile()` moves atoms between them. Measured over the live half
    alone the 2026-08-26 split reads as 224 deletions and every honest refile as one more; over
    the union it is zero. A rung keyed to one half would wedge the map's normal operation."""
    reordered = MAP_AT_HEAD.split("- id: B_leaf")[1]
    assert _run(new_map_text="- id: B_leaf" + reordered + MAP_MINUS_B) == []


def test_an_unestablishable_map_baseline_is_a_refusal_and_never_a_clean_result():
    """`None` and `frozenset()` are opposite claims. An empty baseline says "HEAD's map was empty,
    so nothing was removed" and would report clean on every tree where git cannot answer. Driven
    through the production route — the probe failing — not by passing a sentinel."""
    out = _run(old_map_text=None, head_tracks_map=None)
    assert len(out) == 1 and "could not be established" in out[0]


def test_a_genuinely_new_map_is_not_refused():
    """The other side of the same distinction, and the reason the three-valued probe exists at
    all: HEAD's tree POSITIVELY not containing the map is an established empty baseline. Refusing
    here would make creating a map impossible, which is a rung that refuses everything."""
    assert _run(old_map_text=None, head_tracks_map=False) == []


def test_a_head_map_that_is_tracked_but_unreadable_is_a_refusal():
    """The third value. The tree says the file is there and the read did not produce it — that is
    a broken read, and the flattering reading of a broken read is "nothing was removed"."""
    out = _run(old_map_text=None, head_tracks_map=True)
    assert out and "could not be read" in out[0]


def test_an_unparseable_head_map_refuses_rather_than_degrading_to_empty():
    """Deliberately STRICTER than `evaluate()` one function above, which degrades an unparseable
    baseline to {}. For a LEVEL comparison an empty baseline reads every atom as new and blocks
    nothing that matters; for a REMOVAL comparison it reports "nothing was removed", which is the
    flattering answer produced by a broken read."""
    out = _run(old_map_text="- id: [unclosed\n")
    assert out and "could not be parsed" in out[0]


# ── RUNG 2: a row that left the RETIREMENT register ──────────────────────────────────────────

def test_a_retirement_row_deleted_after_the_fact_is_refused():
    """Without this the reason can be erased ONE COMMIT after it cleared rung 1: by then the atom
    is gone from HEAD's map, so rung 1 has no subject and says nothing. Deleting the row would be
    the cure for the refusal the row was added to clear — the fail-open-with-an-extra-step that
    this whole family of controls exists to close."""
    out = _run(old_retired_text="B_leaf: folded in\nC_gone: abolished\n",
               new_retired_text="B_leaf: folded in\n",
               head_tracks_retired=True, staged_tracks_retired=True)
    assert len(out) == 1 and "C_gone" in out[0] and "append-only" in out[0]


def test_a_retirement_row_may_be_deleted_when_the_atom_comes_back():
    """The one honest way out, and what stops this being a regress (a retirement reason for
    retiring a retirement reason). An atom retired in error and restored to the map has no
    business in the register, and the map is the evidence."""
    back = MAP_AT_HEAD + "- id: C_gone\n  level_current: 1\n  level_target: 2\n"
    assert _run(new_map_text=back,
                old_retired_text="C_gone: abolished\n", new_retired_text="",
                head_tracks_retired=True, staged_tracks_retired=True) == []


def test_clearing_a_large_retirement_register_is_refused_once_and_names_the_count():
    """Collapsed to one refusal rather than one per row, because a wall of 22 identical complaints
    is how a reader stops reading. The count is in the message so it cannot be mistaken for a
    single dropped row."""
    out = _run(old_retired_text="".join(f"X{i}: abolished\n" for i in range(5)),
               new_retired_text=None, head_tracks_retired=True, staged_tracks_retired=False)
    assert len(out) == 1 and "5 row(s)" in out[0]


def test_clearing_a_small_retirement_register_still_names_every_id():
    """The other side of the collapse threshold, and the reason there is one: a message that names
    no id tells the reader a number and leaves them nothing to restore. Below the threshold the ids
    are worth more than the brevity, and a collapse-always rung fails this leg."""
    out = _run(old_retired_text="X_gone: folded in\nC_gone: abolished\n",
               new_retired_text=None, head_tracks_retired=True, staged_tracks_retired=False)
    assert len(out) == 2 and {"X_gone", "C_gone"} <= {w for f in out for w in f.split("`")}


def test_an_unreadable_retirement_register_grants_no_reasons():
    """A corrupt register must not read as an empty one. Empty grants no reasons and hides
    nothing; unreadable grants no reasons and hides every row that left it."""
    out = _run(new_map_text=MAP_MINUS_B, new_retired_text="- a\n- list\n",
               staged_tracks_retired=True)
    assert any("unparseable" in f for f in out)


@pytest.mark.parametrize("text", ["- not\n- a mapping\n", "just a string\n", "3\n"])
def test_a_register_that_is_not_a_mapping_raises_rather_than_reading_as_empty(text):
    """It is not a third half of the map and must not parse as one. `{}` here would say "nothing
    is retired", which reads every removal as unexplained — noisy rather than dangerous — but the
    same laxity applied to the HEAD copy would erase rung 2's entire subject set."""
    with pytest.raises(Exception):
        g.retired_reasons(text)


def test_an_empty_register_file_is_an_empty_register_and_not_an_error():
    """The register starts life empty and must not wedge the commit that creates it."""
    assert g.retired_reasons("") == {} and g.retired_reasons("# only a comment\n") == {}


def test_a_staged_register_that_is_tracked_but_unreadable_is_a_refusal():
    """Distinct from the parse failure above: the index says the file is there and the read did not
    produce it. Reading that as an empty register would be quieter — the removal below is refused
    either way — and quieter is exactly the danger, because the same laxity on the HEAD copy empties
    rung 2's whole subject set. Added after a mutation returning `{}` here survived."""
    out = _run(new_map_text=MAP_MINUS_B, new_retired_text=None, staged_tracks_retired=True)
    assert any(g.RETIRED_REL in f and "could not be read" in f for f in out)


def test_a_head_register_that_is_tracked_but_unreadable_hides_every_row_that_left_it():
    """The bite. If an unreadable HEAD copy read as `{}`, rung 2's baseline would be empty and every
    deleted retirement row would pass unseen — the register's own low-water mark falling silently,
    one level below the control that watches the map's."""
    out = _run(old_retired_text=None, head_tracks_retired=True,
               new_retired_text="", staged_tracks_retired=True)
    assert any(g.RETIRED_REL in f and "could not be read" in f for f in out)


@pytest.mark.parametrize("rel,expected", [
    ("docs/design/maturity_map.yaml", True),
    ("docs/design/no_such_file_exists_here.yaml", False),
])
def test_the_tracked_probe_separates_present_from_absent(rel, expected):
    """`git show` cannot answer this — it returns the same non-zero for "not at that revision" and
    "git could not run", and those are opposite claims. This is the probe that separates them."""
    assert g._tree_tracks("HEAD", rel) is expected


def test_the_tracked_probe_returns_none_when_git_cannot_answer(tmp_path, monkeypatch):
    """The third value, driven through the production route (git failing) rather than by passing a
    sentinel. A probe that answered True or False here would turn an unavailable check into a
    confident one, and the confident answer this control would reach is the flattering one. Added
    after a mutation returning True on probe failure survived every other leg."""
    monkeypatch.setattr(g, "ROOT", tmp_path)
    assert g._tree_tracks("HEAD", "docs/design/maturity_map.yaml") is None


# ── the subject set, and the wiring ──────────────────────────────────────────────────────────

def test_atom_ids_is_atom_levels_own_key_set():
    """NON-VACUITY plus anti-drift. Two walks over one register drift invisibly: the low-water rung
    would guard a slightly different population from the one the level rung gates, and neither
    would ever say so."""
    text = g._whole_map("HEAD:")
    assert text, "HEAD's map could not be read at all"
    ids = g.atom_ids(text)
    assert len(ids) > 100, "the extractor found almost nothing, so the baseline is not the map"
    assert ids == set(g.atom_levels(text))


def test_the_live_map_is_not_shrinking_right_now():
    """The rung pointed at the real tree. Green is the expected state; a red here means an atom was
    dropped in the working copy without the retirement register saying why."""
    head = g._whole_map("HEAD:")
    assert head is not None
    live = "\n".join((REPO_ROOT / rel).read_text(encoding="utf-8")
                     for rel in g.MAP_PARTS_REL)
    retired_p = REPO_ROOT / g.RETIRED_REL
    assert g.low_water_failures(
        old_map_text=head, new_map_text=live,
        old_retired_text=None,
        new_retired_text=retired_p.read_text(encoding="utf-8") if retired_p.exists() else None,
        head_tracks_map=True, head_tracks_retired=False,
        staged_tracks_retired=retired_p.exists()) == []


def test_the_seeded_register_carries_the_two_atoms_nobody_explained():
    """The register's own honesty. Twenty of the 22 lost atoms have an argued reason in the commit
    that removed them; two have none anywhere, and the row says exactly that rather than supplying
    a plausible sentence. A `None` with a named reason cannot be read as established; an invented
    reason can."""
    reasons = yaml.safe_load((REPO_ROOT / g.RETIRED_REL).read_text(encoding="utf-8"))
    # RE-KEYED 2026-09-05, from `assert len(reasons) == 22`, which was pinned to the register's
    # SIZE ON THE DAY IT WAS SEEDED. That reds the moment the register does its job -- the first
    # six renames recorded in it broke this control, and the cure was to edit the literal, a
    # two-line diff travelling with the very act the register exists to capture. A control keyed
    # to today's answer goes red when the record becomes MORE complete and stays green when it
    # rots, which is exactly backwards.
    #
    # The property is a FLOOR, not a count: the register may only grow, because an entry is the
    # sole surviving record of an atom that left the map, and deleting one is the defect this
    # whole file exists to catch (`test_a_register_control_needs_its_inverse`).
    assert len(reasons) >= 22, (
        f"the retirement register has shrunk to {len(reasons)}: an entry is the only record that "
        "its atom was ever on the map, so removing one removes the last thing that could notice"
    )
    for atom in ("D6a_ageing_gap_metric_reshape", "D6b_ambiguous_remittance_misdating"):
        assert "NO stated reason" in reasons[atom], (
            f"{atom} lost the statement that nothing was ever recorded for it"
        )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                   env={"HOME": str(repo), "PATH": "/usr/bin:/bin",
                        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch) -> Path:
    """A real git tree with a real index, because the wiring is the part that reads git. `ROOT` is
    monkeypatched rather than the subprocess cwd being guessed: every helper in the gate reads
    `ROOT` at call time, which is what makes this substitutable at all."""
    d = tmp_path / "r"
    (d / "docs" / "design").mkdir(parents=True)
    _git(d.parent, "init", "-q", str(d))
    (d / "docs/design/maturity_map.yaml").write_text(MAP_AT_HEAD, encoding="utf-8")
    (d / "docs/design/maturity_map_closed.yaml").write_text(
        "- id: Z_closed\n  level_current: 2\n  level_target: 2\n", encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "baseline")
    monkeypatch.setattr(g, "ROOT", d)
    return d


def test_the_gate_refuses_a_real_commit_that_deletes_an_atom(repo, capsys):
    """THE WIRING, not the rung, and end to end through `main()` against a real index. The rung can
    be perfect and `main()` never call it, or call it and drop what it returns — which is how this
    project has shipped green gates over live defects before."""
    (repo / "docs/design/maturity_map.yaml").write_text(MAP_MINUS_B, encoding="utf-8")
    _git(repo, "add", "docs/design/maturity_map.yaml")
    assert g.main() == 1
    assert "B_leaf" in capsys.readouterr().err


def test_the_same_commit_passes_once_the_atom_is_retired_with_a_reason(repo):
    """The wiring's OTHER side. A gate that returned 1 unconditionally would pass the leg above."""
    (repo / "docs/design/maturity_map.yaml").write_text(MAP_MINUS_B, encoding="utf-8")
    (repo / "docs/design/maturity_map_retired.yaml").write_text(
        "B_leaf: abolished, nothing depends on it\n", encoding="utf-8")
    _git(repo, "add", "-A")
    assert g.main() == 0


def test_a_commit_touching_only_the_retirement_register_is_still_gated(repo, capsys):
    """Rung 2's route to reality. The gate's trigger set used to be the map's two halves alone; a
    commit that deletes a retirement row and nothing else would not have staged either of them, so
    the branch would have been unreachable by construction — the deferral-guard shape from R15."""
    (repo / "docs/design/maturity_map_retired.yaml").write_text(
        "C_gone: abolished\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "retire C_gone")
    (repo / "docs/design/maturity_map_retired.yaml").write_text("", encoding="utf-8")
    _git(repo, "add", "-A")
    assert g.main() == 1
    assert "C_gone" in capsys.readouterr().err


def test_a_commit_touching_neither_is_not_gated_at_all(repo):
    """The gate has always been free for a non-map commit and must stay free: widening the trigger
    to the retirement register must not widen it to everything."""
    (repo / "unrelated.txt").write_text("x", encoding="utf-8")
    _git(repo, "add", "-A")
    assert g.main() == 0
