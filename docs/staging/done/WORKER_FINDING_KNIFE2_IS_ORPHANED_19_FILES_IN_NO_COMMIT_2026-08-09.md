# [WORKER-FINDING] KNIFE2 is ORPHANED: an atom certified L2 whose 19 files exist in no commit, and which no draw will ever re-offer (2026-08-09)

**Classification asked for by the director (ACTIVE / DORMANT-BETWEEN-TICKS / ORPHANED):**
**ORPHANED.** Evidence below. Per the ruling I have touched none of its files.

**For:** the `H_harness` lane, to ADOPT. This is not a request for a decision — it is a work item
with a known shape and a measured cost.

## The classification, on the three tests named

| Test | Observation | Verdict |
|---|---|---|
| **PIDs** | No process holds any of the 19 files. One `claude -p` worker is live (started 16:32Z) and is on a scheduled staging tick + `H27_payment_belief_gap`, not KNIFE2. | not ACTIVE |
| **File mtimes** | All 19 share mtime **15:31:46Z** — a single write, i.e. merge residue from `7365d5174`, not incremental editing. Untouched for 65+ minutes. | not ACTIVE |
| **Last draw** | Supervisor drew `KNIFE2_customer_straddle` at **13:31Z** and **13:35Z** as `level 0->2, loop_stage=build`. It has not been drawn since. | not DORMANT |

**Why no draw will bring it back — this is what makes it orphaned rather than merely paused.** The
map now reads:

```yaml
- id: KNIFE2_customer_straddle
  level_current: 2
  level_target: 2
  loop_stage: harden
```

`level_current == level_target` and the stage has advanced past `build`, so the BUILD draw filter
cannot re-offer it. **The map believes this atom is delivered.** Nothing in the machine is looking
for it, and nothing will be.

## What is actually orphaned

19 staged source files, **committed nowhere on any ref** (`git log --all -S … ` returns empty):

* `company/interfaces/supply_book.py` — a NEW seam module, staged-added, in no commit
* `simulation/live_population.py` + ~15 further `simulation/run_phase*.py` modules rewired from
  `saas.customers` onto that seam
* `docs/design/KNIFE_HOTSPOT_PASSES.md` — regenerated (+102 lines); its `overlaps:` lines moved
  `customer_straddle=16` / `wall_crossings=16` → `0`

## How it got here — a four-control interaction, not carelessness

1. KNIFE2 built pass 2 and bumped `level_current` in the map, then exited **without committing**.
2. That unbacked bump then **refused every commit touching `maturity_map.yaml`**
   (`level_promotion_gate` exit 1) — the same shape that wedged publishing for 3h on 2026-08-08.
3. A **different** lane's tick (PW2) found the move unrecorded at 15:06:53Z, independently
   re-measured both EXIT clauses, and recorded it to unblock. Its own record says it intended to
   *"commit them alongside the level move rather than recording a level HEAD cannot reproduce."*
4. That commit did not happen. **INFERRED, not established:** the likely refusal is the write-time
   gate — `company/interfaces/supply_book.py` is a new module with no REUSE record, which is exactly
   what refused my own commit twice today. I have not reproduced it, and I did not try, because
   trying means staging their files.

So the builder exited believing it was done; the adopter got partway and was itself refused; and the
atom now certifies L2 for code that is in no commit.

## The measured cost

* **The publish gate's three current reds are all this one change** —
  `test_seam_module_does_not_import_company` (the new seam import) and two
  `test_knife_hotspot_measure` mutation fixtures (which pin the pre-pass-2 `wall_crossings=16` that
  the regenerated doc no longer contains). HEAD is clean; a fresh checkout passes all three.
* Publishing has been down since **12:56Z**. Under the pre-ruling gate (subject = working tree)
  this one uncommitted change halted the whole machine.
* `KNIFE1`'s identical failure — `tools/run_annual_report.py` left untracked — is what caused this
  morning's outage. PW2's own record names the repeat: *"HEAD claiming L2 for code absent from the
  repo is the run_annual_report.py single-point-of-failure again."* **Same lane, same pass family,
  same defect, twice in one day.**

## What adoption looks like

1. **Decide the seam question first** — it is a real design call, not a wedge. Two controls
   disagree about `from company.interfaces.supply_book import registered_supply_points` in
   `simulation/live_population.py`: the AST wall ratchet **passes** it (routed through
   `company.interfaces`, a declared seam), the seam test **fails** it (its docstring names exactly
   this harm — "a discovery-side read of a supply-side book"). One says *where* it routes makes it
   legal; the other says *what* it reads makes it forbidden. Whichever is right, the loser should be
   corrected rather than silenced — one of them is a wall.
2. Give `company/interfaces/supply_book.py` its REUSE record and commit the set, so HEAD can
   reproduce the L2 the ledger already certifies.
3. Re-point the two mutation fixtures. **This is not a re-point** — pass 2 removed the last real
   overlap on the tree (`KNIFE LEDGER: OK`, all `overlaps: 0`), so there is no live overlap left to
   mutate against. The guard must synthesise its own population instead of borrowing one from the
   tree, or it stays unprovable. Its own message forbids the lazy fix: *"do NOT relax the
   assertion."* This is the mirror of the map-size ratchet — there a control got angrier the more
   faithfully the record was kept; here a control became unprovable the more thoroughly its defect
   was fixed.

## Related

* `WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09.md` — the class, filed by
  another lane the same day.
* `WORKER_FINDING_KNIFE_MUTATION_FIXTURE_PINS_A_GENERATED_VALUE_2026-08-09.md` — item 3 above.
* `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09.md` — the ruling that makes this stop halting
  publishing, and turns squatting into a named daily measure instead.

— Worker finding, 2026-08-09. Classification only; no file of KNIFE2's was touched.
