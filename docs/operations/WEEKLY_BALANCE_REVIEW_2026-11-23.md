# Weekly balance review for the week from Mon 23 Nov 2026

*Delivery seat (worker tick), drafted Sun 22 Nov about 08:40 GMT, ahead of the Mon 23 Nov 03:00 GMT reset, as
the 81% reading asks. It is a proposal under the 11 Nov ruling (point 4). If he has not answered by
the reset, it stands, and he can change it at any time. It carries the five things the 81% reading
lists, the 22 Nov curiosity steer's design and cost, and the placement of the 22 Nov speed track.*

## 1. Triage counts

The four batches dispositioned between 20 Nov 06:26 and 12:06 GMT. Each finding got exactly one
disposition:

| Batch | Commit | Fixed | Real | Parked | Obsolete | Total |
|---|---|---|---|---|---|---|
| The ten BLOCKING | 6594aec2b6 | 7 | 2 (re-graded LATENT) | 0 | 1 | 10 |
| Supplier batch 1 (oldest B–E) | 17b3697d6d | 8 | 0 | 5 | 7 | 20 |
| Supplier batch 2 | 8ee7d4be90 | 11 | 3 | 2 | 4 | 20 |
| Supplier batch 3 (23–29 Oct) | dfd53e8bf0 | 9 | 8 | 1 | 2 | 20 |
| **Total** | | **35** | **13** | **8** | **14** | **70** |

**The open count.** On 20 Nov the advisor counted 204 open, which the batches took to 165. Today's
draw reads **203 open: 2 BLOCKING, 171 LATENT, 30 RECORDED**. That is not a reversal. The two numbers
count different things. 165 counted documents in the staging root. 203 counts every open item in the
one work system's store after the cut-over (§2), which also holds findings filed since. The item
store on disk holds 175 open finding items. The rest of the draw's 203 are items from its other
sources. **No triage batch has landed since 20 Nov 12:06.** About 92 supplier money findings were
named in the 15 Nov plan and 60 are dispositioned, so **32 remain, plus everything filed since.**

## 2. The work system's cut-over

- **Increment 1 (20 Nov, 6aaec3c8b1).** The item store and `next_item()` went live in shadow. 185
  root findings became 185 items, with none refused. The shadow cost 32 ms a draw.
- **Increment 2 (21 Nov, e1b34c245a).** The map's atom steps became a shadow source with no dial.
  96 live atoms became 96 items, with none refused.
- **Increment 3, the cut-over (21 Nov 14:20, 5532d24b2d).** The side-by-side day passed its own
  test: 0 real failures, and where both draws named a finding they agreed 96 of 96. Staging
  findings are now items. Rung 1c and the draw read the store, and the staging root's findings
  listing went from 161 names to 1.
- **Not yet cut over:** the map atoms (still shadow), continuations and the advisor queue. The draw
  that gave this tick its work still carries the self-refill's dial-weighted three-lane block. The
  dials were retired on 21 Nov.
- **The share table runs, on thin data.** This tick's pick says "correctness 42%, 2 of 4 landed this
  week". Four landings since the cut-over cannot tell a share from noise. The first readable week is
  this one.

## 3. Why both slipped in the first half of last week

**The likely cause: the plan ranked them, and the ranking never reached the mechanism that draws.**
The 15 Nov plan's §5 lived in a document. The draw read continuations and the map, and neither the
triage nor the one work system had a continuation. So from Mon 16 to Thu 19 Nov nothing could draw
them. The open count rose from 184 to 204. Two handoffs were written at about 06:30Z on 20 Nov. The
first triage batch landed at 07:52Z the same day, and the work system's K8 page at 07:13Z.

It is the same shape as the week before ("the pause never reached `feature_share`"), and that makes
it a pattern: **a plan in prose does not move a draw.** The cut-over in §2 removes the cause for
findings, because the draw now reads the item store directly. It does not yet remove it for this
review's own §5. **The remedy proposed:** each ranked item in §5 below is written as an item the
draw reads, in the same commit that lands this review, or it is not in the plan. Where that is not
yet possible (the store has no "direction" source), it goes onto the seat's lane-0 focus, which the
draw does read. This tick did not do that, so the seat's next orientation owes it.

## 4. The floor per lane

**Proposed: 5% per row, as now set** (`docs/direction/priority_order.yaml`, `weekly_split.floor`,
refused below it by `work_items.load_shares`). That is one pick in twenty, half the smallest row (10%,
knowledge). It is low enough that the review's shares still decide the order, and high enough that no
lane starves for a week. If the shares stay as below, no row is near the floor, so the floor binds
only when a future review cuts a row to 5–10%. That week is the test of whether 5 is enough.

**The shares: unchanged from 16 Nov** (correctness 42, supplier features 18, world features 15,
harness 15, knowledge 10). The store has drawn by share for about 18 hours. There is no landed week
to say any row is wrong, and moving several rows at once could not be attributed. The path-class
count for 16–22 Nov (455 non-merge commits) is:

| Class | Commits |
|---|---|
| Records and staging | 188 |
| Harness | 96 |
| Site | 77 |
| World | 28 |
| Knowledge | 28 |
| World and supplier together | 22 |
| Supplier | 16 |

That is a rough first-hit classification by path, not by purpose. It is not a share reading, as the
16 Nov review showed.

## 5. Bill shock and the customer voice: where they sit

- **Knowledge (10%), first.** Both K8 pages landed on 21 Nov: how households respond to bill shock
  (two families, three SVT moments, by payment method, coding proven on 16 published accounts,
  7128283615) and the customer-voice theme map (fc7976e4f8). G1's media-moment readings landed the
  same day (26e4555df1, 80e1ba16a1). Still owed in knowledge: **household time per problem type**
  (the 22 Nov call-time addendum), due 4 Dec. It is held as stated ranges, tricky problems costing
  most, grounded in the coding's "time and effort spent" field.
- **World features (15%), next.** The bill-shock world build extends activation energy, grievance,
  payment behaviour, DD failure and contact, with no parallel shock table. It sits beside the meter
  data faults. The commitment `bill-shock-responses-knowledge-page-with-the-customer-voice-coding-scheme`
  is due 4 Dec. Its validation gate names historical targets with tolerances before any run.
- **Supplier features (18%).** The value test comes first (§7). Then B8's retention holdout, which
  he approved on 22 Nov, default-off at the derived share (due 4 Dec). The customer-voice themes
  that became supplier items queue behind it.
- **The curiosity steer applies here first** (§6). Every rate the bill-shock page states needs its
  mechanism and a second view before the world build reads it.

## 6. The curiosity steer (22 Nov): design and cost

His words: "we lack a little curiosity and desire to learn. To figure out more deeply how stuff
works and if answers make sense." The design is folded into what exists, and adds as little as
possible:

| Leg | Folded into | What it removes or replaces | Cost |
|---|---|---|---|
| **The measure (landed today).** A tally of nonsense found by the director or the advisor before the machine found it | `docs/institutional/ways_of_working.md` W5 (a learning-loop entry), with 6 baseline rows | Nothing. It makes the gap visible | Minutes a week. The seat adds a row when a steer or chase names a case |
| A GAP clears a standard search list, and names the decision that needs it, before it reaches him (landed today) | The contact-centre page §5a holds the list. `director_concerns --raise` is where it would be checked | Questions with no decision behind them | None to run. A check in `--raise` is about an hour, proposed only if the tally shows a repeat |
| A second view before a number feeds the world, the supplier or the site: a second source, a per-unit restatement, an order of magnitude, or an identity | The K8 page template, as one line "checked by: …". It extends the existing "print the numbers at real inputs" habit | Folds into K8. No new gate | About 10 minutes per page |
| Mechanism on every rate: what causes it and what would move it | The same K8 template line | Pages that give only a number count as unfinished | Applied to bill shock first |
| Surprise is work: an outlier or a result that disagrees with intuition becomes an item, ranked | The one work system: filed as a finding, which the store already ranks | Explaining a surprise away in a commit message | None new |
| A practitioner's cold read of knowledge pages, not only books and pages | The cold-eyes skill (`.claude/skills/cold-eyes-walk/`), pointed at a K8 page | Nothing | About one cold read a week, from the knowledge share |

**Prediction:** no more than 2 new tally rows in the four weeks to 22 Dec (W5).

## 7. The order after the reset, by share

**Correctness (42%).**
1. The won-switch BLOCKING finding: a won switch is never put on supply, so the switching
   guaranteed-standard payment has no account to credit. It is the draw's own pick.
2. The second BLOCKING item.
3. The remaining 32 supplier money findings, in batches of 20.

**Supplier features (18%).**
1. **s.12g, the thesis test,** is queued and starts unattended once the nightly census frees memory
   (bdf38eaba). It reads in about 34 h. Its grade is what this share is for.
2. B8's holdout, default-off.

**World features (15%).** The bill-shock world build as §5 orders it.

**Harness (15%).**
1. **The speed track** (§8), first step only.
2. The work system's next cut-over: map atoms, then continuations.
3. The §3 remedy.

**Knowledge (10%).**
1. Household time per problem type.
2. The second-view and mechanism line on the bill-shock page.
3. One practitioner cold read of a knowledge page.

## 8. The speed track (22 Nov steer): placement

He said "Yes, stage it", so it is implemented directly, in the harness share. **First, profile
before changing anything.** Three workloads, time and peak memory each: a standard book run, the
commit gate chain gate by gate, and the suite by file and fixture.

The advisor found no standing profile, and that is confirmed with one correction.
`docs/observability/commit_hook_step_timings.jsonl` exists, but it holds only two rows, from 17–18
Sep, and one of those is partial. So the series exists and is two months stale.

**Tools on this machine: py-spy and memray are not installed.** `cProfile` and `tracemalloc` are in
the standard library and need no install and no code change (`python3 -m cProfile`). Installing
py-spy needs no widening of the sandbox, but it is a new dependency. It is proposed only if
`cProfile`'s overhead distorts the book run.

**Memory is the constraint.** The book run cannot be profiled while s.12g holds 11.8 GB for about
34 h. So the gate chain and the suite go first, and the book run follows s.12g.

Each fix follows the steer's rules: a prediction first, identical results on recorded calls,
whole-workload timing interleaved, and a named switch. Gains are reported in his terms: accounts
and worlds per run, landings a day, and tests per change.

## 9. Open with the director

Two rows were answered today and are closed:
- `b8-s-retention-holdout-needs-two-practitioner`: yes.
- `practitioner-number-needed-how-long-is-a`: returned. It was re-researched and closed "not needed
  yet", with the condition that reopens it.

The weekly rhythm's baton has been on the 16 Nov `monday_ranking` step since then and was never
closed. This review is that step's output for the 23 Nov week, so the seat closes the baton when
the review lands.
