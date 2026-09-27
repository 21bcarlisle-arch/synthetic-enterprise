**Severity:** RECORD · **Lane:** delivery · result for DIRECTION item `the-brand-reference-pages-leave-the-published-tree`

# Result: three unlinked published files are gone from site/, and their debt entries with them

**Disposition of the duplicate-work note.** The draw reported this id as already held in
`.seat_work_in_hand.json`. That was the draw's own write, not another writer, so I did the work
rather than releasing it. The path check said "6 already landed". That meant the paths were
unchanged, not that the move had been done: at `b2d2de01f` all three files were still under `site/`.

## What changed
- `site/brand/exemplar.html` and `site/brand/proof.html` moved to `docs/design/brand/` with
  `git mv`. `proof.html` now links `../../../site/brand/tokens.css`, so it still renders from a
  checkout.
- `tests/tools/test_brand_compliance.py` points at the new paths. The exemplar is still
  byte-pinned to the §7 fence, and `proof.html` is still graded as a token-consuming surface,
  now named explicitly instead of found by globbing `site/brand/`.
- `BRAND_RULES.md` and `BRAND_CONSTITUTION.md` point at the new paths.
- `site/snapshots/DASHBOARD_20260623_120151.html` is deleted. Its `.json` companion is deleted
  too: it existed only to advertise the deleted page's public URL.
- `PAGE_ORPHAN_DEBT` loses all three entries, leaving only `404.html`, which is permanent by
  design. `BANNER_EXEMPT` in `background/publish_provenance.py` is now empty, and its test
  asserts that.

## Controls re-keyed rather than weakened
- The anti-vacuity test in `site/test_ia_register.py` and its two mutation tests used the brand
  files as the rare branch. They now use `404.html`, a non-area file the page walk still has to
  report. The branch can still be taken, and both mutations still fire.
- `test_the_typed_five_were_blind_to_nineteen_pages` measures the tree at `03dd8c49e^`, which
  still holds the snapshot. It now passes the exemption that applied to that tree, using the
  `exempt` parameter that exists for this case, so 24/19 still holds.

Verified: the whole `site/` suite (978 passed), `tests/design/`, the brand, provenance, e2 and
reachability suites all pass.
