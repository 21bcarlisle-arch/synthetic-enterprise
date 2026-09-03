**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: whether the eleven unnamed gates can each be given an honest needle

Written **before** the measurements below were run, at HEAD `964def09f`, 2026-09-03T03:07Z.
Filed by the autonomous worker closing the open half of
`SEAT_FINDING_THE_GATE_NAMING_TABLE_MATCHED_NOTHING_FIVE_OF_ITS_SEVEN_GATES_PRINT_2026-09-03.md`.

## What is already known (measured, not predicted)

Established before this file was written, and therefore **not** predictions:

- `_REFUSING_GATE_BANNERS` in `background/process_run_complete.py` carries **five** rows after
  the repair at `8895925cc`; `tools/git-hooks/pre-commit` invokes **fifteen** gates. Eleven
  report `UNNAMED`.
- The finding names those eleven: `site_lane_gate`, `moap_coherence_gate`,
  `ruling_archive_question_gate`, `consolidation_rhythm`, `size_ratchet_gate`,
  `company_network_isolation`, `file_scope_generated_paths`, `annual_report_import_ratchet`,
  `half_hourly_dependency_ratchet`, `running_total_order`, `scope_evidence_ratchet`.
- The finding's stated rule for closing the gap: a needle must be read from the gate that
  prints it, never invented from a module name. Its control
  (`test_every_needle_is_a_string_its_named_emitter_actually_prints`) enforces
  non-docstring-literal presence in the named emitter.
- The shared tree was two commits behind origin when this turn opened and has been
  fast-forwarded to `964def09f`; the repair's 21 tests pass here.

## The predictions

**P1 — At least two of the eleven cannot be given an honest needle at all**, and must stay
`UNNAMED` with a named reason rather than be given an invented one. Mechanism: the finding
already found one gate (`LIVE LEDGER`) that raises an exception instead of printing a banner,
and gates that refuse through a shared helper or a bare `sys.exit(1)` have no distinguishing
string of their own. Refuted if all eleven yield a distinct, refusal-only literal.

**P2 — At least one of the eleven prints a banner that also appears on a NON-refusal path**
(warn mode, `--check` mode, or a summary line printed before the verdict is known), so a
single-needle row would name it as the refuser of a commit it let through. This is the
false-positive direction the repair's ALL-OF rule exists for, and I predict the repair's own
`(prefix, verdict)` two-needle shape will be required again for at least one gate. Refuted if
every gate's refusal line is unique to refusal.

**P3 — The count of gates in the chain is not fifteen.** The finding says fifteen; I predict
the true count of distinct refusal-capable invocations differs, because
`tools/git-hooks/pre-commit` also prints a refusal banner *itself* for `status_honesty` at
line 13 — the emitter is the hook, not a `tools/` module — which is a category the finding's
"eleven `tools/` modules" framing does not have a slot for. Refuted if the chain contains
exactly fifteen and every refusal banner is emitted by the module rather than the hook.

## What must NOT happen

- No needle written from a module name, a docstring, or a guess. If the gate's refusal string
  cannot be read from its source, the row is not written and the reason is stated.
- The disclosure control `test_the_table_does_not_silently_claim_to_cover_the_whole_chain`
  must continue to hold, with its numbers corrected to whatever the new coverage is — it must
  not be deleted because coverage improved.
- No row added without the emitter that actually prints it, even when another module in the
  chain contains the same string.

## How each prediction gets graded

By reading each gate's source for the literal printed on its non-zero-exit path, and by
running the existing control, which fails any needle absent from its named emitter. Grading
is recorded in the finding that supersedes this file, beside these predictions, whether or not
they held.
