# land11 timed out, and the MSC landing is split in two

*Worker, 25 Nov 2026, holding `land10-outcome-is-read-and-msc-lands-or-is-re-cut`.*

**What land11 did.** It found the council-tax fix on origin (`dd6901041b`, 02:05Z), waited out a live
book, applied msc8.patch 3-way on `05958e99f3` cleanly, and passed the fire-time stale-copy census
apart from the declared drop. It waited 1,810 s for the landing-gate lock (the gas-AQ landing held it)
and acquired it at about 03:21Z. It ended `exit 124` at 04:20:45Z with no failure printed
(`/var/tmp/se-msc-land11-ended.txt`).

**What the 124 was, read plainly.** It was land11's own outer `timeout 5400` around `surgical_land`,
and that clock *did* spend the lock wait, though the gate's message says the wait "is not spent from
the hour". So the gate itself had about 3,590 s and had not finished. land10's gate on the same
patch ran to the end in 3,379 s. Either way, the whole patch's serial gate sits at the 3,600 s hook
hour, and whether it fits depends on load. That is what `da44381d2` predicted. This is the item's
"gate timed out" branch: **split the landing.**

**The split, read off `select_targets` file by file** (probe `/tmp/msc_split_probe.py`):

- `saas/ledger.py` alone pulls in 120 test files beyond the control set, including
  `test_collections_journey.py`, whose two live-run setups took 700 s serially.
- `simulation/run_phase2b.py` and `run_phase4c_on_phase2b.py` pull in the whole-run setups: the flat
  supplier (1,542 s before sharing), phase 4c's `main_result` (1,097 s before sharing), and reg 6C (557 s).
- Neither half selects the other's heavy setups. So two gates, each well under the hour, replace one gate that sits on it.

**Increment A, landed with this record.** It is the company's booking of the charge:
`saas.ledger.make_market_stabilisation_charge_event`, `growth_desk.book_market_stabilisation_charge`,
the 6300 posting in `double_entry`, and the optional `market_stabilisation_charge_events` argument to
`close_the_books`. Its company-side test is `tests/simulation/test_the_market_stabilisation_charge_is_booked.py`:
margin falls by the charge, acquisition spend does not move, the journal posts to 6300, and two fuels
are two events. No run moves. Nothing emits the event until B lands, and every new argument defaults to empty.

**Increment B, still owed** (handed on as `msc-b-the-world-charges-the-msc-on-a-replacement-win`).
It covers `simulation/run_phase2b.py` (the charge on replacement wins, `book_after_the_run`, and reg 6C's
decision-leg guard), `run_phase4c_on_phase2b.py`, `annual_report.PHASE2B_KEYS_NOT_PUBLISHED`,
`orphan_baseline.json`, and the shared-fixture pieces (both conftests, the flat-supplier test, and the
phase 4c test). Cut it from msc8.patch with `--exclude` on A's five paths. Keep the declared drop of
`tests/simulation/conftest.py`. The outer timeout must start *after* the landing-gate lock, or must
not exist.

**A's first gate, 701 s, went red on origin's own defect, now fixed in this landing.**
`test_collections_journey.py::test_every_live_consent_offer_goes_to_an_account_still_supplied` errored
at setup with `plan 19: an agreed instalment must be positive, got 0.0`. It fails the same way on a
clean origin `95cec7822b`, without A. A probe printed the offer: ACC-SYN-2016-356 on 8 Nov 2016,
undisputed overdue GBP 0.07. The world's own instalment (`simulation/plan_offer_response._own_instalment`)
is the debt over the months to recover. For 7p that rounds to GBP 0.00, and the household "agrees" a
plan that never repays, which the company's plan book rightly refuses. The fix floors the household's
own instalment at one penny (a unit of account, not an estimate), still capped at the debt. Control:
`test_a_debt_of_a_few_pence_is_agreed_at_a_payable_instalment`, red on the unfixed module and green
on the fix. The collections test passes on the fix (494 s, with both constant registers). The gate
time also measures the split: A's selection of 2,890 tests ran in 701 s, against the whole patch's 3,379 s.

**Behind that error, the gate's second pass (969 s) found two strict-xfail Consent controls XPASSing.**
`test_an_answered_live_run_decides_the_consent_offer_both_ways` and
`test_the_world_counts_every_consent_offer_the_company_made` were held open on the premise that the
answered 2017 window holds no Consent offer to a supplied account. Reproduced locally (490 s): both
pass, and the leaver guard is green. The marks are dropped, and `made` keeps the second from going
vacuous. **I cannot yet say which change put a supplied offer back in 2017.** It could be the gas-AQ
landing `b3f3a23f6f` or this penny floor. Origin errored at setup, so these controls had not run
since b3f3a23f6f. For the owners of `the-answered-window-holds-a-consent-offer-to-a-supplied-account` /
`the-answered-window-re-key-from-the-probe-result`: the 2017 window no longer needs re-keying on
today's tree. Their 2018 probe still answers its own pre-registered question.
