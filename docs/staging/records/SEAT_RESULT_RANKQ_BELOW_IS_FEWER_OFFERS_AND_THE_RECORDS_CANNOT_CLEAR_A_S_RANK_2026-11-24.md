**Severity:** RECORDED · **Lane:** 0 delivery · **Direction item:** `rankq-below-is-split-into-ranking-and-volume-from-its-own-records` · **Triage:** `retention-money-goes-to-debtors-priced-as-payers`

# Result: rankq's −£2.45 sits on offers it dropped; the records cannot show A's rank picks better at equal volume, and lean against it

The pre-registration is `SEAT_PREREG_RANKQ_BELOW_SPLIT_INTO_RANKING_AND_VOLUME_FROM_ITS_OWN_RECORDS_2026-11-24.md`,
on origin as `1c3072781` before the reader was run. The reader is `/var/tmp/vtn-driver/s12g-reader/read_rankq_split.py`
(sha256 `2229a88bdffc7352…`, unchanged), and its output is `read_rankq_split.out` beside it. No run was launched.

## Pre-registered readings

| | Measure | Predicted | Read | Verdict |
|---|---|---|---|---|
| Q0 | Twin asks joined to A's logged rank | — | **751 of 777** (0.967) | A's rank is logged; the read can proceed |
| **M1** | Within the twin, advantage per twin ask, TOP − REST | +£10 (−£60 to +£80) | **+£31.4 (−£72.6 to +£135.4)**. TOP +£52.8 (171 hh-seeds), REST +£21.4 (293) | point in range; **cannot tell from ranking** |
| M1b | The same, per twin-offered household | straddles | **−£111.2 (−£446.6 to +£227.3)**. TOP +£45.1 (77), REST +£156.3 (112) | straddles, as predicted; point against A |
| **M2** | rankq − twin, by offer class, £/hh-yr | TWIN_ONLY −£1.60 (−£3.20 to −£0.20), ≥ 50% | **TWIN_ONLY −£2.659 (−£4.654 to −£0.930)**, 127 hh-seeds. BOTH +£0.499 (+£0.096 to +£1.008). RANKQ_ONLY −£0.239. NEITHER +£0.030. Sum −£2.369; −£0.085 falls outside the asked/offered households | point **beyond** its range (more loss than predicted); rule met: **fewer is where the money went** |
| D | Debtor share among offered households | rankq higher | **rankq 0.114** (79 households) vs **twin 0.180** (189). Asked: 0.147 vs 0.159 | **refuted**: the rank gate sends offers to debtors *less* often |
| D2 | Debtors in rankq's 20 highest-belief offers | ≥ 6 | **0 of 20** | **refuted** |

**The pre-registered combined reading.** M1 is "cannot tell" and M2 is TWIN_ONLY-led. The money went with the
dropped offers, but **the records cannot say whether A would have picked better at equal volume.** That is
what a volume-matched rerun would separate.

## Exploratory, not pre-registered (written after the above was read)

`read_rankq_split_explore.py` (sha256 `e455b5576d34…`), output `read_rankq_split_explore.out`.

- **Where TWIN_ONLY's loss sits.** On households A ranked **below** its bar: −£2.624 (−£4.584 to −£0.926), 112 hh-seeds.
  On those A passed but the value test declined: −£0.035 (−£0.324 to +£0.220), 15. So the loss is the bar, not the
  value test after it.
- **Would an equal-volume bar reach them?** A static stand-in for a volume-matched gate is the 1 − 215/777
  quantile of rankq's own asked beliefs, 0.476. Only **49 of the 112** clear it. They carry **£7,239** of the drop
  (about −£0.64/hh-yr). The other 63 carry **£22,661** (about −£1.99/hh-yr), and A ranks those below even an
  equal-volume bar. The twin made its money on them.

**What the exploratory read suggests, and how far it goes.** At equal volume, a rank gate would most likely still lose about
£2 per household-year on households A ranks low, unless the extra A-ranked households it adds earn that back. Their value under
an offer is unobserved: the twin did not offer most of them. Together with M1b's point, this **leans** toward "A's rank does
not know whom to retain". It does not establish it. The bar is static, not the rolling one, and the value of the added offers is unmeasured.

## What the volume-matched rerun would separate

One number: whether the offers a q = 0.277 rank gate adds to A's ranked households earn back about £2/hh-yr. That is
the £22.7k on households both gates skip. If the rerun goes ahead, its prediction should be about −£1.4
(−£3.5 to +£0.5) on rankq's measure, on this read. The director's row is unchanged.

## The triage row

`retention-money-goes-to-debtors-priced-as-payers` is not shown live under the rank gate. Rankq's offered debtor
share is lower than the twin's, and its top-belief offers are clean. The row's mechanism (the payment score raising a
debtor's churn belief) was not visible here at A's top. The row stays open: this read covers one book and the rank gate,
not the standing guard. Its owner is now this record.
