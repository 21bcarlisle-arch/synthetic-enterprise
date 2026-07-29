# [DIRECTOR-RULING] — Give us the LITERAL act. One executable list, for all blocked items. (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Priority above further minting and above all HARDEN work.

## 0. The finding

The director executed a console act at ~19:40 BST on 2026-07-28 intended to release `generator_draw_wiring`, `cohort_assignment` and `gap1_reader_contract`. **At 02:46Z on 2026-07-29 — eight hours later — `generator_draw_wiring` was still reported blocked on "a director word authorising live activation."** Nothing released.

**The advisor's error, on the record:** that paste ratified the `LEDGER: BUILD_OPEN <atom>` convention **and used it in the same message**, when the parser for that convention was part of the work being authorised. The ratification landed; the release lines had nothing to read them. A bootstrap failure inside the fix for a bootstrap failure.

**What actually moved overnight:** the planner released five *stale-blocked* mints whose propose-then-proceed windows had elapsed (02:16Z). Time-gated items freed themselves. **Nothing requiring a director act moved.** Twenty-two remain, and the count is not falling.

Three days of this. Every mechanism added detects the condition accurately and none of them clears it. **We are going to stop designing the authority plumbing from the advisor side and ask you what it needs.**

## 1. What is required — the literal act, for every blocked item

Produce **one document, and one batched [ACT] pointing at it**, listing every currently-blocked minted item with, for each:

1. **The atom / mint name.**
2. **What it is blocked on**, in one line.
3. **THE LITERAL ACT** — the exact text to paste or the exact command to run, verbatim, character for character, that releases it. Not a description of the class of act. Not "a director word". **The string.** If it is a console command, the command. If it is a signed NTFY message, the exact message body. If it is a file the director must create, the path and contents.
4. **Where it must be executed** — console, phone-signed NTFY, advisor bridge, or self-drawable.
5. **What will be observable** when it has worked — the commit, ledger row or status change to look for, so success is checkable rather than assumed.

**Group them by execution channel**, so the director performs one act per channel rather than twenty-two acts.

## 2. Non-negotiables

- **If the release mechanism for a class does not yet exist in code, say so explicitly** rather than emitting an act that cannot be parsed. That is the exact failure that wasted the last eight hours. An honest *"no mechanism exists to release this; here is what would need building"* is a correct answer.
- **The four items blocked with reason unstated** (`intra_year_price_cap_granularity`, `money_representation_evidence`, `payment_channel_dd_consistency_invariant`, and any sibling) are resolved either way: state the reason and its literal act, **or** treat them as unblocked and draw them. A block with no reason is not a block.
- **Anything releasable at your own authority — take it now**, do not list it. Level-ups within the twin's standing L1/L2 authorization, stale windows elapsed, self-drawable mints. The list is only for what genuinely requires the director.
- **R12:** the count of blocked items is a diagnostic, never a target. Do not clear items by re-scoping them into nothing.

## 3. Priority

This outranks further gap minting, the K-pilot decomposition, and all HARDEN work. Twenty-two blocked items with a working detector and no working release is the top defect in the system.

## WORK THIS CREATES

1. The literal-act list, grouped by channel, with observable success criteria.
2. Explicit statements where no release mechanism exists.
3. Reasons stated or blocks dropped for the unstated four.
4. Everything self-releasable already released before the list is sent.

Acceptance: the director can clear every genuinely director-blocked item by executing a small number of verbatim acts, and can verify each worked without asking.

**Risk & proportionality:** reporting and self-release only; no new scope. Tag: **priority zero.**

— Advisor bridge, recording the advisor's own bootstrap error as the cause of the wasted act. 2026-07-29.
