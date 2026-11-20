# The one work system: decision map

Plan item 6 of `docs/operations/WEEKLY_BALANCE_REVIEW_2026-11-16.md` §5, second half. The first
half is the K8 page, `docs/market_research/one_backlog_and_flow_practice_2026-11-20.md`. This map
cites that page by section (K§) and by finding (F1 to F5). The steer is the director's of 14 Nov
(`docs/staging/advisor/done/DIRECTOR_STEER_DESIGN_ONE_WORK_SYSTEM_INTO_THE_HARNESS_NOT_MORE_RULES_ON_MANY_LISTS_2026-11-14.md`),
with its addendum on three lanes.

**Nothing here is built.** The build is item 11. Each decision gives the outcomes considered, the
recommendation and why, and **whether it changes something he ruled**. Under the plan, the map goes
back to him only for those decisions. §7 lists them: there is one (D7, the dials), and it waits for
his go. Everything else goes ahead as item 11.

Written 20 Nov 2026.

---

## D1. Where items live, and how state is kept

| Outcome | For | Against |
|---|---|---|
| a. One JSON or YAML file holding every item | one read | every lane writes one file. The 14 Nov "one writer per shared file" measurement says that is where lanes collide |
| b. An append-only event log (`.jsonl`) | flow measures come free from the event timestamps | concurrent appends in a shared tree; a replay is needed to read the state |
| c. **One small YAML file per item, state as a field, the file never moves** | no collisions between lanes; pathspec commits stay natural; F2 (stranding by location) cannot happen | many small files |
| d. Extend the staging documents' header and keep rooms as state | the least change | keeps F2, which leaves 202 documents stranded today |

**Recommended: c.** Items go in `docs/work/items/<id>.yaml`. The prose evidence (a finding's write-up,
a steer, a run report) stays where it is now, and the item points at it. Arrival, take and close are
recorded as timestamps on the item. **Does not change a ruling.**

## D2. The item shape

The steer fixes the core fields. The K8 page adds the timestamps (K§1.2), and the item-5 measurement
drops the concept link (31a49789f1: a concept link would have surfaced 0 of 3 repeat-defect
families).

```yaml
id:            short-kebab-slug           # one per CAUSE, not per occurrence (K§2 GAP-4)
title:         one sentence
lane:          world | supplier | building # the side; seam-spanning items name ONE owner (D4)
kind:          correctness | feature | knowledge | trial | harness
affects:       [money | customer_outcome | fidelity | method | tooling]
class:         stop_the_line | dated | standard        # K§1.3; dated carries `due:`
severity:      BLOCKING | LATENT | RECORDED            # existing finding_severity scale, kept
source:        finding | gate_breach | cold_read | knowledge_gap | steer | question | seam_gap | alarm | atom_step | census_red
evidence:      [paths, commits]
knowledge_gap: none | <GAP id or knowledge page>       # the director's 06:46 question 1, asked once, at intake
insight:       none | <one sentence>                   # his question 2
decider:       machine | director                      # director => not drawable; feeds the for_the_director view
director_rank: null | int                              # set only from a director-sourced order (priority_order steps)
atom:          null | <maturity-map atom id>
blocked_by:    [item ids]
occurrences:   1                                       # a repeat increments this; it does not mint a new item
state:         open | chosen | done | parked | obsolete
opened_at / chosen_at / closed_at: ISO timestamps
chosen_by:     null | <session or claim id>            # the ONE claim (D5)
done_evidence: null | <commit>                         # required for done
parked:        null | {reason: ..., revisit: YYYY-MM-DD}  # required for parked; on the revisit date it reopens itself
obsolete:      null | <reason>
```

**Does not change a ruling.** The steer specifies this shape.

## D3. What each store becomes

**FOLD** means its open entries are migrated in as items, and the store stops taking writes.
**VIEW** means it becomes a generated query. **KEEP** means it is a record, not a list of waiting
work. **RETIRE** means it is deleted after migration.

| Store (K§3) | Decision | Notes |
|---|---|---|
| Staging root as the queue, and rooms as state | **FOLD**, then **RETIRE** the rooms as state | Each finding becomes one item, with the document as its evidence. Rooms stop meaning state. The advisor channel and console keep their directories as **input channels**, because they are where his words land (G8). |
| `.seat_continuation.json` (2,038 rows, no state: F1) | **FOLD**, then **RETIRE** | Open rows are migrated as items. The rest are closed as obsolete, each with a reason. |
| delivery-lane claims, `.draws`, `.refusals` | **RETIRE** | Replaced by `state: chosen` plus `chosen_by` plus the existing 100-minute return (D5). |
| `.seat_work_in_hand.json` | **RETIRE** | This is the second claim store. MEMORY records that it and the delivery-lane store must be cleared separately. |
| `DIRECTION.yaml` `focus` and `not_now` | **FOLD** | `focus` becomes `director_rank` or seat-ranked items. `not_now` becomes parked items with a revisit date. `thesis_read`, `stretch_reviewed` and `wrong` stay as a **KEEP** record. |
| `DIRECTION.yaml` `for_the_director` | **VIEW** | It becomes a query for `decider: director` and `state: open`. `director_concerns --raise` writes an item. |
| `priority_order.yaml` steps and candidates | **FOLD** into `director_rank` | Its share settings stay as the share table (D6). |
| `director_asks.yaml` | **FOLD** | It becomes an item with `source: steer`. |
| `open_question_register.json` (205) | **FOLD** (open questions only), then **RETIRE** | Answered entries stay in git history. The steer names this store for retirement. |
| `coupled_gap_ledger.json` (19) | **FOLD** as `source: seam_gap`, then **RETIRE** as a store | The coupled-triad *gate* keeps its measurement as an instrument and writes items. The steer names this store too. |
| Nine gap registers (`gap_register_scan.py`) | **sources** | Each register keeps its own instrument. An open row writes an item. `gap_register_scan` as a rest blocker is retired, because a rest is legal only when no item is drawable (D6). |
| HEAD-red register, post-publish reader reds | **sources** | An owed red becomes an item with `source: census_red`. A stale census is one `stop_the_line` item, not a doorbell. |
| `WORKER_FINDING_REPEATING_ALARM_*` (20 in the root) | **FOLD**, deduplicated | One item per alarm, with `occurrences` counting repeats (K§2 GAP-4). |
| `maturity_map.yaml` | **KEEP** as the capability record (levels and evidence) | An atom's **next step** becomes an item with `source: atom_step` and `atom:` set. The map stops being a draw source. |
| `knowledge_map.md` GAPs | **KEEP** | A GAP becomes an item only when it **blocks** something (the steer's wording), through `knowledge_gap:` or `source: knowledge_gap`. |
| `sanity_adjudication_ledger.json` (658), fidelity ledger | **KEEP** as instruments | Open adjudications write items. |
| Known Issues page, map of ignorance, weekly review numbers, the advisor's waiting read | **VIEW** | These are all queries on the item store (D8). |

**The count the steer asks for:**

- **Added:** one store (`docs/work/items/`), one module (pick plus views) and one lifecycle.
- **Retired as stores that must be kept in step:** eight. They are:
  1. the continuation store;
  2. delivery-lane claims, draws and refusals;
  3. seat work in hand;
  4. the open question register;
  5. the coupled gap ledger as a list;
  6. the staging rooms as state;
  7. `director_asks.yaml`;
  8. the `focus`, `not_now` and `for_the_director` lists in `DIRECTION.yaml`.
- **Converted from draw or rest sources into item writers:** about twenty-four supervisor draw and
  detector functions, the nine-register rest check and the twelve-level `authorized_set_enumeration`.

**Does not change a ruling**, with one exception. The 28 Jul ruling PUBLISHED_GAPS_ARE_THE_BACKLOG
is *kept*: its sentence, "a saturation claim is impossible while any published register holds an
open, un-triaged item", becomes "a rest is impossible while any item is drawable". The registers
still write items, so its intent holds by construction.

## D4. Lanes, and items that span the seam

| Outcome | Notes |
|---|---|
| a. One ranked list across all lanes | It breaks the baseline/curriculum split: the world's priority would see supplier results |
| b. **Three ranked lanes on one mechanism: world, supplier and building** | This is the director's 14 Nov addendum |

**Recommended: b, which he has already ruled.**

- The world lane ranks on fidelity and correctness only. **No supplier result field is readable by
  the world lane's order.** The build tests that property: a supplier-side change cannot reorder
  world items.
- An item that spans the seam carries one `lane`, chosen by the interface steward's rule. What
  crosses the seam is the supplier's question. What the world must model is the world's.

## D5. The one claim, and the WIP limit

- **Claim:** `state: chosen` plus `chosen_by` on the item itself. If no landing is bound to it, the
  item returns to `open` after 100 minutes. That is the existing sweep, kept. `--landed` binds the
  commit to the item. This gives one claim store instead of two.
- **WIP limit:** the number of chosen items cannot exceed the worker slots the memory governor
  admits. **The limit is derived from that, not picked** (K§2 GAP-1).
  - An item drawn N times without a landing parks itself with the reason "drawn N times, no landing".
    That is today's pass ceiling, moved onto the item.
  - **N is today's value, carried as-is.** It is flagged in the build as a constant that needs its
    origin declared (`test_a_domain_constant_carries_its_origin`).

**Does not change a ruling.**

## D6. The ranking rule (the one rule that picks)

It lives in one function, `next_item()`, in the build's module. The supervisor calls it and
nothing else chooses work. In order:

1. **Eligible** means all of these:
   - `state: open`;
   - `decider: machine`;
   - every item in `blocked_by` is done;
   - the item is not parked. A parked item whose revisit date has passed has already reopened itself.
2. **Stop-the-line first, across all lanes, with WIP 1.** This is Anderson's expedite class (K§1.3).
   It takes in today's priority-zero rungs:
   - publish-gate wedge (rung 1);
   - persistent operational red (rung 1b);
   - producer starved (rung 1d);
   - a stale HEAD census.

   These are director rulings from 23 and 24 Jul, 25 Jul and 17 Aug, and **their precedence is
   kept**.
3. **Choose the lane by its share.** Take the share row (lane × kind) furthest below its share this
   week, measured on points landed.
   - The share table is the weekly balance review's own rows: supplier feature, world feature,
     harness (which is the building lane), knowledge and correctness. They are written into
     `priority_order.yaml` as they are now.
   - It is deterministic deficit, not a weighted coin. That reduces the variance of the draw (D7).
4. **Error-budget stop inside a lane.** While a lane holds an open BLOCKING item, that lane's
   feature rows are not chosen. This is rung 1c, OPS12, kept (K§1.4). It does not touch other lanes.
5. **Order within the row:**
   1. `director_rank` ascending, so his order is followed exactly;
   2. then `class: dated` whose `due` falls inside the row's median cycle time;
   3. then severity: BLOCKING, then LATENT, then RECORDED;
   4. then **age**, oldest first.

   **No cost-of-delay score is used** (K§2 GAP-2).
6. **Rest** is legal only when no item is eligible. That one query replaces
   `authorized_set_enumeration`'s twelve levels.

**Does not change a ruling**, with the exception in D7. The 11 Nov share ruling ("the weekly balance
review sets each lane's share") is honoured by step 3. A deficit draw and a weighted coin both
deliver the share over a week. The coin was not ruled; the share was.

## D7. The maturity-map dials (THE ONE DECISION THAT GOES BACK TO HIM)

Today, `self-refill from maturity map (dial-weighted)` chooses an atom by a per-lane dial, for
example `W2_customer_generator, dial=50`. Under D3, the map stops being a draw source, and an atom's
next step is an item ordered by D6. Two outcomes:

| Outcome | Effect |
|---|---|
| a. **Retire the dials.** Lane weight comes only from the review's share table | one weight setting instead of two; the dials' intent (work the dial orders is never zeroed) is kept by D6 step 5's age order, under which every eligible item eventually rises |
| b. Keep the dials as a tie-break inside a share row | two weightings kept in step, which is what the steer asks to remove |

**Recommended: a.** CLAUDE.md quotes the dials as his ("everything else is a dial that orders work
but never zeroes it"), so retiring them **may change something he ruled**. It waits for his go
(G9), and it goes in Monday's review (23 Nov). The rest of item 11 does not wait for it: until he
answers, the build can carry the dial as one more input to step 3.

## D8. The views

The steer asks for one view of the whole backlog's health. That is a single generated page, one
section per lane, showing:

- WIP and throughput per week;
- the age of the oldest open item and of the oldest chosen item;
- cycle time (median and 85th percentile);
- arrivals against exits per week;
- the parked count and overdue revisits.

These are the Kanban Guide's four measures, plus the steer's arrival rate and parked count (K§1.2),
all read off the timestamps on the items.

The other views are queries on the same store:

- `for_the_director` (`decider: director`);
- Known Issues (`kind: correctness`, `state: open`);
- the map of ignorance (`knowledge_gap != none`);
- the weekly review's "how is the one backlog flowing, and what share went where";
- the advisor's waiting read.

The figures are **diagnostics, not targets** (R12). None of them gates a commit.

## D9. Migration

The triage now under way is the migration, as the steer says
(`docs/staging/SEAT_RECORD_TRIAGE_OF_THE_BLOCKING_FINDINGS_2026-11-20.md`).

1. Build the store and `next_item()` first.
2. Move one source over (the staging findings), behind a cut-over flag. Run the old ladder and the
   new pick side by side for one day and record where they differ.
3. Migrate the other sources one at a time. **Each migration deletes its old store in the same
   commit.** Done includes deletion, as the steer says.
4. Close the 2,038 continuations last, as obsolete with a reason, except for the ones still open.

---

## Done for item 6, and what item 11 inherits

**Item 6 is done when** this map and the K8 page are on origin and the page's sources are on the
published reading log. **Item 11 is done when** `next_item()` is the only thing that chooses work,
the eight stores in D3 are deleted or generated, and the health view in D8 renders from the item
store.

The steer's own test applies: one place where work waits, one rule that picks it.
