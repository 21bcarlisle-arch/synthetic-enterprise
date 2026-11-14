**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Nothing logged is left to malinger: triage every open list, and mine it for knowledge and insight

**Type:** STEER, through the advisor channel. The director's words, from chat, Sat 14 Nov:

- 06:43 GMT: "Do we log issues with the world and simulation that are outstanding? I saw something on the website that implied we log these"
- 06:45 GMT: "Before we do that. Is it prioritising fixing these and not just listing and forgetting?"
- 06:46 GMT, approving the advisor's proposal (a one-off triage, an age rule in the learning loop, then a generated Known Issues page): "Yes. We also need to see if there is a knowledge gap or useful insight available. Are there similar lists malingering elsewhere on other topics, supplier etc"

## What the advisor measured on origin (Sat 14 Nov, 06:45)

| List | Open | Concern |
|---|---|---|
| `docs/staging/*FINDING*` | **184** | Only **9** are named in `priority_order.yaml`, `DIRECTION.yaml` or the map. 145 are older than 14 days and 56 older than 28. The oldest is 2 Oct (for example, newly rolled households spiking for six weeks, a world defect). 11 are BLOCKING. |
| Knowledge-page `GAP`s | 836 mentions in 96 files | There is no ranking of which GAP, if closed, would change a world parameter, a supplier decision or a published figure. |
| Maturity map | 31 `blocked_on`, 19 parked | Unknown how many are still blocked on something real. CLAUDE.md warns about rows "blocked on something that was abolished weeks ago". |
| `open_question_register.json` | 182, of which **21 answered "wrong"** | A belief that proved wrong is an insight. Unknown whether any reached the insight layer. |
| Staging proposals and notes | 8 older than 21 days | For example, the 11 Oct personal payment plan proposal and the 15 Oct advisor question on batch-then-bisect. |
| `coupled_gap_ledger.json` | 16 atoms | World-supplier gaps. Unknown which are being closed. |
| `docs/staging/console/` | 27 files of his console words since Aug | Has every ask in them reached a disposition? |
| Queued director steers | several, after the reset | Each must sit in `priority_order.yaml`, not only in done/. |

These are counts, not verdicts. Many findings may already be fixed and simply not closed. The point is that nobody knows.

## What is asked

1. **One triage pass over every list above.** Each item gets one disposition, with evidence:
   - **fixed** (close, citing the commit or gate that shows it);
   - **real** (rank it by whether it changes money or a customer outcome first, then fidelity, then tooling, and put it in `priority_order.yaml`);
   - **parked** (with a reason and a date to revisit);
   - **obsolete** (with the reason).

   Start with the 184 findings and the 11 BLOCKING, then the map's blockers, then the rest.
2. **For every item still real, ask the two questions he added.**
   - Is there a **knowledge gap** behind it? That means a number or rule no published source establishes, or one we have not yet looked for. Find it, then check the commons and published evidence first, under K8.
   - Is there an **insight** in it? That means a pattern across items, a wrong belief, or a cause shared by several items. File insights in the insight layer with a trust grade, on the side they belong to: world, supplier, or building it.

   The 21 "wrong" answers in the question register are the first place to look.
3. **One age rule, applied to all of these lists.** No item stays open more than about **three weeks** without a decision: fixed, scheduled in `priority_order.yaml`, or parked with a reason. A money or customer item is scheduled the day it is raised. Make the rule mechanical, and make "items past three weeks with no decision" one of the learning loop's measures, with a target of zero.
4. **Then the Known Issues page**, generated from the triaged lists and not written by hand. Group it by world and supplier, with the tooling items apart. Show for each item what it affects, its age, and what is being done. Fill the empty `map_of_ignorance` on the fidelity page from the same source.
5. **Do not build a new register.** Build on the staging rooms, `priority_order.yaml`, the map, the question register and the insight layer. If two lists hold the same kind of thing, propose merging them.

**Budget.** The triage is correctness and backlog work, not the feature third. Keep within the 0.45 points an hour pace until the Monday reset. Say in Sunday's balance proposal how far it got, what it found, and what is left. The page and the age rule can follow in the week of 16 Nov.

## Addendum, Sat 14 Nov 06:55 GMT: prevent the recurrence, not only clear the pile

The director's words: "Will this prevent reoccurrance?"

The advisor's answer to him was "partly". The triage clears the pile and the age rule catches the next one late. Neither removes the cause. What is asked in addition:

1. **Find the cause first, as the learning loop's next worked case.** The advisor's reading is that findings are not an input to the work draw. The draw follows gates and cold reads, which are fresh, ranked signals. A finding is a cheap "done" output that lands in a pile the draw never reads. Confirm or refute that against origin's history, and state the cause plainly.
2. **Raising a finding is entering the queue.** A finding enters the draw when it is written, with a rank, and is not filed somewhere for later. That is one mechanism, not a second list.
3. **Cap the backlog against capacity.** When open real items exceed what the machine can fix in about three weeks at its measured rate, it must choose: park with a reason, or ask for a rebalance in the weekly review. It must not accumulate.
4. **Guard against gaming the measure.** "Zero items past three weeks" can be met by parking everything. Every parked item carries a reason and a revisit date. The weekly balance review shows these each week, and the advisor spot-checks a sample:
   - the count parked;
   - the count fixed;
   - the count past three weeks.
5. **The advisor's side.** The advisor reads these three numbers in every weekly review and raises it with the director if parking grows faster than fixing.
