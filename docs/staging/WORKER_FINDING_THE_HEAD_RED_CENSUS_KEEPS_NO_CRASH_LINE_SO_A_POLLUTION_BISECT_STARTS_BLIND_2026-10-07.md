**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `H40_full_suite_pollution_bisect`
**Evidence:** `docs/staging/records/WORKER_RESULT_H40_THE_FULL_SUITE_POLLUTER_IS_THE_REGISTRY_EAC_REWRITE_WRITING_INTO_THE_SHARED_ROSTER_2026-10-07.md` §4

# The head-red census keeps no crash line, so a pollution bisect starts blind

`background/head_red_register.record(...)` stores each red's node id, run count and dates. The
only cause it keeps is a per-run count by exception type (`causes`: `AssertionError x13`). The
nightly journal prints `NEW RED <node>` and nothing more.

**Why it cost something.** A red that is green in isolation is pollution, and the first thing a
bisect needs is the census's own failure line: which assertion fired, and with what value. H40
named the polluter for `test_c1_eac_calibrated_to_ofgem_tdcv_medium` and
`test_c4_solar_reduces_multiplier` only by reproducing them. For the two
`test_the_registry_eac_rewrite_reaches_the_dd_opening` nodes it could not get that far. Without
their crash lines it could not tell an empty drawn book (`assert drawn`) from a broken identity
(`not_shared`), and that took one 58-minute batch that timed out plus one six-minute probe. The
2026-10-04 turning-commit finding hit the same wall ("the store does not keep a cause per test").

**Proposed remedy, the smallest one:** keep the first line of each red's `reprcrash`
(`<path>:<line>: <message>`, truncated to about 200 characters) on its record and print it beside
`NEW RED`. That is one field and no new store. It is reversible by dropping the field.

**Not done here:** the H40 tick's subject was the bisect, and this is the census's code.
