# SEAT FINDING — the published-supplier check inferred its subject from two figures agreeing, and the answer flipped by which tree regenerated it

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, lane 0 draw)
**Claim:** `two-artefacts-claim-to-be-the-companys-net-margin-and-the-gap-is-16597`
**Pre-registration:** `docs/staging/records/SEAT_PREREGISTRATION_WHICH_OF_THE_TWO_NET_MARGINS_IS_THE_COMPANYS_BOOK_2026-09-10.md` (prediction filed, refuted, kept beside the result)

---

## The question, and the answer

`site/data/value_arms.json`'s `realised.is_the_published_supplier` was WITHHELD, caught between
£131,289.34 and £147,886.78 with nothing establishing which is the company's book.

**The company's book is £147,886.78** — run `36e3ee8c4` /
`run_output_36e3ee8c4_20260909T210648Z.json`. Established, not chosen by nearness:

| evidence | says |
|---|---|
| `site/data/publish_provenance.json` → `showing_run` (committed every publish) | `run_id` = `run_output_36e3ee8c4_...json`, `git_commit` = `36e3ee8c4` |
| `site/data/dashboard.json` → `meta` | same file, `git_commit_source: "run_stamp"` — the authoritative tier |
| shared tree's `docs/reports/run_output_latest.json`, **working copy** | `total_net_gbp` 147,886.781507, `producing_commit.commit` **36e3ee8c4** |
| `background/sim_runner.py:417-418` | copies each fresh versioned run onto that path after every run |

**£131,289.34 is not a rival book.** It is the *committed blob* at the same path, frozen at
`0247f3061` (2026-09-01), because that path is not in
`background.process_run_complete.git_commit_push`'s publish surface. `0247f3061` said so in its own
STILL OWED section — *"the next publish that moves the book will ship the output without the input
again"* — and 19 publishes in the following seven days did.

So the two artefacts were never two runs competing for one quantity. They are one path, working
copy versus committed blob.

## The defect, which is in the reader and not in either artefact

`_is_the_published_supplier` established its subject by **arithmetic**: it treated
`run_output_latest.json`'s `total_net_gbp` matching `dashboard.json`'s `portfolio.net_margin_gbp`
as proof they were the same run. Two figures agreeing is evidence of identity and is not identity.
That has both failures at once:

* **False pass.** Two different runs landing within £0.01 read as one run, and the feed then makes
  a claim about "the supplier this site publishes" on an artefact that is not it. Not far-fetched:
  the A/B's own arms sit £67 apart on ~£148k.
* **False refusal, and this one was live.** The committed blob is a real, current run's *path* at
  a stale *revision*, so the check saw a £16,597 gap and reported *"the two are not the same run"*
  — a claim about the RUN, and false. Nothing was wrong with any run.

**The published verdict alternated by which tree regenerated the feed.** Six consecutive commits
to `site/data/value_arms.json`, same generator, same code, opposite sentence to the reader:

| commit | verdict | run figure read |
|---|---|---|
| `eb0054acf` | `checked=False` | 131,289.34 (clean checkout) |
| `d648c7e2a` | `checked=True` | 147,886.78 (shared tree) |
| `bee46622d` | `checked=True` | 147,886.78 |
| `65e5c172f` | `checked=False` | 131,289.34 |
| `7148b6260` | `checked=True` | 147,886.78 |
| `39065da9d` | `checked=False` | 131,289.34 |

A refusal that names the wrong cause sends the reader to the wrong remedy. "Two different runs"
sends them to re-run or re-publish the A/B; nothing there would move it.

## The repair

`fe895db3a` — the commit this item was drawn against — is what made the honest version possible:
it put `producing_commit` at the top of the run output's payload, so the artefact states its own
identity. `showing_run.git_commit` on the other side has always been committed by the publish
cycle. **Both sides name a run, so the gate now compares run identities and the money is left to
answer the question it can actually answer — how big the difference is, once the subject is
settled.**

`tools/generate_value_arms_data.py`:

* `_same_run_verdict()` — establishes `same` / `different` / `unestablished` from
  `producing_commit.commit` against `publish_provenance.showing_run.git_commit`, comparing by
  **prefix** (one side is short-sha, the other may be the full 40).
* `_withheld_statement()` — the refusal names **which of three things** is wrong: a genuinely
  different run, a site that does not say which run it shows, or the live case — an artefact that
  cannot name its run, where the statement names the path and the publish surface as the cause.
* The old dashboard-mismatch refusal is **kept as its own branch**, and it now means something
  narrower and sharper: both sides claim the same run and report different net margins. One run
  cannot have two net margins, and its remedy is not "re-publish the run output".
* `run_identity` is published in the feed, so a reader meets the verdict and not just the sentence.

## What it says now, at real inputs, on both trees

**Clean checkout** (what HEAD's bytes now carry):

> This feed cannot say whether the baseline arm is the supplier the site publishes. The run
> artefact it reads does not say which run produced it (and says so in its own payload), and the
> site says it is showing run_output_36e3ee8c4_20260909T210648Z.json.
> `docs/reports/run_output_latest.json` is refreshed on disk after every run but is not in the
> publish surface, so its committed copy can be many runs behind the figures published beside it
> — and this feed cannot tell that apart from a genuinely different run. […] The run artefact
> reports £131,289.34 and the figure the site publishes reports £147,886.78, a gap of £16,597.44.

**Shared tree**, against the published run — identity `same`, and the question gets answered:

> The published run's net margin (£147,886.78) is NOT the baseline arm's (£147,954.26) — they
> differ by £67.47.

## Controls — poison round first, then seven mutations, each killed by its named leg

Poison round: all seven legs green at HEAD before any mutation, because "survived" means two
opposite things.

| mutation | killed by |
|---|---|
| identity gate deleted (fail-open) | the DIFFERENT-run leg, the cannot-name leg, the site-silent leg |
| verdict always returns `same` | the cannot-name leg |
| **gate refuses everything** | the penny leg, the short/full-sha leg, the divergence leg |
| refusal drops "not in the publish surface" | the cannot-name leg |
| refusal drops the path name | the cannot-name leg |
| refusal drops the gap size | the cannot-name leg |
| `_same_commit` by equality, not prefix | the short/full-sha leg |

The third row is the one this project keeps needing: a guard that refuses *everything* passes every
test that asks whether it refuses correctly. `test_a_penny_of_divergence_is_still_the_same_supplier`
and `test_a_short_sha_and_a_full_sha_for_ONE_run_are_the_same_run` are the legs that prove the gate
can be PASSED, and they are what redden when it cannot be.

`test_a_DIFFERENT_run_is_caught_by_IDENTITY_even_when_every_figure_agrees` is the control the old
check could not have had: every figure agrees to the penny and the artefact is still not the
published run. Under the arithmetic gate that case asserted *"the supplier on the front of this
site IS the baseline"*.

170 passed in `tests/tools/test_generate_value_arms_data.py`; 130 passed / 1 skipped on the door,
`site/test_the_baseline_comparison_reaches_the_reader.py` — the page's own JavaScript against the
real feed, so the new refusal is proven to reach the reader and not just the JSON.

## What is NOT closed, and the cost I did not take

**1. The publish surface still omits the path, so the feed will go on alternating.** Both sides of
the alternation are now honest and correctly named, which is the whole of what this repair buys —
it does not stop the oscillation.

The obvious fix is to add `docs/reports/run_output_latest.json` to
`git_commit_push`'s file list. **I did not take it, and this is a decision and not an oversight.**
`0247f3061` measured the cost — 27.6 MB raw, ~2.8 MB packed, once per publish that moves the book —
and said it should be taken out loud if it became binding. Measured this week: **19 publishes in 7
days**, so that is ~53 MB packed per week, ~2.8 GB/year, on a figure a reader never opens. That is
not obviously worth it, and it is the director's call and not mine to make silently. Reversal is one
line either way.

**2. There is a cheaper repair available and it should be considered first.** The feed needs two
things from the published run: its identity and its net margin. **Both are already committed** —
identity in `publish_provenance.showing_run`, net margin in `dashboard.json`'s
`portfolio.net_margin_gbp`, stamped with the run it came from. So the check may not need
`run_output_latest.json` at all, and the 27 MB question may not need answering. Not done here
because it changes what the feed's subject IS, which is a bigger move than this item asked for.
The caveat to check first: `dashboard.json`'s figure is `_fmt`-rounded to 2dp against a £0.01
tolerance.

**3. `generate_dashboard_data._find_latest_run_json()` cannot run outside the shared tree, and
nothing says so.** It globs `docs/reports/run_output_*[0-9Z].json` and sorts by **mtime** over
files `.gitignore:40` ignores. In the shared tree that is the freshest run and is correct. In a
clean checkout it silently picks one of four force-added **June 2026** artefacts by checkout mtime
— the site's headline net margin, from a three-month-old run, with no refusal anywhere. Only
`process_run_complete` generates the dashboard today, so this is latent rather than live. It is a
separate finding and is not repaired here.

**4. The £67.47.** With the subject settled, the feed's answer on the published run is that the
supplier this site publishes is NOT the baseline arm — they differ by £67.47 on ~£148k (0.046%).
That is the substantive question this item's staleness artefact was masking half the time, and it
is open. It is small enough to be re-run nondeterminism and large enough to be 6,747× the feed's
own £0.01 tolerance; nothing here establishes which. Handed on.
