# DIRECTOR OBSERVATION — PUBLISHED SURFACE, THREE ITEMS

Staged by the advisor on the director's behalf, 2026-08-12.
Report-and-fix at your ranking. No priority attached — rank this against
the drain and the OPS10 class work.

## Provenance

Items 1 and 3 come from the director reading the live site. Item 1 was
then independently confirmed by the advisor against committed source
(see evidence below). Item 2 is an advisor observation from the same
page, and may be a false alarm.

## 1. The Knowledge section has no route in from the main nav

`site/index.html` links to: company, world, proof, glossary, now,
customers, evidence, privacy. It does not link to `./knowledge/`.

Nine knowledge pages exist and render — wholesale-price-formation,
electricity-wholesale, gas-wholesale, gb-electricity-market, merit-order,
hedging-forward-market, imbalance-cashout-settlement, price-cap,
carbon-price. The director reached one of them only via the Company
section. Eight are effectively unpublished.

Note the shape: work that exists, is correct, passes its tests, and is
connected to nothing that a reader can reach. That is the
uncommitted-and-orphaned class expressed in the published surface rather
than in code — and the first instance the orphan ratchet is structurally
unable to see, because it analyses callers in source, not routes in a
site.

## 2. Chart vintage stamps may be stale

On the wholesale-price-formation page the header reads data 2026-07 and
claims verified 2026-07-25, while every chart footer reads "as of
2025-06-07". This may be correct — different feeds, different vintages —
or it may be the published-figure staleness class. Confirm which, and
say so on the page if the difference is legitimate.

## 3. Nav alignment moves between sections — director preference

The nav sits on different sides depending on which section you are in.
The director's preference is consistent right-hand alignment.

This is director taste on a public surface, not a defect to diagnose.
But note it may share a cause with item 1: if the knowledge pages carry a
different nav treatment from the rest of the site, one fix may close
both.

## What is asked

Not these three fixes. The class behind them.

- Fold these into existing class work if they fit rather than filing them
  separately. OPS10's five classes already hold fifty-one instances; if
  these belong there, put them there.
- Sweep the published surface for the same shapes: any other page or
  section with no route in, any other stamp that disagrees with its own
  page, any other treatment that varies by section without reason.
- If the sweep shows this is one cause and not three items, say so and
  fix the cause.
- If a control could make "a published page with no route in" fail at
  build time rather than be found by the director looking at the site,
  that is worth more than the fix. Whatever you build must be
  deliberately breakable and shown to go red.

## Reserved

- No change to the orphan ratchet landed today unless the sweep shows it
  should have covered this.
- No new site structure work beyond what closes the cause.

## Epoch arc

Epoch 1 — core fidelity. This is the published evidence surface, not
company machinery: the knowledge pages are how the work is shown, and a
page nobody can reach shows nothing.
