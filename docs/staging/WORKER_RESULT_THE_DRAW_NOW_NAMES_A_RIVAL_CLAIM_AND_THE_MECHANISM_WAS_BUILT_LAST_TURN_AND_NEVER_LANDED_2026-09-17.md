**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The draw now names a rival claim, and the mechanism was built last turn and never landed

*Worker, 2026-09-17, scheduled tick, on `lane0-two-ids-one-work-is-undetectable-at-draw-time`.
The drawn item asked for a draw-time question that catches two ids describing the same work. It
already existed, uncommitted, in the shared tree — written by an earlier invocation of **this same
claim** that landed nothing before its window closed. This turn verified it, corrected two false
claims inside it, and landed it.*

## 1. The premise check fired, and it was right about the commit and wrong about the work

The dispatch carried `PREMISE CHECK ... 7d9eabe49 ... ALREADY an ancestor of origin/main`. That is
true and it is **not** a spent premise. `7d9eabe49` is the *rival's* landing — the evidence the
item is built on, cited as context, not the remedy. This is precisely the shape `premise_note`'s
own docstring reserves ("items also cite commits as CONTEXT"), and the annotate-never-suppress
design is what let the work proceed. Recorded because it is the first observed instance of that
carve-out being load-bearing rather than hypothetical.

## 2. What was actually spent was the LAST TURN, not the premise

`background/delivery_lane.py` carried 213 uncommitted lines (mtime 09:54) and
`tests/background/test_two_ids_for_one_piece_of_work_are_named_at_the_draw.py` was untracked
(mtime 10:03). Neither was at `HEAD` or at `origin/main`. The claim was re-drawn at 10:49 under the
same id.

**The item exists to stop two ids costing two turns; it cost two turns itself, to one id.** The
sweep returned the claim to the pool and nothing carried the built-but-unlanded work across, because
the binding this lane reads is `--landed`, and `--landed` needs a commit. An unlanded turn is
indistinguishable from a turn that did nothing. That is the same lesson the mechanism below encodes,
arriving from the other direction, and it is the argument for *land the increment* being a rule
rather than advice.

## 3. The mechanism, as landed

`rival_claims` / `rival_note`, composed into `doorbell` ahead of the work. Two legs:

* **SUBJECT** — two ids sharing ≥2 tokens that almost nothing else in the draw ledger uses. This is
  the leg that answers at the moment of collision, when neither claim has landed and so neither has
  a path bound to it.
* **PATHS** — a file this item's prose names that another live claim already holds, via `paths`
  (bound by a landing) or `named_paths` (extracted at its own draw). Shared-by-design rooms are
  dropped by `claims_mod._informative`.

It reads **both** claim stores, excludes stale claims without sweeping, and **annotates — it never
refuses**. Two live claims on one subject are often correct; a refusal would have to be right about
which, a note only has to be worth reading.

## 4. Measured at real inputs, on the live ledger

| | |
|---|---|
| ledger population | 358 ids, 63,903 pairs |
| rarity ceiling at `_DISTINCTIVE_SHARE` = 1% | 3 ids |
| pairs the rule fires on | **31 (0.049%)** |
| the 2026-09-17 pair | **caught** — shares `23`, `era5`, `pull` |

Reading all 31: every one names work a reader would call the same subject. Against the two *live*
claims it is quiet for this item (`{}`) and fires correctly on a synthetic near-twin of the other.

## 5. Two claims inside the work were FALSE, and are corrected beside themselves

Both were in the flattering direction. Neither changes the mechanism; both change what a reader
would believe about it.

**(a) `_RIVAL_TOKEN_COUNT`'s justification did not hold.** The comment said one token was a
coincidence "because `era5` alone is shared by the 09-05 resume item, which was genuinely different
work" — i.e. that the threshold of 2 excludes it. It does not:
`resume-the-era5-pull-for-the-last-31-weather-cells` shares **`era5` and `pull`** and fires against
both 09-17 ids. The true justification is the measured volume — threshold 1 fires on 456 of 63,903
pairs (0.714%), 2 on 31, 3 on 10 — and the firing on the resume item is *accepted*, because the
mechanism annotates rather than refuses. The corrected reasoning is now at the constant.

**(b) The mutation table miscounted and misnamed.** It said "All fourteen were RUN" over a list of
sixteen, and named `..._ONE_SHARED_WORD_IS_A_TOPIC_NOT_A_DUPLICATE` and
`..._A_SHARED_ROOM_IS_TRAFFIC_NOT_DUPLICATION` — neither of which is a test in the file (both omit
`AND`). A reader greping for either finds nothing. Corrected.

## 6. Eight mutations re-run independently, and two of my own simulations were wrong

Rather than trust the table, c, d, e, f, j, k, n and o were re-run by monkeypatch. All eight fired.
Two fired **only after the simulation was corrected**, and both slips flattered the control:

* **(d)** patching `_ledger_path` to blind the `named_paths` read also moved where the *fixture
  writes* the vocabulary, so both sides moved and the mutation changed nothing. A mutation the
  fixture follows is not a mutation. Strip the field at **read** time instead.
* **(o)** passing a one-store list raised `IndexError` out of the fixture, which is not the control
  refusing. Blind the second store at **read** time instead.

Both are written into the suite's own mutation table, because the next person to re-run it will
reach for the same two shortcuts.

## 7. A finding that is NOT mine, left for its owner

`tests/architecture/test_static_quality_ratchet.py` is **red in the shared working tree** —
`I001: 1308 → 1307`, one *fewer* violation. It is not this lane's, and it is good news: a clean
`git archive` extract of `b10e16207` reproduces the baseline exactly (all codes identical), so the
drop lives entirely in uncommitted bytes. The file is
`tests/tools/test_generate_maturity_map_data.py`, whose single I001 is fixed in the working tree and
not in any commit. **Somebody's import-sort fix is stranded.** It does not wedge this landing —
`REPO_ROOT` resolves from `__file__`, so `surgical_land` grades the extract of the tree the commit
would create, where HEAD's copy restores 1308 — but it wedges any lane that runs the ratchet in the
shared tree, and it will stay red until its author lands it.
