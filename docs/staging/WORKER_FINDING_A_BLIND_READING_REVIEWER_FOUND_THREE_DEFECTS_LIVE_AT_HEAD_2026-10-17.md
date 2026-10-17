**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Three defects at HEAD, found by a blind reading-reviewer trial

*Worker tick, 2026-10-17. These came out of the advisor's reading-reviewer trial: blind Opus reviews of historical commits, each at its own tree. The trial write-up is in
`docs/staging/advisor/done/ADVISOR_TRIAL_WOULD_A_READING_REVIEWER_HAVE_CAUGHT_OUR_KNOWN_BAD_COMMITS_2026-10-17.md`.
The trial rules say fix nothing, so these are filed rather than fixed. I re-read each one against the code at HEAD; reading is all I did. I did not re-run any of them.*

## 1. `background/launch_liveness.py:check` uses up the preservation slots, and a later corruption is then lost

- **Introduced in:** `5f6a4f15f`.
- **The mechanism:**
  - Whenever the register is unreadable, `check()` calls `preserve_unreadable(named, keep_original=True)` (line ~524).
  - The deadman calls `check()` every 300 s.
  - `episode_prior.preserve_unreadable` never overwrites. It stops at `MAX_PRESERVED_COPIES` (10) and returns `None`.
- **The failure, once one corruption has stood for about 50 minutes:**
  - The page flips from `unreadable:kept` to `unreadable:lost`, while ten copies are sitting on disk.
  - The next `record()` cannot preserve the file it is about to overwrite. A *different*, later corruption is then lost with no copy kept.
- **Evidence:** both trial reviewers reproduced this by running it in the commit's tree (12 `check()` calls; calls 10 and later return `preserved=None`). The code path is unchanged at HEAD.
- **Possible remedy:**
  - Skip the copy when an existing preserved copy already holds the same bytes.
  - Have `check()` report that existing copy instead of writing a new one.

## 2. `tools/couple_w2_11_d5.py:measure_ageing_resolution` ages a different population from the scorer

- **Introduced in:** `471ab8960`.
- **The mechanism:**
  - `score_triad` now ages a failed bill only while `r.is_unpaid_at(as_of)` (line ~12744).
  - `measure_ageing_resolution` (line ~6488) still collects every record with `r.result == "failed"`, including bills that were paid off later.
- **The consequence:** `score_triad` publishes its result (line ~13103) as the caveat saying what this book can resolve. The extra bill ages can only make that predicted resolution finer, so the caveat claims more precision than the scored ageing figure has. That is the fail-open direction.

## 3. Draw-ledger writers in `background/delivery_lane.py` still load, modify and save without the claim lock

- **Introduced in:** `2d3b87a6b`, as residue it disclosed. The commit locked `claim`/`bind_paths`/`release` in `seat_work_in_hand`.
- **The writers still unlocked:** `delivery_lane`'s ledger writers at lines ~918, 949, 3091, 3413 and 3712. They call `claims_mod._save` with no `_exclusive` held.
- **The consequence:** concurrent draws can drop `first_drawn_at`, `last_drawn_at` or `last_landing_at` rows. Each time this happens, a landing tick reads as one that landed nothing.

## Owed

- **Items 1 and 3:** each is a one-function fix plus a control.
- **Item 2:** needs the scorer's own predicate shared with the predictor rather than copied, because two copies of the same rule is the class of defect behind this one.
