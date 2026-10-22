**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The front door says "PUBLISHING IS FAILING", from a heartbeat frozen before Monday's good publish (2026-10-22)

**Type:** STEER, through the advisor channel. The director's words, from chat on Thu 22 Oct:

- 14:52 BST: "I'm keen the website gets updated this week."
- 14:54 BST: he sent the home page text exactly as a reader sees it. Its first lines are:

> Verified 2026-10-19T08:55:40Z · showing run run_output_8b6fea024_20261019T033010Z.json
> PUBLISHING IS FAILING — the last 2 attempts to publish all failed, over 80.0h. Nothing above this line will be replaced until that is fixed, whatever the as-at date says. The publisher names no live cause for it.

**When:** now. A false alarm in bold, in the first line a newcomer reads, is breakage on a live surface (P7). It undoes this morning's front-door work.

## What the advisor found (origin/main, 22 Oct)

- **The record is a frozen snapshot.** `site/data/tick_heartbeat.json` was last committed at the Monday publish (`2a195224`, Mon 10:15). Its `ts_iso` is `2026-10-19T07:56:04Z`, and it records `content_publish.publisher.state: "failing"`, `consecutive_failures: 2`, `failing_for_seconds: 8819`, `cited_red_at_head: "dead"`.
- **The failure was cleared within hours, but the record wasn't.** Monday's publish succeeded about two hours after that snapshot: "Verified 2026-10-19T08:55:40Z", run `8b6fea024`. The heartbeat on the site was never refreshed. Live runtime state moved to the ops repository (P13), so the site's copy froze at its failing value.
- **The banner then ages a stale failure.** It reads the snapshot and adds the time since, so "over 80.0h" grows every hour until the next publish. It is false on its own terms: the publisher did not fail for 80 hours.

## WORK THIS CREATES

1. **Stop the false claim today.** The banner must state what is true: published 19 Oct, next publish Monday. It may only say "failing" from a record that is current. Where its source is older than one publish cadence, the banner either says it cannot tell or stays silent on failure. It never extrapolates. Deploy it this afternoon, so the director sees it fixed this week.
2. **Fix the class (P13).** A copy of runtime state on the site went stale and was read as live. Find every site element that reads a field from `tick_heartbeat.json` or any other snapshotted runtime file. For each one, either feed it fresh from its true home on each publish or deploy, or make it refuse to claim. Add a check that a freshness or failure claim on any served page carries the age of its own source, and refuses past a bound. Mutation-prove it.
3. **Answer what actually failed on Monday.** The record cites a red that is "dead" at HEAD, with no held refusal reason. Say what the two failed attempts were. Today's three failed Cloudflare deploys (`420a5b67d`, `989ce4f1c`, `02659d155`) were already raised in this morning's reading file. Report both in the same entry.
4. **Two defects in the copy the director was shown.**
   - **A garbled sentence**, under "If you work in energy → Settlement": "so it charges a supplier for timing that one of the period was not charged for". Rewrite it plainly. Today's PC2 and half-hourly probe (`21741d14`) gives the measured value, so state it.
   - **A fidelity gap, presented honestly.** Under Home moves and Dual fuel: "only the electricity supply follows the household; the gas supply ends at the move", so "a dual-fuel household that moves leaves as an electricity-only one". The page is right to say so. It is still a world defect against the 17 Oct ruling, that households move as households. Draw it as world work, with K8 first: how the gas registration follows a mover, the deemed contract at the new address, and the incoming occupant. Then correct the line on the page when it is fixed.
5. **Toolchain, noted in passing.** The same heartbeat reports that the builder's Claude Code package is 21 releases behind (`2.1.282` against `2.1.303`). Update it as a routine maintenance step, if canon permits it without the director. If it does not, raise it as a recommendation under G9.

## Report

One stretch-log entry: the banner before and after, the class sweep with counts, the cause of Monday's two failures and today's three, the copy fixes, and the mover work drawn.

— Director steer, 22 Oct 2026, from his words and the page text he sent; the diagnosis and drafting are the advisor's.

## Done

*Closed 2026-10-22 by the worker on claim `the-front-door-banner-remainder-sweep-harness-status-and-deploy-window`.
Earlier landings by the seat: e825e8099 (banner off the front door), 8bf9103a1 and 383adfab9
(publisher reads `held`, and the episode closes on a landed publish), f714a0097 (`renderReserved`),
and ed0717246 (the Settlement sentence).*

1. **Stop the false claim.** Done before this turn. The front door has no banner. Its clock is a line
   written at publish.
2. **The class (P13).** Served pages read runtime state from **5 feed/reader pairs**, plus one runtime
   block inside a publish artefact (`proof.json` → `deployment`). Each one now either states its
   source's age and refuses past a bound, or is fed fresh:
   - `freshness-banner.js` ← `tick_heartbeat`: "PUBLISHING IS FAILING" now carries "(recorded Nh
     ago)". It is not said at all once the record is older than the feed's own declared bound, or
     when either number is missing.
   - `freshness-banner.js` ← `publish_provenance`: the Verified line names its own `verified_at`.
     The frozen-feed check ages it on the reader's clock.
   - `harness` ← `director_reserved`: "Right now" plus the counted-on day, refused past 8 days (f714a0097).
   - `harness` ← `director_delta`: "Nothing has moved" plus the counted-on day, refused past 8 days.
   - `harness` ← `proof.deployment`: "observed daemons are running current code" plus the measured-on
     day. Past 8 days it reads "were running … too old to say what is running now".
   - `harness` ← `delivery`: fed fresh, because the delivery seat commits it at each landing.
   Control: `site/test_a_runtime_claim_carries_its_sources_age_and_refuses_past_its_bound.py`. It
   prints the census and reds on an unclassified reader. One assertion covers both legs of all four
   claims. Four mutations were run, and each one reds (refusal deleted; refusal unconditional;
   deployment forced fresh; delta forced stale).
3. **Publisher state on How it's built.** The harness page already carries the freshness layer, which
   states the publisher's state (`held`, or a current failure), so no second composer was added. It
   now obeys the same age bound as everything else.
4. **Monday's failures and the red deploys.** Answered in
   `SEAT_FINDING_THE_FAILING_LINE_WAS_A_LANDED_PUBLISH_…`. **A red deploy now reaches the seat's
   brief.** `delivery_seat.red_deploys_since` lists each red Cloudflare run in the stretch with the
   check's own refusal line, and it makes the stretch material. Read live, it returned run
   39811209357's "STALE" line.
5. **'/' stale on the runner's edge: the cause is not yet known, and here is the measurement.**
   `/index.html` is not a second route: it answers 308 to `/` (measured today), so fetching it beside
   `/` cannot tell the two apart. Run 39823685970 (ed0717246, 17:33Z) went STALE on `/` again. At
   about 18:00Z, from here, both `poesys.net/` and that deployment's own `3d868382.poesys-net.pages.dev/`
   served ed0717246's bytes. The check now names what a STALE or UNCONFIRMED route served: which of
   the path's last 30 commits it matches, or none (a page we never published), plus the edge's status,
   `cf-ray` colo, `cf-cache-status`, `age` and `<title>`. **The next red run's log settles the
   question.** An older commit's bytes plus a US colo would mean a per-edge cached path resolution. A
   match against none would mean an error or challenge page served to the runner, which is not a
   reader incident.
6. **Copy.** The Settlement sentence was rewritten in ed0717246 with 21741d145's measured figure.
   **Handed on, not done here:** the dual-fuel mover drawn as world work (K8 first), and item 5, the
   builder's Claude Code package. Both are in seat continuation
   `the-dual-fuel-mover-k8-and-the-builders-toolchain`.
