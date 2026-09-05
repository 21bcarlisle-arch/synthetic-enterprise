# RESULT — the convergence proved a contract that had been proved NOWHERE

**Severity: INFO** — the result of the measurement pre-registered in
`SEAT_PREREGISTRATION_DOES_A_CONVERGED_LOW_WATER_RUNG_STILL_FIRE_FROM_THE_GENERIC_2026-09-05.md`,
filed beside it rather than over it.

Ran 2026-09-05, twice: once after the census leg was re-pointed and before the canon leg was, and
once after both. Running it at the halfway point was not planned and is where the finding came
from.

## The mutations, on `background/register_low_water.py` only

Each was applied to the **generic**, never to a call site: the question is whether a call site's
own tests still reach the mechanism. Each patch asserted its target string was present and unique
before applying, and `background/__pycache__` was cleared between runs — a mutation harness that
reports SURVIVED off a stale `.pyc`, or off a patch that never applied, is this project's named
way of buying a false clean sheet.

| mutation | census | class register | maturity map | canon |
|---|---|---|---|---|
| **M1** drop the `or ""` null treatment | 5 red / 3 red | 3 red / 3 red | 4 red / 4 red | **17 green** → **4 red** |
| **M2** unestablishable baseline reports clean | 1 red / 1 red | 2 red / 2 red | 1 red / 1 red | **17 green** → **1 red** |
| **M4** `keys_at_head` returns `frozenset()` on git failure | green / green | green / green | green / green | **17 green** → **1 red** |

*(cells read "before the canon leg / after it"; the census leg was already converged in both runs.)*

## The verdicts

**P1, P2, P3 — CONFIRMED.** Mutating the generic reds the census, the class register, the map and
the canon. All four call sites reach the shared code; none of them is a decorative wrapper whose
tests have quietly become assertions about `register_low_water`'s own fixtures.

**P4 — CONFIRMED, and it is the finding.** `keys_at_head`'s `return None` on a git failure is the
never-empty contract, and it is the leg that separates "HEAD's register was empty, so nothing can
have been removed" from "I cannot answer". **Before the canon leg was re-pointed, mutating it to
`return frozenset()` survived in ALL FOUR suites.** The only test of that contract in the tree —
`test_THE_HEAD_READER_ITSELF_returns_None_and_never_an_empty_set` — was pointed at
`canon_drift_check._claim_ids_at_head`, a hand-rolled copy. The generic's own reader, which the
census, the class register and the maturity map all depended on, was proved by nothing.

Re-pointing the canon did not merely remove a duplicate. It moved the one existing proof of that
contract onto the reader every register now shares.

**P5 — REFUTED, and the refutation is the honest reading rather than a defect.** P5 said a
mutation reding only ONE suite would mean a call site is not reaching the code I think it is. M4
reds only the canon. But M1 and M2 red all four through the same call path, so the wiring is
proved; what M4 measures is *test coverage of the reader's own contract*, which exists in exactly
one place because there is exactly one reader. The prediction conflated "shares the mechanism" with
"has its own copy of every test of it", and those came apart the moment the mechanism converged.

**Not refuted, and worth saying plainly:** no assertion was relaxed to make anything pass. The
refusal line now carries its register's name, because one line may come from any of four registers
and a line naming none is a line a reader cannot act on. The two `startswith("<key>")` assertions
that this broke were keyed to today's formatting; both were replaced with a **stronger** pair —
the register name AND the key — not dropped.

## What is now true of the mechanism

One implementation. `background/register_low_water.py` holds the `or ""`-before-`str` null-reason
treatment, the None-is-never-`frozenset()` refusal, and the no-subject-gone-exception argument, and
four registers call it:

| register | call site |
|---|---|
| `docs/design/self_clearing_alarm_dispositions.json` | `self_clearing_alarm_census.removed_dispositions` |
| `background/finding_classes.py` `CLASSES` | `finding_classes.removed_classes` |
| `docs/design/maturity_map.yaml` | `level_promotion_gate.low_water_failures` |
| `docs/design/canon_claims.yaml` | `canon_drift_check.removed_claims` |

`tools/domain_constant_origins` is deliberately **not** in this table and that is a finding, not an
omission: its subject set is derived by `scan()` over source, so "deleting a row" means deleting
the constant itself — an honest change, not the erasure of the record that a carrier existed.

## The premise leg that was SPENT

The drawn item's third piece — decide the retirement-reason home for `docs/design/maturity_map.yaml`
and wire its rung — was already done and on `origin/main` when the item was drawn: wired at
`level_promotion_gate.low_water_failures()`, reasons in `docs/design/maturity_map_retired.yaml`,
which is itself append-only and escapable only by the atom returning to the map. Re-measured and
recorded rather than done twice.

## What this leaves open

The census, the class register and the maturity-map suites have no leg of their own that drives the
shared reader on a real git failure, and after this convergence they do not need one — a fifth copy
of that test per register is the exact shape just removed. But the coverage now rests on a test
living in the CANON's file, which is a strange home for a contract belonging to
`register_low_water`. Moving it, or adding one leg beside the generic, is a small honest tidy that
nothing here depends on. Recorded so that whoever deletes the canon's copy knows what else goes
with it.
