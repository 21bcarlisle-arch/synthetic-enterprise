# [WORKER-REPORT] OPS9 — every finding in the staging root now carries a machine-readable severity (2026-08-12)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** the pass is complete and its control
is landed; nothing here is owed.

**Atom:** `OPS9_finding_severity_field` **L0 → L2**, self-certified into
`gate_authorizations.jsonl` (R16). Deliverable 1 of the WORK THIS CREATES block in
`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`.

## What landed

`background/finding_severity.py` reads one header line off a document —

    **Severity:** LATENT · **Lane:** H_harness

— and returns the value **with its lane**, because clause 2's refusal is lane-scoped and a
severity without a lane cannot be acted on. `tests/background/test_finding_severity.py` holds
19 named tests.

## The pass, counted from the filesystem

`python3 -m background.finding_severity`:

    documents (from filesystem): 121
      BLOCKING     35
      LATENT       73
      RECORDED     13
      UNCLASSIFIED 0

Exit criterion 2 is met against the glob, never a hand-kept list. Machine doorbells
(`run_complete_*`, `run_pending_*`, `from_rich_*`) are excluded by exact prefix and named as a
population boundary in the module: they are written and archived by the machine on every sim
run, so requiring a severity on them would make the zero-unclassified control flap red on
ordinary operation, and an alarm that fires on normal behaviour is one nobody reads.

## Where the blockers are

    C_customer_ops         2     E_finance_treasury     1     W2_customer_generator  1
    D_billing_metering     1     H_harness             29     W4_the_wall            1

29 of the 35 sit in `H_harness`, which is the ruling's own measurement showing up again: the
two largest families it counted — controls that cannot fail, and measurements that mirror the
thing they measure — are harness families. When `OPS11` lands, the next `H_harness` level-raise
must first repair or explicitly accept each of those 29. That is the intended consequence, not
a side effect, and the discharge path is cheap: repair, or record the limitation and accept it.

## The classification rule I applied, stated so it can be argued with

BLOCKING where the document's own text says a **currently relied-on control's verdict may be
wrong, or a currently published figure may be wrong** — a control that passes bad work, a
measure that mirrors its own subject, a guard that reads GREEN on missing input. LATENT where
the instance is repaired and only the class is open, or where the defect degrades a diagnostic
rather than a verdict. RECORDED for receipts and reports of landed work with nothing owed.

A false-negative here is the anti-pattern clause 2 exists to forbid, so the rule is
**checkable, not merely written**: `--by-construction` names any non-BLOCKING document whose
own text says an instrument, a control or a published figure is wrong. It reports **0** after
this pass. It stands down only on a header block carrying a repair/discharge word — clause 2's
own two releases — and the anti-loophole is the scope: the word must sit in the header block
where the next reader meets it, never in a retrospective paragraph forty lines down.

One document self-classified before this atom existed
(`WORKER_FINDING_ONE_HOMES_CERTIFICATE_...`, "SEVERITY: BLOCKING, DISCHARGED ON LANDING") and
its own reading was honoured: discharged by the repair in the same commit, residue LATENT.

## R15, both ways

Two mutations, each loaded from a **copy** of the module under a fresh name (editing a source
file mid-pytest corrupts `inspect.getsource`, and a same-length mutation can survive its own
restoration through the `.pyc` cache — both are filed findings in this repo):

- **fail-open** — the missing-header branch returns `LATENT` instead of `UNCLASSIFIED`. Kills
  `test_a_missing_header_reads_unclassified_never_latent`. The clean input still passes under
  it, which is what makes the kill informative.
- **lane dropped** — the successful parse returns the severity without its lane. Kills
  `test_the_parse_returns_the_lane_beside_the_severity`.

The mutation loader asserts its own anchor is unique, so a no-op mutation cannot make its test
pass for the wrong reason.

## What this does NOT do

Nothing refuses anything yet. `OPS11` (lane-scoped refusal at the level-record and the commit
gate) and `OPS12` (blockers ahead of the disposition queue) are the mechanisms that read this
parse; both are minted and both depend on this atom. `OPS10` (class consolidation) will
supersede many of the 121 individuals — the severity header survives the move, since the parse
is per-document and counted from the filesystem.
