# [WORKER-FINDING] The ruff ratchet is red at HEAD, and only a commit that happens to select it can see that (2026-08-14)

**Severity:** LATENT · **Lane:** H_harness · **Status:** measured and bounded, not repaired —
finding *which* three violations are the new ones is a bisect, and this tick queued it rather than
spending the drawn work on it (SELF_INTERRUPT_DISCIPLINE).

Found while landing the W2 home-mover repair: `tests/architecture/` was run as a pre-flight and came
back with two failures that had nothing to do with the change.

## The measurement, `observed-with-evidence`

`tests/architecture/test_static_quality_ratchet.py` freezes a per-rule ruff census (frozen
2026-08-06, ruff 0.15.16). Counted this tick with the test's own method (`ruff check .
--output-format=json`, counted by code) in three trees:

| tree | E402 | F811 | I001 |
|---|---|---|---|
| frozen baseline | 193 | 95 | 1376 |
| `HEAD~1` = `0f44bd4ec` | **194** | **96** | **1377** |
| `HEAD` = `b5fa18d3a` | **194** | **96** | **1377** |
| working tree | **194** | **96** | **1377** |

Identical in all three, so: **+1 on each of three rules, already on HEAD, and it entered before
`0f44bd4ec`** — not from this tick's work, and not from working-tree dirt. Two tests are red:
`test_ruff_no_rule_exceeds_baseline` and `test_ruff_baseline_matches_frozen_census`.

## The part that is a finding rather than a chore

A red static control on HEAD is not, by itself, interesting. What is: **most commits cannot see it.**
The pre-commit gate selects test files by the name stem of the changed paths, so a commit touching
`simulation/` or `background/` never selects `test_static_quality_ratchet.py`. The two landings this
tick both passed a full surgical gate against the tree they created while this red sat in that same
tree, untouched and unreported. It is visible only to a commit that happens to touch an
`architecture`-stemmed path, or to the full-suite publish run — which is why it has survived at least
one prior commit.

That is the same shape as the no-caller class this project has already filed: a control that runs
only when something unrelated happens to summon it.

## What the repair is, and is not

The ratchet's own rule, in its own file: *"Fix the new violations — do not raise the baseline."* So
the work is to find the three offending sites, not to re-freeze. The census stores counts and not
locations, so the cheapest route is a bisect over the commits since 2026-08-06 with the three-code
count as the predicate; this finding narrows the interval's upper end to `0f44bd4ec` and no further.

## What is NOT claimed

- No claim about which files carry the new violations. Checked and cleared: none of the changed or
  untracked `.py` files in the tree this tick carries an E402 or F811 at all.
- No claim that publishing is currently wedged by this. Publishing was observed healthy at
  01:03 UTC (`[process_run] Committing and pushing (net=£1,547,113)`); the separate `commit_refused`
  at 01:10 cites a different test, and the wedge-state file cites a third.
- No claim that the count is the only drift: only E402, F811 and I001 were compared.

**Evidence:** `tests/architecture/test_static_quality_ratchet.py` · trees `0f44bd4ec`, `b5fa18d3a`
and the working tree, each counted with the test's own command · `docs/observability/sim-runner-log.md`
(the 01:03 publish).
