**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] For the 11 Nov reader review: calibrate the selector on our own history, and say what each commit gate has caught (2026-11-05)

**Type:** STEER, through the advisor channel. It feeds the two-reader review's two-week review, due 2026-11-11. The director's words, from chat on Thu 5 Nov:

- 05:10 GMT, sharing Stephen Mc Gowan's "Review Gates for Code You Didn't Write" (https://smcgowan.me/posts/review-gates-for-code-you-didnt-write/) and Anthropic's AI-Native SDLC Playbook: "Anything additional and useful for us in here."
- 05:12 GMT, on the advisor's recommendation to calibrate the reader selector and review what each gate catches: "Stage it"

## Where it comes from

Mc Gowan reports six months of machine review across 336 agent-written changes. His caveats: must-fix is the reviewer's judgement, not a confirmed defect, and the smallest bands are tiny.
- **Size was the strongest predictor of a must-fix finding.** Under 150 lines: 29%. 150–499 lines: 24%. 500–1,499 lines: 53%. 1,500 lines and over: 68%.
- **"Sensitive" paths predicted nothing:** 40% against 41%.
- **Small was not safe:** 7 of the 24 smallest changes still had one.
- **"A borrowed model will be wrong in ways you can't see":** calibrate on your own rework, reverts and incidents.
- **Gates "only grow".** One of his matched too broadly, and agents waited about 108 hours for him. His remedies: gate on what a change does rather than where it lives, hold scheduled reviews of what each gate actually caught, and record every skipped review so it can be audited.

Ours: the two readers select only new modules and re-implementations (1.3% of commits, and the re-implementation selector does not exist yet). Every commit passes about 21 pre-commit gates, and nothing reviews whether each one earns its place. The 29 Jul mothball audit still has no trigger. `tools/commit_refusal_attribution.py` already attributes every refusal to the gate that made it.

## 1. Calibrate the readers' selector on our own history

At the 11 Nov review, alongside the confirmed-findings rate, answer from our own record:
- **Does commit size predict a confirmed defect here?** Use the defects found since June that can be traced to an introducing commit: the class documents, the head-red and standing-red registers, and the trial's labelled set.
- **Does any other observable predict it?** For example: a new module, a second implementation, touching `company/`, or a long gap since the file was last touched. Say which predict, and which do not.
- **Recommend the selector the evidence supports:** keep it, widen it to large commits, or something else. Give the expected share of commits it would select and the reading cost.
- **Skipped commits are visible.** Count them, and give the reason each was not selected, so a missed defect can be traced back to the selection rule.

Classify a commit from its diff, never from its message.

## 2. Say what each commit gate has caught

Use the refusal attribution that already exists. For each pre-commit and commit-msg gate, give over the last three months:
- **refusals,** and how many were real defects rather than noise or a gate's own fault;
- **when it last caught something real;**
- **its time cost per commit.**

A gate that has caught nothing real in three months is either dead, which is the naive organ's shape, or redundant with another gate. Say which, with evidence. Propose retiring or merging any that earn nothing. A retirement of a gate goes to `for_the_director` with your recommendation, because removing a control is the one direction this harness has never practised.

This answers part of the open mothball-audit trigger. If it should become the standing trigger for that audit, say so.

## Not wanted

- No new gate.
- No change to any gate in this turn, beyond what the review recommends and he approves.

## Risk

Touches: the reader selector and a read of existing refusal records. No gate changes.
Blast radius: none until a recommendation is acted on.
Probable failure mode: dividing two counts with different populations, for example refusals per publish cycle against commits. Say what each number counts.
Proportionality: reversible and narrow — just do it.

— Director steer, 5 Nov 2026, his words above; the reading of both sources and the drafting are the advisor's.

## Done (delivery seat, 2026-11-07 21:10 GMT): the signed text was read, restored and tracked; the work itself is not done

- **Why it moved here.** The advisor channel refused this file because d3b0b0f15 added an unsigned seat section.
  The executor's draw said to act on the signed text (0d575337d) and to move the file here with the reason once
  it was seen. The bytes above are 0d575337d's, restored exactly. The seat's section is now
  `docs/staging/records/SEAT_READING_THE_REFUSAL_RECORDS_COVER_ONLY_THE_PUBLISHERS_CYCLES_FOR_THE_11_NOV_GATE_REVIEW_2026-11-07.md`.
- **What is NOT done.** Both items, the selector calibration and the per-gate catch count, are still owed. They are due
  at the 11 Nov review. The 18:22 stretch-log entry carries them as focus item 5, ahead of the ninth cold read.
  Moving this file does not discharge them.
