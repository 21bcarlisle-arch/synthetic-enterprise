**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Cost per result and rework rate: for the machine to act on, not for the director to read (2026-11-17)

**Type:** STEER, through the advisor channel. The director's words, from chat on Tue 17 Nov:

- 06:15 GMT, sharing https://www.span.app/blog/uplift with no comment.
- 06:24 GMT, on the advisor's recommendation below: "Yes. But ideally I don't want to have to get involved in detailed results just steer strategy, direction and big goals."

## What the advisor found (check it)

- **The source.** Span, "Introducing UPLIFT: Measuring AI Effectiveness in Engineering" (Stephen Poletto). Vendor marketing for its own platform; no dataset and no results. It has six dimensions: Uptake, Pace, Leverage (human attention per outcome), Investment (cost per outcome), Focus and Trust. It has three stages: Assisted, Agentic and Factory. Its useful line: "Trust is the gate on Leverage: autonomy should expand only as fast as Trust can prove it is safe."
- **We are past its Factory stage.** Uptake is meaningless here. Focus is held by the Friday balance review and `priority_order.yaml`. Pace is partly held by commitments with done-tests and due dates.
- **Two gaps.**
  - **Investment:** cost per finished result. It was named as unknown in the 15 Nov reading-token discussion; we know cost per seat kind, not per result.
  - **Trust:** rework rate as a standing number. It exists only as a one-off measure in the 15 Nov CLAUDE.md trial.

## The outcome wanted

1. **Define "a result" first** ("before measuring a thing, say what it is"). Candidates are a closed staging item, an atom level move, or a landed `[ADVISOR-STAGED]` steer reaching its done-test. If these are distinct experiences, measure them separately and say which one each figure means.
2. **Two standing lines in the Friday efficiency review** (the backlog started 16 Nov):
   - **cost per result:** usage points and tokens by class;
   - **rework rate:** the share of landed commits reverted or corrected within 14 days.

   Each line shows the week, the trend and the bound its sample earns. No new dashboard, gate or daemon.
3. **The machine acts on them itself.** They steer its own choices: which trials to keep, where to spend, whether a kind of work is getting more expensive or less reliable. Use the trust idea as a rule for the machine: where rework rises in a kind of work, add verification there before adding autonomy.

## How results reach the director: they don't, by default

His words above are the rule. **He steers strategy, direction and big goals; detailed results are the machine's.**

- These figures go in the Friday review and the stretch log, which the advisor reads. They are **not** raised to `for_the_director` and not relayed as numbers.
- **Only a strategic implication is raised,** and only with a recommendation. For example: "rework in billing has doubled for three weeks, and I propose slowing billing autonomy until verification catches up", or "cost per result has halved, and I propose spending the saving on X". That is one line he can answer yes or no.
- The advisor applies the same rule: relay the decision a result implies, never the result.

## Rules

- **Measure what you can instrument reliably.** "A simple metric you trust beats a sophisticated one you don't" is the one other line worth taking from the source.
- **Key the result to the property:** cost and reliability of results, not activity volume.
- **No new ceremony on his path.** Proposing one is itself a defect.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-17 | Span, "Introducing UPLIFT: Measuring AI Effectiveness in Engineering" (Poletto), vendor framework with no data | Director | We are past its Factory stage; we already have Focus and part of Pace. Gaps: cost per result and rework rate, both now standing Friday lines the machine acts on. "Trust gates autonomy" becomes a machine rule. | ADAPT (two lines, no framework) |

## Risk

Touches: the Friday efficiency review, `tick_burn_rate` or `work_cost_estimate` (extend, don't add).
Blast radius: none to runs.
Probable failure modes:
- **"Result" defined to flatter,** for example counting small items so cost per result looks low. Mitigated by defining it before the first figure and keeping the definition fixed.
- **Rework hidden as "follow-up" rather than "correction".** Count any commit that changes a landed result's behaviour within 14 days unless it was planned in that result's own done-test.

Proportionality: harness measurement. Implement directly.

— Director steer, 17 Nov 2026, his words above; the reading and drafting are the advisor's.
