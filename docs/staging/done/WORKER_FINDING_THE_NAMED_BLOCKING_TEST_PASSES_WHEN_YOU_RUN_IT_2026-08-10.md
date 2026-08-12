# [WORKER-FINDING] The wedge alarm names a blocking test that PASSES when you run it

**Severity:** LATENT · **Lane:** H_harness

**Status:** wedge closed (`6156b8b97`, pushed). The finding is the class, not the instance.
**Class:** fail-silent responder trap / uncommitted-repair. Sibling of "untracked build = local-green".

## What happened

`.publish_gate_state.json` had wedged publishing for ~23h with one entry:

```
"blocking_tests": ["FAILED tests/tools/test_capability_index.py::test_the_live_register_rules_on_every_live_orphan"]
```

The obvious first move — run the named test — reports:

```
1 passed, 1 warning in 3.55s
```

So the responder's cheapest, most natural check **exonerates the named cause**, and sends them
looking for a second cause that does not exist. Eighty-one `run_complete_*.md` markers piled up
behind it.

## Why the test passes locally and fails in the gate

`tools/capability_index.py` reads the **working tree**; the gate reads **HEAD**. The repair for
the four findings — `company.core.{account_intelligence,adr_register,event_ledger,three_horizon_clv}`
nominating `simulation.churn_journey`, which imports nothing from `company.core`, replaced with an
honest `none:company.core` — had been **made and never committed**. Every local run read the fix.
Every gate run read HEAD's unrepaired register.

Measured, in a clean `git archive HEAD` extract:

| tree | `disposition_findings` |
|---|---|
| working tree | 0 |
| HEAD | 4 |
| HEAD + the one uncommitted patch | 0 |

That third row is the proof the patch alone was the whole cause — worth stating because the same
extract *also* showed two unrelated failures (`test_cli_exit_codes_distinguish_clean_from_could_not_run`,
`test_live_repo_index_is_healthy_and_substantial`) which are **artefacts of the extract itself**:
`git archive` output has no `.git`, so `git ls-files` returns rc=128 and the coverage oracle is
unavailable. A responder who extracts HEAD to reproduce will see three reds and can easily chase
the two that only exist because of how they reproduced it.

## The general shape

> When a control reads the working tree and its gate reads HEAD, an uncommitted repair makes the
> control **green for the person diagnosing it and red for the machine**. The alarm is accurate and
> the reproduction is misleading — the worst combination, because it discredits the alarm.

This is the same asymmetry already recorded for the capability index reading the working tree, but
the operational consequence is new: it is not that the index is fail-open, it is that **the wedge
responder's reproduction step is the thing that fails**.

## What would have caught it sooner

The 12:32 recommendation the director ratified today
(`DIRECTOR_NOTE_SUSPECT_LIST_REDERIVATION_2026-08-10.md`) — re-derive the suspect list from the
gate's ACTUAL red and its blame trail rather than a frozen recency set — is the right fix and this
is another datum for it. One addition worth folding into that mint when it draws:

**a suspect list for a working-tree-reading control must carry the tree it was evaluated against.**
"FAILED <test>" is not actionable on its own; "FAILED <test> at HEAD `<sha>`, passes in the working
tree, `git status` shows its input modified-uncommitted" names the fix in the alarm itself. The
diff between the two trees, restricted to the control's declared inputs, IS the suspect list.

## Cheap standing control (proposed, not built)

At publish time, for each control the gate runs that reads the working tree, assert
`working_tree_verdict == head_verdict`, and on divergence emit the modified-uncommitted paths among
that control's inputs. It fails on its own named defect (this incident reproduces it exactly), which
is what R15 asks for. Registering as a finding rather than fixing on sight, per self-interrupt
discipline.

---
*Instance closed: `6156b8b97`. Second, unrelated orphan found while here — the KNIFE3 step 11
bill-assembly cut was also sitting entirely uncommitted; landed separately with its seam control.*
