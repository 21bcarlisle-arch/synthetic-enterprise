**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The site must be current, and the value test must be redesigned so it can return an answer (2026-11-02)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Mon 2 Nov.

- 07:27 GMT, after reading the live Capabilities page: "Reading the capabilities tab I see issues, are these the ones you mentioned?"
- 07:29 GMT, on the advisor's proposal: "Yes. And please make sure the website is up to date"

## Part 1: the site is current. BLOCKING: this comes first

The live site still shows **"Generated 2026-10-26 … at commit 185355386"** and **"Fixed in the 7 days to 26 Oct"**. Publishing has refused every newer run for about 162 hours. This morning's book was refused with: **"carved GBP 197,965.24 != booked GBP 193,406.52"**. Your direction says twelve page fixes are made and graded but not live. The safety catch is right, and no unverified figure may go live. But the director's ask is that the site be **current**.

1. **Fix the refusal before anything else.** Find out why this morning's book fails the over-ceiling reconciliation, a £4,558.72 gap between carved and booked. Treat it as a defect. Do not just re-run and hope. Check whether today's pre-registered fresh run at 85b044be54 addresses that cause. If it does not, fix the cause first. Then publish the first book that passes.
2. **Separate the pages from the run, if publish decoupling allows it.** The publish-decoupling ruling of 10 Aug keeps the last verified *run*. It does not require the *pages* to stay at a 26 Oct commit. If the publisher can rebuild the pages from current code against the last verified run (4ae8da9b0f), do that now. The twelve graded page fixes, the privacy notice and the copy fixes then go live today without any unverified figure. If it cannot, say why in Done, and give the earliest time a verified run will publish.
3. **Tell the director in plain words.** The paused banner should give the reason a reader can understand: "This week's run failed a billing reconciliation check, so the site shows last week's verified figures while it is fixed." Do not print the internal string.

## Part 2: the value test must be able to return an answer (after the correctness exit test, except item 6)

The director read the Capabilities value test. The advisor's read, for you to test:

1. **It cannot answer the thesis on the current design.**
   - The published whole advantage (£5,244) sits **below all three of its own re-draws** (£9,375–£11,766).
   - The price-level leg **changes sign** between draws.
   - **0 of 5 families state a sign for the choosing.**
2. **It reaches almost none of the book.**
   - It priced 104 of 2,824 renewals (3.7%) on a 154-account book.
   - 2,490 of the unpriced renewals are SVT customers with no renewal to price.
   - As built, per-customer pricing touches only households already on a fixed deal. The rest is an acquisition and tariff-choice question that no arm asks.
3. **One household and one world rule move it.**
   - PROS-2016-0098 moves the published figure by about £5,300.
   - Part of that comes from the world writing off *every* failed bill in full for *any* customer who ever leaves. The page itself calls this an open fidelity question.
4. **Figures and their bounds come from different code and different books.**
   - The run and the page differ on 180 code paths.
   - The floors were measured on 164 settled accounts, the figure on 154.
   - The control arm is pinned to a run of 9 Sep.
5. **The baseline proves little.** It is a £2/MWh flat margin, far below what an efficient supplier earns. The page says so itself.

**Ask: own the redesign.** These are prompts; you decide.
- **One world, one code tree, one book, one date** for every arm and every bound.
- **A book large enough to price.**
- **Arms that reach the whole book**, including an arm that places SVT households onto a tariff (tariff choice), so the thesis is tested where most of the book actually is.
- **A realistic baseline**: a flat margin at the level an efficient supplier earns, or the price-cap headroom.
- **Settle the write-off rule against GB evidence** before the next value run. Use bad-debt provisioning, debt sale and recovery rates, and the Knowledge pages.
- **Score it on the vector scorecard the director ruled on 31 Oct:** customer money, time and carbon; company outcomes; and fairness.
- **Pre-register the predictions.**

Write `docs/design/THE_VALUE_TEST_REDESIGN.md` now, as cheap thinking work. Bring a two-minute proposal to the director. Build after the correctness exit test.

6. **The Capabilities page itself. This item is cheap and comes now.**
   - **Blank insertions are visible.** For example: "produced at ,", "the run executed  and this page", "Source:  Open question: ", "measured on ." Find the empty fields and fix the renderer. Add a test that no published page contains a field rendered empty.
   - **The carbon contradiction.** This page says carbon is "designed, never measured". The home page lists "Household carbon, per half hour" as a capability. Make them agree with the record.
   - **Readability.** Keep the honesty but move it. The public page should give the question, what the current test can and cannot say and why, and what the redesign will do, in plain words. Put the full statistical apparatus (floors, seeds, withdrawals, R12 notes) in a linked technical appendix, unchanged. An outside reader should finish the section knowing that the answer is not in yet, and why.

## Done (part 1, so far; the file stays here until part 2 is met)

*Worker tick, 2 Nov 10:30Z.*

- **Item 1, the refusal.** The £4,558.72 gap was the grader, not the book. It compared the ledger's EPG share on settled kWh with the discount on billed kWh, and it is fixed with a test (6062596dc). The bb58608b9 book was then offered again and refused twice more for other reasons:
  - **A site census counted prose as a page reading a feed.** The regenerated "How it's built" timeline cites `site/data/tick_heartbeat.json`, which the page never fetches. This is fixed in this tick's census commit: a feed now counts only as a quoted URL, with a two-leg control and mutations run.
  - **The domain-invariant gate.** That book's saved JSON has no SLC 22C renewal-notice log, so every renewal reads as breached (1,171; 3cb000dc3 fixed the cause for later runs). It also has 9 breaches on profile-class-2 homes. **bb58608b9 cannot publish.**
- **Earliest verified publish.** This is the fresh run at 85b044be54, which carries the PC2 and gas fixes. It finished at 10:12Z today and its grade chain is running. Its raw result is kept whole, so the renewal-notice row can be graded on it. If the grade is clean, it goes to the publisher today. If a row still breaches, the grade names it, and the next sim_runner run at or after 3cb000dc3 is the earliest.
- **Item 3, the paused banner.** It now leads with a sentence a reader can follow: "The latest run did not pass its correctness checks, so this site shows the last verified figures while it is fixed." The pause facts the ruling requires follow that sentence, and no internal refusal string is printed. The wording says "correctness checks" rather than "billing reconciliation" because the reconciliation is no longer the cause. It reaches the live site with the next publish.
- **Item 2, decoupling the pages from the run.** Not attempted this tick. It belongs to the delivery seat's `the-site-is-current` focus.

*Delivery seat, 2 Nov 11:50Z.* This note supersedes the worker tick's line on the earliest publish.

- **Correction to the premise the seat's own direction carried.** The direction said bb58608b9 "passed every publish gate at 08:46Z and failed only on 'cannot lock ref HEAD'". That was wrong. At 08:36Z the book was `REFUSED (bills)` on the over-ceiling grade. The ref-lock failure at 08:46Z was the **paused-banner** commit, which lost a race to another lane after its hook chain passed. Since the grader fix, the book has been offered at 09:44Z, 10:33Z, 11:04Z and 11:14Z, and the **domain-invariant gate** refused it every time: INV_RENEWAL_NOTICE_42_TO_49_DAYS 1,171, INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS 3, and E7 two-register, read-monotonic and TOU-bands at 2 each. **bb58608b9 cannot publish.** The marker is still in the staging root and is re-processed every cycle, which wastes the cycles but does no harm.
- **The fresh 85b044be54 book is graded, and it is refused too** (`/var/tmp/fresh-grade-85b044be54/grade.txt`, 10:15Z). The renewal-notice row is fixed: 0 of 1,171. Four billing rows still breach, 9 households in all, and no exception covers them:
  - INV_E7_METER_BILLED_ON_TWO_REGISTERS 2
  - INV_READ_MONOTONIC 2
  - INV_TOU_BANDS_SUM_TO_THE_TOTAL 2
  - INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS 3

  These are the profile-class-2 rows in `SEAT_FINDING_THE_E7_AND_PC2_BUILDS_LEAVE_EIGHT_ROWS_BREACHED_ON_PROFILE_CLASS_2_HOMES_2026-10-30.md`. They are owned by the `the-fresh-run-after-the-pc2-and-gas-fixes` focus item.
- **Earliest verified publish: not today.** It will be the first sim_runner run at or after the commit that fixes those four rows. A run takes about 95 minutes on top of the 78-minute pause between runs, so once that fix lands, publishing is about 3 hours behind it. No fix for the four rows is on origin yet.
- **The ref race, fixed as a class.** A banner commit whose chain passed and then hit git's `cannot lock ref` is now re-landed on the new HEAD through `surgical_land.land`. That is the same clean-extract route the content publish already used, with the same race retries. If every attempt is lost, the cause is recorded as the new `lost_commit_race`, a cause on which no test was judged. A red gate on the new tree is still recorded as `gate_refusal`. Control: `tests/background/test_a_banner_commit_that_loses_the_ref_race_is_relanded.py`, which drives git's real 08:46Z text. Three mutants were run, and each one fired.
- **Item 3, the banner wording.** It stays as the worker tick wrote it: "The latest run did not pass its correctness checks…". The sentence is one constant, and it is shown for every pause. "A billing reconciliation check" would become false the first time a different gate refuses. Today's cause is billing rows, so the director's example was right for today, and the generic sentence is true for today as well.
- **Item 2, rebuilding the pages from current code against 4ae8da9b0f.** Not done. No door for it exists yet: every page generator reads the run it is publishing, and nothing re-derives pages from an older verified run under current code. This is handed on as the next piece of `the-site-is-current`.

## Done (moved to done/ by the worker tick, 2 Nov, on the advisor channel's instruction)

**Why it moved.** The channel refused this file as unsigned. Its staging commit 2e50f42c3 verifies against
the advisor's key. Only the later in-file notes (a1bead7ab, 1d623ccad) are unsigned. The ruling was read in
2e50f42c3's bytes and acted on as signed. The channel's instruction was to move it here with the reason once
seen. **Nothing it asks is dropped:**
- **Part 1, the site is current.** The last code blocker on the publish is the E7 catch-up split. That
  covers the 3 of 9 rows on 85b044be54 that 1b709ac0e9 did not fix. It was fixed this tick, in the commit
  that lands `tests/tools/test_an_economy_7_catch_up_closes_each_register_on_its_own_read.py`.
  - The earliest verified publish is the first sim_runner run at or after that commit. That is about three
    hours behind it.
  - The rest of the publish is carried by focus item `the-last-pc2-catch-up-defect-then-the-publish`,
    steps (2) to (5).
  - Item 2, rebuilding the pages against the last verified run, is queued as
    `the-pages-rebuilt-against-the-last-verified-run`.
- **Part 2, the value test, and item 6, the Capabilities page.** These are carried whole by focus item
  `the-capabilities-page-and-the-value-test-redesign` in `docs/direction/DIRECTION.yaml`.
  `docs/design/THE_VALUE_TEST_REDESIGN.md` is not yet written.
