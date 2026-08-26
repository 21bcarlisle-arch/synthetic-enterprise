**Severity:** LATENT · **Lane:** H_harness

# The live verifier resolves two waves of feeds. The wall exhibit fetches three deep, so it can never pass.

**Found:** 2026-08-18, running R11 live verification after landing `SITE7` (`656ae7325`).
12 of 13 doors verified; `/customers/` failed, and it fails for a reason that has nothing to
do with the change that prompted the run.

**Class:** `controls_that_cannot_fail` — inverted. Not a control that cannot fail; a control
that cannot *pass*.

---

## Observed, with evidence

`site/live_pixel_verify.py` reports:

    [FAIL] /customers/  http=200 feeds=5 rendered_elements=13
             - G3 door fetched ../data/customers/C1g.json, which was not live

The feed is live. `curl -o /dev/null -w '%{http_code}' https://poesys.net/data/customers/C1g.json`
returns **200**, and `site/data/customers/C1g.json` is tracked at HEAD. Nothing is missing
from the deploy.

The cause is in the verifier's own two-pass design (`verify_door`, lines ~309–318):

1. **Pass 1** loads the feeds a static scan of the markup can see.
2. The harness reports every URL the door actually requested; anything new is fetched.
3. **Pass 2** re-renders with those.
4. `unresolved` from *pass 2's* render is reported as a failure.

The wall exhibit resolves in **three** waves, not two: the page boots and asks for the
household index; that payload yields a customer id, which produces
`"../data/customers/" + id + ".json"`; and *that* payload is what makes the page ask for
the gas leg, `C1g.json`. The third wave has no pass to be fetched in, so it is reported
unresolved on every run, forever, on a door that is serving correctly.

The module's own docstring already anticipates the mechanism and stops one wave short:

> several doors fetch through a helper (`jget(url)`, `j(url)`) or build the URL from a
> variable (`"../data/customers/"+id+".json"`), which no regex can resolve. Pass 1 renders
> with what was found and lets the harness REPORT every url the door actually asked for;
> pass 2 fetches those for real and re-renders.

Two passes closes the *variable-URL* gap. It does not close the *chained-dependency* gap,
and the wall exhibit is the door that has one.

## Why this matters more than one red door

R11 is a wall on this project: a user-visible change is done only when the live surface has
been fetched and the rendered value asserted. `/customers/` is 152KB, the largest content
page on the site and the exhibit the whole epistemic-wall claim rests on — and it is the one
door for which that wall's own instrument returns a permanent, uninformative red.

The practical consequence is worse than a false alarm. A permanent red trains its reader to
discount it, and this one sits on the door where a real regression would matter most. A
control that always fails is skipped, and a skipped control is not a control.

## Not claimed (R9)

- **Not caused by `SITE7`.** That commit's only change to the served page is the nav block
  (`git diff` on `site/customers/index.html` is nav-only); the failing URL is a data feed it
  does not touch, and the commit changed nothing under `site/data/customers/`. The carried
  `_wall_harness.mjs` is the *repo-side test* harness and is not the module this verifier
  uses (`site/_live_harness.mjs`).
- **Not verified as long-standing.** No prior live-verification record for this door was
  checked, so "it has always failed" is *inferred* from the mechanism, not observed. The
  mechanism is sufficient on its own: the third wave has nowhere to be fetched.
- **No claim that the door is broken.** Everything the reader sees renders; 13 elements came
  back with real content. The defect is in the instrument's reach, not the door.

## Candidate repairs — none chosen, this is QUEUED

1. **Loop until the requested set stops growing** (with a hard cap, say four rounds, and a
   named failure if the cap is hit). Closes the class rather than this instance, which is
   what R10 requires of an absurdity-class defect. The cap is the part that must not be
   forgotten: an unbounded loop against a door that requests a fresh URL every render is a
   hang, and a hang in a verifier reads as an outage.
2. Let a door declare its feed graph. Rejected on sight for the reason the module already
   states about hand-typed lists: it would go stale the first time a door added a fetch.

Option 1 is the likely answer, and it is a change to a control that gates published work, so
it needs its own mutation proof: a door that resolves in three waves must PASS after the fix
and must still FAIL when a genuinely absent feed is in the third wave.
