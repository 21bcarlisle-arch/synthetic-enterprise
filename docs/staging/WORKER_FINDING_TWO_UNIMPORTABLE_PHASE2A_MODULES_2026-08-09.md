# [WORKER-FINDING] Two `simulation/run_phase2a*` modules cannot be imported at all — and nothing noticed because nothing imports them

**Found:** 2026-08-09, during the `KNIFE2_customer_straddle` draw (incidental — not this atom's scope).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight; the machine is not blocked.
**Rank:** backlog — but see "why this one is worth more than its blast radius" below.

## Observed, with evidence

`simulation/run_phase2a.py` and `simulation/run_phase2a_repriced.py` raise on import:

```
File "/home/rich/synthetic-enterprise/simulation/run_phase2a.py", line 74, in <module>
    STARTING_TREASURY_GBP = 3250.0 * (sum(c["eac_kwh"] for c in CUSTOMERS) / ORIGINAL_4_CUSTOMER_EAC_KWH)
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
```

Both fail at module scope, on the same line, for the same reason: **12 of the 18 entries in the
customer roster carry `eac_kwh: None`** (`C7`, `C8`, `C9`, the four `C_IC*` I&C accounts, and the
five gas twins `C1g`–`C4g`, `C_IC3g`). `saas/customers.py`'s own docstring says the field "may be
`None` for future smart-meter customers", so the `None`s are intended data; the two modules'
unguarded `sum()` over the whole roster is not.

## Ruled out: this is not the KNIFE pass that surfaced it

The pass replaced `from saas.customers import CUSTOMERS` with a seam accessor that returns **the
same list object**. Verified directly rather than assumed — evaluating the identical expression
over `saas.customers.CUSTOMERS` fails the same way:

```
$ python3 -c "import saas.customers as sc; sum(c['eac_kwh'] for c in sc.CUSTOMERS)"
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
```

Since `from X import CUSTOMERS` binds that same object, HEAD's version fails identically. The
other 14 modules the pass touched all import cleanly with roster identity preserved.

## Why nothing caught it

Nothing imports either module. `grep -rn "run_phase2a\b" tests/ simulation/ tools/ background/`
returns **zero** hits outside the files themselves — no test, no caller, no CLI. They are SIM-side
orphans, so no suite ever executes their module scope, and a module that cannot be imported looks
exactly like a module nobody happened to call.

## Why this one is worth more than its blast radius

The blast radius today is zero — that is precisely the problem, and it is a **new instance of a
class this repo has already paid for**. The company-side orphan census
(`docs/design/ORPHAN_DISPOSITION_REGISTER.md`, KNIFE pass 4) established that all 258 company-side
orphans carry test evidence, and concluded the real class was `unhooked` — *tested capability whose
consumer was never built*. These two are the SIM-side counterpart and they are strictly worse:
**untested capability whose consumer was never built, and which does not even load.** The orphan
census was scoped to `company/`, so this population was never looked at.

Two questions follow, and neither is answered here:

1. **Is there a SIM-side orphan population at all, and what is in it?** `probe_company_orphans`
   reads the capability index, which is company-scoped. Nobody has run the equivalent census over
   `sim/` + `simulation/`.
2. **How many of those orphans are also un-importable?** An import smoke-test over every module in
   the tree is a cheap, fail-loud control and the repo does not appear to have one. Two of the
   sixteen modules one arbitrary pass happened to touch were broken; that is not a rate anyone
   should extrapolate from, but it is a reason to measure rather than assume.

## What closing it needs

- **Not** a patch to the two `sum()` calls. That is the instance fix R10 forbids for a class defect,
  and it would restore two modules nobody calls to a state nobody checks.
- A positive disposition for each, on the KNIFE pass 4 model: wired (a caller exists and was
  missing), retired-to-archive (superseded — name the superseder; `run_phase2b` is the obvious
  candidate and `run_phase2a_repriced` looks like a variant of a variant), or kept-and-explained.
  `ARCHIVE, NEVER DELETE` governs either way.
- The two census questions above, which are the class half and are the part actually worth doing.

## Not currently blocking

Nothing imports them, so nothing fails. `KNIFE2_customer_straddle` landed with the ratchet suite
and the KNIFE ledger green (`customer_straddle` 16 edges → 0; `wall_crossings` 104 → 88).
