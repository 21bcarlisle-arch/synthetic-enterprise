# The Hour's record landed without its mechanism — and it is at least the third instance

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-11 · **Found by:** worker tick (H27_payment_belief_gap 2→3 HARDEN draw)
**Class:** a record can be committed ahead of the code it describes
**Status:** instance FIXED (commit `1e01735dc`, pushed in `2a0466aa0`); **class OPEN** — queued, not
fixed on sight (SELF_INTERRUPT_DISCIPLINE)

---

## What the tick drew, and what it actually found

The self-refill drew `H27_payment_belief_gap` for its 2→3 HARDEN, whose level-hold note ends:

> *"the reshape is atom `D32_the_latency_headline_cannot_attribute_its_two_knobs` at L0, and the
> next promoter runs Hour #15 on the corrected instrument"*

**Hour #15 could not be run on the corrected instrument, because the corrected instrument was not
at HEAD.** (observed-with-evidence)

At HEAD, before this tick:

| artefact | state at HEAD |
|---|---|
| `docs/staging/WORKER_FINDING_THE_CAVEAT_CARRIED_A_SUB_READINGS_RESOLUTION_2026-08-11.md` | **committed** (swept in `6202d3371`) |
| `D32_…` mint in `docs/design/maturity_map.yaml` | **committed** |
| `H27` level-hold note: *"#14 changed the instrument again"* | **committed** |
| `tools/couple_w2_11_d5.py` — `PUBLISHED_FIGURE_CAVEAT_CONTRACT`, the derived knob × dimension reach grid, `predict_published_latency_step_days`, the corrected latency caveat | **uncommitted** (+427 lines in the working tree) |
| `tests/tools/test_couple_w2_11_d5.py` — the R15-both-ways controls for all of the above | **uncommitted** (+242 lines) |
| `docs/design/simplifications/archive/H27_payment_belief_gap.003.yaml` (the rotation that carries Hour #8's record) | **untracked** |

So HEAD asserted, on four surfaces a promoter and the Proof door read, that a control existed
which HEAD did not contain. The 381 tests that certify it passed **only in the working tree** —
the local-green shape. Had the tree been cleaned or the box died, Hour #14's entire pass would
have been lost while its record survived saying it had happened.

Landed this tick, unchanged, after `tests/tools/test_couple_w2_11_d5.py: 381 passed in 389.19s`.

## It is not an instance — the same shape is live right now on another lane

`tools/scale_probe_10k.py`, `tests/tools/test_scale_probe_10k.py` and
`docs/design/SCALE_PROBE_10K.md` are **untracked in this same tree**, while `scale_probe_10k` is
referenced at HEAD by `docs/design/maturity_map.yaml`,
`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`,
`tests/design/test_maturity_map_facets.py` and four worker reports. (observed-with-evidence —
`git grep -l scale_probe_10k HEAD` against `git status --porcelain | grep '^??'`.) Not landed
here: it is another lane's build and may be mid-flight; auditing before pruning or adopting is the
owner's call, and this finding is the register of it, not the fix.

`docs/staging/WORKER_REPORT_THE_GATES_OWN_CONTROL_WAS_UNTRACKED_2026-08-10.md` is a prior instance
by name, and this atom's own `harden_note` (2026-08-08) records the mirror image — code committed,
map cell silent. **Three occurrences of one class ⇒ R3 (two-strike redesign): the answer is not a
fourth careful commit.**

## Why the existing machinery does not catch it

(inferred, not measured this tick — this is the lead, not a verdict)

* The pre-commit test gate maps **changed files → tests** and runs them against the **working
  tree**. An untracked file is not a changed file, and the tree it lints is the tree that contains
  it, so the gate is green in exactly the state that produces the defect.
* The publish gate's subject is HEAD, so it *could* see the absence — but only if something asked
  it whether the names a committed record cites resolve to committed code. Nothing does.
* The derived-artefact register (`WORKER_FINDING_A_DERIVED_ARTEFACT_CAN_BE_COMMITTED_AHEAD_OF_ITS_INPUT_2026-08-10`)
  is the same family one layer over: an output committed ahead of its input.

## The mechanism this class wants

A HEAD-side check with the register shape this repo already uses elsewhere: **a committed record
that names a code symbol owes that symbol at HEAD.** The keyset is derivable both ways — worker
findings / simplification records / map atoms on one side, `git ls-files` on the other — so an
undeclared cell RAISES rather than passing, and it must be vacuity-guarded (a checker that finds
no citations at all certifies everything). R15 both ways: it must fire on this tick's actual
pre-state (`PUBLISHED_FIGURE_CAVEAT_CONTRACT` cited, absent at HEAD) and on the live
`scale_probe_10k` case, and must NOT fire on a record citing a symbol it deliberately proposes but
has not built (an L0 mint) — that discrimination is the hard part and is where the atom's design
work is.

## What is NOT claimed

No published number moved; nothing was tuned (R12). Whether Hour #14's controls are *correct* is
not re-litigated here — this finding is only that they were not at HEAD. Hour #15 remains un-run,
and now genuinely can be: the instrument at HEAD is the corrected one.
