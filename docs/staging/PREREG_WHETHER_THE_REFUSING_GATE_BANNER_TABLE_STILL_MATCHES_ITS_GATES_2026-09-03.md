**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: whether the refusing-gate banner table still matches the gates it names

Written **before** the measurements below were run, at HEAD `b6b3c3fa8`, 2026-09-03T02:09Z.
Filed by the delivery seat working the claim `the-publish-wedge-is-one-staged-unwired-file`.

## What is already known (measured, not predicted)

Established before this file was written, and therefore **not** predictions:

- The drawn brief's own three done-conditions are all satisfied on the shared tree.
  `background.publish_freshness.describe()` reads `live -- figures reached origin 0.2h ago`;
  `git log -1 -- site/data/` on `origin/main` is `b6b3c3fa8` at 2026-09-03 02:55 +0100, later
  than the `1c4f64733` the brief named; `docs/staging/run_complete_*.md` is **0**, down from the
  35 the last prereg measured, with 1452 in `done/`. The work landed at `19f226e46`,
  `eb0fae2fc` and `15709e9e8`. This seat adopted rather than rebuilt.
- The reading `NO verified publish on record` in this linked worktree is not a second fault.
  `publish_freshness.STATE_FILE` resolves from `__file__` and
  `docs/observability/.last_content_publish.json` is untracked, so the answer is per-tree. It
  fails to UNKNOWN, never to fresh, which is the direction that module's own docstring requires.
- `background/process_run_complete.py:2982` `_REFUSING_GATE_BANNERS` is a hand-written tuple of
  seven `(name, literal_substring)` pairs, matched with `banner in hay` by `_parse_refusing_gate`.
  Six name a first-party gate whose source exists in this tree; the seventh, `I001`, names ruff.
- `tests/background/test_a_non_test_gate_refusal_is_named.py` passes (28 passed, 1 skipped with
  `tests/tools/test_artefact_rerun_diff.py`). Its legs exercise the matcher against **fixture**
  strings the test file itself supplies.

## The gap this registers a measurement about

The matcher's correctness rests entirely on those seven literals still being what the gates
print. Nothing in the tree compares the table to the gates. The module's comment argues one
direction of that risk is safe — *"a gate that changes its wording goes UNNAMED ... rather than
misattributed"* — and that argument is sound as far as it goes. It covers one direction.

## The predictions

**P1 — at least one banner in the table does not appear literally in the source of the gate it
names.** `I001` is the declared external case (ruff emits it, we do not), so P1 is graded on the
**six first-party** entries only. If a first-party banner is absent, that entry can never fire
and the gate is unnameable today, not on some future rewording.

**P2 — at least one banner is short enough to match a line that is not a refusal.** Four
entries are bare uppercase fragments — `WRITE-TIME GATE`, `LEVEL PROMOTION`, `LIVE LEDGER`,
`FINDING SEVERITY`. A gate that prints its own name while **passing**, or a header printed
unconditionally before the verdict, would satisfy `banner in hay` on a cycle it did not refuse.
Because `_parse_refusing_gate` returns the **first** match in chain order, one such entry
sitting above the true refuser misattributes the refusal — the precise defect the module was
built to end, re-entering by the other door.

**P3 — no control in the tree relates the table to the gates.** No test imports both
`_REFUSING_GATE_BANNERS` and any gate module, and no test asserts a table banner is present in a
gate's source or in its real output.

## What would refute each

- **P1 refuted** if all six first-party banners appear literally in their named gate's source.
- **P2 refuted** if every one of the seven banners appears in its gate's output **only** on a
  refusing run — i.e. no gate emits its banner substring on a passing run.
- **P3 refuted** if `git grep _REFUSING_GATE_BANNERS` returns a control outside
  `process_run_complete.py` that reaches a gate.

## Why this is registered rather than just measured

P2 is the one I could talk myself into either way after seeing the answer. The fail-safe argument
in the module's own comment is genuinely convincing, and having read it I would be inclined to
report "fail-safe, fine" whichever way the substrings fell. Writing down first that a **short**
banner fails in the opposite direction to a **reworded** one is what makes the measurement able
to refute me rather than agree with me.

**Graded:** P1 CONFIRMED and splits (source-presence was the wrong instrument and erred both
ways; 5 of 7 rows dead against printed output, worse than predicted). P2 **REFUTED** as stated —
the four bare fragments match nothing at all, so they cannot false-positive in either direction;
the mechanism P2 names was then found live in this seat's own repair and is why needles became
ALL-OF. P3 CONFIRMED. Full grading in
`SEAT_FINDING_THE_GATE_NAMING_TABLE_MATCHED_NOTHING_FIVE_OF_ITS_SEVEN_GATES_PRINT_2026-09-03.md`,
filed beside this file.
