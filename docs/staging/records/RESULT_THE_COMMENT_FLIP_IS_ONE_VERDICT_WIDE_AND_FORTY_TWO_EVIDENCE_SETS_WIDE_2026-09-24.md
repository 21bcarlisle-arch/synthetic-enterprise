**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the flat comment flip moves ONE verdict and loads FORTY-TWO evidence sets, so the narrow third reading is the remedy

*Delivery seat, 2026-09-24, from an isolated worktree. Answers
`docs/staging/records/PREREG_HOW_WIDE_IS_COMMENTS_AS_EVIDENCE_IN_THE_STALE_COPY_CLOCK_2026-09-24.md`
(landed `ddc325c9c`, BEFORE the measurement). Discharges the three-step remedy ordered by
`docs/staging/done/SEAT_FINDING_NO_RULE_IN_THE_STALE_COPY_MODULE_CAN_SEE_A_COPY_WHOSE_ONLY_LOSS_IS_A_LANDED_COMMENT_2026-09-24.md`
(`89e94ec5a`), instance 54 of CLASS_CONTROLS_THAT_CANNOT_FAIL.*

## The predictions, and what happened — two of four refuted

Measured on the live shared tree `/home/rich/synthetic-enterprise`, 52 tracked-modified `.py` paths,
judgement tree `origin/main`. The flip measured is `_trivial(ln)` →
`_trivial(ln, comments_are_evidence=True)` in `distinctive_lines`' STRONG set.

| | predicted | measured | |
|---|---|---|---|
| **P1** width of the flat flip | **≥ 8**, point estimate 12–25 | **1 of 52** | **REFUTED** |
| **P2** the flip also subtracts | **≥ 1** path loses its complaint | **0** | **REFUTED** |
| **P3** the target path gains one | gains a `Loss` | gains `predates_landing_carrying_some` | CONFIRMED |
| **P4** the narrow reading is narrow | fires on ≤ 3 | 7 on content, **2** with the clock, **1** net new | CONFIRMED |

**P1 was wrong by an order of magnitude, and the reason it was wrong is the finding.** I predicted
from comment DENSITY — correctly, as it turns out — and inferred width from it. The inference is the
error: density decides how many evidence sets the flip loads, and the CLOCK decides how many verdicts
change. Those are different numbers and I conflated them.

**P2's mechanism was backwards in the safe direction.** I claimed the flip demotes `predates_landing`
by breaking `len(missing) == len(distinctive)`. That is real, but adding lines makes the all-missing
equality strictly HARDER, so the flip can only ever remove a PREDATES verdict — never add one — and
on this population it removed none. The prediction was refuted; the leg is monotone-safe either way,
which is worth more than the prediction was.

## The attribution — and it is the whole result

One-variable control, because "1 of 52" alone would have licensed the one-character flip:

| | count |
|---|---|
| A. the flip ADDS comment evidence to the path's set | **42 of 51** |
| B. …and the copy MISSES some of those added lines | **9** |
| C. `taken_before` — the copy is OLDER than its landing | **4** |
| B ∧ C — the PARTIAL leg's full gate | **2** (1 of which already complains) |

**The flat flip's narrowness is the clock's, not the comment filter's.** It loads 82% of paths'
evidence sets with prose and is held to one verdict only because `taken_before` is true for four. It
is therefore quiet exactly while a tree's copies are fresh, and noisy on nine the day they are old —
which is the day this control matters. A guard whose width is bounded by how lucky the tree is, is
not narrow; it is untested.

## The registered disposition was NOT taken, and this is the departure, stated plainly

The pre-registration said: *"P1 refuted if the gain count is ≤ 3 — then the flag flip IS the remedy
and the third reading is unnecessary complexity. I would take the one character and delete the
design."* The count is 1. **I did not take the one character.** Two reasons, one of which I could
have known before registering and did not check:

1. The attribution above. The disposition conditioned on verdict width alone, and verdict width is
   the wrong instrument for a change whose cost is carried by the evidence set.
2. **`tests/tools/test_stale_copy_refusal.py::test_the_comment_fallback_does_not_displace_code_evidence`
   already forbids the flip, in terms**: *"the fallback must be reachable ONLY where the strong set
   is empty, or it is a widening wearing a fallback's name"*, on the argument that comments travel
   with cherry-picks, rewraps and reverts. That control is right. The way to honour it is to ask the
   comment question SEPARATELY, not to delete the control that forbids mixing it in.

Registering a disposition conditioned on one number, when a second number and a standing control both
bear on it, is the defect in the pre-registration. The remedy is not to have skipped the
pre-registration — it caught P1 and P2 — it is that a registered disposition should name the evidence
that would change it, not just the threshold.

## What was built

**Rule 1b — `stale_copy_refusal.reverted_comment_block`.** The contiguous comment BLOCK the landing
added that the copy holds not one line of. Reachable in `judge` only where `partial is None` (rule 1
had nothing to say) and `taken_before` is true, so it can never displace a verdict rule 1 reached, and
rules 1, 1a, 2 and 4 are untouched. Its own content half fires on 7 of 52 against the flip's 42.

Two guards, and they are different guards: **wholesale** (a copy holding part of the prose is editing
it), and **not-a-rewrite** (where the landing displaced prose, the copy must hold all of it — a rewrap
supplies a third text and satisfies neither half).

**`stale_copy_refusal.unread_populations`** — the readings NOT made for a path, each naming why, and
`()` is a reachable positive claim.

**`refresh_to_head`'s `NOT_SUPERSEDED` text** no longer asserts "it deletes no name … an ordinary
edit" over a population it never read. Cleared verdict names the comment reading; where rule 1b was
clock-skipped, the verdict says so and withholds the ordinary-edit claim.

## Two honest negatives, recorded because the flattering reading is available

* **The floor does nothing on today's tree.** `COMMENT_BLOCK_FLOOR = 2`, and the fire count is 7 at
  every floor from 1 to 6. It is kept for the lint-pragma and licence-header churn it is aimed at, and
  `test_a_single_landed_comment_line_is_not_a_block` is a CONSTRUCTED proof it bites — otherwise it
  would be an unfalsifiable green.
* **The not-a-rewrite guard is not what makes today's count small either.** All 7 firing paths have
  zero superseded comment lines, so the revert-versus-rewrite discrimination is exercised only by
  constructed fixtures. Both guards are controlled; only the wholesale one is load-bearing live.

## A mutation came back GREEN, and the cause was the third one

`any(...)` → `all(...)` on the wholesale guard left
`test_a_partially_held_comment_block_is_an_edit_not_a_loss` passing. Not an equivalence and not a
no-op: the fixture did not hold the superseded line, so the copy was refused by the REWRITE guard
instead. **The test named one guard and was carried by the other, leaving the guard under test
unreachable.** Fixed by constructing the fixture to hold both halves, and the test now asserts the
other guard is satisfied first so a future fixture drift cannot silently re-route it.

Final state: **8 of 8 mutations RED** (7 on `stale_copy_refusal`, 3 on `refresh_to_head`'s two
sentences — one shared). 133 tests green across the three subject suites, 72 across the downstream
consumers, 161 across `tests/design/` + the static-quality ratchet.

## The gate refused once, and the refusal is worth keeping

`tests/architecture/test_a_control_reads_python_as_code.py` refused the first landing:
`reverted_comment_block` reads Python source as text and must either route through
`tools/python_code_text.searchable` or be frozen as a floor row with a stated reason.

**Routing it would have installed the exact defect that rule exists to prevent.** `searchable()`
BLANKS COMMENTS — that is its whole purpose, so a control cannot mistake prose describing a thing for
code doing it. This function's subject IS that prose, so routing it would erase the only evidence it
reads and return `()` for every copy: a silent, permanent fail-open, arrived at by obeying the rule.
As far as this pass can tell it is the only reader in the tree in that position.

So the row is frozen (added BY HAND to `docs/observability/substring_source_scan_baseline.json`, never
`--freeze`, which goes stale as well as growing), beside `judge` and `clock_judge` which are frozen for
the same underlying cause — the census fails closed when a scope's only path evidence is a SUFFIX tuple
rather than a tree path. The reason is written in the function's own docstring rather than as a per-row
JSON field, because `freeze()` rewrites rows from a three-key schema and would drop the field silently;
a docstring it cannot reach.

## What it unblocks, concretely

`tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` graded
`refused_head_does_not_supersede_it` — "an ordinary edit" — before this change, and grades
**`refreshable`** after it: *"rival copy: supplies no name origin/main lacks, and the stale-copy
control refuses it [reverts_a_landed_comment_block]."* It was one of the two `.py` copies holding the
shared tree's pure fast-forward (`behind=22 ahead=0`). The other,
`test_publish_gate_wedge_draw.py`, is holder work and still wants `isolate_hunks` — unchanged, and
correctly so. **No `--base-wins` was used and the new rule is deliberately NOT in
`BASE_WINS_RULES`:** enacting a discard is a separate judgement from being able to see the loss, and
the finding's instruction on that door stands.

No other verdict on the tree moved: 5 pre-existing complaints unchanged, 1 new.
