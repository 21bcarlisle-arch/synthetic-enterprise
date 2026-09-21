**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the status page states two net margins and T6 now fires on every tick"

# The status page's two net margins are ONE quantity at TWO vintages, and the run ledger they are compared against has been uncommitted for 64 days

**Delivery seat, 2026-09-19, claim
`the-status-page-states-two-net-margins-and-t6-now-fires-on-every-tick`. Predictions in
`SEAT_PREREGISTRATION_WHICH_OF_THE_TWO_NET_MARGINS_IS_THE_STALE_ONE_2026-09-19.md`, written before
the cause was traced and left uncorrected beside their results.**

---

## 1. The premise, and the duplicate-work note

The commit the item cites (`0bd90d7e0`) is an ancestor of `origin/main`, and **that does not spend
the premise** — it is the item's prior art. It repaired `detect_t6` to read every claim its
patterns find, and *that repair is what made this contradiction audible*. The work the item asks
for is on the page and was not done by it.

The duplicate-work note named
`the-status-page-states-two-net-margins-and-t6-now-fires-on-every-tick` as already held. That is
**this item's own id**, under this draw, `paths: []` — the same shape as the previous Lane 0 draw.
Not a rival claim.

## 2. What each figure counts — the question the item asked first

Both are `net_margin_gbp` as emitted by `tools/generate_insights.generate_insights` from
`total_net_gbp` of the same run artefact (which its own comment records as *including bad debt and
hedging costs*). **They are the same measure of the same book.**

| figure | what it is | clock |
|---|---|---|
| **£1,521,070** | the net margin of the simulation run at git `ac0869715` | **2026-07-17T09:57Z** |
| **£158,278.48** | the net margin of the latest completed run, git `52f572916` | **2026-09-19T21:39Z** |

So this is **not** the *average unit rate* shape the drawn item expected, and saying so matters more
than the fix: there is no definitional split here to name. It is **one quantity at two vintages**,
and the page stated the older one with no clock in a place a machine reads as the present. The
item offered two remedies — *"give each its own name and clock, or delete the one that is not the
book"* — and the measurement chooses between them: **the clock, not the name**, and nothing is
deleted, because a dated record of a past run is not a false claim.

The cohort did move materially between the two runs (1,588 bills over N=19 in July; 9,892 bills
now), which is why they differ by ~10x. A different cohort does not make a different measure, and
the July figure is the one the director already ruled absurd on the veteran sniff test
(`IDEA_FIRST_EXTERNAL_REGISTER`, 2026-07-24) — that ruling stands and is untouched here.

## 3. Why T6 could not stop firing, and why the alarm named nobody's defect

`detect_t6`'s claims surface was the whole of `docs/status/LATEST.md` — **268,525 characters**, of
which **192,701** sit under `## PREVIOUS`, an append-only log of dated entries recording what was
true, or what the site published, on some past day.

Measured on the real page before choosing anything:

```
live head (above '## PREVIOUS')     : 0 net-margin claims
below the heading                   : 2  — £1,521,070 (a 2026-07-23 record) and £158,278 (the run block)
```

With both in scope, T6 fires **exactly one trigger per tick and cannot do otherwise**: whichever
figure the comparator agrees with, the other stands as a permanent contradiction. And the trigger
it raised named **no defect anyone could fix** — £1,521,070 *was* the net margin at `ac0869715`, so
the only remedy the alarm left was to falsify the historical record. An alarm with no available
remedy is how a detector gets ignored, and this one had just been given its first coverage.

**Repaired:** `_current_claims` scopes the surface to the page's live sections. Absent the heading
the whole text is returned — an unrecognised surface is judged in full, because over-firing costs
one answered question and under-firing costs the catch while saying nothing.

**The trap on the other side was live, not hypothetical.** The run block is appended at the *foot*
of the file, below the history, and the live head carries no `£` at all — so a head-only slice
would have dropped the page's only current financial claim and left T6 returning the same `[]` it
returns when it agrees. That is precisely the fail-open `0bd90d7e0` had just closed, re-entered
through the surface instead of the read. `_LIVE_BLOCKS_BELOW_HISTORY` re-attaches it, and
`test_the_live_run_block_survives_the_history_scoping` drives it with a contradiction that must
still be caught, rather than with the absence of one — a scope that asks nothing passes any test
that only checks for silence.

Four legs, each mutation-proven in a `git archive` extract, each caught by the leg written for it:

| mutation | leg that fired |
|---|---|
| `_current_claims(...)` → the raw `claims_text` | `..._does_not_judge_a_dated_historical_record_as_a_current_claim` |
| `_LIVE_BLOCKS_BELOW_HISTORY = ()` (head-only slice) | `..._the_live_run_block_survives_the_history_scoping` |
| no-heading branch returns `""` | `..._an_unrecognised_surface_is_judged_whole...` |
| the block marker renamed (generator drift) | `..._the_live_status_page_still_offers_t6_a_net_margin_claim_to_judge` |

The last is keyed to the **property** — the real page still puts a current net-margin claim inside
the scoped surface — and deliberately not to the figure, nor to whether T6 is quiet today. A
control pinned to *"T6 fires nothing on LATEST.md"* would go green the day the page stopped stating
a net margin at all, which is the failure and not the fix.

**End state on the real page:**

```
computed £158,278 (live run ledger)     -> 0 triggers   # the page and the data agree
computed £1,521,070 (HEAD's ledger)     -> 1 trigger    # a real disagreement, correctly raised
```

The second row is not a leftover. It is the detector working, and what it is pointing at is §5.

## 4. The live figure had no clock either, because the line that carried it was deleted 78 days ago

`update_latest_md` stamped the run's git hash and date onto a `Net position:` line via
`re.sub(r"Net position: .*", ...)`. **That line was deleted from `LATEST.md` on 2026-07-03
(`e50ae96c1`)**, so for 78 days the substitution matched nothing and wrote nothing, without raising
— a zero-match `re.sub` is silent by construction, and there is no natural edge on which it could
have complained.

So the page's **only live financial figure carried no basis at all**, which is the rule in
`CLAUDE.md`'s own table (*"every financial figure carries its clock"*) and is the mechanical reason
the two vintages were indistinguishable to a reader as well as to the detector.

Repaired in the **generator**, not the file: the block now writes its own clock inline —
`auto-processed (…s / … min) // run <git>, <date>:` — so it is re-drawn on every run rather than
hand-annotated once and lost at the next write. The dead `re.sub` is deleted rather than
re-anchored: a second home for one published quantity is the shape this whole item is about.

The two July figures in `## PREVIOUS` are annotated in place with the vintage they published, so a
human reading the log gets what the detector now gets structurally.

## 5. THE FINDING UNDERNEATH — `run_history.json` has been uncommitted for 64 days

Filed rather than fixed, because the fix is not mine to pick and the evidence should not wait.

`docs/observability/run_history.json` is the artefact `detect_t6` names in its own `evidence_refs`
as *"raw data"*, and whose last entry is the comparator for every net-margin judgement. It is also
read by `generate_dashboard_data.count_run_history_total`, which publishes the Project tab's **"Sim
runs"** KPI on the live site, and by `extract_run_history`.

```
shared tree working copy : last entry 2026-09-19T21:39:56Z  git 52f572916  £158,278.48
HEAD (any fresh checkout): last entry 2026-07-17T09:57:51Z  git ac0869715  £1,521,069.65
git status               : ' M docs/observability/run_history.json'   (since 2026-07-17)
```

`append_run_history` is **not** broken — it appends on every run, and the two silent early returns
it does carry (a non-hex git hash; a non-positive net margin) are not firing. The file is simply
never committed. **Nothing anywhere reds on this**, and there is no natural edge on which it
could: the file is present, it parses, and it returns a number.

Consequences, stated as measured and as inferred, separately:

- **Measured.** T6's verdict on the status page inverts depending on which copy the reader holds,
  as §3's end state shows. Any session reading the run ledger from `HEAD` — which is every
  isolated worktree, including the one this finding was written in — gets July's book.
- **Inferred, not yet measured.** The publish gate grades a throwaway `HEAD` checkout. If the site
  build runs there, the "Sim runs" KPI and the run-history series are built from a 64-day-old
  ledger with 100 entries frozen since 2026-07-17. **This is the thread to pull next and I have
  not pulled it** — it is a different subject from the page, and guessing at it here would be
  exactly the invented answer `CLAUDE.md` forbids.

The remedy is a judgement between two shapes and should be taken deliberately: either the run
ledger is **tracked** and `process_run_complete` commits it with the rest of the run's artefacts,
or it is **untracked** machine-local state and `HEAD`'s stale copy is deleted so no checkout can
read it. It is currently both, which is the only option that fails silently.

## 6. What was NOT done

- The `HEAD`-vs-working-copy divergence in §5 is **filed, not repaired**.
- The site's published run-history series is **not measured** against the stale ledger (§5).
- The `## PREVIOUS` annotations in §4 are written into a file whose live copy is continuously
  read-modify-written on the shared tree by `process_run_complete`. They may be lost to a later
  write from that copy. **The determination does not depend on them** — it is held here and in the
  code comments, both of which are committed; the annotations are a convenience for a human
  reading the log.
