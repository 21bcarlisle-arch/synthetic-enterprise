**Severity:** RECORDED · **Lane:** 0 delivery · **Direction item:** `rankq-below-is-split-into-ranking-and-volume-from-its-own-records` · **Triage:** `retention-money-goes-to-debtors-priced-as-payers`

# Pre-registration: is rankq's −£2.45 a matter of worse households or fewer households? Read from the records it already wrote

Written 24 Nov, before any outcome below was opened. It runs nothing new.

**The question.** Rankq graded BELOW the twin: −£2.454 (−£4.762 to −£0.474) per household-year (s.12g, `5cf54da43`).
It offered 0.109 of its asks; the twin offered 0.277. So the run cannot yet say whether A's rank is
**worse** (it picks the wrong households) or the loss comes from **fewer** offers. The director's open row asks
whether to spend about 11 h on a volume-matched rerun to separate the two.

**Premise check.** `5cf54da43` is on origin. The grade is not re-done here.

**Q0, what the records carry (checked for coverage only; no outcome was read).** A's rank *is* logged for the
twin's asks. Rankq's `rank_gate_log` holds the belief and the gate at each of its 754 value-arm asks. Joining
them on (account, term_start, fuel) covers **751 of the twin's 777** asked renewals (373/388 and 378/389 by seed).
The other 26 have no rankq ask and are counted, not imputed.

**The reader.** `/var/tmp/vtn-driver/s12g-reader/read_rankq_split.py`, sha256 `2229a88bdffc7352…`. It uses
grade_rankq's unit (household), divisor (the twin's control-arm household-years), and resampling
(2,000 households, seed 20261117). TOP means a household with at least one twin ask where A's belief was at or above
rankq's gate at that ask. A None gate is the standing 0.30. REST means every other asked household.

**What "value" is here, and where it falls short.** It is the twin's own value arm minus its flat book, per
household. That is realised money under the twin's offers. It is not a counterfactual value of offering, because
TOP and REST were offered by the twin's rule and not at random. It also nets every renewal-margin effect on the
household, not the offer alone.

**Measures, predictions and rules.**

| | Measure | Predicted | Rule |
|---|---|---|---|
| **M1** | Within the twin, advantage per twin ask, TOP − REST (£) | +£10 (−£60 to +£80) | Lower bound > 0: **A's rank concentrates value**, so rankq's loss is volume. Upper bound < 0: **A ranks worse than its complement**, so the loss is ranking. Otherwise **cannot tell from ranking**. |
| M1b | The same, per twin-offered household | straddles zero | As M1. Context only. |
| **M2** | rankq − twin, split by offer class (BOTH / TWIN_ONLY / RANKQ_ONLY / NEITHER), £/hh-yr | TWIN_ONLY carries over half: −£1.60 (−£3.20 to −£0.20) | If TWIN_ONLY's interval is below zero and it carries ≥ 50% of the whole: **fewer** is where the money went. |
| D | Debtor share among offered households, rankq vs twin. A debtor is a household with a write-off or stayer provision in that run's value arm, or a negative flat-book net. | rankq higher than twin | Higher: the triage row's mechanism is live under the rank gate. Not higher: it is not shown here. |
| D2 | Debtors among rankq's 20 highest-belief offers | ≥ 6 of 20 | Read as stated. |

**Combined reading, fixed now.**
- M1 concentrates and M2 is TWIN_ONLY-led: **fewer, not worse.** A volume-matched rerun would only confirm this,
  so it is not needed for this question.
- M1 is "worse": **worse.** A volume-matched rerun would be expected to stay below.
- M1 is "cannot tell" and M2 is TWIN_ONLY-led: the money went with the dropped offers, but **the records cannot
  say whether A would have picked better at equal volume.** That is exactly what the rerun would separate.
- M2 not TWIN_ONLY-led: the loss sits on households both runs treated, or in the book's feedback (the control arm moved
  −£0.97). Neither reading is licensed, and that is said.

**What I already knew before writing this.** The grade output (`grade_rankq.out`), including the movers list.
Nothing split by TOP/REST or by offer class.
