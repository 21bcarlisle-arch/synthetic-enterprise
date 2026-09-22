**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_and_landing_doors`

# PRE-REGISTRATION — is the publish path's stale-producer refusal actually ARMED?

A verification of a landed control, filed before the measurement. It becomes BLOCKING only if a
mutation survives — and the result note beside it records that one half did.

**Written 2026-09-22, BEFORE running any mutation.** Filed by the delivery seat holding
`restore-the-six-live-reverts-before-anything-regenerates-from-them`.

## Why this measurement exists

The drawn item asked for two things. The first — restore the six live reverts — is **spent**: the
two copies it names by path (`simulation/net_new_acquisition.py`,
`tools/generate_value_arms_data.py`) are byte-identical to HEAD on the shared tree, so the revert
they would have committed no longer exists.

The second — close the publish half of the door — is **landed at `cc5cc0032`**
(`background.process_run_complete.refuse_stale_producers`, `stale_copy_refusal.refused_to_run`,
`producer_refusal`, `StaleProducer`, and
`tests/background/test_the_publish_path_refuses_a_stale_producer.py`).

The item's third clause is the one nobody has discharged: *"a mutation that neuters the refusal
reds a control rather than a sibling assertion."* A landed control is not an armed control. This
project's own catalogue says so in three separate shapes — **a green mutation on a refusal guard
means the guard is UNREACHABLE**; **a mutation caught by a DIFFERENT leg than the one written for
it is the flattering reading**; and **a control that stubs its own subject proves the stub**.

That last one is the live risk here, and it is why this is worth measuring rather than asserting.
Three of the six controls in that file **monkeypatch `scr.refused_to_run`** — the very function
whose behaviour is the claim. If the only controls that die under mutation are the monkeypatched
ones, the suite proves its own stubs and the production guard is ungraded.

## The mutations, and what I predict BEFORE running them

Each mutation is applied in this ISOLATED worktree only, one at a time, then reverted. I record
which test IDs red — not merely that something red, because the leg that catches it is the finding.

| # | Mutation | Predicted killer | Predicted to SURVIVE |
|---|---|---|---|
| **M1** | `refused_to_run` returns `{}` unconditionally — the guard refuses nothing | `test_the_whole_producer_partition_is_reachable_in_one_tree` (the `stale in refused` leg) | the three monkeypatched controls, which never call the real function |
| **M2** | `refused_to_run` returns every path — the guard refuses everything | same partition test (the `dirty not in refused` and `clean not in refused` legs) | the same three |
| **M3** | `_site_producers` returns `{}` — the register is empty, so nothing is ever graded | `test_the_producer_register_is_the_publish_paths_own_imports` (the `live` half) | the partition test, which passes paths in directly |
| **M4** | `generate_dashboard_json` calls `_generate_dashboard_json` directly, without the `refuse_stale_producers` wrapper — the guard is unwired from production | `test_the_entry_point_holds_the_refusal_over_every_return_below_it` | everything else |

**The prediction that matters, stated so it can be refuted:** I predict **all four die**, and that
**M3 and M4 die on a leg that does NOT monkeypatch `refused_to_run`** — i.e. the production wiring
is graded by something other than its own stub.

**What would refute me and become a BLOCKING finding:** any mutation that survives; or M4 dying
only because a monkeypatched control noticed, which would mean the production entry point is held
up by a test of a stand-in.

**A second, cheaper prediction I am less sure of:** M1 will ALSO be caught by a control outside
this file — some caller elsewhere in the tree. I predict **no**: I expect this file to be the only
reader. If a sibling suite catches it, that is a coverage fact worth having and I will record it.

## What I already know and am NOT predicting

That the census returns 17 paths on the shared tree rather than empty. Those are other lanes' live
working copies, and `stale_copy_refusal`'s own docstring establishes why that is the normal
resting state of a shared checkout rather than a defect: `surgical_land` never writes the working
tree, so a landed commit leaves every other lane's copy clock-stale by construction. That is a
separate question from this one and it is recorded in the result note, not here.
