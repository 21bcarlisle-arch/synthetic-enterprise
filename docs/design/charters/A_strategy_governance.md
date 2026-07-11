# A — Strategy & Governance: lane charter

**Dial reached 2 2026-07-11** (SPIKE_WEEKEND charter flood, `docs/staging/in_progress/SPIKE_WEEKEND.md`
item 4) — DISCOVER/FRAME stage, documentation only, no code built this pass.

## Mission

The project's own retrospective/learn-loop mechanism (`docs/retrospectives/*.md`, driven by
CLAUDE.md's phase-close checklist rule 6, "Retro check") must mature from a crisis-triggered,
ad-hoc writeup habit into something closer to a real board strategy/risk committee's own
formalised review cadence — this lane's own `real_world_twin`
(`docs/design/maturity_map.yaml`, atom `A1_learn_loop_chair`).

## Sub-capability tree

- **A1 (this atom, `A1_learn_loop_chair`)** — the retrospective/learn-loop cadence itself: when a
  retro gets written, what it covers, and who (or what mechanism) reviews the accumulated log.
- Downstream, not yet its own atom: whether retro *action items* get tracked to closure (today
  a retro documents root cause and a fix; it does not carry a structured, later-checked
  outcome/owner/due-date the way a real corporate postmortem process does).
- Cross-lane note: this is a **process/governance** capability, not a SIM or company-observable
  one — it governs how the AGENT (this project's own builder) learns, not how the simulated
  company learns. No epistemic-wall interaction.

## What L2/L3/L4 mean in this lane's terms

- **L1 (pre-existing baseline):** ad hoc — a retro gets written only when a problem is bad
  enough to force one (five real retros exist: `2026-07-04-verification-week.md`,
  `2026-07-08-test-suite-tmux-leak.md`, `2026-07-08-wake-doorbell-third-strike.md`,
  `2026-07-09-doorbell-failure-4-supervisor.md`, `2026-07-09-doorbell-failure-5-busy-regex.md` —
  every one is incident-driven, none is a scheduled/periodic review).
- **L2 (current, `level_current: 2`):** a *named trigger condition* exists and is followed, even
  though execution so far has always been the crisis branch of it — CLAUDE.md's own rule 6:
  "if this phase closed a multi-day/multi-false-claim problem, **or ~50 phases/2 weeks have
  passed since the last retro**, or a harness rule changed — write a retro before closing." The
  periodic branch (50 phases/2 weeks) has never yet been the thing that actually fired one; this
  is the honest gap between "the rule exists" and "the rule's non-crisis branch has ever been
  exercised."
- **L3 (target for this atom):** retro *action items* become a structured, trackable list (owner
  = agent or director per item, a real due-date or "next phase touching X"), not prose buried in
  a markdown file that's never re-read. The periodic branch of rule 6 actually fires at least
  once on a schedule, not only after a crisis.
- **L4 (full governance maturity):** something functions as this project's own "risk committee" —
  a periodic (the FRC's real cadence below: annual) structured pass over the accumulated retro
  log, each entry's action items checked for closure, findings rolled into a director-facing
  summary — matching a real UK board's own Provision 29 declaration, adapted to this project's
  scale (this need not mean literally annual; it means *a defined periodic review exists and
  actually runs*, at whatever cadence this project's own pace warrants).

## Named best-practice references

(Independently sourced this pass via real web search — not invented, not carried over from any
existing project doc.)

- **Google SRE, "Postmortem Culture: Learning from Failure"**,
  https://sre.google/sre-book/postmortem-culture/ — the blameless-postmortem standard this
  project's own R9 (label every claim OBSERVED or INFERRED, root-cause not blame) already
  matches in spirit. Google's own postmortem artefact structure — summary, timeline, root-cause
  analysis, impact, and **corrective action items with owners and due dates** — is the concrete
  reference for this lane's L3 target: this project's retros already have the first four
  elements; owner/due-date tracked action items are the real, named gap.
- **Google SRE — the "postmortem reading club"** (same source): a recurring, scheduled forum
  where past incidents are re-read and discussed as a group — the closest real precedent for
  this lane's L4 "periodic review of the accumulated log," distinct from writing an individual
  retro at the time of the incident.
- **UK Financial Reporting Council, UK Corporate Governance Code 2024, Provision 29**,
  https://www.frc.org.uk/library/standards-codes-policy/corporate-governance/uk-corporate-governance-code/
  — requires a UK listed board to review the effectiveness of its risk-management and internal-
  controls framework **at least annually**, with a formal declaration of that review having
  happened. Real, cited, UK-specific, and the direct structural analogue for this lane's L4: a
  defined periodic cadence, not indefinite ad-hoc deferral, with an explicit record that the
  review actually took place.

## Lane roadmap

1. **This pass (DISCOVER/FRAME, documentation only):** this charter. No code touched, no new
   retro-tracking mechanism built.
2. **Next (not started):** decide the concrete trigger for exercising rule 6's periodic branch
   for real at least once — e.g. an explicit check at the next natural phase-close counting
   phases/days since `2026-07-09-doorbell-failure-5-busy-regex.md` (the most recent retro) —
   rather than waiting for the next crisis to force one.
3. **Later:** a structured action-item register (could be as simple as a markdown checklist per
   retro doc, or could reuse this session's own `background/action_needed.py` ledger pattern —
   built for a different purpose, director-facing waits, but structurally similar: item + owner +
   status) so a retro's fixes are checked for closure, not just written and left.
4. **L4:** a genuinely periodic (cadence TBD, director's call — this project moves far faster
   than an annual real-board cycle) pass over the whole retro log, explicitly modelled on the
   FRC Provision 29 pattern above: review effectiveness, declare it happened, roll findings to a
   director-facing summary.

## Simplifications register

- This lane has exactly one atom (`A1_learn_loop_chair`) in the current map — no sub-capability
  split exists yet because none has been needed; if the action-item-tracking idea above (roadmap
  item 3) becomes real work, it may earn its own atom rather than staying folded into A1.
- No automation exists to detect "50 phases/2 weeks have passed" — rule 6's periodic branch is
  currently a human-legible (agent-legible) judgement call at each phase close, not a mechanically
  checked condition. Not flagged as a defect: the crisis branch has always fired first in
  practice, so the periodic branch's own detection mechanism has never yet been load-bearing.
