**Severity:** BLOCKING · **Lane:** publish · **Item:** `the-76f894811d-book-reaches-origin-and-the-blocking-billing-findings-are-graded-on-it`

**Disposition (26 Nov 2026):** fixed in this landing, for the class and for the instance. The 76f894811d
book is not on origin, and it will not be published as it stands. The 2100f84f85 book has superseded it on the
shared tree, and that book is paused by INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR (4 breaches against
an exception allowing 1).

# A pause banner pushed a refused publish's stamp, so origin named 76f894811d over the 6af7fd0bfd feeds (26 Nov 2026)

## What the item asked, and what was already spent
- The grading was already on origin when this item was drawn. d415a97872 graded the six BLOCKING
  billing findings on 76f894811d (12 held, 4 missed) and closed or re-parked their items.
- The `grade-the-first-book-at-or-after-7f90f9563` continuation was already retired.
- The 22:42Z publish of 76f894811d (pid 4171222) was refused by
  `site/explore/test_a_catch_up_bills_vat_is_the_vat_of_the_lines_above_it.py::test_inv5940_...`. That
  test pinned a £21.57 catch-up that the bill no longer carries. I re-keyed it to the identity and
  mutation-proved it, but de3138e6d0 landed the same fix first, so my copy was dropped. Its version passes
  6/6 against the 2100f84f85 feeds on the shared tree.

## The defect found
- Origin at 0b22846e13 served a `publish_provenance.json` that read:
  - `showing_run` = `last_verified` = 76f894811d, with 1,382 accounts and 54,463 bills.
- Every feed beside it is still the 6af7fd0bfd book. For example, `company.json` reads
  `git_commit 6af7fd0bfd`, and OCC-a097d0031a9f's April 2023 bill still reads £21.57. The site was
  claiming a book it does not show.
- How it happened:
  1. `process_run_complete` calls `record_verified` before the publish commit, so that the stamp lands
     in the same commit as its figures.
  2. The commit was refused at 22:42Z, and the stamp stayed in the working file.
  3. The next cycle (2100f84f85, red on a domain invariant) ran `_publish_provenance_banner`. That pushes
     this file alone, and it pushed the stale stamp.
- `record_paused` is right that it cannot move the served fields. The gap is that it was never asked
  whether the fields it left alone had ever been served.

## Fix
- `publish_provenance.withdraw_unserved_stamp(committed)` resets `showing_run`, `last_verified` and
  `figures_caveat` to the committed copy's values.
  - It can only move them back to what is published, never forward.
  - It writes nothing when the two agree or when git cannot say.
- `_publish_provenance_banner` calls it before `record_paused`.
- Instance: origin's provenance is put back to the 6af7fd0bfd stamp (from 0b22846e13^), with the pause
  fields left untouched.

## Evidence
- `tests/background/test_a_banner_pushed_alone_names_the_run_whose_figures_are_committed.py` passes 2/2.
  With the call removed, it goes red: `assert '76f894811' == '6af7fd0bf'`.
- The provenance and decoupling suites pass 39/39.

## Left open
- A refused publish still leaves the stamp in the shared tree's working file until a banner or a
  verified publish rewrites it. Only the alone-push is guarded. The full publish commits the stamp with
  its figures, so the two agree there.
