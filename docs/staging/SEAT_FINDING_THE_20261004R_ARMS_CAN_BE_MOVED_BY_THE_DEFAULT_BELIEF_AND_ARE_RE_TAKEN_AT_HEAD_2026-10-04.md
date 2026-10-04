# The 20261004r arms can be moved by the default-belief change, so they are re-taken at HEAD, and the code check now sees the whole run

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-20261004r-arms-are-not-heads-code-seven-paths-moved` (Lane 0 delivery)

**2026-10-04.** Premise re-measured at origin `efe1b7dee`: the seven `simulation/`/`company/` paths
still differ from `96517e68c` with no exemption. The premise is not spent.

## Path by path: can it move the arms?

| path | verdict | why |
|---|---|---|
| `company/pricing/default_belief.py` | **CAN** | `renewal_default_belief` defaults to `own_book` at BOTH commits (`company/policy/decision_policy.py:166`), so `run_phase2b` asks `LivePaymentTriad.default_belief_rate` at every priced resi renewal. The change drops account-years whose method register answers `None`. Its own docstring says the run's SME accounts C5 and C6 used to enter the belief this way, one of them carrying a GBP 75 final-bill charge. A different learned rate is a different bad-debt cost in `decide_margin`. |
| `background/live_payment_triad.py` | **CAN** (and the check could not see it) | Lump settlements are now held until the account's collections journey has been walked, and they cross before `advance_collections_journey` in `record_period`. Before, they crossed only when a reader asked. So the journey now sees cash it used to miss. |
| `company/billing/collections_journey.py`, `payment_observation_consumer.py`, `payment_plan.py`, `company/interfaces/sim_interface.py`, `simulation/plan_offer_response.py` | inert while `PUBLISHED_BASIS` has gaps | Every plan offer is answered `accepted=None`. No plan goes ACTIVE, `_read_instalments` never reaches the seam, `HouseholdPlanBook` stays empty, and `repays_through_plan` is always False. The only difference is the text of the `acceptance_gap` reason. |
| `simulation/run_phase2b.py` | inert | It adds one summary key (`later_settlements`), a read-only sum taken after `total_net`. |
| `tools/book_seed_authorisation.py` | not argued | The widened check (below) named it. It is imported by the run and moved. |

One path that can move the arms is enough. An exemption argued for the rest would buy nothing:
after a re-take at HEAD, `_code_since_the_run` diffs HEAD against HEAD. So none was written.

## Re-take, in flight

`longjob-heads-arms-retake` was launched at 13:05Z in the locked worktree `/var/tmp/se-heads-arms`
(origin `efe1b7dee`), running `/var/tmp/se-heads-arms-handoff.sh`, with a declared peak of 11,200 MB:

1. `--level-arm --out docs/observability/value_cycle_ab_s1_three_arm_20261004h.json` (about 70 min).
2. Only if leg 1's artefact parses and is not a refusal:
   `--noise-floor-seeds 11111,22222,33333 --redraw-mode all --out
   docs/observability/value_cycle_ab_s1_noise_floor_20261004h.json` (about 3h20). A
   `floor_run_refused` artefact is deleted and retried every 5 min, at most 48 times.

The log ends `END both legs DONE` or `STOP <why>`: `/var/tmp/longjob-heads-arms-retake.log`.
Expected end is about 17:40Z. Re-ask with `python3 -m background.launch_liveness --check`.

**Prediction, written before the result:** the world digest stays `cdba75ebb9197b33`, since no
departure-level path moved. The value advantage moves by less than the 3-re-draw spread
(24.1k..27.5k). I have not established the direction of the default-belief change in the run, so
I make no claim about the sign of the move.

**When both artefacts exist:** copy them into an origin worktree. Move `CURRENT_WORLD_THREE_ARM_PATH`
and `CURRENT_WORLD_NOISE_FLOOR_PATH` onto the `20261004h` pair. Regenerate `site/data/value_arms.json`.
Re-key any value-arms reds that pinned the `20261004r` answer. If origin has moved substrate paths
past `efe1b7dee` by then, argue those paths in the exemptions file.

## The code check could not see the whole run (fixed in this commit)

`ARMS_SUBSTRATE_PATHS` was `("simulation", "company")`. The run also imports `saas/`, `sim/`,
`interface/`, eleven `background/` modules and eighteen `tools/` files besides the runner, measured by importing
`simulation.run_phase2b` and `tools.run_value_cycle_ab` and listing the repo modules loaded. The
triad, which holds the company's payment consumer and the world's settlement queue, moved unseen.
The substrate is now that import closure, with the runner still named as excluded.
`test_the_arms_substrate_covers_every_module_the_run_imports` keys the list to the closure, not to
today's answer. Mutation: dropping `background/live_payment_triad.py` reds it, naming the file. The
page now names 9 unexempted paths, not 7.

**Limit:** imports deferred inside functions are not seen by the probe. The directory entries cover
those in `simulation/`, `company/`, `saas/`, `sim/` and `interface/`, but not in `background/` or `tools/`.
