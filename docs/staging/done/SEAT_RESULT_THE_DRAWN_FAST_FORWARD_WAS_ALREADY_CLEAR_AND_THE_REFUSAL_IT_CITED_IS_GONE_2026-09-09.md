**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `two-rival-copies-of-the-stale-copy-refusal-hold-the-tree-behind-origin-and-the-publisher-dark`) · **Class:** `publish_gate_and_wedge`

# The drawn fast-forward was already clear, the two "rival copies" are byte-identical, and the refusal the wedge cited no longer exists at HEAD

**2026-09-09, scheduled tick. PREMISE SPENT — measured at draw time, not assumed. The claim is
released; no work was redone.**

---

## The premise check, four measurements

The item's own finish condition was `git rev-list --count HEAD..origin/main == 0` and a non-null
`last_clean_publish`. The first half is already met and the second half's stated cause is gone.

| What the item said | Measured now |
|---|---|
| "`git rev-list --count HEAD..origin/main`" is non-zero, 27.1 hours dark | **0.** `HEAD == origin/main == 16f6684513f7b28a54ebbaad205e99c52e89e454`; `origin/main..HEAD` is also 0. |
| `tools/stale_copy_refusal.py` working copy is +180/-16 against HEAD, origin's is +98/-10 | **Identical.** `git diff HEAD` and `git diff origin/main` on that path are both empty. |
| `tests/tools/test_stale_copy_refusal.py` is +190 here, +62 on origin | **Identical.** Same, empty both ways. |
| the level-promotion gate refuses the publish commit | **`python3 -m tools.level_promotion_gate` → rc 0.** |

The doorbell's own premise check was right: `a9f3288c8` and `0caf9ab52` are ancestors of
`origin/main`, and the repair landed by another route while the item was queued.

## The refusal that was still on the surface, and why it is stale

`.publish_gate_state.json` carries `last_clean_publish: null`, `wedge_since` older than every commit
in the stretch, and a `liveness_surface_refusal` recorded at `a0a62f918`:

```
[scope-evidence] ❌ COMMIT REFUSED -- 1 atom(s) CLAIM A LEVEL on evidence that is not in the tree
  W2_32_the_billing_and_commercial_axes_are_measured_against_the_demand_sample (level_current 2)
      NOT IN GIT:  tools/billing_axis_coverage.py
      NOT IN GIT:  tests/tools/test_billing_axis_coverage.py
```

Both paths are in `git ls-tree -r HEAD` as of `16f668451`. The refusal is a record of a state one
commit old, and the level-promotion gate agrees: rc 0.

**So the wedge state is a stale artefact, not a live blocker.** `wedge_since` and
`last_clean_publish: null` describe what happened up to `a0a62f918` and nothing that is true of
`16f668451`. They clear on the next publish attempt rather than by a repair — and per the rule that
publishing the newest artefact unsatisfies every control keyed to the staleness it fixes, the honest
move is to leave the state alone and let the next publisher run write over it, not to hand-clear it.

## What this leaves

Nothing to do on the drawn item. The claim is released rather than worked, which is the whole point
of a premise check that runs at draw time. **The one thing worth carrying forward**: this item was
drawn twice — 11.8 hours ago under a different framing, and again this turn under a more specific one
naming the two paths. Both times the underlying repair had already landed. A re-draw that names its
subject more precisely is not evidence the subject is still live; the ledger fact that the cited
commits are ancestors is, and it was in the doorbell both times.
