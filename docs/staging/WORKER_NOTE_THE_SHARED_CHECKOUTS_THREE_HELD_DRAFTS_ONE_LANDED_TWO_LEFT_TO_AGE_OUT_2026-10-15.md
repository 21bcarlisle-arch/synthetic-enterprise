# The shared checkout's three held drafts: one correction landed, two left to age out

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

*Worker, 2026-10-15. Disposition of the delivery item `the-shared-checkouts-three-held-drafts-are-landed-or-let-age-out`.
The shared checkout was 122 commits behind origin/main and 0 ahead when this was read.*

**(1) `docs/institutional/knowledge_map.md`: the draft was right, and origin was wrong.** Origin carried
£130 per dual-fuel customer as the Capital Target in three places. Ofgem's decision of 26 July 2023,
*Strengthening Financial Resilience - Minimum Capital Requirement*, §1.28: *"We have therefore decided
that the Capital Target should be set at £115."* §1.36 records the cut from the consulted £130. Origin's
own `docs/market_research/bad_debt_provisioning.md` already quotes both passages; the map had not
caught up. I landed only the three corrected lines, taken from the draft and applied to origin. The
rest of the draft predates origin (it would delete the W1_29 spread row, among other things) and is
not landed.

**(2) `tests/company/compliance/test_crisis_bad_debt_validator.py`: not landable as written.** The
draft is a fork from before `c0e383908` (crisis window moved to 2022-23) and before the gzip switch
(2026-10-10). Its `test_the_strict_marker_is_not_armed_by_the_working_tree_copy` grades the committed
blob at `HEAD:docs/reports/run_output_latest.json`. That plain path has not been committed since the
switch, so on origin the helper always skips. The guard would pass without ever testing anything.
Landing the file whole would also revert origin's three strict xfails, its gz-reading guard and its
IFRS 9 leg.

**The concern behind it still holds on origin.** `tools.run_output_store.load_run_output` prefers the
plain file and falls back to the gz. In the shared tree, the plain file is whatever run finished last,
published or not, so a strict xfail run there can flip because of a concurrent write. A gate extract
or a worktree holds only the committed gz, so the gate's verdict is unaffected. Only ad-hoc runs in
the shared tree are exposed. The remedy, if wanted, is small: have `_published_run_or_skip` read
`git show HEAD:<PUBLISHED_REL>` and hand the bytes to `loads_run_output`, then port the draft's
mutation guard against that read. Not done this turn.

**(3) `site/data/knowledge_topics.json`:** a superseded N-page draft. Left to age out, as the item said.
