**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the key-level term answers both directions, and the loss half had to be a SENTENCE, not a licence

Drawn as `teach-the-stale-copy-reading-a-key-level-term-in-both-directions`. Closes the open half of
`SEAT_FINDING_THE_SAME_KEY_IS_NOT_A_SYMBOL_BLIND_SPOT_NOW_REFUSES_TO_CLEAN_A_REVERT_IT_ONCE_OFFERED_TO_CREATE_2026-09-24.md`
(`db1c8460e`). Pre-registration:
`docs/staging/records/SEAT_PREREG_HOW_WIDE_IS_A_KEY_LEVEL_LOSS_TERM_BESIDE_THE_SYMBOL_LEVEL_ONE_2026-09-24.md`.

---

## The premise, re-measured first

All three commits the item cites — `971e3680c`, `19f340e65`, `db1c8460e` — are ancestors of
`origin/main`. The DETECTION half is landed and spent, as the draw said.

What is **not** spent, and was re-measured on the shared tree before any code was written:

* `saas/reporting/annual_report.py`'s working copy drops `gas_shape_provider_by_customer` and
  `gas_shape_refusals` against `origin/main`, and gains no dict key
* `symbols()` returns the same set for both sides, both ways round
* `stale_copy_refusal.judge(...)` returned **`None`** — no complaint at all
* the door's refusal read "**it deletes no name**"

Those bytes were **not touched**, as the item required. The subject path is still in the state the
finding exists to explain.

**Duplicate-work disposition.** `teach-the-stale-copy-reading-a-key-level-term-in-both-directions`
is held under this very id — it is this draw's own claim, the known self-citing shape, not a rival.
`nothing-can-tell-a-working-boot-stamper-from-a-dead-one` holds `saas/reporting/annual_report.py`,
which this turn never writes; different work on a path this item explicitly leaves alone. Neither is
dispositioned; both stand.

**Base.** This worktree was 0 behind / 0 ahead of `origin/main` at `db1c8460e` throughout, so the
draw's `[stale-copy]` caveat (46 behind) describes the shared tree and not the tree these verdicts
were computed in. Every reading above asks `origin/main` explicitly.

---

## What landed

One key-level supersession term beside the symbol-level one, both directions out of one set
difference:

* `declared_key_delta()` → `KeyDelta(gained, dropped)`. `dict_key_gains` is now that delta's own
  field, not a second walk of the text, so the direction that refuses a refresh and the direction
  that names a loss cannot drift.
* `judge`'s **rule 2 key-level half** (`KEY_SUBSET`): drops declared keys the base binds, adds none,
  supplies no symbol, supplies no prose.
* `refresh_to_head`'s two `NOT_SUPERSEDED` sentences now name the dropped keys instead of asserting
  "it deletes no name".

No fourth clause was added. A string literal in a list, a decorator and an `__all__` entry remain
one population's business — widening is a change to `_dict_string_keys` alone — and that widening
was priced and refused below rather than left as an intention.

---

## The thing this turn got wrong first, recorded beside the answer

The obvious build — make `judge` return a loss for the key drop — **was written, ran green on the
commissioning file, and was wrong.** `refresh_to_head._judge_copy` turns *any* non-`None` loss into
`REFRESHABLE`, and `background.origin_reconcile` calls `refresh` on that grade **with no person in
the loop**. Measured on the live paths: two of them, including `annual_report.py`, flipped from
`refused_head_does_not_supersede_it` to `refreshable`.

And the copy is not a pure revert. It adds **six comment lines the base lacks**, explaining why
`covers_svt_route: false` is live. The honest-looking repair would have had a daemon discard that
writing on its first live application — the same class as the defect it was fixing, one population
to the right.

So the leg carries a prose guard, and the loss half of the direction is delivered in two places:

* `judge` refuses the copies that supply **nothing at all** — those are the ones the base genuinely
  supersedes, and `REFRESHABLE` is the correct grade for them;
* the door's refusal says what it read for everything else, which is where the commissioning file
  lands and which is what the item asked for: *"no sanctioned door clears it and none should be
  sought."*

Net door-grade change across the shared tree's 77 dirty `.py` paths: **zero paths loosened.**

---

## The measurements, against the predictions filed before them

| Question | Predicted | Measured | |
|---|---|---|---|
| Q1 — strict key subsets newly refused, last 200 commits | 1.5%–6%, under 40 | **0 of 362 pairs (0.0%)** | **REFUTED** — too high |
| Q2 — extra `REFRESHABLE` withdrawals if the population widens | 2–10 | **10** of 77 dirty paths | held, at the band's edge |
| Q3 — live copies dropping a key and gaining none | 2–15 | **4** | held |

**Q1's decision rule (≤5% → unconditional) fires, and the count is 0.** Every real commit that drops
a dict key also adds one, so a strict key subset is not a shape honest landings make — the leg is
unconditional, exactly as `SUBSET` is, and it costs the landing gate nothing.

**Q2's decision rule (widen only if ≤3 extra withdrawals) does not fire.** Ten is over the line, and
the copies the wider population newly catches are things like a test's expected-strings list
`['os', 'p', "pathlib.Path('x')"]` — not a whitelist. One extra loss verdict for ten extra refusals.
The narrow population is the measured answer and the number is now in the code beside it.

**Q3's four paths all supply prose,** so after the guard the `judge` leg fires on **none of them**.

---

## What is honestly still true: the `judge` leg is inert on today's tree

The `KEY_SUBSET` verdict fires **0 times** on the live shared tree and **0 times** across 200
commits. Everything biting today is the door's repaired sentence. That is said here rather than left
for a reader to infer from a green suite, because the flattering reading — "a new rule, therefore new
coverage" — is available and wrong.

It is **reachable**, not vacuous: a copy that drops a whitelist key and adds no symbol and no prose
is an ordinary shape, and `test_a_strict_declared_key_subset_is_a_loss_rule_2_cannot_see` constructs
one. Deleting the leg reds two controls. The equivalence is established, not assumed.

---

## Controls, each mutation-proven

`tests/tools/test_stale_copy_refusal.py` (5) and `tests/tools/test_refresh_to_head.py` (1). Eight
mutations were run and each killed its own control:

| Mutation | Result |
|---|---|
| delete the `KEY_SUBSET` leg | 2 failed |
| drop the prose guard | 1 failed |
| drop the symbol guard | 1 failed |
| unreadable key population falls through to `partial` | 1 failed |
| re-split `dict_key_gains` into a second walk | 1 failed |
| door stops naming the dropped keys | 1 failed |
| door prints the key clause unconditionally | 1 failed |
| the shared `_is_comment_line` floor replaced by a bare `startswith('#')` | 1 failed |

Two carry explicit anti-tautology arms asserting **`is None`** and a *different copy* rather than a
missing word — a leg keyed to a word from the positive case survives the unconditional mutation, and
both of these were built to fail it.

Suites: `tests/tools/test_stale_copy_refusal.py` + `tests/tools/test_refresh_to_head.py` **138
passed**; `tests/design/` + the static-quality ratchet **161 passed**; `ruff` clean;
`finding_classes --check` PASS.

---

## What is left

The pre-existing hole this turn did **not** widen and did not close: a strict *symbol* subset copy
that adds a comment block is still graded `REFRESHABLE` today, and `origin_reconcile` still acts on
it. The key-level leg is guarded against it; rule 2 is not. That is a separate item and is named
here so it is not rediscovered as new.
