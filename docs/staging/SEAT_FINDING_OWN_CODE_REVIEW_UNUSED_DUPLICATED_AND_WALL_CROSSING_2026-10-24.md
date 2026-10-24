**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `KNIFE3_wall_crossing_paydown`

# The seat's own code review: what is unused, what is duplicated, what crosses the wall, and why nothing flagged it (2026-10-24)

Acting on `docs/staging/advisor/DIRECTOR_STEER_REVIEW_YOUR_OWN_CODE_FOR_WHAT_IS_UNUSED_DUPLICATED_OR_CROSSES_THE_WALL_2026-10-24.md`
(director, 24 Oct 09:35 and 09:40). The advisor's illustration was tested, not adopted. Every
figure below was measured on `52a5f2cf3` today; how is beside it.

## 1. What the review found

| # | Finding | Measured | The illustration said |
|---|---|---|---|
| 1 | Supplier modules no run reaches: imported by their tests and nothing else | **268** in `company/`+`saas/` (`tools/capability_index.py --dispositions`), 41,565 lines; **401 test files, 81,623 lines, 9,207 test functions** (about 23% of the 39,465 collected) touch them | 286, ~38,900 lines. **Different instrument**: 286/327 is the code-tab census (zero import edges in the drawn graph); 268 is the ruled orphan set. Both are true of their own definitions; the ruled set is the one to act on |
| 2 | By package | market 69, crm 49, regulatory 42, billing 35, trading 22, finance 18, pricing 11, risk 10, other 12 | 72 `*_register` modules — not re-counted; the package split is the more useful cut |
| 3 | The orphan control has **no automated caller** and is **red today** | `--dispositions` returned a STALE row (`company.regulatory.energy_bill_support`, wired by `d8129f3f6` for the EBSS fix) and nothing noticed. It runs in 22 s and nothing runs it | **Missed.** The illustration said the register "passes when every orphan has a row"; in fact nobody asks it |
| 4 | The world draws household churn truth from supplier models | `simulation/customer_events.py:31-33` imports `company.crm.churn_model`, `saas.churn_model`, `saas.home_move_win_rate`; the stay/leave roll starts from `build_churn_risk` → `effective_retention_probability` (lines 733-744, 999) | Correct |
| 5 | The run loop holds the supplier's decision policy | `simulation/run_phase2b.py:121` → `company.policy.decision_policy` | Correct; asked whether it is legitimate orchestration. **It is not wholly**: the register's §3aa records two supplier processes read world-side (retention offer, hedge), not only the choice of which policy arm the run executes |
| 6 | Two more crossings, indirect through a bridge | `run_phase2b -> company.billing.account_ledger`, `-> company.billing.payment_observation_consumer` (design B14) | **Missed** — "4 go round the seam" counts direct edges only; the wall register holds **6** |
| 7 | Two churn models | `saas.churn_model` (6 importers, bill-shock driven) and `company.crm.churn_model` (12, rate/tenure/arrears). Both are live supplier code | Correct as duplication; but they are not interchangeable today, and `saas.churn_model` is the one the world reads |
| 8 | `sim/` vs `simulation/` | sim = the market (43 modules), simulation = households and the runners (124). sim imports no supplier code; simulation→sim 21 files, sim→simulation 4 | "split by history rather than by job": half right — the split is history, but it does now fall on a job line (market vs people) |
| 9 | Package READMEs contradict the wall | `simulation/README.md` licensed "import from both `sim/` and `saas/`"; `saas/README.md` claimed "the customer reaction function" — a household behaviour — for the business layer | The licence was named; the saas claim was missed. **This is the origin of B2**: July built household reaction inside the business layer |

**Wall-crossing seam doors are clean.** The 18 world behaviour modules that import `company.interfaces.*`
(not the runners) were listed: every door is something a household receives (a bill, a letter, a DD
instruction, a renewal offer). None is a supplier belief. So the seam is not laundering B2.

## 2. Why nothing flagged it — from the record

The advisor offered two hypotheses.

**Hypothesis 2 (the world and the runner share a package, so the world→supplier direction has no
structural check): REFUTED.** `tests/architecture/test_epistemic_wall_ratchet.py` class (b) has held
exactly that direction since 2026-08-05, every `simulation → company|saas` import off the seam
included, runners and all. It drove 105 crossings to 6. The README licence was stale prose, not
the rule; corrected today.

**Hypothesis 1 (controls stop growth and approve rulings, never ask whether the thing should exist):
CONFIRMED, and narrower than stated.** Both registers were examined, not unexamined:
- The wall register ruled the B2 edges `owed` with a full design ("a coupled-triad build, not a
  mechanical move") on 2026-08-09. `owed` required a design and nothing else. Its owning atom
  `KNIFE3_wall_crossing_paydown` sits at level 0, dial 3, so the weighted draw almost never reached
  it, and no date ever came due. A ruling with a design, no payer and no date stood 11 weeks.
- The orphan register required a row per orphan, then lost its only caller; it has been able to go
  red without anyone seeing (finding 3).

**Root cause:** a deferral was accepted as examined once it named HOW the debt dies, without WHO
pays and BY WHEN; and a control invoked only by hand is permanently passing. The second is a known
class (the wall gate's own docstring names it); the first was not.

## 3. The mechanism now catching it (P13, proven able to fail)

`tools/wall_crossing_dispositions.py`: an `owed` row must carry `owner=` (a LIVE maturity-map atom)
and `due=YYYY-MM-DD`, and a row past its date is refused. It runs in the commit gate on every staged
`.py` (`_wall_crossing_landed_check`), so an overdue debt stops the tree; moving `due=` is allowed
and is a visible edit to the register.

- Proven on the real instance: `test_the_live_owed_rows_are_scheduled_against_the_live_map` was
  **red on today's register** (12 findings, all six owed rows) before the rows were scheduled.
- Six mutations each red exactly one finding (no owner, dead owner, four bad dates, overdue by a day);
  the control row passes, and the due day itself passes, so the guard is not "refuse everything".

The six rows are now scheduled: B2 ×3 due **2026-11-21**, A ×1 and B14 ×2 due **2026-11-28**, owner
`KNIFE3_wall_crossing_paydown`.

The orphan register's missing caller is NOT fixed here: 22 s on every commit is the wrong price, and
the archive below empties most of what it would check. Owed with the archive step.

## 4. Rulings

| Item | Ruling | Why | When |
|---|---|---|---|
| 268 unhooked supplier modules + their tests | **ARCHIVE**, except 2 | Built, tested, never reached by a run. They cost 23% of test functions, a third of `grep` hits on `tariff`/`hedge`/`register` in the supplier (38%/31%/34%), and every gate that reads the whole tree. Archive is reversible; a later P1 that needs one restores it with its tests | **After Monday's publish (26 Oct)**, one package per commit, largest first (market, crm, regulatory) |
| `company.billing.ppm_warrant_register`, `company.regulatory.consumer_vulnerability_register` | **KEEP**, owner `C32_one_obligation_one_vulnerability_scorer` (L2→3) | In a live atom's file_scope | — |
| B2: `customer_events` → `saas.churn_model`, `saas.home_move_win_rate`, `company.crm.churn_model` | **CUT by a world build** (the register's B2 design) | World truth from a supplier model breaks W7 p1 and makes the churn belief-against-truth gap measure a model against itself | K8 page and predictions first; due 2026-11-21 |
| `run_phase2b` → `company.policy.decision_policy` | **OWED** to A_composition_lift: the policy arm is orchestration, the retention offer and hedge reads are not | — | due 2026-11-28 |
| `run_phase2b` → `account_ledger`, `payment_observation_consumer` (indirect) | **OWED** to B14 | the run measuring itself | due 2026-11-28 |
| Two churn models | **MERGE, after B2** | Until the world stops reading `saas.churn_model`, a merge would move world truth too. After B2 it is supplier-only and folds into `company/crm/` | after B2 |
| `saas/` vs `company/` as packages | **KEEP**, owner H_harness, fold module by module as each is touched | 34 modules, live importers on both sides; a big-bang move is churn across every lane for no behaviour change | standing |
| `sim/` vs `simulation/` | **KEEP** with the legend | It now falls on a job line (market vs people); renaming 167 modules buys nothing | — |
| Code tab | **Legend shipped** (`site/code/index.html`, "What each cluster is") | the director could not tell the clusters apart | with Monday's publish |
| Package READMEs | **Corrected** (simulation, saas) | factual errors against the wall | done |

## 5. The saving, measured

Pre-registered before measuring (13:26 BST): P1 the 401 test files run in 2–6 min serially; P2
their collection is 15–35% of the suite's; P3 the median commit saves under a minute because the
gate's test selection is change-driven.

**Result.** P1 REFUTED: about **10 minutes** serially. The run (13:26:45, `pytest -x`) reached 98% at the
harness's 10-minute background limit and was stopped there, with no failures in the part that ran;
the prediction was low by about half. P2 CANNOT ATTRIBUTE: collecting the 401 alone takes 17 s and
the whole suite 33 s (12.7 s against 23.8 s of pytest's own clock), but start-up is shared, so the
difference is not the subset's share. P3 not measured; it stays a prediction. Search noise, measured:
the unused modules hold 38% of `tariff` hits, 31% of `hedge`, 34% of `register`, 12% of `bill` and
8% of `churn` in `company/`+`saas/`.

## 6. What is owed, and to whom

- The archive (hand-off `archive-the-unhooked-supplier-modules`), after 26 Oct, with a pytest
  `norecursedirs` / ruff exclude for the archive root so gates stop reading it, and the orphan
  `--dispositions` check given its weekly caller in the same step.
- B2 world-truth churn (hand-off `b2-world-churn-truth`): K8 page from the switching evidence the
  knowledge layer holds, a labelled range where it is missing, predictions filed, before/after on
  one seed, the published churn belief-against-truth figures re-graded.
