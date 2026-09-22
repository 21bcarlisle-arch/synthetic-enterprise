**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — found in passing

# FINDING — the capabilities page renders almost entirely empty on the current base, and nothing
raises a script error

**Filed:** 2026-09-22, found while landing
`the-unbounded-quotient-is-caught-as-a-class-by-a-control-not-as-a-fifth-instance-by-hand`.
**NOT THIS LANE'S WORK, and measured to establish that before saying so.**

## What I measured

Driving `site/capabilities/index.html` through its own harness (`site/_live_harness.mjs`) against
the real feeds, **36 of 37 rendered elements come back as the empty string.** Only `arms-note`
carries content (3,729 characters). Every `arms-*` element a reader meets — `arms-headline`,
`arms-decisions`, `arms-method`, `arms-errorbar`, `arms-split`, `arms-sample` — is empty, as is
every `ddopen-*` element and the page's `stamp`, `world` and `supplier` blocks.

**`_meta.scriptError` is `null`.** So is any unhandled promise rejection: I re-ran the harness with
a `process.on('unhandledRejection')` probe attached and stderr came back empty. The page is not
reporting a failure; it is rendering nothing and saying nothing about it.

It is not a data refusal either. `value_arms.json` carries `decisions.available: true` with a full
key set, and the writer at `site/capabilities/index.html:2710` is guarded on exactly that flag.

## It is pre-existing, and here is the control that establishes it

Extracted a clean tree at HEAD with `git archive` (no working-tree copies, no uncommitted work) and
ran the identical render: **`arms-decisions` comes back empty there too.** Running the affected
suite in both trees, like-for-like:

| tree | result |
|---|---|
| clean HEAD extract | 5 failed, 5 passed, 1 skipped, **12 errors** |
| my tree, after this lane's changes | 4 failed, 9 passed, 1 skipped, **9 errors** |

So this lane's change **improves** the file and did not cause it. The same base also carries 7 reds
in `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py`, all `KeyError:
'the_verdicts'` — confirmed identically in the HEAD extract, and `the_verdicts` appears the same
number of times in my copy as at HEAD, so no edit of mine reaches it.

Both arrived with `d3b420cbb` ("the share the page leads with now carries its own null"), which
added ~345 lines to `tools/generate_value_arms_data.py`.

## Why this is BLOCKING rather than a note

The page is the business surface. A reader visiting it today gets a near-blank document, and
**nothing in the pipeline says so**: the door's own script error channel is `null`, so the failure
presents as a page that simply has nothing to say. That is the fail-silent class this project
names repeatedly — an unavailable check wearing a pass's colour — except here it is the artefact
rather than the control.

The second-order damage is that the site lane is red for every lane that touches `site/`, and a
lane reading that red will reasonably assume it is theirs.

## What I did NOT do, and why

I did not chase the cause. It is another lane's change, the repair is plausibly inside a 345-line
addition I have not read, and this lane had a landed increment to protect. Diagnosis stopped at
the point where I could prove it was not mine and could hand a next reader the measurements rather
than a suspicion.

## Where to start

1. `_live_harness.mjs` records only the FIRST error per block and continues (`scriptError =
   scriptError || ...`). A page erroring inside a `.then` that the door itself `.catch`es will
   report `null` while rendering nothing — see the harness's own comment at line 24. **The channel
   that should have caught this is the first thing to check**, because a door that cannot report
   its own failure will hide the next one too.
2. `KeyError: 'the_verdicts'` in the sibling suite is probably the same root cause read from the
   Python side, and it is much cheaper to debug there than through the harness.
