# [WORKER-FINDING] Four Expert Hours of landed work cite two atom ids the map has never carried, and a third that names a different atom (2026-08-12)

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, during the DISCOVER/FRAME draw on
`D35_the_render_site_sweep_stops_at_this_processs_edge` (LANE 3, idle atom).
**Disposition:** QUEUED. Not fixed on sight per SELF-INTERRUPT DISCIPLINE — the repair is a map
edit that has to decide *which* atom owns four Hours of shipped work, and the source comments are
the wrong place to guess from.
**Rank:** backlog, but due before the next H27 Expert Hour on `tools/couple_w2_11_d5.py` — that is
the module the citations are in, and each Hour adds another.

## Observed, with evidence

`tools/couple_w2_11_d5.py` (HEAD, 9,700 lines) attributes its render-site machinery to four atoms:

```
$ grep -n "atom D3[5-8]" tools/couple_w2_11_d5.py | sed -n '1,8p'
6025:  # at 3dp, via `fmtGap`. Coarser than the declared 4dp ...  (atom D36, Hour #20)
6035:  # SPLIT BY DOOR REGION (atom D37, Hour #21) ...
6113:  # THE RENDER SITES PAST THE COMPONENT STRINGS (atom D35, Expert Hour #19)
6889:  # THE DOOR IS NOT ONE SURFACE (atom D37, H27 Expert Hour #21)
7030:  # THE ENTRY IS THE COMPOSER'S (atom D36, Hour #20)
```

(the uncommitted working tree adds `atom D38, H27 Expert Hour #22` in `_composer_renderer_bindings`
and `measure_reader_render_sites` — a fifth.)

**Two of those ids have never existed:**

```
$ grep -c "D37\|D38" docs/design/maturity_map.yaml
0
```

Zero occurrences, anywhere in the 296-atom map — not as an id, not as a `depends_on`, not as a
`couples_with`.

**The third names a different atom.** The map's `D36` is:

```
$ python3 -c "..."   # atom D36 in docs/design/maturity_map.yaml
id: D36_bill_render_footing_and_pence
lane: D_billing_metering   value_stream: price_to_bill   epoch: 1
provenance: director_ruling
file_scope: ['site/customers/index.html', 'site/customers/_bill_render_harness.mjs', ...]
```

A printed-bill atom from a director ruling, epoch 1, whose file_scope is the customer portal. The
"atom D36" the render-site comments mean is a `tools/couple_w2_11_d5.py` Hour in epoch 3. Same id,
two subjects — the map-id-collision class, this time between a real atom and a phantom.

**And the atom whose `file_scope` the work actually sits in still reads as unstarted:**

```
id: D35_the_render_site_sweep_stops_at_this_processs_edge
level_current: 0   loop_stage: idle   provenance: proposal
file_scope: ['tools/couple_w2_11_d5.py', 'tests/tools/test_couple_w2_11_d5.py']
```

## Why it matters

This is the **inverse** of the class the repo already has memory of (`the record can outrun the
code`): here the *code* outran the record. Three consequences, all `inferred` from the above except
where marked:

1. **The citations resolve to nothing.** Anyone auditing why `reader_renders` declares
   `door:coupled-gaps#gap-val` at 3dp is sent to "atom D37" and finds no such record — the same
   dead-anchor shape as
   `WORKER_FINDING_A_MINT_SOURCES_CITED_DESIGN_ANCHOR_HAS_NEVER_EXISTED_2026-08-11.md`, but
   self-inflicted and four instances deep.
2. **D35 reads as unstarted while carrying shipped work** (`observed-with-evidence`: the module
   symbols are in HEAD, the atom is `level: 0 / idle / proposal`). Any draw on this atom re-derives
   what exists — the "a draw may already be BUILT" trap, with the map itself supplying the wrong
   prior.
3. **The Hours are not counted anywhere.** H27's Expert-Hour ledger cannot show #19–#22 against an
   atom that does not exist, so the per-atom `expert_hour` status under-reports by four.

## What would close it

Not a comment edit. One of two decisions, and it is a decision, not a lookup:

- **(a) Mint the missing atoms.** D37 and D38 become real map entries in `D_billing_metering`,
  epoch 3, `file_scope` `tools/couple_w2_11_d5.py`, each with the level the shipped work earns and
  a `simplifications` record carrying its Hour — and the "atom D36" citations are corrected to
  whichever of D35/D37 actually owns them.
- **(b) Fold them into D35.** The four Hours are one atom's arc, the citations are rewritten to
  `D35 / Hour #N`, and D35's level moves once on the whole body of work.

**Recommendation: (b).** The four Hours are consecutive passes over one sweep in one file with one
exit criterion; minting three siblings to hold them creates three more records for the same
`file_scope`, and this module already has D32–D35 sharing it. (a) is right only if the shipped work
splits along a real seam — and it does not: `reader_renders`, the door regions and the composer
provenance are one control's three stages, each of which fails without the others.

Either way the map is edited first and the source comments follow it, never the reverse.

## What this finding is NOT

It is not a claim that the render-site work is wrong. Measured today, the sweep covers the renderer
output, the composed note and the four door regions, and it works. The defect is entirely in where
that work is recorded — see
`docs/design/simplifications/D35_the_render_site_sweep_stops_at_this_processs_edge.yaml` for what
the sweep does and does not yet reach.
