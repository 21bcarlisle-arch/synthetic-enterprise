**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The control stack also shows two-way doors, pace and how work is balanced (2026-10-23)

**Type:** STEER, through the advisor channel. It is the third and last addition to `DIRECTOR_STEER_SHOW_THE_HARNESS_AS_A_LIVE_CONTROL_STACK_2026-10-23.md`, after `..._SHOWS_MEANING_LEARNING_AND_WHAT_IT_REFUSES_2026-10-23.md`. It goes into the same How it's built rework. The director's words, from chat on Fri 23 Oct:

- 09:25 BST: "Also our approach to 2 way doors is important. As is effort and pace management and tokens. And how we balance work ?"

The first two additions cover how the machine is controlled. These three cover how it decides, how it spends, and how it divides its time. A tech reader asks about these next, and most published harnesses say nothing about them.

## 1. Two-way doors: act by default, stop only at a short list

What to show (the advisor's reading; check it against the code):
- **Reversibility is the default verdict.** The burden of proof sits on "this is a one-way door", and "I'm not sure" resolves to proceed and log. A needless escalation is counted as a defect, the same as a needless stop.
- **The doors are one list, in code** (`background/one_way_door.py`): real money, real people, real-world commitments, public claims that cannot be retracted, live credentials and safety controls, and destroying evidence. Everything else is acted on, with how to reverse it recorded and what was done said.
- **Why:** a wrong reversible decision costs about an hour of compute, and a stall costs the director's attention, which is the one scarce resource.
- **Over it all:** a single director-only kill switch, a dead-man's switch keyed on real commits, and the walls that no approval can open.

Live evidence, if the stores hold it: how many actions proceeded against how many were escalated, and when a reserved door last held. If that split is not recorded anywhere, say so rather than estimate it.

## 2. Effort, pace and tokens: spend where depth compounds

What to show:
- **Measured before designed.** Only three unattended routes start a model session (`background/tick_mode.py`, from the 27 Sep finding). Everything else spends nothing, so nothing else is throttled.
- **The model is matched to the work, not the process** (`background/model_tier.py`). The top model is the default and the fallback. Cheaper models are reachable only for named classes of routine work. The loss is deliberately asymmetric. The director's words: "I'd rather spend the tokens than get shallower work."
- **Pace is managed against the weekly allowance by the machine itself,** never by idling to save budget. The remaining allowance cannot be read from inside, so the director supplies a reading and the machine paces against it. One dial (normal, slow, product-only) puts itself back to normal when its time is up. No loop can run unbounded.

Live evidence: sessions and spend per route per week, and the share drawn on each model tier, if recorded. Say what each figure counts.

## 3. How work is balanced: a map, not a plan

What to show:
- **Work is drawn from a map of small pieces,** each with the evidence its level needs. It is not taken from a schedule. When a date and a test disagree, the date is the thing that is wrong.
- **The dials order work but never zero it.** No lane can be starved. The delivery seat writes direction and can make work more likely, never impossible, so a wrong instruction slows the machine and never wedges it.
- **Interconnection comes before novelty.** When something that just landed is contradicted downstream, that is the next item, ahead of new work.
- **The lesson that shaped it** (4 Sep): the dials were re-ranked, and the machine then ran ten hours and 66 commits with no product work, because the dial was not what chose. That is a good lesson card: what happened, and the rule it created.

Live evidence: the split of last week's landings between the product (world and supplier) and the machine that builds it, and how that split has moved over time. This is the most honest single number about balance. Show it whichever way it reads.

## Requirements

The same as the parent steer: every count generated at publish, plain words, one click from each box to the real mechanism, and "not measured yet" rather than a placeholder. Fit these into the one diagram or its second panel. The whole control story stays on How it's built and does not start another page.

## Risk

Touches: the How it's built page and its generator. Reads existing stores only.
Blast radius: one public page, which is reversible.
Probable failure mode: a token or spend figure that leaks something that should stay private, such as account usage detail, or a figure that implies a cost per unit nobody has defined. Publish the shape (routes, tiers, product against machine share), not account-level usage, and say what each figure counts.
Proportionality: reversible and narrow — just do it.

— Director steer, 23 Oct 2026, his words above; the reading of the mechanisms and drafting are the advisor's.

## Done

*Worker tick, 23 Oct 2026.* How it's built now has a second collapsed section, "Two-way doors, pace and how work is balanced", with its own In brief. Its figures are written at publish: the 7 reserved categories read from `RESERVED_CATEGORIES`; the questions raised to the director in 30 days and how many are open, from `DIRECTION.yaml`; the 3 spending routes from `background/tick_mode.py`; sessions started in 30 days and the share on the top model, from `model_tier_log.jsonl` (1,071 and 98% today; it says not measured if the log has nothing in the window); and the weekly share of commits that changed the world or the supplier, over eight whole weeks (4% to 24%), shown as it reads. How many actions went ahead without asking is not recorded, and the page says that. It gives no spend and no account usage. The 4 Sep lesson is a card, with its rule taken from the director's console words of 5 Sep.

**Cold-reader pass over the whole page (23 Oct), one energy reader and one tech reader, blind, with the extra question.** Both said the page is for showing how AI builds and runs a simulated supplier through eight layers of checks. The tech reader led with achievements and answered the extra question: "live per-layer evidence that each check can fail, with sample sizes, instead of boxes and arrows", a measured error rate for the AI reviewers, failure stories, a number only a simulation can produce, and "an explicit rule against tuning itself to a score". The energy reader led with neither, opening with purpose and scale, and said the most concrete content was the lessons, the reviewers misses and the low product share. Fixed from their confusions: "Four classes of decision are the director's" contradicted the "7 kinds of action" read from `background/one_way_door.py`, and the prose was wrong against the code, so it now lists the seven; "A refused one leaves no record" now reads "Refusals are not logged, so they are not counted". Not fixed here, and left open: both readers read the HTML source, so sections the page fills from its feeds looked empty to them; the one that a reader without JavaScript also sees empty is the belief-and-truth number, which the parent steer asks to render at publish and which is still filled by script. The low product share (4% to 24% a week) is shown as it reads, as the doors-and-pace steer asks.
