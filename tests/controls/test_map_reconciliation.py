"""RECONCILIATION GUARD: the map's level self-report must not silently diverge from
external truth (docs/design/MAP_TRUTH_RECONCILIATION.md, F2, 2026-07-15).

Root cause it guards: `maturity_map.yaml` `level_current` is a JUDGMENT-written self-report;
a fork writes its level to a narrow inbox at `docs/design/atom_status/<id>.yaml` and an
integrator folds it into the map via `tools/merge_atom_status.merge()`, which CLEARS the
inbox only after folding. An inbox left at rest is therefore a level report that never
reached the map — the exact self-report-vs-external-truth divergence the director gated the
unwatched loop on. This control FAILS on that signal (fail-closed), and is R15
mutation-proven: a planted inbox makes it fire; folding/clearing makes it pass.

The unwatched executor loop (background/executor_governor.run_loop) consults the SAME
primitive (`unfolded_inbox_ids`) as a per-cycle STOP condition, so the divergence class is a
loop halt, not a silent drift discovered hours later.
"""
import json
from pathlib import Path

import yaml

from tools import maturity_map_store as map_store
from tools.merge_atom_status import unfolded_inbox_ids

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_INBOX_DIR = REPO_ROOT / "docs" / "design" / "atom_status"
REAL_MAP_YAML = REPO_ROOT / "docs" / "design" / "maturity_map.yaml"


# ─────────────────────────────── the live guard ───────────────────────────────
def test_no_unfolded_atom_status_inbox_at_rest():
    """THE control: at rest, no atom carries an unfolded write-inbox. A non-empty
    result means a fork's level report never reached the canonical map — a silent
    map-vs-committed-work divergence. The loop treats this as a STOP."""
    unfolded = unfolded_inbox_ids(REAL_INBOX_DIR)
    assert unfolded == [], (
        "unfolded atom_status inbox(es) at rest -- a level report never folded into the "
        "map (self-report vs external truth, MAP_TRUTH_RECONCILIATION.md). Run "
        "`python3 -m tools.merge_atom_status` and commit the map, or delete the stale "
        f"inbox: {unfolded}"
    )


# ───────────────────── R15 MUTATION PROOF (mandatory) ──────────────────────────
def test_guard_FIRES_on_a_planted_inbox(tmp_path):
    """A planted inbox makes the guard fire (it is load-bearing, not tautological)."""
    (tmp_path / "SOME_atom.yaml").write_text("id: SOME_atom\nlevel_current: 2\n", encoding="utf-8")
    assert unfolded_inbox_ids(tmp_path) == ["SOME_atom"], "guard did NOT see the unfolded inbox"


def test_guard_PASSES_when_inbox_folded_and_cleared(tmp_path):
    """After the inbox is folded+cleared (merge()'s post-condition), the guard passes --
    proving it keys on the DIVERGENCE SIGNAL (inbox at rest), not on the dir existing."""
    inbox = tmp_path / "SOME_atom.yaml"
    inbox.write_text("id: SOME_atom\nlevel_current: 2\n", encoding="utf-8")
    assert unfolded_inbox_ids(tmp_path)  # fires while present
    inbox.unlink()  # merge(clear=True) deletes it after folding
    assert unfolded_inbox_ids(tmp_path) == [], "guard still fired after the inbox was cleared"


def test_guard_ignores_readme_and_non_inbox_files(tmp_path):
    """No false positive on the dir's README / non-*.yaml scaffolding (the real dir
    ships a README.md -- it must not read as an unfolded level report)."""
    (tmp_path / "README.md").write_text("# atom_status inbox dir\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("scratch\n", encoding="utf-8")
    assert unfolded_inbox_ids(tmp_path) == []


def test_guard_fail_closed_on_missing_dir(tmp_path):
    """A missing inbox dir is 'nothing unfolded' (clean), not an error -- the dir is
    created on demand by a fork; its absence is the empty state, never a false alarm."""
    assert unfolded_inbox_ids(tmp_path / "does-not-exist") == []


# ───────────────── the map must be INTACT, not merely parseable ─────────────────
# 2026-07-29: C11_segment_debt_policy carried FOUR copies of the
# (expert_hour, real_world_twin, depends_on) triple -- three other atoms' tails,
# appended to the wrong block by their registration commits. pyyaml keeps the LAST
# duplicate key silently, so C11's `depends_on` read as `[]` when it should have
# listed two atoms, and three atoms lost their `real_world_twin` entirely. Nothing
# ever noticed: the map parsed, every consumer got a dict, no value was missing --
# just the WRONG one. Same family as the unfolded inbox above (a self-report that
# never reached the map), and the same shape the director named on 2026-07-29: a
# single derived view that nothing independently contradicts. "It parses" is not
# "it is intact"; this asserts the STRUCTURE the parser throws away.
def _duplicate_keys_by_atom(text: str) -> dict:
    dupes = {}
    for node in yaml.compose(text).value:
        keys = [k.value for k, _ in node.value]
        repeated = {k for k in keys if keys.count(k) > 1}
        if repeated:
            atom_id = next(
                (v.value for k, v in node.value if k.value == "id"), "<no-id>"
            )
            dupes[atom_id] = sorted(repeated)
    return dupes


def test_no_atom_in_the_real_map_has_duplicate_keys():
    """THE control: a duplicate key is silent data loss -- the shadowed value is
    simply gone, and every reader agrees on the wrong answer."""
    # `map_text()` is the concatenation of BOTH halves, which is what this scanner wants: a
    # duplicate key is silent data loss wherever the record lives, and a closed atom's record
    # is still read by every survey. Scanning the drawn half alone would leave 224 records
    # unchecked by a control whose whole subject is records nobody re-reads.
    dupes = _duplicate_keys_by_atom(map_store.map_text(REAL_MAP_YAML))
    assert dupes == {}, (
        "atom(s) with duplicate keys -- pyyaml keeps the LAST silently, so the "
        f"shadowed value is lost with no error anywhere: {dupes}"
    )


def test_duplicate_key_guard_FIRES_on_a_planted_duplicate():
    """R15 mutation proof: the guard is load-bearing, not a tautology."""
    planted = (
        "- id: A\n  depends_on: [x]\n  depends_on: []\n"
        "- id: B\n  depends_on: [y]\n"
    )
    assert _duplicate_keys_by_atom(planted) == {"A": ["depends_on"]}


def test_duplicate_key_guard_is_SILENT_on_a_clean_map():
    """...and does not fire on healthy input -- a control that reds a clean map is
    worse than none (it trains you to ignore it)."""
    clean = "- id: A\n  depends_on: [x]\n- id: B\n  depends_on: [y]\n"
    assert _duplicate_keys_by_atom(clean) == {}


# ─────── the map's OPEN findings vs the adjudication ledger's own verdict ───────
# 2026-08-13: SITE2_two_sided_wall_exhibit's disposition tick fixed four cold-eyes
# findings, wrote the fix evidence into docs/observability/sanity_adjudication_ledger.json
# (state -> "fixed") and into the atom's simplifications record -- and left all four sitting
# in the map's `expert_hour.findings` list under the comment "open; each needs its own atom
# -- most are SIM/COMPANY fidelity, not render". Two records, one subject, opposite claims,
# and nothing anywhere compared them. Same family as the unfolded inbox and the duplicate
# key above: a self-report that never met the external truth it is a report OF. The map is
# the drawn-from record, so a finding that stays "open" there re-draws work already done and
# holds a level move that may no longer be held.
#
# THE LEDGER IS THE TRUTH here, deliberately: it carries the adjudication timestamp, the
# adjudicator and the fix evidence per key; the map carries a bare list. So the direction of
# the check is one-way -- ledger says CLOSED while the map says OPEN is a defect.
REAL_LEDGER = REPO_ROOT / "docs" / "observability" / "sanity_adjudication_ledger.json"

# States that CONTRADICT membership of an open-findings list. `adjudicated-false-positive`
# is deliberately NOT here: a refuted finding is part of the Hour's narrative record and the
# map annotates those in place (`# adjudicated REFUTED`), which is a disclosure, not a
# divergence. Only "the defect is gone" states contradict "still open".
CLOSED_LEDGER_STATES = {"fixed", "superseded"}


def _open_findings(atom, store_dir=None):
    """One atom's OPEN Expert-Hour findings, wherever they now live.

    THE REHOME FOLLOWED THIS CONTROL'S SUBJECT (2026-08-18). `expert_hour.findings` is
    drained into the sibling record store one atom at a time as the per-atom map budget
    names each one, and on 2026-08-18 it named SITE2_two_sided_wall_exhibit — whose single
    open key was, measured, the ENTIRE population this comparison had. A reader left on the
    inline field would not have drifted quietly: `test_the_findings_ledger_comparison_is_not
    _vacuous` fired the moment the keys moved, which is the fail-open guard doing exactly
    what its docstring promised. This function is the repair, not the workaround.

    Inline WINS over stored, matching `simplifications_store.hydrate`, `atom_name` and
    `generate_proof_data._expert_hour_findings` — one rule across every reader of a
    partially-migrated field. The inline value is what the spine is actually showing, so a
    silently-preferred store copy would make the two-sources-of-truth contract
    unfalsifiable.

    Only `expert_hour_findings` (the OPEN list) is read. Its sibling tenant
    `expert_hour_history_findings` holds the dated `fixed_*` record and is deliberately NOT
    consulted: those keys ARE closed in the ledger, so folding them in here would
    manufacture a contradiction per fixed finding and turn the guard into noise.
    """
    inline = (atom.get("expert_hour") or {}).get("findings")
    if inline:
        return inline
    aid = atom.get("id")
    if not aid:
        return []
    from tools import simplifications_store as store

    stored = store.records_for_atom(str(aid), store_dir).get("expert_hour_findings")
    return stored if isinstance(stored, list) else []


def _map_findings_vs_ledger(atoms, ledger, store_dir=None):
    """Returns (contradictions, resolvable_count).

    `contradictions` — (atom_id, finding_key, ledger_state) for every key listed under an
    atom's open findings (see `_open_findings` for where those live) whose ledger state says
    the defect is closed.
    `resolvable_count` — how many listed findings resolve into the ledger AT ALL. That
    second number is what stops this being a fail-open control: most atoms' findings are
    prose narrative, so an empty contradiction set is only meaningful if SOMETHING was
    actually compared.
    """
    contradictions, resolvable = [], 0
    for atom in atoms:
        if not isinstance(atom, dict):
            continue
        for key in _open_findings(atom, store_dir) or []:
            if not isinstance(key, str) or key not in ledger:
                continue
            resolvable += 1
            state = (ledger[key] or {}).get("state")
            if state in CLOSED_LEDGER_STATES:
                contradictions.append((atom.get("id", "<no-id>"), key, state))
    return contradictions, resolvable


def _real_map_and_ledger():
    return (
        map_store.load_atoms(REAL_MAP_YAML),
        json.loads(REAL_LEDGER.read_text(encoding="utf-8")),
    )


def test_no_map_finding_is_listed_open_while_the_ledger_records_it_fixed():
    """THE control: no atom advertises as an open Expert-Hour finding something the
    adjudication ledger records as fixed or superseded."""
    contradictions, _ = _map_findings_vs_ledger(*_real_map_and_ledger())
    assert contradictions == [], (
        "map lists finding(s) as OPEN that the adjudication ledger records as closed -- "
        "the fix landed and the map never heard. Move them out of `expert_hour.findings` "
        "(a dated `fixed_<date>` list keeps the history) or correct the ledger state: "
        f"{contradictions}"
    )


def test_the_findings_ledger_comparison_is_not_vacuous():
    """ANTI-BLINDNESS (R15 fail-open): the control above passes trivially if no listed
    finding resolves into the ledger. A key-naming convention that drifts, or an atom
    record rehomed out of the map, would empty the population silently and the guard
    would read green forever. This fails the moment there is nothing left to compare."""
    _, resolvable = _map_findings_vs_ledger(*_real_map_and_ledger())
    assert resolvable > 0, (
        "no `expert_hour.findings` entry in the real map resolves to a key in the real "
        "adjudication ledger -- the reconciliation above is comparing nothing and would "
        "pass whatever the ledger said"
    )


def test_findings_guard_FIRES_on_a_fixed_finding_left_in_the_open_list():
    """R15 mutation proof, the real defect: SITE2's shape exactly -- a finding the ledger
    calls `fixed` still sitting in `expert_hour.findings`."""
    atoms = [{"id": "A1", "expert_hour": {"findings": ["coldwalk:x_repaired"]}}]
    ledger = {"coldwalk:x_repaired": {"state": "fixed", "fix_evidence": "..."}}
    contradictions, resolvable = _map_findings_vs_ledger(atoms, ledger)
    assert contradictions == [("A1", "coldwalk:x_repaired", "fixed")]
    assert resolvable == 1


def test_findings_guard_is_SILENT_on_a_genuinely_open_finding():
    """...and does not fire on healthy input. An `adjudicated-real` finding IS open work,
    and an `adjudicated-false-positive` is a disclosed refutation -- neither is a
    divergence, so a control that flagged them would be noise that trains you to ignore
    it. The population is still counted, so this case is not silently vacuous."""
    atoms = [
        {"id": "A1", "expert_hour": {"findings": ["coldwalk:x_real", "coldwalk:x_refuted"]}}
    ]
    ledger = {
        "coldwalk:x_real": {"state": "adjudicated-real"},
        "coldwalk:x_refuted": {"state": "adjudicated-false-positive"},
    }
    contradictions, resolvable = _map_findings_vs_ledger(atoms, ledger)
    assert contradictions == []
    assert resolvable == 2, "healthy findings must still COUNT, or the anti-vacuity check lies"


def test_findings_guard_counts_nothing_when_the_keys_do_not_resolve():
    """R15 fail-open proof: prose findings and drifted key names resolve to nothing, and
    the guard reports that honestly as a population of ZERO rather than as a clean pass --
    which is the signal test_the_findings_ledger_comparison_is_not_vacuous acts on."""
    atoms = [{"id": "A1", "expert_hour": {"findings": ["the panel read as a leak", None]}}]
    contradictions, resolvable = _map_findings_vs_ledger(atoms, {"coldwalk:x_real": {"state": "fixed"}})
    assert contradictions == []
    assert resolvable == 0, "unresolvable findings must not be counted as compared"


# ───────────── the guard must follow a REHOMED atom out of the map ─────────────
# 2026-08-18: SITE2's open findings moved to the record store when the per-atom map budget
# named it. Measured before the move: SITE2's single key was 1 of 1 resolvable findings in
# the whole 314-atom map, so a reader left inline would have taken this comparison's entire
# population with it. These four are the R15 proof that the follow is real, in both
# directions -- the store is READ, the history tenant is NOT, and inline still wins.
def _store_with(tmp_path, atom_id, **fields):
    from tools import simplifications_store as store

    for field, value in fields.items():
        store.set_record_for_atom(atom_id, field, value, tmp_path)
    return tmp_path


def test_findings_guard_FIRES_on_a_fixed_finding_left_open_IN_THE_STORE(tmp_path):
    """THE rehome proof: the defect this control exists to catch must still be caught once
    the atom's findings live in the store. Same defect as the inline case above, same
    verdict -- otherwise rehoming an atom is a way to launder an open-vs-fixed divergence."""
    sd = _store_with(tmp_path, "A1", expert_hour_findings=["coldwalk:x_repaired"])
    atoms = [{"id": "A1", "expert_hour": {"status": "findings_open"}}]
    ledger = {"coldwalk:x_repaired": {"state": "fixed", "fix_evidence": "..."}}
    contradictions, resolvable = _map_findings_vs_ledger(atoms, ledger, sd)
    assert contradictions == [("A1", "coldwalk:x_repaired", "fixed")]
    assert resolvable == 1, "a rehomed atom must still COUNT toward the anti-vacuity check"


def test_the_history_tenant_is_not_read_as_open_work(tmp_path):
    """The dated `fixed_*` record moved to `expert_hour_history_findings`, and every key in
    it is closed BY CONSTRUCTION. Reading it here would manufacture one contradiction per
    fixed finding -- a control that fires on correctly-recorded history is noise that trains
    you to ignore it, which is the failure mode `test_findings_guard_is_SILENT_on_a_
    genuinely_open_finding` already guards on the other side."""
    sd = _store_with(
        tmp_path, "A1",
        expert_hour_findings=["coldwalk:x_open"],
        expert_hour_history_findings=["    fixed_2026_08_18:\n    - coldwalk:x_repaired"],
    )
    atoms = [{"id": "A1", "expert_hour": {"status": "findings_open"}}]
    ledger = {"coldwalk:x_open": {"state": "adjudicated-real"},
              "coldwalk:x_repaired": {"state": "fixed"}}
    contradictions, resolvable = _map_findings_vs_ledger(atoms, ledger, sd)
    assert contradictions == [], "the history tenant must not be read as open work"
    assert resolvable == 1, "only the OPEN tenant is the comparison's population"


def test_inline_findings_win_over_the_store(tmp_path):
    """One rule across every reader of a partially-migrated field (`hydrate`, `atom_name`,
    `_expert_hour_findings`): inline wins. A silently-preferred store copy would make the
    two-sources-of-truth contract unfalsifiable -- so a stale store copy must NOT be able to
    hide a divergence that is sitting inline in the map."""
    sd = _store_with(tmp_path, "A1", expert_hour_findings=["coldwalk:x_stale"])
    atoms = [{"id": "A1", "expert_hour": {"findings": ["coldwalk:x_repaired"]}}]
    ledger = {"coldwalk:x_repaired": {"state": "fixed"},
              "coldwalk:x_stale": {"state": "adjudicated-real"}}
    contradictions, _ = _map_findings_vs_ledger(atoms, ledger, sd)
    assert contradictions == [("A1", "coldwalk:x_repaired", "fixed")]


def test_the_REAL_map_still_has_a_population_after_the_rehome():
    """ANTI-VACUITY, anchored to the live tree rather than to fixtures. This is the test
    that went RED when SITE2's keys left the map and is the reason `_open_findings` exists;
    it names the atom so a future rehome that forgets the reader says which one."""
    _, resolvable = _map_findings_vs_ledger(*_real_map_and_ledger())
    assert resolvable > 0, (
        "no open Expert-Hour finding in the real map OR its record store resolves into the "
        "adjudication ledger -- if an atom was just rehomed, `_open_findings` is the reader "
        "that must follow it"
    )
