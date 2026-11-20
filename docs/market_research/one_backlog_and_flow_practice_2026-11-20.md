# One backlog and flow: what published practice says, and where we stand against it

**Knowledge:** none -- building-it practice, not a market topic. Published through the reading log (`docs/institutional/reading_log.md`, step "Delivery and CI") and read by the decision map `docs/design/ONE_WORK_SYSTEM_DECISION_MAP_2026-11-20.md`.

**K8 page** for the director's steer of 14 Nov, "Design one work system into the harness and the method, not more rules on many lists"
(`docs/staging/advisor/done/DIRECTOR_STEER_DESIGN_ONE_WORK_SYSTEM_INTO_THE_HARNESS_NOT_MORE_RULES_ON_MANY_LISTS_2026-11-14.md`).
This is plan item 6 of `docs/operations/WEEKLY_BALANCE_REVIEW_2026-11-16.md` §5. It contains knowledge only. Nothing is built
here; the build is item 11.

Written 20 Nov 2026. **How each source was read:** the Kanban Guide's four measures and the SRE
error-budget policy were checked by web search on 20 Nov against the guide's own site and the
workbook's Appendix B, through secondary copies. The Scrum Guide sentence was checked the same
way, also through secondary copies. The official PDF's text did not come back in the extract. The
other sources (Little, Reinertsen, Anderson, Forsgren et al.) are cited from the published texts
and were not re-fetched this turn, and each one is marked where it is used.

---

## 1. What the published practice establishes

### 1.1 One backlog is the single source of work

- **Scrum Guide 2020** (Schwaber and Sutherland): the Product Backlog is "an emergent, ordered list of
  what is needed to improve the product" and "the single source of work undertaken by the Scrum
  Team". Several teams on one product share one backlog. *Checked 20 Nov via secondary copies.*
  It is ordered, not scored. One accountable person orders it, and nothing else chooses work.
- **What this means for us.** The rule says every item of work lives in one place. It does not say
  every item has the same priority. Order is a single list, kept by one owner.

### 1.2 Flow is measured on the items themselves

- **The Kanban Guide** (Vacanti and Coleman, 2020): the minimum flow measures are **WIP** (items
  started and not finished), **throughput** (items finished per unit time, as a count), **work
  item age** (time since an unfinished item started) and **cycle time** (start to finish). "Started"
  and "finished" are whatever the team's own Definition of Workflow says. An item's age becomes its
  cycle time when it exits. These four are a minimum, not a full set. *Checked 20 Nov.*
- **Little's Law** (Little, *Operations Research* 9(3), 1961): in a stable system, average WIP =
  throughput × average cycle time. Holding throughput fixed, the only way to shorten cycle time is
  to hold less in flight. *Cited from the text.*
- **Kanban Guide for Scrum Teams** (Scrum.org): when cycle times are too long, the first remedy is to
  lower WIP. *Checked 20 Nov.*
- **What this means for us.** Age, WIP and arrival rate against exit rate are not rules to bolt on.
  They can be read off any store that records, for each item, when it arrived, when it was taken and
  when it closed. **A store with no state field cannot yield them at all** (§3, finding F1).

### 1.3 Ordering: classes of service, then cost of delay, then age

- **Anderson, *Kanban* (2010)** names classes of service:
  - *expedite*: stops other work, with a WIP limit of one;
  - *fixed date*: has a real deadline;
  - *standard*: first in, first out;
  - *intangible*: no near-term cost of delay.

  Ordering is by class first, then within a class. *Cited from the text.*
- **Reinertsen, *The Principles of Product Development Flow* (2009)** says queues are the largely
  invisible root cause of poor product-development economics. Work should be sequenced by cost of
  delay divided by duration ("CD3", later called WSJF). *Cited from the text.* CD3 needs a cost of delay
  for each item, and **we have no published or measured way to put one on a finding** (GAP-2).
- **What this means for us.** The ranking rule can be built from things we already know: a class,
  the director's own order, severity and age. It does not need a cost-of-delay number we would have
  to invent.

### 1.4 When to stop features: error budgets

- **Google, *The Site Reliability Workbook* (2018), Appendix B, example error-budget policy:** a
  service that has spent its error budget over the preceding four weeks halts all changes and
  releases except urgent and security fixes, until it is back within its objective. *Checked 20 Nov
  through a secondary copy of the appendix; Google's own CRE blog warns that a reflexive freeze is not
  always right.*
- **What this means for us.** The rule that "correctness preempts features" already exists here as
  ruling and code:
  - BLOCKING-finding lane precedence, rung 1c in `background/supervisor.py`;
  - the correctness stretch's `feature_share` in `docs/direction/priority_order.yaml`.

  The practice confirms the shape: a lane-local stop, triggered by a measured state, that lifts on its
  own. It also says the budget should be stated in advance, and ours is not (GAP-3).

### 1.5 Triage at intake

- Scrum puts refinement on the backlog itself: items are split, ordered and described as they
  enter. The steer names Cagan's "opportunity backlog" for the product side. **Not checked on this
  turn** (GAP-5). The point the steer draws from it stands without the citation: decide at intake
  what an item affects and whether a knowledge gap or an insight sits behind it, and decide it
  once.
- **Accelerate** (Forsgren, Humble and Kim, 2018) measures delivery by lead time, deployment frequency,
  change-fail rate and time to restore. These are flow and stability measures, not counts of rules.
  *Cited from the text.*

---

## 2. What practice does not settle (GAPs)

- **GAP-1. A WIP limit for agent workers.** The published limits are for human teams, where context
  switching is the cost. In this repo the binding costs are different: memory headroom (the governor
  deferred the census at 13,990 MB declared), tree collisions between lanes, and verification time.
  No source gives a limit for concurrent agent sessions in one tree. **The limit is derived from what
  the governor admits, not picked**, and its effect on cycle time is a measurement to take after the
  build.
- **GAP-2. Cost of delay for a finding.** Nothing published puts a cost of delay on a defect in a
  simulation's evidence chain. Until one exists, ordering uses class, the director's order, severity
  and age (§1.3).
- **GAP-3. Our error budget.** "Correctness first" is a share (`feature_share`) and a precedence
  (rung 1c). Neither one is a budget stated in advance with a window. Whether to state one is a design
  choice for the build, and nothing here decides it.
- **GAP-4. Single backlogs with many automated writers.** The literature assumes that humans
  write items. Here, eleven-plus automated sources write them, and repeating alarms mint a new
  document per occurrence (twenty `WORKER_FINDING_REPEATING_ALARM_*` documents in the staging root on
  20 Nov). Practice gives no rule for deduplication at intake. The design takes "one item per cause,
  occurrence count on it" as its own choice and says so.
- **GAP-5.** Cagan's "opportunity backlog" was not checked on this turn.

---

## 3. Where we stand against it (read from the tree, 20 Nov 2026)

What waits, where it waits, and what picks it. The counts were read on 20 Nov from the shared tree.

| Store | What waits there | Size on 20 Nov | Has a state? | Read by the draw? |
|---|---|---|---|---|
| Staging root `docs/staging/*.md` | findings, records, dispositions | 36 (32 LATENT, 4 RECORDED); rooms: console 84, records 1,047, done 5,183 | **by location** (which room) | yes (staging watcher, rung 1c) |
| `.seat_continuation.json` | the seat's hand-offs | 2,038 rows | **no**: the rows carry `id, what, why, done_means, lane, written_at` and no state | yes (lane 0) |
| delivery-lane claims, `.draws`, `.refusals` | claims on lane-0 items | n/a | yes (claim and deadline) | yes |
| `.seat_work_in_hand.json` | the seat's own claim | 1 claim | yes | separate from the claims above |
| `docs/direction/DIRECTION.yaml` | `focus` 4, `not_now` 5, `wrong` 6, `for_the_director` 3 | 18 rows | partly | lane 0 |
| `docs/direction/priority_order.yaml` | ordered steps, candidates, accelerate | 8 lists | no | the stretch and the feature share |
| `docs/direction/director_asks.yaml` | his console asks | 1 | — | — |
| `docs/design/maturity_map.yaml` | atoms and their next level | 375 atoms, 278 closed, 97 open | level and stage | yes (dial-weighted) |
| `open_question_register.json` | questions and answers | 205 dispositions | free-text disposition | no |
| `coupled_gap_ledger.json` | world-supplier gaps by atom | 19 atoms | yes | via the gate |
| Nine gap registers (`background/gap_register_scan.py`) | open residue across simplifications, fidelity, sanity (658 rows), board, battery, placeholders, model tf2, follow-ons, primitive census | residue | each its own rule | only as a rest blocker |
| HEAD-red register, post-publish reader reds | owed fixes | 17 owed, 1 red | yes | yes (doorbell) |

**What picks the next item:** `background/supervisor.py` (7,407 lines). It has 24 draw and detector
functions (`_*_draw`, `_*_open`), a ladder of rungs (1, 1b, 1c, 1d, 4, 4b, 7 and others), and
`authorized_set_enumeration()`, which checks twelve levels before a rest is allowed. The lane-0
item is prepended ahead of the ladder.

### Findings this page files against our own method

- **F1. The largest work store has no lifecycle.** None of the 2,038 continuation rows says whether
  it is open, done or obsolete. So age, WIP and cycle time cannot be read off it (§1.2). Its state is
  inferred elsewhere, from the draw ledger and from claims.
- **F2. State is kept by location in staging, and location drifts from HEAD.** On 20 Nov,
  `staging_rooms --check` reports **202 documents archived into a sub-room on disk while still in the
  root at HEAD**. Anyone reading the queue from a ref sees as open work that has already been
  dispositioned. A state field on a file that never moves cannot strand this way.
- **F3. Arrival outruns exit.** In the seven days to 20 Nov, 60 documents were filed into the staging root and 37 were
  dispositioned out (net +23, overstated by uncommitted archivals; see F2). By Little's Law, this
  queue grows without bound unless exits rise or arrivals fall. That is a measurement, not a rule.
- **F4. Several picking rules, not one.** The ladder, the dial-weighted map draw, lane 0, the
  correctness stretch and rung 1c's lane precedence each choose work. Scrum's "single source of work"
  and Anderson's classes of service do the same job with one ordered list and four classes.
- **F5. Many intake shapes.** Findings carry `Severity · Lane · Epoch · Atom`. Continuations carry
  `what · why · done_means · lane`. Questions carry free text. Map rows carry a level and a stage.
  The steer's intake questions (what it affects, which side, the evidence, whether a knowledge gap or
  an insight sits behind it) are asked in none of them as fields.

---

## 4. What carries into the design

1. **One store, one item shape, state as a field.** The item records when it arrived, when it was
   taken and when it closed, so the four flow measures are read straight off it (§1.2, F1, F2).
2. **One ordering rule, built from what we already hold:** class of service, the director's own
   order, severity, then age. It does not use an invented cost of delay (§1.3, GAP-2).
3. **Lane-local stops, triggered by a measured state,** which is the error-budget shape and what
   rung 1c already does (§1.4).
4. **WIP derived from what the governor admits** (GAP-1).
5. **Deduplicate at intake:** one item per cause, with an occurrence count on it (GAP-4).
6. **Views, not lists**, for the director's waiting list, the Known Issues page, the map of
   ignorance and the weekly review's numbers.

The decision map applies these to our stores:
`docs/design/ONE_WORK_SYSTEM_DECISION_MAP_2026-11-20.md`.

## Sources

- Schwaber and Sutherland, *The Scrum Guide* (Nov 2020): https://scrumguides.org/scrum-guide.html
- Vacanti and Coleman, *The Kanban Guide* (Dec 2020): https://kanbanguides.org/the-kanban-guide/2020.12
- Scrum.org, *Kanban Guide for Scrum Teams*: https://www.scrum.org/resources/kanban-guide-scrum-teams
- Google, *The Site Reliability Workbook* (2018), Appendix B: https://sre.google/workbook/error-budget-policy/
- Google Cloud CRE, "Good housekeeping for error budgets": https://cloud.google.com/blog/products/devops-sre/good-housekeeping-error-budgetscre-life-lessons
- Little, J. D. C., "A proof for the queuing formula L = λW", *Operations Research* 9(3), 1961
- Reinertsen, D., *The Principles of Product Development Flow* (Celeritas, 2009)
- Anderson, D., *Kanban: Successful Evolutionary Change for Your Technology Business* (Blue Hole, 2010)
- Forsgren, Humble and Kim, *Accelerate* (IT Revolution, 2018)
