**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none -- this is a harness state, not domain understanding.

# The site lane is red at HEAD, and the working tree's "fix" deletes sixteen controls

**Found 2026-09-07** while landing a Knowledge page. **Reproduce:**
`git archive HEAD | tar -x -C /tmp/x && cd /tmp/x && python3 -m pytest site/test_harness_delivery_record.py -q`

---

## The state

**Three controls in `site/test_harness_delivery_record.py` fail in a clean HEAD extract.** The site
lane runs on any commit touching `site/`, so **no lane can land a site change** until this clears.

They fail because `site/data/delivery.json` renders a withheld message —
*"the product-ceiling artefact in this tree predates the ceiling/floor split, which IS the finding…
re-run `python3 -m tools.r4_product_ceiling --save`"* — while the controls assert the product table
and the two-sided A49 finding reach the reader.

**It is not visible locally.** In the shared working tree the same file collects **22** tests and
passes; at HEAD it collects **37** and three fail. The difference is not data — it is the test file
itself.

## Why I did not fix it

`site/test_harness_delivery_record.py` carries an **uncommitted working-tree change of +70/−697
lines that deletes sixteen controls**, including
`test_whether_the_gating_figure_SURVIVES_A_REDRAW_reaches_the_reader` and
`test_the_WHOLE_BOOK_magnitude_and_its_disagreeing_verdict_reach_the_reader`.

Landing that would make the lane green by removing the controls that are red. **Whether those
deletions are a considered retirement or an edit in flight is not mine to judge**, and a commit that
deletes sixteen controls needs its own message saying why — not a line in someone else's.

Regenerating the artefact is not enough either: I copied the freshened
`docs/observability/r4_product_ceiling.json` (which does carry `tariff_fit`) into a HEAD extract and
the controls still failed, because the page reads `site/data/delivery.json`, which is stale in both
tree and HEAD. So the repair is a publish-cycle regeneration plus a decision about the sixteen
controls, and both belong to the lane that owns R4.

## What it blocks

A finished Knowledge page — *"How many synthetic households represent Britain"*, the director's
request of today — is written, passes all 606 site tests **in the working tree**, and cannot land
because the site lane gates on the committed tree. The gate is behaving correctly; the tree is not.

## What is not affected

Commits touching no `site/` path land normally. The Knowledge-layer gate extension that accompanies
this finding landed without difficulty.
