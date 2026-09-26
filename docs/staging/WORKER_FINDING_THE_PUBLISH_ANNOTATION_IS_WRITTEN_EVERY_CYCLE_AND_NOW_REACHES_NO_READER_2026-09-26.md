**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publish annotation is still written every cycle and now reaches no reader at all, and the ruling that withdrew its only reader recorded two readers that do not exist

## What was established, and how

Found while unwedging the publish gate (the red was
`tests/background/test_publish_decoupling_exit.py::test_the_annotation_reaches_the_rendered_page`).
Not inferred from the ruling's prose — counted in the tree at `389da83b7`.

`74900fcf0` ("the public banner said publishing was failing through six successful publishes, and
its third line was repository provenance no reader needs") withdrew the annotation line from the
public banner on the director's 2026-09-26 ruling. That decision is right and is not what this
finding disputes.

The comment it left in `site/assets/freshness-banner.js` says:

> *The counts stay in `publish_provenance.json` for the health page and the machine, which is
> where they are read.*

**Both named readers are absent.**

* **There is no health page.** `site/` contains exactly two HTML pages, `index.html` and
  `404.html`. `grep -rln publish_provenance site/ --include=*.html --include=*.js` returns
  `site/assets/freshness-banner.js` and nothing else — the asset whose slot was just removed is
  the *only* site-side reader of the feed.
* **No machine reads the fields.** Outside `background/publish_provenance.py` itself (which only
  *writes* `state["annotation"]`, line 478), no module in `background/`, `tools/`, `company/` or
  `saas/` reads the annotation. `background/sanity_daemon.py` calls
  `adjudication.open_findings()` — a different function over the adjudication ledger — which is
  the near-miss that makes this read as covered.

Meanwhile the producer is fully alive and pays for itself every cycle:
`process_run_complete._open_findings_count()` →
`publish_provenance.record_annotation(open_findings=…, nonblocking_reds=…)` →
`site/data/publish_provenance.json`, at `process_run_complete.py:8205`, `:8262` and `:8297`.

So `open_findings`, `nonblocking_reds`, `nonblocking_reds_total`, `nonblocking_reds_measured_on`
and `checked_at` are computed, written and published every publish cycle, and are read by nothing.

## Why this is a finding and not a fix

Two remedies exist and **both are design calls above this lane**, which is why this is filed
rather than actioned:

1. **Stop writing them** — if no reader is wanted, the write is cost and the field is a trap for
   the next reader who assumes a published field is a used one.
2. **Build the reader** the ruling assumed — an internal health surface, which is a page, and
   pages are the director's.

Choosing (1) silently would destroy a record the ruling explicitly intended to keep. Choosing (2)
silently would re-add a surface the same ruling just removed. Neither is mine.

## The class this belongs to

`no_caller_and_never_runs`, in the direction this repo has paid for before: not a function nobody
calls, but a **published artefact nobody consumes**, which is harder to see because publishing
looks like delivery. The field is in the live feed at `https://poesys.net/data/publish_provenance.json`,
so every check that asks "does it reach the site" answers yes. The question that fails is "does
anything READ it", and no control asks that.

## What this cost already, measured

The withdrawal left two controls asserting the opposite of the ruling, and they wedged publishing
for an episode of 5 failures (~286 min):

* `test_the_annotation_reaches_the_rendered_page` — grepped the asset for `open_findings`,
  `nonblocking_reds` and `"open finding"`.
* `test_the_tree_the_reds_were_counted_on_reaches_the_rendered_page` — grepped it for
  `nonblocking_reds_measured_on`, and its own docstring named the companion door that `74900fcf0`
  deleted in the same commit.

Both withdrawn at the head of this finding's commit, pointing at
`site/test_freshness_banner_publish_state.py::test_the_feeds_repository_annotation_does_not_reach_the_public_page`,
which holds the ruling's property in the correct direction by RENDERING the page.

**Why the gate did not catch this at `74900fcf0`:** gate selection is by subject module stem.
That commit touched `process_run_complete.py`, `freshness-banner.js` and the site door; nothing in
it was named `publish_decoupling_exit`, so neither test was selected. The reds were only ever
reachable from a full-suite run, which is the publish gate — i.e. the first thing to notice was
the thing they blocked.

**And the third assertion would never have gone red at all.** `"open finding" in js` was still
passing at `389da83b7` — satisfied by the COMMENT that documents the removal
(`freshness-banner.js:354`, "This slot rendered \"Published with N open findings…\""). A control
that greps source cannot tell a rendered clause from prose describing its deletion; two of the
three legs went red together and the third was green on the evidence of its own obsolescence.

## The pre-registered prediction

**PREDICTED:** a census of readers of `site/data/publish_provenance.json`'s `annotation` object,
run at any commit after `74900fcf0`, finds zero outside `publish_provenance.py`'s own writer and
its tests.

**WHAT WOULD REFUTE ME:** any non-test consumer — a daemon, a tool, a page, a generator — reading
`open_findings` or `nonblocking_reds` from the feed or the state. I searched `background/`,
`tools/`, `company/`, `saas/`, `site/*.html` and `site/assets/*.js`. A reader outside those roots
would refute this.
