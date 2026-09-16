**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the blind-arm re-run sits uncommitted and disagrees with the published baseline"

*LATENT and not BLOCKING deliberately: the one live consequence — HEAD's published arms artefact
describes the pre-repair-1 world — is already owned by the lane running repair 2, and marking this
BLOCKING would draw ahead of the queue in a lane that is mid-repair on exactly this. The provenance
gap is real and structural, and it is handed on rather than wedged.*

# The two blind-arm artefacts are two worlds, not two calibrations, and neither can grade the other

Delivery seat, 2026-09-16, against `fd899ddf0`. Pre-registration written before the measurement:
`docs/staging/SEAT_PREREG_THE_TWO_BLIND_ARM_CALIBRATIONS_MAY_PRICE_DIFFERENT_BOOKS_2026-09-16.md`.

**Disposition: the premise is spent. The working copy is another lane's live work and must not be
landed.** Nothing about the uncommitted artefact is committed by this finding.

---

## What the item asked

> Establish which of the two calibrations is right — HEAD says `world_curve_basis: "saturated --
> past the ceiling"`, shortfall −£467.81, belief error 41.1pp; the working copy says `"observed --
> inside the calibrated window"`, +£303.27, 18.7pp — then either land it … or discard it.

Those six numbers are real and I reproduced all six. **The framing around them is wrong**, and it is
wrong in the way this project has now paid for repeatedly: *before dividing two numbers, say out
loud what each one counts*.

## Four of the premise's factual claims about the tree are false

| premise | measured at `fd899ddf0` / shared tree |
|---|---|
| "HEAD's 73 lines" | HEAD's copy is **15,799 lines**, and has not been 73 since `856b65d9d` (08-25) |
| "a finished re-run of 1,491 lines" | the shared copy is **10,361 lines** — *smaller* than HEAD. Direction reversed |
| `world_curve_basis: "saturated"` is HEAD's reading | it is a **per-account** field. HEAD carries `saturated` on 189 accounts, `EXTRAPOLATED` on 160 and `observed` on 48. The premise read `accounts[0]` and reported it as the artefact's verdict |
| the re-run is "unowned", from the stranded 08-30 line | the file's mtime is **2026-09-16 06:09:20**, i.e. **86 seconds before `9fd8ca3c3`**, today's repair-1 commit |

## What the two artefacts actually are

**They differ in at least three variables at once, so neither can be graded against the other.**

### 1. Different books

| | HEAD | shared working copy |
|---|---|---|
| `accounts_priced` | 397 | 226 |
| `SYN-*` accounts | **1** (`SYN-2021-001`) | **63** (62 of them `SYN-2016-*`) |
| id sets | \|shared ids\| = 60 of 397/226, and only **4** of those 60 carry the same `eac_kwh` |

`customer_id` is **not a stable key across these runs**: `C1` exists in both, with `eac_kwh` 1779.0
at HEAD and 1786.2 in the working copy. The 60 "shared" ids are overwhelmingly coincidental
collisions, not the same customers. Any per-account comparison keyed on `customer_id` — which is
what the item's −£467.81-vs-+£303.27 is — is comparing two different households.

The 62 new `SYN-2016-*` accounts identify the working copy exactly. Today's
`SEAT_RESULT_A_GAS_ONLY_ACCOUNT_CAN_NOW_LEAVE_…` records that the 18 gas-only accounts which could
not depart "are all drawn `SYN-2016-*` points". Repair 1 (`9fd8ca3c3`, 06:10:46) is what gave them
renewal decisions — 81 where there were 0.

### 2. Different worlds

On the **4 accounts that are genuinely the same account** (same id, same `eac_kwh`), the readings
still move:

| account | HEAD shortfall / basis | WORK shortfall / basis | `endpoint_side` |
|---|---|---|---|
| `PROS-2020-0012g` | −1148.01 / saturated | −956.70 / saturated | None = None |
| `PROS-2025-0170g` | −1376.41 / saturated | **−19.73 / observed** | floor = floor |
| `PROS-2023-0014g` | −857.11 / saturated | **−329.27 / observed** | None = None |
| `PROS-2023-0172g` | −1206.69 / saturated | −488.14 / saturated | None = None |

**P3 of the pre-registration is refuted and the refutation is kept here.** I predicted identical
accounts would agree, because I thought only the book had narrowed. They do not agree: two of four
flip `saturated` → `observed`. Repair 1 changed who departs across 2016–2025, so the realised book
evolves differently and the world's own response curve is read at different points. **P4 held** —
`endpoint_side` is identical on all four, so the candidate grid and its bounds did not move.

### 3. Different producer vintages

`belief_vs_truth.shared_calibration.sides.world` has a different **shape** in each: HEAD carries a
`witness` prose string; the working copy carries `reads: market_departure_rate_pct`,
`descends_from_the_record: true`, `years_checked: 10`. The working copy was written by newer code.
The working copy also carries a `population` block (8 keys) HEAD lacks entirely.

## So which is right?

**Neither grades the other, and the question as posed has no answer.** On the one axis where they
can be compared — is a gas-only account able to leave this world — the working copy is right and
HEAD is wrong, and that was settled by `9fd8ca3c3` this morning, not by either artefact.

**It still must not be landed**, for a reason that is about sequence and not about quality. Repair 2
is *in flight right now* (pid 2289566, drawn as `the-gas-tariff-type-read-becomes-the-c1b-roll-…`),
and its own draw text says:

> repair 2 done honestly puts roughly a third of the 72 already-labelled gas legs onto SVT, which
> **SHRINKS the priced population** before the 158 enlarge it — the net sign is deliberately not
> predicted.

Landing the working copy now would publish a mid-sequence snapshot of a population the live lane is
deliberately about to change again, as if it were a settled baseline — and would pre-empt a net sign
that lane has explicitly declined to predict. The artefact is not stranded work. It is a
measurement taken between two halves of a repair, by the lane doing the repair.

## The structural defect underneath, which IS ours to fix

**`docs/observability/value_based_pricing_arms.json` carries no run provenance at all.** Walking
both copies for any key matching `provenance|book|generated|vintage|commit|stamp|world|run_id`
returns nothing at the top level — no `generated_at`, no `book_identity`, no world or code stamp.

That is the same defect class `f9866cd2a` closed on 2026-08-30 for the **sibling** artefact, under
the title *"the arms' book was read once at the end, so two arms on two books read as one"*, whose
`WORKER_FINDING` was literally named `THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON`. The fix
landed `book_at_run()` and `same_book_across_arms()` into `tools/run_value_cycle_ab.py` and **was
never propagated to `tools/couple_value_based_pricing.py`**, which writes this artefact at line 1168.

This is the whole reason the present confusion was possible, and the reason it cost a full Lane 0
invocation: **an artefact that cannot name its book or its world is indistinguishable, on inspection,
from a rival calibration of the same one.** The item's author had no way to tell — nothing in the
file says. That is a defect in the artefact, not in their reading.

`f9866cd2a`'s own commit message already contains the ruling that applies here:

> No run was executed and no artefact regenerated: the three superseded readings **cannot have their
> books established after the fact** and are deliberately not backfilled.

The same applies to HEAD's arms artefact. It cannot be retro-stamped, and this finding does not
propose to.

## One observation, flagged and NOT over-claimed

`endpoint_bound` is **19 in both files** — HEAD splits it 1 ceiling / 18 floor, the working copy
17 / 2. Two near-disjoint books of 397 and 226 landing on exactly 19 endpoint-bound accounts is
either coincidence or a constant leaking into a count. I have not established which, and I am not
asserting a defect. It is worth one probe by whoever next opens the producer.

The ceiling/floor *split* is separately explained by the working copy's own `population` block,
which states `lawful_ceiling_passed: false` and that at this call site `ceiling_bound` is
"structurally False for every account here and its count is not a measurement of anything".

## What is owed next

1. **Propagate `f9866cd2a`'s provenance discipline to `tools/couple_value_based_pricing.py`** — the
   arms artefact must record the book it priced and the world it priced it in, failing closed on an
   unrecorded book rather than letting today's resolver stand in. Handed on.
2. **Do not re-open the "which calibration" question.** It is not a question. Re-running the arms
   after repair 2 lands produces the first artefact that can be compared to anything, because it
   will be the first one that names its own book.
3. The 19/19 `endpoint_bound` coincidence above.
