# WORKER FINDING — the gate was the branch's own admission ticket, read back to it

**Severity:** BLOCKING · **Lane:** H_harness

**Atom:** `H_GAP_fabric_belief_truth_gap` (L2→L3 draw, worker tick)
**Date:** 2026-08-12 — the TWELFTH Expert Hour on this atom
**Outcome:** IT FOUND SOMETHING, SO THE LEVEL STAYS 2.
**Subject:** `background/fabric_gap_ledger.py::panel_mirror_register_refusal`,
`panel_mirror_register_channel`

Every figure below came out of the running code. Seventeenth time this atom surfaced
something by running a thing rather than reading it.

---

**Discharged:** `tests/harness/test_premise_two_level.py::test_the_FALLBACK_BRANCHS_ABSOLUTE_SHAPE_IS_ALWAYS_RED_and_the_MEAN_NO_LONGER_GATES`, `tests/harness/test_premise_two_level.py::test_the_STOCK_COARSENESS_DISCLOSURE_PRINTS_ON_A_ROW_THE_MIRROR_CERTIFIED`, `tests/harness/test_premise_two_level.py::test_BLUNTNESS_IS_PUBLISHED_ONLY_ON_THE_BRANCH_THAT_PRODUCES_IT` — the entry condition no longer doubles as the gate, the disclosure prints on rows the mirror certified, and it is published only on the branch that produces it. 8 green, 2026-08-12.

## 1. The directed question

The eleventh Hour left this: *`panel_mirror_register_infidelity` is now known to be a
reading of the STOCK's register accuracy, is still published under a name that says
fidelity, and is still the bluntness gate's statistic; the band it is compared to (5%)
was calibrated when it was believed to be an instrument artefact, and nobody has
re-asked what the right threshold is for "this stock is too coarse to attribute a
null".*

**The band is not the defect and no threshold would have fixed it** (`observed`). The
statistic cannot gate at all, for a reason that is in the branch's ENTRY CONDITION
rather than in any panel it happens to run on.

---

## 2. The defect

`_level_reflection_is_feasible` fails exactly when `2*epc <= actual` — i.e. when that
home's relative register error is **at least 0.5**. So:

**The fallback branch only ever runs on a panel containing a home ten times the band
its gate compares a mean to, and no panel on this branch can be free of one.**

And the eleventh Hour's identity says what that mean is: `Σ e_i·r_i / Σ e_i` where
`r_i = e_i/actual_i`. It is a mean of relative errors **weighted by absolute error** —
so the home whose extreme error opened the branch is inside it, and cannot be outside
it, and enters it with a weight nobody chose.

### What that weight actually does, measured

The SAME rogue home, 60% out in every panel below (one certificate lodged for another
dwelling), ten homes each:

| the neighbours | rogue's weight in the gate | gate reads |
|---|---|---|
| certified to 0.1% | **95.0%** | 0.5701 |
| certified to 1% | 65.6% | 0.3969 |
| 10% out | 16.0% | 0.1800 |
| 20% out | **8.7%** | 0.2348 |

At the coarsest stock it is **not even the heaviest home**: a larger house that is
*less wrong* carries more of the reading than the one that is 60% out. The reading is
neither the worst home nor the typical one — it is how wrong the home you would land
on is, if you sampled homes in proportion to their error.

### And it moves with the panel, not with the stock

Same composition rule, one rogue plus neighbours certified to 0.1%, varying only n:

| n | gate | median home's error | verdict |
|---|---|---|---|
| 10 | 0.5701 | 0.0010 | refused |
| 40 | 0.3503 | 0.0010 | refused |
| 100 | 0.1142 | 0.0010 | refused |
| 200 | **0.0344** | 0.0010 | **passed** |

The stock's median home is 0.1% out at every one of them. What changed is how many
well-surveyed neighbours the rogue happens to have.

---

## 3. The cost

Twelve stocks on this branch, a register 30% under to 30% over, one rogue certificate
each. On **all twelve** the branch's own promise is kept to float noise
(worst ratio breach 1.1e-16 to 2.2e-16 — the instrument is doing exactly what it says).
On **all twelve** the retired rule refused.

Underneath it, the MONEY channel — the one denominated in the unit the verdict is
published in, with its own band and its own interval — had already resolved
`attributable` on **five of them with an artefact share of exactly 0.0000**. Those five
were being refused, in kW/K, on a reading of how far out the stock's register already
was.

**This is the third Hour's law read in the other direction.** That Hour established
that a term denominated in kW/K cannot CERTIFY a verdict denominated in GBP and built
`panel_mirror_weight_artefact` to do it properly. It cannot REFUSE one either. The
repair was applied to one polarity and not the other.

---

## 4. Mechanised

- `panel_mirror_register_refusal` is now `""` or `"fault"` and nothing else. On both
  branches it says one thing in one unit: the instrument did, or did not, do what it
  says it does (level branch — absolute error back unchanged, worst breach; fallback —
  ratio error exactly inverted, worst breach; both against the float-noise floor).
- `panel_mirror_register_bluntness` (`""` / `"blunt"`) carries the reading that used to
  refuse. **Published on the fallback branch only**, `None` on the branch that does not
  produce it — the eleventh Hour's own discipline applied to this Hour's output.
- `_bluntness_caveat` — the sentence moved OUT of `_why_unattributable`, which is where
  it could only ever be read by someone already being told the mirror had failed (the
  second Hour's own finding about COMPOSITION-DECIDED, one level down and in this
  atom's machinery). It now prints on rows the mirror CERTIFIED — the state it could
  never previously reach — says **"disclosure, not a refusal"** in its own first
  clause, and keeps the raw MAE pair the old sentence carried, because a share whose
  numbers are not printed is not auditable.
- **The band and the constants are untouched.** `MIRROR_FIDELITY_BAND` still decides
  what the row SAYS about the stock (R12 diagnostic); nothing was re-calibrated,
  because re-calibrating a statistic that answers the wrong question is the shape this
  Hour is about.
- **The fault test is untouched and still refuses.** Breaking the reflection LOWERS the
  retired reading (a partial fallback leaves homes level-reflected, whose absolute
  error does not move) and RAISES the ratio breach — pinned as a test, because a gate
  that reads better the more broken its instrument gets is what the eleventh Hour
  caught this one doing.

### This Hour GRANTS certification, and that is named rather than glossed

Every Hour before this one could only take certification away. Of the twelve stocks,
five are now certified and they are exactly the five the money channel had already
resolved at 0.0000; the other seven are still refused **in GBP** — four `unresolved`,
three `unattributable`. The channel can still say either word.

**Five tests were rewritten and none deleted**, which is a departure from the previous
Hours' record and is the honest consequence of a gate legitimately changing: three
asserted `blunt → unattributable` directly, and two pinned a controlled comparison on
a mirror that was "unfaithful" only in the blunt sense. Both of the latter now pin it
on a mirror that is genuinely BROKEN, injected at the reflection call — a stronger
control than they were, not a weaker one.

---

## 5. R15 — eight source mutations, each firing its own named test

md5 byte-clean restore `ce4df81304cf77627b5fe6374ba4ca69`.

1. the gate reads bluntness again (the exact defect)
2. the fault test stops gating on the fallback branch
3. the disclosure is dropped
4. bluntness keyed to the float-noise floor instead of the band
5. bluntness published on the branch that does not produce it
6. the disclosure drops the raw MAE pair it is a share of
7. the disclosure loses its not-a-refusal marker
8. bluntness can never fire

**Not always-on, searched not assumed:** an 80-home panel whose register is accurate to
1% with one rogue certificate discloses nothing (`bluntness == ""`), so the disclosure
fires on some fallback panels and not others.

---

## 6. No published figure moved — checked, not asserted

Both rows re-taken on their declared population (`--seed 17 --unit-rate 7.4
--population 200 --population-seed 17`) AFTER the code landed, and every leaf diffed:

- gap **0.4269 / 0.4042** — unchanged
- register channel `attributable`, refusal `""`, `panel_mirror_is_attributable`
  **False**, attribution `unresolved` — all unchanged; the money channel is still what
  refuses them
- whole-ledger diff: **two added keys** (`panel_mirror_register_bluntness`, `None` on
  both rows — neither published population takes the fallback branch) plus
  `measured_at` and `run_git_commit`. Nothing else.

Suites: **265 passed / 2 xfailed** in the atom's own file (was 259); 79 across its three
siblings; 15 in `site/proof/test_coupled_gaps_panel.py`; `epistemic_verifier` **PASS**,
555 files.

---

## 7. R10 classes

**A GATE MAY NOT BE COMPUTED FROM ITS OWN BRANCH'S ENTRY CONDITION.** Where the
condition that selects a branch also determines the statistic that branch is judged by,
the control is not measuring anything it can vary — the population it is allowed to see
has been filtered on the quantity it reads. **Signature:** the reading has a floor (or
ceiling) set by the selection rule, and moves with the size of the panel around it
rather than with the property it names. Fourth in this atom's run of denominator/unit
classes, after SENSITIVITY-FALLS-WITH-N (ninth), GUARD'S-SUBJECT-GROWS-WITH-N (tenth)
and A-BRANCH'S-GATE-MUST-AUDIT-ITS-OWN-PROMISE (eleventh).

**A REPAIR MADE IN ONE POLARITY IS NOT MADE.** The third Hour's law — a term in one
unit cannot certify a verdict in another — was applied to CERTIFY and left standing in
REFUSE for nine Hours. When a rule is established about what a control may conclude,
it has to be re-asked of the opposite conclusion in the same pass.

---

## 8. Opener for the thirteenth Hour

The register channel now has exactly one gate on each branch and both are worst-breach
tests against `REGISTER_PRESERVATION_TOLERANCE`. **Nothing has ever asked what happens
when the two branches disagree about the same panel** — a panel where the level
reflection is feasible for 199 of 200 premises falls WHOLLY to the log form on the
strength of one home, and the instrument the other 199 are judged by changes because of
a home that is not them. The whole-panel rule is defended as forbidding a two-instrument
confound; nobody has measured what the one-home switch costs.

**Also named, and unchanged again this Hour:** this atom publishes FOUR retained-but-
superseded fidelity statistics whose only defence against being misread is their
docstrings.

---

## 9. The ledger lands this time, and the eleventh Hour's lands with it

The eleventh Hour deliberately left `docs/observability/coupled_gap_ledger.json` out of
its commit: a concurrent lane's live writer had re-stamped the W2_11 row mid-Hour with
a real figure movement (`unpursued_counts.actual.n_ever_detected` 31 → 4) and a pathspec
cannot split one file.

**Re-checked against HEAD rather than assumed** (`observed`): that movement is no longer
in the tree — every W2_11 leaf now equals its committed value except `measured_at` and
`run_git_commit`, which are a re-stamp carrying no figure. So the file commits here, and
it carries the eleventh Hour's two ratio fields (`None` on both level-branch rows) as
well as this Hour's one, since that Hour's ledger never landed.

The site-lane depth-limit census that refused the eleventh Hour's commit
(`site/proof/test_coupled_gaps_panel.py`) passes on this payload: 15 passed.
