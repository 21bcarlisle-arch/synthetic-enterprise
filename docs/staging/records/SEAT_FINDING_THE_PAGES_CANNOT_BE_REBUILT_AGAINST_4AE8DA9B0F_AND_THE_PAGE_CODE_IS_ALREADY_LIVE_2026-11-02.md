**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The pages cannot be rebuilt against 4ae8da9b0f, and the page code is already live

Delivery seat, 2 Nov 14:30Z. This answers item 2 of the director's 2 Nov steer
(`docs/staging/advisor/done/DIRECTOR_STEER_THE_VALUE_TEST_MUST_BE_ABLE_TO_ANSWER_AND_THE_SITE_MUST_BE_CURRENT_2026-11-02.md`):
"If the publisher can rebuild the pages from current code against the last verified run (4ae8da9b0f),
do that now. … If it cannot, say why in Done, and give the earliest time a verified run will publish."

**Answer: it cannot, and it would not help. I did not build the door.** There are three reasons, and
each one was measured.

## 1. The page code is already current

`deploy-pages.yml` deploys `site/**` to Cloudflare Pages on every push to main. On 2 Nov at 14:20Z,
the live bytes matched `origin/main` exactly for `/`, `/privacy/`, `/capabilities/index.html`,
`/explore/index.html` and `/assets/freshness-banner.js`. So the privacy notice, the copy fixes and every
fix made in page HTML or JavaScript are **already live**. Only the generated data feeds under
`site/data/` are held at the 4ae8da9b0f publish. That includes the "Generated 2026-10-26" stamp. The
steer's premise that "the pages stay at a 26 Oct commit" holds for the feeds only.

## 2. Most of the twelve fixes are in the run, not in the pages

Of the twelve fixes in DIRECTION.yaml's "THE PAGES" row, these change code in `company/` that runs
**inside the simulation**: the EPG line (82d26fbd4), the printed register after an estimate
(37abacdf4), the opening read (1bdd86b84), the successor's MPAN and MPRN (971a37583), one serial per
supply point (6ef8f1b67) and one definition of a missed payment (dae9f598d). Those fixes are in
`monthly_bill_assembly`, `customer_registry`, `collections_journey` and `raw_account_export`. No
rebuild against a saved 26 Oct JSON can carry them, because they change what the run itself writes.

## 3. Today's correctness gate refuses 4ae8da9b0f's book

Prediction, written before grading (`/var/tmp/regrade-4ae8/PREDICTION.txt`):
- P1: refused, with INV_RENEWAL_NOTICE between 1,000 and 1,400.
- P2: at least one PC2 or E7 row also breaches (low confidence).

Method: `tools.generate_billing_ledger.generate` (current code) over
`run_output_4ae8da9b0f_20261026T022647Z.json`, then `tools.domain_invariant_runner --ledger` with the
live customer files as `--printed`. Grading 1,291 accounts gives **17 rows breached, 42,355
breaches**:

| row | breached |
|---|---|
| INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF | 23,706 |
| INV_PPM_NOT_CREDIT_BILLED | 6,254 (100%) |
| INV_STANDING_CHARGE_SVT_GAS | 4,150 |
| INV_STANDING_CHARGE_SVT_ELEC | 2,898 |
| INV_OVERDUE_WITHIN_BALANCE | 1,638 |
| INV_RENEWAL_NOTICE_42_TO_49_DAYS | 1,326 (100%) |
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | 889 |
| INV_UNIT_RATE_SVT_ELEC / _GAS / _EPG_HOUSEHOLD | 540 / 460 / 374 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 52 |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | 25 |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 18 / 12 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 6 |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 4 |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 3 |

- **P1 held:** 1,326, which is every term, because the JSON has no `renewal_notice_log`.
- **P2 was refuted in the form I wrote it.** E7 two-register is NOT_IN_EXPORT, and read-monotonic and
  ToU bands are clean. The breaches are much wider than I predicted, though. This book predates the
  whole correctness stretch: prepayment billed as prepayment, the cap-window prices and the gas
  conversion.

4ae8da9b0f was "verified" under the 26 Oct gate and its exceptions. Those exceptions have since been
retired. The director's ruling of 26 Oct says: "A breach blocks the publish, or is recorded as a named,
dated exception." So rebuilding its feeds under current code would publish a book that today's suite
refuses on 17 rows, with a fresh stamp on it. That breaks his ruling, and it is the fake-fresh sin
that property 3 of the 10 Aug decoupling ruling names. Bypassing the gate for this one door would need
his ruling changed (G9). It is not worth asking for, because of point 4.

## 4. The earliest verified publish is today, by the ordinary route

8cf2ecb744 (13:10Z) is the E7 catch-up fix for the last 3 of the 9 PC2 breaches on 85b044be54, and
it is on origin. The shared tree's HEAD contains it. The sim runner finished its between-run pause at
about 14:01Z, and it has been **deferring** since then, "the code a run would import is not origin's"
(41812d65cc is not yet on origin). It starts as soon as the shared tree and origin agree. A run takes
about 95 minutes and its grade and publish chain follow, so the **earliest verified publish is about
17:00–18:00Z on 2 Nov**, if that book grades clean. If it does not, the refusal names the rows. That
watch is owned by focus item `the-last-pc2-catch-up-defect-then-the-publish`, step (5).

**Reverse:** delete this file. No run, publish or real-world act. The regenerated ledger and grade are
scratch files under `/var/tmp/regrade-4ae8/` and were never written into the tree.
