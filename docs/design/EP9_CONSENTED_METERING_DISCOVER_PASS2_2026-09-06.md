# EP9 — consented metering via a DCC Other User: DISCOVER pass 2 (2026-09-06)

**Atom:** `EP9_adapter_n3rgy_consented_metering` · lane `W4_the_wall` · epoch 3 · level 0 → 3 ·
`loop_stage: idle` · `dial_inherited: 3`
**Draw:** 2026-09-06 scheduled tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — no
adapter, no client, no fixture; `file_scope` stays `[]`. `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1.
**Level HELD at 0.** Not moved, not requested.
**Measured at:** HEAD `fdfa0c94f`. Every claim below re-measured on disk this pass.

**Builds on:** `EP9_CONSENTED_METERING_DISCOVER.md` (2026-08-18, landed `64b23e8d3`). That pass is
saturated and this one does not re-derive it. This is the interconnection re-check: **of what it
named, what has moved in nineteen days?**

---

## 0. The answer

**Nothing it named has moved. One thing about the record has: the finding it queued was archived
without being fixed.**

That is the result worth having, because a queued finding sitting in `docs/staging/done/` reads, to
every subsequent orientation, as a finding that was dealt with.

---

## 1. §2 — the access class is unchanged, and correctly so

The 2026-08-18 pass found no n3rgy host in `background/egress_allowlist.py` and recorded that widening
it would be a change to this agent's own sandbox profile — director-console-only, a wall.

Re-measured this pass: **`n3rgy` still does not appear in `background/egress_allowlist.py`.** No change
was made, none is proposed, and the atom's `name:` field still records the access class as
**SANDBOX NOW** — a statement about n3rgy's service, not about this machine's reach to it. The two are
not in conflict and the atom's field does not need editing.

---

## 2. §3 — the registration-key defect is live in both modules, three weeks on

The 2026-08-18 pass measured 18 of 19 live MPANs as check-digit invalid, six metered accounts with no
MPAN at all, and a `validate_mpan` that is a length regex with zero non-test callers. It queued the
fix rather than making it (SELF_INTERRUPT_DISCIPLINE: the fix touches a live CRM generator and a live
billing module; a doc-only draw does not carry it).

Re-measured at HEAD `fdfa0c94f`:

| what | 2026-08-18 | 2026-09-06 |
|---|---|---|
| `company/crm/customer_registry.py::_mpan` (L24–27) | `f"1{seed:012d}"[:13]`, no check digit | **byte-identical** |
| `company/billing/meter_points.py::validate_mpan` (L57–59) | `bool(_MPAN_RE.match(...))` — length only | **byte-identical** |
| `validate_mpan` non-test callers | zero | **zero** (only its own definition; `tests/company/billing/test_meter_points.py` is the sole importer) |

The two tests that exercise it are `test_validate_mpan_13_digits` and `test_validate_mpan_wrong_length`
— both assert the length property the function actually has. **Nothing in the tree can go red on the
check-digit defect**, so nothing was ever going to notice.

---

## 3. What DID move: the finding was archived, not actioned

`WORKER_FINDING_THE_REGISTRATION_KEY_FOR_A_REAL_COUNTERPARTY_IS_INVALID_IN_EIGHTEEN_OF_NINETEEN_ACCOUNTS_2026-08-18.md`
now sits in **`docs/staging/done/`**. Its own header still reads *"QUEUED not fixed"*.

The commit that moved it is `2766c8ca2` (2026-08-26): *"a checker crashed on a scratch path two
documents honestly mention, so it refused every staging commit and a 419-file archive backlog could
not be cleared for six days"*. It was swept in a **419-file bulk backlog clearance**, not dispositioned
on its merits.

So the record and the tree disagree: the record says done, the code says untouched. This is the
landed-but-unbound shape — a document filed for a reason nobody re-read, moved by a mechanism that was
fixing something else. **Nothing here is anyone's error**; the backlog clear was the right move and a
bulk move cannot triage. The point is that the archive room carries no evidence of disposition, so
"in `done/`" cannot be read as "closed", and this pass is the only thing that noticed.

**Not re-filed as a new finding**, deliberately: a second copy of a live finding is the two-rooms
trap, and `finding_classes --check` already refuses documents present in two rooms. The existing
document is correct, its measurements reproduce exactly at today's HEAD, and its severity (LATENT,
lane `D_billing_metering`, rank backlog) is right. What it needs is to be *worked*, not re-written.
This paragraph is the pointer that says so.

---

## 4. FRAME — unchanged, with one precondition made explicit

The L1/L2/L3 criteria in `EP9_CONSENTED_METERING_DISCOVER.md` §7 stand as written and are not restated.
One thing that pass left implicit is now explicit, because this pass proved it does not decay on its
own:

> **EP9-P0.** L2 ("a company-side *is this supply point smart* register, keyed by an identifier a real
> system would accept") **cannot be reached while `_mpan` emits check-digit-invalid keys and
> `validate_mpan` cannot fail on them.** The archived finding is the work, and it is a prerequisite of
> this atom's level move, not a hygiene item beside it. Falsifier for its closure: a control that
> computes the real check digit over every MPAN in `company/data/registry.db` and goes red on any
> mismatch — keyed to the property, so it stays honest when the registry grows.

---

## What this pass did NOT do

No code changed; no adapter, client or fixture written. No network call attempted and no egress change
proposed. The `docs/staging/done/` archive was **not** disturbed — the finding was not moved back to
the root, because a document present in two rooms refuses every subsequent staging commit and because
moving it would misrepresent when it was filed. The six MPAN-less successor accounts (§3 of pass 1) and
the §4 addressability contradiction were **not** re-measured this pass; they were not the thing at risk
of being silently read as closed. EP8's findings were not revisited. Level unchanged at 0.
