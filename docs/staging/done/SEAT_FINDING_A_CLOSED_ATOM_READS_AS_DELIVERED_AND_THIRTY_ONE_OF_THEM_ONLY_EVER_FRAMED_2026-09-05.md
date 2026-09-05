**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

# A closed atom reads as delivered, and 31 of them never built anything

**Found:** 2026-09-05, delivery seat, on the director's instruction to check two closed atoms before
stage 1 rebuilt their ground. The two answered differently, and the difference is the finding.

---

## What he asked

> *"W2_12_change_of_tenancy_debt_physics and W2_13_occupancy_consumption_volume_shape are closed
> atoms on exactly the ground the people ruling covers. Before stage 1 builds that again, find out
> what those actually delivered — extend them if they hold, and say so if they were closed without
> delivering."*

## W2_13 — HOLDS. Stage 1 extends it.

`simulation/demand_model.py` (753 lines) and `simulation/dwelling_records.py` (268 lines) are both
imported by `simulation/run_phase2b.py`, the live run loop. Occupancy genuinely reaches consumption.
What is missing is the people **joint** on small-area geography — today's traits are drawn
independently — so `W2_19` conditions what exists. A commit there that forks a parallel demand model
would be the defect, not the deliverable.

## W2_12 — DID NOT DELIVER ITS HEADLINE

| Artefact | Lines | Production importers |
|---|---:|---|
| `company/crm/change_of_tenancy_register.py` | 593 | **0** |
| `company/billing/account_closure.py` | 422 | **0** |
| `simulation/final_bill_outcome.py` | 522 | **0** |
| `simulation/arrears_engine.py` | 710 | 9 — genuinely wired, but arrears is not tenancy change |
| `saas/home_move_win_rate.py` | 345 | 3 — and see below |

**1,537 lines reachable only from tests.** `home_move_win_rate` does run, at
`simulation/customer_events.py:412`, but only to compute a retention probability at renewal: "home
move" is a name on a churn coefficient, not a modelled move. The live run emits 110 customer events,
every one `renewed` or `churned`. No move, no property staying, no incoming occupier, no deemed
contract — which is exactly what the merit-order amendment puts at rung 2 and calls "a third of the
book's real dynamics".

## The atom is not dishonest. The FILE is misleading.

`W2_12` has `level_current: 1, level_target: 1`. Level 1 is DISCOVER — the map's own notes say
"DISCOVER (L0->L1) ... level_current HELD at 0 (nothing built)". So it never claimed to have built
the emitter. It reached the target it was given.

But `maturity_map_closed.yaml`'s membership rule is `level_current >= level_target`, so it holds two
different things under one word:

    closed atoms: 227
      level_target 0:   8   (4%)   -- closed having done nothing at all
      level_target 1:  23  (10%)   -- closed at DISCOVER: framed, not built
      level_target 2: 126  (56%)
      level_target 3:  70  (31%)   -- closed having actually delivered

**Thirty-one of 227 closed atoms — 14% — never built anything**, and nothing distinguishes them from
the 70 that did at the surface anybody reads. A session checking "is this ground already covered?"
finds a closed atom on the exact subject and moves on. That is what nearly happened here, and only
happened not to because the director asked.

## And the same subject caught this seat's own measurement twice

Both wrong answers came from grepping a module NAME rather than resolving imports:

- `grep -rln change_of_tenancy_register` returned "2 production callers". All three hits were
  strings — a path in `working_day_guard`'s registry, a docstring in `dd_balance_book`, a dict key
  in `clv_three_horizon`. The real count is zero.
- Earlier the same day, `pgrep -af "haduk\|ceda"` returned nothing and was read as "the pull is
  dead". `pgrep` takes an ERE, where `\|` is a literal, so the pattern matched nothing. The pull was
  running the whole time.

A grep for a concept's NAME is blind to the mechanism, and it is equally blind to the difference
between a mention and a call. The AST import scan that settled this is four lines.

## What would close this

1. `maturity_map_closed.yaml` distinguishes **DELIVERED** (reached a build target) from
   **FRAMED** (reached a discover target) at the file's own surface, or the two live in separate
   files. A reader asking "is this built?" must not have to read `level_target` to find out.
2. The prior-art check becomes routine rather than director-prompted: before an atom is minted on
   ground a closed atom names, its artefacts are opened and their importers resolved. The check that
   found this took under a minute.
3. `W2_12`'s three unwired modules are either wired by the stage-1 move emitter or recorded as
   superseded — 1,537 lines that no production path reaches is its own finding, filed to the
   `no_caller_and_never_runs` class.

## Class registration

Belongs to `no_caller_and_never_runs`.
