<!-- CONSUMED 2026-07-29: minted into RUNG-1 staged atoms. Deliverables #1/#3/#4 →
PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29.md; deliverable #2 →
PLANNER_MINTED_self_authority_release_sweep_2026-07-29.md. This ruling and its sibling
(DIRECTOR_RULING_LITERAL_ACT_LIST) are one repeated ask, deduped into those two atoms. Parked in
in_progress/ (open sub-item = both atoms unbuilt) to stay out of the unprocessed-staging re-scan. -->

# [DIRECTOR-RULING] — Give me the literal acts. Stop describing blocks; emit executable text. (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Priority: above all other work except a live gate wedge.

## 0. Evidence, and the advisor's error

At 19:40 BST on 2026-07-28 the director performed a console act ratifying the authority seam and carrying three release lines (`LEDGER: BUILD_OPEN generator_draw_wiring / cohort_assignment / gap1_reader_contract`). **At 02:46Z — eight hours later — `generator_draw_wiring` was still escalating as blocked on "a director word authorising live activation", in the same wording as before the act.** Nothing the director did released anything.

**Cause, owned by the advisor:** that act *ratified* the `LEDGER:` convention and *used* it in the same message. The parser for the convention was part of the work being authorised, so the ratification landed and the three release lines had nothing to read them. A bootstrap failure inside the fix for a bootstrap failure.

**Separately, for the record:** the 02:16Z recovery was not self-healing in any interesting sense — the planner released five **stale-blocked** mints whose propose-then-proceed windows had elapsed. Time-gated items freed themselves; nothing requiring a director act moved. Three days of blocked items now, with every detection mechanism working perfectly and none of them clearing anything.

## 1. THE REQUIREMENT — literal acts, not descriptions

For **every** currently-blocked minted item, emit **the exact literal text or command that releases it**, in a single batched artifact. Not "needs a BUILD_OPEN ledger entry". Not "director ratification required". **The precise string the director runs or sends**, such that pasting it performs the release.

For each blocked item: its id; the **verbatim executable act**; where it is executed (console command / phone-signed NTFY / advisor-staged doc — whichever genuinely works today, not whichever *should*); and whether the mechanism that consumes it **exists and is tested right now**.

**If the releasing mechanism does not yet exist for some class, say so explicitly and do not emit an act for it** — an unexecutable instruction is worse than an admission. Build the mechanism first, or state what blocks building it.

**Verify before emitting.** Every act in the batch must have been proven to work — a real release performed end-to-end against at least one item, or a test proving the consuming path fires. The director has now performed two console acts that did nothing; a third that also does nothing is a worse outcome than a delay.

## 2. The four unstated-reason blocks

`intra_year_price_cap_granularity`, `money_representation_evidence`, `payment_channel_dd_consistency_invariant`, and any other reading *"blocked (reason unstated in the mint doc)"*: **state the reason and the release condition, or draw them.** A block without a reason is not a block; it is work hidden behind a status. This was already ruled (`a8c182642` §3) and has not been actioned.

## 3. Empowerment

**How you produce this is yours.** If you judge that some blocks should simply be released under authority you already hold — level-ups at L1/L2 under the twin's standing authorization, items whose ruling has already been consumed, anything time-gated and elapsed — **release them yourself and report it**, rather than adding them to a list for the director. The batch should contain only what genuinely requires an act he alone can perform.

**And if you judge this whole approach wrong** — if the right fix is to change how blocks are represented rather than to enumerate acts — **say so with reasoning and propose that instead.** The advisor has now designed this plumbing incorrectly twice; you are closer to it.

## WORK THIS CREATES

1. One batched artifact: every remaining director-required act, verbatim and executable, each proven to work.
2. Everything releasable under existing authority, released and reported.
3. Reasons and release conditions for the unstated-reason blocks.
4. A plain statement of any block class whose releasing mechanism does not yet exist.

Acceptance: the director performs one action and the blocked count falls measurably — verified by the count before and after, published.

**Risk & proportionality:** diagnosis and enumeration; releases only under authority already granted. Tag: **priority; proceed.**

— Advisor bridge, recording that the advisor's own paste design caused the failed release. 2026-07-29.
