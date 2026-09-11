**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Convergence moved the code to one place. It did not move the proof.

**Result document. The pre-registration is
`docs/staging/SEAT_PREREG_WHICH_CALLERS_PROVE_THE_CONVERGED_LOW_WATER_CONTRACTS_2026-09-05.md`,
written before the run, and it is kept unrevised beside this — four of its seven predictions were
wrong and the scoring is below.**

## The drawn premise was spent, and this says so

Lane-0 claim `register-low-water-three-implementations-one-mechanism` asked for
`removed_dispositions` and `removed_claims` to be re-pointed at `register_low_water.removed_rows`.
**Both were already re-pointed before this turn began** — the census in `fc950dda6`, the canon in
`029c21452`, each landed after the item was written. Verified by reading the function bodies rather
than the docstrings that assert it. Four call sites, one implementation, no surviving hand-rolled
copy of the three repairs. The item as written had nothing left to do.

## So the hazard was re-measured instead, and it had not gone with the premise

`register_low_water.py` records that mutating `keys_at_head`'s never-empty contract **survived all
four suites** while the canon held its own copy. Convergence fixed that one mutation. Nobody asked
the same question of the other contracts afterwards.

Seven mutations, each applied alone, each suite run **separately** so the answer is per-caller.
Every patch asserted its target string present exactly once before applying, and `__pycache__` was
cleared between runs — a survivor is otherwise indistinguishable from a patch that never applied,
which has happened here before. Baseline: 77 passed.

| # | Contract attacked | census | class | canon | map | shared (new) |
|---|---|---|---|---|---|---|
| M1 | git cannot run → empty baseline | survived | survived | survived | survived | **DIED** |
| M2 | register absent at HEAD → empty | survived | survived | DIED | survived | **DIED** |
| M3 | extractor raised → empty | survived | DIED | DIED | survived | **DIED** |
| M4 | extractor's own `None` discarded | survived | survived | DIED | survived | **DIED** |
| M5 | unestablishable baseline → clean | DIED | DIED | DIED | DIED | n/a |
| M6 | JSON `null` reason opens hatch | DIED | DIED | DIED | DIED | n/a |
| M7 | whitespace reason opens hatch | DIED | survived | DIED | survived | **DIED** |

### M1's contract is proved by nothing at all

`except (OSError, subprocess.SubprocessError): return None` → `return frozenset()` **survived every
one of the four suites.**

**Said precisely, because the imprecise version is worth less and I drafted it first.** The shipped
code is CORRECT — `keys_at_head` really does return `None` on a git that cannot run. Nothing is
mis-reporting today and no control has given a wrong verdict, which is why this is LATENT and not
BLOCKING. What the battery establishes is that **the contract is held in place by nothing**: any
edit that traded that `None` for an empty set would be caught by no test in any of the four suites.
The first draft of this document called M1 "a live fail-open", and that was an overstatement of a
real finding — the fail-open is one careless edit away, not present.

The branch is genuinely reachable, which is what makes the gap worth closing rather than
theoretical: `subprocess.run(["git", ...])` raises `FileNotFoundError` (an `OSError`) where git is
not on PATH, and `TimeoutExpired` (a `SubprocessError`) when the 30-second cap trips on a loaded
machine — this machine, under a full gate run. Were the contract ever broken, both would become
"HEAD's register was empty, so nothing can have been removed" and **all four registers would report
clean at once** — the exact fail-silent shape the module's header says it exists to refuse.

### M2 and M4 were load-bearing on a single caller's suite

Both died only in the canon's tests. A canon test edited in good faith would silently un-prove two
contracts *for four registers*, and every suite would stay green. That is the R15 catalogue shape —
a control that calls the shared helper survives mutation of the caller — displaced one level up:
after convergence the callers are fine, and it is the **proof** that is now concentrated in one
place while reading as though it were distributed.

**The general lesson, and it is why this is filed MATERIAL rather than as a tidy-up.** Converging N
implementations onto one is sold as making a repair reach every caller. It does. What it silently
does *not* do is converge the evidence: the shared code inherits whichever caller's tests happened
to be strongest, every other caller's suite goes on passing without proving anything about the
shared contract, and the tree now *looks* like one well-tested mechanism with four callers. **After
any convergence, ask which caller's suite each contract is standing on.** The answer here was "the
canon's" for two contracts and "nobody's" for one.

## The repair

`tests/background/test_the_shared_low_water_reader_refuses_rather_than_reading_empty.py` — 13
tests, proving M1/M2/M3/M4/M7 **on the shared reader, where the contract lives**. Confirmed by
re-running the battery: the new suite kills all five.

Deliberately **not** a per-caller routing test asserting "this rung calls `removed_rows`". Three of
those would be a control guarding a control, which this project's standing habit says is usually
not worth having. M5 and M6 got nothing new — they already die in all four caller suites, so they
are proved four times over and adding a fifth would be redundancy, not coverage.

Two legs exist purely to stop the file being vacuous: one asserts the reader **can** succeed
against a register really committed at HEAD (a reader that returned `None` unconditionally would
pass every refusal leg), and one asserts a real retirement reason still clears the hatch (a refusal
that can never be cleared is a wall, not a control).

## Scoring the pre-registration: 3 of 7, and the standing prediction held

- **M1 survives all four — RIGHT.** The one that mattered.
- **M2 dies in canon only — RIGHT.**
- **M3 dies in ≥2 suites — RIGHT** (class + canon).
- **M4 survives all four — WRONG.** Predicted the loudest finding of the run and it died in the
  canon. I read the class suite's extractor test as the only nearby coverage and never checked
  whether the canon drove the same leg from the reader's side; it does.
- **M5 survives the census suite — WRONG.** It died there.
- **M6 survives the census suite — WRONG.** It died there too.
- **M7 dies in canon only — WRONG**, it died in the census as well.

The three misses share one cause: I graded the census suite from what its test *names* suggested
rather than from what its bodies drive, and it is stronger than its names read. That is the
"a row graded from a sibling is a row nobody opened" shape, applied to my own reading of a test file.

- **Standing prediction — "at least one contract will prove to be held up by exactly one caller's
  suite" — CONFIRMED, twice** (M2 and M4, both canon-only), plus one held up by nobody (M1).

## What this does not claim

The mutations were run against the four low-water suites and the new one, not the whole tree.
Another suite elsewhere may incidentally kill M1; nothing found in `grep` suggests one, but "no
other suite covers this" is not established here and is not claimed. The repair stands either way,
since a contract proved incidentally somewhere else is the same fragility one file further away.
