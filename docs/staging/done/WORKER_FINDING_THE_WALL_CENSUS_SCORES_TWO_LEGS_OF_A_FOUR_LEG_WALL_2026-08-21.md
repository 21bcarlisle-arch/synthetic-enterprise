**Severity:** LATENT · **Lane:** H_harness

# The wall census scores two legs of a four-leg wall, and a seam already declares one of the two it cannot see

**Found:** 2026-08-21, pass 48 of `EP6_wall_protocol_typing`, while giving the v2 message
shapes the wire they had never had. Every claim below is `observed-with-evidence` (R9), read
off the live tree; the one inference is labelled.

**Class:** `measurements_that_mirror` — the instrument's subject set is narrower than the
population it reports on, so its verdict is about the part it happens to know.

**Discharged:** `tests/tools/test_wall_channel_census.py::test_MUTATION_an_INTERIM_leg_with_no_decoder_is_reported_unmigrated`,
`tests/tools/test_wall_channel_census.py::test_MUTATION_a_NOTIFICATION_leg_with_no_encoder_is_reported_unmigrated`,
`tests/tools/test_wall_channel_census.py::test_NULL_CONTROL_a_seam_wired_on_all_four_legs_is_wire_borne_and_names_each`,
`tests/tools/test_wall_channel_census.py::test_MUTATION_dropping_a_leg_from_the_lookup_takes_it_OUT_OF_THE_SUBJECT_SET`,
`tests/tools/test_wall_channel_census.py::test_the_census_SUBJECT_SET_is_the_whole_envelope_family_not_two_of_it`
— EP6 pass 51, landed e84b6d54c. The first two are the mutations this document asked for, the
third is the null control that stops the widened census being red on every new leg by
construction, and the fourth restores the old two-key lookup and watches the green come back.
See the DISCHARGED section at the foot of this document for the two predictions it made that
did not hold, and for the one defect it surfaced and did not close.

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

---

## DISCHARGED 2026-08-21, EP6 pass 51, `e84b6d54c`

Taken by a later EP6 pass exactly as this document reserved it for one, and on the asymmetry it
named: the repair could only ADD subjects to the census, so the lane widening the instrument
could not benefit from having widened it.

`LEG_ENVELOPE_NAMES` now carries all four envelope names; `LEG_WIRE_CONSTANT`,
`LEG_DECODE_NAME` and `LEG_ENCODE_NAME` gained the matching rows; `WIRE_FIELD_CONSTANTS`,
`wire_field_sets_by_leg` and `leg_payload_types` derive from a single `LEGS` tuple, so the
two-leg assumption is gone from the code rather than papered over at the lookup. R15 both ways,
run rather than asserted: an interim leg whose decoder is removed is now reported
`interim=ENCODED-only` and reds its seam, where the pre-widening census returned the same tree
WIRE-BORNE and green; a notification leg with no encoder does the same; the null control — a
seam wired on all four legs — comes back `wire` on all four, which is what proves the widened
census is not simply red on every new leg. A third test restores the old two-key lookup by
monkeypatch and watches the green come back, so this document's own claim is now a test.

**Two things this document predicted did not hold, and both are recorded rather than quietly
dropped**, because it asked for them to be measured rather than trusted:

1. **The predicted red did not happen.** The stated limit was that widening would red-list the
   payment crossing on its two new legs, `decode_framed_interim` / `decode_framed_notification`
   having no caller. Pass 50 wired both into `company/billing/payment_observation_consumer.py`
   (`:1247`, `:1272`) between this filing and its discharge, so the widened census reports
   `interim=wire` and `notification=wire`. Checked for a false green rather than accepted: the
   world side builds each exact key set (`simulation/payment_seam_adapter.py:1137`, `:1164`),
   the company side decodes, and the two are distinct modules, which is what
   `_leg_is_transported` requires.
2. **The baseline did not move**, contrary to "the baseline moves in the same commit".
   `docs/design/wall_channel_census_baseline.json` is a channel-MEMBERSHIP list, and widening
   the leg tables added no member to any channel.

**And the filing itself was an instance of a second class.** This document states
`**Class:** measurements_that_mirror` in a bold line near its head — prose the classifier cannot
read. `classify_file` returned `None` for it, `--check` PASSED with it live and unlisted, and
the class document never learned it existed: the exact fail-open hole `finding_classes.py`
documents at `_CLASS_REGISTRATION_HEADING_RE`, whose own cited precedent
(`WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_THAT_IS_IN_NO_COMMIT_2026-08-19`)
went six passes the same way. The registration below is the machine-readable act that fixes it
for this document. **The hole itself is NOT repaired here** — a finding that declares its class
only in prose is still silently unclassed, and that is a live harness defect this discharge does
not close.

## Class registration

Belongs to `measurements_that_mirror`. The instrument's subject set was narrower than the
population it reported on, so its verdict was about the part it happened to know — and, unlike
the existing members, the narrowing was invisible from the report, which ended `every frozen
channel matches its list exactly` while answering for half the wall.
