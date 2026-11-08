**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Census of the director's quoted questions in 59 archived rulings: 115 answered, 19 not his, 2 carried, none needing him (2026-11-08)

**Claim:** `census-the-archived-rulings-quoted-questions`, owed by
`docs/staging/done/SEAT_FINDING_THE_ARCHIVE_QUESTION_GATE_NOW_READS_ADVISOR_DONE_AND_64_ARCHIVED_RULINGS_CARRY_HIS_QUESTIONS_UNREGISTERED_2026-11-08.md`.

## What was done

Every ?-sentence inside his quotes in `docs/staging/done/` and `docs/staging/advisor/done/` that had no
entry in `docs/observability/open_question_register.json` was read against its whole ruling: his words in
context, the advisor's text, and the Done section. That was 136 questions in 59 rulings. Three readers
split the rulings, and the seat sampled their dispositions against the files. Each of the 136 now has a
disposition dated 2026-11-08. Re-running the extractor over both archives gives **0 without a disposition**.

| how it closed | rows | status |
|---|---|---|
| answered in the ruling's own Done section | 60 | answered |
| answered elsewhere: the ruling's body (the advisor answering in place, or the design he approved), or a commit or page that was opened | 31 | answered |
| a fragment of a longer question ("Or not?", "No need?"), answered as part of it | 22 | answered |
| not his question: a check string the ruling prescribes for the machine ("could a real supplier know this?", "does this die at 10^5?"), a description of a gate's logic, or page copy | 19 | wrong |
| never answered until now, answered from the record | 2 | answered |
| owed work, carried | 2 | carried |

**The premise's two examples, both answered:**
- *"Also why wasn't this picked up automatically?"* (24 Oct code review) was answered in
  `SEAT_FINDING_OWN_CODE_REVIEW_UNUSED_DUPLICATED_AND_WALL_CROSSING_2026-10-24.md` §2. An `owed` deferral
  was accepted with no owner and no date, and the orphan control lost its only caller.
- *"Does debt sit with supplier or dno?"* was answered for other markets in the pack synthesis
  (7fb1aabcc3). For GB the record had the evidence but no direct sentence, so the census wrote one:
  the debt sits with the supplier, never the DNO.

**None needs the director.** No question was a decision of his that nobody took. So nothing was raised
through `director_concerns`, because raising a question he asked as a concern for him to rule on would
hand him back his own question.

## Answered for the first time here (the advisor may want to relay these)

- `b515af8d4e74` · DIRECTOR_STEER_COMFORT_HEALTH_AND_CARBON_ARE_OUTPUTS_AND_BUDGET_FIRST_ADVICE_IS_PARKED_2026-10-25.md — *"Many people have the heating on all the time and could save money?"* — Fewer than "many" say they do, more than that behave as if they do. `docs/market_research/heating_behaviour_comfort_and_health_floors_2026-10-25.md` ("Continuous heating") gives 6% heating all year and ~4% reporting 17 h+ runs, but 30.9% of homes show a flat living-room profile (H15). The median is 7-8 h a day. The 31%-more-gas for 24 h against 9 h is from one test house in the ruling's pack, so the saving is real but home-specific and bounded by the health floor (§6 of `docs/design/PERSONALISED_ASSET_WORLD.md`). Note that boiler homes are never `continuous` in `fabric_physics.py`, per the page's own FLAG.
- `3a96c2852f77` · DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN_2026-10-24.md — *"Also is there knowledge for the main things already built?"* — Partly. The six built domains the map steer found with notes but no page now all have one: payments/DD 997cfc67e, switching 3660142eb, accounts and capital 25d95f3ab, and tariffs, smart meters/HHS and vulnerability/PSR 2d33139a4b. But by the map's own coverage today (tools.the_map.build()['coverage']), only 114 of 745 modules attach to a concept with knowledge, and 631 attach to none, with no machinery ruled yet.
- `be32aef59a4d` (GB half, above): In GB, with the supplier: the supplier bills the household and carries its arrears; the DNO bills the supplier for use of the network (DUoS), never the household. A switch leaves the debt with the old supplier, except prepayment debt moved under the Debt Assignment Protocol. GB evidence: docs/staging/advisor/done/DIRECTOR_EVIDENCE_WHAT_HAPPENS_TO_UNPAID_DOMESTIC_ENERGY_DEBT_2026-11-07.md. Abroad, same file's synthesis item 5 and pack dimension 16 (7fb1aabcc3): mostly the same, but Italy's CMOR lets arrears follow the customer, and in Belgium debtors move to the DSO as social supplier.

## Carried: work nobody has done yet

- `5f6977f9349b` · DIRECTOR_STEER_FORWARD_YEARS_MUST_REPRODUCE_VOLATILITY_AT_EVERY_SCALE_2026-10-25.md — *"Will the gas price have appropriate volatility too?"* — Not yet. The K8 page (docs/market_research/how_gb_gas_and_power_prices_move_2026-10-25.md §0.1) finds the world's 'NBP' is a monthly-flat TTF proxy, so daily and weekly gas volatility is zero by construction (recorded as blocking in 085f89e42e). What would answer it: a daily NBP (or daily TTF plus FX) history (gap 9), volatility claims in tools/world_claims.py (none exist), and EP16 grading the generators against them. Carried on EP16 (forward-years grading against the volatility claims), which his 26 Oct correctness ruling holds behind the correctness stretch.
- `b847cb1a34a8` · DIRECTOR_STEER_FORWARD_YEARS_MUST_REPRODUCE_VOLATILITY_AT_EVERY_SCALE_2026-10-25.md — *"And mix and depth of backwardation and contango?"* — Not yet. The same page §0.2 finds the forward quote is an EWMA times a fixed monthly shape times an always-positive premium. Backwardation arises only from the shape or EWMA lag, and the seasonal spread cannot invert. The record's share of backwardated days is unpublished (gap 4). What would answer it: measure that share and the slope-on-spot from NBP and GB forward settlements, file it as a world claim, and grade the forward quote under EP16. Carried on EP16 (forward-years grading against the volatility claims), which his 26 Oct correctness ruling holds behind the correctness stretch.

## Found on the way: a ruled step whose hand-off was never written

The 24 Oct code-review finding (§6) owes *"the archive (hand-off `archive-the-unhooked-supplier-modules`),
after 26 Oct"* of 268 supplier modules that only their tests import. No commit on origin/main archives
them. The hand-off ID is in neither `seat_continuation --list` nor the direction files. The step was
named but never handed on, which is the same shape as the "why wasn't this picked up automatically?"
answer. It is handed off with this landing.

## Known limits

- The readers' dispositions are judgements. A wrong `answered` closes a question silently, which is the
  direction the 28 Jul ruling fears. They were told a Done section that acts on a steer without
  answering it is not an answer. The seat sampled 9 of 136 and found none stretched. That sample bounds
  the error rate only loosely.
- The keys are per (ruling, normalised question). If a ruling's quoted wording is edited later, the key
  changes and the question reopens. That is the gate's intended behaviour.

## How to reverse

Revert the landing commit. The dispositions are additive, keyed per question, and nothing else reads them.
