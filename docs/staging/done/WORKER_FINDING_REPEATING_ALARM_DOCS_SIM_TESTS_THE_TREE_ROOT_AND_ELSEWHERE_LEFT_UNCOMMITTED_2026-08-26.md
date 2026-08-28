**Severity:** LATENT · **Lane:** H_harness

> **DISPOSITION 2026-08-26, worker tick — ADOPTED IN PART, NOT YET ARCHIVABLE.** The EP13
> carbon-intensity half of the path list below was read, verified and committed as
> `ad5961b24` (pushed; origin/main confirmed at that SHA). Adopt, not rebuild: the diff was
> coherent and complete, 112 tests pass across its three test files, and the regenerated feed
> was checked byte-identical to the code's own output before landing.
>
> **Committed and now clean:** `sim/grid_carbon_intensity.py`, `sim/elexon_fuel_outturn.py`,
> `tools/generate_grid_intensity_feed.py`, `tests/sim/test_grid_carbon_intensity.py`,
> `tests/sim/test_elexon_fuel_outturn.py`,
> `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`,
> `docs/design/simplifications/EP13_adapter_carbon_intensity.yaml`.
> Already clean by other hands: `_r11_tmp.mjs`, `docs/design/maturity_map.yaml`,
> `docs/direction/DIRECTION.yaml`, `docs/direction/decisions.jsonl`, `head.txt`.
>
> **STILL UNCOMMITTED, and deliberately left — each belongs to a lane that is not EP13, so
> sweeping them into a carbon commit is the pathspec mistake this project has already made:**
> `CLAUDE.md`, `PRIORITIES.md`, `docs/context-handshake-latest.md`,
> `docs/design/PB3_book_growth_as_earned_outcome_exit_d_DISCOVER.md` (untracked),
> `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`, `docs/status/LATEST.md`
> (staged by the publish lane), `docs/status/PROJECT_STATE.txt`,
> `tests/simulation/test_policy_cost_coverage.py` (untracked; belongs with
> `WORKER_FINDING_THE_POLICY_COST_CLAMP_TESTS_..._2026-08-24.md`).
>
> Archive this file only when that second list is committed or reverted. Do not re-read the
> EP13 diff — it is landed.

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
- `docs/context-handshake-latest.md`
- `docs/design/PB3_book_growth_as_earned_outcome_exit_d_DISCOVER.md`
- `docs/design/maturity_map.yaml`
- `docs/design/simplifications/EP13_adapter_carbon_intensity.yaml`
- `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`
- `docs/direction/DIRECTION.yaml`
- `docs/direction/decisions.jsonl`
- `docs/status/LATEST.md`
- `docs/status/PROJECT_STATE.txt`
- `head.txt`
- `sim/elexon_fuel_outturn.py`
- `sim/grid_carbon_intensity.py`
- `tests/sim/test_elexon_fuel_outturn.py`
- `tests/sim/test_grid_carbon_intensity.py`
- `tests/simulation/test_policy_cost_coverage.py`
- `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`
- `tools/generate_grid_intensity_feed.py`

## Where it had got to

- Last tools it ran, oldest first: Bash, Bash, Bash, Write, Edit, Bash, Bash, Read, Bash, Read, Bash, Bash
- Tool calls this session: 497
- Last commit on the tree: `61b8250fc the delivery lane's 'has this work moved?' signal is a constant: every Lane 0 claim is recorded with no paths, so it is recycled and falsely alarmed 100 minutes after it is drawn`

## What to do with it — decide, do not just re-run

**Adopt** if the uncommitted paths above are coherent work part-way to something: read the
diff, finish it, commit it. That is the cheap outcome and the usual one.

**Discard** if the diff is a half-applied edit that no longer makes sense — `git checkout --`
the paths and take the claim from scratch. Say which you did.

Do NOT assume the work is wrong because the session died. The failure was in the transport,
not in the edit; the tree state above is exactly what a healthy session would have had at that
moment.

Archive to `docs/staging/done/` once the paths above are either committed or reverted.
