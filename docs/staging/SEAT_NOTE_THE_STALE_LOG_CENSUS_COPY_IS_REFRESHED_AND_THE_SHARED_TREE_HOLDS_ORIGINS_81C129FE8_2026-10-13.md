# The stale log-census copy is refreshed, and the shared tree now holds origin's 81c129fe8 bytes

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-shared-trees-stale-log-census-copy-reverts-origins-tool-reader-leg` (Lane 0 delivery)

*Worker tick, 2026-10-13. Item: `the-shared-trees-stale-log-census-copy-reverts-origins-tool-reader-leg`.*

**Premise: live, not spent.** Both cited commits (81c129fe8, a070c2195) are on origin, but the shared
tree's copy of `tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py`
(mtime 2026-10-10 20:58) was older than HEAD and older again than origin. The landing door graded it
`predates_landing`; `refresh_to_head` found it supplied no name HEAD lacks.

**Done.**
1. `refresh_to_head --write --slug stale-log-census-copy-2026-10-13` — the old copy is preserved at
   `refs/preserved/refresh-to-head/stale-log-census-copy-2026-10-13`.
2. HEAD's bytes were not enough. The shared HEAD is 29 behind origin (and 2 ahead), and 15 of the two
   commits' paths already held **origin's** bytes on disk, `saas/reporting/annual_report.py` among
   them. Against that disk, HEAD's copy of the test **failed**
   (`test_the_census_selects_enough_logs_to_be_capable_of_finding_one_dropped`) and origin's passed
   3/3. So I wrote origin's blob instead.
3. The same mixed-state red applied to two files that were clean at HEAD and behind origin:
   `tests/saas/reporting/test_a_run_level_record_the_runner_returns_is_actually_published.py` and
   `tests/simulation/test_the_gas_half_of_the_shape_switch_reaches_a_reader.py`. Both failed at HEAD's
   bytes. I wrote origin's bytes and all three files passed, 9/9.
4. `tests/saas/reporting/test_annual_report.py` held exactly one hunk: the weak solvency assertion
   that 81c129fe8 replaced (`"15" in result` / `"below" in result`, which the header alone satisfied,
   as origin's docstring records). I wrote origin's bytes and the solvency tests passed, 7/7.
   `refresh_to_head` refused it because of the old comment line, and I judged that line superseded.

**Left alone:** `simulation/run_phase2b.py`. It is staged by another lane: a hedge executes at the
market's forward quote, cited to `docs/market_research/a_hedge_executes_at_the_markets_quote_...2026-10-12.md`.
That is holder work, not a stale copy.

**Nothing to commit from the tree.** Every file now equals origin, so landing any of them would be a
no-op. This note is the only landing. When the shared HEAD reaches origin, these paths read clean.

**Duplicate-work check:** `value-arm-term-cost-base-measure-what-moved` names the same test file as
a substrate it measures. It is different work, so I took no disposition against it.
