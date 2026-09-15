**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is a harness/provenance state, not domain understanding.

# Pre-registration: what the 20260910 pair move changes, and which pair the bounds come from

**Written BEFORE the measurement below was run, and before the floor it concerns exists.** The
floor run `longjob-noise-floor-20260910` (PID 1072649, started 2026-09-10T14:50Z, nine seeds,
`--redraw-mode all`) is ~5h from finishing at the time of writing, so nothing here can be fitted to
its answer.

Filed against the Lane 0 item *"pair-move the 20260910 run and its floor so the independent grading
reaches the page"*.

---

## The two questions

`tools/generate_value_arms_data.py` opens **four** artefact constants, not two:

| constant | resolves to |
|---|---|
| `THREE_ARM_PATH` | `value_cycle_ab_s1_three_arm.json` |
| `NOISE_FLOOR_PATH` | `value_cycle_ab_s1_noise_floor.json` |
| `CURRENT_WORLD_THREE_ARM_PATH` | `value_cycle_ab_s1_three_arm_20260908.json` |
| `CURRENT_WORLD_NOISE_FLOOR_PATH` | `value_cycle_ab_s1_noise_floor_20260909b.json` |

The drawn item moves the **canonical** pair only (the first two), and calls the whole thing "a pure
DATA move with no code change". The `CURRENT_WORLD_*` constants name dated files, so moving *them*
is a code change, not a copy.

**Q1. Is `contrast_bounds` built from the canonical pair or the `CURRENT_WORLD_*` pair?**

**Q2. Does moving the canonical pair alone restore the bounds the item exists to restore?**

## What I predict, before looking

1. **`contrast_bounds` is built from the `CURRENT_WORLD_*` pair, not the canonical pair.** The
   reason to expect it: `_floor_tree_pairing` is called twice, and the call at line 7662 that feeds
   `bound_tree_pairing` passes `floor_current`/`current` — the current-world artefacts — while the
   canonical-pair call at line 1317 feeds a different block. Confidence: moderate. I have read the
   call sites, not the bounds builder.
2. **If (1) holds, the canonical pair move does not by itself repopulate `contrast_bounds`**, and
   the item's stated mechanism ("`staleness_caveat` fires and `contrast_bounds` — which gates every
   directional claim on the page — empties out") describes a coupling I have not yet located.
   Something did refuse the run-alone promotion; I predict the refusal is real but that at least one
   of the four controls is keyed to the canonical pair and not to the bounds.
3. **`floor_tree_pairing.same_tree` stays `False` after the pair move**, exactly as it is on the
   live page today. Measured already and not a prediction: the live pair renders `same_tree=False`
   (floor `c066c114b`, figure `8b846013e`). The moved pair will render `same_tree=False` with
   different hashes (floor `4e7938f67`, figure `9cf9d16ed`). **This is not a regression the move
   introduces.**
4. **`staleness_caveat` goes from FIRING to `None`** once the new floor lands, because the floor
   will be stamped ~2026-09-10T19:5xZ against a point estimate of `2026-09-10T14:04:08Z`. This is
   the one thing the move unambiguously buys.
5. **`contrast_bounds` count does not fall.** It is a dict of 7 keys on the live page. I predict 7
   again after the move, not more — the item's "10 bounds lost, 3 gained" trade from 2026-09-09 was
   about a different pairing.

## What would refute each

- (1)/(2): building the payload with the canonical pair swapped and observing `contrast_bounds`
  change. If it changes, the bounds *are* canonical-pair-driven and prediction 1 is wrong.
- (3): a `same_tree=True` on the moved pair. Only possible if the floor's `producing_commit` equals
  the run's, which it cannot — the floor worktree is pinned to `4e7938f67` and the run was drawn at
  `9cf9d16ed`.
- (5): any count other than 7.

## The provenance probe, and its limit

To test (4) before the floor exists I restamp the **real** 09-09 floor's `generated_at` and
`producing_commit` and leave its seed rows untouched. That probes the provenance branches
`_staleness_caveat` and `_floor_tree_pairing` actually read — the cut-down-to-what-it-looks-at shape
`_pair_for_staleness` already uses in `tests/tools/test_generate_value_arms_data.py`. **It says
nothing about the numbers the real floor will carry, and no figure from it may be published.**

---

## RESULT, run 2026-09-10T15:2xZ — predictions 1 and 2 are REFUTED

Measured by calling `generate_value_arms_data.build()` in memory on three pairings. Nothing was
written to `site/data/value_arms.json`.

| | A. status quo | B. run alone | C. pair move (probe) |
|---|---|---|---|
| `contrast_bounds` shape | 7 keys | **3 keys** (`available`/`reason`/`what_this_costs`) | 7 keys |
| `contrasts` | 3 | — refused — | 3 |
| `staleness_caveat` | `None` | **FIRES** | `None` |
| `floor_tree_pairing.same_tree` | `False` | `False` | `False` |
| `is_it_available_today` | `false` | `false` | **`true`** |

**Prediction 1 — REFUTED.** `contrast_bounds` is built from the **canonical** pair
(`THREE_ARM_PATH`/`NOISE_FLOOR_PATH`), not the `CURRENT_WORLD_*` pair. Swapping the canonical pair
alone changed it (A≠B). I reasoned from two call sites of `_floor_tree_pairing` and generalised from
the wrong one; the `CURRENT_WORLD_*` pair feeds `bound_tree_pairing`, a different block.

**Prediction 2 — REFUTED, and it follows from 1.** The canonical pair move *does* restore the
bounds. **The drawn item's stated mechanism was right and my reading of it was wrong.**

**Prediction 3 — CONFIRMED.** `same_tree` is `False` in all three columns, including the live page.

**Prediction 4 — CONFIRMED.** `staleness_caveat` clears. Under B the page states the refusal's price
in its own words: *"no contrast on this page can have its direction stated until the noise floor is
re-run on the book published above"*.

**Prediction 5 — WRONGLY FRAMED, not merely wrong.** I predicted a *count* of 7 and 7 is the number
of dict KEYS, not of bounds. The bound count is `len(contrasts)` = 3, and the refusal is a **shape
change** (7 keys → 3), not a count falling. *This is the "say what it is before you measure it"
rule, and I broke it in the pre-registration itself.*

**A≠C on numbers is NOT established.** `contrasts` came out byte-identical in A and C only because
the probe reuses the 09-09 floor's seed rows. The real floor will carry different rows and different
widths. The probe establishes the provenance branches and nothing else, exactly as scoped above.
