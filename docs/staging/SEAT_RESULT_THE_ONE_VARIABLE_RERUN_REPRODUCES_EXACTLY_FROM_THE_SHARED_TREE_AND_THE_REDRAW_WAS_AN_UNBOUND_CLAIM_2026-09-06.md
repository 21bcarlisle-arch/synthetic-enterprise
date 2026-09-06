**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The one-variable re-run reproduces exactly from the shared tree — and the redraw was an unbound claim, not unfinished work

**Drawn item:** *"Re-run the COMMITTED `r1_inference_ceiling` instrument against
`run_output_23cbe058b_20260906T141424Z.json` — the book the page currently publishes — so re-keying
is the ONLY variable."*
Claim `the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.

**The premise is spent.** That run landed at `50081fb4e`, which is already an ancestor of
`origin/main`. This document records two things: that its numbers reproduce **independently, from
the shared tree**, and **why the item was drawn again anyway**.

---

## Part 1 — the premise, re-measured rather than trusted

`50081fb4e` was written from `/var/tmp/se-seat-executor`, a locked worktree. A landed claim's own
measurement is worth re-running from the other tree before it is called complete, so it was.

The working-tree copy of `tools/r1_inference_ceiling.py` is **another lane's in-flight version**
(dirty, and its `measure()` returns a `field_provenance` key HEAD's does not), and
`docs/observability/r1_inference_ceiling.json` is **held dirty by that same lane**. So HEAD's source
was read out with `git show` and `measure()` called directly — `main()` is the only writer of
`OUT_PATH`, and the artefact's md5 was checked either side to prove nothing wrote it. The book is
gitignored run output, so this had to run in the shared tree and not an extract. **4.7 seconds.**

Every quantity `50081fb4e` cites for this cell reproduces:

| quantity | `50081fb4e` claims | re-measured here |
|---|---|---|
| households graded | 213 → **149** | **149** |
| ceiling (best of 45) | +0.6127 → **+0.6308** | **+0.6308** (in-sample +0.2288, n=69) |
| selection-corrected p | **0.0249**, 4/200, unmoved | **0.0249**, exceedances **4**, bound_p95 0.5779 |
| full-coverage rung | observed **+0.0537**, p **0.8657** | **+0.0537**, p **0.8657**, does not clear |
| census | 264 supply points, 177 households, 87 legs | **264 / 177 / 87**, base seed 20260724 |
| fields moving | **two** of ten, both 213-coverage | **two** — see below |

And the "eight of ten byte-identical" claim, which is the load-bearing one, is confirmed
field-by-field against the pre-keying column the page publishes:

| field | scope | published (pre-keying) | committed instrument, same book |
|---|---|---|---|
| `perceived_bill_saving_gbp` | decision_only | n=69, +0.4799 | n=69, **+0.4799** |
| `company_churn_estimate` | decision_only | n=69, +0.2362 | n=69, **+0.2362** |
| `expected_term_margin_gbp` | decision_only | n=56, −0.0061 | n=56, **−0.0061** |
| `resentment_score` | decision_only | n=69, refused | n=69, **refused** |
| `svt_rate_gbp_per_mwh` | account_state | n=69, −0.1263 | n=69, **−0.1263** |
| `rate_vs_svt_pct` | account_state | n=69, −0.3530 | n=69, **−0.3530** |
| `unit_rate_gbp_per_mwh` | account_state | n=100, refused | n=100, **refused** |
| `company_eac_kwh` | account_state | n=69, −0.0645 | n=69, **−0.0645** |
| `mean_recent_margin_rate` | account_state | n=213, −0.0422 | n=**149**, **+0.0537** — moved |
| `portfolio_premium_pct` | account_state | n=213, −0.0509 | n=**149**, **−0.0401** — moved |

Nothing is added to the record's conclusions and nothing is refuted. The one thing this adds is
that the result is **cheap to reproduce** — 4.7s from the shared tree — so it is not a measurement
anyone has to take on the word of a worktree that is now locked.

**No artefact is regenerated and no page changes.** `site/data/delivery.json` is already staged by
the other lane at the corrected figures (`n=164`, `+0.6308`, no `+0.6127` left in it) and HEAD's
committed `docs/observability/r1_inference_ceiling.json` already carries 164 / +0.6308 / p 0.4328.
The exposure the earlier finding left open is closed. Landing a third variant of the same number is
the failure this project calls two lanes fixing one defect concurrently.

## Part 2 — why a finished, pushed item was drawn again

At the start of this tick the claim was **open with `paths: []`**:

```
"the-r1-ceiling-is-a-selected-maximum-published-as-a-bound": { "claimed_at": 1788726308.8, "paths": [] }
```

`/var/tmp/se-seat-executor/docs/observability/.delivery_lane_claims.json` is **3 bytes — `{}`**,
last written 2026-09-05. So **no store anywhere holds a binding** for `50081fb4e`. From the record I
cannot tell whether `--landed` was never run or was run somewhere neither store can see, and I do
not claim either; the outcome is identical and it is the point. Work that is committed, pushed, and
an ancestor of `origin/main` is **invisible to the lane that commissioned it**, so the sweep returns
the claim to the pool and the next tick draws the same direction. This tick is that draw.

This is the class
`SEAT_FINDING_THE_STORE_REPAIR_LANDED_WAS_NEVER_BOUND_AND_THE_LANE_RE_OFFERED_IT_2026-09-05.md`
filed, still open in the root, recurring on a different claim one day later. Its recommendation —
*"bind in the landing turn, always; no new mechanism is proposed here"* — was the right call and it
did not hold, because the habit is the thing that a bounded turn ending early is worst at keeping.

Bound this tick, from the shared tree, against the already-landed commit:

```
python3 -m background.delivery_lane --landed the-r1-ceiling-is-a-selected-maximum-published-as-a-bound --commit 50081fb4e
→ bound 3 path(s)     (verified in the store, not read off the message)
```

### And that bind should have been refused, by the record as it stood yesterday

The prior finding states flatly: *"a landing that was never bound in its own turn **cannot** be
bound retroactively by the next one — the guard that stops a re-draw stealing earlier work also
stops an honest repair."* On this claim it **can be**, and the discriminator is worth naming
because the sentence as written will send the next seat round the long way:

| instant | value | |
|---|---|---|
| `first_drawn_at` (draw ledger) | 1788707110 | 2026-09-06 **15:05:10Z** |
| `50081fb4e` commit time | 1788725645 | 2026-09-06 **20:14:05Z** |
| `claimed_at` (this re-draw) | 1788726308 | 2026-09-06 **20:25:08Z** |

The commit predates the **current** claim by 11 minutes and would be refused against it. It
postdates the id's **first** draw by five hours. `delivery_lane._binding_instant` compares against
`first_drawn_at` and only falls back to `claimed_at` when the ledger has never heard of the id — so
the retroactive bind is refused exactly for a **promoted or hand-off id that never went through
`draw()`** (the case the prior finding was written from) and succeeds for an id with draw history,
which is this one. The repair the prior finding said was not available had in fact been built.

**The generalisable part:** a bounded seat working from an isolated worktree can complete its
direction, land it, push it, and still leave the lane reading "not started" — and the only symptom
is that the item comes back looking like unfinished work. The cheap check before doing a drawn
item's work is not "does the code look done", it is **`paths: []` in the shared tree's claim store
against `git log` for the subject**. Those two disagreeing is the signature, it costs one turn of
measurement to fall for, and when the id has draw history the recovery is one command.

**Released** on this note.
