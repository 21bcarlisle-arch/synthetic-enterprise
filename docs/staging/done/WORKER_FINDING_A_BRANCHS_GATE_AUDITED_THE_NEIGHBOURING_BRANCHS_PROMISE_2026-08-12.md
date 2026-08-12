# WORKER FINDING — a branch's gate audited the neighbouring branch's promise

**Severity:** BLOCKING · **Lane:** H_harness

**Atom:** `H_GAP_fabric_belief_truth_gap` (L2→L3 draw, worker tick)
**Date:** 2026-08-12 — the ELEVENTH Expert Hour on this atom
**Outcome:** IT FOUND SOMETHING, SO THE LEVEL STAYS 2.
**Subject:** `background/fabric_gap_ledger.py::panel_mirror_register_channel`

Every figure below came out of the running code on this atom's own published
population. Sixteenth time this atom surfaced something by running a thing rather
than reading it.

---

## 1. The directed question, and its refutation

The tenth Hour left this: *the register channel's own evidence count has never been
asked for; its fallback branch is still a panel mean against `MIRROR_FIDELITY_BAND`
with no interval and no statement of how many premises carry it, and the ninth Hour's
own subpanel measurement of it was taken on a branch neither published population
enters.*

**The tenth Hour's class does not reach this term** (`observed`, by measurement). That
class was *a guard sized on the panel cannot protect a statistic carried by a subset
of it*. This statistic is a size-biased mean to which every premise with a nonzero
error contributes:

| reading | value |
|---|---|
| Kish effective sample size, drawn 200 forced onto the branch | **89.8 of 200** |
| largest single premise weight | **3.1%** |
| real fallback subpanels (n=20/30/50/100) where the published count disagreed with the gate | **0 of 600** |

Copying the tenth Hour's resample mechanism onto this channel would have been cargo.

**The premise about the published populations is confirmed** (`observed`): both rows
carry `panel_mirror_reflection: level_preserving`, so the fallback branch never runs
on anything this atom publishes.

---

## 2. The defect

`_reflect` is `through**2 / value`, and its own docstring says what that buys —
**"same RATIO error, opposite sign"**. That is an EXACT, UNIVERSAL, PER-PREMISE claim,
and nothing has ever audited it.

The ninth Hour asked whether the fallback branch could take a worst-case shape,
measured the **absolute** error's worst breach there, correctly found it always-red
(every premise's absolute error moves on that branch by construction), and kept a
mean. Both horns of that dilemma are **the level branch's promise asked on the log
branch**. The refusal sentence that Hour wrote even names the right promise — *"this
reflection preserves the RATIO error"* — one line from the gate that never read it.

### What the mean actually is, as an identity

Under a correct log reflection each premise's absolute error moves by exactly
`e**2 / actual`, so every per-premise breach equals `e / actual` — **the register's own
relative error at that home** — and the gate's reading is a size-biased mean of those.
Checked against the running code on the drawn 200 (`observed`):

- per-premise agreement to **9.9e-15**
- **the whole gate reading reproduced from the UNMIRRORED panel alone, to 1.3e-16 relative**

A fidelity term computable with no mirror in the loop is reading the **stock**, not the
instrument. R15 TAUTOLOGY; the third Hour's all-denominator note in a new place.

---

## 3. The cost, both directions

**SATURATED where it runs.** Drawn 200 forced onto the fallback branch:

| reflection | gate reading | verdict |
|---|---|---|
| correct | 0.8423 | `unattributable` |
| wrong pivot | 0.8398 | `unattributable` |
| partial fallback | 0.5804 | `unattributable` |

The control returns the same verdict with and without its own named defects — and the
wrong pivot reads *lower* than the faithful mirror.

**FAIL-OPEN where it can pass.** On the suite's own `epc_bias=0.99` panel — the only
stock accurate enough for the mean to certify at all, and the not-always-red
demonstration the ninth Hour rested on — a **partial fallback**, the two-instrument
confound the whole-panel rule exists to forbid:

| reflection | gate reading | verdict |
|---|---|---|
| faithful mirror | 0.0306 | `attributable` |
| **partial fallback** | **0.0283** | **`attributable`** |

**It passed by being more wrong.**

---

## 4. Mechanised

- `_register_ratio_breaches` — per premise, never averaged; order/length/empty guarded;
  fail-closed to `inf` where the ratio cannot be formed.
- `panel_mirror_register_ratio_worst_breach`, `panel_mirror_register_ratio_breaching_premises`.
- `panel_mirror_register_refusal` **in three states** — `""` / `"fault"` / `"blunt"`,
  worst-first. Two subjects opposite in polarity were riding on one word (the sixth
  Hour's `MIRROR_FIDELITY_BAND` class one level down; the eighth Hour's three-state
  repair applied to the other channel). A reader acts differently on *fix the mirror*
  and *this stock is too coarse for it*.
- **The constant is untouched and reused deliberately.** `REGISTER_PRESERVATION_TOLERANCE`
  is a float-noise floor for an exact per-premise preservation promise — the same
  SUBJECT the level branch gives it — so this is **not** the sixth Hour's
  one-constant-two-subjects class (R12/R13: the statistic was wrong, not the threshold).
- **The bluntness test is kept exactly as it was.** An instrument whose by-design
  disturbance swamps the band still cannot attribute a null — the second Hour's MIRROR
  INCONCLUSIVE fires unchanged. Both refusal sentences now say which of the two they are.
- **The Hour's own output audited by the Hour's own finding:** the two ratio fields are
  published ONLY on the branch that makes the promise. The level reflection moves the
  ratio by construction (200 of 200 premises, worst breach 1.91 on this atom's own
  row), and a reader seeing "200 premises breached" beside an EMPTY refusal field would
  be reading a fault count that decided nothing.

Adding a second refusal test can only TAKE certification away. Every existing refusal
survives: **259 passed / 2 xfailed, up from 252, with no test rewritten and none deleted.**

---

## 5. R15 — eight source mutations, each firing its own named test

md5 byte-clean restore `196ff087a5d214eaa548809420ee9238`; 9 green unmutated.

1. gate reads the mean again (the exact defect)
2. fault test widened to the fidelity band
3. ratio breach computed as a DIFFERENCE instead of the product-held-at-1
4. branch keying removed, so the ratio is audited on the level branch too
5. an unreadable ratio fails OPEN to 0.0
6. the premise-order guard removed
7. the blunt sentence keyed back to the retired wording
8. the fault COUNT keyed to the band, not the tolerance

**Not always-red, searched not assumed:** on a register 17% out — where the absolute
worst-case shape the ninth Hour rejected *is* fatal — the ratio promise is kept to
**2.220e-16** and the refusal reads `blunt`. The fault test passes exactly where the
rejected shape would have refused an instrument behaving as designed.

**One guard is unreachable and the test says so** rather than dressing it up:
`FabricObservation.__post_init__` already refuses non-positive/non-finite HLCs, so the
fail-closed corner is defence in depth and is entered only via a stand-in.

---

## 6. No published figure moved — checked, not asserted

Both rows re-taken on their own declared population (`--seed 17 --unit-rate 7.4
--population 200 --population-seed 17`) AFTER the code landed:

- gap **0.4269 / 0.4042** — unchanged
- register channel `attributable`, refusal `""` — before and after
- `panel_mirror_is_attributable` **False**, attribution `unresolved` — before and after;
  the money channel is still what refuses them

Every leaf of the ledger diffed: **10 changed** — `measured_at`, `run_git_commit` and the
three new fields on each of the two rows, and nothing else.

Suites: 259 passed / 2 xfailed in the atom's own file; 79 across its three siblings;
`epistemic_verifier` **PASS**, 555 files.

---

## 7. R10 classes

**A BRANCH'S GATE MUST AUDIT THE PROMISE THAT BRANCH MAKES.** Auditing a neighbouring
branch's promise produces a control that is SATURATED where the promise holds and
FAIL-OPEN where it does not. **Signature:** its reading is a closed-form function of the
population rather than of the instrument. Sibling of the ninth Hour's
SENSITIVITY-FALLS-WITH-N and the tenth's GUARD'S-SUBJECT-GROWS-WITH-N, and the first
about the **unit** a control is denominated in rather than its shape.

**A dilemma between two bad shapes is evidence the quantity is wrong**, not that the
better shape must be sacrificed.

---

## 8. Opener for the twelfth Hour

`panel_mirror_register_infidelity` is now known to be a reading of the **stock's**
register accuracy, and is still published under a name that says fidelity, on both
branches, and is still the bluntness gate's statistic. The band it is compared to (5%)
was calibrated when it was believed to be an instrument artefact, and nobody has
re-asked what the right threshold is for *"this stock is too coarse to attribute a null"*.

**Also named:** this atom publishes FOUR retained-but-superseded fidelity statistics
whose only defence against being misread is their docstrings — unchanged this Hour.

---

## 9. Landed WITHOUT the ledger file, and why (2026-08-12)

`docs/observability/coupled_gap_ledger.json` was re-taken and every leaf diffed (§6),
but it is **not** in this commit. While this Hour ran, a concurrent lane's live writer
re-stamped the **W2_11** row in the same file (`measured_at` 05:22:48 against this
run's 05:19:46; `unpursued_counts.actual.n_ever_detected` 31 → 4). A pathspec cannot
split one file, so committing it would have swept another lane's uncommitted half-write
into this commit.

`site/proof/test_coupled_gaps_panel.py::test_R15_the_control_fires_on_the_pre_repair_depth_limit`
caught it and refused the commit — correctly. Its census read **54** against a recorded
53. Attributed by measurement, not assumed:

| payload | census | breakdown |
|---|---|---|
| working tree as-is | 54 | W1_11 **22**, W1_12 **22**, W2_11 **10** |
| W2_11 components reverted to HEAD | **53** | W1_11 **22**, W1_12 **22**, W2_11 **9** |

**This Hour's change contributes zero numbers to that census** — which is exactly what
publishing the two ratio fields only on the branch that makes the promise (§4) bought.
The 54th figure is entirely the W2_11 re-stamp.

**FOR THE W2_11 LANE, NOT ACTIONED HERE:** that test says a change in its count "is a
real movement to re-read, not a number to update". The movement is real and belongs to
whoever owns the W2_11 live writer — `n_ever_detected` falling 31 → 4 is a population
change in that row, and its ageing/arrears rates moved with it. Registered as a finding
for that lane rather than absorbed or silenced here.
