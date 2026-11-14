# C32's sixth Expert Hour: the widened Safety Net was still a list, and a list breaches a welfare test

**Fate (2026-11-14):** RESULT. **C32 stays at level 2.** The pass failed on items 1 to 3. All
three are fixed in this tick, with commons §4 amended first.

**Blocker:** a seventh blind pass is owed, on one rule only: "any vulnerability evidence held
reads cannot determine". I chose that rule and graded it in the same tick.

**Why this was drawn and not skipped.** The draw asked for the fifth pass, and that pass was
already spent (ledger 22:30Z, fix a333b8d772, recorded spent in d3d4476b7d). The sixth pass is
the blocker the map named, and it was owed by an instance that did not write the fifth pass's
fix. This one did not.

## The pass

- **Reviewer:** a fresh agent with no tools, as a veteran of PSR and debt-and-disconnection
  operations.
- **What it was shown:** the fifth pass's plain words, with the net paragraph rewritten to
  describe the six categories, the stated over- and under-protection, and the S5 and SLC 0 gaps.
- **Ledger:** C32 row recorded 2026-11-14T23:30Z in `docs/observability/blind_review_ledger.jsonl`.
  It has 16 questions, 10 of them disqualifying. `--audit` reports the blindfold intact on all 17
  rows.

**The reviewer's first doubt was the finding.** Its words: a supplier that names an S5 gap and
still disconnects on it "has, in effect, written down a Safety Net breach in advance".

## Measured before the fix (15 Jul 2024, `can_disconnect`)

**Permitted with vulnerability evidence held:**
- codes 8 and 9 (blind or partially sighted), 35 (hearing), 17 (language) and 32 (temporary
  life change);
- every uncategorised code: 19, 27, 28, 31, 33, 34, 36 and 37, including post-hospital
  recovery;
- the flags `fuel_poverty`, `bereavement`, `job_loss`, `language_barrier`,
  `payment_difficulty` and `ppm_self_disconnected`.

The two partition controls held language, job loss and bereavement on the **permitted** side.
That is a control keyed to the answer of the day, which in this case was the defect.

## The fix

**The rule.** The company holds no welfare assessment. So any registration or flag reads
CANNOT_DETERMINE, in every month, and that blocks disconnection.

**What changed in the code:**
- `safety_net_protection`: a category outside the six now reads CANNOT_DETERMINE.
- New `safety_net_on_record`: catches evidence that never reaches a category, namely
  uncategorised codes and operational flags. `can_disconnect(record=)` now routes through it.
- The six net categories stay PROHIBITED. A future welfare assessment may clear
  CANNOT_DETERMINE and never PROHIBITED.

**After the fix:**
- In July and January, every code on the published list, every category and every flag is
  refused.
- A household with no evidence is permitted, with or without a 1985 birth date. A 1944 birth
  date is refused.

**New control:** `test_any_vulnerability_evidence_held_blocks_a_summer_disconnection`. It
partitions the whole space: the full published code list, all 10 categories, all 12 flags, and
no evidence.

**Mutations, all red:**
- the record-evidence leg dropped;
- the outside-six leg dropped;
- refuse-everything, on either path;
- outside-six categories read PROHIBITED.

**Tests:** 628 pass across the billing, CRM and regulatory vulnerability suites.

**What it costs.** Nearly every debt household an agent has spoken to cannot be disconnected
until a welfare assessment exists. That agrees with the published record: debt disconnections
have been in single digits since 2017 and zero since Q1 2023 (`debt_and_collections.md`).

**Reversible** by removing `_held_evidence` from `safety_net_on_record` and the `other` leg from
`safety_net_protection`.

## The other thirteen

| # | | grade |
|---|---|---|
| 3 | DISQ | **Passes in part.** Financial insecurity an agent recorded (job loss, payment difficulty, fuel poverty) now blocks. Financial insecurity nobody recorded, which is the debt itself, needs an ability-to-pay step before disconnection. That belongs to the collections atom. |
| 14 | DISQ | **Passes.** Code 26 (oxygen) is CANNOT_DETERMINE in every month, and no path turns it into a permit. The new control covers it. |
| 15 | SUPP | **Passes** (fifth pass item 13). An AST guard stops any numeric weight deciding an outcome. |
| 13 | SUPP | **Passes as described.** The 60 to 65 band is CANNOT_DETERMINE without sex, and an evidenced pensionable-age code is honoured whatever the band. |
| 7 | DISQ | **Open, outside the claim.** `disconnection_warning.can_disconnect` checks the notice sequence only and reads no vulnerability. Neither it nor `WinterMoratoriumRegister.can_disconnect` has a production caller. The first caller must route through the one decider. |
| 6, 12 | DISQ / SUPP | **Open** (fourth pass item 7, fifth pass item 1). There is no run, so there is no rate and no cannot-determine share. |
| 4 | DISQ | **Open, collections atom.** There is no step that finds vulnerability before a disconnection (contact attempts, a visit). |
| 5, 11, 16 | | **Out of scope:** the PPM offer before disconnection, self-disconnection support, and the debt lever. These belong to the collections and prepayment atoms. |
| 10 | DISQ | **Open, new, unverified.** The reviewer's prior is reconnection within 24 hours of a wrongly disconnected protected household. Nothing models reconnection. That it is published practice is not established here. It is a knowledge question before it is a build. |
| 8, 9 | SUPP | **Known gaps** (fifth pass items 12 and 15): expiry and refresh, network sharing, PSR services. |

## Verdict

**FAIL on items 1 to 3. Fixed in this tick, in the direction of protection.** Held at 2. If the
seventh pass, run on the "any evidence held" rule alone, raises nothing within the claim, the
level moves.
