**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# PREREG — the one-variable floor run, and whether its narrow width is a degenerate re-draw

A pre-registration and its result. The BLOCKING finding it produced is
`SEAT_FINDING_THE_NARROW_WIDTH_BEHIND_THE_PUBLISHED_SELECTION_SIGN_IS_A_REPEATED_DRAW_2026-09-22.md`;
this file is the register of the prediction, which is why it is not itself BLOCKING.

**Filed 2026-09-22, BEFORE the check in §3 was run.** The run in §1 was already on disk when this
was written (see §2) and its numbers are therefore NOT pre-registered — §3 is the only question
here whose answer was unknown when this file was written, and it is the one that decides whether
§1 may be published at all.

---

## 1. What the run is, and why it was owed

`NOISE_FLOOR_PATH`'s comment block in `tools/generate_value_arms_data.py` has owed one run since
2026-09-18 and names it explicitly: **the next12 seed set at commit `4e7938f673`**. It is owed
because the four same-world families the census publishes each vary BOTH the instrument and the
seed set at once, so none of them can say why they disagree.

The run closes a 2x2 corner. Against the nine-seed floor of 2026-09-10 it holds the TREE fixed and
changes the SEEDS; against next12 it holds the SEEDS fixed and changes the TREE:

| family | tree | seed set | book | n |
|---|---|---|---|---|
| the nine of 2026-09-10 | `4e7938f673` | 11111..99999 | 164 | 9 |
| **this run** | `4e7938f673` | 3100001..3100012 | 164 | 12 |
| next12 of 2026-09-17 | `a178b56d6` | 3100001..3100012 | 154 | 12 |

**The tree leg is not perfectly one-variable and this file says so rather than letting a reader
assume it.** The book moves with the tree — 164 accounts settle at `4e7938f673`, 154 at
`a178b56d6`. The book is not an independent knob: it is what the instrument realises. So the tree
leg separates INSTRUMENT (tree and the book it produces) from SEED SET, which is the separation
the comment block asked for, and it does not separate tree from book. Nothing on disk can.

## 2. The run was already done and never landed

`/var/tmp/se-floorrun-20260910/docs/observability/value_cycle_ab_s1_noise_floor_next12_at_4e7938f673.json`,
untracked in a locked worktree pinned at `4e7938f67`. `producing_commit` resolved
2026-09-18T12:56:26Z, assembled 2026-09-18T23:49:20Z — roughly eleven hours, twelve seeds, world
`39a192ce04c1eda8`, redraw mode `all`, clock `settled-realised`, same patched symbol. A prior
invocation ran it and the turn ended before it landed.

## 3. THE PRE-REGISTERED QUESTION — is the narrow width a degenerate re-draw?

Three of this run's twelve seeds return a **byte-identical** `selection_gbp` of
`-143.32862000001478`: seeds 3100003, 3100006 and 3100012. Three of twelve draws landing on the
same float to fifteen digits is not a coincidence of the world; it is what a re-draw that did not
actually re-draw looks like.

**This matters more than the headline.** If those three seeds are draws the instrument failed to
vary, the run's narrow standard deviation is partly an ARTEFACT of a broken re-draw rather than
evidence about the world — and so, by the same argument, is the nine-seed family's, since it was
drawn at the same tree. That would not merely weaken this run: it would put the page's published
NEGATIVE selection sign, which rests entirely on a narrow width, on an instrument that partly does
not work.

**PREDICTION, written before looking.** If the duplication is a property of the `4e7938f673`
instrument:

- **(a)** the nine-seed family of 2026-09-10, drawn at the SAME tree, will ALSO contain at least
  one duplicated `selection_gbp`; and
- **(b)** next12 at `a178b56d6` will contain NO duplicated `selection_gbp` across its twelve.

If instead next12 also duplicates, the duplication is not tree-specific and some other explanation
is owed. If the nine do NOT duplicate while this run's twelve do, the duplication is specific to
these seeds on this tree, which is the worst case for publishing the run and the one I would least
expect.

**What follows from each outcome, decided now rather than after:**

- **(a) and (b) both hold** — the duplication is the instrument's, it affects BOTH families drawn
  at `4e7938f673` equally, and the width comparison between the two trees is confounded by it. The
  run is published with the duplication named on the page's own surface, and the honest statement
  is that the narrow width at this tree is not yet established as a property of the world.
- **(b) fails (next12 duplicates too)** — duplication is a property of the measurement generally,
  not of the tree, and it weakens the degeneracy reading rather than the run. Publish with the
  count stated.
- **(a) fails (only this run duplicates)** — do NOT publish the family as evidence about the
  width. File it as a run whose instrument is in question and say so.

## 3a. THE RESULT — both clauses hold, and the split across five families is total

Run 2026-09-22, after §3 was written. Kept here beside the prediction rather than edited into it.

| family | tree | n | distinct `selection_gbp` | repeated |
|---|---|---|---|---|
| this run, next12 | `4e7938f673` | 12 | 10 | one value 3x |
| the nine of 09-10 | `4e7938f673` | 9 | 8 | one value 2x |
| the nine of 09-10b | `9f0ab066f` | 9 | 7 | one value 3x |
| next12 of 09-17 | `a178b56d6` | 12 | **12** | **none** |
| next12 at 18327d977 | `18327d977` | 12 | **12** | **none** |

**(a) holds and (b) holds.** Every family drawn at an OLD tree repeats a residual; neither family
drawn at a NEW tree repeats one. Five for five, with no family on either side of the line
behaving like the other.

**And the families line up with the widths exactly.** The three repeating families are the NARROW
ones; the two that never repeat are the WIDE ones. The width disagreement the comment block has
been unable to attribute since 2026-09-18 and the repeated residuals are not two findings — they
are the same phenomenon seen twice.

### The mechanism is NOT a re-draw that failed to fire, and that matters

The obvious reading — "the seed never reached the draw" — is wrong, and the artefact refutes it on
its own rows: `elasticity_redrawn` is 292–296 with `elasticity_held_fixed: 0` on every seed. The
re-draw fires everywhere. There are TWO distinct mechanisms behind the repeats:

1. **An identical pass.** Seeds 3100003 and 3100012 are byte-identical in every recorded field —
   same 296 draws, same advantage, same residual. Two seeds, one outcome.
2. **A residual invariant to a pass that genuinely differed.** Seed 3100006 is a DIFFERENT pass —
   292 draws against 296, `value_advantage_gbp` 20,383.78 against 18,757.89 — and yet its
   `selection_gbp` matches to fifteen digits. The reason is lockstep: between the two passes
   `value_advantage_gbp` moved by 1,625.897961 and `level_advantage_gbp` moved by 1,625.897961,
   identical to the last digit. The two arms move together and the residual is their difference,
   so the residual does not move at all.

Mechanism 2 is the one worth the ink. On this instrument the selection leg is, for part of its
range, structurally unable to vary — not noisily small, but pinned. **A quantity that cannot vary
has no spread to measure**, and a standard deviation computed across draws that include pinned
ones is not an estimate of anything about the world. That is what the narrow width is made of.

### What this does and does not establish

- It **does** establish that the narrow widths, and therefore the NEGATIVE selection sign the page
  publishes off them, rest on an instrument whose selection residual repeats and is in part
  pinned. The narrow width is not established as a property of the world.
- It does **not** establish that the wide width is correct. Not repeating is not the same as being
  right, and this file does not claim the 5,398 figure is the true one.
- It does **not** identify the code change between the trees that removed the lockstep. That is
  the next question and it is named in the hand-off, not answered here.

So the comment block's "I cannot say which width is the right one" is now **half answered, in the
unflattering direction**: one of the two candidates is disqualified as an artefact, and the
surviving one is not thereby confirmed.

## 4. The run's WIDTH *was* pre-registered — by the 09-18 file, not by this one

**This section replaces what it first said, and the first version was wrong in the direction that
flattered nobody — it gave the result away.** It said the run's spread figures were not
pre-registered because they were on disk before this file was written. They are pre-registered:
`docs/staging/records/PREREG_THE_ONE_VARIABLE_WIDTH_CHECK_SEPARATES_THE_INSTRUMENT_FROM_THE_SEED`
`_SET_2026-09-18.md` was filed before the run was launched, predicts the answer, and fixes a
numeric decision rule so the answer could not choose it. Found by reading `docs/staging/records/`
before claiming the gap.

**That prediction is CONFIRMED, and by its own rule rather than by my reading of it.** The rule:
`sd_X < 3000` confirms the width is the INSTRUMENT's; `sd_X > 4000` refutes; between is
indeterminate. **`sd_X = 1311.96`** — inside the confirming band with room to spare.

The two F-ratios that file asked for by name, plus the published floor for context:

| leg | held fixed | moved | F | df | two-sided p | sd ratio |
|---|---|---|---|---|---|---|
| **instrument** | the twelve seeds | the tree | **16.93** | (11,11) | **4.9e-05** | 4.11x |
| **seed set** | the tree `4e7938f673` | the seeds | 1.97 | (8,11) | 0.295 | 1.40x |
| vs published floor | — | — | 1.55 | (17,11) | 0.466 | 1.24x |

Move the tree and the width changes by a factor of four with a p of five in a hundred thousand.
Move the seed set and it does not move at all. **The width belongs to the instrument.** The run
also sits indistinguishably close to the published floor's own width (p = 0.47), which is the
consistency check that makes the instrument reading hard to argue with.

### Where this turn's finding goes BEYOND the 09-18 rule, and why that is not a re-interpretation

The 09-18 rule attaches a sentence to the confirming branch: *"The published sign's width is
defensible on its own instrument."* **§3a refutes that clause on evidence the rule's author did
not have** — and the distinction matters, because reading a pre-registered rule's conclusion loosely
after the fact is the thing pre-registration exists to stop.

The rule asked one question: does the width belong to the instrument or the seed set? It answered
INSTRUMENT, and that answer stands exactly as written. It did not ask whether the narrow
instrument's width is a measurement at all. §3a shows it partly is not: 5 of the published floor's
18 draws are repeats of other draws, and at least one repeat is a residual pinned by two arms
moving in lockstep. **"The width is the instrument's" and "the instrument's width is trustworthy"
are different claims, and only the first was pre-registered.** So the confirmation is clean and the
`defensible` clause is withdrawn — by the run that the same file commissioned.
