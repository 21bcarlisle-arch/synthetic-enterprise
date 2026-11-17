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
