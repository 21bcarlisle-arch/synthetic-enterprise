**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — whether the "empty capabilities page" was a withheld feed in the harness call

**Filed:** 2026-09-22, delivery seat, BEFORE running the one-variable control.
**Claim:** `the-unbounded-quotient-six-remaining-debt-sites-and-the-page-that-renders-empty`

## What I already know, and it refutes the drawn item's premise

Driving `site/capabilities/index.html` through `site/_live_harness.mjs` on `origin/main` (my base,
which contains 5973f923b and 08c696269) with every feed the page requests supplied from
`site/data/`: **42 of 42 elements render, `scriptError` is `null`, `unresolved` is empty.**

The filed finding measured **36 of 37 empty with only `arms-note` carrying content**. Both
measurements cannot describe the same call. The page is not blank on this base.

## The prediction, registered before the control is run

The harness's `requested` list on this page is:

```
../data/capabilities_door.json
../data/book_growth.json   (twice)
../data/value_arms.json
../data/dd_opening_arms.json
```

The finding's account names `value_arms.json` and `dd_opening_arms.json` and does **not** mention
`capabilities_door.json`. The harness REJECTS any url the caller did not supply — deliberately,
fail-closed, so a missing feed drives the page down its real error path.

**I predict:** withholding `../data/capabilities_door.json` alone, with every other feed supplied,
reproduces the finding's measurement — a near-blank page with `scriptError: null` — because the
door `.catch`es its own boot chain and the harness records only the first error per block.

**I predict specifically:** `arms-note` is among the survivors, because it is set independently of
that feed.

**If that is right**, the defect is NOT in the page. It is that a door which cannot report its own
failed boot looks identical to a door with nothing to say — and a harness caller that omits one
feed gets a silent near-blank page rather than a named refusal. That is the thing worth fixing,
and it is exactly where the finding's own "Where to start" pointed.

**If that is wrong** — if the page renders fine without that feed — then the finding's 36-of-37 has
some other cause, the page moved between the filing and now, and I will say so and hunt it.

## What would refute me

A run with `capabilities_door.json` withheld that still renders most elements. Or a
`scriptError` that is NOT null, which would mean the swallowing story is wrong even if the
blankness reproduces.
