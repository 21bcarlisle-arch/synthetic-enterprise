**Severity:** LATENT · **Lane:** H_harness

# The interactive seat stopped mid-work, and this is what it was holding

**Filed automatically by `background/seat_continuity.py`, not by a person.** The seat ran no
tool for **0.5h** and its process is gone. It did not stop on purpose: an
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
- `_r11_tmp.mjs`
- `background/pull_forward_proposal.py`
- `background/seat_work_in_hand.py`
- `docs/context-handshake-latest.md`
- `docs/design/BLOCKED_ATOM_VISIBILITY.md`
- `docs/design/PB3_book_growth_as_earned_outcome_exit_d_DISCOVER.md`
- `docs/design/maturity_map.yaml`
- `docs/design/simplifications/FUT2_pull_forward_proposal.yaml`
- `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`
- `docs/status/LATEST.md`
- `docs/status/PROJECT_STATE.txt`
- `head.txt`
- `sim/elexon_fuel_outturn.py`
- `sim/grid_carbon_intensity.py`
- `tests/architecture/test_static_quality_ratchet.py`
- `tests/background/test_file_api.py`
- `tests/background/test_producer_starvation_draw.py`
- `tests/background/test_publish_decoupling_exit.py`
- `tests/background/test_publish_gate_subject_is_head.py`
- `tests/background/test_pull_forward_proposal.py`
- `tests/background/test_rest_ladder_isolation.py`
- `tests/background/test_seat_work_in_hand.py`
- `tests/design/test_atom_notes_store.py`
- `tests/sim/test_elexon_fuel_outturn.py`
- `tests/sim/test_grid_carbon_intensity.py`
- `tests/simulation/test_phase27b_ccl.py`
- `tests/simulation/test_policy_cost_coverage.py`
- `tests/simulation/test_settlement_fold.py`
- `tests/tools/test_couple_pb3_book_growth.py`
- `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`
- `tests/tools/test_head_green_census.py`
- `tests/tools/test_map_assertion_provenance.py`
- `tests/tools/test_model_tier_report.py`
- `tests/tools/test_site1_proof_crawlability.py`
- `tools/couple_pb3_book_growth.py`
- `tools/generate_explore_carbon.py`
- `tools/generate_grid_intensity_feed.py`
- `tools/head_green_census.py`
- `tools/revenue_sanity_check.py`

## Where it had got to

- Last tools it ran, oldest first: Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash
- Tool calls this session: 120
- Last commit on the tree: `f1ac32932 EP13's Expert Hour was taken and it did not pass: three of its findings were wrong on the customers' own page, and L3 is refused for a reason the finding count does not name`

## What to do with it — decide, do not just re-run

**Adopt** if the uncommitted paths above are coherent work part-way to something: read the
diff, finish it, commit it. That is the cheap outcome and the usual one.

**Discard** if the diff is a half-applied edit that no longer makes sense — `git checkout --`
the paths and take the claim from scratch. Say which you did.

Do NOT assume the work is wrong because the session died. The failure was in the transport,
not in the edit; the tree state above is exactly what a healthy session would have had at that
moment.

Archive to `docs/staging/done/` once the paths above are either committed or reverted.

## Still live
- **2026-08-26** — still live. 1 repeats over 0.4h without the state changing. No second document filed: this condition already has one.
