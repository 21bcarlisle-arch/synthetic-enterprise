**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# The director's "a save is never paid for by the stayers" control is red at origin, and no red census holds it (2026-10-14)

`tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py` fails 2 of 8. The two failures are the
same on both sides of e3b5ed01a:

| test | 58e1e8905 (origin, e3b5ed01a's parent) | e3b5ed01a (writer one's basis) |
|---|---|---|
| `test_a_saved_term_ends_and_stayers_renew_after_it` (line 76) | FAILED | FAILED |
| `test_no_stayer_price_moves_with_the_save_price` (line 95) | FAILED | FAILED |
| the other six | pass | pass |

Run 2026-10-14 in `/var/tmp/se-w1-origin` and `/var/tmp/se-w1-basis`, 1h45m each at load ~47. The logs are
`/var/tmp/w1-basis-out/stayers-{origin,fix}.log`.

**What fails.**

- **Line 76 is the precondition.** The `on` and `placebo` arms no longer save the same households.
- **Line 95 is the director's condition** (2026-10-08). It lists stayer price moves on both sides. Pytest
  truncated the list, so the count is not known; the first rows carry different unit rates on the two sides.

Line 95's red cannot be read while line 76 is red. If the arms save different households, a stayer's price
can differ for that reason alone. So the control currently says nothing either way about whether the stayers
pay for the save. That is why this finding is BLOCKING: the save has been live by curriculum since
2026-10-10.

**Not established:**

- **When it went red.** The last commit to the test is afd818b22 (2026-10-11). The test is slow, so it is
  probably outside every selection that ran since then.
- **Why it is held nowhere.** It is in neither `head_red_observed.json` nor `head_red_baseline.json`. Whether
  the census skips it for its runtime is the first thing to ask.

**What it changed.** The writer-one claim had held e3b5ed01a off origin on exactly this comparison. Its holder
died before the comparison ran. Both reds are already present at origin, so e3b5ed01a did not cause them, and
it is promoted on that basis. The regrade5 arms (price match against risk tiers, plus the save's S1) wait on
that promotion.

**Next, one variable at a time:**

1. Bisect line 76 between bfcae065d (2026-10-08, where the control was written green) and 58e1e8905. The
   control takes about 50 minutes on an idle machine, so bisect with `--report-end` shortened only once a
   shorter window is shown to still end a saved electricity term. The docstring says the first one ends on
   2018-06-20.
2. Find out why the census cannot see this test.

---

## Worked 2026-10-14 (worker tick, claim `the-save-stayers-control-is-red-at-origin-bisect-and-hold-it`)

**Correction, beside "Why it is held nowhere".** The census does hold this test. The file read above
was the *legacy* tracked `docs/observability/head_red_observed.json`. Nothing has written it since
2026-09-10 (`background/head_red_register.py`, `LEGACY_OBSERVED_PATH`). The live observation is the
untracked `docs/observability/.head_red_observed.json`, and it reads:

| census run (head) | line 95 `test_no_stayer_price_moves_with_the_save_price` | line 76 |
|---|---|---|
| 2026-10-10 05:41 (cf8706023) | red | green (not listed) |
| 2026-10-11 05:45 (ab1bf89f7) | red | green |
| 2026-10-12 05:56 (ed9aa25eb) | **green** (`currently_red: false`) | green |
| 2026-10-13 03:37 | not run: deferred by the memory governor ("UNPROVEN ... register not updated") | — |
| 2026-10-14 03:38 | not run: deferred (termcost-arms-floor-a declared 11,200 MB) | — |

So the census stopped seeing it because the census stopped running, not because it skips the test.
It has been deferred two nights running. Nothing needs to change to "make the census hold it": the
next census that is admitted will record it. What is owed is the governor's two-night deferral,
which is the census's own standing condition and is not this item's to fix.

**What this does to the bisect.** Line 76 was green at ed9aa25eb (the 2026-10-12 census head, an
ancestor of origin). The range is ed9aa25eb..58e1e8905, not bfcae065d..58e1e8905: 263 commits,
about 20 first-parent commits touching `simulation/`, `company/`, `saas/` or `sim/`, so about 5
bisect steps instead of 9.

**What the failing run already says about line 76.** The first 18 saves are identical in both arms.
At index 18, `on` saved SYN-2016-365 (term 2017-08-13) and `placebo` saved SYN-2016-391 (2017-09-05),
and `on` holds one more save (SYN-2016-347, 2018-08-04). That is a divergence in **2017-08**, ten
months before the first saved electricity term ends (2018-06-20). So the cause is *not* an ended
saved term teaching the premium. Something that reads the save price *during* a saved term reaches a
later household's renewal rate or its roll. Line 95's first listed move is SYN-2016-406, electricity,
off 107.23 / on 106.78 £/MWh: a stayer priced 0.4% *lower* in the `on` arm.

**Prediction, filed before the probe below returns.** Stayer price moves begin before 2017-08-13, and
the earliest is a renewal priced after a save's first bill has posted. Probe: both arms to
2017-12-31 at origin 55701bb84, every stayer row diff with its keys
(`/var/tmp/stayers-probe/probe.py`, launched under `launch_long_job` as `stayers-probe-2017`).
