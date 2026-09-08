**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — the stale-copy census is not the mtime census

*A prediction, filed before the measurement, so the measurement could refute it. **It did.** The
result is at the bottom, beside the prediction and not in place of it.*

**Filed:** 2026-09-08, before running anything. Seat executor, lane 0.

## What I am about to measure

Lane 0 direction (b) says sixteen files are "in that state right now", oldest
`site/test_harness_delivery_record.py` (32.3h), `site/harness/index.html` (13.3h),
`tests/design/test_maturity_map_contract.py` (12.5h) — and it names the census that produced the
number: `git diff --name-only HEAD` filtered to code and pages, **comparing mtime against
`git log -1 --format=%ct -- <path>`**.

It then asks for a refusal keyed to something else: *the worktree copy's symbol set is a strict
subset of `git show HEAD:<path>`'s*.

**These are two different questions and I am predicting they give different answers.** The mtime
census asks "is this working copy older than the last commit that touched the path" — a
*suspicion*. The symbol-subset rule asks "would committing this copy delete a name HEAD has, while
adding none" — a *demonstration*. Every symbol-subset path should be an mtime-stale path, but most
mtime-stale paths will have no symbol loss at all: a lane holding a file open and editing a
function body is stale by mtime and destroys nothing.

Writing this down because the failure mode I want to avoid is reading "16" as the population the
guard should refuse, then tuning the guard until it agrees — which is
`feedback_a_synthetic_fixture_you_keep_retuning_until_it_agrees`, one level up.

## Predictions, before looking

1. **Strict-subset count < 16.** I expect somewhere in **2–8** paths, not 16.
2. `tests/design/test_maturity_map_contract.py` **is** a symbol-subset violator — the direction
   names it as 12.5h stale and it is a control file, where a stale copy is exactly the shape that
   deletes another lane's newly-added control.
3. `site/harness/index.html` — **no prediction**, and that is itself a finding if it holds: I do
   not yet know whether an HTML page has a symbol set worth extracting, and a guard that extracts
   nothing from a page passes it vacuously. If both sides extract to the empty set, the sets are
   equal, there is no strict subset, and the page is *waved through while looking checked*. That is
   `feedback_a_coverage_measure_can_be_useless_without_ever_being_fail_open` and I will say so on
   the page rather than let an empty extraction read as a clean verdict.
4. **The strict-subset rule under-catches the three banked BLOCKING findings.** A whole-file
   rewrite that deletes a mechanism *and adds its own new names* is not a strict subset, so
   `A_REWRITE_DELETED_THE_BINDING_REPAIR` would **not** be refused by this rule. I predict this
   before checking, and if it holds the guard must say so in its own docstring rather than be
   described as closing that class.

## What would refute me

A count at or near 16 refutes (1) and means mtime-staleness and symbol-loss are near-identical
populations here, which would make the mtime census the better subject and this rule redundant.
A strict-subset hit on a file no lane is holding refutes the premise that this is a concurrency
artefact at all.

## Result — measured 2026-09-08 against `/home/rich/synthetic-enterprise`

**Prediction 1: REFUTED, and not in the direction I hedged toward.** I said 2–8. The strict-subset
rule fired on **zero** of the 59 changed code paths. My mtime census reproduced the direction's
sixteen exactly — same members, same ages (`site/harness/index.html` 13.3h,
`site/test_harness_delivery_record.py` 32.3h, `tests/design/test_maturity_map_contract.py` 12.5h) —
so the two censuses were run over the same population and the disagreement is real, not a scoping
artefact.

**Prediction 2: REFUTED.** `tests/design/test_maturity_map_contract.py` is not a subset violator; its
working copy is a strict **SUPERSET** of HEAD, adding six names (`ALLOWLIST_FREEZE_COMMIT`,
`atom_ids_at`, three `test_MUTATION_*`, one check) and losing none.

**Zero was reachability, not blindness.** Poison round, run before believing the number: rebuild
HEAD's own copy of that file with one `test_MUTATION_*` removed and nothing added — the control
FIRES and names the removed test. The identity passes, a pure superset passes. A first poison
attempt did *not* fire, and that was the tell that mattered: I had poisoned the *working* copy,
which already carried six additions, so it was never a subset.

**Why the specified rule measures zero.** `surgical_land` **never writes the working tree** — that
is deliberate, and it is exactly what makes it safe for a two-lane file. So a landed commit leaves
every other lane's copy stale-by-mtime while its symbol set stays a superset of HEAD: the lane's own
additions are still there, and the other lane's are simply missing. **Symbol-set granularity cannot
see a landing it never received.** The sixteen are not a backlog the specified guard would have
cleared; they are a population it is structurally blind to.

**Prediction 3 (no prediction, flagged as a vacuity risk): held, and it mattered.** An HTML page
does have an extractable anchor set, but `site/harness/index.html`'s stale copy loses no anchors at
all — it is missing a 13-line *comment block* explaining why the frontier's rows must never render.
Under the symbol rule the page passes while looking checked. It is caught only by the line-level
rule, and only because the distinctive filter keeps prose lines in the evidence set.

**Prediction 4: HELD.** The strict-subset rule does not catch a rewrite that deletes a mechanism and
adds its own names, so it does not close `A_REWRITE_DELETED_THE_BINDING_REPAIR`. This is now stated
in `tools/stale_copy_refusal.py`'s own docstring rather than left for a reader to discover.

## What replaced it

`tools/stale_copy_refusal.py` refuses on **"your copy contains not one of the distinctive lines the
last commit to this path added"** — qualitative, no threshold, no fraction. `distinctive` = added by
that commit, non-trivial, and appearing exactly once in that commit's version of the file;
uniqueness is a property of the evidence, not a dial. It fires on **8** of the same 59 paths where
the specified rule fired on 0. Dropping the uniqueness filter drops the population to 5 — two
genuinely-stale files escape on a single coincidentally-repeated line — which is why the filter is
there and is the only reason it is.

The strict-subset rule is **kept as the second rule**, because it catches a deletion whose name came
from an older commit than the last one, which rule 1 cannot see. It was demoted from primary to
secondary by this measurement, not deleted by it.
