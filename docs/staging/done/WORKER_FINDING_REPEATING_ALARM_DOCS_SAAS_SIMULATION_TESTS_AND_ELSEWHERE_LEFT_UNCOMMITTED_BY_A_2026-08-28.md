**Severity:** LATENT · **Lane:** H_harness

# The interactive seat stopped mid-work, and this is what it was holding

**Filed automatically by `background/seat_continuity.py`, not by a person.** The seat ran no
tool for **0.3h** and its process is gone. It did not stop on purpose: an
interactive session that finishes says so, and this one just stopped — which is the shape an
Anthropic API error leaves behind, four times now by the director's count.

This document exists so that nobody has to notice. It is a staged doc, so the next worker tick
draws it like any other work.

## What it had claimed

- Nothing was claimed. Whatever it was doing, it did not say.

## What it left in the tree, uncommitted

SOURCE paths only — the daemons' own output under `docs/observability/`, `site/` and the rest
of `tree_divergence.GENERATED_PREFIXES` is excluded, and so is `docs/staging/`, which is the
queue you are reading this from. This is the real state, and more reliable than anything the
session could have written about itself, because an API error is precisely the thing that
stops it writing.

- `docs/context-handshake-latest.md`
- `docs/status/LATEST.md`
- `docs/status/PROJECT_STATE.txt`
- `saas/reporting/annual_report.py`
- `simulation/run_phase4c_on_phase2b.py`
- `simulation/settlement_clocks.py`
- `tests/simulation/test_phase40a_pass_through.py`
- `tests/simulation/test_settlement_clocks.py`
- `tests/tools/test_run_value_cycle_ab.py`
- `tools/generate_value_arms_data.py`
- `tools/run_annual_report.py`
- `tools/run_frozen_baseline.py`
- `tools/run_value_cycle_ab.py`

## Where it had got to

- Last tools it ran, oldest first: Bash, Bash, Bash, Bash, Bash, Bash, Write, Read, Edit, Read, Write, Bash
- Tool calls this session: 718
- Last commit on the tree: `537a6f012 the drawn book should NOT carry a tariff_type, because the anchor says fixed is a minority`

## What to do with it — decide, do not just re-run

**Adopt** if the uncommitted paths above are coherent work part-way to something: read the
diff, finish it, commit it. That is the cheap outcome and the usual one.

**Discard** if the diff is a half-applied edit that no longer makes sense — `git checkout --`
the paths and take the claim from scratch. Say which you did.

Do NOT assume the work is wrong because the session died. The failure was in the transport,
not in the edit; the tree state above is exactly what a healthy session would have had at that
moment.

Archive to `docs/staging/done/` once the paths above are either committed or reverted.
