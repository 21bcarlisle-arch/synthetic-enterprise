# EP6 — the vintage stamp's path, traced end to end

**Atom:** `EP6_wall_protocol_typing` · **Pass:** DISCOVER/FRAME only, 2026-08-18 (third pass of the day)
**Level stays 0, `loop_stage` stays idle.** No BUILD code written, no protocol designed, no adapter
started — this atom is epoch-3 BUILD-gated on director-reserved curriculum sequencing (R13), and
`EPOCH_GATING_AND_ATOM_AUTHORSHIP` Rule 1 makes DISCOVER/FRAME available while BUILD is not.

**Measured at:** HEAD `3b153f2f0`. Shipped modules read as they sit on disk; the live published
artefact `docs/reports/run_output_latest.json` (4,154,354 bytes, mtime 2026-08-18 23:44:24, 93
top-level keys) parsed in full; the round-trip in §4 executed against that artefact's real entries.
Nothing monkeypatched, nothing regenerated, no network. Everything is `observed-with-evidence` (R9)
unless labelled `inferred`.

**This document is the fifth in the EP6 DISCOVER set**, beside the 2026-08-15 conformance census,
the 2026-08-17 protocol-typing pass, and the two 2026-08-18 passes (dependent-atom property audit,
AWACS scope audit). It is not a replacement for any of them.

---

## 0. The question this pass was drawn to answer

The first 2026-08-18 pass closed by naming two open questions and, for each, the method that would
resolve it. This pass takes **NEW-2**, quoted from that pass's own register entry:

> whether the vintage stamp's absence from the artefact is a SERIALISATION gap (channel C messages
> are in-process objects that never reach the report) or a POPULATION gap (fields left at defaults)
> — that distinction decides whether recommendation 2 is plumbing or correctness, and this pass did
> not separate them.

with the stated resolution method: *a live call-path trace from a `WallRequest`/`WallResponse`
construction site through to whatever, if anything, writes envelope fields into
`run_output_latest.json`.*

**Verdict: SERIALISATION, on both families, with no population gap anywhere — but the either/or in
the question is too coarse to be actionable, because the two families fail at different points on
the path and the two fixes are different in kind.** §5 states what that costs recommendation 2.

---

## 1. The population half — complete, both families

### 1.1 Envelope family (channel C)

An AST walk of every production `.py` in the tree (tests, `__pycache__` and the stale worktree of
§6 excluded), collecting every call to `WallRequest`/`WallResponse` or any per-crossing
specialisation of them, and recording the `schema_version` keyword actually passed:

| module | line | constructed | `schema_version=` |
|---|---|---|---|
| `company/comms/conversation_generator.py` | 228 | `WallRequest` | `SCHEMA_VERSION` |
| `company/interfaces/sim_interface.py` | 220 | `FlexEnrolmentWallRequest` | `SCHEMA_VERSION` |
| `sim/flex_dispatch.py` | 337 | `FlexDispatchWallResponse` | `SCHEMA_VERSION` |
| `sim/flex_dispatch.py` | 384 | `FlexSettlementWallResponse` | `SCHEMA_VERSION` |
| `sim/flex_dispatch.py` | 840 | `FlexDispatchWallResponse` | `SCHEMA_VERSION` |
| `sim/flex_dispatch.py` | 886 | `FlexSettlementWallResponse` | `SCHEMA_VERSION` |
| `simulation/conversation_response.py` | 414 | `WallResponse` | `SCHEMA_VERSION` |
| `simulation/payment_seam_adapter.py` | 290 | `WallResponse` | `SCHEMA_VERSION` |
| `simulation/payment_seam_adapter.py` | 302 | `WallResponse` | `SCHEMA_VERSION` |
| `simulation/payment_seam_adapter.py` | 331 | `WallResponse` | `SCHEMA_VERSION` |

**10 of 10 sites populate the field, every one of them from the crossing's own module constant —
never a call-site literal, never a default.** The three constants are
`interface/contracts/flex_observable_seam.py:56`, `conversation_seam.py:74` and
`payment_observable_seam.py:62`, each `SCHEMA_VERSION = 1`.

This is structurally guaranteed, not merely observed: neither `WallRequest.schema_version` nor
`WallResponse.schema_version` carries a default in `interface/contracts/wall_envelope.py`, so a
construction that omitted it would raise `TypeError` at the call site. A population gap is not
reachable on this family.

### 1.2 Port family (channel D)

Three of the five `tools/*_port.py` ports carry `SCHEMA_VERSION = "1.0"` and expose it as a
dataclass field default (`contact_centre_port.py:53,74`, `meter_read_port.py:39`,
`acquisition_funnel_port.py:60`), so **every instance is stamped by construction**.

**Correction to the 2026-08-17 pass, recorded here because this store is append-only.** That pass
wrote "the 5 W4_1 ports (`tools/*_port.py`) are typed VALUES … with `schema_version` fields that are
structurally present but … never populated on the wire." Two parts of that are wrong at this HEAD:

* it is **3 of 5, not 5**. `tools/credit_bureau_port.py`'s `CreditCheckResult` has no version field
  at all, and `tools/market_data_port.py` is a bare `Protocol` with no message dataclass to hold one;
* "never populated" conflates the two things NEW-2 exists to separate. The field **is** populated on
  every instance. What never happens is that the populated value is *emitted* — §2.2.

The conclusions that pass drew do not depend on either correction.

---

## 2. The serialisation half — the gap, and it is two different gaps

### 2.1 Envelope family: there is no wire to be absent from

**Zero production reads of `.schema_version` on any envelope.** A whole-repo grep returns eight
hits: five in tests (`tests/interface/test_wall_envelope.py:29`,
`tests/interface/test_payment_observable_seam.py:70`, and three port tests), and three in
`tools/*_port.py` that are the ports' own unrelated `self.schema_version`. **No production consumer
of an envelope reads the field.**

The code that holds an envelope longest is `company/billing/payment_observation_consumer.py`. Across
its six observation handlers (lines 484–558) it forwards `response.observed_at` and
`response.correlation_id` into ledger events and **drops `schema_version` and `status`**. That is the
end of the path: the envelope is unwrapped, two of its five metadata fields are carried into a
company-side record, the vintage stamp is not among them, and no serialiser for an envelope exists
anywhere in the tree.

So for this family the answer is serialisation in the strongest sense — **not a switch that is off,
but a wire that was never built.** There is nothing to plumb into.

### 2.2 Port family: the wire exists, and the stamp is switched off

Each of the three stamped ports has a serialiser, `to_log_entry(include_schema_version: bool = False)`
(`contact_centre_port.py:92`, `meter_read_port.py:96`, `acquisition_funnel_port.py:159`), which emits
the stamp when the flag is set and omits it otherwise. Its docstring names the reason:

> `include_schema_version` is opt-in so the default output is byte-for-byte the pre-conversion
> `contact_centre_log` entry (lossless identity round-trip); callers migrating to the versioned wire
> can set it True.

**Every production caller declines. Every caller that opts in is a test.**

| caller | file:line | flag |
|---|---|---|
| meter read log build | `simulation/run_phase4c_on_phase2b.py:270` | default → `False` |
| contact centre log build | `simulation/run_phase4c_on_phase2b.py:357` | default → `False` |
| acquisition funnel log build | `simulation/run_phase2b.py:1705` | default → `False` |
| — | `tests/tools/test_contact_centre_port.py:70` | `True` |
| — | `tests/tools/test_meter_read_port.py:48` | `True` |
| — | `tests/tools/test_acquisition_funnel_port.py:90` | `True` |

Those three production call sites are exactly the ones that build the three published log keys. So
the stamp's absence from the artefact is, on this family, **one default argument on three lines** —
and the capability is exercised in the suite only by the three callers that turn it on.

This is a disclosed, deliberate design, not a defect: the flag's own docstring states the migration
intent, and the migrating caller it anticipates simply does not exist yet.

---

## 3. The artefact agrees

`docs/reports/run_output_latest.json`, 4,154,354 bytes, 93 top-level keys, raw substring counts:

| token | occurrences |
|---|---|
| `schema_version` | 0 |
| `correlation_id` | 0 |
| `observed_at` | 0 |
| `valid_time` | 0 |
| `NOT_KNOWABLE_YET` | 0 |
| `WallStatus` | 0 |
| `wall_` | 0 |

The three port-built keys are present and stamp-free: `meter_read_log` (1,600 entries),
`contact_centre_log` (392), `acquisition_funnel_log` (4). No entry in any of them carries a
`schema_version` key.

---

## 4. The ports' own round-trip claim, tested against the live population

The docstring in §2.2 makes a falsifiable claim — that the default emission is a **lossless identity**
on the pre-conversion dict. Tested on the real published data rather than a fixture: all **1,996**
published entries parsed back through their own `from_log_entry` and re-emitted with the default flag.

| key | n | parse errors | identity mismatches | already stamped |
|---|---|---|---|---|
| `contact_centre_log` | 392 | 0 | 0 | 0 |
| `meter_read_log` | 1,600 | 0 | 0 | 0 |
| `acquisition_funnel_log` | 4 | 0 | 0 | 0 |

**The claim holds: 1,996 of 1,996 round-trip byte-identically.** Flipping the flag on adds exactly
one key on every family — `{"schema_version": "1.0"}` — and changes nothing else.

That measurement is what makes recommendation 1 below a *bounded* change rather than an assertion: the
flip's blast radius on the live population is one added key per entry, measured on the whole
population, not sampled.

---

## 5. What this costs the first 2026-08-18 pass's recommendation 2

That pass recommended, for EP6's first BUILD move when the director opens epoch 3:

> the vintage stamp reaching the wire: the only unanimous requirement, already present as fields on
> both envelope shapes, absent from every published key — populate-and-prove, not design.

Two clauses of that survive and one does not.

* **"Absent from every published key" — confirmed** (§3), independently and at a newer HEAD.
* **"Populate-and-prove" — wrong on the population half.** Nothing needs populating. Both families
  are fully populated already (§1); the recommendation was written against the possibility of
  default-valued fields, and that possibility is now excluded.
* **"The vintage stamp reaching the wire" is not one move.** It is two, and only one is cheap:
  * **ports** — a three-call-site default flip, blast radius measured (§4). Plumbing.
  * **envelopes** — no serialiser exists, so this is the question of *whether an envelope is ever
    serialised at all*, which is protocol design and squarely the BUILD-gated half of this atom.
    Not plumbing, and not something a conformance pass can close.

---

## 6. A measurement hazard worth naming

The §1.1 census initially returned **20** construction sites — exactly double — because
`.claude/worktrees/agent-a7e53b3f1c77109b1` (registered in `git worktree list`, branch
`worktree-agent-a7e53b3f1c77109b1`, HEAD `2539d3a90`) is a live git worktree **inside the repo**
carrying a full duplicate of `company/`, `sim/` and `simulation/`. Any repo-wide `rglob('*.py')` or
`grep -r` census double-counts through it unless it is excluded by name.

This belongs to the class already queued as `in_progress/WORKER_FINDING_FORK_BRANCH_TRIAGE_2026-08-03.md`
and is recorded here rather than filed again, so a future census in this atom does not rediscover it
as a novelty.

---

## 7. Recommendations — recorded, not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **Re-word recommendation 2 of the first 2026-08-18 pass** to the split in §5: ports = a measured
   three-line flip, envelopes = a design question. A single recommendation covering both understates
   the second and overstates the first.
2. **The port flip should not be EP6's headline first move, despite being the cheapest thing on the
   board.** This atom's own `gain` is "go-live becomes a transport swap instead of a redesign" — that
   is about the envelope family. Flipping the port flag makes the published artefact carry a version
   stamp for the pattern EP6 is *least* about, while the family the atom is named for still has no
   wire. Do it as EP6's cleanup; do not let it stand in for the atom.
3. **Do not unify the two version types speculatively.** The two families disagree: envelopes use
   `int` `1`, ports use `str` `"1.0"`. No shape has diverged yet, so reconciling now is
   adapters-for-future-adapters (SIMPLICITY GUARD, which this atom's `origin_note` names by name).
   Record the disagreement; settle it at the first real second version, when there is evidence about
   which discipline the wall actually needs.
4. **Do not delete `include_schema_version` as dead code.** It has no production caller, but its
   docstring honestly names the migrating caller it is waiting for, and it is precisely the seam
   recommendation 1's flip would use.

---

## 8. Open questions after this pass

* **NEW-2 — CLOSED by this document.** Serialisation, both families, no population gap; the
  either/or was too coarse and §5 records the finer answer.
* **NEW-3 (opened here):** which version discipline the protocol layer standardises on — monotone
  `int` (envelopes) or semver `str` (ports). Not decided; deciding it is BUILD.
* **OQ6 (carried, unchanged):** identity of the 93rd published key. Untouched by this pass.
* **OQ2–OQ5 of the 2026-08-17 pass:** carried unchanged.

**No new `WORKER_FINDING` filed** (`SELF_INTERRUPT_DISCIPLINE`). The §1.2 correction is a within-atom
correction to this atom's own append-only register, which is that register working as designed; the
§2.2 flag is disclosed in its own docstring; the §6 worktree belongs to a class already queued.
