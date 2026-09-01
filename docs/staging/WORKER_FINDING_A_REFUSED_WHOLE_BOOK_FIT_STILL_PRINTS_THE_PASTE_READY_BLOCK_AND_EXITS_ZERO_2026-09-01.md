**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# A refused whole-book fit still prints the paste-ready `YEAR_LEVEL_ANCHOR` block, and exits 0

**Found:** 2026-09-01, delivery seat, Lane 0, while grading
`WORKER_PREREGISTRATION_WHAT_A_RERUN_FROM_THE_CLEAN_TREE_MUST_SHOW_2026-09-01.md`. Not predicted.

## What happened

`python3 -B -m tools.fit_year_level_anchor /tmp/svtcap2/c2_marketterm.json`, on a capture with zero
SVT segment decisions, printed **both** of these, in this order, in one run:

```
  NO WHOLE-BOOK FIT — the world and this fit disagree about the SVT composition.
  Reason: this capture has no SVT segment decisions to establish a composition from.
  ⚠ c2_marketterm_svt_segment_decisions.json is EMPTY. ...

  YEAR_LEVEL_ANCHOR: dict[int, float] = {
    2016: 4.685356,
    ...
    2022: 1.659480,
  }
```

`FIT_RC=0`.

## Why it is a defect and not a display choice

The module states the intended design itself, at `tools/fit_year_level_anchor.py:517`:

> `# THE DIAGNOSTIC TABLE ABOVE ALWAYS PRINTS AND THE CONSTANT BELOW DOES NOT. A measurement`
> `# withheld is a measurement nobody can argue with, so the per-year fit stays visible; what`
> `# is refused is the block a reader would paste into the world.`

That is honoured on the whole-book branch: `svt_market_invariance_refusal()` fires and the function
`return 1`s at line 526, **before** any block is printed. It is not honoured on the fallback branch.
There (lines 538–560), the whole-book refusal prints **narrative only** — it gates nothing — and the
sole gate on the paste-ready block is `emission_refusal(decl)`, whose subject is the *declared
`a_shock`/`scale` pair*, not the composition. Two different subjects; only one of them can stop the
artefact. When the composition refusal fires and the declared-pair refusal does not, the tool
refuses in prose and emits in fact.

**The block it emits is the renewal-route-alone diagnostic**, which the same output labels twelve
lines earlier:

> `THE TABLE ABOVE IS THE RENEWAL ROUTE ALONE and is a diagnostic, not the world's level`

and it is rendered in exactly the `YEAR_LEVEL_ANCHOR: dict[int, float] = {` form of
`simulation/departure_level_anchor.py:55` — the literal shape of the paste. The one artefact the
design says must be withheld is the one printed, wearing the destination's own syntax.

## The exit code makes it worse, and is the part that reaches automation

`return 0`. The two branches that refuse *properly* both `return 1`. So a caller that reads the rc —
which is the only thing a script can read — sees this run as a **successful fit**, on a capture the
tool has just declared unfittable. A human reading the whole output would probably catch it. Nothing
downstream reads the whole output.

## Class

This is two catalogued classes at once:

- *a control whose scope is narrower than its claim* — the composition refusal claims "NO WHOLE-BOOK
  FIT" and its scope is the printed sentence.
- *a fail-open guard whose verdict no surface reads* — the refusal is composed into stdout prose
  while the rc, the machine-readable surface, says PASS.

It is also the shape this repo has paid for before: **the refusal that names its reason correctly and
then does not act on it.** The reason here is accurate and well-written. The block prints regardless.

## What it did NOT cause

No constant was adopted from it. The 2026-09-01 grading recorded its whole-book block as a *result*,
not an adoption, and this stretch adopted nothing. `simulation/departure_level_anchor.py` is clean
against `origin/main`. **So this is latent, not blocking** — but the next reader to run the tool on a
recorder-less capture gets a paste-ready 2022 anchor of `1.659480` under a heading that says no fit
was produced, and rc 0 to go with it.

## Repair, not applied here

`tools/fit_year_level_anchor.py` is **outside this stretch's pathspec** and was not touched. The
repair is to make the fallback branch behave like the whole-book branch: when `book_refusal` or the
composition refusal fires, print the diagnostic table, print the cause, and `return 1` **before** the
`YEAR_LEVEL_ANCHOR` block — never after it.

The control that would have caught this keys on the property, not on today's answer: **for every
refusal path, the string `YEAR_LEVEL_ANCHOR: dict` must not appear in stdout, and the rc must be
non-zero.** Both halves are needed — a test on the text alone passes an rc-0 refusal, and a test on
the rc alone passes a refusal that still prints the paste.
