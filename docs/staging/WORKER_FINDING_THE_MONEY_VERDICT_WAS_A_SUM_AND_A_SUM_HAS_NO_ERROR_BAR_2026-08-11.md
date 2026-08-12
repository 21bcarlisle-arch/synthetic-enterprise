# WORKER FINDING — the money verdict was a difference of two sums, and a sum has no error bar

**Severity:** BLOCKING · **Lane:** H_harness

**Atom** `H_GAP_fabric_belief_truth_gap` (H_harness, level 2, `loop_stage: build`)
**Date** 2026-08-11 · **FIFTH Expert Hour** on this machinery, run under the termination
condition the previous four wrote for themselves: *an Hour finding nothing NEW moves the
level.* **It found something, so the level stays 2.**

**Directed question, set by the fourth Hour verbatim:** *"the next starts on
`panel_mirror_normaliser_drift` and the MONEY half of `_favours`."*

---

## The short version

The fourth Hour repaired `accuracy_favours` — a relative band on the difference of two
aggregate population gaps, no error bar — into a paired per-premise bootstrap. In its own
NOT-DONE section it wrote:

> the MONEY half of `_favours` is still a band on two aggregate GBP sums with no error bar
> (its decisiveness DOES improve with N, so it is not obviously the same defect, but the
> confidence mirror already flips it)

**It is the same defect.** Improving with N is not the absence of the failure; it is the
failure read from the wrong end.

---

## Measured, not argued

120 random subpanels of this atom's own **drawn** population, at each size:

| n | aggregate rule decisive | paired evidence decisive | **published a verdict the homes cannot support** | direction disagreements |
|---|---|---|---|---|
| 25 | 75% | 13% | **62%** | 0% |
| 50 | 87% | 59% | **28%** | 0% |
| 100 | 98% | 100% | 0% | 0% |
| 150 | 100% | 100% | 0% | 0% |

The over-claim column does not fall with N because the rule learns. It falls because a
missing error bar was only ever going to bite while the panel was small — and the rule is
**most confident exactly where it is least entitled to be**. The accuracy verdict's failure
signature was *decisiveness FLAT IN N*; this one's is *decisiveness DECOUPLED FROM N*.
A rule that is 75% decisive on 25 homes is not reporting evidence, it is reporting that a
sum of 25 numbers is rarely exactly equal to another sum of 25 numbers.

**And the authored panel — one of the two PUBLISHED populations — is in that regime.**

* n = 15. The aggregate rule reads **57.7% of the larger**, eleven times the materiality
  band, the single most decisive-looking number in the row.
* **Four** of the fifteen premises differ at all, and **one of them carries 80.6%** of the
  margin (GBP 20,466 of 25,379).
* The paired interval is **[+GBP 3, +GBP 4,736]** per premise against a point of +1,692.
  **Dropping any ONE of those four premises makes it unresolvable** — while the aggregate
  rule survives every single-premise deletion in the panel (0 of 15). A headline that
  cannot notice it is one house is not a headline about a stock.

**Direction was never wrong**, exactly as with accuracy: over 249 decisive subpanels the two
rules never named different arms, and every premise that differs at all favours the
inference (+4/−0 authored, +16/−0 drawn). That is what let it survive five Hours — an
over-confident verdict that happens to point the right way reads as a strong result, and
nothing in the row said how much of it was one home.

## The other half of the directed question: `panel_mirror_normaliser_drift`

**Examined and REFUTED by measurement — it is the quantity it names.** The term recovers the
no-skill baseline by division (`register_mae / gap`) rather than reading `GapResult.g0`,
which is the shape that usually hides a reconstruction error. Measured against the direct
`g0` on both published populations: **identical to six decimals** (0.123681 vs 0.123681
authored; 0.018725 vs 0.018725 drawn; g0 0.092495→0.081055 and 0.104879→0.102916). No
finding.

**One real defect there, and it is small and now written down rather than fixed by
accretion:** `MIRROR_FIDELITY_BAND` gates `panel_mirror_register_infidelity` (a per-premise
kW/K MAD ratio) **and** triggers the yardstick disclosure on `panel_mirror_normaliser_drift`
(a relative move of the truth population's spread) — one constant, two subjects, which is
precisely what that constant's own comment says must never happen. Recorded in the new
`ONE_HOUSE_SHARE` comment as the reason the third band is a third constant rather than a
reuse. Not repaired in this Hour: the two subjects agree on both published populations, so
moving one would move no published figure, and inventing a fourth band to prove a point is
accretion. **NAMED, NOT CLOSED** — it is the next Hour's opener.

## A second finding, inside the controls themselves

Retuning the suite for the repaired rule surfaced this, and it is worth more than the
retune: **every cell of the panel mirror's 2×2 (flip × fidelity) was pinned on a money
verdict that was ONE HOUSE.**

* `_fixed_offset_population`, the fixture family behind three cells: on **every**
  parameterisation tried, `largest_premise_share == 1.00`. A fixed offset over 0.10–0.55
  kW/K is 30% of the tightest home and 5% of the loosest, so exactly one premise ever
  decided differently between the arms.
* The FLIP cell was unreachable from any fixture in the file under a verdict with an error
  bar. **400 randomised panels produced exactly one** that flips a resolvable verdict into a
  different resolvable verdict with an attributable mirror. That it took 400 draws is the
  point: a composition flip that survives an error bar on both sides is RARE, and the old
  suite made it look routine.
* The R15 fixture for `MIRROR INCONCLUSIVE` was a two-premise margin called decisive.

## What was mechanised

* `PremiseForgone` + `_premise_forgone` — the money consequence per premise, lifted out of
  `money_consequence`, which now aggregates it. **One definition**, pinned by a test that the
  sum reproduces `forgone_lifetime_gbp` exactly and every count agrees. Zero-forgone premises
  are rows, not absences: a resample that dropped them would resample a different panel from
  the one the totals are quoted over (mutation M8).
* `MoneyVerdict` + `_paired_money_verdict` — paired per-premise advantage
  (`forgone_epc − forgone_inferred`), percentile bootstrap CI on a **named C-S2 substream**,
  `neither` where the interval straddles zero. Carries the tie count, the
  `largest_premise_share`, and the OLD rule's answer.
* **Applied to ALL FOUR money verdicts** (base, panel mirror, revision mirror, confidence
  mirror) — R10, class not instance. `composition_decided`, `direction_bought` and
  `confidence_bought` are comparisons BETWEEN these verdicts; repairing one and leaving three
  on the aggregate band would measure a paired verdict against an unpaired one.
* `_bootstrap_mean_ci` — one resampler, shared with the accuracy verdict. The accuracy CI is
  unchanged to the bit.
* **Three disclosures, so the repair deletes no sentence and adds the two it owes:**
  `MONEY VERDICT UNRESOLVED` (the aggregate rule named an arm the homes cannot),
  `MONEY VERDICT CARRIED BY ONE HOME` (it resolved AND ≥50% is one premise — the authored
  panel's case, which an interval alone does not cover), `MIRROR VERDICT UNRESOLVED` (the
  mirror reached no verdict at all: read the absence of a flip as NO EVIDENCE, not as
  evidence of no composition effect).
* `ONE_HOUSE_SHARE = 0.50`, a THIRD constant, longhand about why it is not a reuse.
  Populations either side: 80.6% authored, 22.5% drawn.

## R15

**Nine source mutations, each firing its OWN named test, md5 byte-clean restore.** M1
aggregate rule returned · M2 CI ignored · M3 concentration zeroed · M4 overstated-flag
always False · M5 panel mirror left on `_favours` · M6 one seed for every substream · M7
unseeded draw · M8 zero rows dropped from the resample · M9 mirror-unresolved disclosure
deleted.

**M5 initially SURVIVED, and that is the R15 lesson of this Hour.** On every fixture in the
file the aggregate and paired rules happened to AGREE on the mirrored panel, so an arm still
wired to the old band was indistinguishable from a repaired one, and the structural test
(isinstance, interval-contains-point, premise count) could not see it. *A control set with no
population where the controlled thing VARIES is a control that cannot fail.* Fixed by
searching out a 14-home panel where the mirror's two rules disagree, and by asserting the
property that actually distinguishes them: **a verdict must say `neither` exactly when its
OWN interval straddles zero** — plus a guard that the fixture still disagrees, so the
assertion cannot become a tautology satisfied by agreement.

Proven the other way too: the verdict resolves where the panel carries it, names EITHER arm,
and resolves more often as the panel grows.

## No published figure moved

`0.4269` / `0.4042` re-taken on the row's own declared `refresh_args`. Drawn money verdict
stays **inferred**, now earned at **+GBP 485 per premise, 95% CI [+196, +883]**, 184/200
premises forgoing the same under both arms, largest premise 22.5% of the margin. Accuracy
verdict, all three flip caveats (`composition_decided` False, `direction_bought` False,
`confidence_bought` True) and every gap figure unchanged on both populations.

## R10 CLASSES

1. **A verdict on an EXTENSIVE quantity cannot be banded as a share of its own total.**
   Failure signature: decisiveness that does not fall as the panel shrinks. Sibling of the
   fourth Hour's *a band must be measured against the distribution of the quantity it bands*
   — same root, opposite sign: that one silenced a true direction, this one asserted one the
   evidence could not carry.
2. **An interval is not a concentration measure.** A verdict can survive its own error bar
   and still be a statement about one house; both must be said, and only one of them is a CI.
3. **A control set needs a population where the controlled thing VARIES.** Agreement across
   every fixture makes a wiring mutation invisible.

## Two things found while landing it, both pre-existing and both repaired

**1. This atom's map budget was already RED, and this Hour drained it.** Recording the
finding tripped `test_map_within_per_atom_budget` — and the atom was **already over on HEAD**
at 15,735 B against a 12,288 B cap, before this Hour added a byte. Eleven Expert-Hour
narratives had accreted into the governance spine, which is exactly the flow
`records_rehomed: [expert_hour_findings]` was built to drain (H41). Drained: findings moved
verbatim into the store, `expert_hour` keeps `{last, status}`, and the atom is now
**1,349 B — GREEN**. Pinned by a new test, because a drain nobody asserts is a one-time
cleanup and this atom takes an Hour most weeks.

**A bound worth watching, NOT fixed here:** the store file for this atom is now
**98,386 B against its own 102,400 B per-file bound**. Roughly one more Hour of headroom.
Both of this atom's record homes are near their caps; the durable answer is probably a
per-Hour file rather than one growing document, and that is a design change, not a tick.
QUEUED, not fixed on sight.

**2. `test_generate_proof_data_expert_hour_findings` was RED on HEAD**, on an atom this Hour
never touched: it pinned `len(findings) == 11` for `H27_payment_belief_gap`, which took its
twelfth Hour in another lane. **A count of an append-only register is a generated value**, and
pinning one turns every future entry into a test failure while proving nothing the property
does not. Repaired to the property — the reader returns exactly the store, and the store is
non-empty — with the literal kept only as a lower bound.

## NOT DONE AND NOT IMPLIED

* `MIRROR_FIDELITY_BAND` still serves two subjects (above). Named, not closed.
* `VERDICT_MATERIALITY` still decides the four `aggregate_favours` fallbacks. That is now its
  only job and it is a DISCLOSURE of the old rule, never a published verdict — but nothing
  measured whether the aggregate answer is worth showing at all.
* The `weight_null` panel's money figures are still published as raw totals with no interval.

**TERMINATION CONDITION unchanged.** FIVE consecutive Hours have found the same FAMILY — a
published number that is not the quantity it names. The next starts on
`MIRROR_FIDELITY_BAND`'s two subjects and the `weight_null` totals.
