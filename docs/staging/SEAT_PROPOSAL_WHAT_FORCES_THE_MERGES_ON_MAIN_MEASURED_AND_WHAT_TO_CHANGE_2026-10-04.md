# PROPOSAL — what forces the merges on main, measured, and what to change (2026-10-04)

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `what-forces-the-merges-on-main` (Lane 0 delivery)

**For the director.** You asked three things: what keeps causing the merges, whether they cost much,
and what to do about the files nearly every lane writes. Nothing measured any of it, so the
measurement came first: `python3 -m tools.merge_pressure_census [--since 14.days] [--json] [--tokens]`.
Its definitions are in its docstring. Every figure below comes from it, over origin/main for the 14
days to 2026-10-04.

## The answer in four lines

1. **The cause is one race, not many faults.** Every landing must fast-forward origin. Each gate
   takes about ten minutes, and origin advanced 890 times in 14 days (about 64 a day). So most
   landings find origin has moved under them, and must merge and gate again. Merges are themselves
   pushes, so they move origin too: 93 of the 417 merges were the second or later link in a chain.
   Fork refusals, wedges, reconcile loops and the shared tree falling behind are all this one race,
   seen from different places.
2. **The count is mostly noise, but the wait was not.**
   - **Mostly harmless:** 374 of the 417 merges touched no file the incoming side touched, and git
     merged them alone.
   - **The cost was re-running the gate on other lanes' changes.** That was 120.6 hours of landing
     wait across lanes before `3c5702901` (2026-10-03 21:57), at a median 748 s per merge. Since then
     the median is 149 s, and 24 of 43 merges ran no tests.
   - **But the total has not fallen in step.** Merges came 3.5 an hour after that commit, against
     1.25 before. So lane wait only fell from 9.7 to 7.6 hours a day.
3. **Conflicts are rare and scattered.** 22 of 417 (5%) needed someone to choose the bytes. Those
   are the expensive ones: the median gate wait is about 1,500 s, and a session has to read them.
4. **Tokens: about 4% of billed tokens** went to API calls that ran or resolved a merge (1,377
   calls). Push and promotion loops took about 1.5%. Reconcile and refresh work, the shared-tree
   symptom handling, took about 4.5%. Together that is roughly a tenth of the spend on the
   repository rather than the product. That is a ceiling, because the pattern match also catches
   calls that merely mention those tools.

## Which files drive merges

The kinds below are what arrived on the side a lane caught up to. A merge "forced by" a kind is one
where only that kind arrived, so had that kind not committed to main, the merge would not have
happened.

| forced by | merges | median wait |
|---|---|---|
| work | 364 | 664 s |
| mixed (two or more kinds arrived) | 31 | 1,085 s |
| heartbeat alone | 9 | 320 s |
| seat records alone | 6 | 1,147 s |
| nothing (empty) | 7 | 167 s |

**The heartbeat was not the main driver of merges, but it is a real cost.**
- It is 199 commits and 21% of origin's advances.
- On its own it forced only 9 merges; it arrived in 36.
- Every heartbeat commit also triggered a full Cloudflare site deploy.
- Before yesterday's selection fix, a merge that carried a `site/` file re-ran the whole site lane:
  1,188 s against 627 s. That cost is gone now.
- Taking it off main removes a fifth of origin's moves. That shortens chains, which this census
  counts but cannot price ahead of time. **Your steer is being built** (see "In hand" below).

## The shared files: what I would do and why

The deciding number is how often **both** sides of a merge changed the file. Only that can conflict.

| file | commits | merges where both sides changed it | conflicts | what I'd do |
|---|---|---|---|---|
| `docs/design/maturity_map.yaml` | 67 | 4 | **0** | **Nothing.** Git merges row edits cleanly. Splitting buys nothing measurable and has caused bugs before. |
| `docs/direction/DIRECTION.yaml` | 46 | 2 | 1 | **Nothing more.** The one conflict was yesterday's stranded seat. The reconciler now resolves that case itself when origin already holds the rows. |
| `docs/direction/decisions.jsonl` | 43 | 1 | 1 | Same event; same fix. |
| `docs/status/SEAT_STRETCH_LOG.md` | 20 | 1 | 1 | Same event; same fix. |
| `site/data/value_arms.json` | 55 | 6 | **6** | **Regenerate it on merge, never merge it.** All six fell on 22 September, during concurrent retakes. It is generated, but it is not in `derived_artefact_register`, which is what makes a landing regenerate a file instead of merging it. I'll add it if its generator can run inside the gate's extract. If not, one lane owns it. |
| `tests/architecture/test_static_quality_ratchet.py` | 19 | 4 | **4** | **Stop making every lane edit one line.** See below. |
| `docs/institutional/knowledge_map.md` | 21 | 3 | 0 | Nothing. |
| `docs/observability/gate_authorizations.jsonl` | 22 | 2 | 1 | Nothing yet. It is append-only, so a union merge would fit if it recurs. |

**The ratchet line is the one live hotspot.** `test_ruff_baseline_matches_frozen_census` demands
that the baseline literal *equal* today's count. So a lane that fixes a single import must lower the
same number on the same line, and two lanes doing that concurrently conflict: four times in five
days. While I was measuring this, it had also turned the shared tree red, because some lane fixed an
import there.

The ratchet's job is "the count never rises", and that leg stays. "The literal equals the count"
forces the edit. Planned change, reversible:
- keep failing on any rise;
- stop failing when the count falls;
- the Monday step lowers the literal to the measured count, once a week, as a single writer.

The cost is that slack of up to a week's improvements can be spent by a regression before Monday.
That is bounded and visible. **I'll make this change unless you object.**

## In hand, in this order

1. **Heartbeat off main, per your steer.** The liveness-only commit is replaced with a write to the
   ops repository (for your advisor), plus a single-commit `liveness` branch on the public repo for
   the website's banner. The ops repo is private, so the public site cannot read it.
   - The dead-man switch already ignores heartbeat commits.
   - Every reader of origin's or the site's copy is being given the new route.
2. **The ratchet change above.**
3. **`value_arms.json` regenerated on merge**, if its generator runs in the extract.
4. **This census as one line in the Monday end-to-end check**: merges, what forced them, conflicts,
   wait and tokens. The next fortnight should show whether 1 to 3 moved the numbers.

**Not doing now: a merge queue** (one lander serialising all landings, so no lane ever races). It is
the structural fix for item 1 of the answer, and the expensive one. If the race is still costing
hours a day after 1 to 3 and the selection fix have had a fortnight, the census will say so, and I'll
bring it to you with that number.

## The general rule, recorded

When a class of wasted work keeps recurring, ask why it recurs, not only how to clear this instance.
If nothing measures it, the missing measurement is the first thing to build. That is what this
document is.
