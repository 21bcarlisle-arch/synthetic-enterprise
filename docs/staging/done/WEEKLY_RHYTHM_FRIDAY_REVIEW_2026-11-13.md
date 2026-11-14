**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — weekly rhythm

# Friday: what actually happened against Monday's ranking, and the adjustment

**Due:** 2026-11-13 (Europe/London). Armed by the step before it.

> **LATE.** Filed on Saturday 14 Nov at about 02:35 London, one day after it was due. The Monday it reviews was closed in the same tick, five days late, after every Monday since 7 Sep had lapsed unclosed. This is the first Friday the rhythm has ever filed. Numbers are read from origin at 84a44b51c3, not recalled.

Monday's ranking for this week is in `docs/staging/done/WEEKLY_RHYTHM_MONDAY_RANKING_2026-11-09.md`. Read it against what actually landed, item by item, and adjust. A review that only records outcomes teaches nothing: where a ranked item did not move, say whether it was wrong to rank it or wrong to leave it.

## Overdue rituals, measured from their own artefacts

- **harness_pruning** (never run) — The harness pruning ritual (HARNESS_BEST_PRACTICE_ASSESSMENT.md §6): which controls have never fired, which duplicate another, which are keyed to today's answer. Verdicts belong in a new dated docs/design/HARNESS_PRUNE_<date>.md.
- **mothball_audit** (last run 2026-07-29, 18 day(s) past a 90-day cadence) — Re-run the mothball question over the apparatus: for every gate, queue, window and reporting ritual, what is this actually for under THE STANDARD? Mothball what cannot say. Verdicts belong in a new dated docs/design/MOTHBALL_<date>.md.
- **claude_md_decay_audit** (last run 2026-08-27, 34 day(s) past a 45-day cadence) — The CLAUDE.md decay audit: which rules in CLAUDE.md are now enforced elsewhere, which have no enforcement at all, and which describe a machine that no longer exists. Findings belong in a new dated *_DECAY_AUDIT_<date>.md.

## Parked work that stated what remained

- **ADVISOR_FINDINGS_REGISTER_ERROR_CHANNELS_ARE_INERT_2026-08-09.md** (96d) — OPEN: §2a (older certificate = more wrong, as a mean shift) and §2b (
- **WORKER_FINDING_THE_ONLY_DOOR_PAIR_A_TEST_RUN_CAN_REPUBLISH_IS_THE_ONE_NOTHING_COMPARED_TO_ITS_LEDGER_2026-08-17.md** (88d) — OPEN: §"What this tick did NOT build" **item 2** — the SITE-lane > live tripwire. It is unbuildable *as a gating control* until the finding-4 dive

The rest of the parked room is 21 document(s), oldest 113 day(s). That is a count, deliberately, not a list: the bulk drain is already declined in `DIRECTION.yaml`'s `not_now` with a reason that still stands, and re-listing it every week would make this rhythm the noise it exists to replace.

## Burn per kind of turn, this week

| kind | model | turns | per day | landed | median fresh tokens | median cache-read tokens | median weighted $ | total weighted $ | advisor calls (turns without) |
|---|---|---|---|---|---|---|---|---|---|
| delivery_seat | claude-opus-5-5 | 48 | 6.9 | n/a | 115,488 | 1,182,818 | 1.318 | 66.53 | 0 (48) |
| other | claude-fable-5-2 | 14 | 2.0 | 0% | 136,083 | 769,081 | 0.0 | 0.0 | 0 (14) |
| other | claude-haiku-5-5 | 1 | 0.1 | 0% | 4,457 | 3,912 | 0.0 | 0.0 | 0 (1) |
| other | claude-opus-4-8 | 2 | 0.3 | 0% | 4,469 | 4,463 | 0.0 | 0.0 | 0 (2) |
| other | claude-opus-5 | 1 | 0.1 | 0% | 8,587 | 0 | 0.086 | 0.09 | 0 (1) |
| other | claude-opus-5-5 | 42 | 6.0 | 0% | 27,083 | 132,679 | 0.312 | 18.75 | 5 (37) |
| seat_executor | claude-haiku-4-5-20251001 | 1 | 0.1 | 100% | 257,494 | 7,899,185 | 3.58 | 3.58 | 0 (1) |
| seat_executor | claude-opus-5-5 | 185 | 26.4 | 78% | 120,970 | 3,923,513 | 2.038 | 451.09 | 0 (185) |
| worker_tick | claude-opus-5-5 | 171 | 24.4 | 67% | 124,579 | 3,806,107 | 2.032 | 429.09 | 0 (171) |

**Prompt changes under measurement** (landing rate on the old wording vs the new; revert a change whose new arm lands less, once both arms have turns):

- `prompt-audit-2026-09-29` seat_executor: old 0 turns, no turns yet; new 186 turns, 78% landed. To revert: restore the capitalised line in the `background.seat_executor` CHARTER.
- `prompt-audit-2026-09-29` worker_tick: old 0 turns, no turns yet; new 171 turns, 67% landed. To revert: restore the capitalised `background.worker_tick` WORKER_PREAMBLE.

**Propose, then enact unless the director disagrees.** For each kind of turn, is its cadence, model tier or effort earning what it costs? Enact the reversible changes (timer cadence, `model_tier`, effort), each with its reversal written down, and NTFY the director what changed and how to reverse it. Anything the weighted figure cannot judge -- whether the turns LANDED anything -- is read from the commits, not assumed.

## The balance for the coming week (proposal; stands at the reset unless he answers)

The live feature share in the BUILD draw is `0.33` (`docs/direction/priority_order.yaml`, `correctness_stretch.feature_share`).

Propose the split across **correctness and backlog / harness / world features / supplier features / knowledge**, and name what each share is for. Base it on the week gone, each measured, not recalled: the learning loop's hit rates; regressions; serious classes per cold read (`serious_class_rule`); whether the site published; and the week's usage curve. Write the agreed share into `feature_share` and stage the proposal to the advisor channel. Correctness keeps first claim; the publish gate does not move.

**Proposal: hold `feature_share` at 0.33 for the week from 16 Nov.** Changing it would be a second variable in the same week the 16 Nov book grades W1-W4 and the value test reads. Correctness keeps first claim because both its areas read STOP (below), and the share is not the binding constraint: both areas now have their maps. Harness work is held at today's level, with one exception: the three overdue rituals go first in the harness lane. Knowledge goes to the M3 utility page (due 23 Nov). Nothing in `priority_order.yaml` is edited by this step. A proposal that changes nothing needs no new write.

**The accelerate list** (`priority_order.yaml` `accelerate:`), ranked: ready work worth pulling forward from Saturday if more than the ~10-point reserve is unspent. Decide it here, never on the day. Live list: EMPTY -- write it now.

## Cost of the work to come

Cost of work to come, fitted from 1001 landed sessions over 30 days (one point = USD 7.6 weighted; the week holds 100). Each landed session carries its share of the spend that landed nothing: every session spent 685 points, 1.66x what the landed sessions alone spent.

| work class | landed sessions | median points | range | open level steps |
|---|---|---|---|---|
| world_build | 202 | 0.68 | 0.43-1.10 (quartiles) | 102 |
| supplier_build | 128 | 0.71 | 0.50-1.09 (quartiles) | 40 |
| grading_run | 221 | 0.48 | 0.31-0.76 (quartiles) | 1 |
| knowledge_page | 97 | 0.63 | 0.41-0.85 (quartiles) | 3 |
| site_page | 55 | 0.78 | 0.52-1.14 (quartiles) | 15 |
| harness | 148 | 0.44 | 0.33-0.70 (quartiles) | 31 |
| record | 150 | 0.34 | 0.25-0.56 (quartiles) | 6 |

**Landed sessions per level step:** median 2, range 1.5-7.5 (quartiles), measured over 13 level steps named by a landed commit; 5 step(s) no landed commit names are left out, not counted as zero. Biased LOW: work toward a step in a commit that does not name the atom is not counted.
**Atom backlog:** 198 open level steps, about 255 points (128-1507), **2.6 weeks (1.3-15.1)** at the full allowance.
**Advisor queue:** 0 director file(s).
**This week:** no reading since Monday's reset (last: 44% at 2026-10-25T06:35 UTC), so what remains is not known.

| step | atom | points | fits this week | split first |
|---|---|---|---|---|
| 2 | W2_36 | 1.4 (to 8.2) | no |  |
| 2 | D48 | 1.4 (to 8.2) | no |  |
| 2 | B7 | 2.7 (to 16.5) | no |  |
| 2 | W2_37 | 2.7 (to 16.5) | no |  |
| 3 | E6 | 1.4 (to 8.2) | no |  |
| 3 | W2_41 | 1.4 (to 8.2) | no |  |
| 3 | B11 | 1.4 (to 8.2) | no |  |
| 3 | EP1 | 1.4 (to 8.2) | no |  |
| 3 | W2_38 | 1.3 (to 6.4) | no |  |
| 4 | W2_39 | 1.4 (to 8.2) | no |  |
| 4 | C34 | 2.8 (to 16.4) | no |  |
| 4 | C35 | 1.4 (to 8.2) | no |  |
| 4 | C29 | 2.8 (to 16.4) | no |  |
| 4 | PB4 | 1.4 (to 8.2) | no |  |
| 4 | PB5 | 2.7 (to 16.5) | no |  |
| 4 | B12 | 1.4 (to 8.2) | no |  |
| 4 | W3_3 | 2.7 (to 16.5) | no |  |
| 5 | EP4 | 1.4 (to 8.2) | no |  |
| 5 | C30 | 4.1 (to 24.7) | no |  |
| 5 | G14 | 1.4 (to 8.2) | no |  |
| 5 | C5 | 2.8 (to 16.4) | no |  |
| 6 | EP16 | 4.1 (to 24.7) | no |  |
| 7 | C4 | 2.8 (to 16.4) | no |  |

**Estimate against actual:** no item drawn with an estimate has landed yet; the draw records one on every Lane 0 item from now on.
**Not yet estimated:** open findings (no classifier reads them yet).

**Within the priority order, never instead of it.** Of two items of equal value take the cheaper. The draw flags (`COST FLAG`) any item estimated above 10 points before it starts; split it, or say why not. A class whose items miss by more than 3x either way is a finding, and its fit is refitted from the landed sessions every time this runs.

## What actually happened

_Against Monday's ranking, item by item. Where one did not move, say whether it was wrong to rank it or wrong to leave it._

- **1. The fix and its book: moved.** The reg 6D refund clock landed on its seventh attempt (ceeefa5960, promoted through 99c8e05dd). S6b posts a repayment as money in on its cash day (69866925bd). The statement walk carries the closing set-off: walk against page went from 84 legs to 0 of 1,302 (84a44b51c3). The plan re-offer exception was retired at 0 of 1,248 (a481c9ab96). Ranking it first was right.
- **2. The value test's 12-draw family: running, not read.** The driver (77bf74f880) and the per-household-year appendix (837a26f020) landed, and the noise floor now records household-years per seed (b4703df53a). The grade was due after 08:00Z today and is not on origin. Ranking it was right. It moves on its own clock, and nothing here can make it go faster.
- **3. The rhythm: moved, five days late.** Ranking it was right, and leaving it was wrong. It sat in focus for four orientations and was never drawn, while the draw took newer items above it each time. Lane 0 drew it only once the seat made it the delivery decision. **The adjustment:** an armed rhythm step that is past due should rank above new direction items in Lane 0. A focus row that only orders work never fires on a step nobody draws. That needs a mechanism. Here that means the draw reading the baton, which `--status` already prints. It is not a note in this document. Filed as the next harness item. It is not built in this tick.

## The learning loop, as it reads on origin

Read with `background.learning_loop.measures()` at 84a44b51c3 (7-day window, 21 graded fixes). The figures differ from the ones the drawn item quoted because two grades landed since it was written.

| area | held of graded | code-or-reader misses | W1 stop | map on origin |
|---|---|---|---|---|
| repayment-posting | 30 of 49 | 15 | **STOP** | REPAYMENT_POSTING_AREA_MAP_2026-11-14.md (ad48737415) |
| level-dd | 41 of 57 | 15 | **STOP** | LEVEL_DD_AREA_MAP_2026-11-11.md |
| class-l | 11 of 12 | 1 | no | |
| close-refund-book | 15 of 15 | 0 | no | |
| eleventh-read-prereg | 6 of 6 | 0 | no | |

**0.143 regressions per fix over 21 graded fixes. The drawn item quoted 0.158 over 19.** Cold-read escapes: [2]. W1's stop condition is now built into the draw (c29205f253). A fix in an area with three code-or-reader misses in seven days is refused until that area's map is on origin, so the stop is no longer applied by hand.

**Read with care.** Repayment-posting went from 25 of 41 to 30 of 49 after its map landed. That is 5 held and 3 missed since the map. One week cannot say whether the map is working. The 16 Nov book grades W1-W4 against it.

### The two unparsed trailers, named without rewriting history

`measures()` reports both under `unparsed`. Neither is a malformed trailer. Each is a prose line in the body that wraps so that it begins with `Graded:`. They age out of the 7-day window on 17-18 Nov.

- **a481c9ab96** ("Graded: e1587ec5b 19 -> 0 of 1,248…"). This is the plan re-offer row, a collections-journey area with no trailer of its own. It made one prediction, 0 of 1,248, which held on both books. **held=1 missed=0 code=0 reader=0 regressed=0 width=0** (a point prediction). It is not added to any area above, because the area was never named in a trailer.
- **ef64912eee** ("Graded: trailer, so background/learning_loop.py…"). This is prose. The commit's real trailer, `Graded: class-l held=3 missed=1 code=0 reader=1 regressed=0 width=0.0`, parsed and is **already counted** in class-l above. **held=3 missed=1 (reader=1)**, counted once. The unparsed row adds nothing.

The parser's reach: `_GRADED` matches any line that starts with `Graded:`, so a wrapped prose sentence is refused as a bad trailer. That is the safe failure (reported, never dropped). The cheaper cure is in the writing: a body sentence should not begin with the trailer's keyword.

---

Close it with `python3 -m background.weekly_rhythm --close`. That arms the next step — nothing else does — and archives this document to `done/` itself, so the rhythm disposes of everything it files.
