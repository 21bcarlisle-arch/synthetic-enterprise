**Severity:** RECORDED (read down from BLOCKING 2026-09-03T03:2xZ by §"The open half, closed",
which supplies the eleven-gate coverage the filer left open and states the two refusal paths that
still resist a needle, with the reason each resists. The instrument no longer answers "cannot
tell" for eleven of fifteen causes; it answers for fourteen and declares the residue. Mutation-
proven in both directions.) · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The gate-naming table matched nothing five of its seven gates print

Grades `PREREG_WHETHER_THE_REFUSING_GATE_BANNER_TABLE_STILL_MATCHES_ITS_GATES_2026-09-03.md`,
written before any of the measurements below.

**CLASS:** controls_that_cannot_fail

## What was drawn, and why this is not it

The drawn brief was "dispose of `tools/artefact_rerun_diff.py` and make the publish-gate
classifier able to name a non-test refusal". **Both halves were already landed** by another seat
at `19f226e46`, with follow-ups at `eb0fae2fc` and `15709e9e8`. This seat adopted rather than
rebuilt, and verified by the subject exactly as the brief demanded — all three done-conditions
hold on the shared tree:

| Done-condition | Reading, 2026-09-03T02:09Z |
|---|---|
| `publish_freshness.describe()` not DOWN | `live -- figures reached origin 0.2h ago` |
| origin `site/data/` later than `1c4f64733` | `b6b3c3fa8`, 2026-09-03 02:55 +0100 |
| `run_complete_*.md` falling | **0** queued, 1452 in `done/` (was 35) |

`python3 -B tools/orphan_ratchet.py` prints nothing, rc=0. The brief said *"if clearing this
reveals the next gate rather than a green publish, name it and clear that one too."* It revealed
a green publish. So this finding is about the thing the fix itself left broken.

## The defect

`background/process_run_complete.py:_REFUSING_GATE_BANNERS` is the table that names the non-test
gate which refused a publish commit — the whole point being that a reader is not sent to a suite
that was never the problem. It shipped with seven rows. **Five matched nothing any gate prints.**

Measured against the strings the gates actually emit:

| Row | What the gate really prints | Verdict |
|---|---|---|
| `orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS` | same | live |
| `FINDING-CLASS CONSOLIDATION BROKEN` | `[test-gate] ❌ FINDING-CLASS CONSOLIDATION BROKEN` | live |
| `WRITE-TIME GATE` | `[write-time-gate] ❌ COMMIT REFUSED` | **dead** |
| `LEVEL PROMOTION` | `[level-gate] ❌ COMMIT REFUSED` | **dead** |
| `LIVE LEDGER` | raises `LiveLedgerWriteUnderTest`; not a chain gate at all | **dead** |
| `FINDING SEVERITY` | the words occur nowhere in this repository | **dead** |
| `I001` | ruff's code; `tools/git-hooks/pre-commit` never invokes ruff | **dead** |

Run against the gates' real refusal lines, `_parse_refusing_gate` returned `None` for the
level-promotion gate, the write-time gate and the live-ledger guard. So a **level-promotion
refusal — the second gate in the chain** — reported `UNNAMEABLE` about a refusal that names
itself on the very next line of the buffer being parsed.

That is the same defect the table was written to end, alive inside the fix for it. The original
cost 18.7 hours of publishing down.

## Why its own R15 suite could not see it

`tests/background/test_a_non_test_gate_refusal_is_named.py` is a good suite and every leg passed.
Its fixtures are strings **the test file supplies**. The table and its control were therefore
written from one guess about what a gate prints, and a shared wrong guess is invisible to both
sides. Nothing in the tree reached a gate.

This is the tautology killer wearing fixture clothes, and it is worth stating as a rule:

> **A control whose fixture and whose subject were authored in the same act by the same author
> can only test that the author was self-consistent.** It cannot test that either matched the
> world. The fixture must be taken from the thing being described, or something must compare
> them.

One further trap, and it is the reason `git grep` is the wrong instrument here: `WRITE-TIME GATE`
**is** in `tools/write_time_gate.py` — it is line 1 of the module docstring. Source-presence says
PRESENT; the process prints it never. Presence in source and presence in output are two different
questions and only one of them matters.

## The repair, landed in the same commit

1. **The table is rebuilt from the gates' own source**, in the order `tools/git-hooks/pre-commit`
   actually runs them. Each row is now `(name, needles, emitter)`.
2. **Needles are ALL-OF, not one substring.** The write-time gate assembles its line as
   `f"[write-time-gate] {head}"`, where `head` is `❌ COMMIT REFUSED` in gate mode and
   `⚠️  WARN ONLY` in warn mode. Matching the prefix alone would name it as the refuser of a
   commit it deliberately let through — the false-positive direction, which is *not* fail-safe.
3. **`tests/background/test_a_refusing_gate_banner_is_a_string_a_gate_prints.py`** is the
   comparison that did not exist. Keyed to the property — *every needle is a non-docstring
   string literal in the file named as its emitter* — not to today's wording. Rows may be added,
   dropped or reworded freely; what cannot happen is a row that no gate prints. A gate that
   rewords now goes **RED here**, named, instead of quietly unnameable in the register.
4. **The order leg is corrected, and the correction is itself the evidence.**
   `test_the_first_banner_in_the_chains_order_wins` asserted that `orphan-ratchet` beat the
   consolidation banner. `pre-commit` runs the test gate at line 24 and the ratchet at line 111,
   so that was backwards — and it passed anyway, for two compounding wrong reasons: the table
   listed the ratchet first, and the fixture's second banner lacked the `❌` the gate actually
   prints, so it could not have matched in either order. A control agreeing with itself.

Mutation-proved, four legs, each firing on its own subject (`python3 -B`, so no stale `.pyc`):

| Mutation | Leg that went RED |
|---|---|
| restore the dead `WRITE-TIME GATE` needle | `test_every_needle_is_a_string_its_named_emitter_actually_prints[write-time gate]` |
| `all()` → `any()` in `_parse_refusing_gate` | `test_all_of_a_rows_needles_are_required_not_any_of_them` |
| move the write-time row to the front | `test_the_table_is_ordered_by_the_chain_that_actually_runs_the_gates` |
| count docstrings as printed | `test_a_needle_that_only_appears_in_a_docstring_is_rejected` |

21 pass across the two files; the tree restores green after each mutation.

## The prereg, graded

- **P1 — "at least one first-party banner does not appear literally in the source of the gate it
  names": CONFIRMED, and it splits in a way the prediction did not anticipate.** Four of six were
  absent. But source-presence turned out to be the wrong instrument, and it erred in **both**
  directions: `FINDING-CLASS CONSOLIDATION BROKEN` was absent from `finding_classes.py` and is
  genuinely printed — by `tools/pre_commit_test_gate.py`, so the *emitter* was misfiled and the
  row was live (a false fail); `WRITE-TIME GATE` was present in `write_time_gate.py` and is
  printed by nothing, because it is a docstring (a false pass). Graded against printed output
  instead, the count is **5 of 7 dead**, worse than predicted.
- **P2 — "at least one banner is short enough to match a line that is not a refusal": REFUTED as
  stated, and its mechanism then found live in my own repair.** I predicted the four bare
  uppercase fragments would produce false positives. They cannot: they match nothing at all, so
  they can never fire in either direction. The prediction was wrong about the original table.
  The mechanism it describes is real, and I walked into it — the obvious repair for the
  write-time row is the bare prefix `[write-time-gate]`, which matches warn mode. Having written
  P2 down first is the only reason I looked, and it is why needles are ALL-OF above. **Recording
  this as a refutation and not as a hit**, because the subject I named was wrong even though the
  shape I named was right.
- **P3 — "no control in the tree relates the table to the gates": CONFIRMED.** The only
  references outside `process_run_complete.py` were five calls in the test file, all against
  fixtures it supplies itself.

## What is owed next, stated rather than papered over

**Coverage is partial and the code now says so.** `tools/git-hooks/pre-commit` invokes **15**
gates; the table names four of them, plus the write-time gate from `commit-msg`. The other eleven
— `site_lane_gate`, `moap_coherence_gate`, `ruling_archive_question_gate`, `consolidation_rhythm`,
`size_ratchet_gate`, `company_network_isolation`, `file_scope_generated_paths`,
`annual_report_import_ratchet`, `half_hourly_dependency_ratchet`, `running_total_order`,
`scope_evidence_ratchet` — still report `UNNAMED`, which reads honestly as "we cannot tell".

That gap is deliberate and is **not** closed by guessing. A needle invented without reading the
gate that prints it is precisely what produced the five dead rows this finding is about, and
authoring eleven more from module names would reproduce the defect at scale while turning the
control green. `test_the_table_does_not_silently_claim_to_cover_the_whole_chain` holds the
disclosure so a later reader cannot mistake `UNNAMED` for "not a gate".

**Why this stays BLOCKING:** by `finding_severity` clause 2 a finding whose plain text says an
instrument was wrong is BLOCKING by construction, and that is not the filer's to soften. The
half repaired here is closed; the eleven-gate coverage gap is what remains open, and it is an
instrument that answers "cannot tell" for eleven of fifteen real refusal causes.

---

# The open half, closed (2026-09-03, autonomous worker, at `964def09f`)

Grades `WORKER_PREREGISTRATION_WHETHER_THE_ELEVEN_UNNAMED_GATES_CAN_EACH_BE_GIVEN_AN_HONEST_NEEDLE_2026-09-03.md`,
written before any measurement below.

**First, the shared tree was two commits behind origin.** The repair above was pushed but the
shared worktree had not fast-forwarded, so every daemon reading this tree was still running the
five-dead-row table. Pure fast-forward `b06af4336` → `964def09f`; two untracked staging files
byte-identical to origin's were what blocked it. *Pushed is not imported.*

## What was done

All eleven needles read from the refusal branch of the gate that prints them, never from a module
name. The table goes 5 rows → 17, covering **14 of 14** `|| exit 1` gates in the chain.

Two shapes the filer's framing had no slot for, both found by reading rather than predicted:

1. **A gate may need two ROWS, not two needles.** `half-hourly-dependency` refuses both for a NEW
   half-hourly read and for a frozen read that is GONE. The messages share no literal that its
   PASS lines do not also print, and needles are ALL-OF, so one row cannot express the disjunction.
   Two rows under one name is the honest form.
2. **The unnameable unit is a refusal PATH, not a gate.** `size_ratchet_gate` has two: the
   CHECK UNAVAILABLE path has a clean literal and now has a row; the violation path does not and
   cannot get one — it prints `f"[{tag}] ..."` where `tag` is `SIZE-RATCHET` or `SIZE-RATCHET WARN`,
   so the token separating a refusal from a warn-mode pass is **interpolated, not a literal**, and
   the shared prefix is also printed on a `return 0` override path. A needle there would name it as
   the refuser of commits it let through.

`_UNNAMEABLE_REFUSAL_PATHS` now carries that residue with the reason each entry resists a needle,
so `UNNAMED` still reads as "we cannot tell" and never as "not a gate".

## A second dead control, found while fixing the first

`test_the_table_is_ordered_by_the_chain_that_actually_runs_the_gates` looked its rows up by
filename. **Six of the fourteen gates are invoked `python3 -m tools.x`, which contains no `x.py`** —
so those six were silently skipped and the order claim covered eight rows while reading as though
it covered all of them. Same family as the defect above: a control that answers about a subset it
never says it narrowed to. Now tries both forms.

That this matters is not asserted, it is measured: with the scope-evidence row moved to the front
of the table (it runs LAST, at hook line 251), the order leg **passes** without the `-m` lookup and
**fails** with it. Sole witness.

## The disclosure leg was itself the shape it guards against

It asserted `len(invoked) > len(_REFUSING_GATE_BANNERS)` — a count of hook LINES against a count of
ROWS. Those are not the same quantity: one gate may hold two rows, one module may host two gates.
It would have gone RED for coverage **improving**, which is exactly backwards, and it could never
have named which gate was missing. Replaced by the property — every gate the chain runs is either
named by a row or declared unnameable with a reason — which fires, named, when a gate is added to
the hook and its row is forgotten.

## Mutation-proved, `python3 -B` throughout

| Mutation | Leg that went RED |
|---|---|
| move the scope-evidence row to the front | `test_the_table_is_ordered_by_the_chain_that_actually_runs_the_gates` |
| delete the running-total-order row | `test_every_gate_the_chain_runs_is_either_named_or_declared_unnameable` |
| empty `_UNNAMEABLE_REFUSAL_PATHS` | `test_the_table_does_not_silently_claim_to_cover_the_whole_chain` |

22 pass in this file (was 12), 34 across both (was 21); the tree restores green after each.

## The prereg, graded — two of three refuted

- **P1 — "at least two of the eleven cannot be given an honest needle at all": REFUTED.** Zero of
  the eleven. Every one got at least one row. The prediction's *unit* was wrong: the thing that
  resists a needle is a refusal PATH, and the one that resists belongs to a gate that is otherwise
  perfectly nameable. Predicting per-gate could not have expressed the answer.
- **P2 — "at least one banner also appears on a non-refusal path": CONFIRMED in the hazard,
  REFUTED in the remedy.** `size_ratchet_gate` is exactly that case. But I predicted the fix would
  be the write-time gate's two-needle ALL-OF shape, and it is not — ALL-OF cannot help when the
  distinguishing token is never a literal at all. The path had to be declared unnameable instead.
  **Recording this as a refutation, not a hit**: naming the hazard correctly while being wrong
  about what it forces is not a successful prediction.
- **P3 — "the chain is not fifteen gates; status-honesty's banner is the hook's": CONFIRMED.**
  Fourteen `|| exit 1` module invocations; `status_honesty` is invoked `|| { ... }` and its banner
  is echoed by the SHELL HOOK — `background/status_honesty.py` prints only JSON. The filer's
  arithmetic (15 = 4 named + 11 remaining) was self-consistent, but status-honesty sat in neither
  group, and it is the one gate that **structurally cannot** have a row: the control reads Python
  source for printed literals, so a shell emitter has no checkable string.

## What is owed next, stated rather than papered over

- **`size_ratchet_gate`'s violation path should stop being unnameable at the source.** The honest
  repair is in that gate, not in this table: print the state as a literal rather than interpolating
  a tag. Not done here — it is a different lane's file and this turn had no measurement of what
  reads its output.
- **`status_honesty` likewise**, if its banner moves from the hook into the module.

Both are recorded in `_UNNAMEABLE_REFUSAL_PATHS`, so neither can be mistaken for "not a gate".

**Discharged: the eleven-gate coverage gap this finding held open.** The table names fourteen of
fourteen chain gates, the residue is two declared refusal paths each carrying its reason, and the
two controls that could not fail for the defects present are keyed to the property and
mutation-proven. Severity read down to RECORDED.
