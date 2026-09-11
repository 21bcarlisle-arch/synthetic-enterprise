# FINDING — the capture tool's default output path overwrites, in place, the artefact two other instruments read as their default

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Class:** `figures_on_a_superseded_clock` (primary), `controls_that_cannot_fail` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0
**Subject:** `tools/capture_departure_factors.py::DEFAULT_OUT`,
`tools/fit_departure_hazards.py::DEFAULT_TABLE`,
`tools/split_price_response_by_curve_position.py::DEFAULT_BASELINE`.

---

## What is true, measured at `c6239eec1`

`SEAT_FINDING_THE_INSTRUMENT_JUDGES_THE_WORLD_ON_A_SUPERSEDED_CAPTURE...` (discharged 2026-09-03)
closed the instrument's own default and named this residue explicitly rather than fixing it blind:
*"`tools/fit_year_level_anchor.py`, `tools/fit_departure_hazards.py` and
`tools/split_price_response_by_curve_position.py` all default to it too; that is three more
instruments on the superseded clock, and each needs its own read before it is moved."*

One of those three has since been closed correctly. The other two have not, and a fourth was not on
the list at all:

| module | default | still `c2`? |
|---|---|---|
| `tools/measure_departure_level.py::DEFAULT_TABLE` | the live capture | no — repointed |
| `tools/fit_year_level_anchor.py::DEFAULT_TABLE` | `_instrument.DEFAULT_TABLE` | no — **derives**, which is the right shape |
| `tools/fit_departure_hazards.py::DEFAULT_TABLE` | `docs/reports/c2_departure_factors.json` | **YES** |
| `tools/split_price_response_by_curve_position.py::DEFAULT_BASELINE` | `docs/reports/c2_departure_factors.json` | **YES** |
| `tools/capture_departure_factors.py::DEFAULT_OUT` | `docs/reports/c2_departure_factors.json` | **YES, and it WRITES there** |

`fit_year_level_anchor` is the model: it does not name a capture, it takes the instrument's. A
default that derives cannot go stale; a default that names cannot help it.

## The fourth one is a different class from the other two, and it is why this is filed rather than noted

`fit_departure_hazards` and `split_price_response_by_curve_position` **read** a stale artefact. That
is the catalogued superseded-clock shape and it is bounded: a wrong number, from a named file, that
a reader can trace.

`tools/capture_departure_factors.py` **writes** to that same path when invoked with no argument.

```
DEFAULT_OUT = PROJECT / "docs" / "reports" / "c2_departure_factors.json"
target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
```

So `python3 tools/capture_departure_factors.py`, with no argument, silently replaces a **committed**
artefact with a run from whatever working tree the caller happens to be in — and it writes the SVT
sibling beside it, or does not, depending on that tree. The two fitters above then read the result
as their default and attribute it to `c2`.

**This is not hypothetical and it is not new.** `simulation/departure_level_anchor.py`'s own
docstring records it already happening once, and the wording is worth quoting because it describes
this mechanism without naming it as a live one:

> *"Its docstring named `docs/reports/c2_departure_factors.json` as its fit input; that file was
> overwritten in place by `b46318106` a day after the block landed, and the artefact carrying the
> name today RAN UNDER THIS BLOCK. The citation resolved, at HEAD, to a capture produced two steps
> later by its own successor — `figures_on_a_superseded_clock`, with a stable path over a moving
> run."*

That entry treats the overwrite as a past event that was diagnosed. **The default that caused it is
still the default.** A stable path over a moving run is exactly what an argument-less invocation
still produces, and the diagnosis did not remove the mechanism.

## What makes it LATENT and not BLOCKING

Nothing published reads `c2` today. The instrument was repointed, the band verdict comes off the
live capture, and `stale_anchor_refusal` now refuses a capture that did not run under the live
anchors — so a `c2` overwritten tomorrow could not silently become a band verdict. The two fitters
are calibration tools invoked by hand, not by any daemon or gate.

It is LATENT rather than RECORDED because the damage is done by an invocation that looks correct.
Nobody types a destructive command here; they type the tool's own documented no-argument form.

## The repair, and why it is not in the commit that files this

Three changes, and they are not the same change:

1. **`capture_departure_factors` should have no default output at all.** A capture is named by the
   person taking it, or it is not taken. This is the one that matters and it is a refusal, not a
   repoint: an argument-less invocation should exit non-zero naming the missing argument. A default
   pointing at a *fresh* name would only move the trap.
2. **`fit_departure_hazards` and `split_price_response_by_curve_position` should DERIVE** from
   `measure_departure_level.DEFAULT_TABLE`, as `fit_year_level_anchor` already does. Not repoint —
   derive. A repoint to `c6` goes stale on the next capture and this document gets re-filed.
3. **The control keyed to the property, not to today's answer:** no module under `tools/` may name a
   capture file as a default; it derives from the instrument or it requires an argument. That fails
   on a new stale default and passes when the capture changes, which is the direction round a
   control has to fail.

Not in this commit because (1) changes the signature of a tool three documents give no-argument
invocation instructions for, and each of those call sites needs reading before the refusal lands —
which is the same discipline the discharged finding applied to this list in the first place, and the
reason it stopped where it did rather than fixing all three blind.

## What is NOT claimed here

- **Not** that `c2` has been overwritten again since `b46318106`. I did not check its content
  against any run; the claim is about the mechanism being live, not about a second instance.
- **Not** that the two fitters are currently producing wrong published numbers. Nothing published
  reads them today. If either is run before item (2) lands, its output is on the superseded clock
  and that is the whole of the claim.
