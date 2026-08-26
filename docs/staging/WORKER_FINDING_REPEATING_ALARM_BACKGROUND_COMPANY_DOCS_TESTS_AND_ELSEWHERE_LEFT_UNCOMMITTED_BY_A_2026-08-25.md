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
- `_r11_tmp.mjs`
- `background/pull_forward_proposal.py`
- `company/pricing/value_based_renewal.py`
- `docs/context-handshake-latest.md`
- `docs/design/PB3_book_growth_as_earned_outcome_exit_d_DISCOVER.md`
- `docs/design/simplifications/EP13_adapter_carbon_intensity.yaml`
- `docs/design/simplifications/FUT2_pull_forward_proposal.yaml`
- `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`
- `docs/direction/DIRECTION.yaml`
- `docs/direction/decisions.jsonl`
- `docs/status/LATEST.md`
- `head.txt`
- `tests/architecture/test_static_quality_ratchet.py`
- `tests/background/test_blocked_atom_visibility.py`
- `tests/background/test_derived_artefact_register.py`
- `tests/background/test_file_api.py`
- `tests/background/test_producer_starvation_draw.py`
- `tests/background/test_publish_decoupling_exit.py`
- `tests/background/test_publish_gate_subject_is_head.py`
- `tests/background/test_pull_forward_proposal.py`
- `tests/background/test_rest_ladder_isolation.py`
- `tests/background/test_seat_work_in_hand.py`
- `tests/company/pricing/test_value_based_renewal.py`
- `tests/design/test_atom_notes_store.py`
- `tests/simulation/test_drawn_smart_meter.py`
- `tests/simulation/test_phase27b_ccl.py`
- `tests/simulation/test_policy_cost_coverage.py`
- `tests/simulation/test_settlement_fold.py`
- `tests/tools/test_couple_pb3_book_growth.py`
- `tests/tools/test_couple_value_based_pricing.py`
- `tests/tools/test_head_green_census.py`
- `tests/tools/test_map_assertion_provenance.py`
- `tests/tools/test_model_tier_report.py`
- `tests/tools/test_site1_proof_crawlability.py`
- `tools/couple_pb3_book_growth.py`
- `tools/couple_value_based_pricing.py`
- `tools/head_green_census.py`
- `tools/revenue_sanity_check.py`

## Where it had got to

- Last tools it ran, oldest first: Bash, Bash, Read, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, ToolSearch
- Tool calls this session: 138
- Last commit on the tree: `7cdd8e66c Auto-process run complete: report + LATEST.md + site/ (git=bf9d30c14, net=£1,264,955)`

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
- **2026-08-26** — still live. 1 repeats over 0.5h without the state changing. No second document filed: this condition already has one.
