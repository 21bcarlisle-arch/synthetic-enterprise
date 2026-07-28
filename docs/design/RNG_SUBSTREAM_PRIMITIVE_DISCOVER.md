# RNG substream primitive — DISCOVER pass (doc-only, no BUILD)

**Source mint:** `docs/staging/in_progress/PLANNER_MINTED_rng_substream_primitive_2026-07-28.md`,
itself from `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §2.2 +
Acceptance item 2 (committed `29361d1c2`).

**This pass does not edit `maturity_map.yaml`, write sim/company code, migrate any caller, or
change `level_current`.** Scope is this one file only, per the assigning instruction. The BUILD
half is `blocked_on: director_build_open` and is untouched here.

---

## 1. Census — every seeded-substream derivation found

The mint's provenance line estimated "≥8"; **the real count of `def _substream` is 11**, and a
broader sweep for functionally-equivalent (differently-named) seeded-substream derivations finds
**5 more constructs**, for **16 total** across `simulation/` and `sim/`. Nothing found in
`company/` or `saas/` (they consume these modules' *outputs*, not their RNGs — wall-clean).

### 1.1 The 11 exact `def _substream` copies

| # | File:line | Signature | Call sites (same file) |
|---|---|---|---|
| 1 | `simulation/conversation_response.py:105` | `_substream(base_seed: int, name: str)` | 5 |
| 2 | `simulation/life_events.py:266` | `_substream(base_seed: int, name: str)` | 2 (+1 fan-out dict comprehension over `_LIFE_EVENT_SUBSTREAMS`) |
| 3 | `simulation/population_draw.py:143` | `_substream(base_seed: int, salt: str = "")` | 12 |
| 4 | `simulation/household_budget.py:106` | `_substream(base_seed: int, salt: str = "")` | 6 |
| 5 | `simulation/sme_distress.py:186` | `_substream(base_seed: int, name: str)` | 3 (+1 fan-out) |
| 6 | `simulation/premise_demand.py:249` | `_substream(base_seed: int, salt: str = "")` | 2 |
| 7 | `simulation/willingness_classification.py:118` | `_substream(base_seed: int, name: str)` | 2 |
| 8 | `simulation/adoption_geography.py:235` | `_substream(base_seed: int, name: str = ADOPTION_SUBSTREAM)` | 2 |
| 9 | `simulation/self_rationing.py:156` | `_substream(base_seed: int, name: str)` | 4 (+1 fan-out) |
| 10 | `simulation/dd_attribution.py:181` | `_substream(base_seed: int, name: str)` | 5 |
| 11 | `simulation/payment_behaviour_source.py:145` | `_substream(base_seed: int, name: str)` | 9 (some via `_period_substream` wrapper) |

Confirmed via `grep -rn "import _substream"` across `simulation/ company/ sim/ saas/`: **zero
cross-module imports**. Every module defines and calls its own private copy — this is *why* there
are 11 rather than 1; no shared primitive module exists yet (e.g. no `simulation/rng_substream.py`).

### 1.2 Five more constructs implementing the same concept under a different name

| Construct | File:line | Notes |
|---|---|---|
| `_adapter_substream(customer_id, period_index, name)` | `simulation/payment_seam_adapter.py:149` | Docstring states it "mirrors `payment_behaviour_source._substream`'s sha256-stable-seed pattern exactly" — a deliberate, documented clone (4-part key: namespace::name::customer_id::period_index) |
| `_cohort_substream(customer_id, base_seed, axis)` | `simulation/population_draw.py:390` | A **second, distinct** derivation inside the same file as construct #3 above — explicitly "a different stream NAME entirely" per its own docstring |
| `_u01(*parts)` | `simulation/segment_debt_obligation.py:274` | Same sha256 idea but returns a `float` directly (`digest[:8]/2**64`), not a `random.Random`; single-colon `":".join(parts)` keying |
| `_delivery_rng(seed)` | `sim/flex_dispatch.py:131` | Returns **`np.random.Generator`** (numpy PCG64), not `random.Random` — a different RNG engine family entirely, not just a different hash |
| inline pattern | `sim/scenario/intraday_shape.py:131` | `random.Random(f"{seed}\|intraday\|{date_str}")` — passes a **raw string** as the seed, relying on CPython's own internal string-seeding (SHA-512-based) rather than an explicit hash. No dedicated function at all despite the module docstring's C-S2 claim (line 38). |

---

## 2. The diff — where they genuinely diverge (the core finding)

All 11 `def _substream` copies *look* alike (same docstring boilerplate, same C-S2 claim, same
return type) but resolve to **three structurally different key-derivation formulas**, plus the
5 named-differently constructs add **two more**. This is not a cosmetic difference — different
formulas over the identical `(base_seed, name)` input produce different digests, hence different
draw sequences.

### Formula A — unnamespaced, `base_seed:name`, single colon
```
digest = hashlib.sha256(f"{base_seed}:{name}".encode()).digest()
return random.Random(int.from_bytes(digest[:8], "big"))
```
Used by: `conversation_response.py`, `life_events.py`, `adoption_geography.py` (3 modules).
**No per-module namespace is baked into the key at all** — the key is a pure function of
`(base_seed, name)`, nothing else.

### Formula B — namespaced, `NAMESPACE::name::base_seed`, double colon
```
key = f"{STREAM_NAMESPACE}::{name}::{base_seed}".encode("utf-8")
seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
return random.Random(seed_int)
```
Used by: `household_budget.py` (`STREAM_NAME="W2_4_..."`), `premise_demand.py`
(`STREAM_NAME="W1_5_..."`), `sme_distress.py` (`W2_6_...`), `willingness_classification.py`
(`W2_7_...`), `self_rationing.py` (`W2_8_...`), `dd_attribution.py` (`W2_10_...`),
`payment_behaviour_source.py` (`W2_11_...`) — **7 modules**, byte-identical formula, differing
only in the literal namespace constant (which is the point — that's what keeps them apart).
`_adapter_substream` and `_cohort_substream` are 4-part variants of this same family (extra key
components for per-period / per-axis isolation).

### Formula C — namespaced, `STREAM_NAME:salt:base_seed`, single colon, salt-first ordering
```
key = f"{STREAM_NAME}:{salt}:{base_seed}".encode("utf-8")
seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
```
Used by: `population_draw.py` only (1 module, `STREAM_NAME="W2_2_population_draw"`).

### Formula D — different RNG engine entirely (numpy, not stdlib)
`sim/flex_dispatch.py::_delivery_rng`: `hashlib.sha256(f"{name}:{seed}")` → same digest-truncation
idea, but returns `np.random.default_rng(...)` (PCG64) instead of `random.Random` (Mersenne
Twister). A caller cannot swap this for any of the above without a `.random()` → `.uniform()`
(or similar) API change.

### Formula E — implicit hash, no manual digest at all
`sim/scenario/intraday_shape.py`: `random.Random(f"{seed}|intraday|{date_str}")` — CPython seeds
a `random.Random` given a `str` via its own internal SHA-512-based algorithm, truncated
differently from the manual `sha256(...).digest()[:8]` pattern used everywhere else. Same
*intent* (C-S2 replay), different *mechanism*, and — because it is SHA-512 vs the other formulas'
explicit SHA-256 — cannot coincidentally collide with them, but also cannot be verified against
the same reference-value test pattern the other 11 modules use.

### 2.1 Why the divergence matters: the collision-safety property is NOT uniform

Formula B/C modules are collision-safe **by construction** — the module's own namespace constant
is part of the hashed key, so two modules can reuse the same substream *name* string (e.g. two
modules both naming a substream `"onset"`) without colliding, even when they share the exact same
`base_seed`.

Formula A modules are **not** collision-safe by construction — the key omits any per-module
namespace. Verified this is not hypothetical: `life_events.py::_base_seed_for` computes
`int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)` — **the identical formula** used as
`_base_seed_for` in six Formula-B modules (`household_budget`, `sme_distress`,
`willingness_classification`, `self_rationing`, `dd_attribution`, `payment_behaviour_source`, plus
`premise_demand`'s own customer/premise-keyed variant). So for the **same `customer_id`**,
`life_events` and (say) `sme_distress` compute the **same `base_seed`**. The only thing preventing
a stream collision today is that Formula A's key string (`"12345:job_loss"`) and Formula B's key
string (`"W2_6_sme_distress::job_loss::12345"`) happen to differ as literal byte strings even for
an identical `name` — i.e. **safety is accidental** (a side effect of the two formulas differing),
not structural. If a future module were added copying Formula A verbatim, and it happened to pick
a `name` already used by another Formula-A module sharing that customer's `base_seed`, the two
would draw byte-identical sequences. This is exactly the collision-risk class C-S2 exists to rule
out, and today it is ruled out by happenstance rather than by guarantee for 3 of the 11 modules.

### 2.2 Separator fragility (minor, noted for completeness)
`population_draw._substream` with its default `salt=""` produces
`f"{STREAM_NAME}::{base_seed}"` (the two adjacent colons from `":" + "" + ":"` collapse visually
to a double colon) — structurally resembling Formula B's separator even though Formula C is
nominally single-colon. Not a live collision (no other module shares `STREAM_NAME="W2_2_..."`)
but shows the informal string-concatenation approach is not robust to empty/colon-containing
inputs; the canonical primitive should not rely on ad hoc separator characters at all (see §3).

---

## 3. The one canonical `_substream` — signature and semantics

```python
def substream(base_seed: int, namespace: str, name: str) -> random.Random:
    """Return an ISOLATED random.Random for ONE named mechanism within ONE
    subsystem's namespace.

    Seed = first 8 bytes (big-endian) of SHA-256 over a length-prefixed,
    unambiguous encoding of (namespace, name, base_seed) -- NOT naive string
    concatenation with a separator character (a name/namespace containing the
    separator can otherwise create two different (namespace, name) pairs that
    serialise to the same key -- see the empty-salt collapse in section 2.2).
    Recommended encoding: hash each field length-prefixed, e.g.
    hashlib.sha256(b"".join(f"{len(s)}:{s}".encode() for s in (namespace, name, str(base_seed)))).

    Deterministic across processes (never Python's per-process-salted hash()).
    """
```

**What "named seeded substream" means:** every stochastic mechanism in every subsystem draws from
its own `random.Random` instance, derived as a pure function of three things — (1) which
*subsystem* (`namespace`, e.g. `"W2_6_sme_distress"`), (2) which *mechanism inside that subsystem*
(`name`, e.g. `"onset"`), and (3) the run's `base_seed`. No draw ever consumes from, or advances,
the global `random` module or any other subsystem's stream.

**Why a new subsystem's draw provably cannot shift another's:** `namespace` is now a
**mandatory, explicit parameter** (not an optional convention some modules embedded and 3 of 11
omitted). Two calls collide only if `(namespace, name, base_seed)` is identical across both — and
`namespace` uniqueness becomes a **tested invariant** (§4), not a documentation convention. This
closes the accidental-safety gap in §2.1: Formula-A-style modules currently rely on their `name`
strings never coinciding with another module's, by luck; the canonical primitive makes that
luck structural by requiring the namespace in every call, with a registry test enforcing global
uniqueness of registered namespace strings.

**Scope decision left open for BUILD (not resolved here — outside a DISCOVER pass):** whether
`_delivery_rng` (numpy Generator, Formula D) and `intraday_shape`'s inline pattern (Formula E)
migrate onto the same primitive (would require the canonical primitive to also offer a
numpy-Generator-producing variant, or a documented deterministic hand-off from
`random.Random.getrandbits(64)` to `np.random.default_rng`), or are explicitly scoped OUT as a
separate follow-on because they are a genuinely different RNG engine, not a cosmetic difference.
Flagging as an open question rather than deciding it, since deciding it is a BUILD-time design
choice.

---

## 4. Guard test design + R15 both-ways plan

**Existing pattern to build on:** `tests/sim/test_w2_5_substream_isolation.py` already proves
*within-module* isolation (`test_new_substream_does_not_shift_existing_substream`,
`test_every_named_substream_is_invariant_to_every_other_being_drawn`) — a solid within-module
template, but there is currently **no cross-module "only one definition exists" guard** and no
"namespaces are globally unique" test. Both are new.

**Guard 1 — single-definition guard (structural, source-scanning):**
```python
def test_exactly_one_substream_definition_exists():
    """After migration, `def _substream(` / `def substream(` may only appear in the
    ONE canonical module (simulation/rng_substream.py). Every former copy becomes an
    import, never a re-definition."""
    hits = grep_source_tree(r"^def (_)?substream\(", roots=["simulation", "sim", "company", "saas"])
    non_canonical = [h for h in hits if h.file != "simulation/rng_substream.py"]
    assert not non_canonical, f"duplicate substream definition(s): {non_canonical}"
```
**R15 both ways:**
- *Inject:* paste a second, real `def _substream(base_seed, name): ...` body into any module
  (e.g. temporarily re-add the old `sme_distress.py` local copy) ⇒ guard **REDS**.
- *Remove:* delete the injected copy, leaving only the canonical module's definition and plain
  `from simulation.rng_substream import substream` imports everywhere else ⇒ guard **passes**.
- Not a tautology: the check greps the actual committed source tree independently of which
  module *calls* the primitive, so it cannot be satisfied by merely aliasing an import — it fires
  on any reintroduced `def`, live.

**Guard 2 — namespace-uniqueness registry (new, closes the §2.1 accidental-safety gap):**
```python
_REGISTERED_NAMESPACES: dict[str, str] = {  # namespace -> owning module
    "W2_2_population_draw": "simulation/population_draw.py",
    "W2_4_household_budget": "simulation/household_budget.py",
    # ... one entry per current module, PLUS the 3 Formula-A modules assigned a namespace
    # they did not have before (conversation_response, life_events, adoption_geography).
}

def test_all_registered_namespaces_are_unique():
    assert len(_REGISTERED_NAMESPACES) == len(set(_REGISTERED_NAMESPACES))
```
R15 both ways: inject a duplicate namespace string for two modules ⇒ reds; restore distinct
values ⇒ passes.

**Guard 3 — reference-value migration (updates, does not delete, the 8 existing pinned tests):**
the 8 `test_substream_value_is_stable_across_processes` tests (§5) must be **re-pinned** to the
canonical formula's output, not deleted — deletion would remove exactly the regression protection
C-S2 depends on. R15 both ways on the *new* pinned value: mutate the canonical formula (e.g. flip
byte order) ⇒ all 8 (now: as many as still apply post-migration) red; restore ⇒ green.

---

## 5. The deliberate baseline break (ruling §8)

Ruling text (verbatim, §8): *"Unifying `_substream` will change draw sequences, so any frozen
baseline or lift table computed under the old derivation is no longer comparable. Mitigation:
treat this as a deliberate baseline break — re-freeze after migration, and do not run it
concurrently with any campaign whose evidence depends on an UNMOVED lift table (W1_6 is the live
example)."*

**Concrete, in-scope frozen values that WILL break** (verified directly, not inferred): 8 test
files each pin an exact-decimal regression assertion against the *current* per-module formula —
`tests/sim/test_w2_5_substream_isolation.py:68` (`round(_substream(12345, "job_loss").random(), 12)
== 0.157207184982`), and the equivalent `test_substream_value_is_stable_across_processes` in
`test_w2_4_household_budget.py`, `test_w2_6_sme_distress.py`, `test_w2_7_willingness_classification.py`,
`test_w2_8_self_rationing.py`, `test_w2_10_dd_attribution.py`, `test_w2_11_payment_behaviour_source.py`,
and `tests/simulation/test_conversation_response.py`. Every one of these 8 pinned floats moves
under Formula B/C→canonical migration (Formula-A modules move more, since they gain a namespace
they never had) and each **must be re-pinned to the new canonical value**, not silently loosened
or deleted — that is the re-freeze-and-declare step the ruling requires.

**W1_6, checked directly (a correction to the general citation):** the ruling names W1_6 as "the
live example" of the sequencing-wall policy in general terms. Traced the actual call graph:
`sim/weather_price_chain.py` and `background/weather_price_triad.py` import nothing from
`simulation.*`; `sim/weather_engine.py` (W1_6's underlying RNG source) draws exclusively from
`np.random.Generator` (the same numpy family as `sim/flex_dispatch.py`'s Formula D, *not* any of
the 11 in-scope `_substream` copies). **On direct code inspection, this specific migration does
not move any of W1_6's frozen figures** (chain-mean 81 vs real 78, cold_still spike_ratio 2.18,
etc. — `docs/design/maturity_map.yaml:1440` evidence trail). This is a discovered nuance, not a
license to ignore §8: the ruling's sequencing-wall obligation ("check the open-campaign register
before BUILD") is a **standing policy**, independent of whether W1_6 specifically is code-coupled
— other live campaigns *do* sit directly on top of the 11 in-scope modules' frozen numbers (the 8
pinned tests above are proof of that), so the register check at BUILD time remains mandatory
regardless of this W1_6-specific finding.

---

## 6. Sequencing wall (recorded, binding, ruling §8)

**Do NOT run the BUILD half concurrently with any live campaign whose evidence depends on an
UNMOVED lift table.** Per §5's direct-inspection finding, W1_6 itself is not code-coupled to this
migration — but the wall is not narrowed to "unless proven uncoupled"; it is a standing
obligation: **check the open-campaign register (`docs/design/maturity_map.yaml` `loop_stage`
in-flight HARDEN/BUILD entries + `docs/staging/` open campaigns) fresh at the moment the BUILD
half is drawn**, not at this DISCOVER pass's timestamp (2026-07-28) which will be stale by the
time BUILD opens. If any in-flight campaign's exit criteria cite a frozen numeric assertion
sourced from one of the 11 in-scope modules (population_draw / household_budget / sme_distress /
premise_demand / willingness_classification / adoption_geography / self_rationing / dd_attribution
/ payment_behaviour_source / conversation_response / life_events), **that campaign wins and §2.2
waits** — say so rather than doing both, per the ruling's own instruction.

---

## Summary for the orchestrator

- **Definitions found:** 11 exact `def _substream` (mint estimated ≥8 — undercount) + 5
  functionally-equivalent, differently-named constructs (`_adapter_substream`, `_cohort_substream`,
  `_u01`, `_delivery_rng`, `intraday_shape`'s inline pattern) = **16 total**.
- **Do they agree?** No — genuinely diverge into 3 sha256-based key formulas (A/B/C, differing in
  namespace-presence, field order, and separator) plus 2 that aren't sha256-of-random.Random at
  all (numpy Generator; implicit stdlib string-seeding). 7 of 11 already agree byte-for-byte
  (Formula B) — that's the natural target formula, extended with a mandatory namespace param so
  the other 4 (+5 named-differently) migrate onto one guaranteed-collision-safe primitive.
- **Real, not hypothetical, risk found:** 3 modules (Formula A) share `base_seed` derivation with
  6 Formula-B modules via an identical customer_id-md5 formula, and have NO namespace in their
  substream key — collision is prevented today only by the two formulas' literal strings
  differing, not by structural guarantee.
- **This pass wrote doc only** (`docs/design/RNG_SUBSTREAM_PRIMITIVE_DISCOVER.md`); no code,
  tests, or `maturity_map.yaml` touched; `level_current` unchanged; BUILD remains
  `blocked_on: director_build_open`.
