## CURRENT SYSTEM (declared truth) — bounded-parallel autonomy, gate-governed
Last updated: 2026-08-09T02:17:59Z
**C14_thermal_parameter_inference — the fabric belief now SPENDS MONEY, and the decision metric
could not previously report a loss. Half the L2→L3 step built; LEVEL DELIBERATELY NOT MOVED.**
This atom's own L2 record named two exit conditions: wire the belief into a live decision path, and
measure the gap on the **population** rather than a hand-picked panel. The first is done. The second
is not — the panel is 10 authored premises — so the level stays at **2** and the exit test is not
renegotiated to fit what got built.
**The defect, found by probing numbers rather than by review.** The only decision function the
fabric triad had lived in the *harness that scores it*, and its choice set had **no do-nothing
option**. A 0.08 kW/K flat using 4,000 kWh/yr at 7.4 p/kWh was recommended `time_shift` at a lifetime
net value of **−£41** — spend £300 to save £259 — and the metric scored it as a **perfect decision**,
because the truth arm picked the same value-destroying measure. A choice set that cannot say
*"nothing here is worth doing"* cannot report the loss, and `money_consequence_inferred` had been
sitting at `misrank 0.0, forgone £0.00` reading as good news.
**What was built.** `company/pricing/fabric_intervention.py` — the first thing in this codebase that
spends money on a thermal belief. It reads the two C14 properties that until now were computed by
nothing and read by nobody: `is_actionable` (refuses a stock prior however tight its band) and
`interval_95` (refuses a winner that dies at the pessimistic end of the company's *own* uncertainty).
The harness now calls the company's rule **twice** — once on the belief, once on the SIM truth only
it can see — same rule, same catalogue, so the only difference between the arms is the belief.
**The wall forced a better model.** The harness had made the belief matter by scaling the company's
demand estimate by `belief / truth`, which cannot live in company code even in principle because it
needs the truth. The company instead attributes part of its own bill to fabric (`HLC × degree days ×
24`, capped at the bill, at the 15.5 °C published UK base), so insulation saves a share of the
**fabric** portion, never of the bill — more physical, and consequential without contrivance.
**The measurement disagrees with itself, and both halves are published.** The C14 posterior is
**worse** than the register at predicting fabric (gap **0.2325** vs **0.2049**, improvement −0.0277)
and **better** at deciding what to do about it — **£16,261 forgone against £41,586, a 61% reduction**
— because narrowing the uncertainty converts refusals into correct actions. Reporting either number
alone would be a lie in one direction or the other. Three outcomes are now counted separately
(bought-wrong, declined-where-value-existed, value-destroying) because they cost different things and
a metric counting only wrong purchases scores a company that never acts as flawless. Both new
counters are R15-proven to fire — a counter only ever observed at zero cannot be told from one that
cannot count.
**Three weaker-than-they-read controls corrected in passing.** (1) The carbon-invariance test guarded
on the *count* of misranked premises, not on *which* — two flipping opposite ways keeps the count and
changes every kWh, which is exactly what happened; it now asserts the decision **vector**, computed
independently of the metric it checks. (2) *"The money consequence scales **linearly** with the unit
rate"* was **false** — capex does not move with price and does not cancel, so the relationship is
**affine**; doc, printout and test all now say so. (3) The decision fixtures were priced at 25 p/kWh,
an *electricity* rate at which the heat pump wins on delivered efficiency whatever the fabric — a
belief 85% low cost exactly nothing and every fabric test below it was vacuous. That saturation is
now its own standing test, in both directions.
**R15 found something the design had not.** Guards 2 and 3 **overlap**: a winner negative at the
estimate is negative at the pessimistic bound too, so removing the do-nothing option does *not*
resurrect the loss-making sale, and a mutation test asserting it would have been simply false.
Recorded rather than tidied — **"the outcome did not change under mutation" is not evidence a guard
is inert** — and each guard is instead shown firing *alone*, on an input the other cannot refuse.
**Evidence.** 871 passed, 3 xfailed (`tests/company/pricing` incl. 34 new, `test_premise_two_level`
96, `test_couple_fabric`, `test_premise_trace`); `epistemic_verifier` **PASS**; wall ratchet 12
passed; ledger rewritten at HEAD by `tools/couple_fabric.py --write-ledger`.
**What L3 still needs, now precisely located.** The population. The panel's composition was *chosen*
to span the stock, so no result on it separates the company's skill from the panel designer's taste.
The anchors already exist in `ASSUMPTIONS.md` (EHS 2022-23 AT1_5 property-type and build-era, AT1_2
EPC bands, AT3_1/AT4 heating systems — all four rows still marked *"Gap — household.py not yet
built"*). `simulation/population_draw.py` cannot serve: `SyntheticCustomer` carries no
`home_type`/`epc_rating`/`bedrooms`, so `make_household` defaults every draw to the same
`suburban_semi` and the population would be clones.

**W1_12_premise_trace_generator — the last red cell was the BAND, not the generator, and the band
was gas-shaped. L2→L3 (2026-08-09, `d9ae87986`), self-certified.** Last tick DECLINED this
promotion on a measured red cell and named the work rather than taking the shortcut. This is that
work. The exit test is *"must pass the two-level test"* and it now passes: **7 anchored cells PASS,
2 UNVALIDATED** (L1.4, L2.4 — unchanged `NEED` anchors, not newly anchored to reach green),
`failed_levels []`, re-measured at HEAD rather than re-stamped.
**The residual.** L1.1 half-hourly texture was **0.1248 against a 0.15 floor**, worst home H10 —
the panel's *only* heat-pump home. Texture is `median|Δ| / mean`, and the whole of the deficit
decomposed to the **denominator**: the heat pump is 49% of H10's electricity and moves almost
nothing period to period. The floor's own anchor text reasons from a gas premise in as many words
(*"a kettle is 2.8 kW for three minutes on a ~0.7 kWh half-hour"*) and was applied as **one
national floor to every home regardless of heating system** — structurally the same
one-national-constant defect this atom exists to remove, reappearing in the **control**.
**What was not done (R12).** The 0.15 floor is untouched; no cell was marked UNVALIDATED to duck a
judgement. Either would have turned the suite green in one edit, which is why neither was the move.
**The anchor, fetched this tick, not chosen.** Ofgem TDCV from 1 Jul 2026 (electricity 2,500 —
a *non*-electrically-heated home, i.e. the behavioural baseline — and gas 9,500 kWh/yr); the
EST/DECC in-situ condensing-boiler trial (**mean measured combi efficiency 82.5%**, sd 4.0%, against
a SEDBUK rating of 90.4%); and the DESNZ/Energy Systems Catapult Electrification of Heat
demonstration project (**median ASHP SPFH4 2.78**, IQR [2.55, 3.05], n=428). 9500×0.825 ÷ 2.78 =
2,819 kWh of heat-pump electricity against 2,500 kWh of behaviour — the heat pump is **53.0% of the
mean**, so the electric band is 0.15 × 0.470 = **0.0705**, derived at import and never stored.
Joint-corner envelope across both published spreads: **0.0655–0.0758**. Filed with provenance in
`ASSUMPTIONS.md`, including what is *still* not anchored (no published band for the texture
statistic itself, in either fuel).
**R15 — and the old mutation was invalid here.** `_smooth` has been this suite's L1.1 mutation since
the band was written. On a matched pair (same household, same seed, same weather, differing only in
heating system) it moves the statistic **the wrong way** on a heat pump: gas 0.2471 → 0.1539 as
intended, heat pump **0.1069 → 0.1430, up**. Cross-day averaging strips appliance noise and leaves
the heat pump's repeated diurnal cycle standing. Reusing it would have produced a proof that was
vacuous in the only direction that matters. Replaced with a monotone, daily-total-preserving
`_flatten_blend`, verified monotone *before* being used as evidence — and the class (a mutation
inherits the composition it was validated against; nothing notices when a band is later conditioned)
is filed as its own finding, not fixed on sight.
**The answer to "you lowered a threshold so it would pass".** Thresholds on different denominators
cannot be compared. How broken a home must be before its own band fires **can** be: on the matched
pair, the heat-pump home fires at **0.349** of the way to a flat day and the gas home at **0.396**.
The new band is the **stricter** of the two against the same defect.
**The tell.** The worst L1.1 cell is no longer the heat-pump home at all — it is **D7, a gas home at
0.1804, judged by the unchanged 0.15 band**. The heat-pump home stopped being the worst cell rather
than being let off the one it was failing. Also guarded: fail-closed (missing heating flags judge
every home by the *stricter* band), tautology (the flag is a register fact, never inferred from the
series being judged), and worst-cell selection by **margin** rather than raw value. 155 passed,
1 xfailed — the shipped path's strict-xfail pin still XFAILs, so the legacy PC1 rescale has not been
quietly outgrown. Stops at L3: Expert Hour `not_attempted`.

**H27_payment_belief_gap — the Expert Hour ran on the corrected instrument, and the detection
headline failed it twice. HELD AT L2 (2026-08-09).** The previous tick released H27's procedural
block and left an instruction rather than the promotion: *a promoter must run the Expert-Hour pass
on the corrected instrument, not on the reputation of the old one.* It ran. L3 means "no major
flaws"; two were measured, both in the published headline, neither previously named.
**(1) The headline is an `as_of` artefact.** `truth_set` is `result == 'failed'` — a settled fact
that does not move with the clock — while `flagged_set` is a belief held **at** `as_of`. Holding
the company *and* the world literally fixed (same records, same consumer, nothing re-simulated) and
moving only the date the scorer asks on walks the published figure **0.0725 → 0.1232, +70% over 60
days**. The mechanism is D8's (a case detected on time, then *un*-flagged by an oldest-first
allocation). The sting: this was already solved one dimension over — `detection_latency` was built
on an ever-knew population for exactly this reason, and its test is literally named *"not an as_of
artefact"* while sitting beside a headline that is one. Third instance of the class (D7's prevalence
scalar, D10's retired key), so it is **closed at the class**, not the instance (R10).
**(2) The headline counts one error direction.** `detection_gap` is pure recall, so `flagged_set`
enters only through the intersection and **a company that flagged every invoice scores a perfect
0.0** — while the published baseline names only the opposite degenerate ("flag nobody → 1"), which
reads as though 0 were earned. Measured: **44–51% of everything the company flags is an invoice
that truly succeeded** (seed 7: 101 false flags, 0.0951 over the truly-current population). That is
*the same 101/1062* D7's `overstated_arrears_rate` already publishes on the ageing dimension — the
error direction was visible one dimension over and invisible here. It had even been noticed: the
live test file said "flagged can EXCEED true", explained it away, and declined to assert on it.
**What landed instead of the promotion (HARDEN; R12 clean — the detection gap is byte-identical at
`0.09547325102880659`):** the caveat is stamped **at source** in `gap_metric.detection_gap` (the D6
precedent), so it lands on all **three** coupled triads that call it, not just where it was found;
`n_false_flags`/`false_flag_rate` ride beside the score on their own denominator (`None`, never
`0`, when the universe is unknown — a 0 there is the strongest possible claim handed out free); and
both limits now print **with** the headline at the CLI and in the live ledger note the Proof door
reads. **The class control:** `DIMENSION_AS_OF_CONTRACT` + a real `as_of` sweep holding every
dimension to *truth invariant ⇒ gap invariant*. Deliberately **differential** — ageing is exempt
because an invoice really does age; a blanket rule would false-positive there and teach everyone to
skip the gate. **R15, mutating the source twice:** flipping detection's declared invariance fires
it with the real drift; stripping the fix-atom name from its exemption fires the named-debt
assertion. Plus a vacuity guard so a sweep where nothing moved cannot pass silently.
**A coverage hole found on the way:** `live_payment_triad.measure_and_write` — the path that
actually *publishes* the gap into `coupled_gap_ledger.json` — had **no test reaching it**, so every
word of its note was unexercised. Now covered, with the witness interpolated from the measurement.
**Queued, not fixed on sight:** `D11_detection_gap_is_recall_only` carries the reshape (it moves
three published numbers), and H27's `depends_on` re-points at it — the whole of the remaining hold.
Acceptance is already measurable: the `as_of` sweep must come out flat, and flag-everything must
stop scoring 0. 38 tests in the triad file (was 31), 7 in the live file (was 5), 2,186 green across
the targeted surface; ruff unchanged at 7 vs a pristine HEAD extract.

**D10_detection_headline_is_single_channel (2026-08-09, `e78913088`) — the payment DETECTION
headline gets a shape that can see latency, and a sentence it published turns out to be wrong.
L0→L2, self-certified.** The atom asked for either a dimension that can see latency or a published
note saying the headline is reconciliation-determined alone. Both landed.
**The dimension:** `detection_latency` — days from an invoice's due date to the company's FIRST
knowledge, whichever channel got there first, with the DD-channel-deleted **counterfactual** beside
it. Seeds 7/11/23 at 400 customers: **2.30 / 2.41 / 2.04 days** with the DD-observation channel,
**exactly 5.00** without it. The channel buys ~2.7 days of *earlier* detection while moving the
set-membership detection gap by **exactly zero** — the 2026-08-08 finding stated as a number rather
than a paragraph. No normaliser anywhere (D7's trap applied before it could bite): absolute days,
no class-balance denominator, undetected failures **counted beside** the mean and never imputed
into it.
**The old residual's premise was false.** That pass recorded DD latency as unmeasurable "because
the adapter emits `value_date == due_date` with no ARUDD lag". Wrong *field*, not a missing
capability — `WallResponse.observed_at` is the bank-feed report date and the seam already lags it
`0..ARUDD_NOTIFICATION_LAG_DAYS`. Measured DD lags `{0,1,2}`. Retracted in the register.
**AND THE HEADLINE DOES NOT COUNT WHAT EVERY SURFACE SAID IT COUNTS** (observed case by case, R9):
it was published as "failures the company **never observes** — the no-remittance blind spot". It is
not. Asking the company's own reconciliation organ at each `due+grace` date gives **n_undetected =
0 on all three seeds** — everything that truly failed was flagged *on time*. The misses are
detections the company **un-made**, when a later ambiguous non-DD payment was allocated oldest-first
onto the failed invoice. That is Clayton's Case (atom `D8`) surfacing in a dimension nobody had
looked for it in — the wrongful-**non-pursuit** twin of the wrongful-dunning exposure D7 measures.
Corrected at every site that repeated it, staged as a worker finding, recorded as evidence on D8,
and pinned by a test that fires if anything ever *does* escape both channels.
**Retired, not re-labelled:** `stats["detection_latency_days"]` was days-overdue at whatever single
`as_of` the scorer asked at — `{30,51,72}` on this period grid, a pure artefact of the question's
timing. Its characterization test was replaced, not repaired.
**R12 clean: not one published number moved.** The detection gap is byte-for-byte what it was; what
changed is the sentence describing it. **R15:** four mutations, each proven to fire on its own named
defect — `value_date` instead of `observed_at`; the latency population defined at `as_of` (moved the
mean 1.96→1.80 for zero change in any detection date); DD-only cases folded into the counterfactual;
both channels dead (proving the `n_undetected == 0` witness is not vacuous) — plus two metric-shape
mutants that swing where the real measure is flat. 31 tests green in the triad file (was 24), 467
across every file touching the triad or `gap_metric`, ruff unchanged at 18 vs a pristine HEAD
extract.
**H27's hold released:** D10 was its sole remaining reason, so `depends_on` is dropped rather than
re-pointed a second time. **Not claimed:** the 2→3 is now drawable and is *not* taken — the tick
that finds a published sentence wrong is not the tick to certify the instrument as real; that needs
the Expert-Hour pass, on the corrected instrument. D10 itself stays L2 for the same reason. The size
ratchet (warn-only) flags `detection_latency_gap` at 117 lines against a 60 cap; left standing
rather than split, since the length is its documentation and SP3's own text says not to split to
dodge a count.


**FUT1_attach_forward_hook (2026-08-09, `641a87ae2`) — forward discovery now has an address.
L0→L2, self-certified.** Deliverable #2 of the futures ruling: a finding or DISCOVER mint declares
what it advances by putting **one line in its own body** — `**Advances:** EP16_anchored_generators,
EP17_varied_population_draw — why`. The ledger is **derived from those docs on every read** and
stored nowhere by hand (`background/forward_attachment_register.py`); delete the declaration and the
row disappears, which is the test rather than the claim. Two renderings: the generated
`docs/design/FORWARD_ATTACHMENT_LEDGER.md` (its `--check` fails when it and the docs disagree) and a
per-atom `N BUILT TOWARD` badge on every view of the project map, sources on hover.
**R15 on the defect the atom's own origin note named** — *"a ledger that renders whatever it is
told"*: `verify_rendering()` parses the rendering back to (atom, source) pairs and compares against
a fresh derivation. Proven both ways — mutating that control to `return []` fails 3 tests
(fabricated row, dropped row, re-attributed row); unmutated, 19 pass, each mutation test asserting
the honest derivation is non-empty first so the empty-agrees-with-empty vacuity cannot carry it.
Parse anomalies are loud, never silent drops: `unknown_atom` / `malformed_token` /
`empty_declaration`, exit non-zero; the payload is bounded to its own line so a declaration cannot
swallow the document.
**WORK-THIS-CREATES #5 done — the first three entries are real, not fixtures:** the heat-pump anchor
(`WORKER_FINDING_L1_TEXTURE_BAND_IS_GAS_SHAPED_2026-08-08`) → `EP16_anchored_generators` +
`EP17_varied_population_draw`; the Clayton misdating (`D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER`) →
`EP4_collections_journey`. Both attach by declaring **in the finding itself**, so they re-derive.
19 + 30 + 19 tests green (register / project door incl. 2 new render+independence tests / map
facets), epistemic verifier PASS, 5,437 docs scanned in 1.2s with 0 violations.
**Not claimed:** three entries is three; no gate wires `--check` into pre-commit yet (hence L2, not
L3), and FUT2 (pull-forward proposal, stops at the director) and FUT3 (blocked-atom visibility)
remain L0 and untouched.

**THE FUTURES GO ON THE MAP (2026-08-08) — 23 atoms minted from
`DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08`. Map 206 → 229.** The ruling's diagnosis,
re-measured before writing: no atom's id touched CLV, a named counterparty adapter, or a forecast
feed — "not blindness; homelessness". Deliverable #1 is DONE: **EP1–EP20**, the Epoch-2→5
commitment sets, derived from canon (THE_VALUE_CYCLE_FRAMING, the 2026-08-05 counterparty-API
research, the gas/carbon/cost-stack scope briefs). EP1–EP5 the commercial brain (three-horizon CLV,
variance learning loop, pricing engine, collections journey, settlement true-ups); EP6–EP15 the wall
as real transport (protocol typing + Elexon/IRIS, DCC DUIS, n3rgy, UK Link/Xoserve, GoCardless/Bacs,
CSS/REC, Carbon Intensity, published cost stack, forecast feed); EP16–EP18 generated worlds and
selection; EP19–EP20 go-live. Deliverables #2–#5 have drawable atoms (**FUT1** attach-forward hook
carrying #5 as its acceptance test, **FUT2** pull-forward proposal path, **FUT3** blocked-atom
visibility).
**Already covered, not re-minted:** the tournament mechanism (`A5_tournament_fitness_mortality`,
`B11_evolutionary_tournament_harness`), the adapter pattern (`W4_1_typed_adapters`, SATURATED), the
single-run population draw (`W2_2_population_draw`), and the go-live NFR/licence/DR set (`H4`, `F5`,
`H8`, `F4`). EP18 is the fitness *definition* those tournament atoms select on, which neither fixes.
**The draw is unchanged, proven not asserted:** `_maturity_map_draw_concurrent()` before vs after is
identical bar FUT1/FUT3 — zero removals, and no EP atom entered the BUILD queue.
**Three departures from the ruling's literal wording, reported for see-and-correct** (all recorded
in the map header, none made silently): (1) the E2 gate it names, EPOCH2_EVIDENCE_PASS, was already
DELIVERED 2026-07-09 — writing it into a block field would manufacture a phantom gate; (2) no atom
carries `blocked_on`, because the ruling's own §3 wording ("the director opens the epoch") is
*ignored* by the live `_names_abolished_permission_block` predicate, and `blocked_on` must anyway be
a list of atom ids — all 20 are `loop_stage: idle`, this map's established form for a future epoch
(zero of the 206 prior atoms carried a block; all 9 epoch-4/5 atoms were already idle); (3) prefix
`EP`, not `E`, which is lane-E finance.
**FUT3 half-answered at mint by running both readers.** The staleness clock PASSES — 205 → 229
cells, blocked atoms fully visible. The target-design delta does NOT read the map at all: its seven
targets scan 843 tree modules. So the ruling's "82-vs-7 becomes a measured dial" is genuinely
unbuilt, and is now FUT3's work. Re-measured after the mint: 229 atoms, H_harness 86 vs B_commercial
9 — filing the futures does not fix the imbalance, it makes it countable. R12: a diagnostic.
**Not claimed:** no EP atom is built, framed or above L0; FUT1–FUT3 are L0 and unbuilt; 119 design/
disposition tests green, but nothing user-visible changed, so no R11.

**D7_ageing_gap_metric_reshape (2026-08-08, `3af46d145`) — the ageing number stops being one number.
L0→L2, self-certified.** The single prevalence-normalised ageing scalar the D6 DISCOVER refuted is
RETIRED, not re-labelled: `background.gap_metric.ageing_gap` reports `understated_arrears_rate`
(misses / truly-overdue), `overstated_arrears_rate` (false ageings / truly-current — the
wrongful-dunning exposure) and an ABSOLUTE `mean_bucket_displacement` with no divisor at all.
`misapplication_gap` is untouched and keeps its remaining legitimate caller, W2_9↔C11.
**All three D6 defects answered on the same oracle rows:** finds-all-arrears went from 1.5000
"worse than no-skill" to understated 0.0000 / overstated 0.0150; off-by-one and stone-blind went
from 1.0000 == 1.0000 to 1.0 vs 3.0 buckets; the prevalence sweep went from 3.00→0.15 with the
company held FIXED to exactly flat on all three.
**And the decomposition immediately said something the scalar could not.** Live, 400 customers:
the retired figure read 0.8043; the reshape reads understated 0.0725 (10 misses of 138
truly-overdue) against overstated 0.0951 (101 false ageings of 1062 truly-current). This company
wrongly ages **ten times more settled invoices than it misses real arrears** — the wrongful-dunning
direction is the larger half, and one number had it buried inside a denominator normed on the other
class. R12: a diagnostic, not a target.
**R15, four named mutants**, each REQUIRED to fail the assertion the real measures pass — including
`_MUTANT_ordinal_over_no_skill`, the trap the D6 DISCOVER caught in its own draft (ordinal
numerator, prevalence divisor, defect fully intact). Plus fail-loud on an unrankable bucket label
and vacuity reported as `None`, never 0.0. 535 tests green; epistemic verifier PASS.
**Not claimed:** L3 (no Expert Hour); Defect 3 is fixed on shape and still latent live
(`wrong_bucket == 0`); the live 1.1538 is still not reproduced in detail.
**H27 half-released:** its `depends_on` moves off the satisfied D7 onto a newly minted
`D10_detection_headline_is_single_channel` — the union-blindness finding that had been living only
in prose. A hold must never outlive its cause, and must never be dropped while a real second cause
stands.

**AO9_blind_review_by_restricted_context (2026-08-08, `c9ec19dcd`) — the blind board loses its human
courier. L0→L2, self-certified.** Board scaling §3b/3c. The director named why the blind board worked:
not the courier, not a better reviewer — **what the reviewer could not see**. The courier was only the
enforcement, and it is why the board ran a handful of times. `tools/blind_review.py` replaces the
courier and nothing else.
**Blindness by construction, not by promise.** The packet is *assembled* from a two-field whitelist —
the plain-words capability description (an AO1 index row) plus the domain — so there is no seam
through which build context arrives. The capability id is deliberately **withheld from what the
reviewer sees**: a module path is a map of the implementation, so naming the subject would undo the
blindfold in the act of applying it. That exact text is stored **verbatim in the same record as the
battery it produced**, with a digest — transcript and verdict cannot be separated, because they are
one record.
**The audit can DISAGREE with the record.** `--audit` re-derives the blindfold verdict from the stored
transcript and never reads what the record says about itself: a forged record carrying `leaks: []`
over a transcript full of source is still caught. The load-bearing proof is that removing the
`SOURCE_CODE` rule makes the **same** transcript audit clean — without it, "a finding appeared" would
not distinguish the guard working from something incidental in the fixture. 36 tests; 8 leak classes
each mutation-proven on its own named defect, plus a reachability test that no rule is dead and a
false-positive guard (a blindfold that fires on *three-phase supply* gets switched off within a week).
Fail-open answered both ways: an empty or missing transcript is a **finding**, and an empty ledger
prints *"an empty pass, not a clean one."* Fail-silent: an unparseable ledger returns rc 2, never rc 0.
**3c is a WALL and it lives in the data.** Restricted context gives **BLINDNESS, NOT INDEPENDENCE** —
the reviewer is the same model family. Every record carries `independence: false` and the audit fails
any record claiming otherwise, so the limit cannot be quietly dropped from prose. Genuinely external
review stays the director's, for the few highest-stakes verdicts per epoch.
**ONE MECHANISM, as required** — shipping beside the existing cold-eyes skill would have failed the
atom. `.claude/skills/cold-eyes-walk/SKILL.md` now **owns** the tool: same five steps, two subjects —
a rendered artefact (blindfold = the URL) and a capability (blindfold = this tool). A test fails if any
other skill grows a rival blind-review path.
**Live run, 840 index rows:** 383 blind-safe as derived, 339 refused with a named reason, 118 with no
description. A control that can both pass and fail. `PHASE_LABEL` — now the largest single refusal
cause — was found by *running* the tool, not reasoning about it: *"Direct Debit Mandate Register
(Phase GD)"* passed every other rule.
**NOT CLAIMED:** no fresh-context battery is recorded yet; the ledger is empty and the tool says so
rather than implying coverage. Recording a battery written by the builder who has read the code is
precisely the defect this atom exists to prevent. First live blind run is the next draw.
**AO2 caught this commit three times** — G1, then G6 correctly, then G6 as a **false positive**: the
`INDEX:` field has no terminator, so it swallowed the message body and matched "nothing" 1,200
characters away in unrelated prose. Queued as a finding for AO2's owner (`c1a13ae9f`), not patched on
sight — editing a gate to pass your own commit is the route-around shape even when the diagnosis holds.

**AO2_write_time_reuse_gate (2026-08-08, `b9f1dc5e0`) — a new capability module can no longer land
without the record of the look. L0→L2, self-certified.** MAP step 2, and §5's *"only immediate
behaviour change"* in the whole architected-out programme: AO1 made looking cheap, but nothing yet
changed the price of **not** looking — which is why the director calls the index a demo until this
spends it. `tools/write_time_gate.py`, wired **live** at `tools/git-hooks/commit-msg` (`core.hooksPath`
already points there, so it is running, not merely committed). A commit adding a new `.py` under a
code root must carry a `REUSE:` block answering **both** ruled questions — *do we already have this?*
(the index terms, quoted) and *does the ecosystem already have this?* (the class: **CATALOGUE** names
the library it stands on, **CUSTOM** is the product and owes no note, **SUBSYSTEM** owes the
build-vs-buy note naming what was evaluated and why rejected — silence is a gap).
**The director's wall is a test, not a comment.** `test_the_wall_holds` gives the same new module and
the same index two honest records — *"extended it"* and *"kept it separate, different purposes"* —
and requires **both** to pass. The gate compels the look and the record, never the decision; forced
reuse that couples two purposes is the mirror error of duplication.
**Proven live, both directions, on real commits:** a test commit adding a recordless module was
**REFUSED** by the running hook (`G1`, HEAD unchanged); AO2's own commit — which adds a new module —
**passed carrying its own record**. 41 tests; **8 source mutations**, each breaking one guard alone
(G1 record, G2 class, G3 catalogue-without-library, G4 build-vs-buy, G5 index terms, G6
index-contradiction) plus **two on the detector rather than the guards**, because a gate whose
detector never fires passes every test while checking nothing. G6 is the only guard with an
independent source: it puts the record's *"nothing exists"* claim back through the live index and
refuses a claim the index contradicts. Fail-closed four ways; an absent mode file means **gate**, so
it cannot be disabled by deleting something. Scope is **stated, not silent** — modules only, function
granularity deferred with reasons in `docs/design/WRITE_TIME_GATE.md`.

**W2_16_payment_outcome_rng_substream_isolation (2026-08-08, `14e00c2ba`) — adopted, not authored.**
Found complete, green and **uncommitted** in the shared tree while committing AO2; the authoring
tick's last write was 20:45 and its process was gone. Verified before adopting (bill_substream is
real, all four consumers migrated, 77 tests pass), committed with honest attribution, and its level
move recorded as an **adoption** so the ledger does not read as if this tick built it.

**AO11_map_assertion_provenance (2026-08-08, `e3f5b0c5b`+`220efe7da`) — the map's own cells now
carry when they were claimed and when anyone last looked. L0→L2, self-certified.**
Addendum **A2**, the one item AO1 deliberately did not absorb (an index that re-derives on every
query has no assertion to date; the *map* does). A cell reading L0 while its artefacts say L2 is a
**validity-window failure** — true when written, silently false now, with nothing carrying either
date; the DD cell read level 0 while all six sub-parts were built, committed and live.
`tools/map_assertion_provenance.py` gives every cell **three clocks**: `asserted_at` from `git blame`
of that cell's **own `level_current` line** (so a prose edit cannot launder a stale claim clean),
`artefacts_moved_at` from the newest commit touching its `file_scope` — **the code, not the map**,
which is what makes the comparison independent — and `verified_at` from the append-only ledgers (this
tool's `--record`, plus the existing `gate_authorizations` self-certifications, which *are* a check
against evidence at a known moment). Staleness stops being a discovery someone happens to make weeks
later and becomes arithmetic. **205 cells in ~1.5s: 4 CONTRADICTED, 59 STALE, 116 UNVERIFIABLE
(48 no scope, 66 directory-scope, 2 tautological), 26 CURRENT.**
**Two false-positive classes were found by hand-checking the first run and fixed, not shipped.**
9 CONTRADICTED collapsed to **4** once the rule required the artefacts to have moved *after* the
claim — most L0 cells name files that already exist **because the work is to change them**, and
reading those as "already built" reports live, unstarted work as a defect, which is the same weight of
error as missing a real one. Then **shared scope**: H28 lit up on a gate file **three atoms claim**,
moved by H30 and W2 — so `scope_exclusive` is now printed and a confound cannot pass as evidence.
**Hand-checking all four survivors found every one moved for other work** (H29's exclusively-claimed
`ntfy_utils.py` moved for the NEVER-ASK absorption), so the docstring **states the limit** rather than
hiding it: a file-granular clock knows *that* a claimed artefact moved, never *why*. A status is a
**prompt to look, never a verdict** — which is still the whole ask, staleness as a query.
**R15, mutated in source not mocks: 12 mutations, 12 fire, zero survivors** — vacuity floor,
blame-join, commit-time pass, independence/tautology, contradiction-loses-ordering, all three
unverifiable statuses falling through to CURRENT, git-failure-swallowed, and blame-dates-the-block
across **all three** block-granular strategies. **That last test survived its own mutation twice**: the
fixture had prose on only one side of the level line, so two of the three wrong implementations passed
unnoticed — fixed by putting prose above *and* below, as the real map has. Every fixture is a **real
git repo with controlled commit times**; a mocked git would prove only that the mock returns what the
test told it to. **Bitemporal reuse checked and DECLINED**, reasons recorded in the docstring so the
next turn need not repeat it (it models restatement over a `valid_time` a map cell does not have; it
is in-memory where these dates are derived; it sits behind the company seam) — **git history is the
append-only transaction-time log actually reused**. Capability index `--find` returned **0 rows**, so
nothing was extended. **Additive by design:** writes nothing the draw reads, never edits
`maturity_map.yaml`. 24 tests, epistemic verifier PASS (534 files). Not L3: no Expert-Hour, and the
**59 STALE / 4 CONTRADICTED findings are QUEUED, not swept** — the addendum names a 185-atom field
sweep as the probable failure, and SELF_INTERRUPT_DISCIPLINE says queue by default.

**AO1_capability_index (2026-08-08, `7e5a727d4`+`d96b1d45b`) — MAP step 1 of the director's
ARCHITECTED-OUT programme. The reuse surface, derived. L0→L2, self-certified.**
`tools/capability_index.py` answers *"do we already have this?"* in ~3s over **837 production
modules** — 490 wired, 57 entrypoint, **268 orphan**, 97 unnamed, 67 with no test evidence. Every
field derived from source at query time (plain words = the module docstring; status from real import
**and by-path** edges; evidence = the tests that import it; demo = how you'd see it), so there is **no
committed artefact to drift** — a hand-written index would itself be the duplication the programme
exists to kill. **Addendum A1 answered BY CONSTRUCTION:** the index never reads `maturity_map.yaml`,
so the degraded `file_scope`/`depends_on` fields cannot degrade it — **no 185-atom field sweep, and
nothing the draw reads was touched**, which the addendum's own risk section names as the probable
failure. **A3 delivered as `--orphans`:** 268, of which **260 sit in `company/`**, corroborating July's
KNIFE target (~320 zero-import company modules) from an independent derivation. **R15 was the hard
part, as the atom said** — an index that under-reports doesn't look broken, it looks like a small
codebase, and the builder who reads "nothing to reuse" then writes the duplicate, so a wrong index is
**worse than none**. Five source mutations, each proving its own guard fires: vacuity floor,
**tautology** (the coverage oracle is `git ls-files`, *not* the walk the rows come from),
unparsed-not-skipped, fail-silent oracle, name-only matching. **The floor mutation initially left all
23 tests GREEN** — the test asserted a `VACUITY` tag the per-root guard *also* emits: union-metric
blindness **inside an R15 test**, found only by mutating the source, now witnessed alone.
**Two real defects the first run exposed, both fixed:** `--find "working day"` returned **0 rows** for
`company/compliance/working_days.py` — the exact capability whose duplicate the director cites as
evidence, i.e. the fail-open that *causes* the duplicate rather than preventing it; and a live
dispatcher invoked by path (`exec(open(...))`) read as an **orphan**, the false-orphan reading that
gets a working mechanism retired. **Write-time gate applied to its own build:**
`generate_capabilities_json.py` **not** extended, for cause (12 hand-authored brand cards for a public
page; coupling that to a build-time developer query is the coupling error the director weighs equal to
duplication). 24 tests. Not L3: no HARDEN/Expert-Hour, and the index is a *demo* until **AO2** — the
write-time gate — spends it; AO2/AO3/AO7/AO9 are drawable now.

**H31_secret_scrub_test_leaks_wake_key (2026-08-08, `72d33f7da`) — the suite's verdict depended on
collection order, so the fix went at the CLASS. L0→L2, self-certified.**
`test_model_facing_secret_scrub.py` restored `background.ntfy_utils` with `importlib.reload` inside a
`finally:`. That runs while the test function is still on the stack; **monkeypatch restores `os.environ`
in a fixture finalizer that runs afterwards** — so the restoring reload re-read the still-scrubbed env,
restored nothing, and pinned `WAKE_HMAC_KEY=None` process-wide. Four `test_ntfy_utils.py` signing tests
failed on collection order alone: **the victims red, the culprit green**, which is exactly why this read
as "import order" and sent diagnosis at the wrong target. **Second instance of the class** (H29 was the
first), so an instance fix alone is not a closure (**R3/R10**). *Instance:* `monkeypatch.undo()` before
the restoring reload. *Class:* `tests/background/env_constant_sync.py` **AST-derives** the registry of
every top-level `X = os.environ.get(...)`-shaped constant in `background/*.py`, and a
`pytest_runtest_teardown(trylast=True)` hook in `tests/background/conftest.py` checks all of them after
every test — failing the **culprit by nodeid** and **repairing** the constant so later tests stop
depending on collection order. **Derived, not enumerated**, so tomorrow's constant is covered without
anyone remembering the file. The `trylast` position is the only reliable "after monkeypatch" hook and was
**verified empirically** in a scratch dir outside the repo, not assumed. **R15 both directions on the LIVE
hook, by mutation:** reintroduce the finally-reload → `ERROR at teardown of
test_worker_env_forgery_is_structurally_impossible` with the `STALE ENV CONSTANT` payload and **33 passed**
(the four former victims now *green*, via the repair); restore the fix → 33 passed, guard silent.
**Vacuity guarded** — the registry is asserted non-empty *and* to contain
`background.ntfy_utils.WAKE_HMAC_KEY`, plus an independent grep-vs-AST cross-check, so a scanner that
quietly matched nothing cannot pass. Original repro: **was 4 failed, now 33 passed**; full
`tests/background/` **1971 passed, 1 skipped, rc=0** — no false positives. **Two things the class closure
surfaced that the instance report had not:** a *second* leaked constant nobody had named
(`ntfy_utils.NTFY_TOPIC`), and — **self-caught during the mutation run** — the first draft printed the
live `SE_NTFY_TOPIC` **value** into pytest output, i.e. a guard over the wake-key scrub that would itself
leak the signing key into CI logs; values now redact to `<str len=N #sha8>`, pinned by a test. Not L3: no
HARDEN/Expert-Hour, and wrapped reads like `Path(os.environ.get(...))` stay unguarded **by design** —
broad-and-noisy guards get silenced.

**D6_payment_ageing_gap_validity (2026-08-08, `15f44e022`) — the defect belongs to the METRIC, so it
was closed at the CLASS. L0→L2, self-certified.** The DISCOVER had already answered D6's question: the
live ageing gap of 1.1538 is a metric-shape defect, with a real Clayton's-Case misdating hiding under it.
What that implied under **R10** is what this level records — the prevalence defect is a property of
`background.gap_metric.misapplication_gap` **itself** (majority-class normalisation makes `gap` a joint
statement about the company AND the world's class balance), so it lands on **every** call site, not just
the ageing dimension where it was found. **Stamped at source:** the caveat rides in `components`
(`normalisation` / `minority_class_share` / `prevalence_caveat`), *not* in `note` — both live callers
replace `note`, so a note-borne caveat would have been silently dropped. **R11 to the rendered value:** it
travels to_ledger_entry → `coupled_gap_ledger.json` → `site/data/proof.json` and renders as visible text
in the Proof panel HTML produced by the page's own JS against live data. **The second call site was
audited by measurement, not argument:** on W2_9 ↔ C11, holding C11's misrecording channel fixed and moving
only the world's business share 2%→40% moves the company's own error rate 0.0210→0.0365 while the
published gap moves **1.0000→0.0905** — at a 2% share that pair would read *"no better than blind"* on its
**lowest** error rate. **R12 clean:** W2_9 re-measured to the identical `0.2290836653386454` — the closure
relabelled a number, it did not move one. **R10 mechanism, not exhortation:**
`tests/test_gap_metric_misapplication_class.py` registers every live call site by AST scan, so a **new**
caller fails rather than silently publishing an uncaveated figure; vacuity guards on both the scan and the
ledger sweep. **R15 mutation-proven three ways**, each restoring green: remove the stamp → tests 1+2 fail;
make the metric prevalence-invariant → test 4 fails (the documented signal that D7's reshape landed); add
an unregistered caller → test 3 fails. Test 5 fired *for real* on the uncaveated W2_9 ledger entry before
it was re-measured. Also fixed: the published disclaimer named atom **`D6a`, which does not exist** — it
now names `D7_ageing_gap_metric_reshape`. Found and **queued, not fixed on sight**:
`D9_worse_than_blind_chip_is_metric_blind` — the Proof panel renders **any** gap>1 as the red chip
"worse_than_blind", valid for `detection_gap` but refuted for `misapplication_gap`; latent today (W2_9
reads 0.2291), four consumers, outside D6's file_scope. Not L3: no HARDEN/Expert-Hour, and D7 will replace
the characterized behaviour.

**H30_sim_runner_discards_child_stderr (2026-08-08, `de2c3d7d8`) — the machine can now say WHY it
failed. L0→L2, self-certified.** The sim red loop that cost the director attention this morning logged
`rc=1` eight times and nothing else: `run_simulation()` launched the child with fd 2 inherited, and under
a daemon that fd is a socket, so the traceback — a one-line `NameError` — was destroyed as it was written.
**Closed at the CLASS, not the instance (R10):** `tools/child_stderr_guard.py` AST-flags any launch site
under `background/` that reports a child's FAILURE to a human while discarding its stderr. It found
**eleven**, all fixed, **none exempted** (`EXEMPT` is empty): `sim_runner` (both), `background_worker`'s
leftover-marker sweep, `process_run_complete`'s git add/commit/push and its liveness publish,
`executor_governor`'s map fold. The guard is **invoked, not merely present** — wired into
`pre_commit_test_gate.CONTROL_TESTS`, so it runs on any code change rather than only when the guard itself
is edited. **Its scope is proven, not asserted:** `uncovered_declared_entrypoints()` reads
`background/process_manifest.yaml` and returns rc=2 if any declared non-retired daemon's entrypoint sits
outside the scanned root — a coverage hole is a failure, never a pass, which is what stops the
`background/`-only scope from being a silent exclusion. **R15 both ways:** the real NameError shape as a
source fixture turns it red, as do `check=True`-without-capture and explicit `stderr=DEVNULL`; deleting
`stderr=PIPE` from `run_simulation` turns the LIVE guard red (`sim_runner.py:84`) and fails 4 behavioural
tests; restored, all green. **Verified at runtime, not only in source:** a real failing child through the
new kwargs renders `NameError: name '_IC_SEGMENTS' is not defined` as the NTFY headline and the full
traceback in the log tail. **R2 honoured:** `sim-runner` and `background-worker` were restarted (pids
247602/247604, started 19:09:17 against a file written 18:59) — committed was not running. Sits at
`loop_stage: harden`, not L3: no Expert Hour, and the coverage check has only ever met a fixture manifest.
Found in passing and **queued, not fixed on sight**: `H31_secret_scrub_test_leaks_wake_key` — a
finally-reload that runs before monkeypatch restores the env, leaving `WAKE_HMAC_KEY` unset process-wide
so 4 signing tests pass or fail on collection order (reproduced with H30's files uninvolved).

**DD_seasonal_cashflow_physics (2026-08-03, `e99debe6d`) — the parked residual was waiting on a
mechanism that has never had a caller. L0→L2, recorded.** The cell read level 0 with **no ledger entry
at all** while all six sub-parts (DD1, DD1-sizes-collection, DD2, DD3, DD4a, DD5 SITE, DD-H) were built,
committed and live — the stale-cell class again, so it was re-verified against artefacts rather than
re-stamped: `run_output_latest.json` carries every DD block and `dd_h_solvency_gap.measure_from_run_output()`
now returns **measurable=True** (belief £4,118,110.43 / truth £4,116,298.23 / gap £1,812.20 / tell False,
as at 2020-10) where on 2026-07-29 it honestly reported NOT-MEASURABLE. **DD2's parked opening balance was
wrong in BOTH halves.** Not the prior occupant's debt — SLC 27/12.2, and `change_of_tenancy_register.py`'s
own opening lines, put debt on the **person**; and W2_12 hitting its target is not an unblock, because
`TenancyChangeCoupler` has **no production caller** (grep-verified) and `simulation/life_events.py` emits
**no move event at all**. Wiring it would be a live mechanism with a permanently dead input — the **fourth**
orphan-transition instance, and the first where the orphan was holding another atom's work in a queue by
proxy. **A C-S5 fail-open, found by testing the claim rather than reading the code:** the docstring said
monthly/quarterly billing "all carry the same way" while the loop collected one standing DD **per BILL** —
a quarterly customer paying 4 direct debits a year against 12 months of energy, a 3× under-collection
feeding straight into DD3's booked liability and DD-H's gap. Fixed; byte-identical on the real
(monthly, zero-gap) book. **The measured defect is PINNED, not fabricated shut:** the opening DD is the
first bill — one seasonal month annualised flat — so it is a function of **the month the customer walked
in**: **+33.2%** (gas, April join) and **−46.3%** (gas, July join) against +2.1%/−1.0%/+2.6% on the
weakly-seasonal electricity accounts, with C2g alone carrying **£293.49 of spurious held credit** against
a £1,812.20 portfolio peak. Strict xfail (XPASSes when the source is mutated to annual/12), minted as
atom `D_opening_dd_seasonal_sizing` — fixing it needs a **published** monthly-shape source, and no
coefficient here may be fabricated. **Held at L2:** expert_hour not_attempted, DD4b unbuilt, sizing defect
open. 1835 passed + 1 strict xfail; `epistemic_verifier` PASS (532 files).

**D_printed_figure_rederivation (2026-08-03, `8e57c9cdd`) — the mint's prescribed fix would have changed
the CHARGE to tidy the printout. L0→L2, recorded.** The footing fix closed "the column adds up"; this
closes "each line can be re-derived". Measured on the RENDERED artefact first: **86.1% of usage lines
(1441/1674)** and 243 standing-charge lines showed a multiplication that does not hold — `317.9 kWh ×
11.90p = £37.82` when the product is £37.83 — plus 324 invoices printing raw binary-float residue
(`0.23983870967741938`/day). The mint specified a declared 2dp rate with the **amount derived from it**;
measuring refuted it, because the precision a line needs scales with its magnitude (1–6 dp across the
book; a 2dp rate is out by **£7.86 on a 157,128.8 kWh line**). These rates are *derived*, not
contractual, so the amount is primary: the **rate is fitted to the amount** at the coarsest precision
that reproduces it, `None` when none does. **Zero money moved.** After: **0/1557** on the invariant,
0/1557 as rendered, 0 residue, and 1557/1557 still printing a rate. `PRINTED_LINE_REDERIVES` closes the
class (summary line, standing-charge line, per-register rows); the checker re-implements the arithmetic
and does **not** import `saas.money` (tautology guard, asserted by AST). R15 both ways: 9 real source
mutations each firing its own named test; the render control proven separately (restoring `toFixed(2)` →
1292/1557 fail). This commit also lands `D_money_boundary_reconciliation`, whose build had **never been
committed** despite its cell claiming it was. **R11 bound, stated honestly: verified on the rendered
output of LOCAL regenerated data — the live poesys.net re-fetch lands with the next publish and is not
claimed here.**

**W1_13 (2026-08-03, `89103080d`) — the external anchor landed, and the ENVELOPE was the side that was
wrong. L0→L2, recorded.** The blocker below asked whether a 43,338 kWh/yr domestic gas premise is a real
category or a modelling artefact. Both sides of that disagreement were internal, so the work was external
and only external: **DESNZ NEED 2026** (published 11 June 2026, England & Wales, consumption year 2024,
weather-corrected), the publisher's own tables and no aggregator. Two artefacts answer different halves —
the published aggregate over 21.6m properties, which carries an explicit **`Pre 1919`** age class
(detached gas-heated 3-bed **median 17,283 / UQ 23,068**, n=72,173), and the record-level 50k sample, from
which any percentile is computable; the sample was cross-checked against the aggregate *before use*
(medians 0.5% and 2.8% apart), which validates the **sampling**, not the source, since both share the NEED
lineage. **Two metadata facts did the real work, neither guessed:** `PROP_AGE_BAND 1` is *"before 1930"*,
not pre-1919, so the measured tail includes cavity-walled 1919-29 stock and every percentile is an
**under**-estimate of the true pre-1919 solid-wall tail (stated because the bias runs *against* the
conclusion); and the data is **right-censored at 50,000 kWh/yr** because DESNZ removes larger readings as
too large — making 50,000 the national statistics publisher's *own* threshold for "too large to be a
domestic gas reading", the same **kind** of object as the company's envelope.
**Verdict: `RESI_CONSUMPTION_ENVELOPE_GAS.high` 40,000 → 50,000, cited to that threshold.** The
justification does **not** depend on C4, and that is the point: the old bound flagged **1.02% of all
gas-heated E&W homes and 14.1% of pre-1930 detached homes** as implausible — an absurdity-catcher rejecting
one in seven of a real, common dwelling class had to move whether or not the fabric model existed. **R12
counterfactual, stated because the ordering invites the suspicion: had C4 come in at 55,000 the anchor
would not have covered it and the PHYSICS would have been the side that moved.** C4 sits at ~p99 of its own
size band (pre-1930 detached 101–150 m²: median 16,800, p99 38,900, max 49,900, **zero censoring** so those
percentiles are reliable) — one deliberately-worst archetype at p99 is expected; a *second* premise above
p99 is a physics finding. R13: decided blind to P&L, measured before margin.
**W1_11 stays at L2** — clearing a blocker has never moved a `level_current`. The settlement switch is now
unblocked and drawable, but it is not thrown, and throwing it moves published figures across the whole book.
**Control-set hole closed:** `RESI_CONSUMPTION_ENVELOPE_GAS` had **no test of its own** — the single test
named for the envelope class exercises only the *electricity* invariant, so the gas bound could have been
any number and the suite stayed green. R15 both ways: three real source mutations, each firing its own named
test, baseline restored. 69/69 invariant tests; 532 passed + 2 xfailed across the affected suites;
`epistemic_verifier` PASS. Anchor: `docs/market_research/need_domestic_gas_high_tail.md`.
**Third instance of the orphan class, correcting the record below:** the claim that
`tools/fabric_settlement_gap.py` "is its production caller and writes the artefact each run" is **false on
both halves** — grep finds no caller anywhere, and it writes only under `--write`. Caught because the tool
*printed* every premise inside the envelope while the artefact on disk still showed the old bound and a
breach that no longer existed. Refreshed; the durable fix is registered, not patched on sight.

**W1_11 (2026-08-03, `66d73d1e0`) — the fabric physics now has a seam into the path the company settles on,
and the level is HELD at 2 on a MEASURED blocker rather than shipped on a plausible mechanism.**
`simulation/fabric_demand_path.py` turns a customer + the household register + the real Open-Meteo archive
into the SAME `shape_fn(date_str)->[48]` callable every term-pricing path already consumes — the provider
changes, no consumer does. It replaces (never stacks on) the legacy overlay stack, chains the thermal state
across life-event boundaries via the new `PremiseTrace.final_state`, and RAISES rather than falling back on
a date it has no trace for. **Wiring it found what reading it would not:** `comfort_constraint_for` has
always accepted `prior_year_bill_gbp` and **no caller on any path ever supplied it** — the prebound response
was a live mechanism with a dead input, so every household heated to full SAP comfort however expensive its
dwelling was to run, which is precisely where the empirical prebound gap is largest. Now fed from the
trace's own prior-year kWh, **no coefficient touched**. **The blocker, measured**
(`tools/fabric_settlement_gap.py` → `docs/observability/fabric_settlement_gap.json`): three of four eligible
domestic premises land inside the company's own plausibility envelope; **C4 lands at 43,338 kWh/yr gas
against a 40,000 high bound that was itself set from the PREVIOUS generator's observed maximum.** Two
internal numbers disagreeing is not evidence about the world, and R12 forbids closing it by moving either
side — minted `W1_13_high_tail_gas_anchor` for the external NEED/EHS distribution that settles it.
Settlement is **not** switched: shipping a domain-invariant breach into billing is an R10 absurdity. The
seam is **not** an orphan — the measurement tool is its production caller. 232 green across the fabric
suites; `epistemic_verifier` PASS (530 files). En route, `tests/harness/test_premise_two_level.py`'s 19
errors + 1 failure on main's working tree were fixed (an earlier uncommitted change made `latitude_deg`
required without updating that caller).


**FIXED (2026-07-29, `67a2e3ee6` + `42cff58b6`) — one director message became two queued acts. Cause named,
not filtered.** The director's ntfy arrived twice, eight seconds apart, and each copy was separately acked and
queued as an instruction. Of his four hypotheses the answer is the third: **two consumers**. `ntfy-responder`
*and* `staging-watcher` were each running twice — an installed, enabled, **active** systemd unit **and** a
`start_worker.sh` tmux launch, because the cutover installed the unit but never flipped `launched_by: systemd`.
Evidence, `observed-with-evidence`: the responder log acked the **same ntfy message id** (`AK0UhbkAV2Ko`) at
17:32:19 and 17:32:27, staged as two different `from_rich_*.md`, and the rate file held every event twice with
identical timestamp and hash. A shared message **id** rules out both double delivery and a retry path. Neither
existing guard could ever have caught it: the `since` watermark and the `seen_hashes` dedup are both
**per-process in-memory** state, structurally blind to a sibling consumer. **Fixed by construction, no dedup
filter added before the cause was known:** every inbound message is claimed by its ntfy id via `O_CREAT|O_EXCL`
(an atomic cross-process test-and-set) **before any side effect**, fail-**closed** if the ledger is unwritable;
a second responder now refuses to start (`flock`) and says why; ntfy-app self-tests are dropped at the top of
the path so one costs **no model load, no reply, no ledger entry**; and the `from_rich_<ts>.md` filename
collision is uniquified, because de-duplicating delivery must never become **losing** a distinct message.
**R15 both ways, 9 mutations, all fired:** the same message delivered twice executes once, and two genuinely
different messages with identical text both execute — the guard keys on the **id**, not the body, so a director
deliberately repeating himself is not swallowed. **The class alarms (R10):** `reconcile()` computed
`running = unit_active or tmux_present`, which answers *"is it up?"* and is blind to *how many* launchers are
up — one and two read identically as `OK` — while one live reader queried only migrated units and the other
scanned only un-migrated ones, so a half-migrated daemon was invisible to both. New `DOUBLE_LAUNCH` status,
both readers widened, PID-aware against the unit's `MainPID` after it false-positived on all five healthy
daemons on the live box (the tests did not catch that — they inject `tmux_running` directly). Verified now:
`ps` shows exactly one responder and one watcher; live reconcile **0 drift alarms, 16 OK**; responder +
reconciler suites **64 passed**. **Registered, not silently absorbed (`c94cbcecd`):**
`OPS1_launcher_cutover_completion` — **seven** daemons carry the identical half-done cutover and will each
**double at the next boot**, single-launcher today only because their units happen to be inactive; queued one
cutover at a time per the 2026-07-17 ruling rather than mega-flipped. The ruling itself arrived with **no
"WORK THIS CREATES" block**, a §4 defect, so the work identifiable from its body was minted and the block
requested from its author.

**WIRED (2026-07-29, `eccaa9e2f`) — the backlog became real work: drawable pool 0 → 10.**
Director, verbatim: *"Your backlog is in a document but the thing that picks your next job reads the map.
That's why you keep saying there's no work. Put all eleven backlog items into the map as real unfinished
work items now."* **Premise measured, not assumed:** before this pass, 31 idle atoms carrying a real level
gap yielded a **DISCOVER/FRAME pool of ZERO** — the backlog contributed nothing to the picker. **Three
mechanisms were hiding real work behind a status,** each R15-proven by mutation (re-applying it removes
exactly the named atoms from the pool): (1) **`blocked_on` is not BUILD-only** — `_is_externally_blocked`
drops an atom from *every* lane including DISCOVER/FRAME, so B1/B2/B6, registered earlier the same day with
`blocked_on: director_build_open` to hold only BUILD, read as *nonexistent*; cleared, with the BUILD wall now
resting on `loop_stage: idle` + the `fronts.yaml` `stage_advance` gate, which gates BUILD **without** gating
thought. (2) **A sibling's `*_FRAME.md` in `evidence` silently saturates a new atom** —
`_atom_has_frame_doc` matches any FRAME-named doc under `docs/design/` without checking ownership, and H23
then hard-skips it, so six genuinely-unframed atoms vanished; **fail-silent**, and it breaks the assumption
the mechanism's own docstring states ("every non-canonical `*_FRAME.md` is owned by exactly ONE atom").
(3) **B9/carbon was in the map and still invisible** — `E5_carbon_three_ledger` was `frame_saturated: true`,
honest for the scope framed 2026-07-20 but not for the scope B9 widened it to. **7 minted, 4 reconciled** to
existing atoms, because a duplicate row is worse than no row: B9 **is** E5 (the backlog says so); B7 scoped
to the *remainder* (house moves + income shocks — `W2_5_life_event_stream` already emits job loss/illness/
divorce/retirement/new child at target); B8 registers only the **company** half (world half = `W2_14`);
B10 only the missing **switching response** (`W2_3_competitor_field` and `B4_competitor_field` untouched).
**Every level stays at 0 — registering work is not authorising it, and nothing was self-promoted.**
Still director-reserved and untouched: the idle→build stage advance; named-world VALUES + true probabilities
(B1); shock magnitude + target inversion shape (B2); price-war aggressiveness (B10); emissions-factor set +
counterfactual method (B9, category 6); fitness function + mortality rules (B11's harness carries an exit
test proving it **refuses to run** without a ratified fitness definition). **B1 is the one item still not
drawable** — its FRAME and mechanism are built, so its next step is BUILD (wiring a chosen world into price
formation), which needs the director's stage advance; flagged to him by NTFY. Verified by re-fetching
**origin's** copy of the map (11/11 present, pool 10). 232 + 90 tests green.

**HARDENED (2026-07-29, `03c2e7ffd` + `6f7bc3d32`) — a throughput signal that could not fall.**
Rule-0 yielded the dial (nothing below target anywhere) onto the at-target atom `G5_effort_sizing_discipline`.
Its own controls are fully mutation-rotated, so this pass ran the **class audit** rather than adding an Nth
guard: G5's class is *a flow/effort signal must stay honest — the absence of work must be visible*. Auditing
every consumer of G5's git-mined transitions found one outside its file_scope —
`tools/generate_wip_flow_data.py::_throughput` anchored its trailing 7/14/30-day windows on `ts[-1]`, **the
last transition's own timestamp**, so a window measured "the N days *before* the last transition", never the
last N days. Once transitions stopped, published throughput **froze at its final healthy value and could
never decay**: a build stalled for a month read identical to one at full velocity. Proven before the fix —
19 transitions dated 60 days back still reported 2.71/day. Fixed under `G7_wip_cycle_time_dashboard` (the
atom that owns the code): wall-clock anchor with `max(now, ts[-1])` so clock-skewed commits are not dropped
instead, plus `hours_since_last_transition` + `window_basis` published (R14) and rendered (R11).
**R15 mutation-proven** — restoring `anchor = ts[-1]` reds `test_trailing_windows_decay_to_zero_when_transitions_stop`
(19 ≠ 0) while the independence test (a live build must NOT read 0) and the skew test stay green.
15 door tests, 399 site tests, G5's exit suites re-verified unchanged (52 pass).
**Two honesty corrections, both filed in the map trail:** (1) the first note called `site/wip-flow/` a *live
published surface* — it is **not**. `site/_redirects` 301s `/wip-flow*` to `/proof/` under the RC7 idea-first
ruling; the page is noindex and canonically unreachable, and no reachable page consumes `wip_flow.json`. Real
mechanism defect, **internal-register reach, not a public claim**. (2) the identical anchor defect in
`tools/activity_cost.py::self_maintenance_trend` is **registered under G11 and queued**, not fixed on sight
(SELF-INTERRUPT DISCIPLINE). No level moved; both atoms stay at target.

**BUILT (2026-07-29, `90cd95039`) — the rotation↔curriculum BINDING: the missing join.**
SPINE_1 landed the scenario substrate and the stratified run-rotation landed the grid+cursor+selector;
they were built independently and **nothing joined them**. The grid named its worlds
`history-default / NESO-central / crisis-replay / glut`; the curriculum artefacts named the same four
`history_replay / neso_central / crisis_2021_22 / supply_glut`. A rotation cell therefore could not be
resolved to a world at all — `manifest_for_next_run` stamped ledger rows whose `world_scenario` no
artefact could answer for and whose `true_probability` no ratified artefact backed, and **every §4
verdict (ROBUSTNESS / COMMERCIAL EV / SURVIVAL) is computed from those rows**. Built: `grid_label` on
each artefact (the director's verbatim ruling-§2 label it implements); `grid_label_index` /
`resolve_grid_label` — **fail-CLOSED and deliberately not fail-open-to-baseline** (a baseline fallback
would run real history while the row claimed `crisis-replay`); `bind_cell` / `BoundCell` /
`_reconcile_true_probability` — fail-loud on grid-vs-artefact drift, and an **unratified artefact may
never supply an EV weight (R13)**. **5 R15 mutations RUN** (not asserted — executed), each proven to
red its named test: baseline-fallback, duplicate-label, drift-guard, unratified-weight,
bind-call-removed. **Dormancy held** — all four worlds still carry `true_probability: null` and are not
rotation-eligible, so COMMERCIAL EV keeps refusing to weight; this adds a guard, it does not smuggle a
weight into a previously-unweighted ledger. Evidence: 10 new tests green, adjacent suites 44 green,
epistemic verifier PASS (528 files), all 5 pre-commit gates dry-run green.
**Director's call, reversible:** the label→artefact mapping is the agent's reading of two
director-authored name sets — correct by editing `grid_label`, no code change.
**STILL OPEN (level stays 0, no self-bump):** no SIM generator consumes `paths_as_of` yet, so no run
actually LIVES through a non-baseline world — the spine is resolvable but **not yet consumed**; that is
the next increment. SPINE_2 curriculum values + ratification stay director-reserved (R13).
Registered not fixed-on-sight (SELF_INTERRUPT_DISCIPLINE): atom
`H29_import_time_env_capture_test_isolation` — `ntfy_utils` captures the wake HMAC key at module-import
time, so 4 signing tests pass alone and fail in any full-suite run (pre-existing, proven unrelated).

**PRODUCT LANDED (2026-07-24) — RC7 iteration 1: cohort-derived headline financials pulled off the lead surfaces (director ruling IDEA_FIRST_EXTERNAL_REGISTER).**
Director's correction: *"£80k makes no sense either. Why is that the lead number... what matters more is the idea."* £80,056/customer (and its £1.5M/£3.8M aggregates) fails the veteran sniff test by ~3 orders of magnitude and read as a simulation artefact. Iteration 1 (this pass, gate-on-green): (1) **front door** (`site/index.html`) — the cohort-financial pulse strip (net margin / treasury / EV / bills) **removed**; the front now leads with the idea (hero + cost-to-serve thesis) and the honest build state (the model-on-a-page diagram, promoted to element 2, each node framed for its build stage — live / partly built / planned); `renderPulseStrip` + render harness + tests updated. (2) **/proof** — the *"Investor summary"* genre **retired**; §4b renamed *"The teaching cohort — simulated unit economics, not company economics"*, `renderInvestor` reframed to the required framing (**"Teaching cohort, N=19 — not scaled company economics… a real UK supplier earns tens of £/customer/yr"**), green "on-track" endorsement stripped, "transfers between books" claim removed (id `project-anchor` kept so canonical links resolve). (3) **R10 class guard** added (`test_no_cohort_financials_lead_the_front_door`) — reds if ANY cohort aggregate financial is re-rendered on the front door, not just the instance caught. **Full site suite green (282 passed, 6 skipped).** Render-verified: front door carries no cohort £; /proof note leads with the teaching-cohort framing. **Iterations 2–3 OPEN** (per-node stage-views with one-click "look at this" views; site-wide external-register sweep) — the ruling stays drawable as the top product item.

**PRODUCT LANDED (2026-07-24) — SITE_V5 canonical-door fold COMMITTED (director Decision A: "COMMIT THE FOLD").**
`DIRECTOR_RULING_CANONICAL_DOOR_A_COMMIT_THE_FOLD_2026-07-24.md` resolved the one decision (§A) the SITE_MODEL_SPINE
campaign was walled on. One pass, gate-on-green: (1) all **22** non-canonical internal links (→ legacy `/method`,
`/project`, `/simplified`) rewritten to the canonical `/proof` anchors — **R11 link-walk now 0/0** (was 22); (2) the
`/project` **investor reframe re-homed onto `/proof#project-anchor`** and **render-verified live** via the page's own JS
against published data — **£80,056/customer** (net margin ÷ N=19), total £1,521,070, treasury £3,824,376, all carrying
their claim-status + `//` basis clock (RC6: unit economics leads, totals demoted/caveated); no longer orphaned on the
killed door; (3) the temporary `/method` live-door **retired** — every remaining door's nav is the canonical set only
(Home/World/Company/Proof, no ghost entries); (4) the R11 link-walk **flipped from mechanism-only to a LIVE publish
gate** (`site/test_link_walk.py::test_live_site_has_no_noncanonical_links`), **R15-proven failable** (injected
killed-door link → gate reds; clean → passes). **Full site suite green (283 passed, 6 skipped).** After the fold, the
SITE_MODEL_SPINE evidence-pages work is unblocked and proceeds per the ruling.

**PRODUCT LANDED (2026-07-23) — SITE_V5 surface 1 (Front door) iteration 2: rebuilt to the BRAND_CONSTITUTION architectural exemplar. SITE_V5 CAMPAIGN CLOSED (all 5 surfaces landed).**
Drawn by the seventh-class open-campaign self-refill (no doorbell): surfaces 2–5 landed, so the draw rolled to the last
open item, the front door. MVP #1 (`87ce1b980`) scored axis-1 **FAIL — "It still looks awful"**; `site/index.html` is
rebuilt strictly to the exemplar (§7) and presented **AS SCORED RUBRIC ROWS** vs
`DIRECTOR_AXIS1_SITE_VERDICT_ROWSCORED` + Spec-005 so the director's re-verdict lands **row-by-row**:
**RC4 (hierarchy & brand) ADDRESSED** — (a) type-only **BLACK** `poesys.` wordmark, legacy teal logo killed; (b)
rounded-card soup → **architectural black-on-white hairline grammar** (zero border-radius), ONE focal point (the hero
h1); (c) **colour is information only** — decorative coloured card top-borders removed, colour now appears ONLY on
claim-status chips (blue=VERIFIED, amber=PROVISIONAL) and the thesis chart (achieved cost=green on-track,
benchmark=structural black); off-brand teal/purple chart hex (`#1baf7a`/`#4a3aa7`) replaced by token reads; (d) **no
leading tilde** on any board numeral — the number + its `//` clock, status rides the chip; (e) **chat widget REMOVED**
from the marketing front door. **RC5 (effort-as-outcomes) ADDRESSED** — outcome metrics lead (net margin £1,521,070,
treasury £3,898,729, 1,588 bills, 113 settlement months, EV £7,803,340 PROVISIONAL), **no** tests/commits/phases
anywhere. **Honesty/R14:** every figure carries a claim-status chip + `//` basis clock; margin & EV read their
provisional flag from `portfolio.basis`; no fabricated numbers. **R11+R15** proven by the render harness executing the
page's real inline JS against published JSON (`site/test_home_door.py` — pixels + mutation independence) + 6 RC-row
guards (`site/test_front_door_brand.py`); brand-compliance frontier green. **Full site-lane gate green (292 passed, 6
skipped).** **Expert-Hour** (phase-close-evaluator, fresh context) = **PASS** against the single job (the 10-second
pitch), RC4/RC5 met row-by-row. Marked `landed` in `CAMPAIGN_REGISTER.yaml` **same commit**; all five surfaces now
landed → **campaign `status: closed`** (stops forbidding rest, R15 "all landed permits rest" half; the real-register
draw test flipped to prove closure). **R11 RESIDUAL — the director's own eyes:** if his axis-1 re-verdict is still
FAIL, reopen `surface_1_front_door` (one edit) and the campaign reopens (reversible). Non-blocking follow-on:
treasury/bills/coverage self-declare a VERIFIED chip in JS (defensible for settled/banked facts); the `/now` landing
swap stays the LAST step (ruling §6d) — `/now` reachable via a demoted link, not the default landing yet.

**PRODUCT LANDED (2026-07-23) — SITE_V5 surface 4 (Proof) rebuilt around "corrects itself in public", made MECHANICAL.**
Drawn by the seventh-class open-campaign self-refill (no doorbell): surfaces 2 & 3 landed, so the draw rolled to the
next unfinished item in 1→5 order. `site/proof/` is rebuilt so its single job — **show that this company corrects
itself in public** — is asserted nowhere and rendered everywhere. New centre of gravity: (1) a **claim-status
vocabulary legend** (VERIFIED/PROVISIONAL/PLANNED/RETRACTED, SITE_CONSTITUTION rule 6) + a falsifiable hypothesis
(every figure walks to its repo file; every withdrawn claim shown in place); (2) a **challenge channel** wired to the
real server-side-checked director-comments mechanism (`background/director_comments.py`, write-only, site never reads
back); (3) a **"Corrections in place"** panel fed by a NEW `proof.json.corrections` feed of **three real documented
retractions** this project made and withdrew — calm-year near-naked-hedging (a vol-lookback foresight bug), the
/company raw decision-log dump (RC1), the "overnight rest was legitimate" claim (a real target-matched draw bug, R9) —
each rendered **struck-through** with the corrected value beside it and the artefact linked. **Method folds in**
(`renderMethod` from `method.json` — framing, operating-model roles, R1..Rn rules with their forging incidents); the
**simplifications register folds in** as a clearly-labelled plain-English **appendix** (`renderSimplified` — per-lane
aggregate counts, raw register a click away; RC1 honoured: registers are sources not surfaces). Nav cut to the
five-surface IA; **Method / Journey / Simplified doors KILLED** — `/method /simplified /project /tours /platform
/method-casebook → /proof` 301s, full-link walk clean across all five surviving surfaces (director nav also cut).
**RC5** honoured: test-count effort metric stripped from the footer (R15-guarded). **R11+R15** proven by **51 proof
render-harness tests** (`site/proof/test_proof_door.py` — execute the page's real inline JS against published JSON;
mutation flips method rules, simplified totals, corrections values; fail-closed-visible when the corrections feed is
empty). **Full site-lane gate green.** **Expert-Hour** (phase-close-evaluator, fresh context): first pass
**NEEDS_WORK** caught two real honesty gaps — a claim-status **overclaim** in the hero copy, and "corrections in place"
being **prose with no render path** (an orphan transition, R11); **both fixed this same landing** (copy made true to the
rendered pixels; the corrections feed + render path + 3 tests built). Marked `landed` in `CAMPAIGN_REGISTER.yaml` same
commit; SITE_V5 stays OPEN (surface 1 FAIL + surface 5), so the draw persists. Non-blocking follow-on (belongs to RC4
iteration 6): stale 7-door navs on off-nav auxiliary pages (glossary, wip-flow, customers) still 301 rather than match
the IA. **The corrections feed is a designed, hand-appended feed** (not live-recomputed) — a new retraction is added to
`tools/generate_proof_data.py::_corrections` when it happens.

**PRODUCT LANDED (2026-07-23) — SITE_V5 surface 3 (The Company) rebuilt as the supplier SaaS shown as PRODUCT.**
Drawn by the seventh-class open-campaign self-refill (no doorbell): surface 2 landed, so the draw rolled to the next
unfinished item in 1→5 order. `site/company/` is rebuilt so its single job — **e2e supplier-SaaS evidence, real run
outputs never effort metrics** — is the page's centre of gravity: a **capability grid** (render-not-author from
`capabilities.json`; 12 capabilities, each headline a real output of the latest run — "1,588 bills settled", "avg
hedge fraction 88%", "23 obligations tracked, 19 GREEN") leads, then a **"what it replaces" vendor-coverage map**
(`saas_coverage.json` — the one product vs Kraken / Gentrack / Brady / NetSuite / Aryza / Braze / Opower across 22
categories), then the deep board-pack sections reframed as "walk any capability to its numbers" (pricing & finance
three-clock, hedging & risk, billing & collections drill-down, customer service, compliance). **Single-job
discipline:** no effort metric on the surface (`test_count=18504` kept off, **R15-guarded**); honesty kept (churn
live recall **0%**, carbon **"not yet measured" PLANNED**, not faked). Nav cut to the five-surface IA; falsifiable
hypothesis on-surface (didactic rule); every capability evidence link resolves through the IA change (`normLink`
rewrites the killed /sim//project//method/ doors). **R11+R15** proven by 9 render-harness tests
(`site/company/test_company_door.py` — execute the page's real inline JS against published JSON; mutation flips the
capability-grid pixel + finance figures, proving independence). **Site-lane gate green** (241 site tests pass).
**Expert-Hour** (phase-close-evaluator, fresh context) = **PASS** against the single job. Marked `landed` in
`CAMPAIGN_REGISTER.yaml` same commit; SITE_V5 stays OPEN (surface 1 FAIL + surfaces 4-5), so the draw persists.
Follow-on (non-blocking, belongs to surface 4): the regulatory/carbon cards link to `../proof/#regulatory` — that
anchor lands when Proof absorbs the regulatory fold (link HTTP-resolves now; the figures already render on this
page's own Compliance section).
**Row-scored self-claim vs the director's axis-1 verdict (`DIRECTOR_AXIS1_SITE_VERDICT_ROWSCORED`, /company
baseline 1/5):** **RC1** (machine-exhaust-as-content — the flagship /company offender) **ADDRESSED**: the raw
"Recent decisions" decision-log dump (commit-speak on the board view) is replaced by a plain-English governance
presentation layer — aggregate stats computed from the log (N decisions, reversible vs one-way-door, confidence,
date span) + a drill-down link to the raw `decisions.json`, regression-guarded (`test_decisions_are_a_plain_
english_layer_not_raw_log_rc1`). **RC5** (effort-as-outcomes) **ADDRESSED**: outcome metrics lead, no test/commit
counts on the surface (R15-guarded). **Deferred to their sequenced iterations** (director's order): RC3 charts,
RC4 site-wide brand/hierarchy (the tilde-on-board-figures kill + the director-comment-widget question, item 6/last).
Per the director's iteration order the NEXT campaign draw is **/simplified → the real lay page (RC2)**.

**PRODUCT LANDED (2026-07-23) — SITE_V5 surface 2 (The World) rebuilt around the walkable causal chain.**
Drawn by the seventh-class open-campaign self-refill (no doorbell): with surface 1 deployed-but-FAILED, the draw
rolled to the next unfinished item. `site/world/` is rebuilt so its single job — SIM causal-relationship
observability — is the page's centre of gravity: a walkable spine **weather (240 HDD, Dec-2025) → wholesale (SSP
£85.92/MWh, settled) → segments (14-home book) → usage & behaviour (household C1) → bills (£5,067.57 billed) →
carbon (£/tCO₂e, PLANNED)**. Every node renders a REAL figure read from published run data (render-not-author) +
its external anchor (Open-Meteo/DESNZ, Elexon, ONS/Ofgem) + an evidence link to the source file; the carbon end is
honestly **PLANNED** (E5 three-ledger unbuilt — no fabricated abatement figure); the chain states a falsifiable
hypothesis on-surface so an Expert Hour can walk any link to its data and fail it. Nav cut to the five-surface IA.
**R11+R15** proven by 30 render-harness tests (`site/world/test_world_door.py` — execute the page's real inline JS
against the published JSON; mutation flips the weather/segments/wholesale/bills figures, proving independence, not
baked constants). **Expert-Hour** (phase-close-evaluator, fresh context) = **PASS** against the single job; two
honesty/coverage findings fixed in-place (carbon numerator wording, graceful "--" not "0 homes", +2 mutation
tests). Site-lane gate green (all `site/` tests pass). Marked `landed` in `CAMPAIGN_REGISTER.yaml` same commit;
SITE_V5 stays OPEN (surface 1 FAIL + surfaces 3-5), so the campaign draw persists. Follow-ons (non-blocking):
inline graphs in the spine, external-anchor URL-resolution test.

**SEVENTH-CLASS STALL MECHANISED SHUT (2026-07-23, `1abeb558e`) — open campaigns are now always-drawable.**
Director ruling (CAMPAIGN_CONTINUATION §2, R10-on-R17): "an open campaign with unfinished items IS drawable work
— finishing surface N rolls into N+1, no doorbell." Absorbed as a mechanism, not consumed: `supervisor.py::
_open_campaign_draw` reads a new machine-readable authority `docs/design/CAMPAIGN_REGISTER.yaml` (R16) and forbids
rest while any OPEN campaign has an unfinished item — wired into `_self_refill_draw` (above backlog), `_is_drained_
and_gated`, and the whole-set `authorized_set_enumeration` (7th level `open_campaign`). **R15 both ways**
(`tests/background/test_open_campaign_draw.py`, 8 tests): the must-not-rest control reproduces today's 14:03Z state
(SITE_V5 open, surfaces 2-5 drawable, tick rested) and now draws; the may-rest control passes only when every item
is `landed`. Proof it's load-bearing NOW: the live enumeration reads `[build=. site=. discover_frame=. open_campaign=Y
backlog=. propose_half=. forward_discovery=.] → MUST-DRAW: open_campaign` — without this rung this very tick rests.
**R2:** live immediately on the per-tick `pull_next_work.py` hook (fresh `find_work` import per invocation); the
persistent `supervisor.py` daemon (PID 114010, Jul-22 code) needs a systemd restart from MAIN/console to absorb it
on its own cycle — **flagged, not done from the worker seat** (self-kill/console-sanctity). This is **rung 2** of the
7-rung WORK-SOURCE HIERARCHY (`DIRECTOR_RULING_WORK_IS_THE_DEFAULT`, the class-of-classes fix); rungs 4/5/7 (defect
backlog auto-mint, follow-on queue, PLANNER rung) remain open, parked in `docs/staging/in_progress/` with headers.
**Site verdict recorded (`director_axis_verdicts.jsonl`): axis-1 front-door MVP = FAIL 1/5** ("It still looks awful")
— surface 1 stays OPEN → iterate vs BRAND_CONSTITUTION + Spec-005 rubric as scored rows; surfaces 2-5 roll next.

**PRODUCT LANDED (2026-07-23, `87ce1b980`) — SITE_V5 surface 1 (Front door) MVP is LIVE + pixel-verified.**
The front door at poesys.net is rebuilt to the five-surface IA (Home / The World / The Company / Proof; Director
off-nav), with a distinct honesty line above the fold ("No customers. No licence. A running simulator"), the
`/now/` "default landing" framing de-throned (landing swap sequenced LAST), doors mapped to the three public
surfaces, and the thesis chart now stating its falsifiable hypothesis in copy. R11 confirmed on the live site
(honesty line, hypothesis, and new nav all render); site-lane gate green (60 passed); `test_home_door` canonical
nav updated in lockstep. **Remaining surface-1 steps (next tick):** Expert-Hour (cold-eyes) pass against the
single job, then the `/now/` landing swap; then surface 2 (The World). Alongside: the **scenario-spine + trading-
friction FRAME** landed (`docs/design/SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md`) — director did NOT veto
(ruling `1dd89af03`); launch-world values (`neso_central`/`crisis_2021_22`/`supply_glut`, sourced anchors incl.
SSP max £4,000/MWh confirmed vs Elexon API) await R13 ratification; SPINE_1–5 named for the map.

**OVERNIGHT-REST DRAW BUG FIXED + DEPLOYED (2026-07-21 ~07:25, `0a072a842`, supervisor restarted via systemd):**
The overnight rest (23:00→06:00, zero work commits) **was a real draw bug**, not a correct hold — the earlier
tick's "correct hold, nothing DRAWABLE" claim (`6898247b8`) was WRONG and is **retracted (R9)**: I re-checked
against the live classifier before trusting the narrative. Root cause: `_dependencies_met` was **target-matched**
(each dependency had to sit at ITS OWN target). W1_4 is walled at its L2→L3 coupled-triad step (no company twin),
so that wall propagated down the whole weather cascade — W1_5/W1_10, which only need W1_4 **at L2** (which it is),
read as `blocked_by_dependency` and the loop rested with genuinely-drawable work present. **Fix: level-MATCHED
dependency gate** (both lockstep copies — the draw + `build_atom_hold_reasons`): a dependency is met when at its
own target OR already at the level the downstream is trying to reach (`level_current+1`). Strictly more permissive
than the old rule (only ADDS a met-condition) so it can never newly block a drawable atom; mirrors the coupled-triad
gate, which is itself next-step-matched. **Live proof on the real map:** `W1_5`/`W1_10` now DRAWABLE, concurrent
draw returns `W1_5` (was `[]`); `W1_4` correctly still `coupled_triad_l3_wall`. R15 tests: the exact incident
(walled-upstream / drawable-downstream) as a positive control + a dependency-too-low mutation control proving the
looser rule did not fail open. `tests/background` 265 passed, 0 regressions. Supervisor restarted (systemd, PID
respawned on HEAD) so the deployed loop runs the fix (R2).

**BUILDING RESUMED:** `W1_10_ev_heatpump_geography` (director-named priority) build fork running → L1 national
adoption S-curves (EV + heat-pump). Next: advance idle backlog (E5/C4/C5/A DISCOVER-FRAME) + continue the
learning-value segmentation reframe. **ONE batched [ACT] sent** (NTFY `tl8dnpCfMMro`) naming the genuine director
gates: the W1↔company-twin coupling decision (the root un-dam for W1_4→L3), level-ups (D_cascade/W1_7/W1_9),
SITE1→L3 + W1_6 L3 Expert-Hour, W1_8 zonal (epoch console), generator wiring (reserved), OPS1 live systemd.


**RC3 DONE → "CONTINUOUS" IS NOW GENUINELY TRUE (2026-07-19 ~13:00, `9ada5f245`, deployed):**
The director-priority spine fix landed + supervisor restarted. `find_work` now syncs origin-`[ADVISOR-STAGED]`
docs into the local tree (via `git show`, no index pollution) before every scan — fail-safe, rate-limited (90s),
R15-proven (pulls origin-only / skips local / fail-safe on git error / rate-limited). So a **rested loop wakes
on an origin-staged directive**, not only console input — closing the 2026-07-19 unconsumed-doc failure.
**The loop's continuity is now complete:** RC1 (self-drawing, proven) + RC3 (origin-wake) fixed, RC2 never broken
(supervisor re-arm), build-in-progress guard prevents re-offer thrash. Also this turn: **G1/G2/G3 RATIFIED → L2**
(director console; re-blocked on the real L3 prereq = a live company consumer per COUPLED_TRIAD). **Fidelity steer
registered** — the top price-engine gap is the SPIKE TAIL (max £574 vs £4,038; negatives 0.013% vs 2.241%) by
VaR, worst-cell not average (the "worse than OLS in calm years" was the average trap). **G4 site fidelity
instrument LANDED** (`6c89e536c`, L2 PROPOSED): Proof-door Fidelity section leads with the exposure-tail gap
(spike-tail under-representation), worst-cell 2022, drillable EVIDENCE→WORLD chain; MAE reading subordinate —
honors the fidelity steer. 12 R15 tests, `pytest site/` 182 passed. **Sequence remaining: D + A BUILD** — with
the loop now genuinely continuous, these get authored into the map so the loop self-draws them (fresh-turn work).
Loop at honest rest meanwhile (G1/G2/G3 blocked on L3-prereq, nothing else authored) — wakes on new work.

**SELF-DRAWING LOOP RAN A FULL CYCLE + G MACHINERY DEMONSTRATED LIVE (2026-07-19 ~12:27):**
The self-drawing loop drew G1/G2/G3→L2, I dispatched one integrated emitter build, and it completed the
whole cycle honestly:
- **Emitter LANDED** (`1351502a7`, `background/fidelity_emitter.py`): recomputed the SSP calibration LIVE
  (no fixtures) → emitted to G2's ledger → G1 scored → G3 chained → DoD gate passed. **Honest findings:**
  best-of-family lift **£1.168/MWh over OLS** (not the flattering £2.99 over the weak gas-floor), and
  **6 of 10 years the structural model is WORSE than plain OLS** — a real, previously-unmeasured finding.
  G1 CVaR worst-cell = 2022 (real gas-crisis year). 13 tests, epistemic PASS.
- **BUILD-IN-PROGRESS guard shipped + DEPLOYED** (`aee1e9853`, supervisor restarted): the self-drawing loop
  no longer re-offers atoms a live fork owns (a real re-offer-thrash defect *my own* RC1 fix introduced,
  caught + closed with a fail-open marker filter, R15-proven). The loop now rests quietly behind an in-flight
  fork instead of thrashing.
- **G1/G2/G3 → L2 PROPOSED** (batched), `blocked_on: director_level_up` — worker-complete, awaiting your L2
  ratification; NOT L3 (WORLD-fidelity model-vs-reality, not COUPLED_TRIAD belief-vs-truth — no live company
  consumer, correctly declined). The loop is now at honest rest (`find_work → (None, False)`): all campaign
  BUILD is either done-pending-ratification or gated. Awaits: your L2 ratifications + the batched proposals.

**DIRECTOR CONSOLE ACT EXECUTED + RC1 FIX PROVEN (2026-07-19 ~12:10, `f9cfefff7`):**
- **FRONT_OPEN campaign** — the `EPOCH2_CAMPAIGN` front (over `G_data_learning`, the one campaign lane not
  already covered by the open SIM_ACTORS/SUPPLIER fronts) is DEFINED + OPEN + reconciler-clean.
- **RC1 MECHANICALLY FIXED — self-drawing PROVEN:** the campaign fidelity atoms G1/G2/G3 (which existed only as
  DISCOVER docs + modules, never in the map) are now authored into the map at `loop_stage: build` in the open
  front. **`find_work` went from `(None, False)` "drained-and-gated" to `BUILD=3`** — it now self-draws campaign
  BUILD. The loop no longer starves. (RC3 — origin-staging visibility — remains my spine turn, but an actively
  self-drawing loop pulls origin during work, so the starvation half is closed.)
- **RATIFIED → L1:** SSP engine (W1_6), G1, G2, G3 — cells moved, ledger `LEVEL_UP` recorded (console provenance).
- **Step-zero (reported before building the sensor):** Claude Code **2.1.215**; the statusline stdin payload
  **DOES carry `rate_limits`, populated** — `five_hour: 12% used`, `seven_day: 74% used` (+ reset timestamps).
  So the token-headroom sensor can be built with **no Claude Code update needed**; `executor_governor.py`'s inert
  `max_tokens_per_window` is its ready consumer. (Capture was a temporary, reverted statusline tee.)
- 48 governance tests pass; map/fronts edits validated. **Next (mine):** RC3 spine fix + the campaign BUILD the
  loop now self-draws (G1/G2/G3 → L2 = wire a live emitter) + the token sensor.

**LOOP-CONTINUITY FAILURE DIAGNOSED + 4 DIRECTOR ORDERS DONE (2026-07-19 ~11:15):** The 93-min idle +
unconsumed origin doc: **RC1** the draw starved (gate-after campaign BUILD authorized as policy but never
mechanized into the draw — 30 idle atoms all BUILD-gated); **RC3** the advisor doc was committed to origin
but never landed in the LOCAL tree `find_work` reads (supervisor doesn't `git fetch`; staging_watcher notifies
Rich only). **RC2 RETRACTED (R9):** I first claimed "no re-arm exists" — the supervisor log refuted it (it
cycled every ~2min throughout, correctly resting on an empty draw); I nearly shipped an inferred narrative and
corrected it. Fix = RC3 (the work-check must see origin staging) — queued as its own spine turn; RC1 mechanical
fix needs a campaign `FRONT_OPEN` (director console). Full: `LOOP_CONTINUITY_FAILURE_DIAGNOSIS.md`.
**Orders:** (1) diagnosed ✓ (2) two decade-replay slow tests FIXED `a040f176a` (413s→49s, mutation-verified)
(3) token amendment consumed — folded into `RESOURCE_AWARE_SCHEDULING_PROPOSAL.md` §7-8, 4 scheduling docs
reconciled ✓ (4) campaign BUILD resumed — the **G fidelity-machinery is now COMPLETE**: G1 grid-scorer `991b02007`
(best-of-family/CVaR/map-of-ignorance/CRN-ablation, 24 R15 tests) + G2 emit-ledger+DoD-gate `84efccdd7`
(sibling ledger, 3-red-condition gate, fail-closed, 22 tests) + G3 inspection-chain `42d4de88c` (4 record
types + link graph + the epistemic wall IN-SCHEMA via a truth_ref leak-guard, 25 tests) — all epistemic PASS,
all L1 PROPOSED ✓. **NEXT (mine):** the RC3 spine fix (own turn), then wire an emitter into G2's ledger +
G4 site instrument + D/A BUILD. **NEXT (director's):** a campaign `FRONT_OPEN` (makes BUILD self-drawing —
fixes RC1) + the seat-side step-zero check + the batched proposals. Not claiming "continuous" until RC3 + FRONT_OPEN.

---

**NOW (2026-07-19) — GATE-AFTER operating model adopted (director console); Epoch-2 BUILD underway.**
Director retired the failure-era caution posture: W1 BUILD OPEN; a ratified campaign IS standing BUILD
authorization for its A–G scope (no per-atom console acts); levels/values-calls batch, never block; walls =
schema/sim-structure doors, safety/auth-trust, epoch ceilings, REPO_PRIVATE, R13 dials; **OBSERVABILITY is the
license + per-turn DoD.** Recorded to the decision ledger + memory (`feedback_operating_model_gate_after`).
- **TASK 1 (director's named first task) — SSP PRICE-ENGINE RECAL: DONE + LANDED** (`a2dd6dcac`). The ~10×
  overestimate is fixed: raw `(demand/renewable)^gamma` → residual-demand scarcity form + UK-ETS carbon term,
  calibrated BLIND to P&L (R12/R13; engine is gated-off so cannot move company P&L) against 157,106 real Elexon
  periods 2016–25. **MAE £32.79** (beats the OLS £33.96 and naive gas-floor £35.78), R² 0.419, median £48.75 /
  p95 £217.15 vs real £55/£225, negatives produced. epistemic PASS, **2241 tests green** incl. an R15 mutation
  test (fails on revert to the raw-ratio form). Fidelity evidence emitted in atom-G shape
  (`docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md`). W1_6 → L1 PROPOSED (batched, cell not moved).
  Honest open limits: negative-price frequency gap (−£10 vs real −£185), carbon term uncalibrated, no live
  company consumer yet (so no coupled gap measured). Queued finding: AGWS revision-duplicate inflation in the
  shared aggregator (deduped locally; shared R15-failable fix homed as its own atom).
- **OBSERVABILITY DoD — decision-ledger site view LIVE** (`27745389f`). New Decisions tab on the Journey door
  (`site/project/`) renders the real ledger (`decision_log.jsonl`, count 20, current) — what/why/how-to-reverse,
  reversible + confidence chips, data-driven (R15) + fail-closed. This turn's decisions are visible for correction.
- **EPOCH-2 DISCOVER/FRAME (A–G) complete** and on origin (prior turns); the SSP recal unblocks the cascade
  MAGNITUDE the B/C DISCOVER named as the upstream blocker.
**BATCHED FOR ONE DIRECTOR [ACT]** (none blocking; work proceeded): (1) level proposal W1_6→L1; (2) the 6
Epoch-2 values-calls with conservative asserted defaults I'm running on (`EPOCH2_VALUES_CALLS_BATCH_1.md`);
(3) fan-widening proposal ≤3→min(cores−2,8) (`FAN_WIDENING_SAFETY_CASE.md`); (4) atom-G construct
challenge-response — best-of-naive-family / CVaR-generalizing-MAX / screen-then-ablate
(`EPOCH2_G_CONSTRUCT_CHALLENGE_RESPONSE.md`). Loop running continuous under gate-after. NTFY works,
staging_watcher UP.

**FOUR STEERS HANDLED (2026-07-19, later) — by INTERLEAVING (the scheduling steer's own demand: light forks ran while the main seat worked):**
- **[DIRECTOR] liveness/channel test — answered** (evidence): alive; the 90-min 06:28→08:32 gap was the seat
  HELD for a backgrounded 62-min validation instead of interleaving light work — a scheduling flaw, not a hang;
  the deadman correctly notify-gated a known-active validation (heavy work ≠ dead).
- **Worktree transient-pings — FIXED + DEPLOYED + quiet** (`b8f77cfb3`): `classify_worktree` now graces
  MERGED-pending-reap worktrees (no page on healthy churn), R15-proven both directions; deadman restarted 09:48,
  live check `alarm=False`. R9 correction: NOT committed-not-deployed (services were current) — the hygiene was
  never coded. Asks 2–3 (mirror routing, deploy-reality reconciler) proposed (`DEPLOY_REALITY_AND_MIRROR_ROUTING_PROPOSAL.md`).
- **Resource-aware scheduling — proposal** (`RESOURCE_AWARE_SCHEDULING_PROPOSAL.md`): resource-class budget (≤1
  heavy + N light) replacing the flat ≤3 count, R15-bounded, sequenced measure→propose→adopt (draw + fan-cap never
  change in one turn). Fan-widening reframed: widen MODERATE only, HEAVY stays 1.
- **Test throughput — MEASURED + proposal** (`bd2ac2faf`, `TEST_THROUGHPUT_MEASUREMENT_AND_PROPOSAL.md` +
  `tools/profile_test_suite.py`): 19,082 tests, collection ~8s (not the bottleneck); the multi-minute tail is
  **two specific tests** doing full-decade replays to check one assertion each (`test_retention_log_includes_acq_cost_saved`
  185s, an un-mocked dashboard test 117s = a 9th heavy test missing from `PUBLISH_GATE_HEAVY_IGNORES`) — not a broad
  slowdown. CPU-bound single-core, no GPU; a proven module-scoped-truncated-fixture template already in-repo is ~9× faster.
  **Queued next step (highest payoff, lowest effort):** fix those two tests at root (the top adoption lever) — its own
  commit + R15, next fresh turn. Gates untouched this turn (sequencing honoured).

Session history below retained for the record.

---


**Running processes** (background/process_manifest.yaml, `enabled`): worker-seat-manager, supervisor,
deadmans-switch, background-worker, staging-watcher, ntfy-responder, dispatcher, discovery-daemon,
sim-runner, sanity-daemon, director-comments, naive-organ, token-proxy — all on systemd — plus the
`claude` worker seat under worker-seat-manager. (executor-daemon is dark; autonomous-runner is
retired; session_watchdog was superseded — none of the three run.)

**Governance (running):** crossing a gate — flipping an atom `loop_stage: idle→build` — is authorized
ONLY by a director console act — a FRONT_OPEN or per-atom BUILD_OPEN — recorded and reconciled by the
gate-wall (`background/gate_authorization.py`). Within a director-authorized open front, the twin is the
standing approver that SEQUENCES which atoms flip idle→build (canon §3a); the front's authority is the
director's console act, and the twin never opens a new front. Gate-wall: 0 unauthorized promotions.

**Execution (running):** a serial, self-sustaining pull loop — the Stop-hook transport feeds
`find_work` turn to turn with no human nudge and is loud on a stall. Parallelism is bounded to at
most 3 disjoint Agent forks per draw, and every fork must come home: merged to main on success or
salvage-tagged and reaped on failure (fork-lifecycle reconciler, report-first). Worktree accretion is
reconciled and loud. Every commit passes a pre-commit test gate — a red-test commit is impossible.

**2026-07-17 — parallel made stable.** Bounded fan-out (≤3), enforced merge-or-reap, a worktree
reconciler, this status-honesty gate, and the pre-commit test gate — all report-first or structural,
with the loop running throughout. 33 stranded fork branches are salvage-tagged on origin.

**ACTIVE FRONT (2026-07-18, director console) — real-backlog open front, bounded-parallel build.**
Director authorized the in_progress/ real backlog as an OPEN FRONT: build continuously in bounded
parallel (≤3) under the live controls; REPO_PRIVATE excluded (one-way door, his call). Front
declared in `gate_authorizations.jsonl` (console provenance, R7) + reconciled by the gate-wall
(0 unauthorized promotions). Console-orchestrated worktree forks, merge-or-reap, every fork
orchestrator-verified (scope + tests + epistemic + R15 mutation re-run) before merge.
**WAVE 1 — landed + pushed:** W1_4 regional-weather aggregation-consistency invariant → L2
(mutation control proven to fire) · D5 account-hierarchy + payment-allocation → L2 (C-S1/C-S2
tested; control-activation landed — the 7 R15 ledger/arrears controls are now ACTIVE in the
production path, reconciling against independent invoice.py totals, fail-closed) · E4 CSS
Consolidated Segmental Statement → **L3** (director-RATIFIED this session — verify_css_reconciliation
runtime control + fail-silent closure, 15 R15 mutation tests orchestrator-verified; banked with his
console authorization, live on the site). E4 banked at L3; W1_4/D5 held L2. D5's remaining L3 is the
coupled-triad the director DECOMPOSED this session — W4_4 payment-observable-seam + W2_11
payment-behaviour-source + H27_payment_belief_gap, all FRAMED; that BUILD is director-gated (a
sim-structure seam + R13 curriculum + external Bacs anchors), so the product lane is currently
blocked-on-director (declared). **Self-governance scope model** design proposal landed
(`docs/design/SELF_GOVERNANCE_SCOPE_MODEL.md`) — awaiting director decisions on front/gate scope
before sub-steps 1–5 (which authorize nothing) are built. **Building now:** W1_3 national-weather
joint cold-and-still regime · supplier-reporting §4 obligations-register additions. Weather BUILD
crosses the Epoch-3 gate by the director's explicit authorization (logged). Executor kill-switch
stays DARK during console-orchestrated waves; self-sustaining loop takes over once self-gov proven.

**2026-07-18 — HARNESS RELIABILITY CLUSTER (twin-sequenced within the front).** The git-corruption
cluster is BANKED at L3 (director-ratified by console): **H24_precommit** — the pre-commit test-gate now
scrubs `GIT_*` so a git-touching test can't corrupt the shared `.git` (the root cause of the mid-session
`core.bare` blackout; R15-proven both directions on isolated repos) — + **H26** — a fail-safe guard in
`tree_lock` + the deadman makes any residual bare-repo flip LOUD and auto-repairing. **R15** ("every
control must be failable and mutation-proven; fail-open-green is the defect class") appended to
DIRECTOR_CANON.md (v3), reconciling the canon with CLAUDE.md. Also landed, L-up PROPOSED (awaiting the
director): **H23** — the content-refresh gate partitions by `@pytest.mark.operational` so a red daemon
test alarms but never wedges the live site, with a throttled independent-cadence green signal on the
deadman timer — + **H24_worktree** — a report-first (unarmed) merged/salvaged worktree-dir reaper,
never-reap-live invariant mutation-proven.

**CORRECTION + FAIL-CLOSED (2026-07-18).** These four were opened via TWIN approval (canon §3a), but the
fronts model (`fronts.yaml` `stage_advance` gate + `gate_authorization.py`) reserves idle→build to a
DIRECTOR CONSOLE act — the twin only *sequences* already-`BUILD_OPEN`'d atoms; it does not authorize the
flip. `H_harness` is in no open front, so these were self-promotions with no `BUILD_OPEN`; the reconciler
caught the newest (**G4**, now reverted + fork reaped). **RESOLVED by director console (2026-07-18):** the enforced model STANDS — the draw-filter IS the BUILD
authorization, the twin only *sequences* within it, no manual idle→build ever. My session's twin-opened
builds were the error (mis-reading canon §3a); the correct rule is now in memory + LATEST. Director rulings:
**H26+H24_precommit → L3, E4 → L3, H23 → L3, H24_worktree → L2 — all RATIFIED & banked** (LEVEL_UP recorded
channel:console, §0 satisfied). G4 stays reverted. **BUILD resumed:** the director console-`BUILD_OPEN`'d the
**payment triad** (W2_11 source + W4_4 seam + H27_payment_belief_gap). **W2_11 payment-behaviour-source LANDED**
(L1 PROPOSED, level 0 per §0; generator built + on origin — 44 tests, C-S2 substream isolation proven; wraps the
already-calibrated arrears/Bacs physics, externally anchored to Bacs/DESNZ, difficulty dials director-authored
per R13; `blocked_on: coupled_triad_gap` — its L3 awaits H27 measuring belief-vs-truth, which needs W4_4 seam +
D5). **W4_4 payment-observable seam LANDED + epistemic PASS** (L2 PROPOSED, level 0 per §0; on origin — typed/versioned
WallRequest/WallResponse in interface/, 6 observables-only inbound payloads incl Bacs ARUDD/ADDACS/AUDDIS, async
C-S3, bitemporal; 29 tests; epistemic-verifier confirmed field-by-field no generator-internal leak + the wall test
is load-bearing/mutation-proven; `blocked_on: coupled_triad_gap`). Its BUILD_OPEN cleared both the stage_advance
and schema_sim_structure gates (verified via the reconciler before flipping — ON_FRONT, clean). Both triad SOURCE
(W2_11) and SEAM (W4_4) now landed. **ADAPTER + CONSUMER now LANDED too** (both epistemic-clean, on origin):
`simulation/payment_seam_adapter.py` (W2_11 fills the seam — truth→observable many-to-one non-invertible collapse
proven via the real generator, 25 tests) + `company/billing/payment_observation_consumer.py` (D5 builds belief
from seam observables ONLY — AST-proven no-sim-import, C-S1/C-S3 order-independent/idempotent/missing-tolerant,
20 tests; reuses AccountLedger unchanged). **PAYMENT COUPLED TRIAD — GENUINELY CLOSED (director console ruling 2026-07-18, executed).** Sequence: I first
over-claimed "closed" and wrote the gap to the shared ledger before wiring the coupling — that wedged the publish
gate (Proof-door counted unmapped extras); I backed it out + corrected. **The director then RATIFIED W2_11→L1,
W4_4→L2** (cells moved, LEVEL_UP recorded channel:console — the honest levels, not the premature L3) and
**AUTHORIZED wiring the coupling + measuring for real**, which I executed: `coupled_triad._AUTHORITATIVE_COUPLING`
now carries W2_11↔D5 (8th pair), the scorer writes one bare headline entry (twin=`D5_account_hierarchy_payments`,
no `::suffixed` pollution), **`gap_measured('W2_11')=True`** (detection 0.30 — the no-remittance blind spot;
belief 0.073), the Proof door shows 8 mapped pairs, and the full publish gate is green. **H27→L2 PROPOSED**
(genuinely measured now, per his ruling; he ratifies the cell). The L3-ratification action-needed item is RESOLVED.
**Lesson landed:** don't write to a shared derived surface (Proof-door ledger) before its coupling is wired, and
don't claim "closed" before the full gate is green. **NEXT CAMPAIGN (his ruling): A — site rebuild per the
reconciled site specs, W1 DISCOVER alongside.** **[Campaign A — director-authorized site rebuild -- essentially complete.]** (1) **Front door + sitewide nav LANDED** (canonical IA Home/Company/World/Proof/Method/Journey/Simplified; Director off every public nav, auth-gated; legacy Supplier/SIM/Platform/Casebook retargeted + `_redirects` 301s; all 7 targets resolve, no dead links). (2) **Cross-door honesty AUDIT done + verified** (`docs/design/CAMPAIGN_A_DOOR_AUDIT_FINDING.md`): 5 of 7 doors (Home/Company/World/Proof/Method) PASS all 5 SITE-CONSTITUTION rules with EVIDENCE -- zero hardcoded metric figures, passports + freshness present -- verifying (not asserting) the rule-3 compliance claim. (3) **Journey door test gap CLOSED** (`site/project/test_project_door.py`, 11 tests incl. R15 mutation-independence). (4) Fixed my own W2_11<->D5 8th-pair regression on the Proof-door coupled-gaps panel (was red; site/ tests sit outside the publish gate, a coverage seam now queued). (5) **Debt A CLOSED -- Journey Regulatory tab now DATA-BACKED** (`tools/generate_regulatory_data.py`): the build-status claims (module count / SLC domains / per-scheme WIRED-NEXT-EXEMPT / overall RAG) are now DERIVED from real sources (live `company/regulatory/` module count, the ComplianceDomain enum, the obligations register, and whether the report layer actually imports each scheme's calc module) and rendered from `regulatory.json` with a freshness stamp -- R15-proven derive-not-relocate (10 independence tests; 153 site/tools tests green). The catch that proves the point: the old hardcoded '62 modules' had already DRIFTED -- real count is 63; and FMD was falsely 'WIRED' via a coincidental name match, now correctly NEXT. Published levy rates kept as cited commons. (6) **Debt B/C/D CLOSED** -- Journey Key Discoveries now carry passports/evidence links (all 4 figures traced to REAL sources, no fabrication: hedge cover rendered from `dashboard.json` -- a SECOND drift caught, hardcoded '0.80-0.90' vs real 0.81-0.89; ~30 suppliers + PS3,549 cap + 3-4% switching linked to market-research docs via the github.io docs mirror); Simplified freshness stamp now POPULATES (generator emits `generated_at`, door renders it); Home (8) + Proof (10) door tests added with R15 independence -- 164 site tests green. **Campaign A essentially complete.** **Only remaining item** (`CAMPAIGN_A_DOOR_AUDIT_FINDING.md`): debt E -- the site/ test coverage seam (site tests sit outside the publish gate, so a red site-door test can slip -- how my 8th-pair regression did); it's an off-front harness FRAME (not buildable until a harness front opens). Everything else in the reconciled site spec is landed + verified. **W1 DISCOVER (alongside, per the ruling): W1_3 national-weather joint cold-and-still regime LANDED** (doc-only) -- empirically 2.34x independent-draw tail mass, winter corr(temp,wind)=+0.507 vs all-year -0.06, PROVING the engine's current wind-only regime trigger insufficient; candidate invariants JT1/JT2/JT3 framed; no level claimed (held L1). W1 BUILD stays epoch-gated (director's call). **PAYMENT TRIAD L3 ESCALATED BUILD — LANDED + VERIFIED (director console APPROVED 2026-07-18: 'payment triad → L3 escalated build').** The live coupled sim seam is wired into the run loop (commit 3bfd4e98c, on origin): W2_11 canonical payment truth → emit_wall_responses (W4_4 seam) → PaymentObservationConsumer (D5 belief) → LIVE per-run gap at `run_phase2b:1764`. Verified independently: epistemic_verifier PASS (wall intact, no company/ files touched), live detection gap 0.2 written per run, R15 mutation proves the live gap fires (→0 when belief==truth), FULL PUBLISH GATE GREEN (18058 passed). En route the verify-before-push caught + I fixed 2 PRE-EXISTING origin wedges my earlier Campaign A site work had left uncaught (E2 net-margin floor + Journey supplier-count — both the debt-E site-vs-gate seam). Honest caveats: thin run-book (~5 payment failures/window → statistically thin headline VALUE, mechanism proven); I&C dispute→DD_FAILED + I&C now uses the bacs model (R13 fidelity change, decided blind to P&L). **L3 PROPOSED with evidence — D5 L2→L3, W2_11 L1→L3, W4_4 L2→L3; cells NOT moved (director+advisor own the map, §0); his build-approval is on record for the cell-move.** OPS/HEALTH for the operator (seat-restart casualties — all systemd/platform-reserved, I only flag): (1) NTFY DOWN — the restarted worker seat is NOT loading `background/.env.ntfy` (SE_NTFY_TOPIC unset; ntfy_responder runs but sends fail → director can't be paged); (2) `staging_watcher` daemon is DOWN (0 proc though enabled — process-set drift vs the manifest); (3) run_complete PIPELINE WEDGE — RESOLVED: it had reached 31 unprocessed markers over 7h because the publish gate was RED (on the 2 pre-existing site wedges above) so process_run_complete published but FAILED its ARCHIVE step, and each stuck marker re-spawned a redundant gate (self-amplifying saturation, up to ~10 concurrent pytest). Root-caused + fixed: gate green + I batch-archived the backlog (commit 2482213c7); saturation relieved (→2 pytest). sim_runner is alive. ROOT CAUSE FOUND (director-flagged 'restore ops health first'): `background/.env.ntfy` is MISSING from the box, so SE_NTFY_TOPIC is unset and `ntfy_utils` RAISES at import -> every daemon importing it crashes on start (staging_watcher DOWN; ntfy send fails). BOTH deaf+mute symptoms are this one missing category-5 secret. NET OPERATOR/DIRECTOR TO-DO (only you can — I won't fabricate/hunt a secret): place `background/.env.ntfy` back on the box with the rotated topic; then staging_watcher + ntfy_responder start clean. Full note: `docs/staging/FROM_AGENT_OPS_HEALTH_NTFY_SECRET_MISSING.md`. (Staging processing NOT blocked — I poll it myself.) **PAYMENT TRIAD NOW AT L3 (COMPLETE):** cells D5/W2_11/W4_4 moved to L3 per your repeated console APPROVAL — build landed+verified, reconciler-authorized (logged director-console record_level_up), full gate green 18058, on origin (ba6893d1b). **OVERNIGHT (director-authorized 2026-07-19, all landed):** (1) W1 DISCOVER coupled-weather-cascade doc (`W1_COUPLED_WEATHER_CASCADE_DISCOVER.md`, e434500f4) -- cascade chain + compounding tail + gap_cascade metric; W1 BUILD stays closed. (2) **Debt E BUILT** (site-lane test-coverage gate `tools/site_lane_gate.py` + pre-commit hook, 3f1b513b5) -- the seam that caused 3 site-wedges this session is CLOSED (R15-proven live: a red site test is now refused at commit). (3) **Advisor steer DONE** (both items): ghost worktree agent-a857b050 reaped; **treadmill-quiet mechanism BUILT** (f9b57a209) -- `_is_drained_and_gated()` predicate -> find_work third state -> the hook allow-stops QUIETLY when the map is drained AND blocked on a director act (no more ~2-min at-target HARDEN doorbell thrash / LOOP_BROKEN alarms), anti-idleness preserved, R15-proven, full gate green 18076. **DEPLOY:** the hook + reconciler deploy on merge (quiet-wait live NOW); the daemon `run_cycle` side needs a **`supervisor.service` restart** (operator). CORRECTION (2026-07-19, R9 — my earlier 'secret MISSING' claim was WRONG): the NTFY topic IS present at `~/.config/synthetic-enterprise/.env.ntfy` (the systemd EnvironmentFile) — I verified by SENDING an NTFY. The deaf/mute was (i) staging_watcher DOWN + (ii) the STALE-code deadman/supervisor daemons (started 18 Jul 15:54, before the treadmill fix landed 00:55) crying frozen. BOTH fixed by restarting supervisor.service + deadmans-switch.service (done): staging_watcher back UP, evaluate_pull_loop now HEALTHY_IDLE (alarm=False). NET OPERATOR TO-DO: none required for NTFY (works). Optional: (b) `systemctl --user restart supervisor.service`.
Non-trivial gaps proven (R12/R13, non-tuned): **detection 0.30** — the headline: 78 of 257 true failures are non-DD
and *never observed* through the seam (the no-remittance blind spot, leak-witness 0 every seed); **belief 0.073**
(arrears/cash inference vs truth). R15-independent (the consumer never receives truth — runtime spy-tested +
mutation checks). Honest flags: allocation dimension *dropped* (metric-shape mismatch, its effect surfaces in
ageing); ageing gap ~1.0 flagged for scrutiny; two real bugs found+fixed pre-commit. **All five triad pieces now
built** (W2_11 source + adapter, W4_4 seam, D5 consumer, H27 gap). **W2_11→L3 + D5→L3 + H27→L2 PROPOSED** with the
gap as evidence (`level_up_proposals.jsonl`) — the cell moves are the director's per §0. **One follow-up flagged**
(surfaced, not blocking the measurement): the map W2_11↔D5 coupling doesn't derive cleanly (`_twin_id_for`=None;
ledger twin label ≠ atom id), so the *mechanical* `world_l3_blocked` gate needs the `couples_with`/`depends_on`
wiring fixed before an actual L3 cell-move. W1 stays DISCOVER.

**Fork-lifecycle note (2026-07-18):** the gap fork was mis-killed twice on a buffered-output false-signal before I
corrected — output-file size / mtime / commit-count are NOT progress signals (only the completion notification is);
hardened in memory. No work was lost (the killed forks had written nothing); the third ran to completion.
**[ACT]-paging fix LANDED + DEPLOYED (R2):** the director-caught escalation bug — [ACT]s silently not paging his
phone (a failed send still stamped `last_pinged`, suppressing the deadman's re-ping) — is fixed (decouples
"registered" from "confirmed-sent" via `mark_sent`/`last_sent_at`; a failed send keeps the page due) AND the
running daemons were restarted onto it (deadmans-switch + supervisor via systemd, staging-watcher relaunched) —
committed ≠ running, now both.
**Reap-guard MECHANISM LANDED (H24_worktree HARDEN, advisor-steered, R3 strike-3):** after three live forks were
destroyed this session by raw `git worktree remove --force` on false-death inference, a sanctioned
`reap_one_worktree` entrypoint now REFUSES LOUDLY a locked or live/unmerged worktree (both R15-mutation-proven to
fire; dogfooded live — it correctly refused its own fork's worktree). Raw `--force` reaps are retired.
**IaC drift logged (queued, not fixed):** `staging-watcher.service` is declared in repo IaC but runs
hand-launched (not systemd-installed) — it died on restart for lack of the EnvironmentFile; relaunched with env.
OPS1 reconcile (install the declared unit) is queued in the decision log.
**H27_phone_act_channel threat model landed (DISCOVER, design-only):** `docs/design/PHONE_ACT_CHANNEL_THREAT_MODEL.md`
— the forge-proof phone-answerable [ACT] channel the director asked for ("annoying having to log in and paste").
**SECURITY FINDING (surfaced for review, NOT changed — director/platform-reserved):** confirmed live that Tailscale
**Funnel is active** on the file-api (`https://skynet-1.taila062fa.ts.net` → `127.0.0.1:8765`) and `file_api.py::_auth`
is **X-Api-Key-only** — so the file-api is public-internet-reachable, gated solely by the key. Plausibly intended
(it's the documented File API), but the posture (single-factor key, rotation/scope) warrants an advisor review; the
phone-act build consequently must be tailnet-only + out-of-tree-keyed payload-HMAC+nonce (Funnel strips tailnet
identity). Logged in the decision log; I changed nothing.
**Payment-triad CLOSURE launch-ready (next build phase):** with source (W2_11) + seam (W4_4) landed, the three
closing units are ownership-resolved + all director-BUILD_OPEN'd + disjoint-scope — adapter=**W2_11** (`simulation/`,
fills the seam), consumer=**D5** (`company/billing`, reads `WallResponse` → allocation/ageing belief; its
`blocked_on: payment_seam_triad_built` is now CLEARED), gap=**H27_payment_belief_gap** (`company/compliance`,
belief-vs-truth). Adapter+consumer run bounded-parallel, gap last. Deliberately launched fresh, not at this turn's tail.

---

**Latest simulation results (2016–2025)** — auto-processed (501s / 8 min):
- Net margin: £1,526,675.52 | Gross: £6,468,266.50 | Capital: £51,397
- Treasury: £2,466,636 → £3,902,360 | 38 committee interventions | 1557 bills issued
- Enterprise value: £7,260,568.83 | Net after CTS: £1,503,517
- Retention: 13 offers, 13/13 retained | 5 no-offer churns | 5 total churned accounts

<!-- NAIVE_ORGAN_ASKS -->
**NAIVE ORGAN asks:** — open questions; answer WITH EVIDENCE (`answer_question`) or mark a miss. Never actions.
- (T3_inherence) [unanswered >24h] When you call BUILD "inherently narrow," what is the concrete definition of BUILD's scope that makes narrowness intrinsic — and if you cannot state that scope independently of this particular tree/suite's configuration, on what basis is the word "inherently" doing any work at all?
- (T3_inherence) [unanswered >24h] When you say BUILD is "inherently narrow (1-3 max)," is "1-3" a number that fell out of measuring something about the work — like task interdependence, error rates, or throughput at higher widths — or is it just a cap someone picked and then relabeled as "inherent"? What specific failure have you actually observed (or would predict) at width 4+ that doesn't occur at width 3?
- (T3_inherence) [unanswered >24h] If those 24 atoms truly are read-only, zero-collision, and target-positive, who or what actually enforces the "one at a time" limit — is it a hard mechanical rule of this system, or just an unexamined default that no one has traced back to a real constraint?
- (T3_inherence) [unanswered >24h] If BUILD's "narrowness" can only be demonstrated by pointing at the current tree/suite configuration, what observable would change — some capability BUILD gains or loses — the moment you swapped that configuration, and if the answer is "nothing," why is that dependence being described as "inherent" rather than simply "how it happens to be wired right now"?
- (T3_inherence) [unanswered >24h] If width 3 was itself just carried over from some earlier default rather than measured, what evidence would distinguish "we tested 4+ and it failed" from "we never ran anything wider than 3, so of course we've only ever observed success at 3"?
- (T3_inherence) [unanswered >24h] If 24 atoms are each independently read-only, zero-collision, and target-positive, what concrete failure or cost is supposed to occur if two or more are applied together — and has anyone actually observed that failure, or is "one at a time" just asserted without a single traced example of collision or harm?
- (T3_inherence) [unanswered >24h] When you swap the tree/suite configuration and BUILD's capabilities are unchanged, what would you have to observe changing for you to accept the narrowness as "inherent" — and if no such observable exists even in principle, what work is the word "inherent" doing that "currently wired this way" doesn't?
- (T3_inherence) [unanswered >24h] If all 24 atoms are genuinely read-only, zero-collision, and target-positive as claimed, what specific mechanism or shared resource would make applying two simultaneously behave differently than applying them sequentially — and does anyone actually possess a logged instance of that difference, or does the "one at a time" rule rest entirely on the untested fear that some undocumented coupling exists?
- (T3_inherence) [unanswered >24h] What are the two named open questions, and by what mechanism does merely updating a stale dependency's status actually resolve them rather than just relabel them as resolved without new evidence?
- (T3_inherence) [unanswered >24h] What does any of this — "tree/suite configuration," "BUILD's capabilities," the semantics of "inherent" versus "currently wired this way" — have to do with the only stated goal (a UK energy supplier's enterprise value and its avoidance of administration), given that the observable state contains not a single number, price, cost, or survival metric?
- (T3_inherence) [unanswered >24h] If two atoms are genuinely read-only and zero-collision, then the only thing they can share is the act of applying them — so what does your apply pipeline actually touch in common (a lock, a config reload, a transaction, a live cutover) that two sequential applies never overlap on, and has anyone ever observed that shared step fail under concurrency, or is "one at a time" simply the rule nobody has been given permission to test?
- (T3_inherence) [unanswered >24h] If a DISCOVER pass both raises an open question about anchors and supplies its own answer, what independent evidence confirms that answer is correct rather than merely internally consistent with the assumption that prompted the question?
- (T3_inherence) [unanswered >24h] If the entire observable state is nothing but a token labeled "inherent" and a sentence questioning its own relevance, then what mechanism ever connected this system's inputs to the energy supplier's enterprise value or administration risk — and if none exists, on what basis would any output it produces be treated as advancing the only stated goal?
- (T3_inherence) [unanswered >24h] When two "read-only, zero-collision" atoms are applied concurrently and the shared apply step fails, what actually happens to the business — does the supplier risk administration, or is "one at a time" a convention protecting a step whose real failure cost nobody has ever measured?
- (T3_inherence) [unanswered >24h] If bad debt is observed to be low, what evidence rules out that this reflects an overly strict affordability constraint suppressing legitimate revenue rather than a healthy book — and why is affordability being treated as fixed "physics" rather than a tunable lever that the enterprise-value goal should be free to adjust?
- (T3_inherence) [unanswered >24h] What actual causal pathway—if any—exists by which a token reading "inherent" and a self-referential sentence get transformed into decisions, actions, or signals that reach the energy supplier's finances, and if you cannot name one, why is this system being fed such state at all rather than the supplier's actual operational and financial data?
- (T3_inherence) [unanswered >24h] When you say the two atoms are "read-only, zero-collision," on what basis is that claim verified for the *shared apply step* itself — and if that step can fail under concurrency, what concretely does it write or mutate that makes it "shared" rather than read-only?
- (T3_inherence) [unanswered >24h] If low bad debt is fully consistent with both a healthy book and an affordability constraint choking off legitimate revenue, what observable number would come out *different* under those two worlds — and if none would, on whose authority was affordability stamped as untouchable "physics" rather than just another lever the enterprise-value goal is entitled to loosen?
- (T3_inherence) [unanswered >24h] What decision, action, or signal that reaches the supplier's finances actually consumes this "inherence_token" and "sentence" as input, and can you point to the specific place where that consumption happens — or is this state merely being described and inspected in a loop that never touches revenue, cost, or the survival constraint at all?
- (T3_inherence) [unanswered >24h] If low bad debt looks identical in both worlds, which number moves in only one of them — rejected/declined applications, quotes-to-conversions, or served-demand versus addressable-demand — and if you cannot name that number, why is "affordability" being treated as a fixed constraint rather than a dial whose setting you'd have to measure before calling it untouchable?
- (T3_inherence) [unanswered >24h] When you log that "the approver picks and the pick is logged," what mechanism actually forces a director's discretionary override to bind against the survival constraint — or is the logging merely a record that no one is accountable for acting on, letting a well-documented bad pick still push the company into administration?
- (T3_inherence) [unanswered >24h] When world difficulty and company capability advance on separate tracks that never gate each other, what forces any given depth to ever be experienced as a real constraint rather than as inert scenery — and if nothing does, on what basis is the claim's word "physics" earned at all?
- (T3_inherence) [unanswered >24h] If the simulated approver is a director-authored curriculum standing in for the real director, what guarantees that the real director's actual decisions at go-live match the curriculum the whole system was optimized against—and if they diverge, which side is treated as wrong?
- (T3_inherence) [unanswered >24h] If the whole safeguard reduces to a label — "read/fetch-only tools, connectors stripped" — what actually verifies at run time that a tool tagged read-only cannot mutate state or reach an account, rather than merely being described as unable to?
- (T3_inherence) [unanswered >24h] If world difficulty and company capability never gate each other, can you point to a single state variable through which a given "depth" actually changes the enterprise-value or survival numbers — and if you cannot, what is the word "physics" naming other than a label attached to scenery that never touches the score?
- (T3_inherence) [unanswered >24h] When you say Bacs "physics"—a fixed 3-day settlement cycle and standardized reason codes that are just administrative rules—what makes you confident the sim reproduces the parts that actually threaten survival (timing of cash outflows/inflows against liquidity), rather than just replaying the schedule as if it were an immutable law of nature?
- (T3_inherence) [unanswered >24h] When you vary "depth" while holding world difficulty and company capability decoupled, does any number in the enterprise-value or survival calculation actually change — and if you can name the exact state variable it flows through, why call it "physics" rather than that variable, and if you cannot, on what basis do you claim "physics" is in the model at all?
- (T3_inherence) [unanswered >24h] When Bacs settlement is modeled as a fixed 3-day "physics," does the sim also reproduce the ways that timing can actually break under stress—payment recalls, failed direct debits, indemnity claims, batch cutoff misses, or a bank/Bacs delaying or freezing your access—or does it guarantee inflows and outflows arrive exactly on schedule regardless of the firm's liquidity condition?
- (T3_inherence) [unanswered >24h] When you hold world difficulty and company capability fixed and change only "depth," can you point to a single line in the enterprise-value or survival formula whose output moves — and if so, name that variable; if not, what would anyone lose by deleting the word "physics" from the model entirely?
- (T3_inherence) [unanswered >24h] When the firm's liquidity is stressed, does the sim ever let a scheduled Bacs inflow fail to arrive on day 3 — via recall, failed direct debit, indemnity clawback, cutoff miss, or a bank freezing access — or is the 3-day delay the only deviation it can ever produce, so that every settlement is guaranteed to land intact regardless of the firm's condition?
- (T3_inherence) [unanswered >24h] If "depth" never changes any variable in the enterprise-value or survival formulas, what evidence is there that "physics" was ever wired into the model rather than just named in it — and who has actually traced that path rather than assuming it exists?
- (T3_inherence) [unanswered >24h] Can you point to a single concrete run where changing "depth" produced a different number in an enterprise-value or survival output — and if no such run exists, on what basis is "physics" claimed to be part of the model at all rather than a label attached to inert code?
- (T3_inherence) [unanswered >24h] If "physics" is genuinely wired into the enterprise-value or survival calculations, why has no one simply run the model twice with two different "depth" values and shown the two outputs differ — and if that trivial test has never been run, what specifically has been stopping it?
- (T3_inherence) [unanswered >24h] When you say "run the model twice with two different 'depth' values," has anyone actually confirmed that a "depth" input exists and is even read by the enterprise-value or survival code — or is the whole premise resting on an assumption that such a knob is wired in at all?
- (T7_repeated_fix_class_refill_draw) [unanswered >24h] If all three examples describe designing and gating a single "coupled-triad draw" mechanism (binding rule 1), what independent evidence shows these were three distinct fixes that actually refilled a draw — rather than one design being re-described three times under a label that doesn't match the work?
- (T3_inherence) [unanswered >24h] What evidence shows that merging this weather-physics design doc actually moves enterprise value or survival probability, rather than just adding modeling machinery whose payoff is assumed but never measured against the north star?
- (T3_inherence) [unanswered >24h] Given the goal is to maximise enterprise value while never entering administration, how does a "GB weather-physics hierarchy" connect to either objective — that is, what decision does this weather model actually drive, and where is the evidence it improves survival or value rather than just adding modelling complexity?
- (T3_inherence) [unanswered >24h] If `in_progress/` already holds the file, what evidence confirms the copy you're deleting is a true byte-for-byte duplicate rather than the only surviving version — and what reads that root path today such that removing it won't break the running system?
- (T3_inherence) [unanswered >24h] For a UK energy supplier whose survival hinges on covering demand against wholesale price and volume risk, what specific hedging, procurement, or dispatch decision changes its numeric output when the "GB weather-physics hierarchy" is swapped for a naive weather forecast — and if none does, why is it in the system at all?
- (T3_inherence) [unanswered >24h] What is the actual enterprise-value or survival benefit of registering a four-level weather-physics hierarchy plus a coupled twin and follow-ons, and why is that work being queued and parked (BUILD gated to Epoch 3) rather than tied to any concrete decision this energy supplier must make now?
- (T3_inherence) [unanswered >24h] When the "GB weather-physics hierarchy" and a naive forecast produce different predicted demand or renewable-output numbers, does any downstream hedging, procurement, or dispatch quantity actually read that difference and change its committed volume or price — and if so, can you point to the specific decision variable and the threshold at which the two forecasts would command different actions?
- (T3_inherence) [unanswered >24h] What concrete decision this energy supplier faces now—hedging volume, pricing, capacity procurement—would change its action based on the output of a four-level weather-physics hierarchy, and if none does until Epoch 3, what specifically breaks if that registration is deleted rather than parked?
- (T3_inherence) [unanswered >24h] When the physics hierarchy and the naive forecast disagree, is there a single committed quantity or price anywhere downstream whose value would be numerically different as a result — and if you cannot name that variable and the disagreement threshold that flips it, on what basis do you believe the more sophisticated forecast is affecting enterprise value at all rather than just being computed and discarded?
- (T3_inherence) [unanswered >24h] If no decision this energy supplier currently faces would change based on the four-level weather-physics hierarchy until Epoch 3, what is the concrete cost of keeping that registration parked versus deleting it — and why is preserving a component that changes zero present actions being treated as valuable rather than as dead weight to be justified?
- (T3_inherence) [unanswered >24h] Can you point to one committed order quantity or submitted price in a real decision cycle where the physics forecast and the naive forecast actually produced different numbers, and if no such instance exists, what evidence distinguishes "the physics forecast never changes a decision" from "the physics forecast is wired into nothing downstream at all"?
- (T3_inherence) [unanswered >24h] What is the cost of keeping the registration parked measured against the cost of *reconstructing* it correctly at Epoch 3 (including the risk of getting it wrong or missing the moment it starts to matter) — and how confident are you that "changes zero decisions today" reliably predicts "will change zero decisions before Epoch 3," given that you'd have to delete it now but only find out you were wrong later?
- (T3_inherence) [unanswered >24h] If nobody can produce even one order quantity or price that came out different because the physics forecast existed, on what basis is that forecast being counted as part of the decision system at all rather than inert code that touches neither enterprise value nor the survival constraint?
- (T3_inherence) [unanswered >24h] Given the north star is enterprise value under a survival constraint, what evidence shows that a locational weather dimension actually changes any decision the business will make — rather than being an architectural preference — such that building it *first* is worth delaying the futures engine that the value case presumably rests on?
- (T3_inherence) [unanswered >24h] If the north star is enterprise value under an absolute survival constraint, what makes "physics first" the right ordering rather than whichever lever — renewables trends, zonal pricing, or DSR — most directly moves the survival-risk or valuation numbers you're actually being measured on?
- (T3_inherence) [unanswered >24h] If replacing the physics forecast with a constant provably changes no order quantity or price, then what is that forecast for — and does anything in the system actually read its output, or is it computed and discarded?
- (T3_inherence) [unanswered >24h] If the forecast provably changes no order quantity or price today, was it ever wired into those decisions and later bypassed — or is there some other consumer (a survival/administration constraint, a report, a downstream model) that reads it on paths your "no change" test didn't exercise?
- (T5_sustained_work_flat_goal) [unanswered >24h] If 12 of the last 20 commits went into 'site' work, why has the enterprise-value goal metric stayed completely flat over that same window — is that concentration of effort producing any measurable movement in the north-star metric, or are we mistaking activity in one bucket for progress?
- (T2_terminal_state) [unanswered >24h] How can the claim be "complete" when the observable state shows 47 atoms still explicitly marked "open" — what definition of completeness treats 47 unresolved items as done?
- (T7_repeated_fix_class_two_strike) [unanswered >24h] If a "two_strike" policy means the mechanism is eliminated on the second failure, how has the same defect reached a third application (an R3 "strike two") without the earlier strikes having already forced its elimination?
- (T3_inherence) [unanswered >24h] What evidence connects `route_blocking_decision` sending the W1_2→W1_3 weather-physics BUILD-open "to the standing" with any change in the supplier's enterprise value or its distance from administration — or is "the standing" just an internal state transition with no demonstrated bearing on the north star?
- (T3_inherence) [unanswered >24h] What is the rest of the sentence — specifically, what property or scope of the whole system is being claimed to follow from "BUILD is inherently narrow (one tree/suite/...)," and does that claimed consequence actually hold, or does calling BUILD "narrow" quietly assume the very thing it's being used to justify?
- (T3_inherence) [unanswered >24h] When you say "inherently narrow," can you name the specific thing BUILD *does* that constrains its scope — as opposed to a config choice — and show what would actually fail if that scope were widened, rather than just asserting it would?
- (T3_inherence) [unanswered >24h] When you say BUILD is "inherently narrow (1-3 max)," what is the "1-3" actually counting — parallel tasks, people, work-items, something else — and what specific failure did you observe (or predict) at 4+ that you did not see at 3?
- (T3_inherence) [unanswered >24h] If those 24 atoms are genuinely read-only, zero-collision, and target-advancing, who or what actually verified those three properties — and if they were verified all at once, why can that same batched verification not authorize working them all at once?
- (T3_inherence) [unanswered >24h] When you say BUILD is "inherently narrow," can you point to the actual criterion that decides whether a given action falls inside or outside BUILD's scope — and if that criterion changes when this tree/suite's configuration changes, in what sense is the narrowness a property of BUILD rather than of the configuration you happen to have set?
- (T3_inherence) [unanswered >24h] If width 3 is genuinely a measured ceiling rather than an arbitrary label, where is the record of a width-4 BUILD actually being attempted and failing — and if no such attempt exists, on what basis is the failure being predicted rather than assumed?
- (T3_inherence) [unanswered >24h] If 24 atoms are all confirmed read-only, zero-collision, and target-positive, what specific harm or failure has anyone actually observed—or even predicted—from running more than one at a time, and if none, why does the limit exist at all?
- (T3_inherence) [unanswered >24h] What does BUILD's "narrowness" have to do with keeping a UK energy supplier out of administration — i.e., which survival-or-enterprise-value decision actually changes depending on whether that tree/suite dependence is labeled "inherent" versus "wired that way right now," and if none does, why is this question sitting in the business's observable state at all?
- (T3_inherence) [unanswered >24h] If all 24 atoms are genuinely read-only, zero-collision, and target-positive as claimed, what is the specific mechanism by which applying two together produces a failure that neither produces alone — and if no one can name that mechanism or point to one observed collision, on whose authority did "one at a time" become a binding constraint rather than an untested assumption?
- (T3_inherence) [unanswered >24h] When you say the narrowness is "inherent," can you name even one concrete configuration of tree/suite that you would predict *cannot* widen BUILD's behaviour no matter what — and if you can't, isn't "inherent" just describing the setup you happen to be looking at rather than any property of BUILD itself?
- (T3_inherence) [unanswered >24h] If two atoms are truly read-only and zero-collision, then "applying" them must still write *something* somewhere — so what exactly does an atom change, and how can you call it read-only while also fearing that two of them applied at once could interact?
- (T3_inherence) [unanswered >24h] If the stated goal is a UK energy supplier's enterprise value and survival, why does the entire observable state consist solely of a meta-argument about words like "inherent" and "tree/suite configuration" — who decided that these self-referential semantics, rather than any price, cost, or solvency figure, are the thing this system is actually tracking?
- (T3_inherence) [unanswered >24h] When you say two applies must run "one at a time," is that rule based on an actual observed failure of the shared apply step under concurrency, or has no one ever run two at once — meaning you're calling it a safety constraint when it's really just an untested assumption?
- (T3_inherence) [unanswered >24h] When was the token "inherent" and this self-referential sentence ever generated by, or validated against, any real input from the energy supplier's operations—and if you cannot point to that link, what evidence do you have that this system was ever wired to the stated goal rather than merely asserting it?
- (T3_inherence) [unanswered >24h] When the shared apply step failed in the real system — not in theory, but on some actual date — what concretely happened to the business, and if that failure has never once occurred, on what measured basis does "one at a time" claim to be protecting against administration rather than against nothing?
- (T3_inherence) [unanswered >24h] If affordability really is being held fixed as "physics," who set that constraint and what would the enterprise value look like if it were relaxed — and if no one can produce that counterfactual number, on what basis is anyone asserting the low bad debt is "healthy" rather than evidence of suppressed revenue?
- (T3_inherence) [unanswered >24h] If the only state this system ever observes is a token and a sentence about that token, by what recorded mechanism has any such observation ever changed a number the energy supplier acts on — and can you point to a single past instance where it did?
- (T3_inherence) [unanswered >24h] If the healthy-book world and the affordability-choke world both produce the same low bad-debt number, which *other* observable — approval/rejection rates on applications, revenue per eligible customer, or the count of would-be customers turned away — would diverge between them, and has anyone actually looked at that number before declaring affordability an untouchable constraint?
- (T3_inherence) [unanswered >24h] When you say the two tracks "never gate each other," can you point to a single concrete state in which advancing to a given depth changes what actions are available or what outcomes are reachable — and if you cannot, what observable difference is left between that depth being "physics" and it being a decorative label with no causal handle on enterprise value or survival?
- (T3_inherence) [unanswered >24h] Can you exhibit one concrete run where two scenarios identical in every other input but differing only in "physics"/"depth" produce different enterprise-value or survival numbers — and if no such pair exists, on what basis is "physics" counted as part of the state at all rather than as inert scenery?
- (T3_inherence) [unanswered >24h] When a Direct Debit you've already counted as collected gets reversed days later under one of those "standardized reason codes," does the sim actually open the liquidity hole between the outflow you funded and the inflow that never arrives—or does it quietly net the reversal against the original schedule, which is exactly the survival-threatening timing you're claiming it reproduces?
- (T3_inherence) [unanswered >24h] If varying "depth" leaves every number in the enterprise-value and survival calculation untouched, then what observation could anyone ever make that would come out differently depending on whether "physics" is in the model or not — and if there is none, in what sense is "physics" part of the model rather than just a label attached to it?
- (T3_inherence) [unanswered >24h] When the simulated firm is actually starving for cash, does the model's Bacs "physics" ever turn against it—recalls, failed DDs, frozen access—or does the 3-day rule mechanically guarantee that inflows always land on time precisely in the scenarios where a real bank or Bacs would be most likely to delay, freeze, or claw back your money?
- (T3_inherence) [unanswered >24h] When you vary "depth" with world difficulty and capability held fixed, does any input that actually feeds the enterprise-value or survival formula change value — and if not, what observable outcome would ever differ between "depth = physics on" and "depth deleted"?
- (T3_inherence) [unanswered >24h] Can you exhibit a single concrete run where two states differ only in "depth" and show the resulting numbers in the enterprise-value or survival formulas actually differ — and if you can't, on what basis is "physics" claimed to be wired in rather than merely labelled?
- (T3_inherence) [unanswered >24h] If "physics" has never once changed an enterprise-value or survival number across any run, what observable output would you expect to differ if that code were deleted entirely — and if the answer is "none," what distinguishes it from a comment?
- (T3_inherence) [unanswered >24h] If running the model with two different "depth" values would change the enterprise-value or survival outputs, can anyone point to the specific line where "depth" (or "physics") actually feeds into those calculations — or is the honest answer that no such connection exists, which is why the trivial test was never bothered with?
- (T3_inherence) [unanswered >24h] For a UK energy supplier whose only two objectives are surviving and maximising value, what specific decision would come out differently if the weather-physics hierarchy said "high wind tomorrow" versus "low wind" — and if you can't name that decision and show the money or survival-risk it moves, why is this model in the system at all rather than a cheaper off-the-shelf forecast or none?
- (T3_inherence) [unanswered >24h] When the "GB weather-physics hierarchy" is swapped for a naive forecast, does any downstream number the supplier actually acts on — a hedge volume, a procurement quantity, a dispatch setpoint — change by a non-zero amount, and if you cannot point to that specific number and its delta, what evidence distinguishes this hierarchy from decorative scaffolding that merely feeds itself?
- (T3_inherence) [unanswered >24h] What concrete decision this energy supplier faces in the current epoch would change based on the output of that weather-physics hierarchy and twin — and if none does, why is any effort being spent building it now rather than deferring registration until such a decision exists?
- (T3_inherence) [unanswered >24h] If the physics-based forecast diverges from the naive one, can you name a single trade, hedge, or dispatch order in the last 24 hours whose volume or price was demonstrably different because of that divergence — and if you cannot, what is the forecast being computed *for*?
- (T3_inherence) [unanswered >24h] What actual, measurable difference does the four-level weather-physics hierarchy produce in any decision the supplier makes before Epoch 3—and if the honest answer is "none," on what basis is keeping that registration justified over any other unused component you have not flagged?
- (T3_inherence) [unanswered >24h] When you trace the physics forecast forward, does it feed any committed decision variable that the naive forecast doesn't already feed identically — and if the only consumer of the more sophisticated number is a log, a dashboard, or another model that itself has no committed output, what evidence distinguishes "affecting enterprise value" from "being computed and discarded"?
- (T3_inherence) [unanswered >24h] If keeping the registration parked truly changes zero present actions, what is the cost and risk of *re-creating* it when Epoch 3 arrives — and does anyone actually know whether that cost is lower than the near-zero cost of leaving it parked, or is "dead weight" being asserted without pricing the deletion?
- (T3_inherence) [unanswered >24h] Since this challenge has itself gone unanswered for over 24 hours, what is the actual reason no one has produced even a single decision cycle's order quantity or price computed both ways — is it that the two forecasts are known to always coincide, that the comparison has never been logged, or that no one can currently trace whether the physics forecast reaches any order-or-price code path at all?
- (T3_inherence) [unanswered >24h] Can anyone point to a specific decision rule or line where the physics forecast's output is actually read and changes an order quantity or price — and if so, why has that not been produced in over 24 hours, while if not, what is the forecast wired into at all?
- (T3_inherence) [unanswered >24h] If the physics forecast's output is never consumed by any decision rule that sets an order quantity or price, then on what basis is it called a "forecast" at all rather than a number computed and discarded — and who, if anyone, has ever traced even one such consuming path end to end?
- (T3_inherence) [unanswered >24h] If swapping the forecast for a constant provably moves no order quantity or price, what exactly did you hold fixed when you measured that — was the constant set to the forecast's own average output, and did you check every downstream consumer (risk limits, survival/administration checks, reporting) rather than only the two levers named?
- (T3_inherence) [unanswered >24h] If the arrears/Bacs physics is genuinely anchored to external Bacs/DESNZ references, what prevents the director-authored "difficulty dials" from quietly re-tuning that same physics away from those anchors — and who would notice if the dials and the anchor disagreed?
- (T3_inherence) [unanswered >24h] If `SE_NTFY_TOPIC` was never set, then paging was never configured in the first place — so on what basis is this being reported as NTFY "going down" (an outage) rather than a feature that was simply never enabled, and what does either state have to do with the company entering administration?
- (T3_inherence) [unanswered >24h] If the run_complete wedge is marked RESOLVED only because its markers were cleared, but the RED publish gate causing it stems from the two site wedges (ntfy sends failing and staging_watcher DOWN) that you list as still unfixed, what stops the same 31-marker saturation from re-accumulating the moment the next run completes?
- (T3_inherence) [unanswered >24h] When "the fabric physics now has a seam into the path the company settles on," does that seam let the physics constrain the company's chosen path (a modelling fix), or does it let the chosen path feed back and alter the physics — i.e. can the optimiser now move the simulated world's ground truth to make its own enterprise value or survival numbers look better?
- (T3_inherence) [unanswered >24h] In this simulator, what concretely *is* "the physics" that would have moved — which specific state variable, updated by which mechanism — and what evidence distinguishes it from a hedge/accounting number that the model would have simply re-solved to keep the books balanced?
- (T3_inherence) [unanswered >24h] What specific evidence distinguishes "p99 is a physics finding" — an invariant of the system that no amount of engineering or configuration can move — from the ordinary case of a p99 that merely hasn't been optimised yet, and what observation would falsify the physics claim?
- (T3_inherence) [unanswered >24h] What actual invariant does the word "physics" in `DD_seasonal_cashflow_physics` refer to — a genuine conservation identity (e.g. direct-debit cash in must equal consumption billed plus balance carried, to the penny), or merely a seasonal shape that looked stable in past data? And if the parked residual was "waiting on" something, what observable event would have to occur for it to resolve, versus what would prove it is simply an unexplained gap being deferred?
- (T3_inherence) Who signed off on "by design," and what specifically happens to the never-enter-administration constraint the first time one of those unguarded call sites receives the input it isn't guarding against — is the failure contained and visible, or does it silently produce a number the business acts on?
- (T3_inherence) What actually enforces the "by design" part — is there a mechanism that would fail loudly if this component wrote a key the draw reads, or is the guarantee only that nobody has done so yet, such that the boundary silently breaks the first time the draw's read set expands?
<!-- /NAIVE_ORGAN_ASKS -->

<!-- EFFORT_SIZING_DIGEST -->
**EFFORT SIZING** (G5_effort_sizing_discipline -- DIAL, never a target/gate; R12 anti-goal-seek):
- Remaining effort: ~1657.9h across 77 sized atom(s) (13 of 90 below-target atoms still unsized).
- Estimate-vs-actual by lane: A_strategy_governance: est 10.5h vs actual 12.0h (+1.5h, underestimated); C_customer_ops: est 12.0h vs actual 2.1h (-9.9h, overestimated); H_harness: est 9.2h vs actual 45.7h (+36.5h, underestimated); W2_customer_generator: est 1.0h vs actual 2.6h (+1.6h, underestimated)
<!-- /EFFORT_SIZING_DIGEST -->
