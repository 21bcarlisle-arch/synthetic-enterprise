**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — census-the-promote-by-copy-class) · **Class:** controls_that_cannot_fail

# Pre-registration: which published sentences a promote-by-copy would falsify

**Written BEFORE the census tool has been run once.** The scope discovery below (which paths are
promote-by-copy targets) is already measured and is stated as fact; every numbered prediction is
about output that does not exist yet.

## The class being censused

`77d92e0d1` found three instances of ONE mechanism in ONE file, by reading it. The mechanism:

> A module reads an artefact from a path whose **bytes can be replaced by a newer run of the same
> shape**, and publishes a claim about **which run sits there** — a date, a stamp, a world digest,
> or an ordering ("later than", "beside the", "as it is now") — **stated as prose or a literal
> rather than derived from the artefact's own payload.**

A promote-by-copy moves BYTES. It changes no constant, no import and no source file: the producer's
`git diff` is empty while the page's meaning inverts. **Every control keyed to a constant is blind
to it by construction.** The question is not "does the constant point at the right file" — all three
instances passed that. It is: *if the bytes at this path were replaced by a newer run of the same
shape, would any sentence on the page become false?*

## Scope, measured (not predicted)

A path is a promote-by-copy target iff a **dated sibling of the same stem exists beside it** — that
is the mechanical signature of "the newest run gets copied onto this name". Across `docs/`, `site/`
and `data/` there are **four**, plus one by naming convention:

| target | dated siblings |
|---|---|
| `docs/observability/value_cycle_ab_s1_three_arm.json` | 7 |
| `docs/observability/value_cycle_ab_s1_noise_floor.json` | 6 |
| `docs/reports/run_output_latest.json` | 4 |
| `site/state/live_decisions_latest.json` | 40 |
| `site/state/scenario_analysis_latest.json` | (convention twin of the above) |

Nine other dated stems have **no** canonical twin, so they are not in the class: nothing is copied
onto them and no reader can be pinned to "whichever run is there".

## Predictions

Scored against `tools/promoted_artefact_claim_census.py`, which is written before it is run and
which is the census — no manual pass precedes it.

**P1 — the census finds MORE than the three known instances, and fewer than twenty.** I predict
**5–15 hits** in modules that read a promote target and carry a run-identity literal. Refuted if 3
or fewer (the class really is one file) or 20+ (the detector is matching the concept word, not the
mechanism).

**P2 — at least one hit is OUTSIDE `tools/generate_value_arms_data.py`.** The named candidate is
`tools/inference_claim.py`, which is the only other module in the tree binding a constant directly
to `value_cycle_ab_s1_three_arm.json` (`SKILL_ARTEFACT`, line 115). Refuted if every hit is in the
one file `77d92e0d1` already repaired — which would mean the class is an instance, and the census
was not worth building.

**P3 — the `run_output_latest.json` readers produce hits, and most of them are FALSE.** ~18 modules
bind that path. A generator naming a date beside it is usually naming the *simulation's* period
(2016–2025, a settlement date), not *which run file is there*. I predict the raw detector fires on
several of them and that **fewer than a third survive disposition**. This is the prediction most
likely to reveal the detector is aimed left.

**P4 — the surviving defects are DOCSTRING/COMMENT prose, not feed values.** `77d92e0d1` repaired
two published sentences and one docstring; the published side of `generate_value_arms_data` has now
been keyed to the property (`is_the_later_run` compares two stamps). So I predict the residue after
that repair is **prose-side**: a path in a comment is a reachability edge, and a docstring naming
which run satisfies a guard stops being true the moment the bytes move. Refuted if a **live feed
value** — a string that reaches `site/data/*.json` — is found still carrying a run-identity literal.

**P5 — WILL NOT MOVE: `site/data/value_arms.json` is unchanged by this turn.** No artefact is
promoted, no generator constant moves, and the census is read-only. This is the independence check:
the census must not be able to change the page it is measuring. If `value_arms.json` moves, the
turn contaminated its own subject. Independent by construction, not merely conceptually: the census
tool opens no file under `site/data/` for writing and imports no generator.

**P6 — the control that ships is keyed to the PROPERTY and reds on a real promotion.** Done means:
copying a dated sibling onto its canonical name, with no source edit at all, makes the new control
FAIL. A control that stays green through that is the same blindness in a new coat, and shipping it
would be worse than shipping nothing.

## What done means for this item

1. A census that discovers its targets from the tree (never a literal list of two filenames), so it
   keeps working when a fifth promote target appears.
2. Every hit dispositioned — real, or named as safe with the reason.
3. The real ones fixed.
4. A control that can fail, proven by a poison round: a run-identity literal added to a reader of a
   promote target must be caught, and removing the detector must break it.
