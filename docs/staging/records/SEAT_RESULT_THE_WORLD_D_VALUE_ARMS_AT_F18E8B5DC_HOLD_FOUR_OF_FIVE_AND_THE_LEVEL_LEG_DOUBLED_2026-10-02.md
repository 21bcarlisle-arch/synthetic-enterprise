**Severity:** RECORD · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The world-D value arms at `f18e8b5dc`: four of five predictions held, and the level leg doubled

**Claim:** `land-the-world-d-value-arms-retaken-at-f18e8b5dc`. This grades
`SEAT_PREREG_THE_WORLD_D_VALUE_ARMS_RETAKEN_AT_HEAD_0BAC2B8BE_2026-10-02.md` as amended by
`SEAT_PREREG_ADDENDUM_THE_WORLD_D_VALUE_ARMS_RETAKEN_AT_F18E8B5DC_2026-10-02.md`. Both are in this
directory.

## The run

The unit `longjob-arms-floor-d-head-1002b` exited 0 (`Result=success`). It produced
`value_cycle_ab_s1_three_arm_20261002b.json` at 06:56 BST and `value_cycle_ab_s1_noise_floor_20261002b.json`
at 09:44 BST. Both artefacts carry `producing_commit` `f18e8b5dc6a6…` and `world_identity.digest`
`cf823b185f8ca51c`. `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` moved onto
the two artefacts in the same commit.

## Grades

| | Prediction | 10-01 (`0407ce0e3` + PB4) | 10-02b (`f18e8b5dc`) | Grade |
|---|---|---|---|---|
| P0 | the world digest stays `cf823b185f8ca51c` | — | `cf823b185f8ca51c` | **held** |
| P1 | the whole advantage is positive | +£7,708 | **+£14,856** | **held** |
| P2 | the level leg is positive in the three-arm run and on all 3 floor seeds | +£8,967; floor £8,548 / £9,796 / £12,098 | **+£15,115**; floor £14,607 / £12,400 / £19,728 | **held** |
| P3 | P1 and P2 both come out *smaller* | — | both roughly **doubled** | **refuted** |
| P4 | selection falls on one side of zero on all 3 seeds, and that side is negative | −£1,259 | −£259 in the run; seeds −£404 / −£1,314 / −£7,542 | **held** |

Control net is £85,910, the value arm £100,766 and the level arm £101,025. On every seed the level
share of the advantage is above 1 (mean 1.26). So the whole advantage is the price level, which is
value *moved*. Per-customer choosing adds nothing and, if anything, costs a little. At n=3 the
selection leg is still not distinguishable from zero, and the page states no direction for it.

**P3 is refuted, and the refutation cannot be attributed.** P3 was held weakly in the
pre-registration and weaker still in the addendum. Between the two trees, every one of these
commits applies to all three arms: the foresight fix `cd0c7c39c`, the 2025 standing charge `6f5bb8b68`, the DD opening
`5803d08c3`, ToU against the multi-register cap `8c29e03d9`, the SVT segment at the cap
`592596b44`, a chosen fixed renewal outside the cap `9cfb1817f`, and the rest of the
`0bac2b8be..f18e8b5dc` path moves. The mechanism P3 named ("a binding cap clips the arm that
prices higher") lost to something bigger. The one candidate already measured in the same direction
is the foresight fix, which raised one default world's book margin by £7,331. That is a candidate,
not an attribution. Attributing it would take one commit at a time, and nothing here depends on
the answer.

## What the page says after the move: measured, not current

When the page was regenerated at origin/main `d67aaaf5d`, `is_heads_code` read **False**, and the
level and selection verdicts were withdrawn (`resolved: null`). The figures and the seed family
still stand. Four `simulation/`/`company/` paths moved after `f18e8b5dc`:

- `company/interfaces/growth_desk.py` and `simulation/run_phase2b.py` (`28eb35ec7`): the
  acquisition no-offer rule now prices both fuels, ex-VAT, against the default. That changes which
  prospects are quoted on the replacement path, and so it changes the settled book in all three
  arms. **This cannot be argued.** The addendum's rule applies: a path whose change reaches the
  settled book is re-run.
- `simulation/customer_events.py` and `simulation/run_phase2b.py` (`2cfea34b7`): the
  decline-and-stay splice, switched off, and byte-identical on a 2016–2018 smoke.
- `simulation/fabric_demand_path.py` (`09555ee17`): it reuses fabric traces across forced
  home-move legs.

The second and third could be exempted. No exemption was written, because `28eb35ec7` withdraws
the run either way. An argued exemption does not change what the page says, so it would be a
control with nothing to do.

## What this lands, and what is still owed

**Landed:** the current-world block now reads the `f18e8b5dc` pair. The page no longer reads the
`0407ce0e3` pair, which ran the renewal foresight leak and the SVT segment above the cap. The
withdrawal reason now names four paths, one cause that cannot be argued, instead of sixteen. The
grades above stand whatever the page shows, because they grade the run against its own
pre-registration.

**Owed:** a retake at a HEAD containing `28eb35ec7`, before the 10-05 publish if this page is to
carry a current-world verdict. **It was not launched in this turn, on purpose.** The box is
running `longjob-depth-vs-width-20261002`, which leaves 12.6 GB available. The arms alone peaked
at 8 G + 1 G swap and were OOM-killed once at `0bac2b8be`. The decline-and-stay lane also says its
paired runs wait "once the box is free". If that lane switches `DECLINE_A_FIX_ABOVE_THE_DEFAULT`
on, the world moves again and a retake started now is spent. So the retake goes after that switch
is decided, or the page publishes on 10-05 with the reading withdrawn, as it already does by
mechanism. A withdrawn reading is the fail-closed state, not a wrong one.

## Two things the move surfaced, fixed in the same commit

- **The front door's selection sentence was false at HEAD.** It said "re-drawn nine times … lands
  on both sides of zero" and pointed at "the nine-draw band". The live family is n=3 (since the
  10-01 move), and all three re-draws are now negative. `_check_front_door_selection_draw_count`
  had been red at origin/main `d67aaaf5d` for that reason. `site/index.html` now says three draws,
  every household drawn afresh, below zero on all three, too few to call a sign. The verdict stays
  `withheld`.
- **`site/test_the_baseline_comparison_reaches_the_reader.py` had no branch for a run withdrawn
  for its code.** At HEAD the old run never reached that state, because it left first as "not the
  later run". It now asserts that the headline is silent and that the feed says why. Mutation: when
  the generator's `is_heads_code` silence is removed, the rung goes red, naming the four paths.
