# WORKER FINDING — a null CLV enters the published median, percentile and sum as the number zero

**Severity:** BLOCKING · **Lane:** D_billing_metering · **Disposition:** QUEUED (not fixed on sight)

**Severity ESCALATED LATENT → BLOCKING 2026-08-18** (worker tick, LANE 3 DISCOVER draw on
`EP1_clv_three_horizon`, pass 6) by running the one check this document said it had not run —
see "The check this finding declined to run" at the foot. A published figure is not merely at
risk; `docs/reports/ANNUAL_REPORT.md:2237` at HEAD `9718066ce` names five accounts to the board
as priority retention targets, and two of them are on that list only because five manufactured
zeros sat beneath them in the sort. That is the BLOCKING trigger verbatim.

**Found:** 2026-08-17 worker tick, during the repo-wide sweep closure item 3 of
`WORKER_FINDING_THE_PUBLISH_PATH_SWALLOWED_199_GENERATOR_CRASHES_2026-08-17.md` asked for
(the sweep's job was to find remaining crash sites; there are none — this is what it found
instead).
**Subject:** `saas/reporting/annual_report.py`, lines 8217-8242 and 2367.
**Class:** a structural blank folded into an aggregate as a real value.
**Measured at:** the tree of this tick. Everything below is `observed-with-evidence` (R9).

## The measurement

`build_clv` records `clv_gbp: null` for an account that is no longer supplied — correct
behaviour, and the deliberate output of `W2_17`: an account that has left has no lifetime
value, and publishing 0 for it would state a belief the company does not hold. The
`_round_or_none` helper exists precisely to carry that null to the published per-customer
record without turning it into a number.

Seven sites in the annual report then turn it straight back into 0 before aggregating:

```python
clvs = sorted((v.get("clv_gbp") or 0.0) for v in elec_accounts.values())        # :8217
churns = sorted((v.get("latest_churn_probability") or 0.0) for v in ...)        # :8221
for cid, v in sorted(elec_accounts.items(), key=lambda x: -(x[1].get("clv_gbp") or 0)):  # :8229
    clv = v.get("clv_gbp") or 0.0                                               # :8230
    churn = v.get("latest_churn_probability") or 0.0                            # :8231
    periods = v.get("expected_lifetime_periods") or 0.0                         # :8232
total_clv = sum((v.get("clv_gbp") or 0) for v in elec_accounts.values())        # :8242
```

`v.get("clv_gbp") or 0.0` is a *different* defect from the `round(d.get(k, 0), n)` one just
closed, and it is the reason a sweep for the crash shape does not find it: it never raises.
It silently substitutes.

**Population, measured, not guessed.** In `docs/reports/run_output_latest.json` this tick:
**5 of 13** billing accounts carry `clv_gbp: null` (and the same 5 carry
`expected_lifetime_periods: null`). So on today's book roughly **38% of the accounts entering
these aggregates enter as a manufactured zero.**

## Why it matters, at its real size and no larger

* `sorted(...)` at :8217 and :8221 feeds **percentiles and a median**. Five zeros placed at
  the bottom of a 13-element sorted list do not merely lower the mean — they move the
  *median's index*. A median is supposed to be robust to outliers; it is not robust to
  fabricated members.
* `sum(...)` at :8242 is the one case where the substitution is arguably harmless — an absent
  CLV contributes nothing to a total either way. It is listed for completeness, not as damage.
* The `sorted(..., key=-clv)` at :8229 ranks every no-longer-supplied account **last**, which
  happens to look right, and is right for the wrong reason: it is ranking them as *worth zero*
  rather than as *not applicable*. The moment a genuinely worth-nothing account exists, the
  two become indistinguishable in the published table.

**What this is NOT.** It is not the four-day publish freeze, and it does not retract that
finding's discharge — the crash sites were the two named generators and both are fixed. It is
not a crash, and it is not currently known to have moved a headline the director has read:
this finding measures the mechanism and the exposed population, and deliberately stops short
of claiming a specific published figure is wrong, because that check has not been run.

## Why it is filed rather than fixed

`SELF_INTERRUPT_DISCIPLINE`: the supply of findings is infinite and fixing on sight is the
treadmill. It also belongs to a different lane and a different subject than the finding whose
sweep surfaced it — the annual report's aggregation semantics, not the publish path — and
deciding what an aggregate *should* do with a structural blank (exclude from the population,
or report alongside a coverage count) is a design question, not a patch.

## What would close it

1. Decide, once, what these aggregates do with a null: the strong candidate is **exclude from
   the population and publish the excluded count beside the figure**, so a median over 8 of 13
   accounts says so. Silently dropping them is the mirror defect of silently zeroing them.
2. R10 — close the CLASS, not these seven lines. The invariant is "a structural blank must
   never enter an aggregate as a value"; `or 0` on a field the codebase deliberately publishes
   as null is the detectable shape.
3. R15 — the control must be able to fail: swap one account's `clv_gbp` between null and 0.0
   and the published median must MOVE. If it does not, the control is measuring nothing
   (cf. the swap-the-belief-between-two-units technique).

---

## The check this finding declined to run (2026-08-18, worker tick, EP1 LANE 3 pass 6)

This document stopped, deliberately and correctly, at "it is not currently known to have moved
a headline the director has read: this finding measures the mechanism and the exposed
population, and deliberately stops short of claiming a specific published figure is wrong,
because that check has not been run." The check has now been run. Everything below is
`observed-with-evidence` (R9), measured at HEAD `9718066ce` against
`docs/reports/run_output_latest.json` and the committed `docs/reports/ANNUAL_REPORT.md`.

**The site the finding did not name is the one that publishes a board instruction.**
`saas/reporting/annual_report.py::_section_customer_strategic_value` is where `clvs[n // 2]`
lands: the median is not a reported statistic there, it is the **quadrant boundary** of the
Customer Strategic Value Matrix, and the section ends in

    **Board action: CRITICAL quadrant has 5 account(s). High CLV at risk from elevated churn
    probability. Immediate retention offers recommended.**

— `docs/reports/ANNUAL_REPORT.md:2237`, committed, present at HEAD (`git grep` on HEAD, not on
the working tree). The median itself renders at `:2194` as `Median CLV: £791.98`.

**Population, re-measured this tick:** 13 electricity billing accounts, 5 with `clv_gbp: null`
(C1, C3, C4, C5, C6 — the ceased book; each also `expected_lifetime_periods: null`), 8 valued.
Same 5-of-13 the finding recorded.

**R15, the mutation this document itself proposed, executed on the shipped section builder.**
The proposal was: "swap one account's `clv_gbp` between null and 0.0 and the published median
must MOVE. If it does not, the control is measuring nothing." Calling
`_section_customer_strategic_value` on the real run output, then again with all five nulls
replaced by explicit `0.0`:

    as published    sha256[:12] d997858d414a
    nulls -> 0.0    sha256[:12] d997858d414a   IDENTICAL

Byte-identical. The distinction `build_clv` and `_round_or_none` are built to preserve — a
`null` is *not applicable*, a `0.0` is *worth nothing* — does not survive to the aggregation
site at all. The control measures nothing, as predicted.

**What the substitution actually moves, decomposed so the two effects are not conflated.**

*Effect A — the mechanism this finding names, in isolation.* Hold the population at 13 and the
churn boundary at its published 0.29; change only whether the five nulls enter the CLV order:

    med_clv  £791.98 (as shipped)  ->  £38,255.61   (48x)
    CRITICAL {C2, C8, C_IC1, C_IC2, C_IC3}  ->  {C_IC1, C_IC2, C_IC3}

**C2 (£791.98) and C8 (£1,163.69) are published under the heading "High CLV, High Churn —
priority intervention" and inside a board recommendation for immediate retention offers.**
They are the 7th and 6th largest of the 8 accounts that have a CLV at all. They clear a "High
CLV" boundary of £791.98 that exists only because five accounts with no CLV were counted as
worth zero. C2 clears it by being *equal to* it.

*Effect B — the population question, for completeness.* Removing the five unvalued accounts
outright (the finding's own preferred repair, "exclude from the population and publish the
excluded count beside the figure") also moves the churn boundary 0.29 -> 0.35, because those
five carry real churn probabilities. Executed on the shipped builder:

    Median CLV: £38,255.61 | Median churn: 35%
    **Board action: CRITICAL quadrant has 1 account(s). ...**

**The conclusion is robust to which repair is chosen**, which is why it is stated as a defect
rather than as a preference: the median is £38,255.61 under exclusion and £38,255.61 under
Effect A alone. Only the current silent zero yields £791.98. No honest treatment of a
structural blank reproduces the published figure.

**Sized honestly, and no larger.** The wrong figure is in the committed annual report, not on
the live site: `grep -rl "Strategic Value Matrix\|CRITICAL quadrant" site/` returns nothing, and
the live `https://poesys.net/data/company.json` publishes `enterprise_value_gbp` and a null
`household.clv_gbp`, not the matrix. `total_clv` is unaffected (£1,283,652.65 either way) — the
sum was always the harmless case, exactly as this document said. What is wrong is the boundary,
the quadrant memberships it decides, and the board instruction that counts them.

**One further defect at the same line, recorded not escalated.** `clvs[n // 2]` is not a median
for even *n* — it is the upper of the two middle values. With the nulls excluded the population
is 8, so the published boundary would be the 5th of 8. It happens not to change any conclusion
above, and it is named here so that whoever repairs the null handling does not inherit it
silently.

**What this adds to "what would close it".** Item 1 (decide what the aggregates do with a null)
and item 2 (close the class, R10) stand unchanged. Item 3's mutation is now **executed and
failing** on today's code, so it is available as the falsifier a repair discharges against
rather than as a proposal — and the repair must move `_section_customer_strategic_value`'s
rendered board line, not merely a median, because that line is what a reader acts on.

---

## REPAIRED 2026-08-18 (worker tick, RUNG-1c BLOCKING draw, lane D_billing_metering)

Everything below is `observed-with-evidence` (R9), measured on the tree of this tick.

**Item 1 — what the aggregates do with a null: EXCLUDE, and publish the exclusion.**
`saas/reporting/annual_report.py::_section_customer_strategic_value` now partitions the book into
accounts that carry BOTH a CLV and a churn probability (placeable) and everything else. Boundaries
are medians over the placeable population only. The unplaced accounts are still listed, in their
own "Not placed" section, showing `—` and the reason — silently dropping a blank is the mirror
defect of silently zeroing it, and this document said so.

The rule is applied to churn as well as to CLV, and to `expected_lifetime_periods` in the render,
because the class does not care which field the blank arrived on. Five accounts were being
published as lasting "0.0 periods".

**The board instruction moved, which is the point.** `docs/reports/ANNUAL_REPORT.md` regenerated:

    Median CLV:    £791.98      ->  £19,860.04
    Median churn:  29%          ->  32%
    Board action:  CRITICAL quadrant has 5 account(s)  ->  1 account(s)
    C2, C8:        CRITICAL (priority intervention)    ->  EXIT
    Total portfolio CLV: £1,283,652.65 (UNCHANGED -- the sum was always the harmless case)

C2 and C8 are out of the retention-offer recommendation they only ever reached because five
manufactured zeros sat beneath them in the sort. Regeneration blast radius, checked rather than
assumed: `diff` of the committed report against the regenerated one is this section and the
scenario-metadata timestamp, nothing else.

**The even-n median is fixed in the same pass**, as this document asked. `clvs[n // 2]` is the
upper of the two middle values; `_median` now averages them. On the 8-account valued book the two
differ by £18,395.57, and this figure is a quadrant boundary, so the difference places accounts.

**Item 3 — R15, the falsifier this document proposed, now GREEN and it was RED.**
`test_strategic_value_matrix_r15_the_null_zero_distinction_survives_to_the_render` runs exactly the
proposed mutation: swap the nulls to explicit `0.0` and the render must move. On the shipped code
the two were byte-identical (sha256[:12] `d997858d414a` both ways). They now differ, and the
`0.0` book correctly reports a population of 13 of 13 — a genuinely worth-nothing account is IN
the population, a not-applicable one is not. That is the distinction `build_clv` and
`_round_or_none` exist to preserve, finally reaching the aggregation site.

**Item 2 — R10, the CLASS is closed, not the seven lines.** `tools/structural_blank_guard.py`
AST-walks company/, saas/, sim/, simulation/, tools/, background/ and interface/ for a
deliberately-null field given a numeric fallback at its read site. Three arms: `or 0`,
`.get(k, 0)`, `x["k"] or 0`. Proven on the real historical source — run over
`git show 9718066ce:saas/reporting/annual_report.py` it returns exactly the seven violations this
document enumerated by line, and it is clean on the repair. 23 tests in
`tests/tools/test_structural_blank_guard.py`, including fail-closed rc=2 paths for a missing
producer, a producer that stopped calling `_round_or_none`, a missing package, an empty field set
and an unparseable module.

Two things that make it a control rather than theatre:

* **The field registry is DERIVED, not declared twice.** `NULLABLE_FIELDS` is checked against the
  AST of `tools/generate_customer_data.py` — every key handed to `_round_or_none` and every
  keyword it is bound to. A registry that rots behind the producer passes silently; this one reds.
* **It is in `CONTROL_TESTS`, so it runs on every code commit.** Measured, not assumed: a
  brand-new module under `company/` selects it, whereas name-stem selection would only ever have
  fired it when the guard itself was edited. Both shipped instances lived in modules whose own
  stem-selected tests do not run it. ~3.8s.

**A second instance found and fixed, and sized DOWN rather than up.**
`tools/generate_shadow_html.py:575` carried `s.get("clv_gbp", 0)` one line above a line that
already handled `latest_churn_probability` correctly. It is the same class and it is now fixed,
but it was **LATENT, not live**: `d.get(k, 0)` substitutes only when the KEY IS ABSENT, and a key
present with `None` returns `None`. All 11 of the 19 sampled customers with `clv_gbp: null` have
the key, so they already reached `_gbp(None)` and already rendered `—`. Verified at the rendered
value both ways: the C1/C3/C5 rows in `site/shadow/customers/index.html` are byte-identical before
and after. **This repair moved no published pixel and is not claimed to have.** It is still the
defect — `s` is `sample_custs.get(cid, {})`, so the empty-record path is reachable — but its
triggering population is empty today (19 of 19 lifetime accounts present in the sample).

An earlier draft of this note asserted "11 of 19 rendered as £0.00". That was wrong: it read
`.get(k, 0)` as firing on a null value. The two spellings of this defect do not fire on the same
condition, and the guard's docstring now records the distinction so the next reader does not
repeat it.

**Ratcheted, named, and measured — not filtered away.** Two sites match the shape and are not this
defect: `company/analytics/counterfactual_retention.py` and `tools/generate_dashboard_data.py`
read `churn_probability` off a `customer_events` record, which is the WORLD's per-event churn
draw, a name collision with the company's nullable per-account estimate. Measured on
`run_output_latest.json`: 58 events, 0 null and 0 missing. They are in `KNOWN_NON_DEFECTS` with
that measurement, and `test_the_ratchet_has_no_stale_entries` fails if either stops matching, so
the list can only shrink.

**What this repair does NOT close, stated so the silence is not read as coverage.** The guard is a
SHAPE check at the READ SITE. A null that reaches a local by some other route and is then used in
arithmetic is out of scope, as is any nullable field outside the four `_round_or_none` publishes.
Both are wider classes; neither has a measured instance, and neither is claimed to be covered.

**The class has a JAVASCRIPT half, and this guard does not cover it.** `SITE2_two_sided_wall_
exhibit` independently found and repaired the render instances on the site exhibit —
`(d.expected_lifetime_periods||0).toFixed(1)` printing "0.0 yrs", `d.churn_probability||0`
printing "0%" under a green "Low risk" caption, and `combinedTotals().clv` summing two legs with
`(e?e.clv_gbp:0)+(g?g.clv_gbp:0)` where `null+null===0` in JS, publishing "Combined CLV £0". Its
own record names this finding as the Python half. `tools/structural_blank_guard.py` walks `.py`
files only, so the JS shape is NOT mechanised by it and is not claimed to be; SITE2's repair is an
instance fix on that side. Extending the guard to the site's inline JS is the obvious next step
and is left as a named gap rather than an implied one.

**Where this document now lives.** Archived to `docs/staging/done/`. `docs/design/simplifications/
EP1_clv_three_horizon.yaml` (pass 6) cites it at its old staging-root path, which is now dead —
the known archiving-breaks-atom-evidence class, not repaired here because appending to EP1's store
would force a shared maturity-map edit in the same commit while that atom is mid-pass in another
lane.
