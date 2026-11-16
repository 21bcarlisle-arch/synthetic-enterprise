**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] EP11 reframe approved; test a declared payment lifecycle against past DD defects (2026-11-16)

**Type:** RULING and STEER, through the advisor channel. The director's words, from chat on Mon 16 Nov, 10:10 GMT, answering the advisor's two questions in order:

> "Yes. Yes. Here's more I think https://github.blog/engineering/architecture-optimization/inside-githubs-new-git-storage-architecture/"

The two questions, as asked at 10:09 GMT:
1. "Do you approve reframing EP11 ('Direct Debit against a real sandbox') so it tests failed-payment paths inside the simulation, without a live GoCardless sandbox?"
2. "Shall I stage a test where the machine writes the customer payment lifecycle as one state diagram and checks whether it would have caught our past direct-debit defects?"

## 1. EP11: the reframe is approved

- **Close `for_the_director` row `ep11-is-titled-direct-debit-against-a`** as answered: approved, his words above. EP11 tests the unhappy payment paths its origin note names inside the walls. There is no live sandbox, no allowlist change and no account under Poesys's name (G5). Transport stays with EP6.
- Retitle EP11 to match, and record the ruling where EP11's `director_ruling` lives.

## 2. Test a declared payment lifecycle against past DD defects

**What the advisor found (check it).** From Pavlyshyn, "Your agent doesn't need an ontology. It needs a conceptual model" (15 Nov): an agent's model needs facts, processes and rules, and a process is a state diagram listing every legal move. We have the facts (`docs/design/the_map/concepts.yaml`) and the rules (`company/compliance/domain_invariants.py`). We have **no declared supplier-side payment or account lifecycle**:
- `git grep` finds state machines only on the world side (`simulation/churn_journey.py`, `simulation/life_events.py`);
- 28 files under `company/` touch direct debits.

Our repeat failures are lifecycle-shaped: the half-month first DD, bill shock (a DD change for one population, the bill for another), and the journey's end with two homes.

**The question.** Would one declared lifecycle have exposed the past DD defects as illegal or undefined moves?

**The outcome wanted.**
1. **Knowledge page first (K8).** What the rules require at each stage, from the licence conditions, the Direct Debit Guarantee, and Ofgem's guidance on DD setting and reviews; published practice; GAPs. Search before asking (K4).
2. **Write the lifecycle as one state diagram,** as data in one file, with every state and every legal move and its trigger:
   - sign-up;
   - first DD set;
   - bills;
   - DD reviews and changes;
   - credit and debit balances;
   - arrears;
   - switch away;
   - final bill and refund.

   Mark each move that is a regulatory obligation. It describes what a supplier does, so it lives on the company side of the wall.
3. **Replay the past DD defects against it.** Name the findings first and pre-register a prediction. For each, say whether the diagram shows the defect as an illegal move, an undefined state, or neither.
4. **Decide by the rule set now.** If it would have exposed most of them, propose it as the declared home the 28 files check against, as one check, not a framework. If not, say so and drop it. This is measured, like the concept-link test (0 of 3, dropped) and the collision test.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-16 | GitHub, "Inside GitHub's new Git storage architecture" (Project Rubicon, Raman & Celenza, 5 Nov) | Director | Only ref updates need agreement; objects are immutable so writers never collide on them; compare-and-swap on refs; maintenance off the hot path. Our lanes share one working tree and index, which is the opposite. Relevant to the 14 Nov collision finding and to the unmeasured cost of re-gating when origin moves. | NOTED; informs the gate re-run measurement |

(This is the "GitHub Rubicon" entry owed since 10 Nov.)

## Risk

Touches: one `for_the_director` row, EP11's record, a knowledge page, one lifecycle data file, a read-only replay.
Blast radius: none to runs until a check is proposed.
Probable failure mode: **a lifecycle drawn after the defects are known, so it "catches" them by construction.** Draw it from the rules and published practice first, record it, then replay.

Proportionality: ruling plus doc-and-measurement. Implement directly.

— Director ruling and steer, 16 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

16 Nov, delivery seat.

**1. EP11.** The reframe was already on origin when this file was read. The director's earlier 09:27
"Yes and yes" had closed `for_the_director` row `ep11-is-titled-direct-debit-against-a` (980c242ddf),
and EP11's title was already "Direct Debit against a bureau counterparty in the world" (209f1b93f).
His 10:10 "Yes" confirms the same ruling, and both of the advisor's questions are closed as answered in
`docs/observability/open_question_register.json`. Nothing else changed.

**2. The declared lifecycle: measured, and dropped.**
- K8 first: a lifecycle section on `docs/market_research/payments_and_direct_debit_2026-10-25.md`
  (rules per stage, GAPs, design choices, and the drafter's contamination stated).
- The diagram was drawn from the rules: `company/compliance/payment_lifecycle.yaml`, 14 states, 32
  moves, 6 invariants, 9 obligations. It was landed with the pre-registration (sample by name rule,
  grades, decision rule, prediction) before the replay.
- Result: **10 of 34 past DD defects exposed (29%)** in the deciding reading, against a prediction of
  about 36%, so drop. It is 14 of 34 with the two contaminated invariants, and 8 of 34 without two
  further defects contaminated by origin. No defect sat in an undefined state.
- Record: `docs/staging/records/SEAT_RESULT_A_DECLARED_PAYMENT_LIFECYCLE_WOULD_HAVE_EXPOSED_10_OF_34_PAST_DD_DEFECTS_SO_IT_IS_DROPPED_2026-11-16.md`.
- The yaml leaves `company/` in the commit that records the result. One class (four repeats of DD
  activity after the mandate ended) is noted as the lead for a single domain invariant, should it
  recur.

**Reading log.** The GitHub Rubicon row is appended, in the log's own columns.
