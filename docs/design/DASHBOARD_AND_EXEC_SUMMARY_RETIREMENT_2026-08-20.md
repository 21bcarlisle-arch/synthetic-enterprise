**Severity:** RECORDED · **Lane:** H_harness · **Instruction:** director, 2026-08-20

# The dashboard and the exec summary — decided, and what replaced the rule

> *"Decide what each is for. If nothing reads them, retire them rather than keep them
> consistent. If the dashboard earns its place, it should be data visualisation and analytics
> over the query store, not another hand-derived surface that can disagree with its siblings.
> And a rule beyond those two: a surface no reader can reach must never be able to block
> publishing."*

---

## First, a correction to the premise

I told the director that a consistency gate between these two surfaces **blocked publishing
outright** last night. **It did not, and I should not have said so.**

The gate is advisory: `generate_dashboard_data.generate()` writes `dashboard.json`
unconditionally and returns a verdict, and the only thing the caller does with a False verdict
is raise an NTFY. The log confirms the pipeline carried straight on — `CONSISTENCY GATE
FAILED` at 00:36:xx, `Generated site/data/customers/ JSON` in the same minute.

What actually stopped publishing between 19:17Z and 02:04Z was the producer: six consecutive
run failures (`KeyError: 'net_margin_gbp'`) from a `saas/` margin rename sitting uncommitted in
the shared tree. The gate alarmed *loudly, beside* a real outage, and I read the two as cause
and effect without checking. Same error shape as the two misattributions the night before.

**The decision below does not depend on the corrected premise — it is strengthened by it.**
A surface no reader can reach was not merely capable of blocking; it was firing a
`real_alarm`-class NTFY at the director on every cycle where two derived snapshots of the same
run drifted apart. That is worse than a block, because it is silent about being pointless.

## What each one is, measured

| | The dashboard | The exec summary |
|---|---|---|
| Page | `site/project/index.html`, 853 lines | none — never had one |
| Data | `site/data/dashboard.json`, 378 KB | `docs/observability/run_insights.json` |
| Reader route | **`/project` and `/project/*` have 301'd to `/proof/` since 2026-07-23.** The page also carried `noindex`. No link on the reachable site pointed at it. | **No page on the site fetches it.** Its `executive_summary` string is published nowhere. |
| Runtime readers | `/proof/` and `/world/` fetch `dashboard.json` | the retired consistency gate; and `generate_shadow_html.py`, which renders it onto `/shadow/` — itself unreachable |

The exec summary's entire output was being consistent with the dashboard. That is not a
figure of speech: remove the comparison and no behaviour anywhere changes.

## Decided

**1. The exec-summary comparison is retired.** `_check_consistency`, `_insights_metric` and
`_CONSISTENCY_CHECKS` are deleted (88 lines) along with ten tests that drove them. The alarm
text in `process_run_complete.py` now names what the *remaining* checks actually cover.

**2. The dashboard splits, because the page and the data have different answers.**
- The **page** is retired: `site/project/index.html`, its door test and its render harness are
  deleted. The 301s stay, so old bookmarks still land on `/proof/`.
- The **data** is kept: `/proof/` and `/world/` fetch `dashboard.json`, so it has real readers
  even though its page did not.

**3. `run_insights.json` keeps being generated**, because `run_history.json` accumulates from
it and is a registered source in the projections store (`tools/build_projections.py`), which
`tools/lab_query.py` queries. What it loses is the power to alarm and the power to gate. It is
now an internal record, which is what it always was.

**4. One exclusive feed stopped.** `site/data/test_mix.json` was fetched only by `/project/`
and cost **30–40 s of `pytest --collect-only` subprocesses every publish cycle** — about 7% of
an 8–9 minute cycle, for four weeks, for a file no reader could load. The generator is kept and
still runs on demand. Its in-cycle justification cited `BUDGET_UNCONSTRAINED.md`, a document
whose premise was withdrawn as false on 2026-08-03 and which CLAUDE.md says never to cite
again — it was still load-bearing in the pipeline.

**5. The director's steer on what a dashboard should be is recorded, not built.** If one
returns it is analytics over the query store (`tools/lab_query.py`, `functions/api/query.js`),
not a third hand-derived surface that can disagree with its siblings. Nothing is being built
toward that today.

## The rule, mechanised

> A surface no reader can reach must never be able to block publishing.

`tools/reader_reachability.py` walks the built site from the front door and answers which pages
a reader can actually get to. Three deliberate choices, each traceable to how this defect hid:

- **Transitive closure from `/`, not "does anything link to it".** `/project/` was linked from
  `/director/` and `/shadow/` — both themselves unreachable.
- **A redirect *source* is not a destination.** Links to `/project/` existed the whole time;
  every reader who followed one landed on `/proof/`.
- **Static hrefs only.** A JS-templated `href="./x/"+esc(id)+"/"` is a promise about data, not a
  verifiable route. This *under*-claims reachability, which is the fail-closed direction: it
  over-reports blockers, and a false report costs a conversation while a missed one cost eleven
  hours.

Fails closed on a missing front door **and** on an implausibly small walk — an empty answer
would mark every publish blocker as guarding nothing and invite retiring all seven.

`generate_dashboard_data.PUBLISH_VERDICT_CHECKS` then makes each of the seven surviving checks
name the page it guards, ratcheted in all three directions by
`tests/tools/test_publish_blockers_guard_a_reachable_page.py`:

| direction | mutation run | result |
|---|---|---|
| undeclared blocker joins the verdict | added a new `_check_exec_summary_vibes` to the conjunction | **fires** |
| a declaration names an unreachable page | pointed `_check_bridge_reconciles` at `/tours/` | **fires** |
| a declaration outlives its check | dropped `mix_claim_ok` from the conjunction | **fires** |

The check list is parsed from `generate()`'s AST rather than written out here, because a
hand-kept list of "the checks that block publishing" is a second definition of the verdict, and
this project has repeatedly found that exact defect in its own controls.

## Measured, not acted on: the rest of the site's dead weight

The same walk says **13 of 34 built pages are unreachable**, and of 47 files in `site/data/`,
**24 are fetched by no reachable page**. Two caveats before that number is used for anything:

- Some are **build-time feeds, not browser fetches** — `maturity_map.json` (350 KB) is loaded by
  `tools/generate_capabilities_door.py`, which builds the reachable `/capabilities/`. It earns
  its place. A naive cut here would have broken a live door, and nearly did.
- `evidence.json` (120 KB) is *deliberately* generated with its page held back as an honest
  placeholder (2026-08-19 ruling). Retiring it would be the retreat that ruling ruled out.

**`/director/` and its four feeds are left alone on purpose.** It is unreachable from the nav,
but it is the director's own surface and he may well open it by URL. Killing it is his call,
not mine — and it is the one item here I would not act on unasked.
