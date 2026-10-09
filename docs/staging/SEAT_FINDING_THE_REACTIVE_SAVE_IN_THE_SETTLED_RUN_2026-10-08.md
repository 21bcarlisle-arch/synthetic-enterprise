**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# The reactive save in the settled run: does it still beat never offering, and do the stayers pay for it?

*Delivery seat, 2026-10-08. Direction item `a-save-offer-is-not-paid-for-by-the-stayers`. The director made
`0f1fb3f6a`'s result conditional: "a save must never be paid for by raising the price of customers
who stay". It may not be published until that is shown in the settled run.*

## What was built

- **The switch.** `docs/design/curriculum/save_on_loss_notice_activation.json`, **off**. With it off the
  save branch in `simulation/run_phase2b.py` is never entered.
- **The world.** A household the renewal roll sends away, on a switch that sends the loser a CSS
  Invitation to Intervene (`4805420bd`, requests from 18 July 2022), is offered a save. The world
  re-asks **the same roll** at the save's price (`simulation/save_on_loss_notice.py`). No save
  probability is added. `world_save_response_scale` is a labelled sensitivity on the world's
  response, used only to reach the ends of the published save-rate range.
- **The company.** `company/interfaces/save_offer.py` is the door and `company/crm/save_offer.py` the
  desk. The offer is a Fixed Retention Tariff: domestic, fixed term, priced at the renewal offer less
  `DecisionPolicy.save_offer_cut_share`. That share is **None on every standing policy**, because no
  figure establishes a save's size (`q4_save_offer_cost_share_of_annual_bill`, GAP).
- **The arms.** `tools/save_on_loss_notice_arms.py` runs `off`, `on` and `placebo`. The placebo saves
  the same households, decided by the world at the save's price, but bills them at the renewal
  price. So `on` against `placebo` holds the book's composition fixed and isolates the save's price.

## Found while building, before the measurement: the save's cost was recovered from the stayers

A smoke pair (2016-2017, CSS gate patched open so saves could happen, response scaled to 50) moved
**50 stayer account-terms, 9 of them up**. Two channels, read off the margin feed:

1. **The save's own cost.** A saved term's margin is thinner by the cut, and
   `EndedTermMargins` feeds every later renewal's portfolio premium. So the cut was recovered from
   everyone renewing after it. **Fixed:** a term held on a save no longer enters that feed
   (`_held_on_a_save` in `run_phase2b.py`).
2. **The book's composition.** A saved household is not replaced. In the smoke, C3 was saved, so the
   run never acquired C3_2, whose first default-tariff segment carried a 24% margin. Its absence
   moved the premium, in both directions. **This is not the save's cost.** It is a different book.

The `on`/`placebo` pair is how the two are separated.

## Pre-registration (filed before the minutes-tier runs)

**Runs:** `report_end` 2024-12-31, base seed as configured, cut share **0.04** of the renewal unit rate.
0.04 is the decision set's GBP 7.5/MWh over its 2016-2024 mean electricity default of GBP 192.6/MWh;
it is an experimental setting, not a sourced size. The arms:
`off`; `on` and `placebo` at the world's own response (k = 1); `on` at k = 0 (the 0.0 end of
`q4_save_rate_on_loss_notice`); `on` and `placebo` at k = 0.041 / (the settled run's own implied
rate at k = 1), the 0.041 end. Also `off` on the parent commit, for byte-identity.

**Predictions, written before any of these ran:**

- **P1, byte-identity.** `off` on this code equals `off` on the parent: the same `total_net` and the
  same unit rate on every account-term. And `on` at k = 0 equals `off` on both.
- **P2, the director's condition (the save's cost).** `on` against `placebo`: **zero** stayer
  account-terms move, at k = 1 and at the 0.041 end. A move here reds the control.
- **P3, composition.** `on` against `off`: some stayer account-terms move, in both directions, with a
  median absolute move under 1% of the rate. Reported, not a pass/fail.
- **P4, vulnerability.** Zero twin shortfalls. A vulnerable household in the same position is never
  offered a higher save price. This holds by construction under a flat cut, so it is a guard on
  future sizing rather than a finding.
- **P5, value.** The settled run's implied save rate at k = 1 falls between 0.02 and 0.05 (the
  decision set gives 0.029 to 0.037 at GBP 7.5-10/MWh). **I cannot predict the sign of `on` minus
  `off` in total net with confidence.** Saves only start in late 2022, when renewal margins in this
  world may be negative, and saving a household at a negative margin loses money. My best guess is
  positive at k = 1 and larger at the 0.041 end, each under 1% of total net.

## Amendments, 20:46-21:15 BST, written before any arm of THIS code reported

This build was salvaged from the 14:19 attempt (`17495e30d`, a fork_salvage commit, never landed) and
finished by the 19:46 one. Three changes, each beside its reason:

1. **The guard was not in the salvaged code.** `_held_on_a_save` was set and never read; the margin
   feed still took a saved term. The salvage most likely caught the build mid-mutation (the control's
   docstring reports a measurement "with the guard deleted"). Restored: `if term_revenue > 0 and not
   _held_on_a_save` in `run_phase2b.py`.
2. **Vulnerability is now the company's own knowledge.** `d29dcddc3` landed vulnerability as a hidden
   household state the company learns only by disclosure. The save door now takes the company's
   Priority Services Register, built from the disclosure wire, and offers as vulnerable iff the point
   is registered on or before the switch. The log carries `known_vulnerable`, never the latent state.
   P4 is graded on those households' ACTUAL offers, plus a second leg: no known-vulnerable leaver
   holding an Invitation goes unoffered while plain leavers are offered.
3. **The save-rate range's denominator was wrong in P5 and in the arm list.** `q4_save_rate_on_loss_notice`
   (0 to 0.041) counts saves **per domestic switch away**. P5 and the 0.041-end scale used saves per
   *offered* leaver, a much smaller population (fixed-term leavers holding an Invitation). Matching that
   to 0.041 would overstate the world's response. The tool now also reports
   `implied_saves_per_domestic_switch_away_from_css`, and the 0.041 end is set on that denominator.
   The three arms launched at 20:49 (`off`, `on`, `placebo`, k = 1, cut share 0.04, to 2024-12-31)
   predate that field. Their departure count comes from a later run.

**Seen before these amendments, so not a prediction:** the 17:19 attempt (code lost, no ref holds it;
outputs in `/var/tmp/save_fairness/`) ran a full window with a GBP 7.5/MWh cut. It made **14 save
offers in the whole run, all from 2023-12-21**, and **saved nobody at k = 1**: total net was identical
to `off` at GBP 198,348. Implied per-offer save rate was 0.076. At k = 20 it saved 10 of 15, and net was
GBP +3,043. So I expect `on` at k = 1 to save 0 or 1 of about 14, and **any net difference to be within
one household's margin**: the book cannot tell the save's value at either end of the range.

## Amendment, 23:00 BST, written before the top-end arm reported (successor, `the-reactive-saves-zero-end-and-its-departure-denominator`)

**The departure count was not short, and the denominator was mixed across arms.** `off` started 11
domestic switches from CSS go-live, and all 11 were Invitation-held fixed-term leavers. In the `on` k = 1 arm,
PROS-2022-0400 was saved on 2023-12-21 and sent a **second** loss notice on 2024-12-20, so that arm
started 12. "11 < 12" compared two worlds. The defect was in `compare`. It borrowed `off`'s
departures as the denominator for `on`'s saves, and its departures left out the saved households,
which started a switch too. The fix is `switch_attempts_from_css`: the arm's own departures plus its
saves, never another arm's. An arm without recorded departures falls back to its own
Invitation-held notices, labelled "at least". The control is
`test_the_save_rate_denominator_is_the_on_arms_own_switches_and_never_undercounts_them`. It reads
9 against 12 on the old code (run 2026-10-08). The implied per-switch rate now also uses the arm's own
response scale. Before this it read the k = 1 curve in every arm, so the k = 0 arm reported 0.024
having saved nobody. That leg is mutation-proven too (0.1 against 0).

**The k = 1 rate, exactly:** expected saves 0.5328 over **12** switches started = **0.0444** per
domestic switch away, from CSS go-live to 2024-12-31. This is just above the published ceiling of 0.041. So
the 0.041 end is **k = 0.041 / 0.0444 = 0.9234**, and `on` at that k was launched at the unit start time below
(`longjob-save-arms-on-k0923`, artefact `/var/tmp/save_arms/on-k0923.json`) from the landed code
(`14c5deea3` = `bfcae065d`'s tree on these paths).

**Placebo at the top end, replaced by a stronger test.** If `on` against `off` moves 0 stayer
account-terms, then the stayers pay neither for the save's price nor for its composition, and that is
P2 and more. A `placebo` arm is run only if `on` against `off` moves a stayer.

**Predictions for the top end:** the same roll at a smaller scale saves a subset of k = 1's saves,
so **1 or 2 accounts saved**; **0 stayer price moves** against `off`; `on` minus `off` **positive and at most
+GBP 1,749**. The subset can drop a loss-making save, so a figure above 1,749 would refute the last one.

## Result

*(Filled after the runs, below this line. Nothing above is edited after it.)*

### Run, 2026-10-08 20:49-21:28 BST, code at `7981270d0` plus this change, to 2024-12-31, cut share 0.04

All three arms used the same base seed and window. `off` was OOM-killed once, by my own co-running
jobs, and relaunched; its result is one clean run. Raw: `/var/tmp/save_arms/{off,on,placebo}-k1.json`
and the `cmp_*` files beside them.

| | `off` (never offer) | `on`, k = 1 | `placebo`, k = 1 |
|---|---|---|---|
| total net, GBP | 178,413 | **180,162** | 180,471 |
| on/placebo minus off, GBP | | **+1,749** | +2,058 |
| renewal-point departures | 35 | 33 | 33 |
| loss notices with an Invitation held (all from 2023-12-21) | | 12 | 12 |
| offers made / terms saved / accounts saved | | 12 / 3 / 2 | 12 / 3 / 2 |
| offers to a household the company knew was vulnerable | | 2 | |
| stayer account-terms compared, against `off` | | 4,898 | 4,898 |
| **stayer prices that moved / were raised** | | **0 / 0** | 0 / 0 |

`on` against `placebo` (the save's price alone): 4,900 stayer account-terms compared, **0 moved**.
The save's own cost is the gap, GBP 309, and the saved households carry it.

**P1 (byte-identity): HALF HOLDS, HALF STILL UNGRADED (successor, 2026-10-08 23:00).** `on` at k = 0 equals `off`. The account_state lists are identical across 4,898 account-terms, total net is GBP 178,413.248132 in both, 0 saved, and 11 offers were answered and declined. `off` on the parent was never run to 2024-12-31, so that half is still ungraded. The original text follows. ~~NOT YET GRADED.~~ No arm of the parent ran to 2024-12-31. The one difference with the
switch off is the roll's records argument, which moved from positional to keyword under the same names
(`roll_lifecycle_event(customer_id, term_start_str, commodity, records_so_far, customers, ...)`).
`on` at k = 0 was launched at 21:43 (artefact `/var/tmp/save_arms/on-k0.json`) and is graded by the successor.
**P2 (the director's condition): HOLDS at k = 1.** 0 of 4,900 stayer account-terms move between `on` and
`placebo`. The control reds when the guard is deleted (run 2026-10-08 21:00, `stayer_price_moves`
non-empty).
**P3 (composition): REFUTED.** I predicted moves in both directions; there were **none**. 0 of 4,898
stayer account-terms moved between `on` and `off` either. Two households kept out of 452 did not move
the premium any stayer was priced on in this window.
**P4 (vulnerability): HOLDS, with a subject.** 2 of the 12 offers went to households the company knew,
from its own disclosure register, to be vulnerable. 0 were offered above their twin, and 0
known-vulnerable leavers holding an Invitation went unoffered.
**P5 (implied rate): OUTSIDE MY RANGE, on the definition I wrote it against.** The implied save rate
**per offered leaver** is 0.093 at k = 1, above the 0.02-0.05 I predicted. On the published
denominator, per domestic switch away, it is **at most 0.044**: expected saves 0.533 over at least
12 departures (the 12 leavers who held an Invitation). So the world's own response sits at about the
**top of the published range** (0 to 0.041) and possibly inside it. The tool's own departure count
read 11 in `off`, fewer than the 12 leavers `on` offered, which cannot be right. **That count is
unresolved and not used.** It is the successor's first job. *(Resolved, successor 23:00: the count was right, and the tool compared two arms' worlds. Exactly 0.0444 over 12 switches started. See the 23:00 amendment.)*

### Does the reactive save still beat never offering in the settled run?

*Rewritten 2026-10-08 23:15 BST by the successor, with both ends of the published range (0 to 0.041
per domestic switch away) graded exactly. The earlier text said "at most 0.044" at k = 1 and left the
0.0 end ungraded.*

| | `on` at k = 0 (bottom end) | `on` at k = 0.9234 (**top end**) | `on` at k = 1 (world's own) |
|---|---|---|---|
| expected saves per domestic switch started from CSS | **0.000** | **0.0414** | 0.0444 |
| switches started from CSS (own arm, departures + saves) | 11 | 12 | 12 (at least; departures unrecorded) |
| accounts saved / terms saved | 0 / 0 | 1 / 2 | 2 / 3 |
| `on` minus `off`, total net, GBP | **0.00** | **+1,679** | +1,749 |
| stayer account-terms moved against `off` (of 4,898) | 0 | **0** | 0 |
| known-vulnerable offered / twin shortfalls / left unoffered | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |

> **Rests on the pre-correction world (arrears ~10x too high); re-graded by the 400-founder end-to-end run on the corrected world.** *(Marked 2026-10-09; corrections 23fca0567, 54dbd5650.)*

- **At the bottom of the range: it TIES never offering, exactly.** Total net and every account-term's
  price are identical to `off`.
- **At the top of the range: it BEATS never offering by GBP 1,679 (about 0.9% of total net), and no
  stayer's price moves at all.** The 0.041 end saves **one household**, PROS-2022-0400, at
  two consecutive renewals. That is a direction from a single customer, not a size. One household's
  margin either way moves it by the same order, and one seed gives no sampling bound.
- **Top-end predictions: all three held.** 1 account saved (I predicted 1 or 2), 0 stayer moves,
  and +1,679, which is positive and at most 1,749. The k = 1 save of PROS-2023-0230 is the one the
  smaller response drops, and it was worth about GBP 70.
- **P2 at the top end is held by the stronger test, so no `placebo` was run.** `on` against `off`
  moves no stayer, so the stayers pay neither for the save's price nor for its composition.

### The departure share, labelled

**Renewal-point departures of the whole book, 2016-01-01 to 2024-12-31, one seed:** 35 with saves off and
33 with them on (k = 1), counted as `customer_events` with `departure_occasion == "renewal"`. **What it
counts:** one event per departing account at a renewal point, all fuels and segments, over nine years.
It is neither a rate nor focus one's per-ender 42-day share (`7981270d0`). A per-ender share on that
definition needs the ender population from the run. This tool does not yet record it, so I do not
compute one here.
