# FINDING — the wall's only automated conformance control is import-shaped, so a same-step, unversioned crossing carrying 1,600 rows into the company layer is invisible to it

**Severity:** LATENT · **Lane:** W4_the_wall · **Disposition:** QUEUED (not fixed on sight)

**Atom:** `EP6_wall_protocol_typing` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-13)
**Class:** a control's subject is the mechanism the crossing happened to use (imports), not
the property the crossing is supposed to have (protocol shape), so a crossing that uses a
different mechanism satisfies every control while having none of the property

Full derivation and every number:
`docs/design/simplifications/EP6_wall_protocol_typing.yaml` (finding 2).

## Measured, on the live published artefact

`docs/reports/run_output_latest.json` (mtime 2026-08-13 17:51:47), entries parsed not sampled:

| log | entries | any entry carries `schema_version` |
|---|---|---|
| `meter_read_log` | 1,600 | **False** |
| `contact_centre_log` | 392 | **False** |
| `acquisition_funnel_log` | 4 | **False** |

The three ports these logs come from (`tools/meter_read_port.py`,
`tools/contact_centre_port.py`, `tools/acquisition_funnel_port.py`) each define a
`schema_version` field and each serialise it behind an opt-in flag:

```python
def to_log_entry(self, include_schema_version: bool = False) -> dict:
```

All three live call sites take the default — `simulation/run_phase4c_on_phase2b.py:237`,
`:324`, `simulation/run_phase2b.py:1647`. The only three occurrences of
`include_schema_version=True` in the repository are test assertions. **The version has never
crossed the seam.**

## The fail-open half (R15 killer pattern 2)

`from_log_entry` reads:

```python
schema_version=entry.get("schema_version", SCHEMA_VERSION),
```

`SCHEMA_VERSION` is the module constant *at read time*. With one version in existence this is
harmless. The first bump to `"2.0"` silently relabels every archived `"1.0"` entry as `2.0`,
because absence is indistinguishable from agreement. A version field that cannot disagree
cannot negotiate, and negotiation is the whole point of versioning the wall.

Contrast `interface/contracts/wall_envelope.py`, which has no such case: `schema_version: int`
is a required field on both `WallRequest` and `WallResponse` — structurally impossible to omit.

## Why nothing fired

`tools/epistemic_wall.py`, read directly:

```
WALL_DIRS    = ('company', 'saas', 'sim', 'simulation')
SEAM_PACKAGE = 'company.interfaces'
```

Both `tools` and `interface` are unclassified — `tests/architecture/test_epistemic_wall_ratchet.py`
asserts that deliberately (`assert not _under_seam("interface.contracts.wall_envelope")`).

The ratchet polices **import edges** between the two sides, and it is sound for that subject
and honest about it. But data crossing as a JSON list through an unclassified package is not
an import edge. So this crossing is invisible to every control in the repo:

```
producer   simulation/run_phase4c_on_phase2b.py  ->  meter_read_log (1,600 rows)
consumers  company/billing/monthly_bill_assembly.py
           company/compliance/population_sanity.py
           saas/reporting/annual_report.py
           saas/reporting/css_statement.py
```

Same-step, unversioned, and carrying `true_consumption_kwh` (SIM ground truth) in the
published bytes. **That last part is a KNOWN, already-registered latent gap** from
`W4_1_typed_adapters`' 2026-07-22 red-team (accessor-enforced, not read-enforced) — re-confirmed
here on the live artefact, not filed as new. It is repeated only because it is the same blind
spot with a second face: the accessor is enforced, the wire is not, and no control reads the wire.

## Why LATENT and not BLOCKING

Every published figure here stands, and each control's verdict holds for the subject that
control itself names. The ratchet's tests pass and mean what they say. `SCHEMA_VERSION` has never been
bumped, so the fail-open has never yet mislabelled anything. This is a real defect with no
invalidated output — the definition of LATENT. It becomes BLOCKING on the day someone bumps a
port's `SCHEMA_VERSION`, or the day a control starts claiming the wall is protocol-conformant.

## Recommendation (not asked — recorded, per NEVER_ASK_WITHOUT_RECOMMENDING)

Do **not** fix on sight (SELF_INTERRUPT_DISCIPLINE) and do **not** flip the three call sites to
`include_schema_version=True`: that would break the lossless-identity guarantee those ports are
mutation-proven on, and would put a version on the wire that still nothing reads.

Fold it into `EP6_wall_protocol_typing`'s exit criteria instead, where the atom already owes a
conformance census: every live crossing either carries a `WallRequest`/`WallResponse`, or
appears in a dated, **shrink-only** allowlist of grandfathered same-step crossings — the exact
shape `test_epistemic_wall_ratchet.py` has already proven it can keep honest. Mutation proof
(R15): inject a synthetic same-step crossing and require the suite to red on it, the way that
file's `_SYNTH_COMPANY_READS_SIM` already does for import edges.

EP6 is epoch-3 BUILD-gated (R13, director-reserved curriculum sequencing), so no code was
written for this. This document is the queue entry.

---

## Cleared as a publish-gate wedge suspect, 2026-08-20 (archival provenance)

`.publish_gate_state.json` named this document in `cited_findings` for the whole 13-run wedge
episode of 2026-08-20, so every wedge doorbell for ~7 hours told the drawing seat to dispose of it
FIRST. It was never the cause.

**Observed-with-evidence (R9):** the episode's single red was
`tests/controls/test_control_mutation.py::test_dashboard_consistency_gate_fires_on_surface_disagreement`,
whose subject is `tools/generate_dashboard_data.py::_check_consistency`. This finding's subject is
`tools/epistemic_wall.py`'s import-edge ratchet and the three `tools/*_port.py` serialisers. The
red was an `AttributeError` at call time on a function deleted by the 2026-08-20 exec-summary
retirement (03dd8c49e) — a missed consumer, not a wall-conformance question. This document's own
"Why LATENT and not BLOCKING" section already stated the condition under which it could block
anything: *the day someone bumps a port's `SCHEMA_VERSION`*. Nobody has; it is still `1`.

**Why it was cited anyway:** the same defective suspect ranking recorded in commit 159172f5e —
ranked by AST traversal depth, capped at eight, and this project's test convention puts the
subject-under-test below that cap. `cited_findings` came from that ranking, not from evidence.

**Disposition confirmed as landed, not merely recommended.** This document recommended folding the
gap into `EP6_wall_protocol_typing`'s exit criteria as a conformance census with a dated,
shrink-only allowlist. That fold is now live and enforced, not queued:
`tools/wall_channel_census.py` is the census, `company/interfaces/wall_protocol.py:91` holds
`SUPPORTED_SCHEMA_VERSIONS = frozenset({1})` with an out-of-set version raising
`UNSUPPORTED_VERSION` and an absent one raising `MISSING_FIELD` — the fail-closed answer to the
`entry.get("schema_version", SCHEMA_VERSION)` fail-open this document named — and EP6's record
(`docs/design/simplifications/EP6_wall_protocol_typing.yaml`, Q11) cites this exact sibling defect
as the shape it exists to avoid. `LEG_DECODE_NAME` is now a per-leg enumerated tuple, so a leg
dropping out of the census reds the gate.

**What is still owed** is the atom's, not this document's: the three live logs
(`meter_read_log`, `contact_centre_log`, `acquisition_funnel_log`) still cross same-step and
unversioned, and EP6 holds that as outstanding build work. Archived to `done/` because the queue
entry has been consumed by the atom that owns it.
