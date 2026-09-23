**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, pre-registration

# Pre-registration: are the publish gate's four reds red AT HEAD, or red only in the shared tree?

**Claim:** `publish-the-withdrawal-the-belief-leg-did-not-survive`
**Written BEFORE the measurement was run.** Base: `c50ea7f0b` (== `origin/main` at draw time).

## The question

The drawn item states the publish gate "names four reds and has never graded them at HEAD", and
asks for the one-variable control: a clean extract of `HEAD`, the same door files, nothing else
different. Two answers are possible and they lead to different work:

- **red at HEAD** — the reds are a property of the trunk. They belong in the draw as work, and no
  amount of tidying the shared working tree clears the publisher.
- **red only in the shared tree** — the reds are caused by the shared tree's uncommitted state
  (which includes the three armed-revert inputs this same item names), and the publisher clears as
  soon as those are resolved.

## What I predict, and why

**I predict: GREEN at HEAD** — i.e. *red only in the shared tree*.

Reasoning, stated so it can be wrong for a named reason:

1. `SEAT_FINDING_THE_SITE_LANE_REFUSED_ON_TWO_DOORS_PINNED_TO_THE_SHAPE_THE_CHANGE_REMOVES_...
   _2026-09-22.md` records four site-lane reds, establishes their cause as two doors pinned to a
   shape the change removed, and records both fixes as mutation-proven and landed.
2. The publish gate's subject is documented in this repo as `HEAD`, but `process_run_complete`
   regenerates `site/data/value_arms.json` from the **working tree**. The three inputs that
   generator reads are stale in the shared tree (09-22 10:24 and 08-31 against later landings), so
   the feed the gate grades is built from superseded bytes there and from HEAD's bytes here.
3. That is exactly the class the 09-22 finding named: *a feed produced against a superseded tree*
   reds site doors that read provenance.

**The prediction is about the INSTRUMENT, not the world.** It says where the reds live, not whether
the code is correct. A GREEN-at-HEAD result does not license "the trunk is fine"; it localises the
cause to the shared tree's uncommitted state.

## The refutation condition, fixed in advance

- Any of the four named doors failing in a clean `HEAD` extract refutes the prediction outright.
- A different set of doors failing in the extract also refutes it: the prediction is that *these
  four* are tree-local, and a different four at HEAD means the finding I reasoned from was about a
  population the gate is no longer naming.
- An extract that cannot complete (box saturation) is **not** a result either way, and must be
  recorded as `cannot_tell` rather than as the flattering reading. The 09-22 finding above was
  written by an invocation whose whole-`site/` run never completed, and it wrote "only the landing
  is outstanding" while four doors were red.

## The instrument, named in advance

A `git clone --local` of the common git dir forced to `c50ea7f0b`, **not** `git archive` — an
archive extract has no `.git`, and that artefact alone produced six spurious failures on 09-22.
`pytest site/` over the whole tree, because the site lane runs the whole `site/` tree and a targeted
green is not a green lane.

## AMENDMENT, written BEFORE the measurement ran: I NAMED THE WRONG FOUR

**The population above is wrong and the reasoning behind the prediction is refuted, and neither is
refuted by the measurement — they are refuted by reading the instrument's own record, which I should
have done before writing the prediction.** Kept above verbatim rather than revised, because the
shape of the error is the finding.

`docs/observability/.publish_gate_state.json` on the shared tree names the four `blocking_tests`
outright, and they are **not site doors**:

    FAILED tests/background/test_publish_step_ledger.py::TestWiredIntoThePublishPath::test_the_publish_path_actually_uses_the_ledger
    FAILED tests/background/test_publish_step_ledger.py::TestWiredIntoThePublishPath::test_the_five_evidenced_failures_are_all_covered
    FAILED tests/background/test_the_site_publish_pipeline_is_contained.py::test_the_publish_pipeline_actually_calls_the_guard_first
    FAILED tests/tools/test_website_integrity_fix.py::test_the_gate_verdict_is_what_generate_dashboard_json_returns

Their declared `suspects.modules` are `background/publish_step_ledger.py`,
`background/process_run_complete.py`, `background/live_ledger_guard.py` and
`tools/generate_dashboard_data.py` — the publish PATH, not the published PAGE.

**What I did wrong.** I reached for the most recent staging finding whose title contained "four
reds", and it was about a different four, on a different claim, already fixed and landed. *Four* is
not an identifier. The instrument records the names; I predicted against a number.

**So the mechanism I predicted cannot be the mechanism.** The site doors read feed provenance, which
is why the stale-input story was available; none of these four reads `site/data/value_arms.json`
at all, so the three armed-revert inputs cannot be their cause either. **The whole causal chain in
the prediction above is dead regardless of what the extract returns.**

## The re-stated prediction, on the correct four, still before the run

The state file already says `red_at_head: "not_established"`, with the reason: *"the red was
measured at git=d533d9a93 and HEAD is now git=c50ea7f0b — that record describes a different commit's
tree, so it says nothing about HEAD."* That is the gap this measurement closes.

**I predict: RED at HEAD, all four.** Reasoning, and it is weaker than the reasoning above was:

- `fork_state: "level"` on the most recent record — the graded tree was LEVEL with `origin/main`,
  so the citation names the shared branch's red rather than a local divergence.
- `episode_failures: 26`, `episode_clean_publishes: 0`, `wedge_since` set — a wedge that has held
  across 26 failures and many commits is more consistent with a trunk property than with a
  transient working-tree state.
- The two commits between `d533d9a93` and `c50ea7f0b` (`205b01093`, `c50ea7f0b`) touch the staging
  census, not any of the four declared suspect modules.

**Refutation condition:** any of the four passing in a clean `HEAD` extract refutes it. A split
result (some red, some green) also refutes it as stated — the prediction is *all four*.

**This prediction is about the INSTRUMENT.** It says where the reds live. It does not say the four
tests are correct, and a RED-at-HEAD result does not establish that the production code is wrong
rather than the controls being pinned.

## Separately, and NOT a prediction

The feed regeneration in the same turn is **confirmatory, not a measurement**: `d533d9a93` already
landed the producer logic and its own commit message states the leg survives neither pooling nor a
second draw. Regenerating `site/data/value_arms.json` at HEAD re-derives a published answer from an
already-landed producer. It is recorded here so that it is not later counted as a second
independent confirmation of the withdrawal. It is one.
