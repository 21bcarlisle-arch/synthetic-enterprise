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
