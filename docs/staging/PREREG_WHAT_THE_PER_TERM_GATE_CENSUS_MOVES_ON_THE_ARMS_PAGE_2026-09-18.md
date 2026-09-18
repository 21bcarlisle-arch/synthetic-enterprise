**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# PRE-REGISTRATION — what fixing the product-gate census's UNIT moves on the arms page

**Filed:** 2026-09-18, before writing the module and before regenerating any feed.
**Claim id:** `the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term`
**Finding it answers:**
`docs/staging/done/SEAT_FINDING_THE_PRODUCT_GATE_CENSUS_ANSWERS_ON_THE_OPENING_TERM_WHILE_THE_GUARD_REFUSES_PER_TERM_AND_ONE_ARTEFACT_SAYS_BOTH_2026-09-18.md`

---

## The duplicate-work check, answered

The draw named one rival live claim —
`reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` — on the ground that it
"already holds `tools/run_value_cycle_ab.py`, which this item names".

**It is genuinely different work on the same file.** Its draw record's `named_paths` are
`background/boot_sha.py`, `background/process_run_complete.py`, `docs/design/maturity_map.yaml`,
`tests/background/test_a_multi_chain_landing_is_not_recorded_as_one_chain.py`,
`tests/tools/test_fold_noise_floor_family.py`, `tests/tools/test_value_cycle_ab_noise_floor.py`,
`tools/run_value_cycle_ab.py`, `tools/wait_for.py` — a fork reconciliation whose subject in this
file is the **noise-floor family**, not the renewal funnel. Its claim record binds **no paths**
(`paths: []`), so nothing of it has landed. A live process does hold it (`ps` shows the id twice),
so I treat `tools/run_value_cycle_ab.py` as **contested** and will land my hunks with
`tools/isolate_hunks.py` rather than a plain pathspec if the working copy moves under me.

Disposition: **carry on.** Not `--landed-under`, not `--release`.

## What I checked before writing this, rather than taking the drawn item's word for it

| the item's claim about the tree | checked how | result |
|---|---|---|
| the census publishes `the_guard_admits_it: true` for every one of 232 legs | read the 09-18 artefact | **holds** — 6 leg GROUPS summing to 232, every one `resolved_tariff_type: "fixed"` |
| `a_found_account_can_reach_the_product_gate: true`, 145 found accounts | same | **holds** |
| `product_not_upliftable_by_tariff_type = {'svt': 2490}` of 2,824 offered | same | **holds** (88.2%) |
| the field is what "the live page's sentence turns on" | `grep` every reader | **holds, and narrower than stated** — exactly two readers, both in `tools/generate_value_arms_data._who_the_method_has_priced` (`:5552`, `:5572`, `:5649`). No site JS reads it. |
| the page's sentence is the `gate_reachable` branch's | read `_who_the_method_has_priced` against the artefact | **REFUTED, and this matters** — see below |

### The refuted premise, and what it makes the actual defect

The item (and the finding) locate the harm in the branch `measured and gate_reachable and not
won_priced`, which demotes the verdict to `unresolved`. **That branch cannot fire on either the
published or the promoted artefact**, because `won_priced` is non-empty in both: the 09-10 run
priced 90 found accounts and the 09-18 run priced 59. So the wrong-unit boolean does **not** flip
this run's verdict, and I will not claim it does.

What fires instead is the `won_priced` branch, and its published sentence is:

> "The gate that used to refuse every won household is passable, so **what limits this experiment
> now is book size, not eligibility**."

That clause is on the live page **today**, under the 09-10 run, where 1,475 of 1,975 renewals
offered to found accounts (74.7%) stopped at the product gate. It is the same defect the finding
names — a conclusion about eligibility drawn without counting per term — and it is the clause that
licenses "grow the book". So the unit repair is right and the sentence it repairs is a different
one from the one the item predicted. **The boolean is the wrong unit; the sentence is the live
harm.**

## What I am building

One function, in one module, called by the **producer** and again by the **publisher** — the shape
`tools/product_gate_refusal.py` and `tools/decisions_that_existed.py` already establish here,
because the page renders artefacts weeks old.

`tools/decisions_by_account_class.py` splits the decision population **by how each account joined
the book**, by calling `decisions_that_existed` once per class over that class's own stage counts
(`renewal_funnel.by_account_class.classes[*].stages`, which every artefact since 2026-08-30
carries). The membership rule is therefore **not re-implemented** — a slice of `FUNNEL_STAGES` by
guard order is the control-pinned-to-today's-order shape `decisions_that_existed` refuses in its
own docstring, and it was my first draft.

The per-record census keeps its block and **loses the shared verdict field**:
`a_found_account_can_reach_the_product_gate` → `a_found_accounts_opening_product_is_upliftable`,
`found_accounts_the_guard_would_admit` → `found_accounts_whose_opening_product_the_guard_admits`.
Renaming rather than deleting is deliberate: a stale reader then fails closed instead of reading
the wrong unit silently, which is the whole class of defect here.

## Predictions, before running anything

**P1 — the per-class decision population, on the 09-18 artefact.** Derived by hand from
`by_account_class.classes[*].stages` before the code exists:

| class | renewals offered | decisions that existed | priced | priced share of decisions |
|---|---|---|---|---|
| `drawn_by_the_curriculum` | 1,138 | **42** | 42 | **1.000** |
| `won_by_the_funnel` | 1,614 | **54** | 51 | **0.944** |
| `founder_hand_authored` | 72 | **11** | 11 | **1.000** |
| **found (drawn + won)** | **2,752** | **96** | **93** | **0.969** |

**P2 — the reading this produces is the OPPOSITE of the published one, and unflattering in a
different direction than expected.** The arm prices ~97% of the renewals that presented a decision
to a found household. What bounds the experiment is that only **96 of 2,752** (3.5%) of the
renewals the world offered found accounts presented a decision at all. Book size scales both sides
of that 3.5% equally and cannot move it. So: *eligibility, not book size* — and the eligibility
limit is **market structure, not plumbing**, which is
`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION`'s own closing claim.

**P3 — the same repair changes the LIVE page before any promotion.** On the currently published
09-10 artefact I predict found decisions **263** (drawn 35, won 228), priced **198**, share
**0.753**, against 1,975 offered (13.3%). So regenerating `site/data/value_arms.json` on the
*existing* `THREE_ARM_PATH` should already delete the "book size, not eligibility" clause. If it
does not, my reader repair is in the wrong branch and P2 is unsupported.

**P4 — the 09-10 artefact carries a per-class caveat the 09-18 one does not.** Its
`product_not_upliftable_by_tariff_type` has `None: 158`, so `refusal_breakdown.defect_count > 0`
and the per-class decision populations are not exact — the funnel publishes no per-class label
breakdown, so that 158 cannot be attributed to a class. I predict the block will carry an explicit
"the per-class unresolved bucket is not established" field on 09-10 and **not** on 09-18 (whose
breakdown is `{'svt': 2490}`, defect_count 0). This is the fail-closed leg and it is the one I am
least sure of, because it depends on my reading that `decisions_that_existed` returns
`unresolved: None` for an absent breakdown rather than refusing.

**P5 — three controls in `tests/tools/test_the_renewal_funnel.py` go red on the rename and are
repaired by the rename alone** (lines 560, 561, 566, 567, 588). They were repaired to green at
HEAD four commits ago (`47d3115f7`); their null rung survives the rename untouched, because what
they assert is that the census's verdict can come back both ways and the verdict still can. If any
of them needs its *assertion* changed rather than its field *name*, the rename has moved more than
a name and I will say so.

## What would refute the whole thing

A reader of `by_account_class.classes[*].stages` that already re-counts per class downstream (I
have not enumerated every reader of that block — the same open edge the finding left). Or a class
whose stage counts do not sum to its `renewals_the_world_offered`, which would mean the per-class
stage dict is not a partition and every share above is over the wrong denominator. I check the
second in the module itself and fail closed on it rather than assuming it.

## What is NOT in this turn

The six controls blocking the republish, and the promotion of the 09-18 artefact to
`THREE_ARM_PATH`. The item's own order puts the unit fix first and says to land the part that
finishes; a verdict change and a promotion in one commit is unattributable, which is the reason
the finding gave for not attempting either together.
