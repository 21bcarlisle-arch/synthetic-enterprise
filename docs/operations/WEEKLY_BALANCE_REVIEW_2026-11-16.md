# Weekly balance review for the week from Mon 16 Nov 2026

*Delivery seat. Drafted Fri 13 Nov and rewritten Sat 14 Nov 07:50 GMT so that it carries the
director's four 14 Nov steers. This is the first review under his ruling of 11 Nov
(`docs/staging/advisor/done/DIRECTOR_RULING_END_THE_FEATURE_FREEZE_A_THIRD_TO_FEATURES_AND_A_WEEKLY_BALANCE_REVIEW_2026-11-11.md`,
point 4). It is a proposal. If he has not answered by the Mon 16 Nov 03:00 GMT reset, it stands,
and he can change it at any time.*

## 1. The value test's 12-draw grade

**Graded 14 Nov 08:54Z** (`docs/design/THE_VALUE_TEST_REDESIGN.md` §7; §2's re-run graded (a) at
12:53Z). *Rewritten 14 Nov 14:30Z: the bullets this replaces said the grade was pending.*

- **2 Nov prediction 1 held, by £311.** The published £5,244 is below all 12 elasticity re-draws
  (£5,556 to £12,462). What sets it apart is its price-level leg (−£6,101, 3.5 sd below the
  family), not its total. §2 then showed the harness reproduces the published run to the penny, so
  no process or tree state explains it.
- **P6 missed, read as "not shown".** Roll noise is 4.6% (1.5% to 10.0%) of the per-household
  variance, a lower bound because only the elasticity was re-drawn. The `churn_roll` family (§8)
  measures the rest. It is running in `/var/tmp/vtcr-out/`, 12 members in pairs, and should read
  about 09:00Z Sun 15 Nov.
- **What we know, per household per year.** The family mean is +£5.24 (−£3.34 to +£14.35), not
  distinguishable from zero. The belief's AUC against who left under the flat price is 0.549
  (0.530 to 0.572 across draws), and believed minus realised retention is −0.21. **Still no
  evidence that per-customer value works, and none that it does not.**
- **What runs first after the reset is already decided, whatever `churn_roll` says.** §6a's order
  table puts **candidate A, switching on the corrected belief `renewal_belief_by_ending_term`
  (`7a7ad95dc`)**, first under all four outcomes. The grade decides only how A is run and what
  follows. If kill condition 2 fires (AUC half-range < 0.03), A is one draw, about 1.5 h. If it does
  not, A is twelve `churn_roll` draws, about 19 h. B (the retrain) and C (about 4,860 households, or
  the 1,200-household sized run if the roll share is ≥ 0.25) follow in the matching row of §6a.
  A's bar: AUC clear of 0.549 by more than the family's half-range, and calibration moving from
  −0.21 towards zero. Its prediction is filed in the launch commit.

## 2. What the week did

**The commit split, measured.** These are landed sessions from the Mon 9 Nov 02:00 GMT reset to
Sat 14 Nov 07:40, priced from the session logs and classed by the paths each session's commits
touched (`tools.work_cost_estimate`). There were 214 landed sessions, costing $544:

| Class (by path) | Sessions | Share of landed spend |
|---|---|---|
| Records and staging | 62 | 24% |
| Grading runs | 39 | 18% |
| Harness | 37 | 14% |
| Supplier code (`company/`, `saas/`) | 19 | 13% |
| World code (`sim/`, `simulation/`) | 22 | 11% |
| Knowledge | 19 | 10% |
| Site pages | 16 | 10% |

**The path class is not the purpose.** On Friday I read the supplier and world sessions' commits
one by one. All but one were correctness fixes or the grading of them. So **the feature share was
about 0.5% of landed spend, against the third the ruling set.** Since Friday, three feature
commits have landed, and all three are breaches (below).

**The learning loop on origin (7 days, filed late in a2604837f).**

| Area | Grade | Reading |
|---|---|---|
| repayment-posting | 30 of 49 | STOP. Its area map is on origin (ad4873741). |
| level-dd | 41 of 57 | STOP. Its area map is on origin. |
| class-l | 11 of 12 | |
| close-refund-book | 15 of 15 | |
| eleventh-read-prereg | 6 of 6 | |

That is 0.143 regressions per fix over 21 graded fixes. Cold-read escapes: 2. Both STOP areas
take no new fix until each map's next item is drawn, and W1's stop condition now enforces that in
the draw (c29205f25).

**Ruling breaches that landed, and why.** The 11 Nov 12:00 ruling said "no more knowledge passes
this week" and "everything goes to the fix and its book". The 18:10 reading said other
world-feature work not yet drawn "also waits for the review".

| Commit | What | Which clause it broke |
|---|---|---|
| e17ebc596 (13 Nov 19:08) | W2_21: 15% of homes POOR, not 72% | World feature after the 18:10 hold. It landed 47 minutes after the direction held it. |
| 98ba0292e (13 Nov 21:41) | Pensionable age in the licence | Knowledge pass |
| f3d88c1fe (13 Nov 22:20) | E6's 2022 bad-debt leg | Knowledge pass |
| fcdbd4cb0 (14 Nov 04:37) | The housing page on roofs and parking | Knowledge pass |
| c85ef6e55 (14 Nov 04:41) | G15: the weekly forward series | Feature work. Its own message says it was drawn "from the stretch's feature third". |
| 61b266b2f (14 Nov 06:18) | W2_41 to level 2 (ADDACS 1) | World feature |

**Why.** The most likely shared cause: **the pause never reached the mechanism.** The 18:10 hold
was written into `DIRECTION.yaml`, which binds the seat's own lane-0 draw. But `feature_share` in
`priority_order.yaml` has read 0.33 since bb69c250d on 11 Nov and was never set to 0. So the BUILD
draw kept handing out held atoms at a third, and nothing in the knowledge lanes reads the "no
knowledge passes" clause at all. G15's own message confirms this path for one commit. For
e17ebc596, the seat's earlier reading is that its claim predated the hold. I have not checked
which draw handed out each of the other four.

None of the six is wrong work. Each is real fidelity or knowledge, and none touches the 16 Nov
book's pre-registrations except e17ebc596. That one does: it now sits under every 16 Nov grade,
and cc27c048e and f63824238 amended the pre-registrations for it. **Proposed remedy:** a pause
in a ruling is applied by setting `feature_share` to 0 in the same commit that records it, and
restored at the reset. This is one line, and it is already the documented switch (the comment
above `feature_share` says so).

## 3. The director's 14 Nov steers, costed

Costs are in usage points. The basis is the fitted cost per item by class in
`tools.work_cost_estimate`: harness 0.9 (0.5–5.2), knowledge page 1.3 (0.6–6.4), record 0.7
(0.4–4.2), world build 1.4 (0.6–8.2). Each estimate below is a count of items times that fit. None
has been measured on this kind of work before.

- **One work system** (BLOCKING, 06:57). One backlog with one item shape and one lifecycle, in
  three lanes: world, supplier and building it. Each lane is ranked by its own rule, every other
  list becomes a view of the backlog, and the old stores are deleted.
  - Steps: the K8 page on single-backlog practice and flow metrics (1.3); the decision map (0.7);
    the build and the deletion of the old stores (about 4 harness items, about 3.6).
  - **About 5.6 points (3–15).** It is harness work. It should make the rest of the harness
    smaller, so I propose it takes most of next week's harness share, and the build may run into
    the week of 23 Nov.
  - **The deletion is part of done.** `open_question_register` and `coupled_gap_ledger` stop
    being separate stores, and the staging root stops being a filing cabinet.
- **The triage** (BLOCKING, 06:47; its age rule, page and cap are superseded by the steer
  above). The triage is how existing items migrate into the one backlog.
  - **How far it got: not started.** The counts on origin at 07:40 confirm the advisor's
    census: **184 findings** in the staging root. 145 are older than 14 days, 98 older than 21,
    and 56 older than 28. The oldest is 43 days.
  - By severity line: 10 BLOCKING (the advisor counted 11), 151 LATENT, 22 RECORDED, 1 with none.
  - By side: supplier lanes (B, C, D, E) 92, world lanes (W1 to W4) 49, building it (A, G, H) 42.
  - **Cost:** at about 20 findings per record-class session, about 9 sessions, **about 6 points
    (3–38)**. That is correctness and backlog work. BLOCKING items come first, then supplier
    money items, then the world, then building it.
  - The other lists (836 GAP mentions, 31 map blockers, 182 questions with 21 answered "wrong",
    16 coupled gaps, 27 console files) follow inside the one-work-system migration.
- **Linking findings to concepts** (05:52). This is a tagger, a 30-item precision sample and three
  replayed defect families, with a decision rule fixed in advance. **About 1.6 points.** It goes
  ahead of the work-system decision map, because its answer decides whether the item shape
  carries a concept link.
- **Where reading tokens go** (released by his 06:42 ruling). A measurement only, built by adding
  to `tools/tick_burn_rate.py`. It covers a full week and every seat kind, and reports tokens by
  class (fresh input, cache write, cache read, output). **About 0.9 points.** Its own steer
  file's cut list is the ranking it must produce.
- **The hidden weighted utility** (his 13 Nov 18:59 ruling; commitment
  `value-test-hidden-weighted-utility-knowledge-page-first`, **due 23 Nov**).
  - Done means: M3 is amended after the advisor reads the draft; the K8 page on household need
    weights is published with its GAPs labelled; and this review names its cost and queue
    position.
  - **Cost of the commitment:** the K8 page, 1.3 (0.6–6.4). The M3 wording is the director's
    document. It goes as a proposal and costs almost nothing to us.
  - **The build in the world comes later.** It is a hidden weighting per household, discovered by
    the supplier, and the first redesigned run reports the vector without it. It is unsized here:
    world build, several items, after the sized value-test run (step 6, week of 23 Nov). Sizing it
    is one line of the K8 page.
  - **Queue position:** the page is supplier-feature item 3 below, after value-test steps 3 and
    4. That puts it on origin before 23 Nov if the week runs at the proposed split.

## 4. The split proposed for the week from Mon 16 Nov

| Share | % | What it is for |
|---|---|---|
| Correctness and backlog | 42 | The 16 Nov book's grades first, then the triage |
| Supplier features | 18 | Value test steps 3 and 4, then the utility's K8 page |
| World features | 15 | Value test step 2 (the write-off rule), then W3_3, then W2_30/N17 |
| Harness (building it) | 15 | The linking measurement, the one work system, the token measurement |
| Knowledge | 10 | Only K8 pages that the items above need first |

- **The feature third is held at 33%** (18 + 15). Harness rises from 10% to 15%, and knowledge
  falls from 15% to 10%, for one week only. The one work system is the director's BLOCKING steer,
  and it should shrink the harness in later weeks. The knowledge share still covers every K8 page
  the ranked items need.
- **Holding the share is a mechanism, not a number.** The value test steps go onto the seat's
  lane-0 focus, and the remedy in §2 makes a pause reach `feature_share`.

## 5. The order of work after the reset, ranked

Nothing below is built by this review.

1. **The eight continuations stamped DO NOT DRAW BEFORE 16 Nov 06:00.** They grade the 16 Nov
   book against its amended pre-registrations. Correctness, and they come first because they
   decide whether the book stands.
2. **The triage: the 10 BLOCKING findings**, then the supplier money findings (92 in the B, C, D
   and E lanes). Each gets fixed, real (ranked), parked (with a reason and a revisit date) or
   obsolete. For each still real, I ask whether a knowledge gap or an insight sits behind it.
3. **Value test candidate A, then steps 3 and 4** (supplier feature, about 8 points with step 2,
   plus A's 0.9). A is first because §6a of the redesign puts it first under every `churn_roll`
   outcome. That outcome sets A's draw count (one or twelve) and where B and C come after it. The
   §8 grade is read against §6a's rows before A launches.
4. **Value test step 2: the world's write-off rule** at an 86% final-account loss (world
   feature), after the `debt_and_collections.md` P5 amendment (K8).
5. **The linking-findings measurement** (harness, about 1.6 points). Its prediction is
   pre-registered before the tagger runs.
6. **The one work system: the K8 page, then the decision map** (harness, about 2 points). The
   decision map comes back to him only if it changes something he ruled.
7. **The hidden utility's K8 page** (supplier feature, due 23 Nov).
8. **W3_3, the standing charge in settlement** (world feature). It is parked on the map until the
   16 Nov book is graded (ebe786128), so it is drawn after item 1 closes.
9. **W2_30/N17** (world). Metered electricity barely moves year to year: a median same-month
   change of 1.1%, against NEED's 14.7%. Recheck by 23 Nov.
10. **Where reading tokens go** (harness, about 0.9 points).
11. **The one work system's build and the deletion of the old stores** (harness, about 3.6
    points). It may run into the week of 23 Nov.
12. The rest of the triage, as the work system's migration.

Each lane takes from its own rank by its share, so item 11 can run before item 2 finishes. The
numbers order work inside a lane; they are not a single queue.

**The accelerate list** (drawn from Saturday, only when more than the roughly 10-point reserve is
unspent):

1. Value test candidate C as §6a's matching row places it. If the roll share is < 0.25, it is a book
   of about 4,860 households, which needs the director's call under rule 2 and goes to him with
   its cost (2.3 points, about 24 h). If the share is ≥ 0.25, it is step 6's 1,200-household run
   at 12 draws, which needs no call.
2. The `debt_and_collections.md` P5 amendment for the write-off rule (about 0.6 points).
3. A second gate-passing book on the current tree.

It is written into `priority_order.yaml` `accelerate:` at the reset if he has not changed it, and
not before.

**The measures the ruling names.** Serious classes per cold read: one each on the eleventh and
twelfth reads (N29 and N30), so the reads are converging. The site published on 11 Nov. Usage
was 76% at Sat 05:53, burning 0.54 points an hour against the 0.45 he asked for.
