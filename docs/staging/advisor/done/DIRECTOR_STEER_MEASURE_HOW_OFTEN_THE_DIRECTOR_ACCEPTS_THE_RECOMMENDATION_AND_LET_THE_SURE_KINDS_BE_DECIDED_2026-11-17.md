**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Measure how often the director accepts the recommendation, and let the sure kinds be decided (2026-11-17)

**Type:** STEER, through the advisor channel. The director's words, from chat on Tue 17 Nov:

- 06:24 GMT: "ideally I don't want to have to get involved in detailed results just steer strategy, direction and big goals."
- 07:33 GMT, sharing *Domain-Driven Design: The First 15 Years* (DDD Europe, Leanpub, version of 2024-01-11): "Anything interesting or relevant for us in this."
- 07:35 GMT, on the advisor's recommendation below: "Do it"

## What the advisor found (check it)

- **Jef Claes, "From Human Decisions, to Suggestions to Automated Decisions"** (pp. 203–209). A shop's refund decisions moved through three stages:
  1. Humans decide from one fixed view, and each decision records the snapshot it was based on (`BasedOnSnapshotId`).
  2. The machine suggests with a confidence score, humans pick, and suggestions are compared with picks.
  3. The machine decides, deferring to a human when not confident.

  The trigger for stage 3 was the human's own observation: "I almost always find myself picking the first option… Just defer decisions and call in a human when the machine is not confident enough."
- **We are at stage 2 with the director.** The machine and advisor recommend, he answers, and "silence is validation" already holds. Nobody has measured how often his answer matches the recommendation, or by what kind of decision.
- **Martin Fowler, "Multiple Canonical Models"** (pp. 199–202). One model per bounded context, with translation between overlaps. His example is an electricity utility where "meter" meant the grid connection, the customer's supply, or the physical meter. Our concept register's one home per layer, and the world/company wall, already follow this. Bill shock was the polyseme failure. It confirms the design and needs no build.
- **Jérémie Chassaing, "Time"** (pp. 210–212). "There is no change in the domain that is not due to an Event"; in markets things happen at 4pm "because the bell rang", not because it is 4pm.
- **Scott Wlaschin, "Domain Modeling with Algebraic Data Types"** (pp. 113–134). Make illegal states unrepresentable.

## The outcome wanted

### 1. Acceptance rate by kind of decision (Claes, stage 2 to stage 3)

1. **Find the record of his answers.** Candidates: answered rows of `for_the_director` in `DIRECTION.yaml` and its history; `docs/staging/advisor/done/` rulings and steers, whose header quotes his words beside the recommendation; `docs/direction/decisions.jsonl` where it records his answers. Say what each source holds and what it misses.
2. **For each decision, record:** what was recommended; what he answered (yes, no, changed, or silence-as-yes); and the kind of decision. Define the kinds before counting, for example:
   - a fidelity change;
   - a measurement or trial;
   - adopting or rejecting an outside source;
   - a harness or efficiency change;
   - a curriculum or world choice;
   - strategy, vision or canon intent;
   - a G5 wall.
3. **Report the acceptance rate per kind,** with the bound its count earns. Keep "silence-as-yes" separate from an explicit yes; they are different evidence.
4. **Propose, don't enact.** Where a kind is accepted near-certainly over enough decisions, propose that kind moves to "the machine decides and records it in the stretch log". It reaches him only when the machine's confidence is low or the decision is strategic. Strategy, vision, canon intent, curriculum, anything he has asked to see (G9) and every G5 wall stay with him whatever the rate. The proposal is one line in `for_the_director` that he can answer yes or no.
5. **Record the snapshot with each decision from now on.** Note what was known when it was recommended, so later agreement can be checked against the information he had (Claes's `BasedOnSnapshotId`).

The same pattern applies inside the company, as a note and not a build here: M4's automated method should log each customer decision with the snapshot of what the supplier knew. That is the epistemic wall made auditable. Say whether the company already does this.

### 2. Fold two essays into the payment-lifecycle test (16 Nov ruling)

Amend `DIRECTOR_RULING_EP11_REFRAME_APPROVED_AND_TEST_A_DECLARED_PAYMENT_LIFECYCLE_AGAINST_PAST_DD_DEFECTS_2026-11-16.md`:
- **Events as triggers (Chassaing).** Every move in the lifecycle names the event that causes it, such as DD collection day, billing period end, review date, switch completion or final read, never a bare clock time.
- **Illegal states unrepresentable (Wlaschin).** Where the test's result recommends the lifecycle as the declared home, propose types under which a defect like a half-month first DD cannot be constructed, not only a check that rejects it.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-17 | *Domain-Driven Design: The First 15 Years*, essays from the DDD community (DDD Europe, Leanpub; 2024-01-11 version) | Director | Claes: human to suggestion to automated decision, gated on measured agreement, so measure his acceptance rate by kind. Fowler: multiple canonical models (the utility "meter" polyseme), which confirms our design. Chassaing: events, not clock times. Wlaschin: illegal states unrepresentable. Both feed the lifecycle test. | ADOPT (two measurements) |

## Rules

- **His authority is unchanged.** This measures and proposes; it moves nothing out of his hands without his yes. Proposing a new gate or ceremony on his path is a defect, and so is adding a review step to reduce his load.
- **Define the kinds before counting** ("say what it is"), and pre-register which kinds you expect to be near-certain.

## Risk

Touches: read-only over direction records and staging history; one `for_the_director` line; an amendment to the lifecycle test.
Blast radius: none until he answers.
Probable failure modes:
- **Silence counted as agreement when he simply did not read it.** Keep silence-as-yes separate, and never let it alone qualify a kind.
- **Kinds drawn to make a rate look high.** Define them first; report every kind, including those that are not near-certain.

Proportionality: measurement plus one proposal. Implement directly.

— Director steer, 17 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

*Worker, 17 Nov 2026.*

**1. Acceptance rate by kind.** The kinds, answer codes and predictions were written first. Then 77
decisions were coded: 45 closed `for_the_director` rows and 32 advisor-channel replies. **No kind
qualifies.** Measurement is nearest: 15 of 16 accepted as recommended, with a 90% lower bound of
0.76 against the 0.80 the rule needs. Strategy is lowest at 0.63, and its other seven answers are all
changes, not refusals. One recommendation in 77 was refused outright. Silence is never recorded
in either source. The advisor channel only keeps what he said yes to, so its rates are upper
bounds. Three of my four predictions were refuted, including the one that harness would qualify.
Record:
`docs/staging/records/WORKER_RESULT_NO_KIND_OF_DECISION_IS_YET_SURE_ENOUGH_TO_BE_THE_MACHINES_MEASUREMENT_IS_NEAREST_2026-11-17.md`.
**No `for_the_director` line is raised**, because nothing qualifies. Per the 17 Nov cost-per-result
steer, these figures do not go to him. The record says when to count again: when measurement has 20
explicit answers.

**Snapshot from now on.** `director_concerns.raise_concern` writes `based_on`, the commit the
recommendation was written against, on every new row. There is a test for each branch, and the
mutation that leaves the field empty fires.

**Company side.** Partly. A bitemporal decision log exists
(`company/governance/decision_rights.py`), but only the renewal desk and the write-offs write to it,
and its `context` has no snapshot key. Noted in the record, not built.

**2. The payment-lifecycle amendment.** There was nothing left to amend. The lifecycle test had
already concluded on 16 Nov (381d3a153): 10 of 34 defects exposed, under the half the ruling set, so
the lifecycle was dropped and the EP11 ruling moved to done. Checked against the two essays anyway:
- **Chassaing:** the dropped diagram (5bf7e7c87, `company/compliance/payment_lifecycle.yaml`) already
  named an event on each of its 32 transitions: AUDDIS, ARUDD and ADDACS codes, billing period end,
  new information, the notified collection date. None is a bare clock time.
- **Wlaschin:** this applied only where the test recommended the lifecycle as the declared home. It
  did not, so no types are proposed. The half-month first DD was exposed only in the contaminated
  reading (I*).

The reading-log row is appended.

**A second coder (0fadd2b9b, seat lane).** It coded 85 decisions on its own pre-registration (3d9dbe930,
95% bound). Its answers agree with this count on 66 of 76 shared decisions, and its kinds on 57 of 76.
Its measurement verdict turns on one call (19 of 19, bound 0.83, against 18 of 19, bound 0.75), so
both coders say no kind qualifies yet. The next count wants the answer coded when he answers
(continuation `director-answer-code-at-answer-time`), not by a reader afterwards.
