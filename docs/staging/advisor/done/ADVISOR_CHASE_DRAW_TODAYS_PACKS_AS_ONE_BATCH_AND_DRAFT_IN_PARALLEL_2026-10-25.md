**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ADVISOR-CHASE] Take today's 30 advisor files as one batch, and draft the Knowledge pages in parallel (2026-10-25)

**Type:** CHASE, through the advisor channel. Director's words from chat, Sun 25 Oct:

- 07:05 GMT: "Ok. Is it getting on with the research?"

## The state on origin at 07:05

- You have drawn one of today's 31 advisor files, the forward-years ruling, at 06:27.
- Thirty are waiting:
  - 29 evidence packs and steers;
  - the 44% usage reading;
  - the site copy pack, which is **BLOCKING**.
- Taken one at a time, the queue would take days. The reading says this window has about 50 points left before Monday 03:00, and the serial door caps you at about 1 point an hour.

## What to do

1. **Land the site copy pack first.** It is blocking, and Monday's publish depends on it. Run it through the generators and data, cold-read the result, and record the cold read.
2. **Read every `DIRECTOR_EVIDENCE_*_2026-10-25.md` file at once, as one batch.** They are knowledge, not work orders, and they don't conflict. Give each one a Knowledge page, and draft those pages in **parallel forks**. Drafting doesn't need the serial door. Then land the drafts in a few batched commits through the gate. Register each page's concepts in the concept register, and record its headline bands as world claims or population checks. These are calibration only, never per-home targets.
3. **Rule the steers together and bring back one recommendation.** The steers are:
   - the advice roadmap;
   - asset demand derived per home;
   - comfort, health and carbon as outputs;
   - the asset design note;
   - the flex and network layering.

   They fit together as one plan:
   - basics, then forward years;
   - then the personalised asset world (L0), built in its generative form;
   - then the savings grader;
   - then advice products;
   - then the layers L1 and above, each with its trigger.

   Write the asset design note (`docs/design/PERSONALISED_ASSET_WORLD.md`) and put the order into `priority_order.yaml`.
4. **Close the readings and rulings.** These are the 44% reading and the OCF terms ruling. They need only recording.
5. If an item has to wait behind work already in flight, such as the C30 re-runs, say which one and why, as you did for Explore.

## Done

Seat-executor, 2026-10-25 ~11:55Z. Every numbered step is done or carried by its own file:

1. The site copy pack is not done whole. A2 and A3 have landed (d86d8749c, 2ada25833). The rest (A1, the rest of A2, A4-A6, section B and the single publish with its cold read) is listed in that file's own Progress section, and the file stays in the queue as BLOCKING. This chase does not hold it.
2. The evidence packs were taken as one batch: 21 published in 7fb1aabcc3, three in 2d33139a4b, and the earlier ones in 997cfc67e, 3660142eb and 25d95f3ab. Each pack moved to `done/`, 29 in all.
3. The steers were ruled together: `docs/design/PERSONALISED_ASSET_WORLD.md` and the order after the forward years in `docs/direction/priority_order.yaml` (970f388c3). The MVP-plus-layers recommendation is carried in `for_the_director`.
4. The 44% reading (b436ce80f) and the OCF terms ruling (310b9b74e) are recorded.
5. What still waits is named in the files that own it: forward-years volatility grading (EP16), the advice roadmap's four "now" defects, and the verification census.
