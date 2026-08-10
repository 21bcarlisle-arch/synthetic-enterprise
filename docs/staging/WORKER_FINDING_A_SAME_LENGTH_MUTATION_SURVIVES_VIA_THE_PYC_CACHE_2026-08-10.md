# WORKER FINDING — a same-length source mutation survives its own restoration, via the `.pyc` cache

**Found:** 2026-08-10, KNIFE pass 3 step 7 (design B4), by the control catching its own harness
**Class:** R15 — a mutation harness that damages the suite it protects
**Status:** fixed in the three harnesses this tick shipped; **the class is open** in the older copies
**Rank requested:** backlog — latent, not live (see "How exposed is the tree today")

## The observation (observed-with-evidence, R9)

`tests/simulation/test_dd_payment_day.py` mutates `simulation/dd_payment_day.py`'s
`_MAX_PAYMENT_DAY = 28` to `31`, loads the mutated file as a throwaway module, and restores the
original text in a `finally`. The restoration was verified byte-equal. The next test in the same
session nevertheless received day **29** from the live module, and failed against a defect that no
longer existed in the source:

```
E   ValueError: payment_day must be 1-28; got 29
$ grep -n "_MAX_PAYMENT_DAY = " simulation/dd_payment_day.py
60:_MAX_PAYMENT_DAY = 28
$ python3 -c "from simulation.dd_payment_day import _MAX_PAYMENT_DAY; print(_MAX_PAYMENT_DAY)"
31
```

The file said 28. The import said 31.

## Why (inferred, and consistent with every observation above)

`importlib.util.spec_from_file_location(name, path)` derives its bytecode cache path from the
SOURCE path, not from the throwaway module name — so executing the mutant writes
`__pycache__/dd_payment_day.cpython-3XX.pyc` into the REAL module's cache slot. CPython validates
that cache against the source's **size and mtime**. `28` → `31` changes neither the length nor,
usually, the mtime second. The mutant's bytecode therefore stays "valid" after the source is
restored, and every later import in the process — and in any process started within the same mtime
granularity — silently gets the mutated module.

## Why this is worth a rule and not just a fix

The harness exists to prove a control can fail. A harness that can leave the mutation LIVE proves
the opposite of what it claims, and does so invisibly: the mutation test itself passes (it asserts
the defect is detected), and the damage lands on a LATER, unrelated test, which then reads as a
real regression in the code under review. This tick nearly spent its budget "fixing" a range bug
that was never in the source.

It is also the exact shape R15 warns about from the other side: the restoration assertion
(`path.read_text() == original`) is a TAUTOLOGY here — it checks the text, and the text was never
the thing that survived.

## The fix (applied to the three harnesses shipped this tick)

```python
self._prev = sys.dont_write_bytecode
sys.dont_write_bytecode = True          # write no .pyc for the mutant at all
...
finally:
    self.path.write_text(self.original)
    os.unlink(importlib.util.cache_from_source(str(self.path)))   # drop any that exists
    importlib.invalidate_caches()
    sys.dont_write_bytecode = self._prev
```

## How exposed is the tree today (measured, not assumed)

`grep -rl spec_from_file_location tests/ --include=*.py` returns **20 files** on this tree, of
which 3 are the ones fixed here. The other 17 include
`tests/company/interfaces/test_renewal_offer_seam.py`, `tests/tools/test_write_time_gate.py`,
`tests/tools/test_pre_commit_test_gate.py`, `tests/hooks/test_seat_guard.py` and the four
`tests/background/` daemon suites. Not all 17 mutate a real module in place — several load a
FIXTURE they wrote to `tmp_path`, which is not exposed at all, and that distinction is the work
the closure below has to do rather than assume. None is currently BITING, and where the reason
has been checked it is luck rather than design: their mutations all ADD or REMOVE text, so the file size changes and the cache is
correctly invalidated. The first same-length mutation any of them grows — a digit, a comparison
operator, a `True`→`False` (5 chars vs 4, safe) or `>=`→`<=` (safe), `28`→`31` (NOT safe) — turns
this back on, in a suite whose failure will point at innocent code.

## The R10-shaped closure this asks for

Not "fix the other copies one by one". One shared mutation harness under `tests/` that every suite
imports, carrying the cache guard once, so a new suite cannot re-derive the defect. That is a
refactor across five-plus suites owned by other lanes, which is why this pass filed it instead of
doing it inside a wall commit — but the instance fix alone is explicitly NOT the closure.

**Queued per SELF_INTERRUPT_DISCIPLINE:** the machine is not blocked; this is a defect class to draw,
not an interrupt.
