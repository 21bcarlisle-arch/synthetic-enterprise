> **RESOLVED 2026-08-09, archived.** Re-measured against a pristine `git archive HEAD`:
> E402 194 (= baseline), F401 279 (= baseline), I001 1388 (<= 1392) — **HEAD is GREEN on all
> three**. The E402 201-vs-194 red was real when filed and was fixed by intervening commits;
> it was not bisected, it was overtaken.
>
> The finding's closure steps were followed in spirit, not in form: the ratchet was still RED
> when drawn, but for a DIFFERENT reason — one unused `typing.Callable` in an **uncommitted**
> edit to `background/fabric_gap_ledger.py`. Fixed (not re-frozen) in commit e21066b78.
>
> What this finding did NOT anticipate, and is worth carrying forward: the ratchet lints `.`,
> the WORKING TREE, so a concurrent writer's uncommitted lint error wedges publishing for every
> publisher and never appears at HEAD, where anyone bisecting would look. The finding noticed
> the tree/HEAD divergence and read it the reassuring way round ("uncommitted work is *reducing*
> the count").

# [WORKER-FINDING] The ruff static ratchet is RED at pristine HEAD (2026-08-08)

**Found during:** `AO3_join_test_tier` (join test tier) build. **Not caused by it.**
**Disposition:** QUEUED as a finding, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — the
machine is not blocked; the supply of harness findings is infinite, and fixing this one on
sight is the treadmill).

## Observed, with evidence

`tests/architecture/test_static_quality_ratchet.py` fails on two of its tests:

```
E402: baseline 194, now 201
F401: baseline 280, now 281
I001: baseline 1392, now 1395
```

**This is not working-tree noise and it is not the join tier.** Measured against a *pristine*
`HEAD` extracted with `git archive HEAD | tar -x -C $TMP` — no uncommitted changes present at
all:

| code | baseline (frozen 2026-08-06) | pristine HEAD |
|---|---|---|
| E402 | 194 | **201** |
| F401 | 280 | **281** |
| I001 | 1392 | **1395** |

`tests/system/**` contributes **zero**: `ruff check tests/system/ --output-format=json`
returns an empty finding list.

## Why it matters

The ratchet's own message is *"Fix the new violations — do not raise the baseline"*, and it
is correct to say so. But a ratchet that has been red since some commit between 2026-08-06
and 2026-08-08 is, in the meantime, **a control that reports the same red regardless of what
anyone does next** — it can no longer distinguish a new violation from the standing seven.
That is the fail-state where a red control gets routed around rather than read.

Note also that the working tree currently measures E402=196 while HEAD measures 201, i.e.
uncommitted work in the shared tree is *reducing* the count — so anyone diagnosing this from
the working tree alone will get a different number than the gate will.

## What closing it looks like

1. Bisect 2026-08-06..HEAD for the commit(s) that added the 7 E402 / 1 F401 / 3 I001.
2. Fix the violations in those files (the ratchet's stated remedy), **not** the baseline.
3. Only if a violation is deliberate and justified: re-freeze with the reason recorded, and
   re-freeze the ruff PIN alongside it — the doc in that test is explicit that a baseline is
   meaningful only per tool version.

## Not asserted

Which commit introduced them (not bisected — that is the work, not the finding). Whether any
of the three codes were already drifting before the 08-06 freeze.

— Worker finding, 2026-08-08, during AO3_join_test_tier.
