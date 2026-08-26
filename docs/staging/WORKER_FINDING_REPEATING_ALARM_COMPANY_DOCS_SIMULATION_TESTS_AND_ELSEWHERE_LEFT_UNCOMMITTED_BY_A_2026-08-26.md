**Severity:** LATENT · **Lane:** H_harness

# The interactive seat stopped mid-work, and this is what it was holding

**Filed automatically by `background/seat_continuity.py`, not by a person.** The seat ran no
tool for **0.4h** and its process is gone. It did not stop on purpose: an
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

- `CLAUDE.md`
- `PRIORITIES.md`
- `company/crm/churn_model.py`
- `company/interfaces/renewal_rate_chain.py`
- `company/pricing/renewal_rate_chain.py`
- `company/pricing/value_based_renewal.py`
- `docs/context-handshake-latest.md`
- `docs/design/PB3_book_growth_as_earned_outcome_exit_d_DISCOVER.md`
- `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`
- `docs/direction/DIRECTION.yaml`
- `docs/direction/decisions.jsonl`
- `docs/status/LATEST.md`
- `docs/status/PROJECT_STATE.txt`
- `simulation/run_phase2b.py`
- `tests/company/pricing/test_the_arm_reaches_its_own_segment.py`
- `tests/simulation/test_policy_cost_coverage.py`

## Where it had got to

- Last tools it ran, oldest first: Bash, Bash, Bash, Bash, Bash, Bash, Bash, Write, Bash, Bash, Edit, Bash
- Tool calls this session: 219
- Last commit on the tree: `d8ae96730 the churn-roster aggregation collapsed declared blanks to zero, so "no concentration" was the one answer it could always give`

## What to do with it — decide, do not just re-run

**Adopt** if the uncommitted paths above are coherent work part-way to something: read the
diff, finish it, commit it. That is the cheap outcome and the usual one.

**Discard** if the diff is a half-applied edit that no longer makes sense — `git checkout --`
the paths and take the claim from scratch. Say which you did.

Do NOT assume the work is wrong because the session died. The failure was in the transport,
not in the edit; the tree state above is exactly what a healthy session would have had at that
moment.

Archive to `docs/staging/done/` once the paths above are either committed or reverted.
