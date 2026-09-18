**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# Pre-registration: what retracting the arms producer's stamp pair moves on the promoted-artefact census

**Filed:** 2026-09-18 · **Claim id:** `the-arms-producer-asserts-a-promoted-run-stamp-that-a-repromotion-has-already-falsified`
**Subject:** `tools/generate_value_arms_data.py`, the comment block opening at `:230`
**Instrument:** `python3 -m tools.promoted_artefact_claim_census --check`

---

## The state before the change, measured not assumed

    CLAIMS ABOUT WHICH RUN IS THERE  23   ordering-only 12   STALE 2   retractions 3
      STALE tools/generate_value_arms_data.py:230 token='2026-09-17T15:14:19Z'  vs …_three_arm.json
      STALE tools/generate_value_arms_data.py:230 token='2026-09-10T14:04:08Z'  vs …_three_arm.json
    REFUSED: a sentence keyed to which run sits at a promoted path is false as the tree stands.

Both tokens sit in ONE sentence, which is what `c2fe4469a`'s joined comment-block unit exposed:

> *"Both floors and `THREE_ARM_PATH` carry world digest `39a192ce04c1eda8`, so the bound is over the
> right world before and after, and the folded family is stamped 2026-09-17T15:14:19Z against the
> arms' 2026-09-10T14:04:08Z, so `_staleness_caveat` is satisfied rather than bypassed."*

Three facts about that sentence, each measured on this tree:

| the sentence's claim | what the tree says |
|---|---|
| the floor is the folded family, stamped `2026-09-17T15:14:19Z` | `NOISE_FLOOR_PATH` → `…_folded18_single_arm_20260917.json`, **`2026-09-17T21:39:28Z`** — moved by `5ce5c3c31`, later the SAME DAY, in a paragraph further down this same block |
| the arms read `2026-09-10T14:04:08Z` | `THREE_ARM_PATH` → **`2026-09-18T05:43:40Z`** — promoted by `756a86272` |
| `_staleness_caveat` is **satisfied** | it **FIRES** (measured below) |

## The prediction I am least sure of, and it is not the census

I already know the census verdict follows mechanically from the two regexes, so that is not the
interesting half. The one I did NOT know the answer to before running it is the third row. I
predicted from string ordering alone that `2026-09-17T21:39:28Z < 2026-09-18T05:43:40Z` puts the
floor BEHIND the arms and fires the guard. Run before writing this file, and recorded here with its
own answer beside it because a prediction filed after the answer is not a prediction:

    _staleness_caveat(NOISE_FLOOR_PATH, THREE_ARM_PATH)
      → "THE ERROR BAR IS OLDER THAN THE FIGURE IT BOUNDS. The seed spread was measured on the run
         of 2026-09-17T21:39:28Z and the point estimate on the run of 2026-09-18T05:43:40Z. …
         re-running the noise floor on the run published above is owed work."

**Confirmed, and it makes this a bigger finding than the item drew.** The sentence is not merely
carrying two stale literals — its CONCLUSION has inverted. A reader of this block today is told the
page carries no staleness caveat. The page carries one, and it asks for a re-run.

## What I predict the repair moves, written before the repair

The repair turns the superseded clause into the census's graded correction grammar (a saying-verb
plus a stated closure, in one sentence with the token), and states the live position with **no
literal stamp at all** — the ordering is `_staleness_caveat`'s to answer from the two payloads.

| | predicted before |
|---|---|
| `STALE` count | **2 → 0** |
| `--check` exit code | **1 → 0** |
| `RECORDED CORRECTIONS` | **3 → 7** (two retracted literals + their two `until` closure tokens) |
| `false_retractions` | **0 → 0** — neither retracted literal matches the run at `THREE_ARM_PATH` (`2026-09-18T05:43:40Z`), nor the run at `…_noise_floor.json` (`2026-09-10T23:03:18Z`), so naming `NOISE_FLOOR_PATH` in the correction is safe |
| `site/data/value_arms.json` | **byte-identical** — this is a comment, and `_staleness_caveat` already derived its answer from the payloads before and after |

**The last row is the one that can refute me.** If the feed moves, the comment was load-bearing on
something and I have mis-described the change as documentation.

## What this repair deliberately does NOT do

`republish-the-arms-decomposition-over-one-priced-book` holds
`docs/observability/value_cycle_ab_s1_three_arm.json` and `site/data/value_arms.json`. The floor
re-run that `_staleness_caveat` now asks for is that lane's, not this one's. Rewriting another
lane's in-flight artefact to clear a red is how a repair destroys an attribution. This turn touches
one file: the producer's comment.
