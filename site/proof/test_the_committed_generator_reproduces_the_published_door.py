"""The committed generator must be able to produce the committed artefact.

THE DEFECT, observed at HEAD c47221060 on 2026-08-15 and the reason this file exists.
`site/data/proof.json` is COMMITTED and LIVE (fetched: HTTP 200, 770,702 bytes,
`generated_at` 2026-08-15T04:41:21Z), and it carries `coupled_gaps.basis_audit_ran`,
`basis_finding_count` and `basis_findings` -- the D44 grader's verdict, 14 findings, rendered
to the public reader -- plus a non-empty `world_name`/`company_name` on every row. The
committed generator that nominally produces that block carries NONE of it:

    git show HEAD:tools/generate_proof_data.py | grep -c basis_audit_ran   -> 0
    git show HEAD:background/gap_metric.py | grep -c reserved_component_keys -> 0

So the published door was generated from an UNCOMMITTED working tree, and no tree in the
repository's history can reproduce it. That is the IaC wall in CLAUDE.md stated as a test --
"reconstruct-from-repo-alone" -- and it is the exact inverse of the defect
`test_published_caveat_reaches_the_reader.py` closes. That one catches CODE ahead of
ARTEFACT (a correction that never published). This one catches ARTEFACT ahead of CODE (a
publication no commit can account for). Both are the same seam; neither direction implies
the other, and until now only one had a falsifier.

WHY NOTHING WAS RED. Every check on this block takes ONE side as its subject. The panel
tests recompute the block from the working tree (`_live_coupled_gaps()`), so they see the
generator as it is right now and never ask what HEAD carries. The R11 door tests read the
published file, so they see the artefact and never ask what produced it. A tree where the
artefact is a generation ahead of the code satisfies both, which is what happened for two
days across H27 Expert Hours #28 and #30 -- both of which recorded their mechanism as
"closed" in this atom's own hold note while HEAD held none of it.

THE TWO SUBJECTS, and why they are independent. Subject A is the SHIPPED GENERATOR
(`tools.generate_proof_data._coupled_gaps`, imported and executed here). Subject B is the
PUBLISHED FILE (`site/data/proof.json` on disk, which the deploy uploads verbatim). The
whole defect is a gap between them, so neither may be derived from the other -- in
particular this file never regenerates the artefact and compares it with itself.

R15 BOTH WAYS, PROVEN AGAINST REAL HISTORY RATHER THAN A FIXTURE:
  RED   at c47221060 -- that tree's committed proof.json publishes `basis_audit_ran` and
        named rows; that same tree's committed generator emits neither.
  GREEN once the generator half is landed.
The defect this control catches is a state the repository was actually in, so the mutation
is history, not a mock.

WHY THE SITE LANE. `tools/git-hooks/pre-commit`'s site-lane step triggers on site/data, on
any `generate_*_data` producer, and on a site-consumed ledger -- i.e. on every change that
can move one of these two subjects without the other. The tests/ publish gate selects by
NAME STEM and would not run this.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent  # site/proof -> repo root
PUBLISHED_PROOF = PROJECT / "site" / "data" / "proof.json"


def _published_block() -> dict:
    """The `coupled_gaps` block of the PUBLISHED artefact.

    R15 FAIL-SILENT: a missing, unreadable or block-less artefact RAISES. An unavailable
    check is a FAILED check -- returning {} here would make every assertion below agree
    with nothing.
    """
    assert PUBLISHED_PROOF.is_file(), (
        f"{PUBLISHED_PROOF} is absent -- the published artefact is one of this control's "
        "two subjects, so its absence is a failure of the control, not a pass"
    )
    payload = json.loads(PUBLISHED_PROOF.read_text(encoding="utf-8"))
    block = payload.get("coupled_gaps")
    assert isinstance(block, dict) and block, (
        "the published proof.json carries no coupled_gaps block at all"
    )
    return block


def _shipped_block() -> dict:
    """What the SHIPPED generator emits for the same block, executed here.

    R15 FAIL-SILENT again, on the other side: the generator has an `available=False`
    early return for the case where `background.coupled_triad` will not import. That is
    the generator failing, not the generator agreeing -- so it raises rather than being
    compared, or a broken import would silently green this file.
    """
    sys.path.insert(0, str(PROJECT))
    from tools.generate_proof_data import _coupled_gaps, _load_atoms

    block = _coupled_gaps(_load_atoms())
    assert block.get("available") is True, (
        "the shipped generator could not build the coupled-gaps block "
        f"({block.get('note')!r}) -- an unavailable producer is a failed check"
    )
    return block


def test_the_published_block_carries_no_field_the_shipped_generator_cannot_emit():
    """ARTEFACT AHEAD OF CODE -- the direction that was live and unfalsifiable.

    Compared as KEY SETS, never as values: the two are generated at different times, so
    every timestamp, commit stamp and re-measured figure legitimately differs. What may
    never differ is the SHAPE, because the shape is what the code decides.
    """
    published, shipped = _published_block(), _shipped_block()

    # VACUITY GUARD. A key-set comparison between two empty sets passes forever.
    assert len(published) >= 5, (
        f"the published block has only {len(published)} keys -- too few for this "
        "comparison to be meaningful; the artefact is not the one this control is about"
    )

    orphaned = sorted(set(published) - set(shipped))
    assert not orphaned, (
        f"site/data/proof.json publishes {orphaned} and the committed generator emits no "
        "such key -- the artefact was produced by code that is not in this tree, so no "
        "commit can reproduce the door the public is reading. Land the generator, do not "
        "delete the field from the artefact."
    )


def test_the_shipped_generator_emits_no_field_the_published_block_is_missing():
    """CODE AHEAD OF ARTEFACT -- the same seam, other way round.

    Asserted separately rather than as one set-equality so a failure names WHICH way the
    two have parted; the two directions have opposite repairs (land the code vs regenerate
    and commit the artefact) and a combined assertion would recommend the wrong one half
    the time.
    """
    published, shipped = _published_block(), _shipped_block()
    stale = sorted(set(shipped) - set(published))
    assert not stale, (
        f"the committed generator emits {stale} and site/data/proof.json does not carry "
        "it -- the published door is a generation behind the code. Regenerate and COMMIT "
        "the artefact, then re-fetch the live URL and quote the served value."
    )


def test_every_pair_field_the_door_publishes_is_a_field_the_generator_still_builds():
    """One level in. The block's own key set is stable while a per-ROW field is added or
    dropped, and the rows are what the door renders -- 43 unreadable figures on these very
    rows were Hour #18's finding.
    """
    published, shipped = _published_block(), _shipped_block()
    pub_rows, ship_rows = published.get("pairs") or [], shipped.get("pairs") or []
    assert pub_rows and ship_rows, "one side publishes no coupled pairs at all"

    pub_keys = set().union(*(set(r) for r in pub_rows))
    ship_keys = set().union(*(set(r) for r in ship_rows))
    assert pub_keys == ship_keys, (
        "the published rows and the generator's rows do not carry the same fields: "
        f"only on the door {sorted(pub_keys - ship_keys)}; only in the code "
        f"{sorted(ship_keys - pub_keys)}"
    )


def test_a_field_the_door_fills_on_every_row_is_not_empty_from_the_shipped_generator():
    """THE HALF A KEY-SET COMPARISON CANNOT SEE, and it is not hypothetical: the
    2026-08-14 `name` drain moved every atom's `name` out of the map, and the generator's
    coupled-gaps rows went on reading it inline. The KEY `world_name` survived; its VALUE
    became `None` for all 296 atoms. A door rendering a blank name where the artefact has
    a paragraph is exactly as unreproducible as a missing key, and passes the checks above.

    The population is DERIVED from the artefact -- every row-field it fills anywhere --
    never a hand-typed list, so a field added tomorrow is covered the same day.

    THE QUANTIFIER IS THE WHOLE DESIGN, and the first draft of this test got it wrong in
    the fail-open direction. Written as "a field the artefact fills on EVERY row must be
    filled on every generated row", it passed at c47221060 -- the tree it was built to
    fail on -- because ONE published row of fourteen carries `world_name: ""`
    (`WORLD_recontracting_relationship_start`) and one carries `company_name: ""`
    (`W2_2_population_draw`), so a single legitimately-empty cell disarmed the field
    entirely. Caught by running it against that history rather than by reading it. The
    rule is therefore ASYMMETRIC and counts: fire when the artefact fills a field SOMEWHERE
    and the shipped generator fills it NOWHERE. That is the drain's actual signature
    (14 filled -> 0 filled) and it stays silent on a field that is sparse on both sides.
    """
    published, shipped = _published_block(), _shipped_block()
    pub_rows, ship_rows = published["pairs"], shipped["pairs"]

    def _fill_counts(rows):
        keys = set().union(*(set(r) for r in rows))
        return {k: sum(1 for r in rows
                       if isinstance(r.get(k), str) and r.get(k).strip())
                for k in keys}

    pub_filled, ship_filled = _fill_counts(pub_rows), _fill_counts(ship_rows)
    population = sorted(k for k, n in pub_filled.items() if n)
    # VACUITY GUARD: if the artefact fills no string field on any row there is no
    # population here and this test would pass by having nothing to check.
    assert population, (
        "no field is a non-empty string on any published row -- this control has no "
        "population and would be vacuous"
    )

    emptied = sorted(k for k in population if not ship_filled.get(k))
    assert not emptied, (
        f"the door publishes {emptied} with text on at least one row, and the shipped "
        "generator produces it empty or absent on EVERY row -- the reader is being "
        "served text no committed code can author. (The 2026-08-14 `name` drain did "
        "exactly this to world_name and company_name and raised nothing.) Published fill "
        f"counts {[(k, pub_filled[k]) for k in emptied]} of {len(pub_rows)} rows."
    )
