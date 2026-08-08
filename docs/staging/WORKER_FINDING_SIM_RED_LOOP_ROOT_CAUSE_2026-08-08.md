# [WORKER-FINDING] Sim red loop — root cause: uncommitted half-refactor, not any of the three suspects (2026-08-08)

**Answers:** `DIRECTOR_PRIORITY_SIM_RUNNER_TRIAGE_2026-08-08.md`. Triage done, loop cured, evidence below.

## Root cause (observed-with-evidence, R9)

```
File "/home/rich/synthetic-enterprise/simulation/arrears_engine.py", line 275, in payment_outcome
    if segment in _IC_SEGMENTS:
NameError: name '_IC_SEGMENTS' is not defined
```

Reproduced directly (the runner does not capture its child's stderr — `subprocess.run` inherits
fd 1/2, which point at a socket, so every traceback in this incident was discarded unread; that is
why eight consecutive failures logged `rc=1` and nothing else).

`_IC_SEGMENTS = ("ic", "I&C")` was added in `a1c7b4b50` together with both of its use sites
(`payment_method` line 208, `payment_outcome` line 275). **It was deleted in the WORKING TREE and
never committed** — `git show HEAD:simulation/arrears_engine.py` still contains the definition at
line 62. An abandoned in-flight refactor (`W2_sme_segment_case_normalisation`) replaced the
definition line with a new `_CORPORATE_METHODS` constant and never migrated the two readers.

**This is why landing the stranded build did not cure it.** The defect never existed in git history
on any branch — only in the local tree the runner executes from. All three offered suspect classes
(week-merge × runtime, cache staleness, run-marker backlog) are refuted: the failure is a plain
undefined name, deterministic, ~180s in, at the first I&C bill to reach the corporate rail.

## Fix applied

`simulation/arrears_engine.py` — restored `_IC_SEGMENTS` with a comment recording why it must not be
narrowed without migrating both readers; pointed the corporate-rail method test at the new
`_CORPORATE_METHODS` constant (identical tuple, provably zero behaviour change) so it is not an
orphan constant reading as enforcement.

Behaviour is now exactly HEAD's. No baseline/R13 change.

## Evidence

- `tests/simulation/test_arrears_engine.py` — **50 passed**.
- Direct smoke: `payment_method` resolves resi→direct_debit, sme→bacs, ic/I&C→chaps;
  `payment_outcome` returns on the I&C bacs arm for both spellings.
- **Full run to completion, RC=0** — `python3 -m saas.reporting.annual_report` wrote a 377,009-char
  10-year report and `ledger_latest.json` (3,262,596 events). Zero `NameError`/`Traceback` in stderr.
  This is a complete run, not merely progress past the 180s failure point.

## Registered, NOT built: the stranded W2 build

Two untracked modules are committed alongside this fix **as quarantined dead code, so a broad-add
sweep cannot lose them** — they are imported by nothing:

- `simulation/segment_vocabulary.py` — canonical segment vocabulary + `normalise_segment()`.
- `simulation/sme_payment_behaviour.py` — Ofgem-D6/DBT-anchored SME outcome model.

Both import cleanly. **Neither is wired into any production path, neither has tests, and
`tools/segment_case_guard.py` — the R10 class-closure guard its own docstring promises — does not
exist.** Do not read their presence as coverage.

The defect they target is real and still live, confirmed in this turn's smoke test:
`payment_method("SME", ...)` returns `direct_debit` — a real SME bill (stored canonically as `"SME"`
by `saas/customers.py`) matches neither `== "sme"` nor `_IC_SEGMENTS`, so C5/C6 are billed as
households.

**Not fixed here, deliberately.** Completing W2 moves SME customers onto a corporate rail and changes
SME bad debt — a BASELINE change under R13, needing its own tests, an R15 mutation proof, the missing
guard, and a population-level before/after. That is a BUILD, not a triage, and landing it unverified
inside a red-loop fix would have been the worse error. Proposed as an atom; the case bug has been
latent since `a1c7b4b50` (2026-07-04) and is not urgent relative to the loop.

## Class defect worth mechanising (queued per SELF-INTERRUPT DISCIPLINE, not fixed on sight)

`background/sim_runner.py::run_simulation` calls `subprocess.run` with no `capture_output`, so the
one artefact that identifies any failure is written to a socket and lost. Eight failures over ~60
minutes produced no diagnosable evidence, and the director had to spend attention flagging it.
**R5 says an alert carries its diagnostic payload; this one cannot.** Suggested: capture stderr, tee
the last N lines into `sim-runner-log.md`, and put them in the failure NTFY.

— Worker, scheduled tick 2026-08-08.
