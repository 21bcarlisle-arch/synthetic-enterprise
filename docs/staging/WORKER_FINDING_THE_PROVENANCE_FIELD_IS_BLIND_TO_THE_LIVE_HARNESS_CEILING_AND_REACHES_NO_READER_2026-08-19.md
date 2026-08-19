**Severity:** LATENT · **Lane:** D_billing_metering

# The provenance field is blind to the live harness ceiling and reaches no reader

**Found:** 2026-08-19, D30 DISCOVER/FRAME pass 7 (worker tick, LANE 3 idle draw). Measured in a
detached worktree at HEAD `830c47d9c` (`git worktree add --detach`) — the desk tree's `file_scope`
carries another lane's STAGED, uncommitted changes to both `tools/couple_w2_11_d5.py` and its test
file this tick, so the desk tree could not be the instrument. Shipped `build_scenario` /
`measure_scenario_constant_census` / `score_triad` / `LivePaymentTriad`, n=300, seed 7. Every claim
below is `observed-with-evidence` unless labelled otherwise (R9).

**Class:** controls that cannot fail — the control certifying the distinction asserts, in its own
closing comment, the one property it does not test, and is blind to it by construction.

---

## What the field is for

The 2026-08-18 repair (`9718066ce`) added `scored_company_window_source` to
`measure_scenario_constant_census` (`tools/couple_w2_11_d5.py:6845`). Its own comment states the
job:

> WHERE THAT NUMBER CAME FROM. A reader cannot otherwise tell a company that genuinely holds 400d
> from a caller that supplied no company at all — and those were indistinguishable, on the
> published artefact, for as long as the defect above lived.

Its two values are `"harness_constant"` (no window passed) and `"scored_consumer"` (a window
passed). Three legs below, each measured.

## LEG 1 — it reaches no reader, and NOT by the route its two siblings die on

At HEAD, on the shipped `score_triad` path, n=300 seed 7:

```
belief.components: [... 'scored_company_is_inert', 'scored_company_window_days' ...]
scored_company_window_source in components: False
```

Counted over the module source: `components["scored_company_is_inert"]` — 2 writes (the two belief
dimensions, `:11070` and `:11117`); `components["scored_company_window_days"]` — 2 writes (`:11072`,
`:11119`); `components["scored_company_window_source"]` — **0**. It is also rendered in no prose:
`scenario_constant_census_caveat` mentions it 0 times, while quoting
`scored_company_window_days` and `scored_company_is_inert` in both branches (`:7086`, `:7095`).

This is a DIFFERENT death from D27 DISCOVER pass 7's already-filed lift defect (the ledger writer
selecting components by the last seven characters of a key, `459d41aea`). The live entry at
`docs/observability/coupled_gap_ledger.json`, `W2_11_payment_behaviour_source`, `measured_at`
2026-08-19T02:01:26Z, `run_git_commit` `830c47d9c` = HEAD, carries
`components.dimension_caveats.belief` with exactly two keys — both `*_caveat` — so the two sibling
fields die AT THE LIFT and a lift repair rescues them. The source field dies one step earlier, at
the components write. **Repairing D27's lift leaves this field exactly as dark as it is today**,
which is why it is filed separately rather than as another instance of that finding.

## LEG 2 — the label reads the CALL SHAPE, and the live company's memory is a harness constant

n=300, seed 7, one book, four call shapes:

| window passed | what that number IS | `scored_company_window_source` | `is_inert` |
|---|---|---|---|
| `None` | the offline harness constant, by default | `harness_constant` | True |
| `90` | the SHIPPED `PaymentObservationConsumer` default | `scored_consumer` | False |
| `400` | `DD_FAILURE_WINDOW_DAYS`, the harness constant, via a consumer | `scored_consumer` | True |
| `6000` | `_RUN_SPANNING_WINDOW_DAYS`, the LIVE harness ceiling, via a consumer | `scored_consumer` | True |

Rows 1 and 3 publish the SAME number, 400, and the field does separate them — that is its literal
stated purpose and it meets it. What the vocabulary asserts is PROVENANCE, and what the code reads
is whether the caller passed an argument. On the offline scenario the two coincide by construction,
because a defaulted call is the only harness-constant path there. On the live path they diverge:

```
LivePaymentTriad() default consumer window = 6000  == _RUN_SPANNING_WINDOW_DAYS: True
census called the LIVE way -> source = scored_consumer  window = 6000
```

`background/live_payment_triad.py:120` — `_RUN_SPANNING_WINDOW_DAYS = 6000`, with the comment "A
live run covers ~2016-2025 (~3650 days); a comfortable ceiling keeps the belief severity count on
the same all-time basis as the truth count", and `:645` makes it the constructor default. That is a
confounder-removing harness constant of D27's and D29's exact rhetorical shape ("generous on
purpose", "comfortably past") — this atom's whole subject — and the one field that names provenance
calls it the scored consumer's.

The published prose inherits the attribution. Today's live entry, verbatim: *"AND THE SCORED
COMPANY SITS OUTSIDE IT: it holds 6000d of memory, 2531d past the top of the band, so every belief
figure here is read at a point where the one company parameter these dimensions depend on is inert
by construction."* A reader meets "the scored company holds 6000d of memory" as a fact about a
supplier. It is a fact about `background/live_payment_triad.py:120`. (The `2531` is note 6's
already-filed invoice-population headroom defect, still live at HEAD and NOT re-filed here.)

## LEG 3 — the fail-closed keyset cannot ever raise on it

`scenario_constants()` (`:6623`) derives the census subject from `build_scenario`'s AST, keeping
module-level names that are `isupper()` and do not start with `_`. Measured:

```
scenario_constants() = ('AS_OF_BUFFER_DAYS', 'BILLING_CYCLE_SPREAD_DAYS', 'BILL_AMOUNT_GBP',
                        'DD_FAILURE_WINDOW_DAYS', 'FIRST_DUE_DATE', 'N_PERIODS',
                        'PAYMENT_TERMS_DAYS', 'PERIOD_SPACING_DAYS')
'_RUN_SPANNING_WINDOW_DAYS' in subject: False
```

Excluded twice over — a different module, and `_`-prefixed. `_check_census_is_complete` (`:6904`)
promises "a constant added to the scenario and never censused raises here instead of waiting for an
Hour to trip over it". That guarantee is scoped to the offline scenario builder. The constant that
places the LIVE published company relative to the band it is scored in is outside the scope by
construction, and the census reports on it without naming it.

## The control that certifies the distinction says the false thing itself

`tests/tools/test_couple_w2_11_d5.py::test_R15_the_census_goes_green_on_the_constant_with_the_defect_untouched`
(`:8599`) closes with:

```python
    # A REAL 400d company and a DEFAULTED one agree on every number and differ
    # only in the field that says which they are -- so the provenance field is
    # the whole of the distinction, and it is published.
    ...
    assert differing == {"scored_company_window_source"}, differing        # :8618
```

"and it is published" is false — 0 component writes, 0 prose renders, absent from the live entry —
and the assertion cannot fail on it: both operands are return values of
`measure_scenario_constant_census`, so the control's subject is the in-memory dict and its claim is
about the reader. R15 killer pattern: the check is one seam short of the property it certifies.

Its sibling `test_the_live_publishers_company_is_reported_at_its_own_window` (`:8586`) names 6000
explicitly, asserts `scored_company_is_inert is True`, and has no clause noticing that the company
whose memory it is reporting is the harness's own ceiling.

## What this pass does NOT claim

No published number is wrong because of this finding — LATENT, not BLOCKING. `6000` IS the window
the live consumer holds, `is_inert` IS True on the live book, and the belief figures are what they
are. What is absent is the mark that would let a reader tell a supplier's policy from a harness
ceiling, and what is false is a control comment asserting that mark is published. Leg 2 says
nothing against the 6000 choice itself: the module docstring's reason for it is sound, which is
precisely what D27 and D29 each said about the constant they found.

## What an exit test must show (item 9 on D30's list)

1. `scored_company_window_source` written to `components` on both belief dimensions AND rendered in
   `scenario_constant_census_caveat`, with the live entry as the R11 evidence — asserted at the
   written artefact, not at the return dict, which is the seam the existing control stops short of.
2. A provenance answer that reads the NUMBER's origin, not the call shape: `_RUN_SPANNING_WINDOW_DAYS`
   and `DD_FAILURE_WINDOW_DAYS` passed through a consumer must not label as a supplier's own policy,
   with the shipped 90d default as the null control that must.
3. `:8618`'s comment corrected or its claim made true, and mutation-proven — a revert that removes
   the component write must turn the control RED.
4. The census's completeness subject extended past `build_scenario`'s AST to whatever constant
   supplies the scored company's window on the path that PUBLISHES, so a tenth such constant raises
   rather than waiting for a pass to trip over it.

**Queued, not fixed on sight (SELF_INTERRUPT_DISCIPLINE).** The repair is BUILD on
`tools/couple_w2_11_d5.py` + `tests/tools/test_couple_w2_11_d5.py` — D30's `file_scope`, and D30 is
`loop_stage: idle`.
