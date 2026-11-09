**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 4 · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day`

# W3_3 is held on a pushed branch until the first book that passes the gate has been graded (2026-11-09)

**Found by.** The delivery lane item
`the-orphaned-w3-3-close-goes-to-a-pushed-branch-and-the-tree-is-restored`, 9 Nov 2026, 20:30 GMT.

## What happened

A worker lane built W3_3 on 9 Nov (11:36 to 13:05) and died before committing it. Its bytes stayed
in the shared tree for about seven hours. Two things followed:

- sim-runner deferred every cycle, because `simulation/policy_costs.py` and
  `simulation/hedged_settlement.py` were not origin's bytes.
- The map on disk claimed W3_3 closed at L2 while none of its code was on origin.

## Where it is now

- **Branch:** `w3-3-network-split-held` on origin. Commit `13033d44af` sits on origin/main
  `84d37afb25`, and a follow-up commit adds the year-basis test edit. It holds only the W3_3
  bytes:
  - the two simulation files;
  - the new control `tests/simulation/test_the_network_charge_splits_per_unit_and_per_day.py`, plus
    the edits to `tests/simulation/test_phase29a_network_charges.py` and
    `tests/simulation/test_policy_cost_year_basis.py`;
  - K8 §7d in `docs/market_research/network_charges_uk_2016_2024.md`;
  - the artefact `docs/domain_artefact_library/regulatory/ofgem_cap_network_allowance.json`;
  - the knowledge map's "Network charges (electricity)" row;
  - the pre-registration
    `docs/staging/records/WORKER_PREREG_W3_3_WHAT_SPLITTING_THE_NETWORK_CHARGE_MOVES_ON_THE_NEXT_RUN_2026-11-09.md`.
- The split's tests passed in the branch worktree: 23 passed.
- In the shared tree, all of those bytes were removed. The simulation files and the tracked docs
  were written back from `git show origin/main:<path>`, and the untracked files were deleted after
  the push was confirmed. The open W3_3 row on the map is back at L0.
- The dead lane had also moved its source finding,
  `SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_..._2026-10-14.md`, to `done/`. That finding
  carries two fixes: fix 1 is B12, still at L1, and fix 2 is W3_3, now held. So the finding went
  back to the staging root, byte for byte as HEAD has it. The pre-registration cites the `done/`
  path, so move the finding again when W3_3 and B12 both land.
- **Left as found:** the dead lane appended a `LEVEL_UP_SELF_CERTIFIED` W3_3 line (level 2,
  ts 1794228340) to the uncommitted `docs/observability/gate_authorizations.jsonl`. That ledger is
  an append-only authority record shared by every lane, so I did not edit it. While W3_3 is off
  origin, the line is an L2 claim with no code behind it. If another lane commits the ledger first,
  the landing will find its LEVEL_UP already recorded. Check that the line's evidence still holds
  before you rely on it.

## What the pre-registration predicts (filed before any run)

1. The renewal floor and the rival floor fall: the domestic network per MWh drops from about £66 to
   £37.5 in 2022/23 and from £69 to £31 in 2024/25. **Fewer than half the held electricity renewals
   sit on the floor to the penny** (it was 21 of 21 at d55598dd6). If most still do, B12 fix 1 is
   carrying the effect.
2. Domestic network cost is redistributed: low users pay more and high users less. The sign of the
   book-level move depends on the mean domestic EAC against about 3,100 kWh. State the EAC first.
3. Pre-2022 moves are small: under £10 a year per household, and under 5% of the network line.
4. Churn: no prediction. It needs the one-variable run with the rival floor held.

## Why it is held, and when to land it

W3_3 is on the correctness holds list (`8ab6c159c`). It is a world change that moves every settled
figure. Landing it now would put it on the same book that has to grade the two billing fixes, and
then neither move could be attributed.

**Land condition:** the first fresh book that passes the domain-invariant gate has been graded.
After that, land W3_3 alone, on its own run, and read that run against the predictions above.

**Before landing, fix or carry this gap:** the deemed and flex writers book no standing charge, so
on those terms the fixed network share has nothing recovering it.
`WORKER_FINDING_THE_DEEMED_AND_FLEX_WRITERS_BOOK_NO_STANDING_CHARGE_SO_THE_FIXED_NETWORK_SHARE_HAS_NO_RECOVERY_2026-11-09.md`
(landed beside this). The branch makes that gap live, so its fix belongs in the same landing.

## How to land it

1. Rebase `w3-3-network-split-held` on the then-current origin/main.
2. Re-run the two test files.
3. Make the map move in the landing commit itself. It is **not on the branch**: the level gate
   refused the first branch commit because a move from L0 to L2 needs a recorded LEVEL_UP, and
   self-certifying L2 for code that is not on origin would be false. At landing:
   - record `gate_authorization.record_level_up_self_certified(...)`;
   - move the open W3_3 row to `maturity_map_closed.yaml` with `level_current: 2`, carrying the
     dead lane's note: `# L2 2026-11-09: cap v1.31 NC split (ofgem_cap_network_allowance.json) in
     all three writers; K8 §7d; prereg WORKER_PREREG_W3_3_*.`
4. Land it through `tools.surgical_land`.

## Recommendation

Mint no new atom. The open W3_3 row stays at L0 with this finding as its pointer, and the seat lands
it when the condition above is met.
