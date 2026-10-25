# A cold read of the switching and payments pages finds a five-day clock read from sign-up and an "absolute" DD-amount rule the page itself hedges

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `the-switching-page-says-the-company-decides-the-objection`)

*Delivery seat, 2026-10-25. Asked by the 21:22Z direction after EP12's landing.*

## Premise, re-measured

The ask was to correct `site/knowledge/switching-mechanics/` and
`docs/market_research/switching_mechanics_2026-10-25.md` where they said the world draws the
objection or that `company/market/transfer_objection_register.py` is uncalled. **Most of that was already
done.** EP12's own landing, `43ef01107`, amended section 0 of the note and the page's
`knowledge_topics.json` record. Both now say the company decides from its own ledger, and they keep the
0.283 draw only as history. The one stale sentence left was the Knowledge index card's "why" line,
"The world blocks an indebted household's switch" (`site/data/knowledge_wholesale.json` and
`site/knowledge/index.html`). This landing corrects it. Its wording also takes account of findings
3 and 4 below: the card no longer calls the £200 de-minimis "a rule this page sets out", and no
longer says no switch fails, now that an objection cancels one.

## The cold read

The protocol is `.claude/skills/cold-eyes-walk/SKILL.md`. The reviewer was a fresh agent that read
only the two page shells and their JSON records, with no code and no notes. The persona was a
payments and switching operations director. The reviewer set its priors before reading.
`independence: false`: it is the same model family as the author. The reviewer filed 22 findings.
The ones a cold reader actually gets wrong come first; each line keeps its number from the review.

**Switching page**
1. **High, misleading framing.** "Completes within five working days" reads as five days from sign-up.
   The 14-day cooling-off runs first, and the CSS clock starts at the relevant date. The pre-CSS
   "15-16 days on average" does not say whether it includes cooling-off, so the before/after
   comparison may not be like for like.
2. **Medium, internal.** The subtitle and headline say "an objection only for debt". The body lists
   three grounds, and the theory section lists four (adding linked meter points).
3. **Medium, internal.** "The world cancels only the switches it objected to" sits beside "No switch
   ever fails". An objected switch is a failed switch. The page also never says that an objection can
   be withdrawn when the customer pays, which is the common outcome in practice.
4. **Medium.** "Above £200 per fuel" reads as regulation. It is the top of the published informal
   de-minimis range, chosen by design (the note's section 0 says so), but the published record does
   not say it.
5. **Low-medium, practice.** "Never to a prepayment debt under £500" misreads the Debt Assignment
   Protocol: the losing supplier still objects, and the debt moves with the customer. *Needs a
   practitioner or a DAP read before changing; filed, not edited.*
6. **High, across pages.** The switching page has the company treating prepayment debt differently.
   The payments page says the world draws direct debit and puts every other household in one class,
   "other". The two cannot both describe the same book. The likely reading is that the switching rule
   exists in code and is unreachable in the current world. If so, the page should say so.
7. **Medium.** Pre-CSS saves are blocked "before 18 July 2022", but the rule cited, SLC 22B, dates
   from April 2022. The page's own "about a week to object" also implies the losing supplier did have
   notice in time. Neither the cut date nor the pre-2022 block is explained on the surface.
8. **Low-medium.** The page mixes switches with switch attempts, and objected with blocked. The
   170k/430k counts name no fuel and no year.
20. **Medium.** The company rule is dated "since 25 October 2026", the day the page was written and
   marked "not run". A reader cannot tell whether any published book carries the new rule.
   **The answer today is none:** the last published run is 19 Oct. The page should say the rule
   reaches the book from the next run.

**Payments page**
10. **High, ambiguous.** "Moved by 3 to 4 percentage points over the five years to 2025" sits beside
   61-66% (2017-18) against 72-73% (2025), a move of 6-12 points. The two figures cover different
   windows, so this may not be an error, but a cold reader computes the gap and finds a contradiction.
   The window should be stated, or the claim reworded.
11. **High, internal.** The subtitle and headline call the amount rule "absolute since 2022, with no
   exception". The page's own theory carries a GAP saying the licence text still shows "all reasonable
   steps", and residual 2 asks for SLC 27.15's current wording. Note: `65906582e` (on origin) read
   SLC 27.15 as an absolute "must ensure" with "all reasonable steps" gone, so the GAP line may be
   the stale half. Either way the page currently contradicts itself.
12. **Medium.** For £57, £160 and £19 (the cap's debt-related costs), the page never states the
   basis (per fuel, per dual-fuel customer, or per account), and does not say why prepayment is the
   lowest.
13. **Medium.** In "£80 against £11", the £11 is undefined. "About £135 a year" does not reconcile
   with the £103 gap between £160 and £57.
14. **Medium.** In the Bacs timeline, it is unclear whether "about 1% on day 4" is a share of debits
   or of failures, beside "unpaid 2-3% of collections".
15. **Low-medium, practice.** The reason-code grouping puts ARUDD 4 (advance notice disputed, a payer
   dispute) and 5 (no account) under "supplier's or bank's error".
16. **Low.** The simulation uses gas DD 0.75 (DESNZ Mar 2026), while the plain text says 73%
   (Sep 2025). The vintage and the value both differ.

**Both pages (shared shell)**
18. **Medium.** The shell says "Figures from the run of 19 Oct 2026 … no figure here is typed by hand"
   and "deliberately carries no current cap level". Every figure on these pages is typed prose
   written on 25 Oct, and the payments page leads with 2025 cap allowances. The shell's boilerplate is
   false for this page kind.
19. **Medium.** The green "Reviewed 2026-10-25" badge is a same-day self-check by the author. It
   reads as an independent review.
21. **Low.** The sources are internal repo paths a public reader cannot open.

The rest of the review was low-severity (9, 17, 22), or confirmed the page within the reviewer's
priors: switching volumes, erroneous-transfer rate, £30 compensation, credit balances, the 2022 DD
rises.

## What should happen next

- Items 11, 18 and 6 are the ones a cold reader is most likely to repeat as fact. 11 is a factual
  correction that `65906582e`'s source read may already settle; 18 is the shared shell, so one fix
  covers every page of this kind.
- Items 5 and 15 are practice claims. Per K4, read the DAP and the Bacs ARUDD code list first, and
  ask the director only if the published sources leave them open.
- Item 1 is wording: give the five-day clock its start point.
