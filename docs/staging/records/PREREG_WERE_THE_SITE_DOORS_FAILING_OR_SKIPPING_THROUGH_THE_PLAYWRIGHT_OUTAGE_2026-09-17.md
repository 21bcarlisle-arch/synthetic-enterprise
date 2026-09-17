**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `playwright-lost-so-the-pixel-verification-door-cannot-run`)

# PRE-REGISTRATION: were the site door suites FAILING or quietly SKIPPING through the Playwright outage?

**Filed 2026-09-17, delivery seat, BEFORE running the door suites.** The drawn item names this as
the first thing to establish, and names one of the two outcomes as the more expensive
one. Registering the prediction before the run is the only way that judgement can be refuted.

---

## The question, as the drawn item put it

> *"Whether those door tests currently FAIL or quietly SKIP is the first thing the next hand should
> establish, because a skip here is the more expensive outcome: it reads as 'nothing to report' on a
> surface whose whole job is to refuse that reading."*

— `SEAT_FINDING_THE_MACHINE_HAS_LOST_PLAYWRIGHT_..._2026-09-17.md` §2.

## What I predict, and why

**Prediction: NEITHER. The door suites were unaffected by the outage, and will run green.**

The reasoning, from a read of the tree before any run:

1. A repo-wide search for `playwright` (all of `*.py`, `*.js`, `*.sh`, `*.md`, `*.yaml`, `*.json`,
   excluding `node_modules/`) returns exactly **nine** paths, and **not one of them is a door test
   or any other module under `site/`**: `package.json`, `package-lock.json`,
   `background/health_check.py`, `tests/background/test_health_check.py`,
   `tests/background/test_egress_allowlist.py`, `site/data/simplified.json`, an archived
   simplification YAML, `docs/observability/sanity_adjudication_ledger.json`, and the finding above.
2. `site/test_home_door.py`'s own docstring names the mechanism it actually uses, and it is not
   Playwright: *"these execute the page's ACTUAL inline JavaScript (via a **Node/vm harness**)
   against the REAL published `site/data/*.json`"*.
3. `node` is present and working on this machine; only the npm `node_modules/` tree was lost.

So the capability the alarm reports lost and the capability the doors actually use are **two
different things wearing one name**. If that is right, the expensive outcome the finding feared —
doors silently skipping for the outage window, poisoning every "done" claim in it — **did not
happen**, and no close in the window inherits doubt from this cause.

## What would refute me

Any of these, and I write the refutation next to this prediction rather than revising it:

- A door test that SKIPS, for any reason, on this run.
- A door test that imports `playwright`, or shells to `npx playwright`, through a helper whose name
  does not contain the string (the grep is blind to the mechanism implemented without the name).
- A door test that fails for a browser-availability reason rather than a content reason.
- The Node/vm harness turning out to resolve through `node_modules/`, so that the lost npm tree
  breaks it too. **This is the live risk in my prediction**: `node_modules/` is gone entirely, not
  just its `playwright` entry, and a `require()` of any npm package inside the harness would fail.

## The measurement

`python3 -m pytest site/ -p no:randomly -q -rs` (the `-rs` is the point: it prints the reason for
every skip, so a silent skip cannot hide in a dot). Run BEFORE restoring Playwright, so the run is a
true reading of the outage window rather than of the repaired machine.

## Second, separate prediction

**The restore will not change any door result**, because nothing under `site/` consumes Playwright.
If a door result DOES change after the restore, my model of the dependency is wrong and the first
prediction above is wrong with it.
