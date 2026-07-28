# [DIRECTOR-RULING] — Blocked-mint batch release, and the ruling-vs-ledger mismatch (2026-07-28)

**Type:** [DIRECTOR-RULING] via advisor bridge. Answers the [ACT] of 14:15Z/15:16Z: 24 minted items blocked and un-worked for 3+ hours.

## 0. The mechanism fault — name it and fix it

Generator activation was ruled 2026-07-25 (`0ac3e1b5e`), cohort assignment 2026-07-27 (`e685eb76d`), GAP1 BUILD open this morning (`27271871e`). **All three remain blocked**, waiting on a `BUILD_OPEN` / `FRONT_OPEN` ledger entry or "a director word authorising live activation."

**Director rulings staged through the advisor bridge ARE director authority** (`0675ec915`). If a block releases only on a ledger entry, then **consuming a ruling must create that entry** — otherwise authority arrives in a form the blocker cannot read, and ruled work sits blocked indefinitely. This is the same class as consumed-≠-absorbed.

**Required:** state what act releases each block class, and make ruling-consumption produce it. If the advisor bridge genuinely cannot author a ledger entry for some class, **say so plainly and name what can** — the director will do that act once, and the gap gets mechanised so it is not needed again.

## 1. RELEASED — these are open, by this ruling

- `gap1_reader_contract_failopen_fix` — BUILD open (re-affirming `27271871e`).
- `gap_registers_as_mint_sources` — BUILD open.
- `inbound_ratification_batch_path` — BUILD open.
- `generator_draw_wiring` — **live activation authorised**, third time of asking, on the terms already ratified in `0ac3e1b5e`: N=200 pool, per-run variation, coverage report gating any published figure, λ=1.0 book unchanged per `e0056d53e`.
- `dd_seasonal_cashflow_physics` — its own condition ("a tick after 2026-07-27 with no director revision") is met; no revision is coming. Proceed.

## 2. Level-ups — take them or batch them

`director_window_delta_view` and `owned_quantity_registry_gate` are blocked on `director_level_up (R16)`. **If L1 or L2: the twin's standing authorization applies — proceed, ledger-backed, no self-claims. If L3: batch for the director's next ratification and say which.** Do not leave them blocked on an unstated level.

## 3. Reason-unstated blocks are a DEFECT

Four items report *"blocked (reason unstated in the mint doc)"*: `board_spec_001_wholesale_reconciliation`, `intra_year_price_cap_granularity`, `money_representation_evidence`, `payment_channel_dd_consistency_invariant`.

A block without a recorded reason cannot be escalated, unblocked or judged — it is invisible work wearing a status. **Every block carries its reason and its release condition, or it is not a valid block.** For these four: state the reason, or treat them as unblocked and draw them. Mechanise it so an unstated-reason block cannot be written.

## 4. Coming to the director

`first_ranked_gap_list` needs ratification of the proposed **deliberate-and-staying** set plus front/epoch opens. Per `27271871e`, moves *into* deliberate-and-staying are the director's — so this is correctly held. **Send it as one batched [ACT] with the proposed set and one line of rationale each**, and it will be ruled in a single pass.

## 5. Empowerment

Sequencing across the released items is yours. If any has been superseded, is already in flight, or should not proceed for a reason the advisor cannot see, **say so and skip it with evidence** rather than working it dutifully.

## WORK THIS CREATES

1. Ruling-consumption creates the ledger entry that releases a block — or a plain statement of what can, if it cannot.
2. The five §1 items drawn.
3. Level-ups taken at twin authority or batched with their level stated.
4. Reasons stated for the four §3 blocks, and unstated-reason blocks made impossible.
5. The ranked-gap-list ratification sent as one batched [ACT].

Acceptance: no minted item is blocked without a stated reason and a named release condition.

**Risk & proportionality:** releases already-ratified work and fixes an authority-plumbing gap; no new scope. Tag: **proceed.**

— Advisor bridge, 2026-07-28.
