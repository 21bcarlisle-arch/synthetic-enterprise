# WORKER FINDING (DISCHARGED) — the public Proof door was generated from an uncommitted tree: HEAD publishes a proof.json that HEAD's own code and ledger cannot reproduce, and the unlanded half sat orphaned for a day with every control green

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** DISCHARGED in the tick that found it

**Discharged:** `site/proof/test_the_committed_generator_reproduces_the_published_door.py`, `tools/generate_proof_data.py`, `background/gap_metric.py`, `docs/observability/coupled_gap_ledger.json`, `site/proof/index.html` — the generator, its grader and the ledger are landed, and the direction of the seam that was unfalsifiable now has a control that is RED on the real history it was found in.

**Found by:** the 2026-08-15 worker tick, drawn on `H27_payment_belief_gap` (lane `H_harness`, level 2→3, `loop_stage: harden`) — found while establishing what state the atom's instrument was actually in, before deciding the level.

## Observed, with evidence

Measured at `c47221060`, before any edit this tick.

`site/data/proof.json` is COMMITTED and LIVE. Fetched: `https://poesys.net/data/proof.json` → HTTP 200, 770,702 bytes, `generated_at` 2026-08-15T04:41:21Z — and a leaf-by-leaf diff against `git show HEAD:site/data/proof.json` finds **zero** differences. So the published door and the committed artefact are the same file.

That file carries, in its `coupled_gaps` block:

* `basis_audit_ran: true`, `basis_finding_count: 14`, and 14 `basis_findings` — the D44 grader's verdict, rendered to the public reader as a red alarm naming 13 world atoms;
* a non-empty `world_name` on 13 of 14 rows and a non-empty `company_name` on 13 of 14 rows.

The committed code that nominally produces that block carries none of it:

```
git show HEAD:tools/generate_proof_data.py | grep -c basis_audit_ran      -> 0
git show HEAD:background/gap_metric.py | grep -c reserved_component_keys  -> 0
```

and running HEAD's own generator against HEAD's own map returns `world_name: None`, `company_name: None` for every row — 0 of 305 atoms carry an inline `name` after the 2026-08-14 drain, and the coupled-gaps rows were still reading it inline.

**The published door was generated from a working tree, and no tree in this repository's history can reproduce it.** That is the IaC line in CLAUDE.md — *"reconstruct-from-repo-alone is the test"* — failing on the company's own evidence surface.

The ledger is the same shape one level down. With the generator landed but `docs/observability/coupled_gap_ledger.json` left at HEAD, the new control stayed RED on `['normalisation','raw_gap_is']`: the committed SUPPLIER cannot produce the committed artefact either, because HEAD's ledger predates the D44 declaration the door already renders.

## Whose work this is, and why nothing drew it

It is H27 Expert Hour #30's, recorded in this atom's own hold note on 2026-08-14 as *"Closed as a class: … the grader has a caller on every publish, and its verdict is rendered — six source mutations, all proven to fire."* Every clause of that was true of the working tree and false of HEAD, for a day.

It was not invisible, either. The previous tick's control names it in its own docstring: `site/proof/test_published_caveat_reaches_the_reader.py` explains that it lives in a separate file because `site/proof/test_coupled_gaps_panel.py` *"carries another lane's uncommitted D44 basis-audit work, so appending here would have landed their tests ahead of their supplier."* The entanglement was diagnosed, routed around, and left. Nothing drew it, because nothing in the harness treats "a published artefact its own tree cannot produce" as a state worth failing on.

## Why nothing was red — the part with design in it

Every existing check on this block takes **one** side as its subject.

* The panel tests recompute the block from the working tree (`_live_coupled_gaps()`), so they see the generator **as it is right now** and never ask what HEAD carries.
* The R11 door tests read the published file, so they see the artefact and never ask what produced it.

A tree whose artefact is a generation **ahead** of its code satisfies both. `test_published_caveat_reaches_the_reader.py`, built one tick earlier, closes the opposite direction — code ahead of artefact, a correction that never published. Neither direction implies the other, and only one had a falsifier. This is the same seam, walked the other way.

## The control, and its own caught fail-open

`site/proof/test_the_committed_generator_reproduces_the_published_door.py`. Two subjects that cannot be derived from one another: the SHIPPED GENERATOR (`tools.generate_proof_data._coupled_gaps`, imported and executed) and the PUBLISHED FILE on disk. It never regenerates the artefact and compares it with itself.

**R15 both ways, against real history rather than a fixture.** RED at `c47221060` — two of four assertions fail, naming `['basis_audit_ran','basis_finding_count','basis_findings']` and `['company_name','normalisation','raw_gap_is','world_name']` — and GREEN on the landed tree. The defect is a state the repository was actually in, so the mutation is history, not a mock. Fail-silent guarded on both subjects (a missing artefact and an `available=False` generator each RAISE rather than agreeing); vacuity guarded on both.

**Its own first draft was fail-open, and running it against that history is what caught it.** Written as *"a field the artefact fills on EVERY row must be filled on every generated row"*, it PASSED at `c47221060` — the tree it exists to fail on — because one row of fourteen carries `world_name: ""` (`WORLD_recontracting_relationship_start`) and one carries `company_name: ""` (`W2_2_population_draw`), so a single legitimately-empty cell disarmed the whole field. The rule is now asymmetric and counts: **filled somewhere, empty everywhere.** Reading the test would not have found that; running it at the parent did.

## R12 — no published number moves

The door already serves W2_11 `gap` 0.0833907649896623 with `n_negatives` 1451, `n_false_flags` 242, `flagged_size` 391, `caught` 31, `n_excluded` 118. HEAD's ledger said 0.0859375, measured 2026-08-12. Landing the ledger makes the committed supplier agree with what is **already published**; nothing a reader sees changes. That entry is the real book and not RECORDED 7's test-fixture population of 245 — its component counts are bit-identical to the live door's.

The working-tree regeneration of `site/data/proof.json` was deliberately **not** landed: it differs from the committed one on nine leaves and every one is a stamp. Republishing a public artefact to move a timestamp is churn.

## What this does NOT close, named rather than absorbed

1. **The generic version of the check.** This control's subject is the `coupled_gaps` block of one artefact. Every other `generate_*_data` producer and every other published block on `site/data/` has the same seam and no such control. Registering the population is a harness change outside the drawn work — SELF-INTERRUPT DISCIPLINE, queued, not taken here.
2. **RECORDED 7 of `…THE_CORRECTED_SENTENCE_NEVER_REACHED_THE_READER…`** — a bare `pytest tests/tools/test_couple_w2_11_d5.py` still re-publishes into `docs/observability/coupled_gap_ledger.json`. Untouched by this tick and still owed. It is the mechanism that makes this class recur on this particular ledger.
3. **Whether the publish path itself should refuse an uncommitted generator.** Not designed here. The control fails the tree *after* the fact; a deploy that checked `git status` on its own producer would fail it *before*. Stated as an option, not built.

## Not established, flagged rather than asserted (R9)

* **Which run produced the live artefact is not observed.** That it was generated from a tree HEAD does not contain is observed (the key sets above). Which process, at what time, from whose working tree, is inferred at best and is not claimed.
* **No claim is made that the published figures are wrong.** They are not: R12 above is measured. The defect is reproducibility, not accuracy.
