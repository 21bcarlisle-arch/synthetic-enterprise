# DIRECTOR AXES — what the director currently cares about most

**Version: 1** (2026-07-22). Established by `DIRECTOR_STEER_SELF_MEASUREMENT_AND_AXES_2026-07-22.md` §4.

**What this file is.** The small, versioned record of the axes the director judges the system on —
the judgment *only he can give*. It is the director's document: the agent may propose an axis or a
roadmap rotation with reasoning, but the *weights and the verdicts are his*, changed only by a
director-authored, versioned edit (same discipline as `DIRECTOR_CANON.md`). This file is READ by
reasoning entities (the morning retro, the twin's pre-score, the director) and is **never consumed by
any allocation, draw, reward, or scheduling mechanism** — HARD LAW §2 of the steer, inherited from
LAW A / R12: a scorecard number severed from all wiring. Bump the version on every director edit.

## The verdict loop (how a judgment enters)

1. On the director's cadence (weekly, or at a milestone), he gives a one-line score per axis, e.g.
   `site 2/5 — still can't follow the customer panel`. Console or NTFY.
2. Each verdict is recorded as data in `docs/observability/director_axis_verdicts.jsonl`
   (`{axis, score, note, ts, channel}`) — append-only, ledger-governed.
3. **Before each expected verdict, the twin pre-scores the same axes and logs its prediction** to the
   same ledger (`source: "twin_prediction"`) with a one-line rationale drawn ONLY from its canon +
   origin facts. The director's verdict then scores the twin's prediction. The shrinking prediction
   gap = the system internalising his taste. This is belief-vs-truth (the coupled-triad's own law)
   applied to the director himself. **Law B still binds:** the twin's prediction is logged and read;
   it NEVER updates the twin's canon, and the gap NEVER trains the twin. The gap is a diagnostic.

## v1 axes (director's current priorities)

### 1. Website
- **Usefulness to him as an operational window** — can he open the site and understand the state of
  the company without asking.
- **Simplicity / clarity as a marketing tool** — legible to someone who is not the builder.

### 2. Segmentation
- **Efficiency** — value per segment (cost-to-serve vs value; activity-based, per CLAUDE.md pricing law).
- **Sophistication** — real coupled structure, discoverable *through the wall* (ground truth behind
  the epistemic seam; the company starts from EPC/census priors and discovers via interaction).

### 3. Believability
- Weather, wholesale products and prices, premise demand shape: **does it feel like the real UK
  market to a 20-year veteran.** The 20-year-veteran smell test is the acceptance bar.

## Roadmap (encoded here, director-owned rotation)

Once the three above stabilise:
- → **Billing + CRM** rotate in.
- → then **advice + product journeys**.

Rotation is a director act (a versioned edit here), not an agent decision. The agent may *propose* a
rotation when it has evidence an axis has stabilised, but does not move the roadmap itself.

## Verdict + prediction history

_(none yet — v1 just established; first twin pre-score to be logged before the first director verdict)_
