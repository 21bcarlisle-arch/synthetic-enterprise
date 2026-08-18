**Severity:** BLOCKING · **Lane:** H_harness

# The discharge control's population is a markdown marker, so the register levels are actually argued in — 178 atom stores, 349 test citations, zero markers — cannot be checked at all

**Found:** 2026-08-18, worker tick, H27 Expert Hour #38, while landing Hour #37's repair and
discovering that #37's entire deliverable was in no commit while three separate records said it
was built.
**Class:** `uncommitted_and_orphaned_work` (the class doc is
`docs/staging/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`).
**Measured at:** HEAD `d12b6ab79`. §1 and §2 are `observed-with-evidence` (R9). §4 is inferred and
labelled.
**Owner:** `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py`.
**Intended rank (P-1):** top of H_harness's BLOCKING band.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the tick that found it was landing a
different repair, and widening this control's population is a BUILD with a real false-positive
problem to solve (§3).

---

## 1. The instance that exposed it

Expert Hour #37 built the widened door-vs-ledger subject in `tools/couple_w2_11_d5.py`, wrote its
tests, regenerated the ledger, and landed **none of the three**. Measured by `git show HEAD:` on
both files at `d12b6ab79`:

| symbol | HEAD | working tree |
|---|---|---|
| `door_only` | 0 | 3 |
| `required_missing` | 0 | 2 |
| `_abbrev` | 0 | 3 |
| the derived-subject loop | absent | present |
| the 11 new tests | 0 | 271 added lines |

Three separate records nonetheless stated it was done:

1. the atom's store note, **committed** at `65b26e4e4`, asserting *"BUILT (this atom's own
   file_scope) … R15 BOTH WAYS AGAINST REAL HISTORY, not a fixture: RED on the committed pair at
   HEAD (2 violations…), GREEN on the live regenerated pair"*;
2. the same atom's `level_hold_note` owed list, which moved item (A) to `door_only` on the
   strength of it;
3. the finding document, which says *"archived in the landing commit, so the citation resolves"* —
   and it **was** archived to `docs/staging/done/`, committed at `96c665098`, an unrelated
   auto-process publish run six hours later that could not know whether the code landed.

The live consequence ran for over 20 hours: at HEAD the shipped control compares ten declared
fields and returns **zero violations** on a pair that disagrees on 2 of 19 shared fields —
`recon_saturation_band_days` (door `[-6, 483]`, ledger `[-6, 82]`) and `recon_saturation_caveat`
(2,625 chars vs 821, the ledger still on the pre-D28 sentence). Re-measured this tick, both sides
read from one ref.

## 2. Why the control built for exactly this could not see it

Hour #36 built `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py`
against the subject *"a path a COMMITTED record cites on its `**Discharged:**` line that the index
does not carry"*, and the rung-1c repair at `32b70f644` made the citation (`file::node`) the
subject and checks it against the INDEX. Both are right. Neither could fire here, because the
population is defined by one markdown marker:

```
_DISCHARGE_MARKER = r"^\*\*Discharged:\*\*"
```

Measured over the real corpus this tick:

| population | count |
|---|---|
| archived finding docs in `docs/staging/done/` | **1,598** |
| … carrying a `**Discharged:**` line (in the control's population) | **74** |
| … archived-as-closed and invisible to it | **1,524** |
| atom store files (`docs/design/simplifications/*.yaml`) citing a `tests/**.py` path | **178** |
| distinct test citations in those stores | **349** |
| atom store files carrying a `**Discharged:**` marker | **0** |

The register in which levels are argued, passes are recorded and promotions are justified carries
349 test citations and **not one** marker the control looks for. Archiving to `done/` is this
project's other closure act, and 95% of it is outside the population too. The control is not
wrong; its subject is one of the three places a discharge is claimed, and it is the one place this
atom's Hours do not use.

## 3. The population it would have caught, and the reason this is a BUILD

Running the index comparison over store citations instead of markdown markers returns **8** atom
stores citing a `tests/` path the index does not carry:

```
B11_evolutionary_tournament_harness   tests/background/test_tournament_harness.py
B6_collateral_cash_death_loop         tests/saas/test_collateral_death_loop.py
D36_bill_render_footing_and_pence     tests/tools/test_no_orphan_published_customer_artefacts.py
EP1_clv_three_horizon                 tests/saas/test_clv_margin_basis.py,
                                      tests/tools/test_derived_basis_parentage_gate.py
H18_harness_self_mutation_audit       tests/controls/test_meta_control_mutation.py
H27_payment_belief_gap                (the same two, quoted from #36's own ratchet)
H28_precommit_gate_ambient_cwd_git_discovery   tests/background/test_x.py
OPS_run_marker_sweep_livelock         tests/background/test_run_marker_sweep.py
```

**At least one of those eight is a false positive and that is the point.** `tests/background/test_x.py`
is illustrative prose in H28's note, not a citation; H27's two are quotations *of #36's declared
ratchet entries*, i.e. a record correctly reporting a known debt. A naive widening would be born
red on prose, and a control born red is a control someone disables. So the build is: a citation
grammar for store prose (what distinguishes *"proven by `tests/x.py::test_y`"* from *"a module like
`tests/background/test_x.py`"*), then the same index comparison and the same declared-debt ratchet
the markdown half already has. The remaining six are unverified leads, not asserted defects.

## 4. Why this is BLOCKING rather than latent (inferred)

Three independent records agreed, all three were wrong in the same direction, and the direction is
always *over*-claiming: no record has ever been found understating what landed. Recording is cheap
and landing is not, so the failure mode is structural rather than careless. A second lane found the
same class the same day from a different atom
(`docs/staging/WORKER_FINDING_A_LANDING_STEP_CAN_ONLY_BE_CAUGHT_BY_A_TREE_IT_DOES_NOT_CONTROL_2026-08-18.md`,
KNIFE3 steps 36/37/39/40 — four consecutive steps, each writing in uncommitted text the rule it was
breaking), and that document was itself untracked when this one was written. Two lanes, one day,
one shape.

## 5. Recommendation, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **Do not widen the marker in place.** Add the store-prose citation grammar first and measure the
   false-positive rate against the eight above; land the widened population only once prose and
   citation are separable, with the six unverified leads dispositioned individually.
2. **The cheaper control that is not in this finding's lane**, recorded so it is not lost: the
   discharge test asks whether a cited *file* is in the index; nothing asks whether a store note
   claiming `BUILT` names a symbol `git show HEAD:<file_scope>` actually contains. That check needs
   no grammar at all — the atom already declares its `file_scope` — and it is what would have caught
   §1 in the tick that wrote it, not the tick after.

---

## 6. DISCHARGED 2026-08-18 (worker tick, H_harness rung-1c BLOCKING draw)

**Discharged:** `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py`,
`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_no_committed_store_credits_a_falsifier_the_repository_does_not_have`,
`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_no_silenced_absence_is_undeclared`,
`tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py::test_every_stale_citation_names_a_commit_that_really_retired_it`,
`tests/tools/test_no_orphan_published_customer_artefacts.py`

The store register is now a population. §5.1 was followed as written — the grammar first, the
false-positive rate measured against the leads, and every lead dispositioned individually before
the control was allowed to fire.

**The measured false-positive rate is why the naive widening was refused: 9 of the 10 leads are
records telling the truth.** A store register is DISCOVER/FRAME-heavy and naming a file that does
not exist yet is what design work IS, so a control keyed on mere mention is born ~90% red. The
grammar that separates them is not prose-vs-citation but **claim-vs-location**: a mention is a
claim unless its own clause says where the artefact lives (untracked / absent / owed / still to be
written). Silence is a claim, because §4's measured failure mode is one-directional.

Two corrections to §3, both measured this tick and both against the document rather than for it:

1. **The count.** §3 reported 178 stores / 349 citations and 8 offending stores; re-measured at
   `e844ee864` the corpus is 353 stores, 200 of them citing 281 distinct `tests/**.py` tokens, and
   the naive population is 10, not 8. The shape §3 described is right; its figures were not.
2. **`tests/**/test_*.py` is a GLOB and `test_x.py` a stand-in name** — §3 listed both as citations
   to be adjudicated by grammar. Neither is a citation in any lane, so both are rejected as tokens
   before the grammar runs at all.

**Two leads §3 could not see, because a file-level census cannot see a node.** Both are the
*stale-citation* shape rather than the over-claim shape, and they got their own register with a
stricter discipline — an entry must name the commit that retired the node, and the test resolves
that SHA:

- `tests/tools/test_couple_fabric.py::test_the_LAST_RED_CELL_…_not_moved` (W1_12) — un-pinned on
  purpose at `6828f999f`.
- `tests/tools/test_couple_supply_start.py::test_the_metering_observable_is_present_and_the_derivation_ignores_it`
  (C15) — the pin is real and still there; `7d01fffba` renamed it `…_honours_it` when it fixed the
  derivation, and only the log entry's copy of the name is stale.

**One real violation, and it was landed rather than declared.** `D36_bill_render_footing_and_pence`
credits *"Fixed at the lifecycle instead: `_retire_departed_artefacts()` plus the R10 class guard
`tests/tools/test_no_orphan_published_customer_artefacts.py`"*. The repair is at HEAD (2
occurrences in `tools/generate_customer_data.py`); the guard was on disk for five days, 8,433
bytes, `git log --all` empty, 6 tests green. The repair landed and the control that keeps it honest
did not. It waits on nothing, and a ratchet entry naming no wait is exactly the dishonest shape the
markdown half's stale-entry test exists to delete — so `_KNOWN_UNLANDED` ships EMPTY.

**What is left open, deliberately.** §5.2's cheaper control — does a store note claiming `BUILT`
name a symbol `git show HEAD:<file_scope>` actually contains — is not built here. It is a different
subject (symbols against a declared file_scope, no citation grammar needed) and this finding said
so itself. Registered as its own document rather than absorbed silently:
`docs/staging/WORKER_FINDING_A_STORE_NOTE_CLAIMING_BUILT_IS_NEVER_CHECKED_AGAINST_ITS_OWN_FILE_SCOPE_2026-08-18.md`.

**Evidence:** 18 passed in this module; 35 passed across it, the markdown half and the D36 guard
together — the sibling control re-run because this document's own `**Discharged:**` line is now
part of *its* population, so the citations above are checked against the index by the control this
one was built beside.
