**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-value-arms-world-stamp-names-the-code-it-ran` (Lane 0 delivery)

# The current-world arms now check which code they ran, and the 10-01 run is not HEAD's

## Premise, re-measured at draw time

The premise was not spent. `0407ce0e3` and `592596b44` are both on origin/main. Neither of them,
and nothing after them, made `tools/generate_value_arms_data.py` compare a run's code with HEAD.
The page admitted a run as "the world as it is now" on `world_identity.digest` alone. That digest
covers the departure level and nothing else.

The draw's duplicate-work note pointed at this same id in `.seat_work_in_hand.json`. That entry was
written by the draw itself. It was not a rival claim.

## What changed

- `_code_since_the_run(run, head)` lists the `simulation/` and `company/` paths that differ between
  `producing_commit.commit` and the publishing HEAD (`git diff --name-only`). It refuses when the
  run names no commit, when HEAD cannot be read, or when git cannot diff the pair.
- A moved path is admitted only if `docs/design/value_arms_substrate_exemptions.json` has an entry
  that matches on all three keys: the run's commit, the path, and the path's blob at HEAD. So an
  argument about one change cannot admit the next edit to the same file. The file has no entries
  yet.
- `build` attaches the result as `current_world.code_since_the_run` and `current_world.is_heads_code`.
  When the code has moved, `_current_world_clause` composes nothing, so the headline drops its "IN
  THE WORLD AS IT IS NOW" sentence. The reason goes into `why_the_headline_omits_it`, with the paths
  named.
  - **Design decision:** the measurement stays on the page and only the claim that it is current is
    withdrawn. This is the same cut the run-ordering guard makes in `_current_world_contrast`.
    Withdrawing the whole block would also take off the legs and the composition, which were
    honestly measured and still show their own commit.

## Measured

- At `592596b44`, the 10-01 world-D artefact (`value_cycle_ab_s1_three_arm_20261001.json`, run at
  `0407ce0e3`) is refused. 15 paths differ, including `company/pricing/renewal_rate_chain.py` and
  `simulation/policy_costs.py`.
- At today's HEAD `526f6432f`, 15 paths differ.
- A full build into a scratch path differs from the committed feed in `current_world`, `headline`
  and commit stamps only. The headline loses the sentences "£7,708 … CLEARS the £1,697" and "-£1,259
  … STATES NO VERDICT".

## Controls (tests/tools/test_generate_value_arms_data.py)

1. `test_a_current_world_run_from_older_code_is_refused_though_its_world_digest_matches` checks the
   refusal. It drives one contrast block twice: unrefused it composes a clause, and refused it is
   silent.
2. `test_the_code_guard_admits_heads_code_and_an_argued_exemption_and_refuses_the_rest` covers the
   partition. Both admitting branches are reachable: the same artefact stamped with HEAD's commit,
   and the original commit with every path exempted. Both refusing branches are reached as well: an
   exemption keyed to the wrong blob, and an artefact with no commit.
3. `test_the_published_current_world_block_carries_the_code_its_run_executed` checks the wiring: it
   asserts that `build` reaches the guard.

Mutations, every one of which reds at least one control:

- forcing `refused` to False
- forcing `refused` to True
- dropping the blob key from the exemption match
- deleting the clause's silence line
- forcing `is_heads_code` to True
- diffing the wrong directory
- admitting a run with no commit
- removing the call in `build`

That last mutation survived the first two controls. Control 3 was written for it.

Three existing fixtures build "a feed whose current-world block speaks", and they now pass
`publishing_head=` the run's own commit (a new keyword-only argument). The fixtures are in
`site/test_the_baseline_comparison_reaches_the_reader.py`, the creation-leg rung, and
`_ALSO_ADMIT` in the undriven-pointers file. They test headline composition, not whether the code
is current. 678 passed across the generator, pointer and value-arms site files.

## Not done

- **"Item one's artefact is accepted" could not be shown on a real retake.** No such retake exists.
  The pre-registered world-D retake at `0bac2b8be`
  (`SEAT_PREREG_THE_WORLD_D_VALUE_ARMS_RETAKEN_AT_HEAD_0BAC2B8BE_2026-10-02.md`) wrote only a refused
  floor stub (11,200 MB needed, 8,277 MB offered, 00:41Z). There is no
  `value_cycle_ab_s1_three_arm_20261002.json`, and no runner is alive. The admitting branch is
  proved instead on the 10-01 artefact stamped with HEAD's commit. Until a retake lands, every
  publish withholds the current-world headline. That is the honest state. The pre-registration
  already said this reading comes off the page if the retake is not in by 10-05.
- **The feed is not regenerated in this commit.** The publisher's next build carries the change.
- **The current-world noise floor is not code-checked.** It bounds the figure, and it has the same
  exposure. This is the next step if the class is to be closed fully.
- **A run's stamp records a commit, not a dirty tree.** The 10-01 run was `0407ce0e3` plus the
  uncommitted PB4 patch. The path diff sees that patch only because it has since landed.
- **The guard is deliberately over-sensitive.** A docstring edit refuses as surely as a pricing
  change. Moving `simulation/` or `company/` after a retake will withdraw the headline again unless
  each moved path is argued in the exemption file.
