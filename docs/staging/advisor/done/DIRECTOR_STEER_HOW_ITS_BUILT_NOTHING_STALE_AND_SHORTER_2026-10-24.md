**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] How it's built: nothing stale, every register drawn from the record, and shorter (2026-10-24)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 24 Oct. He sent the live page text:

- 07:28 BST: "This is the how it's built tab. Some good stuff. But long and some credibility is undermined but things not have been updated since July, eg root causes"

**When:** before the Monday 26 Oct publish. This steer is the urgent first part of the still-undrawn `DIRECTOR_STEER_SHOW_EVERYTHING_WE_HAVE_LEARNED_FROM_THE_RECORD_NOT_FROM_MEMORY_2026-10-23.md`. Draw both together. Where they overlap, this one sets the deadline.

---

## What the advisor found stale or self-undermining on the live page (24 Oct)

1. **A warning at the top that cancels the page.** "figures DIFFER from the committed record — treat them as provisional". The stamp beside it reads "Generated 19 Oct 2026". Find why the figures differ and fix it. A newcomer must not meet this line as their second sentence.
2. **"What a human actually decided" gives the July list.** It reads "Seven kinds of action are the director's". Canon v4 G5 (ruled 12 Oct, decision 8) replaced "the July seven, the 29 July four and the five in code" with one list. It also says "When this was last counted, on 2026-09-18, nothing was waiting on him". Rows have waited since then, and they now carry recommendations under the 19 Oct steer. Quote G5. Generate the live count of what waits on him, with each recommendation, at publish.
3. **"What we got wrong, and corrected" stops in July** (COR-1 to COR-3, 5–23 Jul). Since then, real corrections have been made and published. For example:
   - the founder book was 1% dual fuel against a published 72% (17 Oct);
   - standard-variable bills sat above the cap and the EPG, falling from 5,488 to 104 (23–24 Oct);
   - the "publishing is failing" banner was read from a frozen snapshot (22 Oct);
   - the advisor queue was read from a checkout 37 commits behind origin (23 Oct).

   Generate this list from the record, newest first, as the 23 Oct learned-from-the-record steer asks.
4. **"The rules this project has had to mint" shows July rules only,** about retired machinery. Examples: "A directive arriving by NTFY …", although the NTFY responder was retired on 15 Oct, and the tmux send-keys watchdog. Show the rules that are live now, from canon v4 and the class register, newest first. Mark retired ones as retired, with what replaced them, or move them to an archive one click down.
5. **The learning layer says it has stopped learning.** It reads "0 new classes of mistake registered, of 6 in the register; last 28 Aug 2026". The work since August shows many recurring-class fixes, under P13. Either the register is not being used (`background/finding_classes.py`), which is a real defect, or the count reads the wrong place. Fix the cause, and backfill the classes that were found and fixed since 28 Aug.
6. **Two more stale figures:**
   - Checks that can fail: "35 controls … 33 proven" comes from a "hand-kept register … last graded 13 Jul 2026", next to "532 tests proven able to fail" counted live. Use one live figure. Retire or regrade the hand-kept register.
   - The published-state layer's "last 13 Oct 2026". Check whether it is still current.
7. **"Refusals are not logged, so they are not counted"** appears on three layers. This honesty is good, but repeated it reads as weakness. If logging refusals is cheap, log them, so the layers can say what they stopped. If not, say it once, in the stack's caption.
8. **Belief and truth uses internal IDs.** For example, "W1_5_premise_demand_shape is 3.9% past the line". Give each pair a plain name, such as "how a home's demand moves through the day". Keep the ID one tap down.

## Make it shorter

Above the fold, keep:
- In brief;
- the eight-layer stack, with each layer's evidence on one line;
- the scale figures;
- last week's work;
- belief and truth.

Then, collapsed, each starting with an "In brief":
- lessons learned, as cards, newest first, generated from the record;
- what we got wrong and corrected, newest first;
- the rules now live;
- what a human decides, with G5 and the live waiting count;
- how work is chosen;
- doors, pace and balance;
- checks that can fail.

The full historical tables, from July onward, go in an archive one click further down.

## Rule against recurrence

A dated section must not stop aging silently. If a generated section's newest entry is more than 30 days older than the publish, the section says so on the page. In addition, the Monday end-to-end step goes red until it is fixed or explained. The canon check also covers this page: no superseded line, such as the July seven or NTFY authority, may be presented as current.

## Report

One stretch-log entry with:
- each of the eight items above, before and after;
- the cause of the "DIFFER" warning;
- what was wrong with the class register;
- the page's word count above the fold, before and after;
- a cold read by one energy reader and one tech reader.

— Director steer, 24 Oct 2026, his words above; the page review and drafting are the advisor's.

## Done

*Seat executor, 24 Oct 2026. The report is the two stretch-log entries of 24 Oct in `docs/status/SEAT_STRETCH_LOG.md` ("How it's built stops calling its figures provisional…" and its continuation).*

- **Items 1-4, 6-8:** 05831e868. The DIFFER warning had two causes: the projections store was never rebuilt on the publish path, and six unmeasured pairs were graded as uncommitted figures. G5 is quoted from canon with the open `for_the_director` rows. Corrections and rules are read from the record. Each pair has a plain name.
- **Item 5:** 833ef83e8. The register was not wrong. The classes were being fixed in code and never registered. Three are now registered with their commits, so 9 in the register. Still open: nothing registers a class from a commit message.
- **Item 6, "last 13 Oct":** checked on the shared tree on 24 Oct. It is current. The figure dates the last publish-gate run that *stopped* a publish (2026-10-13 19:06Z). The latest run, on 19 Oct, passed. 28 of 81 runs stopped a publish in the window.
- **Shorter:** 833ef83e8. Five blocks above the fold, 1,970 words before and 1,936 after. The other sections are collapsed, each with an In brief, and the historical tables are in an archive.
- **Rule against recurrence:** 833ef83e8. `page_aging_problems` reds when the newest correction is more than 30 days old or when a superseded line is shown as current. The Monday step cannot close on it without `Page aging explained:`.
- **Cold reads:** one energy reader and one tech reader, both fresh instances, in 833ef83e8's log entry.
- **Not done here, carried by continuation `lessons-as-cause-principle-mechanism-evidence-chains`:** lessons generated as chains (at least 10, newest first). Also the cold reads' edits: cut "the book", "four sets of dice", "the galaxy" and "mutation", and fix the contradiction between "no record of what they refuse" and the per-layer Fired counts.
