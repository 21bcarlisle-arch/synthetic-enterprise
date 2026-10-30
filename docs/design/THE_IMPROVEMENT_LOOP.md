# The improvement loop: knowledge, a world that reacts, a supplier that tests, and round again

*Delivery seat, 2026-10-30, for the director's steer of the same day
(`docs/staging/advisor/done/DIRECTOR_STEER_OWN_THE_DESIGN_OF_THE_WORLD_SUPPLIER_IMPROVEMENT_LOOP_2026-10-30.md`).
This is a design note, not a build. Every claim about the tree was checked at `f1e9424606`. The
build waits for the correctness stretch's exit test. One part is the exception the steer named; it
is marked below.*

## 1. The problem, in my words

For each area of the business, the loop has to turn evidence into a supplier lesson that **would
hold in the real market**. A lesson can fail to hold in two ways, and the loop has to guard against
both:

- **The world does not press back.** If no household reacts to a pain point, every supplier
  variant ties on it. Whatever wins then wins for some other reason (F1).
- **The world presses back in exactly the way the supplier expects.** That happens when the
  reaction is the supplier's own belief, or a guessed point the supplier can tune to, or an
  assumption written by the same mind that wrote the strategy. The supplier wins, and the win is
  an artefact.

The method that guards against both is **already ruled**, in W7 and W8:
- build the world from research, with a **labelled range** where evidence is missing;
- freeze it, with predictions filed;
- grade the supplier on fresh seeds **"and across the world's uncertainty ranges"**;
- keep truth as an instrument only.

So the gap is not missing principles. **Nothing makes the ruled method the default path of the
work.** Each area goes round only when someone remembers to take it round, and nothing records how
far round it got.

## 2. The advisor's concerns, judged

| # | Concern | Verdict | Evidence |
|---|---|---|---|
| 1 | No one can say what stage an area is at | **Confirmed.** The materials exist but the stage does not | The map's `loop_stage` (`discover…harden`) is an *atom's* build lifecycle, not the area's place in the loop. A knowledge page exists for each of the six areas (`site/knowledge/payments-and-direct-debit`, `the-first-year-blind-spot`, `unbilled-energy-and-revenue-assurance`, `debt-and-collections`, `switching-mechanics`, `ev-*`). Supplier arms live in separate, hand-built tools (`tools/dd_opening_arms.py`, `move_with_us_arms.py`, `_ladder_chase_arm.py`, …). No artefact joins the three |
| 2 | The world may not react to most pain points | **Confirmed, and measured** | The pain-point audit (`docs/staging/SEAT_FINDING_THE_WORLD_REACTS_TO_ONE_PAIN_POINT_IN_SEVEN_…_2026-10-30.md`): one of seven reacts in full, two not at all, one has no trigger. The DD-rise cancellation, failure and complaint legs are built and **ship at 0**. Under K2, that asserts the one value we know is wrong |
| 3 | The world's defects were found by examples, not by the loop | **Confirmed, with one change since 26 Oct** | Since the 26 Oct ruling, an embedded check exists: the blind-written invariants (`docs/design/DOMAIN_INVARIANTS.yaml`), the runner (`tools/domain_invariant_runner.py`) and five cold reads. They still catch the world wrong **only after a book exists and someone reads its outputs**. And each of the five cold reads found a new class (the gas kWh register, one meter serial on 34 supply points, the committed price read from one bill, …). The defect rate has not converged |
| 4 | The separation is between lanes, not minds | **Confirmed, and it reaches further than stated** | The `sim-engineer`, `saas-engineer` and `phase-close-evaluator` agents all have unrestricted Read, so they are blind by prompt only. The invariants were written "blind", but their own header (`DOMAIN_INVARIANTS.yaml:9`, `blindfold_disclosure`) says the knowledge pages they read **quote code constants from `company/` and `simulation/`**. Blindness built from the knowledge layer is only as clean as that layer. See missed concern A |
| 5 | Thin evidence turns into false precision | **Confirmed. It is ruled against and not built** | W7.1 and W7.3 already demand ranges and grading across them. In the code, the world carries points: `DECLARED_SENSITIVITY_SCALE = 0.039520` (`simulation/departure_risks.py:251`), the shock weight 0.50 "declared", and complaint rates of 3% / 35pp / 8% with no source. No mechanism runs a world over a range |
| 6 | No principled trigger for "make the world more nuanced" | **Confirmed** | The record shows only ad hoc triggers: examples, cold reads and director questions. W7.2 says when the world *may* change (on new evidence, disclosed). Nothing says when it *should* |
| 7 | Rot at the seam | **Partly refuted, partly worse** | *Refuted:* the six owed crossings now carry an owner (`KNIFE3_wall_crossing_paydown`) and dates. Three are due 2026-11-21 and three 2026-11-28 (`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md:4151-4251`), and an overdue row stops the commit gate (`tools/wall_crossing_dispositions.py`). *Confirmed:* `interface/README.md` says "Empty for now" over eight contract files. *Worse:* the README also says "neither side imports the other directly", and three of the six owed edges are the world importing the supplier's churn and win-rate functions (`simulation/customer_events.py` → `saas.churn_model`, `company.crm.churn_model`, `saas.home_move_win_rate`). Those are exactly the renewal-shock leg the audit found |

## 3. Concerns the advisor missed

- **A. The knowledge layer is contaminated by the code.**
  - The loop's first stage is meant to be independent of the build, and it is not.
  - When a market_research note cites a constant because the code uses it, the next "blind" reader
    inherits the constant as evidence. The citation chain then runs code → note → invariant → "sourced".
  - A blind role is worth little until the knowledge it reads is cleaned of code quotations, or
    each quotation is marked as ours.
- **B. Zero by omission is the default state of a new reaction.**
  - The DD4b legs show the pattern: build the mechanism, ship it at 0 "until sourced".
  - That is K2's error made systematic. A world reaction should ship at its labelled range, not at
    0. The default shape matters more than any one leg.
- **C. Each supplier experiment hand-builds its own grading.**
  - The arm tools are separate harnesses. Each decides its own seeds, its own outcome set and
    whether it pre-registers.
  - Seeds per tool range from one mention in `move_with_us_arms.py` to hundreds in
    `generate_value_arms_data.py`.
  - The loop cannot grade "across the range" until there is one grading path to put the range into.
- **D. Weighting the scorecard is the director's call.**
  - The A5 frame (`docs/design/A5_TOURNAMENT_FITNESS_MORTALITY_FRAME.md`) reserves the fitness
    function to him: whatever a search rewards, it will find a way to maximise.
  - A per-area scorecard fixed at the knowledge stage must therefore stay a **vector**: customer
    money, time and carbon (M3), company outcomes, and fairness (X1–X2).
  - A variant wins only if it is no worse on every axis and better on one. Any weighted trade
    between axes comes to him.
- **E. The loop cannot start round one until the world passes its own suite.**
  - Grading supplier variants against a book with unexplained invariant breaches grades them
    against defects.
  - The correctness exit test is therefore not something beside the loop. It is the loop's
    "world reacts **correctly**" stage, done once for the whole book.

## 4. Options considered

Costs are in seat turns, one turn being one bounded invocation. These are my estimates, not
measurements. The one measured cost is the cold read: five in four days, about one turn each,
including pre-registration.

| Area of the design | Option | Trade-off | Cost |
|---|---|---|---|
| Making the stage visible | (a) A hand-kept loop register (the advisor's idea) | Readable, but it is one more register to keep true by hand. This project has 34 alarm documents' worth of evidence that such registers rot | ~1 turn to write, then a tax on every area's work |
| | (b) **A derived register**: one small file mapping each area to its artefacts, with the stage *computed* as the first missing artefact | Keyed to the property, not to today's answer. It cannot claim a stage whose artefact is absent | ~2 turns: the area file, a reader, a door test |
| | (c) Status quo: the seat holds it in its head | Free, but it fails concern 1 by definition | 0 |
| Blind roles | (a) By prompt (today) | Already shown to leak (concern 4) | 0 |
| | (b) **By construction**: a sparse worktree per role. The supplier builder's tree has no `sim/` or `simulation/`; the world builder's has no `company/`, `saas/` or run results; the grader gets results and the scorecard only | It cannot be argued around. It needs the knowledge layer cleaned (A) or a reader cannot work from it | ~1 turn for the tool and its control, plus a cleaning pass over the notes that quote code |
| | (c) A different model family for one role | Different blind spots, but no such family is in use here, and it adds cost | Not costed |
| Thin evidence | (a) Point values (today) | Invites tuning to the guess | 0 |
| | (b) **Range endpoints**: each thin parameter in an area carries low, central and high. A variant is graded at all three on fresh seeds, on the smallest book that answers the question (R5) | About 3× compute per experiment for each thin parameter varied. Vary at most two per area at once (9 runs), or the run grid explodes | Compute, plus ~1 turn per area to label the ranges from the packs |
| | (c) Full sampling from distributions | More faithful, far more compute, and the distributions do not exist | Rejected for now |
| Nuance trigger | (a) Taste (today) | Too early or too late, and at risk of breaking W7.2 | 0 |
| | (b) **Three named triggers**, below | Each is an event already produced by the work | ~1 fresh-agent read per settled result |

## 5. Recommended design

**One loop per area. Its stage is derived from artefacts. Each stage has a single check that can
fail.**

| Stage | Done means (the artefact the derived register looks for) | The check |
|---|---|---|
| 0 Knowledge | A K8 knowledge page with the area's pain-point table. Each pain point has reaction evidence **or** a GAP with a labelled range, plus the area's scorecard vector | The page exists, and every pain-point row has evidence or a range. No row is blank |
| 1 World reacts | Every pain point has a world reaction that ships at its range, not at 0. No world module for the area imports a supplier belief. The invariants for the area pass on a fresh book | The wall census shows no live `owed` edge in the area's files. The reaction toggle is not 0. The invariant gate is clean |
| 2 Frozen | `world_version` pinned (`simulation/run_scenario.py` already returns it), with predictions filed before any supplier run | The pre-registration's commit date is before the first arm's commit date |
| 3 Graded | Pre-registered variants are graded on fresh seeds × range endpoints, against the stage-0 vector, by a grader in a blind worktree | The result file names the seeds, the endpoints and the frozen version |
| 4 Settled or undecided | **Settled:** a variant is no worse on every axis at every endpoint, and better on one. **Undecided:** it wins at some endpoints only, and we publish "we cannot tell" with the range that decides it | One of the two verdicts is on file. Neither verdict is skipped |
| 5 Exploit check, then the next round | A fresh, blind practitioner-reader asks of the settled variant: "would this work in a real GB supplier, or does it exploit something our world fails to punish?" | Its answer is on file |

**The nuance trigger, which answers concern 6.** An area goes round again only on one of three events:
1. **The exploit check names an exploit.** The world gets the missing pressure, disclosed under W7.2.
2. **An Undecided verdict.** The range is too wide to settle, so narrowing it is a *knowledge*
   task, not a world edit.
3. **A cold read or the invariant gate finds a new class in the area's files.**

Nothing else moves an area's world. Taste is not a trigger.

**How the draw uses it.** For each area, the next item is its first unmet stage. Between areas,
the existing priority order decides. The register only says what the next item *in an area* is.

**What I chose not to build:**
- a tournament, which waits for A5's fitness ruling;
- a loop-stage field on the maturity map, which would add bytes to a ratchet to store what can be
  derived;
- a new gate on the commit path. The derived register is read by the draw and published on a
  door. It does not block commits.

**Sequencing.** The steer says the build follows the correctness exit test. Taking it in that order:
1. **Now, because it helps close the exit test:** the blind-worktree tool for the cold reader and
   the invariant writer, and marking the code quotations in the knowledge notes. The current
   cold-reader protocol is blind by prompt. A worktree with no code in it makes it blind by
   construction, and makes leg three's verdict worth more.
2. **After the exit test:** the derived register and its door. Then the first round, on **a new
   account's first months**. The 30 Oct ruling already asks for that experiment, and the evidence
   pack has landed.
3. **In the same window:** the world's own renewal-shock draw, which the six owed crossings due
   21–28 Nov already require. It turns the one "full" reaction into a reaction the supplier can
   actually be wrong about.

## 6. How we will know it works, or has failed

Written before any of it is built, so these are predictions.

**It is embedded if, by the end of the first round on first-months estimates:**
- the derived register shows all six areas, and a hand check by a fresh agent agrees with every
  stage;
- at least one area has passed stages 0–4 with its artefacts on file and dated in order;
- the draw has picked at least one item *because* it was an area's first unmet stage, and the
  draw log names that reason.

**The controls that must be able to fail** (assert that each branch can be taken):
- The register is fed an area with no world reaction. It must report stage 0 or 1, not later.
- The exploit reader is given a seeded known exploit: a supplier variant that wins because the
  world's renewal-shock leg is the supplier's own curve. It must name the exploit. If it does not,
  the reader is toothless, and that is a finding about the reader.
- A grading run over one endpoint only must be refused as stage 3.

**It has failed if any of these happens:**
- an area's world files change after its stage-3 results with no W7.2 disclosure (one leg: git
  dates against the result file);
- every settled result passes the exploit check for three rounds running (the check is not
  reading);
- the register and the hand check disagree on a stage. A register that says an area is further on
  than its artefacts show is exactly the claim rot this design exists to prevent.

## 7. What is open, and whose it is

- **His:** whether the scorecard vector is the right set of axes, and any weighting between them
  (D). The recommendation is no weighting: Pareto only, with trades brought to him.
- **Mine, to do:** the blind worktree now; the rest after the exit test, in the order of §5.
- **GAP:** how much one cleaning pass of the knowledge notes will take. I have not counted the notes
  that quote code, so I cannot yet size it. The first build step counts them.
