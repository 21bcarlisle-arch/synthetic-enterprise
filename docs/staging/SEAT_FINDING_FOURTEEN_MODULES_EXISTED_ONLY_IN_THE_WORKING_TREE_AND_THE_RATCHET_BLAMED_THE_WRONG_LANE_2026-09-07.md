**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Discharged (in part):**
`tests/tools/test_orphan_ratchet.py::test_a_baseline_entry_deleted_only_in_the_working_tree_is_named_as_the_cause`,
`tests/tools/test_orphan_ratchet.py::test_a_module_absent_from_head_is_still_the_committing_lanes_new_orphan`,
`tests/tools/test_orphan_ratchet.py::test_the_two_refusals_are_not_the_same_sentence`,
`tests/tools/test_orphan_ratchet.py::test_an_unreadable_head_keeps_the_ordinary_refusal_rather_than_excusing`
-- four controls, each named for a defect in this document, all four mutation-proven below. The
census half is discharged by the disposition table; eight of fourteen paths remain held and each
names what it is waiting on.

# Fourteen modules existed only in the working tree, and the ratchet blamed the wrong lane

**Found 2026-09-07** by the delivery seat, drawn as LANE 0 DELIVERY. **Reproduce:**
`git status --porcelain | grep '^??' | grep '\.py$'`.

---

## Two halves of one shape: work nothing tracks, and a refusal nothing can act on

The shared tree is written by several lanes at once. Neither half below is a lane behaving badly;
both are what happens when a control's subject is *the tree* and its accusation is aimed at *a
commit*.

## Half one: the census

Fourteen `.py` paths existed on disk and in no commit. The doorbell that drew this counted
**thirteen** — `tools/stock_joint_generator.py` was written at 20:00 while the census was being
taken, which is itself the measurement: this population refills faster than anything looks at it.
The oldest had stood **51 days**.

Nothing in the harness counts this population. `tools/orphan_ratchet.py` deliberately excludes
untracked paths (a repair from 2026-09-03, and the right one — see half two), `tools/capability_index
--orphans` reports reachability rather than trackedness, and the publish gate grades a committed
tree. So an untracked module is invisible to every instrument here **and** to every clean extract,
which is exactly how a whole director-canon deliverable came to be sitting on disk with its poison
round run and nothing on the record saying so.

### The disposition, one at a time

| path | first written | disposition |
|---|---|---|
| `tools/test_generate_company_data.py` | 07-24 | **DELETED** — byte-identical to the tracked `tests/tools/` copy |
| `tools/test_generate_decisions_data.py` | 07-19 | **DELETED** — superseded; tracked copy fixes `PROJECT` depth |
| `tools/test_generate_market_data.py` | 07-20 | **DELETED** — same |
| `tools/test_generate_regulatory_data.py` | 07-18 | **DELETED** — same |
| `tests/tools/test_a_promotion_binds_its_landing_to_the_claim.py` | 09-05 | **LANDED** — subjects `tools/promote_worktree_landing.py`, `background/delivery_lane.py`; green |
| `tests/background/test_the_rows_that_concluded_on_a_sibling.py` | 09-05 | **HELD** — supplier symbol is uncommitted; see below |
| `tests/tools/test_settlement_ceiling_probe.py` | 08-30 | **HELD** — supplier symbols are uncommitted; see below |
| `tools/stock_joint_generator.py` | 09-07 | **LANDED** — `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS` item 1; repairs a live broken import at HEAD |
| `tools/reduction_dimension.py` | 09-07 | **HELD** — `DIRECTOR_CANON_THE_DEMAND_VECTOR` item 3; its declarations are uncommitted |
| `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py` | 09-07 | **HELD** — with the module above |
| `background/standing_red.py` | 09-05 | **HELD** — see below |
| `tests/background/test_standing_red.py` | 09-05 | **HELD** — with the module above |
| `tests/saas/reporting/test_a_departure_route_carries_its_denominator.py` | 08-31 | **HELD** — see below |
| `tests/architecture/test_no_document_asserts_a_licence_condition_that_does_not_exist.py` | 09-03 | **HELD** — see below |

The four deletions were not a judgement about the tests. `tests/tools/` holds all four as tracked
files: they were moved there on 2026-09-05 (`SEAT_FINDING_FORTY_TWO_TESTS_LIVE_WHERE_NO_RUNNER_LOOKS`)
by a copy that never removed the originals. The tracked copies are strictly better — they carry the
`parent.parent.parent` correction the `tools/` originals get wrong, so the originals would fail at
collection if any runner ever found them. Three of the four differ from their tracked twin **only**
in that line and its explanatory comment; one is byte-identical.

### Two of the dispositions were wrong, and the gate is what said so

The first landing named six paths and was **refused**, correctly, by
`tools/symbol_landing_check` — *"the consumer is in this commit and the supplier is not"*:

* `tests/background/test_the_rows_that_concluded_on_a_sibling.py` calls
  `background.self_clearing_alarm_census.rows_graded_by_resemblance` at seven sites.
* `tests/tools/test_settlement_ceiling_probe.py` calls `menu`, `arm_reach`, `book_at_ceiling` and
  `campaign_supply` on `tools/settlement_ceiling_probe.py` at twelve.

A second attempt was refused the same way, on the canon deliverable's own control:
`tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py` asserts over
`tools.demand_case_coverage.REDUCES_OVER` and `tools.weather_cell_derivation.REDUCES_OVER`, and
**neither declaration exists at HEAD** either — the lane that wrote canon item 3 wrote the module,
its control, and the two declarations it grades, and committed none of the three. So
`tools/reduction_dimension.py` is held with its suite as one unit.

**Not one of those thirteen symbols exists at HEAD.** Every supplier file is tracked *and dirty*, so
both suites are green in the shared tree and red in every clean extract of it. I had read "subject is
tracked, suite is green" as sufficient, and it is not: it is precisely the reading the shared tree
manufactures. The pair belongs in the held class with `standing_red` — same shape, an untracked
consumer whose supplier is somebody's uncommitted half — and the census's real count of *work that
exists only in the working tree* is therefore larger than fourteen files, because it includes edits
inside tracked ones that nothing counts at all.

**Three instances of one shape inside a single census**, which is the finding's real weight: the
untracked-`.py` count is a floor, not a measure. Under it sits a second population nothing names at
all — *uncommitted edits inside tracked files* that untracked work silently stands on. Every
instrument here reads either the working tree (which is generous) or HEAD (which cannot see the
consumer), and only the tree a commit would create answers the question.

Landing `tools/stock_joint_generator.py` repairs the mirror image of that: HEAD's
`tools/demand_vector_coverage.py` **already imports it**, so a committed module has been importing
one that does not exist. The consumer landed and the supplier did not, in the direction nobody
checks.

The general form: **an untracked test is not dispositioned by running it.** It is dispositioned by
running it against the tree the commit would create. Only `surgical_land` and a clean extract can
answer that, and the working tree will say yes to both halves of a contradiction.

### The still-held paths, and what each is waiting on

**`background/standing_red.py` + its suite (764 lines).** Its caller exists and is
`background/head_red_register.py`, which **another lane holds dirty** — 115 uncommitted insertions
adding `standing_verdict()` and a whole register section that imports this module. HEAD's copy has
no such import, so landing the module alone makes it an orphan and landing it by pathspec carries
that lane's in-place edits inside mine. Note also that the tracked `background/publish_standing_red.py`
opens with **the same five measurements in the same order** and shares `STANDING_AFTER_CYCLES = 2`:
two lanes built the standing-red ledger, one landed with callers, one did not. Which survives is a
decision, not a landing, and it is not this turn's.

**`tests/saas/reporting/test_a_departure_route_carries_its_denominator.py`.** Imports
`saas.reporting.annual_report`, and `tools/annual_report_import_ratchet.py` refuses any commit that
moves the importer count without `docs/design/ANNUAL_REPORT_IMPORT_DEBT.md` stating the new figure.
That doc is dirty in the shared tree right now. Land it with the doc edit, not around it.

**`tests/architecture/test_no_document_asserts_a_licence_condition_that_does_not_exist.py`.** The one
that is genuinely **red**, and the red is the classic shape: it scans tracked lines for `SLC 27B`,
and **all three** offenders it now names are *prose in a tracked test file describing this very
correction* —

    tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py:192,196,201

Landing it as written wedges every lane in the tree. It must **not** be cleared by widening
`EXCLUDED_PREFIXES`, which would blind it to the room where the real citations live. The file already
carries the right route: `_carries_a_declared_correction` clears any file that states the canonical
negation at its own top level. Add that one sentence to the offending file and this suite is green
and lands.

**And the wait it is waiting on has already cleared.** The offending lines are the `_KNOWN_UNLANDED`
entry in that same file, written 2026-09-06, which says the falsifier *"goes red there on ~16
documents still asserting a ±5% SLC 27B tolerance"* and names
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` as the lane it waits for. Those ~16 are gone: the
control now reports **three** offenders and all three are that entry's own prose. The register entry
describing the wait is the last remaining cause of it. So the move is a chain of three, in one
commit: state the canonical negation once at the top of
`test_no_committed_store_claims_an_unlanded_falsifier.py`, land the falsifier, and delete the
`_KNOWN_UNLANDED` entry — `test_every_declared_exemption_is_still_a_real_violation` reds if that entry
outlives its wait, which is the control that makes the chain safe to leave for the next turn.

## Half two: the refusal that named the wrong lane

**Three times in 24 hours**, an uncommitted deletion from `docs/design/orphan_baseline.json` refused
every lane committing in the shared tree. The first instance stood **22 hours**. Each time the text
was:

> orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS.
> &nbsp;&nbsp;`tools.people_physical_layer`

— naming a module the refused lane had never touched, in a commit that added nothing. Every word
after "orphan-ratchet:" was wrong. The mechanism is one line of arithmetic:

    added = orphans_now - working_tree_baseline["orphans"]

`orphan_baseline.json` is a shared file. When one lane removes an entry from its **working-tree**
copy and has not committed that, the module is still unreachable and is no longer excused, so it
enters `added` for **every** lane. The gate was correct that the tree was inconsistent and wrong
about whose act made it so — and CLAUDE.md's rule is that *a refusal names its reason, so the refusal
itself can be found to be wrong*. This one could not be: the only lane that could read it was the one
lane with no power to clear it.

### The fix is a discriminator, and it is HEAD

A module the accusation names that is frozen in `git show HEAD:docs/design/orphan_baseline.json`
**cannot have been made an orphan by the commit under test** — HEAD already said it was one, and
nobody had to fix it. Its absence from the working-tree copy is an edit to the baseline, and that
edit is the thing to name. `attribute_added()` splits the accusation on exactly that, and the two
halves print different sentences:

* `ADDED_HEADLINE` — unchanged, for a module HEAD never froze.
* `UNFROZEN_HEADLINE` — names `docs/design/orphan_baseline.json`, prints the `git diff --` and
  `git show HEAD:` commands that show the edit, and says plainly that re-running the commit will not
  clear it because the refusal belongs to whoever holds that file dirty.

It still **refuses** (exit 1) — the tree really is inconsistent — and it fails closed: when HEAD
cannot be read, `head_baseline()` returns `None`, which is not an empty set, and every accused module
keeps the original accusation. An attribution that guessed would excuse a real new orphan, which is
the one outcome the module exists to prevent.

### Poison round, run before the battery

Four mutations, each applied to the live source and each killed by its intended control:

| mutation | killed by |
|---|---|
| `attribute_added` returns `(list(added), [])` — *the code as it stood for the 22h instance* | `test_a_baseline_entry_deleted_only_in_the_working_tree_is_named_as_the_cause` |
| `attribute_added` returns `([], list(added))` — attribution becomes a blanket excuse | `..._is_still_the_committing_lanes_new_orphan`, `..._unreadable_head_keeps_the_ordinary_refusal` |
| `UNFROZEN_HEADLINE = ADDED_HEADLINE` — the two texts collapse | `test_the_two_refusals_are_not_the_same_sentence` (+1) |
| `head_baseline` returns `set()` rather than `None` on git failure | `..._unreadable_head_keeps_the_ordinary_refusal_rather_than_excusing` |

The third mutation is the one worth keeping: **every other assertion survives it.** `in err` is
satisfied by either headline and so is the exit code, so a change that quietly merged the two
sentences would undo the whole repair with a green suite. That is why the headlines are module
constants and why one control does nothing but assert they are different sentences.

## What is next

1. **The eight held paths**, each with the act named above — the SLC 27B one is a single sentence in
   a tracked file and unwedges a red.
2. **`background/standing_red.py` vs `background/publish_standing_red.py`** is a two-lanes-one-module
   decision, not a landing. Whichever is kept, the other's caller edits go with it.
3. **Nothing counts this population.** The census here is a one-off by a seat. The cheap version is a
   line in the orientation: untracked `.py` count and the age of the oldest. Three of the fourteen
   were canon deliverables and would have been findable on day one.
