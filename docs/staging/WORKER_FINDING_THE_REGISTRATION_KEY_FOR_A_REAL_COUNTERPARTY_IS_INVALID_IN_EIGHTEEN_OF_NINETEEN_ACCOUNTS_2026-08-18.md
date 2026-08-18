# WORKER FINDING (LATENT, D_billing_metering, backlog): the MPAN is the registration key for two named real counterparties, 18 of 19 are check-digit invalid, 6 metered accounts have none at all, and the module named `validate_mpan` is a length regex with zero non-test callers

**Severity:** LATENT. **Lane:** `D_billing_metering` (the lane of the generator and the
validator; the atom that surfaced it is `W4_the_wall`). **Rank:** backlog (P-1: this declares
its intended rank on arrival). **Filed by:** worker tick 2026-08-18, out of the
`EP9_adapter_n3rgy_consented_metering` LANE-3 DISCOVER draw — QUEUED not fixed, per
SELF_INTERRUPT_DISCIPLINE (the fix is a change to a live CRM generator and a live billing
module; a doc-only draw does not carry it).

**Measured at:** HEAD `4e79c4c8f`. `company/data/registry.db` (19 rows) and
`docs/reports/run_output_latest.json` (4,154,361 bytes, mtime 2026-08-18 15:56:22) read and
parsed in full. Every claim below is **observed-with-evidence** unless labelled **inferred**
(R9).

## What was found

The UK MPAN core is 13 digits, the 13th a check digit over the first 12 (weights
3,5,7,13,17,19,23,29,31,37,41,43; sum mod 11 mod 10). Applied to every MPAN in the live
registry:

```
MPANs: 19    check-digit VALID: 1    INVALID: 18
example  C1 -> 1000000000116   expected check digit 0, actual 6
```

The single pass is what chance gives at 1-in-10 (**inferred**: not a designed valid one). The
generator, `company/crm/customer_registry.py::_mpan`, is digit-count only:

```python
def _mpan(account_id: str) -> str:
    """Synthetic MPAN (Meter Point Administration Number) — 13 digits."""
    seed = sum(ord(c) for c in account_id)
    return f"1{seed:012d}"[:13]
```

`company/billing/meter_points.py::validate_mpan` — the module named for this property —
returns True for all 19:

```python
def validate_mpan(mpan: str) -> bool:
    """Return True if mpan is a valid 13-digit MPAN string."""
    return bool(_MPAN_RE.match(mpan.replace(" ", "")))
```

Its docstring asserts validity; its subject is the digit count. **And it has zero non-test
callers** — grep for `validate_mpan` across all `*.py` excluding `tests/` returns only its own
definition. So it cannot fail on the defect its own name describes, and it never runs either
way. Both halves stated separately so neither carries the verdict alone.

Separately, **six metered accounts have no identifier in existence**. The published
`meter_read_log` carries 19 customer ids and the registry carries 19 account ids; they overlap
on 13:

```
in the read log, absent from the registry:  C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4, SYN-2021-001
in the registry, absent from the read log:  C1_2, C2_2, C3_2, C4_2, C5_2, C6_2
```

The MPAN lives only in the registry. (The six registry-only rows are `successor_of` accounts —
a different question, not chased here.)

## Why it is a finding and not an acceptable simplification

A synthetic identifier is a perfectly reasonable simplification for a simulation, and this one
was harmless for as long as nothing outside the repo had to accept it. Two Epoch-3 atoms make it
load-bearing: `EP9_adapter_n3rgy_consented_metering` (n3rgy registers a supply point **by
MPAN/MPRN** — advisor research verified 2026-08-05) and `EP10_adapter_uk_link_xoserve` (Supply
Point Enquiry / Meter Asset Enquiry are addressed by MPRN). At the moment either is drawn, the
key stops being decoration and today's book cannot be registered.

## Why it is LATENT and not BLOCKING

Nothing published today is wrong because of it: no live figure, bill, or board number depends on
an MPAN being industry-valid, and the two atoms that would depend on it are epoch-3 BUILD-gated
(`loop_stage: idle`). It is a defect that is certain to bite at a known future moment, which is
precisely the backlog case.

## Recommended fix (recorded, not asked — NEVER_ASK_WITHOUT_RECOMMENDING)

Three parts, smallest first, and the middle one is the R15 part:

1. **Give `_mpan` a real check digit** — compute the 13th from the first 12 rather than
   truncating. Same for `_mprn` (Xoserve MPRNs are 6–10 digits with no check digit, so that one
   is a range fix, not an algorithm). Note in passing, not a live defect: `sum(ord(c))` collides
   on any anagram of an account id — all 19 are currently distinct.
2. **Make `validate_mpan` able to fail**, and mutation-test it (R15): it must go red on a
   check-digit-invalid 13-digit string, which is the defect it is named for. Today's population
   is the ready-made mutation corpus — 18 strings the current implementation passes and the
   fixed one must reject.
3. **Give it a caller.** A validator with zero callers is the no-caller class regardless of how
   correct it becomes; the registry write path in `customer_registry.py` is the natural site.

**Falsifier to run BEFORE accepting the fix** (memory: run the proposed falsifier first): assert
that every MPAN in `company/data/registry.db` passes `validate_mpan`. That assertion is **red
today at 18 of 19** and must be green after — and the fix is not complete until the six
registry-less metered accounts either gain a row or are shown to be out of scope for a supply
point identifier.

## Blast radius, counted not assumed

`validate_mpan` has zero non-test callers, so changing it breaks nothing that runs. `_mpan`'s
output is stored in `registry.db.customers.mpan` (19 rows) and re-derived on each registry
build; consumers of that column were **not** enumerated by this pass and must be before the
generator changes — an MPAN that changes value is an identity change, and
`company/crm/switch_analytics.py`, `company/crm/multisite_account.py` and
`company/billing/metering_exception.py` all key records on `mpan`. That enumeration is the
first task of whoever draws this, not a claim made here.
