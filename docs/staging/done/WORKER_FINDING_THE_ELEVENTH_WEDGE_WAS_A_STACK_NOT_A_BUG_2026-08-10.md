# [WORKER-FINDING] The eleventh publish wedge was a STACK of three reds, and `-x` showed only the top one at a time

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-10 04:00–05:00Z, drawn as PUBLISH-GATE WEDGE RUNG 1 (priority zero).
**Wedge age at draw:** ~809 min, 81 consecutive gate failures, no pass at HEAD `d3bf9b739`.
**Disposition:** instances FIXED (this tick). The CLASS — a stacked red set behind `-x` — is QUEUED.
**Rank:** propose top-of-backlog.

## Observed, with evidence

The gate's log named four different blocking tests across six cycles on 2026-08-10:

```
02:51  tests/background/test_seat_guard_daemons.py::test_every_main_entrypoint_is_guarded
03:02  (same)
03:11  tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned
03:25  tests/design/test_atom_notes_store.py::test_declarations_match_the_store
03:38  (same)
03:47  tests/background/test_forward_attachment_register.py::test_live_tree_has_no_violations
```

That reads as flapping. It is not. `publish_gate_pytest_argv` passes `-x`, so each cycle reports
**the first** red in collection order and is blind to every red behind it. Run against a clean
checkout of HEAD `d3bf9b739` (`git archive HEAD | tar -x`, then `git init` + alternates +
`read-tree` — the same construction `_head_checkout`/`_make_checkout_a_repo` use), the four
tests above were **green**, and the true red set was three:

```
tests/design/test_atom_notes_store.py::test_declarations_match_the_store
  D19_belief_gap_is_distribution_only: map notes_rehomed=['origin_note'] != store fields []

tests/design/test_simplifications_store.py::test_map_within_size_ratchet_when_store_populated
  maturity_map.yaml is 430962 bytes, over the 409600-byte spine ratchet

tests/tools/test_capability_index.py::test_the_live_register_rules_on_every_live_orphan
  DECORATIVE REFERENT x4: company.core.{account_intelligence,adr_register,event_ledger,
  three_horizon_clv} nominate simulation.churn_journey, which imports nothing from company.core
```

Collection order is `tests/design/` before `tests/tools/`, so #3 could not have been seen from any
gate log until #1 and #2 were both fixed. Each of the eleven wedge ticks so far has been paying
one layer of a stack and reporting it as *the* cause.

## The two causes, and they are one class

**#1 and #2 are both `feedback_untracked_build_passes_local_green`.**

`D19`'s store file existed at `docs/design/simplifications/D19_belief_gap_is_distribution_only.yaml`
and was **untracked** — `git ls-files --error-unmatch` returned "did not match any file(s) known to
git". Its own `origin_note` (written by an earlier tick's H41 repair) correctly diagnoses the mint
path. That note was never committed either, so the diagnosis was as invisible as the fix.

The H41 records-tenant drain — `evidence: [...]` → `records_rehomed: [evidence]`, content moved to
the store's third tenant — had **already run in the working tree**: map 430,962 B at HEAD versus
301,156 B on disk, comfortably under the ratchet. `tools/migrate_atom_lists.py` was untracked, as
were ten store files and `tests/design/test_atom_records_store.py`; `background/supervisor.py`,
`tools/merge_atom_status.py` and `tools/generate_evidence_data.py` carried uncommitted hydration.

So the gate had been red for 13h on work that was **finished and sitting on the disk it was
failing against**. The lane verified green against a tree that had the fix; the gate judges a clean
checkout of HEAD; nothing compared the two.

**#3 is `feedback_park_reason_may_name_a_dead_mechanism`.** `fda6565e4` (KNIFE3 step 3) cut the
`simulation.churn_journey → company.core` crossing — correctly, it is a wall crossing. `a019ad96d`
(KNIFE4) then wrote a register nominating that already-severed module as the consumer that would
drive four `company.core` orphans. The nomination was stale the moment it was written.

## What was NOT true, and how I nearly filed it

My first checkout was `git archive | tar -x` with **no `git init`**. In it, `test_capability_index`
showed **three** reds — but two were `git ls-files returned rc=128 -- not a git repository`, an
artefact of my own harness, not of HEAD. Rebuilt as a real repo, only the DECORATIVE REFERENT red
survived. The first commit message of this tick says "3 reds that reproduce at pure HEAD"; that is
**wrong** — it is one. Recorded here rather than silently corrected, because the near-miss is the
point: a diagnostic checkout that differs from the gate's own construction manufactures reds, and
`feedback_verify_fork_preexisting_failure_claims` applies to *my own* baseline runs too.

## The gap

The wedge alarm reports "the failing test" (singular) from the `-x` log. It cannot count the stack,
so it cannot tell a one-line fix from a three-deep one, and every tick's estimate of "how close is
publishing to green" has been wrong by an unknown factor. Two candidate mechanisms:

1. **The wedge draw should run the gate WITHOUT `-x` once**, on the clean HEAD checkout, and report
   the whole red set to the drawing tick. Cost is one full uninterrupted suite per wedge episode —
   cheap against 81 failed cycles. `-x` stays for the live publish path, where fail-fast is right.
2. **A committed-vs-tree divergence check on the gate's own subject.** `tree_divergence.json` already
   counts diverged source files (347 at 03:52, oldest 14.88h) and the runner logs it — but nothing
   connects "the tree has 347 files HEAD lacks" to "the gate is red at HEAD", which is precisely the
   inference a human makes in ten seconds. A red gate whose red test passes in the working tree is
   an *uncommitted-work* signal and should say so by name.

(1) is the smaller build and closes the measurement gap; (2) closes the cause class. Recommend both,
(1) first.

## A FOURTH layer, found only by trying to land: `surgical_land` cannot land a site-data change

The first landing attempt was REFUSED — correctly, by the tool's own design — with the site-lane
gate red on the resulting tree:

```
FAILED site/proof/test_predictions_ledger_can_fail.py::test_live_surface_renders_the_derived_headline
FAILED site/proof/test_predictions_ledger_can_fail.py::test_live_surface_states_the_horizon_and_names_the_stale_snapshot
[site-lane] ❌ SITE TESTS FAILED -- COMMIT REFUSED.
```

These two are **not** caused by the change, and they are **not** a real defect in the surface. They
pass in the working tree (`35 passed`) and fail in every clean extract of HEAD (`2 failed, 584
passed`), because they compare the published `site/data/proof.json` against a ledger the generator
rebuilds from `site/state/live_decisions_*.json` — which are **untracked**, so no extract has them.

Both extract builders overlay untracked data from the same named list:

```
process_run_complete.py:1273   UNTRACKED_DATA_OVERLAY = ("sim/cache", "node_modules")
surgical_land.py:205           _overlay_untracked_data(...)
```

`site/state` is not on it. The publish gate never noticed because it runs `tests/` only; the
site-lane gate runs `site/`, and only ever ran in the real working tree — until `surgical_land`
started running the same hook against an extract. So the tool built to make partial commits legal
**cannot be used for any commit that broadly-triggers the site lane**, which is every commit
touching `site/data/**`.

This is fail-CLOSED (it refuses valid commits rather than admitting bad ones), so it is safe, but it
is a dead end on the one path priority-zero work needed. Two candidate fixes, neither taken here
because both change a shared gate constant and deserve their own R15 pass:

- add `site/state` to the overlay — but it holds TRACKED files too (`live_portfolio.json`), and a
  whole-dir symlink would shadow committed truth with live state, which is the exact property the
  gate's subject ruling exists to protect. It would have to be a file-level overlay of the untracked
  members only.
- make the two live-surface tests skip loudly when the decision log is absent, the way
  `test_the_note_tenant_is_populated_precondition` already does for an empty store. That keeps the
  assertion where the data exists and stops it asserting where it structurally cannot.

Recommend the second: the test is making a claim about a machine's live state, and an extract has no
live state to make it about. Filing as an atom rather than fixing on sight (SELF_INTERRUPT_DISCIPLINE).

## Fixed in this tick

- `d3bf9b739`+1 — the H41 records-tenant bundle landed via `tools/surgical_land` (14 paths, gate run
  against the tree the commit would create). Clears reds #1 and #2.
- `d3bf9b739`+2 — the four `company.core` rows re-dispositioned to `none:company.core`. This is not a
  mute: `_referent_findings` REFUTES a `none:` claim if any module imports the package, so the escape
  is itself checked. Clears red #3.

## Still open

`docs/design/ORPHAN_DISPOSITION_REGISTER.md` was written by KNIFE4 against a pre-KNIFE3 import graph.
Four rows are proven stale; the register has 258. Nothing has swept the rest. Proposed as an atom:
re-derive every `unhooked` referent from the live import graph rather than trusting the ruling text.
