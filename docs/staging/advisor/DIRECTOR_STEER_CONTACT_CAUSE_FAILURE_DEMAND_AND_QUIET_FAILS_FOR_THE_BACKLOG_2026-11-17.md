**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Contact cause, failure demand and quiet fails: an idea for the backlog, not for build now

**Type:** STEER, through the advisor channel. Finish what you're doing first, then take this next.

**What to do with it:** log it as a backlog idea beside yesterday's `simulator_spec_candidates` (`docs/direction/priority_order.yaml`). Rank it in Friday's balance review. Nothing is built this week.

## The director's words (chat, Tue 17 Nov, verbatim)

- 09:05: "Use channel preference and call abandonment, call duration, and transcription to infer patience and engagement. Same for relationship/politeness etc? Essentially channle and call stats can say something about who the person is not just their cost. Also the trouble with cost to serve is that sometimes the cost is not the customers fault. There is a need to distinguish between needy and expensive, desiring and valuing high service and high relationship and someone has a problem that takes time and effort, that they don't want to spend to solve it. This is the difference between good service and failure demand. The distinction is key."
- 09:06: "On that same line of thinking, looking at call causation and root cause is real value. Looking at advisor action by call type cluster is also really valuable. This is a great way to get NBA and coaching and training"
- 09:07: "Contacts are a great source, but under the surface is where the customer doesn't contact is just unhappy and leaves or there is a quiet fail"
- 15:13: "Log as an idea or backlog"

## The problem (the machine owns the design)

Today, from the advisor's quick search of origin on 17 Nov:

- cost to serve is a per-segment allowance, not built from contacts, so it cannot say whose fault a contact was;
- "failure demand" appears nowhere in the repo;
- `channel_pref` is drawn but read only by cohort discovery;
- the world has no contact model, so there is no abandonment, duration or reason for contact.

The ideas, as problems:

1. **Contact says who a person is, not only what they cost.** Hidden world traits such as patience, appetite for relationship and service, and how much a household minds spending its own time should shape how it contacts the supplier. The supplier infers them from what a real supplier holds: channel chosen, abandonment, duration, repeat contact, reason and transcript tone. These traits belong with the hidden weighted utility (time and certainty are already needs in it).
2. **Value demand versus failure demand (Seddon's distinction).** Contact the household wants (it values relationship, or advice it asked for) is not the same as a hard problem of its own, and neither is the same as contact the supplier caused (estimates, bill errors, broken promises). Failure demand is the supplier's failure cost. It must not count against the customer's lifetime value. Otherwise the optimiser learns to want rid of the customers it has wronged, which is the cap-pricing pattern built in quietly.
3. **Root cause.** Cluster contacts by cause, rank by frequency × cost to both sides, and fix the source rather than the calls. This links to the spec hypothesis that most holds, disputes and complaints fall into a few bulk-fixable root causes.
4. **Handling by contact cluster: next best action and coaching.** For each kind of contact, find which response resolved it first time, left the household better off by its own hidden weights, and brought no repeat contact. Where a handler, policy or script does worse than its peers on the same cluster, change it. Today that is the machine improving its own policies; if simulated staff are added later, the same reading becomes real coaching and training.
5. **Beneath the contacts: silent unhappiness and quiet fails.** Contacts are a biased sample. Some households never call. Their need stocks drain, and they leave or stop paying. Some errors go unreported: silent over- or under-charging, estimates that run on, a direct debit drifting out of line, a back-billing deadline passing. The world generates both as hidden truth. The supplier must find them without a contact (fewer logins, payment drift, DD cancelled or reduced, read gaps, scanning its own data for silent errors), and choose whether to act, mindful of waking sleeping dogs. Because the world knows the truth, Poesys can score what share of leavers and quiet fails the supplier saw coming, and how early. A real supplier can never measure that.

## Non-negotiables

- **Knowledge first (K8):**
  - published evidence on contact-centre failure demand and its share;
  - Ofgem and Ombudsman complaint-cause data;
  - silent-attrition evidence;
  - what can be inferred from call metadata and transcripts.

  Label the GAPs. Unpublished rates are stated beliefs with ranges.
- **The wall:** the supplier sees only contact records and its own data, never the cause, trait or stock.
- **A guardrail:** inferred traits are used to serve better, never to ration service. Long, difficult contact is also how vulnerability shows, so "expensive" never becomes a reason to steer someone out. This goes with the guardrails in yesterday's item 8.
- **Build on existing work, not parallel modules:** yesterday's need stocks (item 2), step-shaped cost to serve (item 6), and the existing conversation and contact-response modules.

## Risk

- **Touches:** knowledge pages and the backlog now. Later, a world contact model, cost-to-serve attribution, and CLV inputs.
- **Blast radius:** none this week. Logging only.
- **Probable failure mode:** a contact or failure-demand rate invented to fill a slot; or cost to serve re-attributed in a way that silently moves published margins.
- **Mitigation, inline:** knowledge first with GAPs labelled. Any change to cost-to-serve attribution is a serious class under the correctness rule and goes through the publish gate.

**Proportionality:** reversible and narrow: log it and rank it. Building it is feature work, ranked on Friday within the feature share.
