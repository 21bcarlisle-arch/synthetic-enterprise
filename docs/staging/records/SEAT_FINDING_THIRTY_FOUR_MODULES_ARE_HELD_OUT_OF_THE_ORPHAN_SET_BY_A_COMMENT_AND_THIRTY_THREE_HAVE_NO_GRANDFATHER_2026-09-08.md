**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-orphan-baseline-carries-a-module-count-nothing-reads-and-it-was-the-only-evidence-of-a-stale-freeze`)

# Thirty-four modules are held out of the orphan set by a comment, and thirty-three of them have no grandfather

The drawn item asked me to decide whether `tools.published_row_scalar_census` gets wired or stays
frozen. Answering it required asking why the ratchet no longer calls it an orphan, and the answer
generalises past the one module: **the reachability graph counts a path written in a PROSE COMMENT
as an edge, so citing a tool as the provenance of a finding wires it.** That is the habit CLAUDE.md
asks for — say where a number came from — and it silently satisfies the control that asks whether
anything runs the thing.

## The decision the item asked for: it STAYS FROZEN, and not for the reason on file

`docs/staging/records/SEAT_FINDING_THE_BASELINE_DELETION_THIS_ITEM_CALLED_CORRECT_IS_A_STALE_FREEZE_FROM_A_SMALLER_TREE_2026-09-08.md`
said the module is an orphan and whoever wants it running should wire it and shrink the baseline
with the wiring. Measured today at `03c09fd61`, `--report` says the opposite: 372 orphans against a
373 baseline, with `tools.published_row_scalar_census` named as "now wired".

It is not wired. Its whole caller list is one entry:

```
tools.published_row_scalar_census  <-  ['company.finance.vat_book (by path)']
```

and `company/finance/vat_book.py:31` is a comment:

```python
#: expensive recurring defect. Found by `tools/published_row_scalar_census.py`, which ranks a
```

**Pre-registered, then measured.** Prediction, written before the run: rewording that comment so it
is not a path (dropping the `.py`) makes the module an orphan again and moves the tree from 372 to
373, matching the baseline exactly; if the count stayed at 372 some other edge reached it and the
diagnosis was wrong. Measured: **373**, exact. One editorial word is the whole of its wiring.

So the row stays frozen, and shrinking it would have been the mistake. Removing the grandfather on
the strength of a comment means the next person who rewords that sentence — a purely editorial act,
touching no code — makes the module an orphan with nothing excusing it, and the ratchet refuses
every lane in the tree under *"THIS COMMIT ADDS WORK THAT NOTHING RUNS"*, naming a module the
refused lane never touched. That is the 22-hour class the attribution split was built for.

## The class, measured rather than asserted

Method: rebuild the index's own edge map, drop every `(by path)` edge whose every reference in the
calling file sits on a line starting `#`, recompute reachability from the same 58 scheduled
entrypoints, and diff the orphan set. Comment-only path edges dropped: **307**. Modules that lose
all reachability with them gone: **34**. It is a FLOOR, not a total — a path inside a docstring, and
a reference the classifier cannot locate at all, are both counted as real edges.

| | |
|---|---|
| Reachable only via a comment | **34** |
| Of those, frozen in the baseline | **1** (`tools.published_row_scalar_census`) |
| Of those, **no grandfather — an editorial reword refuses every lane** | **33** |

The 33 span every root: `background.autonomous_runner`, `background.band_null_sweep`,
`background.blocked_atom_visibility`, `background.prefetch_elexon_ssp`,
`background.weather_demand_triad`, `company.crm.customer_registry`, `company.crm.home_registry`,
`company.crm.supply_start`, `company.market.tariff_benchmarking`,
`company.pricing.renewal_pricing_engine`, `company.pricing.weather_normalisation_belief`,
`company.regulatory.seg_book`, `saas.arrears_classifier`, `sim.weather_demand_chain`,
`simulation.willingness_classification`, `tools._ladder_chase_arm`, `tools.child_stderr_guard`,
`tools.commit_refusal_attribution`, `tools.couple_w2_7_c9`, `tools.executor_cli`,
`tools.explore_wall_sides`, `tools.generate_test_mix_data`,
`tools.measure_publish_gate_subject_cost`, `tools.need_stock_joint`,
`tools.ofgem_cap_unit_rate_composition`, `tools.reader_reachability`, `tools.render_site_nav`,
`tools.sample_gate_rss_premium`, `tools.site_reachability`, `tools.ssp_refit_local_vs_global`,
`tools.standing_red_replay`, `tools.tou_extreme_day_concentration`,
`tools.tou_price_shape_episode`.

**It is transitive, which is why a caller list alone does not find it.**
`tools.tou_price_shape_episode` is reached by a genuine *import* from
`tools.tou_extreme_day_concentration` — which is itself reached only by a comment in
`company/market/dfs_published_record.py`. `company.regulatory.seg_book` has a real import caller in
`company.regulatory.seg_export_estimator`, which is itself an orphan at HEAD. Reading either
module's callers says "imported, fine"; the prose is one hop up.

## What this says about the shrink that landed at 02:33 today

`9a280c876` shrank the floor by exactly the seven modules wired at HEAD, verified as a set
difference from a clean extract, and it was the right call on the evidence it had. **Four of those
seven are on the list above**: `company.regulatory.seg_book`,
`tools.ofgem_cap_unit_rate_composition`, `tools.tou_extreme_day_concentration`,
`tools.tou_price_shape_episode`. Their grandfather is gone and their wiring is a sentence. This is
not a defect in that commit — it is the reason "shrinking is free and never refuses", which both
that commit and the earlier finding relied on, is false in general. **A shrink is free only if the
reachability it rests on is real, and this graph cannot tell prose from a subprocess call.**

The ratchet's own docstring already records one instance from the other direction (2026-09-03: a
filename written into a comment wired an orphan and silenced the gate being repaired). What is new
is that it is not a one-off — it is 34 modules, and the habit that produces it is one we ask for.

## What is next, and what was deliberately NOT done here

1. **The fix is at the edge model: a path reference on a comment line is not an edge.** It cannot
   be landed on its own — it turns 34 modules into orphans at once and refuses every lane. It has
   to be one commit that prunes comment edges AND freezes the 33 with the reason on the record, so
   the floor honestly says "nothing runs these" and any lane that wires one properly can shrink it.
   That is a change to the gate every lane passes through, with a blast radius that wants its own
   turn and its own both-doors proof. The measurement above is the whole input it needs.
2. **Freezing the 33 without the pruning would be a lie** and was rejected. They are reachable
   today; a baseline entry says "unreachable and deliberately dormant". A false positive whose
   remedy is recording something untrue is the shape this module's docstring already refuses.
3. **The comment at `vat_book.py:31` was restored byte-for-byte** after the probe. Nothing in this
   finding's measurement is committed; the census was a throwaway script and the method above is
   the artefact.
