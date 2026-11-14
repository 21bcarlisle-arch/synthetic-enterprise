**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Design one work system into the harness and the method, not more rules on many lists

**Type:** STEER, through the advisor channel. **It supersedes** the age rule, the generated page and the backlog cap in `DIRECTOR_STEER_NOTHING_LOGGED_IS_LEFT_TO_MALINGER_..._2026-11-14.md` (items 3-5 and addendum items 2-4). The triage and the cause-finding in that file stand, and become this design's migration and its evidence.

The director's words, from chat, Sat 14 Nov 06:57 GMT:

- "This whole thing sounds messy and complicated. And what you have done is a good sticky plaster fix. But surely this could be designed better as part of our harness and method"

## He is right, and the advisor says so

This morning added three rules to seven lists: an age rule, a cap and a gaming guard. That is the shape CLAUDE.md warns against: "A file made of rules breeds rules." The defect is not that the lists lack rules. It is that the method has **many places where work waits and no single place where work is chosen.** The lists are these:

- findings;
- knowledge GAPs;
- map blockers;
- the question register;
- old proposals;
- the coupled gap ledger;
- his console asks;
- queued steers;
- gate breaches;
- cold-read faults;
- the advisor's own channel.

Each grew its own lifecycle. The draw reads only some of them.

## The intent

**One work system.** Every input that says "something should be done or known" is the same kind of thing: one item, in one backlog, with one shape and one lifecycle.

- **Every source feeds it.** That means a finding, a gate breach, a cold-read fault, a knowledge GAP that blocks something, a director steer, a question the machine cannot answer and a world-supplier gap. Any source is welcome, but each one writes items here and keeps no list of its own.
- **One shape.** Every item records:
  - what it affects: money, customer outcome, fidelity, method or tooling;
  - its side: world, supplier or building it;
  - its evidence;
  - whether a knowledge gap sits behind it;
  - whether it carries an insight.

  Those last two are the director's 06:46 questions, asked once, at intake.
- **One ranking rule**, that the draw uses, and nothing else chooses work.
- **One lifecycle:** open, then chosen, then done (with evidence), parked (with a reason and a revisit date) or obsolete.
- **Flow is a property of the system, not a rule bolted on.** Age, items in flight, arrival rate against fix rate and the parked count are read off the backlog itself. They feed the learning loop and the weekly balance review without separate machinery. The weekly review becomes "how is the one backlog flowing, and what share goes where".
- **Everything else is a view.** The Known Issues page, the map of ignorance, the weekly review numbers, the director's waiting list (`for_the_director` as a filter of items only he can decide) and the advisor's what-is-waiting read are all queries on the one backlog. None is a list to keep in step.

## How (the machine owns the design)

- **K8: knowledge first, on the "building it" side.** Read how mature teams run one backlog and keep it healthy before designing: single product backlog and triage at intake (Scrum, Cagan's opportunity backlog), flow metrics and WIP limits (Kanban: lead time, work-item age), and SRE error budgets as a rule for when to stop features. Write the page, with GAPs.
- **A decision map before the build.** Under the other chat's 13 Nov steer, a design with more than two outcomes gets one. Which lists merge? Which become views? What is retired? Where does the ranking rule live?
- **Replace, do not add.** The design must remove more than it adds. State what it retires, for example `open_question_register` as a separate store, `coupled_gap_ledger` as a separate store, and the staging root as a filing cabinet. **Done includes deleting the old lists**, or turning them into generated views.
- **Migrate through the triage.** This morning's triage of the 184 findings and the other lists is how existing items enter the new backlog, each with its disposition. It does not have to finish before the design. It can run as the migration.
- Put the design in Sunday's balance proposal with its cost. It is harness work. It may take part of next week's harness share, since it should make the rest of the harness smaller.

**Done means** there is one place work waits and one rule that picks it. The director can see the whole backlog's health from one view, and the number of lists that must be kept in step goes down.

## Addendum, Sat 14 Nov 06:58 GMT: separate lanes for the world and the supplier, on one mechanism

The director's words: "One for SIM, one for supplier?"

The advisor's answer to him: yes, kept separate, and a third for the method. All three share one mechanism. The reason is canon, not tidiness:

- **The world's work must be ranked blind to the supplier's results.** The baseline/curriculum split says the world "changes only for fidelity reasons, decided blind to company results". If one ranking rule weighed a world fix against a supplier feature, how much a world item seemed to help or hurt the supplier would leak into its priority. So the world lane ranks on fidelity and correctness alone. The supplier lane ranks on value to households and the company. The **building it** lane (harness and method) ranks on flow and risk to the work.
- **Shared:** one item shape, one lifecycle, the same flow measures and the same views. It is one system with three ranked lanes. It is not three systems.
- **Between lanes:** the weekly balance review sets each lane's share of capacity. That is the director's 11 Nov ruling, now with a natural home. The draw takes from each lane by its share and its own rank.
- **Items that span the seam,** such as the value test or a new observable, have one owning lane. They are named in the item and decided by the interface steward's rule: what crosses the seam is the supplier's question, and what the world must model is the world's.

## Done

(worker tick, Sat 14 Nov.) The design is put in Sunday's balance proposal with its cost, as asked
(`docs/operations/WEEKLY_BALANCE_REVIEW_2026-11-16.md` §3, §4 and §5). The cost is about 5.6
points (3–15): a K8 page on single-backlog practice and flow metrics (1.3), a decision map (0.7),
and the build with the old stores deleted (about 3.6). The proposal raises next week's harness
share from 10% to 15%, for that week only, and takes the 5 points from knowledge. The K8 page
and the decision map are item 6 after the reset. They come behind the linking measurement (item
5), whose answer decides whether the item shape carries a concept link. The build is item 11. The
three ranked lanes (world, supplier and building it), the one item shape, the one lifecycle and
deletion as part of done are carried into the proposal as the design's terms. Nothing is built
yet, and this steer is done only when one place holds the work and one rule picks it.
