# Research Methodology — How We Learn Efficiently

## What works (validated June 2026)

### 1. Parallel agents, always

**Pattern:** Launch 3–5 research agents simultaneously on non-overlapping sub-topics.  
**Why it works:** Each agent is independent — no context bleed, no hallucination anchoring. 4 agents in parallel = 4× the discovery in the same wall-clock time.  
**Rule of thumb:** If a research question has 3+ distinct sub-topics, split them. Don't give one agent a 10-question brief; give 3 agents a 3-question brief each.

### 2. Structured numbered questions, not open-ended briefs

**Works:**
> "1. What fields does the EPC bulk CSV contain? List exact column names.
> 2. What is the total record count and date range?
> 3. How do you download it — URL, auth method, file size?"

**Doesn't work:**
> "Tell me about EPC data."

**Why:** Agents fill vague briefs with generic summaries. Numbered questions force specificity and make gaps obvious (unanswered question = known unknown).

### 3. Name specific sources upfront

Tell the agent *where* to look, not just *what* to find. This anchors the search and prevents wasted time on low-quality sources.

**Works:** "Search for the DESNZ NEED 2026 report, Ofgem TDCV consultation, and Elexon BSC documentation."  
**Doesn't work:** "Search for UK energy consumption data."

Good anchor sources by domain (see `source_guide.md` for full list):
- UK energy consumption: DESNZ NEED report (annual), Ofgem TDCV review
- Regulation: ofgem.gov.uk, bscdocs.elexon.co.uk
- Company finances: Companies House, Watt-Logic analysis, Octopus/OVO investor pages
- EPC data: get-energy-performance-data.communities.gov.uk

### 4. Demand numbers, not principles

Every brief should contain: **"I want specific numbers, not generic principles."**

Without this instruction, agents produce framework-level descriptions. With it, they hunt for actual figures: £64.73/ROC, 0.491 ROCs/MWh, 2,500 kWh/yr median, £97/customer/yr opex allowance.

**Add to every brief:** "Report in ~[N] words with specific numbers and sources."

### 5. Write a synthesis document immediately

Raw research documents expire — findings become stale, the connections between them get lost. Within the same session:
1. Write the raw finding to `docs/market_research/<topic>.md`
2. Write the synthesis to `docs/market_research/rd_synthesis_<date>.md` capturing: what the finding means for the simulation, what the priority action is, what's still unknown

The synthesis is what gets actioned. Without it, research becomes a filing exercise.

### 6. Calibration caveats are high-value findings

The most useful research outputs are often **corrections to naive assumptions** — not the headline number, but the footnote that changes how you use it.

Examples from June 2026:
- EPC `ENERGY_CONSUMPTION_CURRENT` overpredicts metered consumption by 50–100% → apply 0.65 correction factor
- OVO's "29% net margin" (2021) is derivative MTM, not trading profit → use "underlying EBIT" metric, not statutory
- Ofgem's £2.57bn sector EBIT in 2023 includes back-dated crisis cost recovery → not normalised profit

When reviewing agent output, actively look for these caveats. They're often buried in footnotes.

### 7. Capture methodology insights immediately

If an agent returns particularly good output, note *why* — was it the source anchoring? The numbered questions? The specificity demand? Add the insight to this file before the session ends.

---

## What doesn't work

**Single agent, broad topic:** Produces a generic survey. Not actionable.  
**Open-ended brief:** "Research the UK energy market" → 500 words of Wikipedia-level overview.  
**No synthesis:** Raw research docs pile up without connecting to action.  
**Sequential agents:** Waiting for one to complete before starting the next wastes time. Always parallel unless topics are genuinely dependent.  
**Not naming sources:** Agents default to whatever Google surfaces first, which tends to be SEO-optimised content rather than primary sources.

---

## Recommended briefing template

```
Research [SPECIFIC TOPIC] for a UK energy supplier simulation. I want to understand:

1. [Specific question — the most important one first]
2. [Specific question]
3. [Specific question]
4. [Specific question]
5. [Specific question]

Look for [SPECIFIC SOURCE 1], [SPECIFIC SOURCE 2], and [SPECIFIC SOURCE 3].
Report in ~[N] words with specific numbers and sources — not generic principles.
```

---

## Session record

| Date | Topic(s) | Agents | Key output | Methodology notes |
|------|----------|--------|------------|-------------------|
| 2026-06-21 | EPC, ONS consumption, Ofgem regulation, supplier financials | 4 parallel | `docs/market_research/` (4 files + synthesis) | First R&D session; parallel agent pattern validated |
| 2026-06-21 | Commercial strategy, debt mgmt, treasury/risk, customer comms | 4 parallel | `docs/market_research/` (pending) | Company behaviour focus; same pattern |

---

## Going deeper on a known topic

When returning to a topic already researched, the next pass should:
1. Start from the existing `knowledge_map.md` row — read what we already know and the listed gaps
2. Brief the agent specifically on the **gaps**, not the whole topic (no re-deriving what's already known)
3. Ask the agent to **confirm or update** specific figures from the previous pass — not just add new ones
4. Update the knowledge map confidence level if new data changes the picture

This is how the knowledge compounds rather than accumulates.
