# archive/

Code kept out of the live tree, at its original relative path, so restoring it is a `git mv` back.

## unhooked_supplier/

Supplier modules (`company/`, `saas/`) that no run reaches — imported by their own tests and
nothing else — archived with those tests. Ruled in section 4 of
`SEAT_FINDING_OWN_CODE_REVIEW_UNUSED_DUPLICATED_AND_WALL_CROSSING_2026-10-24.md` (landed
`4e3a978bf5`): built and tested, never wired, and costing about 23% of the suite's test functions
plus a third of the supplier's `grep` hits on `tariff`, `hedge` and `register`.

- Nothing here is collected (`archive/conftest.py`), linted (`ruff.toml`), or indexed
  (`tools/capability_index.EXCLUDED_ROOTS`).
- The live import paths are gone: `company.market.tnuos_ledger` no longer imports. A module here
  that a later build needs comes back WITH its tests, and must then be reached by a run, or the
  orphan ratchet refuses it.
- `MANIFEST.txt` lists every archived path and the commit that moved it.
