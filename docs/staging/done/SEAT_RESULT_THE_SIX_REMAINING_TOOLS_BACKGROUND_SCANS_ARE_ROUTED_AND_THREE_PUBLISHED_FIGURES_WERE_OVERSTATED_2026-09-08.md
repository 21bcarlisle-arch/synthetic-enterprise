**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The six remaining `tools`/`background` scans are routed, and three of them were overstating a published figure

Continues `SEAT_RESULT_ELEVEN_OF_THE_THIRTY_EIGHT_TOOLS_AND_BACKGROUND_SCANS_ARE_REAL_AND_THE_TWO_I_WAS_POINTED_AT_ARE_NOT_MEMBERS_2026-09-08.md`,
which routed five of the eleven real members and left six with a stated order. That turn's "what
is next" was the work; this is items 1 and 2 of it, and item 3 turns out to be bigger than it was
filed as.

**The drawn direction — read the `tools`/`background` population and route or dismiss each — is
now finished on its own terms: no known real member is left unrouted.** The census returns 28 rows
over that scope, and all 28 are dismissals.

## What moved, and it is three published figures rather than one

| # | Site | The reading | Was | Is |
|---|---|---|---|---|
| 6 | `background/shared_primitive_census::_primitive_inventory` | `vat_constant` callers | **5** | **3** |
| 6 | ditto | `rng_substream_primitive` callers | **45** | **44** |
| 7 | `background/gap_ledger_reconciler::discover_writers` | ledger writers | **21** | **20** |
| 10 | `tools/annual_report_import_ratchet::render_debt` | test files reaching into `_section_*` | **84** | **82** |
| 9 | `tools/half_hourly_dependency_ratchet::scan` | one frozen line carried its trailing `# Phase BR` | — | re-frozen |
| 8 | `tools/commit_refusal_attribution::gate_ranks` | gate order | equivalence today | poison-proven |
| 11 | `background/shared_primitive_census::_quantity_coverage` | quantity ownership | equivalence today | poison-proven |

**Every one of the three moves is in the same direction: the byte reading OVERSTATED.** The
primitive census said more of the tree had migrated to the shared primitive than had; the ledger
reconciler said more modules write it than do; the debt doc said the rebuild it defers is larger
than it is. That is not a coincidence — prose *about* a thing is written near the thing, so a
substring over source can only ever add members, never lose them.

The `vat_constant` row is the sharpest of them. `CLAUDE.md` names the VAT rule as the standing
example of one legal requirement with five implementations and nothing able to notice — and the
census that counts those implementations was itself counting two comments among them.

## The correction beside the claim it replaces

`test_a_marker_matched_on_PROSE_ALONE_produces_nothing` asserted the OPPOSITE of what now holds:
that `background/live_ledger_guard.py` **must** be discovered as a ledger writer, because
`write_site_attribution` gives it no rows and the count is therefore harmless. Both halves were
wrong, and the first one is the interesting one: the test said the mention lives in *help text*
(a call argument, which `searchable` keeps). It does not. It is the module's own **docstring**,
explaining that `tools/couple_*.py --write-ledger` mains are the class this guard leaves open.

That module is `_SELF` one degree removed. `gap_ledger_reconciler` already excludes ITSELF by name
because its own prose quotes the marker — a named exemption for one instance of exactly this class,
with nothing to catch the second. The name is now unnecessary and the class is closed instead.

## Item 3 was filed as one row and is at least two, which changes its remedy

`gate_ranks` is the one fix that did **not** retire its census row, and the reason is worth the
next reader's time. I fixed the defect the previous turn named — the secondary rank is a byte
offset into the emitter, so a paragraph describing a banner ranked the gate where the paragraph is
rather than where it refuses. The census still reports the function, because the site it reports
is a different line: `if emitter not in order`, where `order` came out of `_hook_order(hook_text)`.

That is the **dict-membership blind spot** the last turn filed against
`background/publisher_budget.declared_publisher_budget_seconds` — the taint sweep follows file text
into a call and cannot tell a text container from a structured one on the way out. Filed then as
"one row in 38". It is at least two, and both are in production scanners rather than tests, which
is where the population that has never been frozen lives.

**This does not change the recommendation, and it strengthens it.** The direction is fail-closed
towards reporting by design; the remedy is still an exemption carrying the reason, not a narrowing
of the sweep. But it is now a two-member class rather than a curiosity, so the exemption needs to
name the SHAPE (`x in <structure derived from parsed source>`) and not the two functions.

## A defect found on the way, which is why the published figure had no test

`render_debt(root)` honoured `root` for the importer count and read `PROJECT_DIR` for the
private-reacher count and the line count — two trees under one heading. That is why the published
figure had no control that could drive it: a planted tree was silently measured against the live
repo, so every attempt to test the count had to name real files and went red whenever another lane
added one. Both reads take `base` now, and the control is a `tmp_path` poison round with the
prose-only file and the real reacher both present, so the answer can only be 1.

## Reachability: poison first, because two of the six are equivalences

Two fixes change nothing on today's tree — `gate_ranks` returns the identical 21 pairs, and every
quantity still reads `has_owner=False`. A suite run is silent on whether the reading changed at
all. So each of the six was proved by REVERTING it and re-running its own suite:

```
spc-inventory  FAILED test_MUTATION_a_primitive_named_only_in_a_COMMENT_is_not_a_caller
spc-prose      FAILED test_MUTATION_an_ownership_claim_OUTSIDE_the_docstring_is_not_a_declaration
               FAILED test_a_declaration_below_2000_BYTES_of_imports_is_still_found
glr-writer     FAILED test_a_marker_matched_on_PROSE_ALONE_IS_NOT_A_WRITER
ar-private     FAILED test_MUTATION_the_published_private_count_is_of_CALLS_not_of_MENTIONS
hh-scan        FAILED test_MUTATION_a_marker_named_only_in_a_DOCSTRING_is_not_a_dependency
               FAILED test_MUTATION_a_trailing_comment_is_not_part_of_the_dependency
cra-rank       FAILED test_MUTATION_a_banner_named_only_in_a_COMMENT_does_not_move_the_gates_rank
```

Each is paired with the opposite end — a primitive that is really called, a banner that is only
ever printed, a real half-hourly read — because a control that refuses everything passes every
test that only asks whether it refuses.

`_quantity_coverage` is the one whose fix is not `searchable()`. It wants the docstring, so
blanking prose would delete its subject; it reads the docstring from the tree instead, and the old
`text[:2000]` window turns out to have been wrong in BOTH directions — a comment inside the window
counted, and a declaration below a long header did not.

## What is next

1. **Extend the baseline to `tools`/`background`.** `SCANNED = ("tests",)` is what `--check` and
   `--freeze` use; `--scope` only affects the listing, so extending the gate means moving that
   constant. The precondition the last turn named — local `main` four commits behind `origin` —
   has **expired**: the two are level, and the baseline and census are both local now. The real
   precondition was always the rows, and it is now met on one side and not the other: no real
   member is left, but all 28 dismissals would be frozen with their reasons living in these two
   staging documents rather than beside the rows.
2. **The dict-membership exemption, written as a shape** — see above; two known members.
3. **A hazard this turn did not create and could not clear.** `test_the_debt_record_states_its_own_size`
   is RED in the shared working tree and GREEN in every clean extract of HEAD: another lane holds
   an untracked test file that imports the report, so `test_importers()` reads 89 against a doc
   that says 88. `ANNUAL_REPORT_IMPORT_DEBT.md` is a hand-regenerated artefact whose working-tree
   copy is also two measurements BEHIND HEAD (86/82 against 88/83), so it is a rival copy and not
   a stale one. Left alone deliberately: regenerating it from this tree would publish another
   lane's count as ours, which is the reason the previous two regenerations were done by hand.
