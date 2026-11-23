**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A landing that touches the ledger outruns the gate deadline under ordinary load, and the only door then refuses it

Found by the delivery seat, 23 Nov 2026, while landing the MSC replacement win (claim
`verify-msc-replacement-win-landing-v3`; salvage `ae573846b1` against base `4f9da23163`, nine paths).

**What happened.** The MSC change touches `saas/ledger.py`, `company/finance/double_entry.py`,
`company/finance/accounting_close.py` and `simulation/run_phase2b.py`. `[impact-select]` maps its 7
mappable changes to **1,074 impacted test files** through the static import graph (`/tmp/msc_land/sel_run.log`).
`tools/pre_commit_test_gate.py` runs them in one serial pytest, and `tools/surgical_land.py` kills the
hook at `GATE_TIMEOUT_SECONDS = 3600`.

- v2 (22–23 Nov): refused unrun. The hook timed out while the gas chain gated `run_phase2b.py` beside it.
- v3 (10:48–11:48Z, 23 Nov, `/tmp/msc_land/land3.log`): refused, `timed out after 3600 seconds`, with the
  pytest progress at **88%** and no failure printed. The 11.8 GB cut012 book and other lanes' suites
  were running at the time (16 cores; load 4–6).

There was no red in either attempt. The door could not finish asking.

**Why it matters.** The gate never fails a change like this. It times out on it, and the timeout
looks the same as a refusal. A change to the most widely imported money modules is exactly the
change that most needs gating, and it is the one most likely to run past a fixed deadline that was
set for publish-commit symmetry (`surgical_land.py:873`), not for selection size. Nothing in the
door tells the lander, before the hour is spent, that the selection will not fit.

**Not done here (correctly).** The deadline was not raised and the selection was not trimmed by
hand. Both would weaken a gate in order to land one change. v4 was re-launched unchanged at
11:56Z on a lighter machine (`/tmp/msc_land/land4.sh`, end marker
`/var/tmp/se-msc-land4-ended-20261123.txt`).

**Candidate remedies (for the harness lane; none taken):**
1. Let the gate predict its own run time from recorded per-file durations, and refuse up front with
   that named cause when the selection cannot fit, rather than after an hour.
2. Run the selected files in parallel (xdist) inside the gate, if the suite tolerates it. This needs
   a measurement first, because some controls share on-disk state.
3. `ADVISOR_QUESTION_WOULD_BATCH_THEN_BISECT_LANDING_CUT_GATE_TIME_2026-10-15.md` asks a related question.

**Done means:** a landing whose selection cannot finish inside `GATE_TIMEOUT_SECONDS` is either told
so before it starts, or is given a gate that finishes. A test should show a 1,000-file selection
under a recorded-duration model being refused with the named cause rather than killed.
