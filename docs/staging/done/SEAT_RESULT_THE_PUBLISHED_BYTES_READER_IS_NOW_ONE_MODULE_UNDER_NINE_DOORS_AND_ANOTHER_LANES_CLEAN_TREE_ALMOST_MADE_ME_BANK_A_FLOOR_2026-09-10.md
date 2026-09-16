# SEAT RESULT — the published-bytes reader is one module under all nine door tests, and another lane's cleaner tree almost made me bank a floor nobody else could meet

**Severity:** RECORDED · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, lane 0 draw)
**Claim:** `lift-the-published-bytes-reader-into-the-other-site-door-tests`
**Follows:** `docs/staging/SEAT_RESULT_THE_BASELINE_DOOR_TEST_NOW_GRADES_THE_PUBLISHED_BYTES_AND_AN_UNLANDED_REPAIR_GOES_RED_2026-09-10.md`

---

## The premise, re-measured before starting

The item cites `712a7fc4e`, already an ancestor of `origin/main`. **Live, and the class was exactly
as described.** A grep across the eight other `site/test_*_door.py` and
`site/test_*_reaches_the_reader.py` files found the same one-line relapse in **every one of them**:
a `SITE / "data" / x.json` constant plus `.read_text()`, twenty-two read sites in total. The most
pointed instance is `site/test_published_caveat_reaches_the_reader.py`, whose constant was literally
named `PUBLISHED_PROOF` and read `site/data/proof.json` off the working tree.

## What done was taken to mean

Not "copy the helper eight times". A control duplicated nine times is repaired in one place and
rots in eight — this project has already paid for that shape once (one VAT rule, five
implementations, a July fix still live as a defect in August). So:

* `site/test_the_published_bytes_reader.py` — the mechanism and its proofs, ONE copy:
  `published_blob` (the index copy, fail-closed and in those words), `published_json`,
  `published_file` (materialised, because the render harness boots a FILE), `working_tree_reads`
  (the AST scanner) and `refuse_working_tree_reads` (the guard each file calls with its own
  `*_REL` constants) — plus the scratch-repo proofs, moved out of the baseline door test so they
  are stated once for all nine callers. Why one file and not two: see the third refusal below.
* All nine door tests now take repo-relative **strings** as subjects and read them through the
  reader. `site/test_the_baseline_comparison_reaches_the_reader.py` lost its private copy rather
  than keeping a rival one.

## What changed in the mechanism, and why it is not just a move

The scanner lifted from the baseline door test had two holes that only showed up once it met eight
files it did not grow up in:

1. **Its non-vacuity probe only proved the path-building arm.** The original asserted
   `caught, _ = scan(relapse)` — the read half was never checked, so half the guard could have been
   dead and the probe would have stayed green. Both halves are asserted now.
2. **A subject bound with `Path("site/data/x.json")` and read through the name was invisible** —
   the same defect with the `/` taken out. A one-pass binding step now taints any name assigned a
   subject *path*, and a READ call site matches on any string literal ending in a subject basename
   rather than on the quoted-token form.

The quoted-token/any-mention split is load-bearing and is asserted directly: `FEED_REL =
"site/data/x.json"` — the CORRECT spelling — must never be a hit, or the guard reds on every file
that adopts it and gets deleted within the day; while `open("site/data/x.json")` must be, because
at a read site what is done with the path is the whole question.

## The poison round, both legs, run and reverted

Not a mutation battery: a **pair**, because "green" has two readings and only one of them is a pass.

| leg | state | result |
|---|---|---|
| A | `site/data/book_growth.json` set `available: false` in the **working tree only** | **17 passed** — the tree copy is not the subject |
| B | the identical poison, staged into a **scratch index** (`GIT_INDEX_FILE`, so the shared index was never touched) | **4 failed** across both suites |

Leg A alone is satisfied by a reader that reads nothing at all; leg B alone says nothing about
where the bytes came from. The pair is the control. The relapse guard was poisoned separately —
`INDEX = HERE / "index.html"` restored in `test_home_door.py` — and named the line: *"builds a
filesystem path to a published subject at line(s) 37 (index.html)"*.

## The thing I nearly got wrong

`tests/architecture/test_static_quality_ratchet.py` went red with `I001: baseline 1309, now 1308`
and told me, in its own message, to **lower the baseline** because the tree is cleaner than frozen.

It was not my change. Measured three ways:

* clean `HEAD` extract → **I001 = 1309**, exactly the frozen baseline;
* the same extract **plus only my ten files** → **I001 = 1309**, and the whole ratchet suite
  green there;
* the shared working tree → 1308.

The missing violation is **another lane's uncommitted improvement**, sitting in this tree and in no
commit. Banking it would have frozen a floor that no clean extract — and therefore no other lane's
gate run — could meet. The baseline is untouched. *This is the mirror shape: the ratchet reds
because the working tree beats HEAD, and the instruction printed on the refusal is the wrong move.*

## The second refusal, and why the drop is honest

`surgical_land`'s stale-copy census refused two paths, saying my copies "would revert work that
has already landed": neither carries the literal lines `DD_ARMS = SITE / "data" /
"dd_opening_arms.json"` and `"../data/dd_opening_arms.json": json.loads(DD_ARMS.read_text(...))`
that `e07449df5` added on 2026-09-03.

Deleting those two lines **is the deliverable**. What `e07449df5` actually landed — the fourth
feed reaching the render payload of both doors — survives at the same two sites, respelled as
`DD_ARMS_REL` and `published_json(DD_ARMS_REL)`. The independent check is that the render harness
REJECTS a url the caller did not supply: a feed genuinely lost here reds both suites on
`_meta.unresolved`, and both are green. The census keys on the literal text of a line that moved,
which is the standard way a respelling reads as a revert; declared with `--drops` so the exemption
is in the landing output rather than invisible.

## The third refusal, and why I did not freeze it

The first shape of this was `site/_published_bytes.py` — a plain module beside its test file. The
gate refused with *"THIS COMMIT ADDS WORK THAT NOTHING RUNS: site._published_bytes"*.

That refusal is **structurally unanswerable in its own terms**, and checking why is what changed
the design. `tools/capability_index.py` classifies a module as evidence by NAME —
`is_evidence_file` is `test_*` or `conftest.py` — and drops it from the graph entirely. Asked
directly, the index returns `site._published_bytes -> callers []` and does not hold rows for any of
the nine importers at all. So a module whose only callers are test files can never acquire a caller
the ratchet can see. The two exits the refusal offers are to invent a production caller, or to
`--freeze` it as deliberately dormant. It is not dormant — it executes on every `pytest site/` and
inside the gate's own `site tests green` step — so freezing it would put a false statement on the
record to clear a control. `tools/orphan_ratchet.py` names that failure in its own comments
(`assert_deployed_bytes_are_served`, reported as an orphan on the commit that introduced it):
*"a control whose false positive is cleared by lying is worse than the gap it was closing."*

So the mechanism moved into `site/test_the_published_bytes_reader.py`, beside the proofs, under the
name the index already reserves for evidence. That is the classification being right rather than a
way around a gate: this is test support, it is named as test support, and it is still ONE copy.

**Worth noticing about the ratchet itself:** its message asserts a disjunction — wire it, or admit
it is dormant — that has no true branch for a test-support module. Nothing in it can tell a module
nothing runs from a module only evidence code runs, and the second reads as the first.

## What is next

* The producer-side artefacts that `test_the_stratified_concordance_reaches_the_reader.py` drives
  (`gv.THREE_ARM_PATH` and its current-world twin) are still working-tree reads. They are the
  generator's INPUT rather than the page, so they were deliberately left out of that file's subject
  list and the omission is stated in the file. Whether a door test should grade a pairing whose
  input is unlanded is the same question `MIX_REL` answers "no" to in the reason-mix door — worth
  settling as one rule rather than two.
* `site/proof/`, `site/world/`, `site/project/` and `site/knowledge/` hold further door tests that
  were not in this draw's scope. The class is closed for the nine files in `site/` root; it is not
  closed for the subdirectories.
* The local tree is **1 commit ahead and 2 behind `origin/main`** (`ad7a2f89f` is unpushed while
  origin gained `a06109741` and `bea5c02f2`). Not touched — reconciling a real divergence is not
  this item, and a merge here would risk the unpushed lane's work.

## Evidence

`pytest site/` — **759 passed, 36 skipped**, including the nine new relapse guards and the eight
proofs of the reader itself.
