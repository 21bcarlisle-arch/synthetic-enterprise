# C32's fifth Expert Hour: the Safety Net only saw what the supplier knew, and it was read as a list when it is a welfare test

**Fate (2026-11-14):** RESULT. C32 stays at level 2. Two defects are fixed in this tick, both within
the atom's claim, and both with the commons amended first:
- one found by my own probe before the pass ran;
- one found by the pass itself (item 5).

**Blocker, named and dated:** a sixth blind pass is owed, and only on the widened net, because I
graded that policy myself.

## Before the pass: the net could not see a hint

The fourth pass's fix (ce8179c1d9) put the Safety Net in `WinterMoratoriumRegister.can_disconnect`
and fed it **established categories only**. Several kinds of evidence decide the licence answer
through a counterfactual:
- a needs code or agent flag graded "cannot determine";
- a registration naming no need;
- a birth date.

Those counterfactuals live in `protection_weighing_undetermined` and the two records'
`disconnection_protection`, and they asked the **licence alone**. The licence has no summer duty, so
none of them ever blocked in July. Measured at real inputs (15 Jul 2024, before this change, the
company answer was the licence's):

| evidence held | Jul licence | Jul company, before | Jul company, now | Jan company |
|---|---|---|---|---|
| code 26 "oxygen use" | permit | permit | **refuse** | refuse |
| code 22 chronic/serious illness | permit | permit | **refuse** | refuse |
| PSR registration, no need | permit | permit | **refuse** | refuse |
| flag `serious_illness` | permit | permit | **refuse** | refuse |
| flag `elderly` | permit | permit | **refuse** | refuse |
| no record, born 1944 | permit | permit | **refuse** | refuse |
| flag `job_loss` / `bereavement` | permit | permit | permit | permit |
| no record, born 1962 / 1985 | permit | permit | permit | permit |

**What changed.**
- **The counterfactual takes a decider.** `protection_weighing_undetermined`,
  `PSRRecord.disconnection_protection` and `VulnerabilityRecord.disconnection_protection` take a
  `decider`, which defaults to the licence.
- **A company decider exists.** `winter_moratorium.safety_net_protection` takes the licence
  decider's signature and applies the licence, then the net. A birth date that establishes
  pensionable age falls under the net. One in the untranscribed band reads "cannot determine".
- **`can_disconnect` reads the record.** It takes `record=` (or `categories=`, exactly one), so the
  same counterfactuals run against the company's policy. The licence answer is still readable on
  its own.
- **Two reason strings are corrected.** The licence decider's reason strings said the Safety Net
  "is not modelled here", which has been false since ce8179c1d9.

## The pass

The reviewer ran blind on a fresh agent, with no tools, as a veteran of PSR and
debt-and-disconnection operations. The plain words were the fourth pass's, with the disconnection
paragraph rewritten to describe the net and its reach to suspected needs. Its ledger row is the
C32 entry recorded 2026-11-14T22:30Z in `docs/observability/blind_review_ledger.jsonl`.

It returned 15 questions: 10 disqualifying, 5 supporting.

A first dispatch was sent the literal string `PACKET_PLACEHOLDER` instead of the packet. That was
my error. It produced a generic battery and is **not recorded**.

### The item that failed in part

**Item 5 (disqualifying):** "How do you justify applying the Safety Net as membership of four
categories, when the commitment is a test of inability to safeguard welfare due to age, health,
disability or severe financial insecurity?" The answer the reviewer needed was "the over- and
under-protection named on the surface, or a welfare-assessment step".

Neither was there. The commons said "operationalised as four categories" and named only the
financial-insecurity GAP.

**Fixed, in two parts.**
1. **The divergence is named in commons §4.** A categorical reading over-protects: a fit
   67-year-old is refused. It under-protects: sensory impairment, language, temporary life changes,
   the eight uncategorised needs and financial insecurity are all outside it.
2. **The net is widened, in the direction canon M3's floor points.**
   - Mental health is on S5's own "health" ground.
   - A child five or under is on its "age" ground, as a stated belief.
   - The control now refuses both in July. Dropping either from the set reds it.
   - A welfare assessment is not built. It is the practitioner question for the collections atom.

### The other fourteen, graded against the code

| # | | grade |
|---|---|---|
| 1 | DISQ | **passes on reachability.** The partition control proves the permit branch is taken, for job loss, bereavement, language, a 1985 birth date and no category. The run rate cannot be read: no production path calls `can_disconnect` (the fourth pass's item 7). |
| 8 | DISQ | **passes.** Month-inclusive October to March, judged on the decision date. Boundary tests exist at 30 Sep / 1 Oct and 31 Mar. |
| 11 | SUPP | **passes** (fourth pass, item 16): one decider serves both licences. |
| 13 | SUPP | **passes, and its guard is extended.** The AST guard against a numeric band deciding an outcome now names `safety_net_protection` and `can_disconnect`. A `total_score` planted in the company decider reds it. |
| 9 | DISQ | **known GAP, fails closed.** The reviewer says the Schedule 4 tables are short and public, so not transcribing them is a choice. That is fair. It is the next knowledge task for EH-5's band, and it can only narrow "cannot determine". |
| 7 | DISQ | **open, outside the claim.** No run, no distribution. With no birth date and no composition held, "cannot determine" will dominate. A first caller must publish that share. |
| 3 | DISQ | **open, new.** Pre-2017 PSR eligibility (the old SLC 26 list) against the needs-based register. Whether the 2016 months need a dated switch is a commons question. Filed here; it is not this atom's disconnection claim. |
| 2, 6 | DISQ | **out of scope.** These are the collections and prepayment atoms (PPM offer before disconnection, self-disconnection support). |
| 4, 10 | DISQ | **open, outside the claim** (fourth pass, items 6 and 5): consent, DNO sharing, and every process reading the register. |
| 12, 14, 15 | SUPP | **known gaps:** refresh cycle and expiry, coverage by year, and the PSR services. |

## Verdict

**FAIL in part, on item 5. Fixed in this tick. Held at 2.** Both fixes raise protection, which is
the safe direction. The widened net is a policy reading I graded myself, so a sixth pass is owed
on it alone. If that pass raises nothing within the claim, the level moves.

**Controls.**
- `test_the_safety_net_reaches_what_the_record_only_suggests` partitions the whole space: eight
  refused, four permitted.
- **Mutations, all red:** the record path ignoring the decider; the birth-date leg dropped; the
  net refusing everything; the weighing ignoring the decider; the no-need loop ignoring the
  decider; mental health dropped; under-fives dropped.

**Reversible:**
- delete `MENTAL_HEALTH` and `CHILD_UNDER_5` from `SAFETY_NET_CATEGORIES`;
- pass `categories=record.categories` instead of `record=`.
