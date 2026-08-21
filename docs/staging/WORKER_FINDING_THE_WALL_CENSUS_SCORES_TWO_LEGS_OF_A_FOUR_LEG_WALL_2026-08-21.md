**Severity:** LATENT · **Lane:** H_harness

# The wall census scores two legs of a four-leg wall, and a seam already declares one of the two it cannot see

**Found:** 2026-08-21, pass 48 of `EP6_wall_protocol_typing`, while giving the v2 message
shapes the wire they had never had. Every claim below is `observed-with-evidence` (R9), read
off the live tree; the one inference is labelled.

**Class:** `measurements_that_mirror` — the instrument's subject set is narrower than the
population it reports on, so its verdict is about the part it happens to know.

---

## Observed, with evidence

`tools/wall_channel_census.py:996`:

```python
LEG_ENVELOPE_NAMES: dict[str, str] = {"WallRequest": REQUEST_LEG, "WallResponse": RESPONSE_LEG}
```

That dict is the census's answer to its own documented question. Its comment two lines above
says how a seam declares what it owns: *"How a seam DECLARES which legs it owns: by
specialising the generic envelope. Derived from the seam's own source rather than listed here
... a seam that grows a request leg tomorrow owns the question on the day it lands, not the day
someone remembers it."*

The wall has had four primitives since pass 44, not two — `WallRequest`, `WallResponse`,
`WallNotification` (pass 43) and `WallInterim` (pass 44), all in
`interface/contracts/wall_envelope.py`. And a seam has **already made the declaration the
comment describes**, for both of the shapes the census cannot see:

```
interface/contracts/payment_observable_seam.py:337  AddacsWallNotification = WallNotification[AddacsAdvice]
interface/contracts/payment_observable_seam.py:341  BacsInputReportWallInterim = WallInterim[BacsInputReport]
```

So the mechanism the census relies on fired exactly as designed, on a name the lookup has no
key for, and the leg silently is not a leg. Measured rather than reasoned — running the
census's own `_subscript_base_name` over every `Wall*[...]` subscript in that seam file and
asking `LEG_ENVELOPE_NAMES.get` for each:

```
WallInterim          -> census leg None
WallNotification     -> census leg None
WallRequest          -> census leg 'request'
WallResponse         -> census leg 'response'
```

Two of the four resolve to `None`, and the crossing is dropped at
`tools/wall_channel_census.py:1117` and `:1141` before any per-leg verdict is formed.

**The census does not report this as a gap.** `python3 -m tools.wall_channel_census` on the
live tree ends `every frozen channel matches its list exactly.` A leg that is not in the
subject set cannot be reported missing from it — the census's own docstring names this exact
hazard for a different case: *"a leg silently dropping out of the census is exactly what this
instrument exists to prevent."*

## Why it is being filed now rather than repaired now

**The blindness predates this pass and was not caused by it.** `WallNotification`,
`WallInterim` and both seam specialisations above all existed at HEAD before pass 48 —
verifiable at `27412ab7a`. What pass 48 changed is that the blindness became *actionable*:
until this pass neither shape had a wire codec at all, so there was no migrated-to state for a
census to score, and adding the legs would have red-listed two crossings for failing to use
transport that did not exist. Now `encode_interim`/`decode_interim`/`encode_notification`/
`decode_notification` exist in `company/interfaces/wall_protocol.py`, and the question "does
this leg cross as bytes or as a call frame?" has an answer worth asking.

SELF-INTERRUPT DISCIPLINE: a harness finding is registered, not fixed in the tick that found
it. It is also the shape EP6 has refused before — tightening this atom's own instrument inside
an EP6 draw, where the lane doing the tightening is the lane the verdict is about.

## The mitigating direction, and the honest limit on it

Unlike the pass-37 case, this repair can only **add** subjects to the census and never remove
one, so there is no path by which the lane widening the instrument benefits from having widened
it. That asymmetry is why it is safe for a later EP6 pass to take.

**The limit worth stating before anyone builds it:** widening `LEG_ENVELOPE_NAMES` will
red-list the payment crossing on its two new legs, because the interim and notification legs
are *not* yet wired through the framed port in the live consumer — `decode_framed_interim` and
`decode_framed_notification` exist and `company/billing/payment_observation_consumer.py` does
not call them. That red would be CORRECT and not a regression, and it should be landed
deliberately with the baseline moved in the same commit
(`docs/design/wall_channel_census_baseline.json`), not discovered by a later lane as a wedge on
the shared tree. **Inferred:** that the red would be exactly two crossings and not more — I did
not run the widened census, and the count should be measured rather than trusted from this
sentence.

## What would discharge it

`LEG_ENVELOPE_NAMES` carries all four envelope names; `LEG_WIRE_CONSTANT` and
`LEG_DECODE_NAME` gain the corresponding entries (`INTERIM_WIRE_FIELDS` /
`NOTIFICATION_WIRE_FIELDS`, and the four new codec entry points); the baseline moves in the
same commit with the new per-leg verdicts stated. R15 mutation both ways: a seam specialising
`WallInterim[...]` with no `decode_interim` importer must be REPORTED as an unmigrated leg, and
a null control — a seam that does import it — must not be, proving the widened census is not
simply red on every new leg.

**Suggested rank:** backlog, behind EP6's remaining payable criteria (Q2, Q3, Q5, Q6, Q13,
Q14). This instrument mis-scoping does not block any of them.
