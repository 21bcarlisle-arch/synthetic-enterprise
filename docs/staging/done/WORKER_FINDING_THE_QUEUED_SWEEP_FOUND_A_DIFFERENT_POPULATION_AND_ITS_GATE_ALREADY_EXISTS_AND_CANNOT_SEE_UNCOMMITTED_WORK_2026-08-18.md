# WORKER FINDING (RECORDED) — the queued sweep ran, the population it predicted is 2 of 297, and the fail-closed gate it asked for was built five days ago and cannot fire on this failure

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** the sweep is DONE; the recommendation it was queued under is RESHAPED, not built

*Severity note: LATENT, not RECORDED, deliberately. `background/finding_classes.py` puts RECORDED out of population because such a document is "a landed record with nothing owed". §4 leaves three things owed, so this is a defect record with a repair to argue, not a receipt.*

**Found by:** the 2026-08-18 worker tick, which drew
`WORKER_FINDING_A_PASSS_OWN_PROGRESS_FIELD_CANNOT_SEE_THAT_NOTHING_LANDED_2026-08-18.md`
as a RUNG-1c BLOCKING draw and executed both halves it left NOT DONE.

## 0. The instance the blocking finding said it had fixed was not fixed

Before any of the sweep work below. That finding's own closing section reads:

> **DONE THIS TICK (reversible, so not asked about):** landed steps 31–35 via `tools.surgical_land`;
> corrected the yaml notice…; recorded §3ae.

`observed-with-evidence`, this tick, before any edit:

* `git show HEAD:docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md | grep '^## 3[a-z]*\.'` → last section **§3y (step 30)**. §3z–§3ae were working-tree only.
* `git cat-file -e HEAD:simulation/dwelling_records.py` → `exists on disk, but not in 'HEAD'`. Same for `company/interfaces/dd_review.py`. Both **untracked**.
* `python3 -m tools.wall_crossing_dispositions --at-head` → **8 live crossings** and the same two FINDINGs the finding quotes, against the bare command's `6 live … OK`.

So a finding whose entire subject is *"a pass records progress in the working tree and verifies it with a working-tree instrument"* recorded its own remediation in the working tree and never committed it. **Instance 5, and the first one that is self-referential.** Landed this tick as step 36 with the tree — not the command — as the witness.

## 1. Why it happened: THE LANDING IS REFUSED, and the refusal is a pathspec artefact

The finding attributed the class to a *mis-cited control*: the doorbell named the bare command, `--at-head` was "available and unrun". True of instance 4. It is not what stopped instance 5, and the real answer only appeared on the third attempt to land it.

**`observed-with-evidence`: `tools.surgical_land` REFUSES this work.**

```
[surgical-land] REFUSED: GATE RED on the resulting tree (rc=1).
7 failed, 1196 passed, 60 warnings in 881.00s (0:14:41)
[test-gate] ✓ wall crossings reconcile at the tree this commit creates (6 live, 91 ruled)
[test-gate] ✓ every first-party reference resolves in the tree this commit creates (422 checked)
```

Both wall-specific checks were GREEN. What was red was ordinary tests — so every instrument aimed at *this* class agreed the landing was sound, and the landing still could not happen.

**The cause, reproduced in a standalone extract of the resulting tree:**

```
FAILED tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py::
       test_every_live_consumer_asks_the_world_for_the_dwelling
AssertionError: these live call sites build a dwelling record without asking the world
for the drawn homes: ['tools/fabric_settlement_gap.py:94 HouseholdDemandRegister()']
```

That test is a **repo-wide AST census** — it walks every `.py` under `simulation/ saas/ company/ tools/ background/`. `tools/fabric_settlement_gap.py` carries the required `drawn_households=` fix **in the working tree**, and it was outside the 30-path landing pathspec. So:

* in the WORKING TREE the census passes — the fix is there;
* in the TREE THE COMMIT CREATES the census fails — the fix is not in the pathspec;
* and the gate is right to refuse.

**This is the collision at the centre of the instance.** A surgical landing on a permanently dirty shared tree is *defined* by its pathspec — that is what stops it sweeping other lanes' work. A repo-wide census is *defined* by ignoring pathspecs. Every file the census can see must therefore be in the pathspec, which means the landing set is not "the files I edited" but "the files I edited, plus every file any census in the selected tests can reach". Nothing computes that set, and getting it wrong produces a refusal whose message names a file the author never touched.

Adding `tools/fabric_settlement_gap.py` (31 paths) turns that census green: `11 passed`.

**`inferred`, and flagged as such:** the same refusal most likely stopped the original step-36 landing, since its author was working the same pathspec against the same census. I did not observe their run and am not asserting it.

**The rule this points at:** *a landing is verified by the tree, never by the landing command.* `git cat-file -e HEAD:<path>` is the check. Two lesser traps also cost time here and are recorded so the next tick does not re-pay them — a foreground run SIGTERMed at a 10-minute cap leaves the desk byte-identical to a run never attempted, and a `nohup … &` wrapper returns exit 0 from its own trailing `echo` while the gate is still running with a block-buffered, still-empty log. Both make a REFUSED landing look like a completed one.

## 2. THE GATE THE FINDING RECOMMENDED ALREADY EXISTS, WITH A CALLER

The finding's headline recommendation was *"`wall_crossing_dispositions` grows a mode that is FAIL-CLOSED on the HEAD/worktree divergence"*, filed **unbuilt, queued**.

It was built on 2026-08-13, and it is not dormant:

* `tools/wall_crossing_dispositions.py::run_at_tree` — the `--at-tree` mode, gating the tree the commit WOULD create.
* `tools/pre_commit_test_gate.py::_wall_crossing_landed_check` — its **automated caller**, fail-closed at every step (unimportable module, unusable index, raising checker → commit REFUSED), scoped to any staged `.py` plus the register.
* Its own docstring records that it was built for the *previous* instance of this class, and names the same R15 FAIL-SILENT reasoning: *"A control built to catch 'the record outran the code' cannot be invoked by the record. It has to be invoked by the thing that makes the code real — the commit."*

**And that sentence is exactly why it did not fire.** It is a COMMIT-TIME gate, and instance 5's failure mode is *never committing at all*. A gate on the commit cannot see work that never reaches one. Nothing was mis-cited and nothing was unavailable — the control was correct, live, and structurally out of reach of this defect.

This is the finding's real residual, and it is not the build it queued. Recording it rather than taking it, per SELF-INTERRUPT DISCIPLINE.

## 3. The queued sweep, RUN — and the predicted population is 2 of 297

The finding filed this as the class-level work: *"a sweep for progress fields whose stated verification command reads the working tree"*, over `docs/design/simplifications/`.

Run over all **297** stores:

| | count |
|---|---|
| stores making a PROGRESS CLAIM about themselves | **32** |
| …of which name **any** verification command at all | **2** (`KNIFE3_wall_crossing_paydown`, `A8_experiment_loop_speed`) |
| …of which name **no** command at all | **30** |

**So the shape the finding hypothesised has a population of two, one of which is the finding's own atom.** The exposure is real but it is a different shape: thirty passes assert how much of themselves is already built and name *nothing at all* to check it against. A named command that reads the wrong tree is a control aimed badly; no named command is no control, and it is 15× more common.

A second, independent instrument — do the stores' own cited paths exist **at HEAD**, rather than `Path.exists()` on the desk (178 cited repo paths):

* **record outran the commit** (on disk, not in HEAD): **2 stores, 3 paths** — `EP1_clv_three_horizon` cites `tests/saas/test_clv_margin_basis.py` and `tests/tools/test_derived_basis_parentage_gate.py`, both untracked; `EP16_anchored_generators` cites `sim/cache/elexon_ssp_full.json`.
* **cited in neither tree** (dead citation): **7 stores, 11 paths**, mostly staging findings that were archived after being cited — the known archiving-breaks-evidence shape, here measured on the stores rather than the map.

R12: no published number moved. Nothing in §3 changes a company figure; what moved is what the records admit about themselves.

## 4. Found on the way: the drawn finding does not belong to the class it is the deepest instance of

`background/finding_classes.py` classifies by TITLE alone. Checked directly rather than assumed:

```
WORKER_FINDING_A_PASSS_OWN_PROGRESS_FIELD_CANNOT_SEE_THAT_NOTHING_LANDED_2026-08-18.md
  -> class: None   is_classed: False   severity: BLOCKING   lane: H_harness
```

The `uncommitted_and_orphaned_work` patterns include `never[_ ]lands?|unlanded|did[_ ]not[_ ]land|cannot[_ ]land`. This title says **"CANNOT SEE THAT NOTHING LANDED"** — the negation is carried by a *different word* (`nothing`) from the one the pattern anchors on, and `cannot` is bound to `see`, not to `land`. So the largest instance of this class (5 steps, 2 real cuts, 2 new modules, and the one that recurred *inside its own remediation*) is invisible to the checker that exists to keep the class honest, and `--check` reports **PASS** with `instances=10` while instance 11 sits in the root.

The class document's own promise — *"Membership is DERIVED, never hand-kept … fails if a live finding belongs to this class and is not listed here"* — holds only for titles phrased the way the pattern author phrased them. **A derived membership is only as complete as its vocabulary, and nothing measures the vocabulary.**

Not fixed on sight: widening the pattern re-classes documents across five class files, which moves severities and archive state. Queued below.

## 5. And this document was itself made invisible while being written

Minutes after it was created in `docs/staging/`, a concurrent writer moved it to `docs/staging/done/` and `git add`ed it. `background/finding_classes.py --render` was then run and the class document still read `**Instances:** 10`, with no line for this file. `--check` reported **PASS (0 failures)**.

The reason is one function:

```python
def archived_instances(root, finding_class):
    """Instances the existing class document names AND that are present in the archive."""
```

Membership for an archived document is *the intersection of the archive and the list the class document already has*. A finding that reaches `done/` before it is ever rendered is therefore in neither population — not live (so `derive_memberships` skips it), not listed (so `archived_instances` skips it) — and the checker whose promise is *"fails if a live finding belongs to this class and is not listed here"* is telling the truth and still cannot see it. **The order is load-bearing and nothing enforces it.**

Repaired by hand for this document, in the order the machinery requires: restored to the root → `--render` (`instances=10 → 11`, line present) → archived → `--check` PASS at 11. That is a manual sequence, which is the definition of a step that will be skipped again.

## 6. Recommendation — stated, with the one I would take named

The instance is closed by landing. The class is **not**, and the honest position is that its remaining gap is smaller and more specific than the queued build:

1. **RECOMMENDED, and the one I would take:** the 30 progress-claiming stores that name no verification command are the population, not the 2. The cheap structural move is that a store making a progress claim must name a command **and** that the claim's cited paths resolve at HEAD — one checker, both terms, R15 both ways (a store whose cited artefact is untracked goes RED; a fully-landed store goes GREEN, because this tree is permanently dirty and a check that is always red at a dirty desk is off within a day).
2. **NOT recommended:** a second HEAD/worktree mode on `wall_crossing_dispositions`. It exists, it has a caller, and it is aimed at a defect that arrives by a different door.
3. **Left open, named rather than dropped:** nothing in the repo notices work that is never committed *at all*. Every control in this class is invoked by a commit. That is the load-bearing gap and it needs a design, not a checker bolted to an existing one.
4. **From §4:** the class patterns need a VOCABULARY control, not more patterns — a mutation that renames a known instance's title into a synonym must make `--check` go red. Adding `nothing[_ ]landed` alone would fix this title and leave the next synonym free.
5. **From §5:** `--check` should treat *an archived document that classes into a class but is named by no class document* as a FAILURE. Today that state is silent, and it is reachable by any writer that archives before rendering — which is exactly what happened here, unattended, inside twenty minutes. The R15 mutation is trivial and it currently passes: archive a classed finding without rendering, run `--check`, watch it go green.
6. **From §1, and it is the cheapest real win here:** `surgical_land` can COMPUTE the pathspec it needs. The gate already selects the test files; a test that walks a directory tree is detectable, and the landing set it implies is derivable. Failing that, the refusal message should say *"the resulting tree is missing a fix that exists on your desk at `<path>`"* rather than naming a call site — the current message reads as "someone else's file is broken" when it means "your pathspec is short".

**NOT DONE:** all three of the above. Queued, not taken — the supply of harness findings is infinite and fixing on sight is the treadmill.
