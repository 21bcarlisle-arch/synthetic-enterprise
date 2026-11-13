**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The site must say plainly whether per-customer value works, and the value test redesign is next week's first feature

**Type:** STEER, through the advisor channel. The director's words, from chat, Fri 13 Nov 06:11 GMT, after reading the live Capabilities page (generated 2026-11-11T20:09:07Z at 40a48b5d8):

- "Has the website updated? I don't get the numbers and explanation as to whether bespoke value optimisation works."

## What he read, and why it fails him

1. **The headline question is still answered from the run of 8 Oct.** The page updated on 11 Nov, but its opening paragraph and the value test still quote the 8 Oct run. That run's verdict is withheld because it is on older code. The thesis question is five weeks stale on a page published two days ago.
2. **The opening paragraph cannot be read.** It reads "+£4,722 to +£7,846 across its 3 re-draws, and +£11,345 in this run's own draw, above every one of them". The second number is then said to be "−£6,101 in this run's own draw, below every one of them; so even its sign is not settled". That is the appendix, not a headline. A reader with twenty years in GB retail energy could not tell from it whether the idea works.
3. **"Fixed in the 7 days to 11 Nov 2026: Nothing recorded."** That is false. The week fixed dozens of money classes, among them the close-refund, the level-DD cure, the Bacs-day DD and the repayment dating. Either the reader is broken, or it reads a source that the week did not write to. Find out which, and fix the class.

## What is asked

1. **Now, as a correctness fix** (plain-error fixing, no ruling needed):
   - Rewrite the top of Capabilities so a reader gets the answer in three sentences: what was tested, what it found, and what we can and cannot conclude yet. Give the run date beside it.
   - The honest answer today is something like: "On the 8 Oct run, per-customer pricing earned more than flat rules every time. We cannot yet say whether that came from better choices or from charging more, because the test that separates them is inconclusive, so no verdict is given. A redesigned test is next." Put it in your own words, and keep it true to the record.
   - Move the re-draw ranges to the appendix.
   - Fix "Nothing recorded".
2. **The value test redesign is the first item of next week's feature third.** He approved it on 2 Nov ("Yes to the value test"). It is the thesis, the reason the project exists, and it has waited behind correctness for eleven days. Now that a book passes the gate, it has the base it was waiting for. Put it at the top of the proposal in Sunday's weekly balance review, with the predictions to file before the run. The redesign's own list covers the rest:
   - one world, one tree, one book;
   - an arm for standard-variable households;
   - a baseline at the efficient-supplier margin;
   - the write-off rule settled against the 7 Nov debt evidence;
   - scoring on money, time and carbon apart.
3. **Done means** the page states a verdict, or "we cannot tell yet, because X", from a run no older than the page itself.

## Addendum, Fri 13 Nov 06:13 GMT: state it per household per year, and lead with the belief's skill

The director's words: "£5k to £8k means nothing to me. Is this per customer or on a random size sample?"

The advisor answered him from `docs/observability/value_cycle_ab_s1_three_arm_20261008r.json`:

- The figures are **book totals**: about 120 households, 2016-2025, about 270 renewal decisions.
- **+£5,244 is about 2.2% of net margin**, roughly £45 per household over the run, or about **£5 per household per year**. The selection figure (+£11,345) is about £10 per household per year. Both are derived from the counts, since the artefact does not state them.
- He was also told what the artefact itself says matters more:
  - The control's margin is £2/MWh, far under the regulated allowance.
  - The belief expected 65% retention against 90% realised.
  - Graded against outcomes it did not cause, its AUC is **0.52**. The artefact reads that as "the thesis failing however the P&L reads".

What is asked, adding to the steer above:

1. **Every value-test figure on the site is stated per household per year first**, with the book size and the years beside it. The book total goes second, if at all.
2. **The belief's skill leads with the margin, not after it.** That means AUC against control outcomes, and calibration. A margin gain from a belief that cannot tell who leaves is not evidence for the thesis, and the page must say so in plain words.
3. **The redesign sizes its book from the floor decomposition**, so a per-household effect of the size it predicts can be told from noise. State that size and its cost in tokens in Sunday's proposal.

## Progress, 13 Nov (delivery seat). This file stays open until "done means" holds.

- **Item 1, the lead.** The lead is rewritten in `tools/capabilities_page_figures.render_lead`. It
  is three plain sentences with the run date, and no pound figure. The verdict is withheld in
  plain words, and the re-draw ranges stay in the value test's appendix. The lead still describes
  the 8 Oct run, because no newer run exists. The 12-draw family (77bf74f880) reads on 14 Nov.
- **Item 1, "Nothing recorded".** Both causes were real. The reader is sound. The source is a
  hand-written record (`docs/design/capabilities_fixed_this_week.json`) that nobody wrote to in
  the week. The instance is fixed: three of the week's money fixes were added. The class is
  closed: `generate_capabilities_door.fixed_this_week` now counts the window's commits to
  `company/`, `saas/`, `simulation/` and `sim/` from git. When the record is empty over a busy
  week, the strip says so ("N commits ... none was written to this list") rather than "Nothing
  recorded".
- **Item 2, and addendum 3.** Done in 16d90c311f: the redesign is sized from the household noise
  split, and the 16 Nov review opens with it.
- **Still open: addendum items 1 and 2.** Every value-test figure should be per household per
  year, with the belief's skill first. The feed does not carry household-years or the redesign's
  clustered AUC (0.52), so the page cannot compute them yet. Typing them in is the defect the
  26 Oct steer forbade. Handed on as `value-test-figures-per-household-year-from-the-feed`.

## Archived, 13 Nov 15:45Z (delivery seat)

The advisor channel refused this file because f4f825b8b (the seat's progress note above) is unsigned.
The signed text is bd9875ade's, and the diff between them is that progress section and nothing else.
The ruling itself is unchanged. It was read from bd9875ade's bytes and acted on as the director's.

- Item 1 (lead, appendix ranges, "Nothing recorded"): landed in f4f825b8b.
- Item 2 and addendum 3 (redesign first, sized from the household noise split): landed in 16d90c311f.
- Still open, and each is carried by a live continuation, so this file no longer has to hold it:
  - Addendum items 1 and 2 (per household per year first; the belief's skill leads):
    `value-test-figures-per-household-year-from-the-feed`.
  - "Done means" (a verdict, or "cannot tell yet, because X", from a run no older than the page):
    `value-test-step-1-grade-the-twelve-draw-family-once-it-exits`. That step waits for
    `longjob-value-test-12-draw-family-pairs`, which was still active at 15:44Z. It reads on 14 Nov.
