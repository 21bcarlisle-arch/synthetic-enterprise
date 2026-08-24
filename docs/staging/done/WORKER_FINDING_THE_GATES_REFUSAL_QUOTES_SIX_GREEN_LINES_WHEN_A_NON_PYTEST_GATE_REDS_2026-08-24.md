**Severity:** LATENT · **Lane:** H_harness

**Discharged:** `tests/tools/test_surgical_land.py::test_a_NON_PYTEST_gate_that_reds_after_a_green_pytest_gate_is_named`, `tests/tools/test_surgical_land.py::test_MUTATION_a_green_chain_still_shows_its_green_lines_and_claims_no_refusal`, `tests/tools/test_surgical_land.py::test_the_tail_is_the_FLOOR_and_not_the_fallback` — the falsifier and the null control this document specified, run verbatim.

> **REPAIRED 2026-08-24, and it took the structural route this document asked for rather than
> nine more prefixes.** The recommendation was right on both counts: the vocabulary must not
> grow a gate at a time, and the fallback keyed on the selection being EMPTY could never fire
> on a selection that was merely WRONG.
>
> **The tail is now the FLOOR, not the fallback.** `child_diagnostics.verdict_excerpt` always
> emits the stream's tail and only ever ADDS earlier verdict lines to it. That closes the class
> without knowing any gate's name: `tools/git-hooks/pre-commit` is a `cmd || exit 1` chain, so
> it stops at its first failure and whichever gate reds wrote the END of the stream — which is
> exactly what a tail reads, and a thirteenth gate needs no change here. The selection keeps the
> one job the tail genuinely cannot do: carrying the individual `FAILED` nodes out of a pytest
> run that printed 200 lines after them.
>
> **The second half was in `run_gate`**, and this document did not have it. Returning
> `stdout + stderr` destroyed the floor before it could work: the tail of the joined stream is
> import-time SyntaxWarnings every time, not the refusing gate. It now returns the two streams
> separately and the refusal renders both, labelled, with stderr capped at the size of the
> stdout section — never crowding out a three-line verdict, and given the whole budget when
> stdout is empty (a hook that dies before any gate prints says everything on stderr).
>
> R15, five source mutations, each firing its own named test: restoring the empty-only fallback
> (5 red), re-concatenating the streams (1), dropping stderr (2), a fixed stderr reserve (1),
> and a silent truncation cap (2). 77 tests across the two files, was 72.

**Found by:** worker tick 2026-08-24 15:2x BST, when a `surgical_land` landing of the OOM door
was REFUSED and the refusal it printed was entirely green.

## Class registration

`background.finding_classes` derives the class from the TITLE, and files this one under
`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` (matched phrase: "GATES REFUSAL QUOTES SIX GREEN
LINES WHEN A NON PYTEST GATE RED") — checked by running the classifier, not assumed. That is the
right room: the subject is a landing refusal.

Its **shape**, though, is `CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`'s killer pattern
FAIL-OPEN, and anyone repairing it should read that doctrine rather than this room's: the
selector's documented fail-closed fallback cannot fire in the one case it was written for.

## Observed, with evidence (R9)

The refusal, quoted whole — seven lines, six of them ticks:

```
[surgical-land] REFUSED: GATE RED on the resulting tree (rc=1). ...
578 passed, 14 warnings in 123.75s (0:02:03)
[test-gate] ✓ wall crossings reconcile at the tree this commit creates (6 live, 91 ruled)
[test-gate] ✓ the wall's four walker-invisible channels have not grown; ...
[test-gate] ✓ every first-party reference resolves in the tree this commit creates (103 checked)
[test-gate] 18 test file(s): ...
[test-gate] ✓ all targeted tests green
```

The actual cause was `tools/orphan_ratchet.py`, which had printed a nine-line refusal naming
the module, the class, the census document and the exact repair command. **Not one character of
it survived into the refusal.** Reconstructing it cost a hand-written re-materialisation script
and a second gate cycle — the precise cost the selector this replaced was written to stop.

## The mechanism

`background/child_diagnostics.is_verdict_line` selects on `VERDICT_MARKERS`:

```python
VERDICT_MARKERS = (
    "FAILED", "REFUS", "ABORT", "KILLED BY SIGNAL", "NOT committing", "timed out",
    "[test-gate]", "[site-lane]", "[status-honesty]",
)
```

`tools/git-hooks/pre-commit` runs **twelve** gates in sequence, each with its own refusal
vocabulary. Three are named above. The other nine are not, and none of their refusal lines
matches any generic marker either:

| gate | its refusal's first word | matched? |
|---|---|---|
| `pre_commit_test_gate` | `[test-gate]` | yes |
| `site_lane_gate` | `[site-lane]` | yes |
| `status_honesty` | `[status-honesty]` | yes |
| `level_promotion_gate` | — | **no** |
| `moap_coherence_gate` | — | **no** |
| `ruling_archive_question_gate` | — | **no** |
| `consolidation_rhythm` | — | **no** |
| `size_ratchet_gate` | — | **no** |
| **`orphan_ratchet`** | `orphan-ratchet:` | **no** |
| `company_network_isolation` | — | **no** |
| `file_scope_generated_paths` | — | **no** |
| `annual_report_import_ratchet` | — | **no** |

## Why the fail-closed fallback did not save it — this is the R15 part

The docstring's guarantee is explicit and, read alone, sound:

> FAIL-CLOSED, not fail-open: a stream with no recognisable verdict line degrades to the
> bounded tail (the old behaviour) … This function never returns an empty excerpt — a refusal
> that cannot say why it fired is one an operator learns to bypass.

The fallback is keyed on `if not verdict:` — **the selection being EMPTY, not the selection
being WRONG.** The pytest gate runs FIRST in the chain and, in this episode, PASSED. Its green
`[test-gate] ✓` lines are recognised vocabulary, so `verdict` was non-empty, so the tail
fallback could not fire. The selector is therefore fail-open in exactly the shape it was built
to close, and the condition that disarms it — the pytest gate passing — is the *normal* case
whenever any of the other nine gates is the one that reds.

It is worse than the empty excerpt the docstring feared. An empty excerpt tells a reader it
knows nothing. This one hands a reader six green ticks under the word REFUSED, and the natural
next inference is that the refusal is spurious — which is the inference that ends in a bypass,
and bypass is a WALL.

## Proposed repair, and its null control

Do **not** extend `VERDICT_MARKERS` with nine more prefixes: that is an instance fix for a class
defect (R10), and it decays the moment a thirteenth gate is added to the hook. The hook chain is
a sequence of `cmd || exit 1`, so the failing gate is knowable structurally rather than
lexically — capture per-gate output, or select the output of the gate whose exit was non-zero,
and the vocabulary stops needing to be maintained at all.

Whatever the shape, the falsifier is the same and must be run before the repair is recommended
(and note the null control): **a synthetic stream carrying a green `[test-gate] ✓ all targeted
tests green` line AND a red `orphan-ratchet:` block must excerpt the orphan block.** The null
control is the same stream with the orphan block removed — it must still excerpt the green line
and must NOT report a refusal, or the fix is just moving the blind spot.

## Not fixed here (SELF_INTERRUPT_DISCIPLINE)

Queued, not fixed on sight. The tick that found it was drawn on the RUNG-1d producer door and
the machine was not blocked — the landing completed once the real cause was reconstructed by
hand. The supply of harness findings is infinite; this one is filed because it taxes every
future landing in the repo, not because it stopped this one.
