# WORKER FINDING — twenty-one door tests point at a directory that is in no tree, and they wedge the file they live in

**Severity:** BLOCKING · **Lane:** H_harness

rank: after-current-EP6-pass
found_by: EP6_wall_protocol_typing pass 42 (a refused `surgical_land`)
found_at: 2026-08-20

## The observation (observed-with-evidence, R9)

`tests/tools/test_couple_w2_11_d5.py` has 21 tests that error before reaching an
assertion:

```
RuntimeError: door harness failed: Error: Cannot find module
  '/home/rich/synthetic-enterprise/site/proof/_render_harness.mjs'
```

The two constants they resolve through are `tools/couple_w2_11_d5.py:9005-9006`:

```python
_DOOR_HARNESS = Path(__file__).resolve().parent.parent / "site" / "proof" / "_render_harness.mjs"
_DOOR_INDEX   = Path(__file__).resolve().parent.parent / "site" / "proof" / "index.html"
```

`site/proof/` does not exist in the working tree, and it is in **no tree**:

```
$ git ls-tree -r HEAD --name-only | grep -c 'site/proof/'
0
```

A sibling harness of the same name DOES exist and is tracked —
`site/knowledge/electricity-wholesale/_render_harness.mjs` — so this is a path
that moved (or a door that was never committed), not a tool that was deleted.
Which of the two it is has **not** been established here and must not be
asserted: that is the first job of whoever takes this.

## Why it is blocking, not cosmetic

The pre-commit gate selects tests by filename stem, so **any** commit touching
`tools/couple_w2_11_d5.py` or `tests/tools/test_couple_w2_11_d5.py` re-runs this
file and is REFUSED. That is not hypothetical: it refused EP6 pass 42's first
landing after a 15m51s gate cycle (`21 failed, 1236 passed`), and the pass had
to re-home a live-caller wiring onto a different module to land at all.

`tools/couple_w2_11_d5.py` is the W2_11 ↔ D5 coupling harness and appears in the
`file_scope` of at least nine maturity-map atoms. All of them are currently
unable to land anything in it.

## What this is NOT

Not caused by EP6 pass 42. The failures reproduce with that pass's changes fully
reverted, because the missing path is a property of HEAD.

## What would close it

Either the door is restored (`site/proof/index.html` + `_render_harness.mjs`
committed), or the constants are re-pointed at wherever the door actually lives
now, or the 21 tests are retired with a stated reason. Whichever it is, the
closing evidence is a green `tests/tools/test_couple_w2_11_d5.py` at HEAD — and,
per R11, a check that the door those tests are about is reachable on the live
site, since a green suite achieved by deleting the subject is the failure mode
these tests exist to catch.

Filed rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE): the machine is not
blocked — EP6 pass 42 landed by re-homing — and the repair is a site-lane
question about a door this pass has no standing to retire.
