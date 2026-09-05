**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: after the convergence, which caller actually proves each contract?

**Written BEFORE the measurement, and the answers are not known.** Filed by the delivery seat
under lane-0 claim `register-low-water-three-implementations-one-mechanism`.

## The premise this replaces is spent

The drawn item asked for `removed_dispositions` (`background/self_clearing_alarm_census.py`) and
`removed_claims` (`tools/canon_drift_check.py`) to be re-pointed at
`background/register_low_water.removed_rows`. **Both were already re-pointed before this turn
started** — the census in `fc950dda6`, the canon in `029c21452`, each landed after the item was
written. Verified by reading the function bodies, not the docstrings: all four call sites now pass
`register=`/`current=`/`baseline=`/`retired=`/`row_is=`/`retire_with=` into the shared
`removed_rows`, and the two that need a HEAD read go through the shared `keys_at_head`. No
hand-rolled copy of the three repairs (the `or ""` null treatment, the never-`frozenset()` refusal,
the no-subject-gone-exception argument) survives outside `register_low_water.py`.

So the *stated* work is done. What follows is the hazard the item was really about, which is not.

## Why the hazard is not automatically discharged with the premise

`register_low_water.py`'s own closing paragraph records a result worth taking seriously:

> Mutating `keys_at_head`'s `return None` to `return frozenset()` — the never-empty contract [...]
> **SURVIVED in all four suites** while the canon still had its own copy of the reader. The one
> test of that contract in the tree was pointed at the copy.

That is the R15 shape from the catalogue: *a control that calls the shared helper survives mutation
of the caller* — and its inverse, *converging hand-rolled copies can reveal the shared code's
contract was proved only via one copy.* Convergence moved the proof onto the shared reader for that
one mutation. **Nobody has asked the same question of the other contracts, or of the other three
callers, since convergence landed.** A shared implementation with one caller's tests behind it is
not four callers proved; it is one caller proved and three riding on it, and the next lane to touch
`removed_rows` will be told by a green suite that all four registers are covered.

The measurement is therefore not "does the mutation die" but **"which suites does it die in"** — a
contract that dies in exactly one suite names three registers whose rung is unproved.

## What is being run

Baseline, established before any mutation: the four suites
(`tests/background/test_the_register_can_lose_a_row_and_take_the_alarm_with_it.py`,
`tests/background/test_the_class_register_can_lose_a_row_and_take_the_alarm_with_it.py`,
`tests/tools/test_the_canon_register_can_lose_a_claim_and_take_the_drift_with_it.py`,
`tests/tools/test_the_map_can_lose_an_atom_and_take_the_queue_with_it.py`) — **77 passed**.

Seven mutations to `background/register_low_water.py`, each applied alone, each suite run
separately so the answer is per-caller and not a single pass/fail:

| # | Mutation | What contract it attacks |
|---|---|---|
| M1 | `except (OSError, SubprocessError): return None` → `return frozenset()` | git unavailable reads as an empty register |
| M2 | `if proc.returncode != 0: return None` → `return frozenset()` | register absent at HEAD reads as empty |
| M3 | `except Exception: return None` (extractor raised) → `return frozenset()` | unparseable baseline reads as empty |
| M4 | `if keys is None: return None` → `return frozenset()` | extractor's own "unusable" verdict discarded |
| M5 | `if baseline is None: return [refusal]` → `return []` | unestablishable baseline reads as clean |
| M6 | `str(ret.get(key) or "")` → `str(ret.get(key, ""))` | explicit JSON/YAML `null` opens the hatch |
| M7 | drop `.strip()` from the reason check | whitespace-only reason opens the hatch |

Each patch **asserts its target string is present exactly once before applying**, and
`__pycache__` is cleared between runs — a surviving mutation is otherwise indistinguishable from a
patch that never applied or a stale `.pyc`, and both have happened here.

## Predictions, recorded before the run

- **M3 dies in ≥2 suites.** Both the canon suite (`test_THE_HEAD_READER_ITSELF_returns_None_and
  _never_an_empty_set`) and the class suite (`test_keys_at_head_returns_none_when_the_extractor
  _raises`) appear to assert it directly. This is the contract the convergence write-up says it
  rescued, so if it does *not* now die, the write-up's central claim is wrong.
- **M5 dies in 3 suites** (class, canon, map — each has a named unestablishable-baseline test).
  **Predicted to SURVIVE the census suite**, which shows no such test.
- **M6 dies in 3 suites** (class, canon, map each parametrize a `None` reason). **Predicted to
  SURVIVE the census suite.**
- **M4 SURVIVES all four.** This is the prediction I most expect to be interesting: the class suite
  tests the *extractor* returning `None` directly, which is a different subject from `keys_at_head`
  discarding that verdict. If it survives, the caller-side contract is unproved everywhere.
- **M1 SURVIVES all four.** Nothing visible injects an `OSError` into `subprocess.run`.
- **M2 dies in the canon suite only.** Only the canon patches `subprocess.run`.
- **M7 dies in the canon suite only**, and only if its parametrized reasons include whitespace.

**Standing prediction over the whole battery:** at least one contract of the shared mechanism will
prove to be held up by exactly one caller's suite. If every mutation dies in every suite, the
convergence is better than claimed and this document says so beside the prediction.

## What is NOT being proposed here

Not a routing test per caller asserting "this rung calls `removed_rows`". Three of the four would
be a control guarding a control, which this project's own standing habit says is usually not worth
having. The repair, if the measurement finds a gap, is to put the missing contract test **where the
contract lives** — on the shared reader — and to leave the callers alone.
