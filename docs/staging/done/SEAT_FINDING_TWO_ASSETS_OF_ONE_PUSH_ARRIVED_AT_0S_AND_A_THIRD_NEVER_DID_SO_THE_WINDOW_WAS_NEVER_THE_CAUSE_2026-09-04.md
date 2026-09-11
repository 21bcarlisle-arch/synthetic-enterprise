**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING: two assets of one push arrived at 0s and a third never did, so the window was never the cause

Filed 2026-09-04 ~12:30 BST by the delivery seat, working the Lane 0 direction *"the figures
stopped reaching the reader and no direction ever named the path"*. Grades
`SEAT_PREREG_DOES_A_DIRECTORY_URL_EVER_CONFIRM_THROUGH_THE_DEPLOY_CHECKS_OWN_FETCH_2026-09-04.md`,
filed before any of the measurements below, and **corrects the finding it continues**,
`SEAT_FINDING_EVERY_DEPLOY_RED_FOR_THREE_DAYS_WAS_THE_VERIFIER_AND_NEVER_THE_PUBLICATION`
(2026-09-04, ~90 minutes earlier), which is right about the asymmetry and wrong about its cause.

LATENT, not BLOCKING: the control's **exit code has been right every time** — an unproven deploy
stayed red. What was wrong is what it *said*, and what the finding above concluded from it.

## The direction's own item was already discharged

Checked before assuming: `docs/observability/.publish_gate_state.json` read `{"alerted_at": null,
"failures": []}`; `git status --porcelain site/` was empty; the staging root held **zero**
`run_complete_*` files; all three `site/harness/` files were tracked at HEAD; HEAD ==
`origin/main` == `881debc8b`; last publish `75f2614d8` at 11:51. Another lane landed the unwedge
in `7d33c1986`, and the previous seat turn met the acceptance test and filed the finding above.
So this turn continued from there rather than re-doing it.

## What was measured, and in what order

**1. The tool's own fetch, against the live site, on a quiet tree** (prereg's subject). Importing
`url_for` and `fetch` from `tools/assert_deployed_bytes_are_served.py` rather than reimplementing
them, so the thing measured is the thing that runs in CI:

> **19 of 19 directory URLs matched. Control (`/data/proof.json`) matched. Status 200 on every
> one, no redirect — `final` URL was the requested URL with `?cb=` intact.**

So **H3 is refuted**: the fetch is sound. `?cb=` on a `/`-terminated path does not 404 (H3b), Pages
does not canonicalise the trailing slash away (H3a), and no third body is served (H3c). H4 (a
mixed population) is refuted too — the split is not per-page. H1, the validity check, held.

**2. The run logs of one red and one green** (not in the prereg; run because step 1 left "latency"
standing and latency is measurable). Red run `33858118312`, head `b0bceffae`, base
`1b98c836…`, three changed assets:

```
09:26:18  Run python3 tools/assert_deployed_bytes_are_served.py
          serving the deployed bytes after 0s: https://poesys.net/data/proof.json
          serving the deployed bytes after 0s: https://poesys.net/harness/test_the_deployment_reading_reaches_the_reader.py
09:34:05  FAILED: 1 of 3 changed asset(s) are still not what
          poesys.net serves after 8 minutes:
            https://poesys.net/harness/
```

## The finding

**Two assets of that push were served NEW on the FIRST attempt — `after 0s`, immediately after
`wrangler` exited — and the third never arrived in 467s. One push. One deployment. One edge.**

A window cannot explain 0s and >467s for the same deployment. Whatever the reds are, they are not
a clock set too tight, and **both remedies attempted so far were aimed at the clock**: widening
`ATTEMPTS` from 2m17s to 8m on 2026-08-20, and the 2026-09-04 reading that kept the clock only
because no distribution existed to widen it to. The `after 0s` line was printed in the log of the
run that failed, both times, and neither reading opened it.

What the asymmetry does fit is a **path-resolved route serving a cached resolution while
direct-file routes are already new** — the same Pages asset cache that kept eight deleted pages
alive through eight deployments on 2026-08-20, which a zone purge provably could not reach.

## Three claims in the finding above that this refutes

Kept beside them rather than quietly revised, because the pair is the evidence the experiment
preceded its answer.

1. **"the window is too short, not the deploy"** and *"`Owed next`: an observation of a directory
   URL promoting at all"*. The clock is not the subject, so that owed number would not have
   settled anything. Refuted by the `after 0s` lines above.
2. **"On 2026-09-04 every one of the ten reds was of this kind [UNCONFIRMED]"**, in the `classify`
   docstring and the finding. `classify` landed in **`b02b0c13c` at 11:22, after all ten reds** —
   it has never executed on any of them. That sentence is an inference from an hour-late
   hand-check, not an observation. *This was written into the prereg as a "must NOT happen" before
   the logs were opened, and is the one prediction that paid.*
3. **"No reader was ever served stale bytes — all 19 directory-index pages were verified
   byte-identical by hand"**, which carried the LATENT grade. That check ran at **10:20Z, 57
   minutes after the 09:23Z deploy**. It cannot speak to the window in which the control was red.
   On the reading above, a reader visiting `/harness/` in those minutes got the previous page
   while `/harness/test_…py` beside it was already current. **Not established either way, and it
   should not have been graded as settled.** A reader-end closure attests only what existed when
   it was written.

## My own prereg, graded

H3 refuted, H2 confirmed **as stated** — and the inference I attached to H2 was wrong. I wrote
*"then the 10 reds really were a window too short … `ATTEMPTS` is the honest subject after all"*.
The directory URLs did confirm on a quiet tree, exactly as H2 says, and the conclusion I had
pre-attached to that branch does not follow: a quiet-tree confirmation is silent about what
happens in the minutes after a deploy. The branch was right and the reading of it was wrong, which
is the same shape as the finding I am correcting. The prereg's value was its **negative** clause
(item 2 above), not its ranking.

## What landed

The control now separates a verdict about the reader from a shrug, using evidence it was already
collecting and throwing away. If **any** asset of this push was confirmed served at this edge,
then this push is live there — new bytes cannot come from a copy stored before they existed, which
is the same one-directional soundness argument the file was built on. A route not serving it is
then **STALE**, not unproven.

| verdict | when | says something about the reader? |
|---|---|---|
| `REPLACED` | serving exactly the overwritten bytes | yes — names which page they have |
| `STALE` | serving neither, **and a sibling of this push is live here** | yes — new |
| `UNCONFIRMED` | serving neither, nothing from this push confirmed | no, and says so |
| `RESOLVED` | arrived after the clock | the window, not the deploy |

`deployment_is_live` defaults `False` — the conservative direction. `REPLACED` outranks `STALE` by
**precedence, not composition**: both premises can hold and the more specific one is worth
printing. **The exit code is unchanged in every case**, and `ATTEMPTS` is untouched, as the prereg
required in advance.

Mutation-proved, each fired by the test naming that defect and by no other:

| mutation | test that fired |
|---|---|
| premise wired to constant `False` | `test_the_live_deployment_premise_is_DERIVED_from_a_confirmed_sibling` |
| premise wired to constant `True` | `test_a_push_where_NOTHING_reached_the_edge_claims_nothing_about_the_reader` |
| `STALE` branch removed | 3 tests, incl. the whole-partition reachability control |
| `STALE` moved above `REPLACED` | `test_REPLACED_outranks_STALE_because_it_says_more_about_the_reader` |

The two derivation legs are the ones that matter: every other verdict test *hands* the premise in,
so all of them would pass with a constant at the call site. Those two inject the branch through
`main()` on the exact mixed-push shape that has gone red ten times.

## Owed next — what is missing, stated as a question and not a number

**Does a reader actually get a stale page in the minutes after a page deploy?** The next push that
changes a `site/**/index.html` answers it, and now answers it in its own refusal: `STALE` or
`REPLACED` means yes and names the page; `UNCONFIRMED` means the deploy had not arrived at all.
Until one of those verdicts exists, the reader-facing question above is **open**, which is why the
finding it corrects should not have been closed with "no reader was ever served stale bytes".

If the answer is yes, the remedy is not the clock and not a zone purge — both are already refuted
— but the Pages asset cache for path-resolved routes, and that is a different piece of work.
