**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the standing red has a mechanism now, and replayed over the real log the worst one stood 38 cycles — not the 24 we had counted

**Built and measured 2026-09-05, delivery seat, from an isolated worktree at `origin/main` =
`48e0f20b4`. Pre-registration:
`SEAT_PREREGISTRATION_WHAT_A_STANDING_RED_LEDGER_WOULD_HAVE_ESCALATED_OVER_THE_REAL_LOG_2026-09-05.md`,
filed with the threshold already fixed, before the replay was written or run.**

---

## The premise was live, and the gap was exactly where the brief said

Both cited commits are ancestors of `origin/main`, but they are *measurements* — the build they
argued for had not happened. Confirmed by reading the path rather than the log: at refusal the
publisher already parses the hook chain's failing node ids
(`_record_commit_refusal_reds` → `_write_blocking_tests`) and writes them to
`.last_gate_blocking_tests.json`. **That file is a snapshot.** It is overwritten every cycle and
deleted on green, so a red that has refused twenty-four consecutive cycles is, at every reader in
this system, indistinguishable from one that broke a minute ago. No age, so no escalation, so the
publisher retries into a red that by measurement retrying cannot clear.

`background/head_red_register` is the nearest existing thing and it does not cover this: it is fed
only by the nightly HEAD-green census (`tools/head_green_census.py:502`), and the publisher's own
refusals reach it never.

## What was built

`background/publish_standing_red.py` — the ledger, with the same three properties the director
required of the HEAD-red register (a named subject, a live baseline, an end state where zero means
zero) applied to the other red. Wired at the one function that holds the node ids, spliced into the
draw at rank 36.

**It could not reuse `head_red_register`, and the reason is the design.** Two of that module's
load-bearing rules are wrong here:

- **Its population.** `runs_red` counts nightly census runs. This counts publish cycles. Folding
  one into the other gives a number whose denominator is two different things — the *average unit
  rate* shape.
- **Its absence rule.** `record()` sets `currently_red = False` for every test not in the failing
  set. Correct for a census, which runs the whole suite; **fatal for the hook chain, which is
  fail-fast.** A refusal naming test B does not make test A green — pytest stopped before reaching
  A. Adopting it would let one fail-fast refusal mark the entire backlog fixed, and the register
  would go quiet at exactly the moment the publisher was most wedged.

So the ledger's one asymmetry is its whole design: **appearing in a refusal adds; absence does
nothing; only the hook chain PASSING discharges.** It can over-report a red fixed by a commit that
never happened, and can never under-report one that is still blocking.

## The four pre-registered predictions all held

Replayed over the live 24MB runner log (`--replay`, re-derivable, not quoted):

| | predicted | measured |
|---|---|---|
| escalates at least one node id | ≥ 1 | **16 distinct**, 19 escalation events |
| largest `cycles_blocked` | ≥ 7 | **38** |
| a landing discharges a non-empty ledger | ≥ 1 | **11** of 230 landings |
| a refusal names no test and folds nothing | ≥ 1 | **149** of 219 refusals |

**The worst standing red stood 38 cycles, not 24.** The 24 in `988270c2e` was the largest
*same-gate re-refusal run*; this counts refusal cycles naming the same node id since the last
landing, which is a different and larger population. Both are right and they are not the same
number — naming them apart here rather than letting the larger one quietly replace the smaller.

The top five, by the most cycles each ever stood:

```
 38  tests/architecture/test_static_quality_ratchet.py::test_ruff_baseline_matches_frozen_census
 28  tests/architecture/test_static_quality_ratchet.py::test_ruff_no_stale_baseline_entries
 25  tests/background/test_derived_artefact_register.py::…::test_every_registered_artefact_is_currently_fresh
 24  tests/design/test_atom_notes_store.py::test_declarations_match_the_store
 24  tests/design/test_atom_records_store.py::test_declarations_match_the_store_both_directions
```

**Four of the top five are harness self-governance ratchets** — a ruff baseline census, a
freshness register, two store-declaration checks. Not one of them can make a published figure
wrong. That is a finding in its own right and it is left open here rather than acted on: it is the
next question, not this turn's.

**A caution on the replay's own limit, stated rather than smoothed.** `cycles()` reports
`subject: None` when the log's retained 40-line window cut above the pytest summary, and those fold
nothing — so the replayed ages are a **lower bound**. On this log that cost nothing
(`red_test_refusals_with_no_readable_subject: 0`), but the live path does not have the limit at
all: it reads both streams in full at the moment of refusal.

## Two defects caught while building, both of which would have shipped looking green

**1. The identity was the wrong string.** `_parse_failed_node_ids` returns the *full* summary line
— `FAILED tests/x.py::test_y - AssertionError: 0.31 != 0.29` — which is right for a snapshot that
wants the message and fatal as an identity. Any red whose assertion text carries a varying number
would be a new string every cycle and could never age past one. **That is `alarm_repetition`'s
founding incident re-entered through a different door**: six identical pages that no dedup caught,
because each carried `after {elapsed:.0f}s`. A ledger built to detect "the same red, again" that is
blind to exactly the reds that recur *would still have looked like it was working*, because it
would still have filled up. Fixed by `node_key`; the message is kept per-row where no counter is
keyed to it.

**2. A mutation survived, and it was a fixture gap, not an equivalence.** Folding *every* gate's
subject into the ledger (dropping the `cause == RED_TEST` guard) passed — because the first
fixture's non-test gate had no parseable subject, so the guard was never exercised. On the real log
it does: the level gate names an atom id, the finding-class gate names `.md` files, the
orphan-ratchet names modules. Folding any of them would put a non-test into a register of red tests
and age it as one. The fixture now carries a verbatim level-gate block and the mutation fires.

## The controls

Nineteen in `tests/background/test_a_standing_red_becomes_work_instead_of_a_retry.py`, each naming
its own defect. **Ten mutation-proven to fire**, including: absence discharging (the census rule
adopted), a landing that does not clear, the raw line as identity, the threshold widened without
evidence, the fold unwired from the publisher, the pass unwired from `git_commit_push` (the
ratchet), a phantom subject folded from an empty refusal, and the three replay legs.

Two of them are the ones that matter most and are worth naming:

- **`test_every_function_that_folds_a_refusal_also_records_a_pass`** walks the AST rather than
  today's two call sites, so a third refusal path added next month is covered without this test
  being edited. Keyed to the property — "these two calls are paired" — because a commit path that
  folds refusals in and never records its own pass turns the ledger into a ratchet for that path
  alone, and a register that only grows still *looks* like it is working.
- **`test_the_standing_branch_can_be_taken_and_the_not_yet_branch_can_too`** asserts both sides of
  the threshold over one ledger. A threshold that refuses everything passes every one-legged test
  of a threshold.

## The threshold, and why it is not a dial

`STANDING_AFTER_CYCLES = 2`, and its origin is `e0cc653c9`: **0 of 7** same-test re-arrivals in the
retained log demonstrably re-broke — every one was persistence. The observed base rate of "the
second refusal naming this test is a new failure" is zero out of seven, and nothing in this project
establishes a higher bar. It was fixed in the pre-registration before the replay existed precisely
so the replay could not tune it.

## What this does not do, and the lever it does not touch

It does not change the publish cadence. That was pre-refused before the split and the prediction
held at 17.1%, so the case for touching the inter-attempt gap is *weaker* after the measurement,
not stronger. It does not fix any of the sixteen reds it names — it makes them work with an age,
which is the thing that was missing. And it does not page the director: the escalation goes into
the draw, where everything with a route into the draw gets done.

## One standing red found in passing, and cleared

Landing this turned up a live instance of the very class above. `test_staging_rooms.py::
test_no_LIVE_reference_or_console_document_exists_ONLY_in_the_root` was **red at HEAD** — proven in
a clean `git archive HEAD` extract, so not mine — because another lane's
`SEAT_PREREG_WHETHER_ANY_REMEMBERED_LANDING_WAS_BOUND_BY_THE_FIRST_PARENT_GUESS_2026-09-05.md` was
filed into the queue root with no copy in `records/`. A pre-registration is a RECORD, so it needs
both. That one missing copy refused **every commit in this tree, from every lane**, and the fix is
one `cp`. Both that file and this turn's own pre-registration are now filed in their room.

It is worth naming what that is: a red standing in the publish path, blocking everything, costing
whole cycles, and nothing in the system able to say how long it had been there. That is the finding
this whole turn is about, met on the way to landing it.

## Where the derivation lives

`python3 -m background.publish_standing_red --replay <log>` prints every figure above. The register
it renders is `docs/staging/reference/PUBLISH_STANDING_RED_REGISTER.md`; the live store is
`docs/observability/publish_standing_reds.json`, which starts **empty on purpose** — seeding it
from the replay would be inventing state the live path never observed, and the next refusal is at
most one cycle away.
