**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Capabilities: shorter, consistent with itself, and its gaps become a fix list (2026-10-24)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 24 Oct. He sent the live Capabilities page text:

- 07:25 BST: "This is what the capabilities tab says. Some good stuff but it's long, and flags errors that we should be fixing?"

**When:** before the Monday 26 Oct publish. Do the fixes in the priority order (P1, P7), and make the page change at the same publish.

---

## 1. The errors it flags: fix them, and work through them in this order

Some were fixed overnight. The page still shows the 19 Oct state.

- **Bills above the cap.** This was the biggest. `d909b693` took over-cap standard-variable bills from 5,488 of 18,398 down to 104 of 24,597. The EPG now reaches the household bill (`4ef70aba`), and the void-stub estimate carries the EPG (`ce35a25e`).
  - Close the remaining 104, or name why each one is legitimate.
  - The page's "Not yet" for the cap still reads "the cap's published levels are not yet ingested as a series". If that is still true, ingest Ofgem's published cap levels as a dated series, by fuel, payment method, region and meter type, from 2019. Make the cap bind from that series, so "The price cap as a real constraint" can read Live on evidence.
- **Gas does not follow a mover.** "Only the electricity supply follows the household; the gas supply ends at the move." The knowledge page landed on 22 Oct (`5f3b66db`). No build has followed it, and it breaks the 17 Oct ruling that households move as households. Build it next. Explore's empty "mover" slot is waiting on it.
- **Debt realism.** These three are world-fidelity items, each to start with K8:
  - "Write-offs per pound billed are well below a large supplier's";
  - "the world generates no prepayment debt";
  - "payment-failure rates are not yet sourced".
- **Settlement true-ups are inconsistent.** The world lists "The industry's own settlement timetable" as Live, while the supplier lists "Settlement true-ups on the real timetable" as Planned. Say which is true. If the supplier really takes no financial consequence at each reconciliation run, that is a supplier gap to schedule.

## 2. Five "Live" functions carry no evidence: give each one its evidence, or change its state

Each of these reads "Nothing published yet shows how this is checked":
- Business customers that fail like businesses;
- Three clocks kept straight;
- Telling can't-pay from won't-pay;
- Noticing a customer who has stopped heating their home;
- Its own regulatory obligations, tracked.

A function with no check behind it is not Live (C1, H1). For each one, either link the test or control that proves it, or let the state rule read Building. Then fix the rule, so a function with no evidence can never compute as Live.

Also, industrial and commercial supply is suspended (24 Aug). If "Business customers" stays on the page, mark it as built but not served. Don't show it as a live headline feature.

## 3. The doorways table: "Specification: not read" for sources the run already uses

Elexon/BMRS and the NESO Carbon Intensity API are read by the run every day, yet the table says their specifications are "not read". Either record that the specification was read, with its version, or say what "read" means in this column. Fix the same for the Ofgem cost-stack files.

## 4. Make it shorter: one screen of headline, the rest one click down

- Keep, in this order: In brief; the two-column grid; "Against a real GB supplier"; "The path to a real supplier".
- **Grid rows become one line each:** function name, state and evidence badge, such as "28 tests · proven to fail". The paragraph opens on tap. The test-count sentences move into the badge.
- **The "What a supplier can do with this world" register** is about 20 items and 2,000 words. Move it below the fold as one collapsed section, retitled something like "What this world is for: 21 things a supplier could test here". Keep its three headline counts visible: testable today, waiting on truth, nothing working on it.
- **Put a dated "Fixed this week" strip under In brief.** The over-cap fix is the headline. It turns the gaps into visible progress, and it is generated from the record.
- Show the page's generation stamp in the footer line, not under In brief. Regenerate it at every publish. Today it still reads 19 Oct.

## Checks

- **A cold read of the new page,** by one energy reader and one tech reader.
- **A consistency check that goes red** when a function computes as Live with no linked evidence, or when the world and the supplier state the same capability differently.

## Report

One stretch-log entry with:
- each item in §1, with its status or fix;
- the five evidence resolutions;
- the doorways fix;
- the page before and after, by word count and above the fold.

— Director steer, 24 Oct 2026, his words above; the review of the page text and the drafting are the advisor's.
