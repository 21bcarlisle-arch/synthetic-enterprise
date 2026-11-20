**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# The "E7 and multi-register cap readers green after publish" item was spent when drawn (2026-11-20)

The continuation `e7-crossing-and-mr-cap-readers-green-after-publish` (handed on 19 Nov) asked
for two things once a new book had published: confirm two post-publish readers are green, then
move the E7 finding to done/. It was drawn at about 06:30Z on 20 Nov.

**Measured at the draw:**

- The published book is still 6af7fd0bfd. `run_output_latest` has
  `producing_commit.commit = 6af7fd0bfd`, and `.post_publish_reader_reds.json` was checked at
  2026-11-18T10:57Z against that hash. Its only red is
  `test_the_published_book_charges_its_contracted_tariff`.
  `default_tariff_rate_within_cap` is not in the reds.
- The finding already sits at
  `docs/staging/done/WORKER_FINDING_AN_E7_FIX_ROLLING_TO_SVT_MID_PERIOD_IS_CHARGED_ABOVE_EVERY_RATE_IT_WAS_SOLD_AT_2026-11-18.md`.
  It was moved by 2a214e0c16 at 05:52Z, which also rebuilt the ledger at b3c18d1846 without
  publishing it. On that ledger the test file passes 10 of 10, and the cap claim reads
  27,549 AGREED and 0 DISAGREED.

**Why the item was released, not put back.** The part still open is "the next publish's
readers are green". No continuation needs to hold that. `process_run_complete` runs
`background.post_publish_readers` after every publish, and any red reaches the supervisor's
doorbell through `doorbell_clause()`. A seat item that waits for the same event would only do
that mechanism's job a second time.

**What would refute this.** If the first publish after b3c18d1846 still lists
`test_the_published_book_charges_its_contracted_tariff` in `.post_publish_reader_reds.json`,
the unpublished rebuild did not stand in for the real one. The doorbell would then name that
red, and it becomes a new finding.
