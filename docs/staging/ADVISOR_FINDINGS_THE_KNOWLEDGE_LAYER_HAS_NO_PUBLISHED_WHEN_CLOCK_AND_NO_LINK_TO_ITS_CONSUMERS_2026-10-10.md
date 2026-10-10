# [ADVISOR] The knowledge layer has no "published when" clock, and no link to the constants that use it

**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted` — header added by the scale lane: the file landed without one and the severity gate refused every lane's merge of origin

Date: 2026-10-10. Staged at the director's request, after reading an external open-source
project with him (see "Where this came from"). These are two problems with evidence, offered for the
seat to weigh, scope and sequence. The build, and whether there is one, is the seat's call. Nothing
here claims priority over drawn work.

Measured against origin at `c9a4edc4` (2026-10-10 09:17 +0100).

## Problem 1 — a sourced anchor does not say when a supplier could first have known it

The wall says the company may know only what a real supplier could know **at the time**. For market
data the code enforces that by construction (`company/interfaces/point_in_time_view.py`). For the
published price cap, `company/pricing/ofgem_price_cap.py` reads windows from the published artefact.
**For the sourced anchors behind most other constants, the date a figure became public is not
recorded anywhere a reader or a check can use.**

Evidence:

- `docs/institutional/knowledge_map.md` grades each row H/M/L, but no row carries a publication or
  "knowable from" date. Its own TDCV note admits the gap in prose: "the bands above are today's, and
  the value a supplier could have used in 2018 is not the one published in 2026."
- A search of `docs/market_research/`, `company/interfaces/`, `sim/` and
  `tools/domain_constant_origins.py` for any publication-date field found none.
- The three origins `domain_constant_origins` accepts (CITED, BELIEF, SIMPLIFICATION) record *where*
  a number came from, not *from when* it could have been used.

**This is not the problem the 2026-09-07 supersession atom closed.** That atom
(`a-commons-artefact-cannot-tell-when-its-source-was-revised`) asked whether a source has since been
**revised**, and its pre-registration measured six incompatible source shapes across the nine
commons artefacts. That is about the record moving after we read it. This problem is about the other
end: a figure published in 2020 used by a 2018 decision is foresight, even if the citation is perfect
and current. Two of the nine commons artefacts carry a fetch date in a machine-readable form. A fetch
date is not a publication date.

**Why it matters.** It is the same class as the July hedge-volatility lookback (a point-in-time leak
the import scanner could not see), moved from data into knowledge. A cited constant can be honest
about its source and still hand the company foresight. Nothing currently could notice.

## Problem 2 — a sourced fact and the code that should use it cannot find each other

CLAUDE.md records the instance: a sourced £55 acquisition cost sat in `saas/opex_ledger.py`, cited and
tested, reaching no code for seven weeks, while an invented £150 was what the campaign spent. The
knowledge map held the sourced figure **and** listed the same subject as a gap, in one file.
"Nothing told the reader to look."

`tests/architecture/test_a_cited_constant_has_a_caller.py` and `tools/domain_constant_origins.py`
close part of this from the **code** side (a cited constant must be reached; a constant must declare
an origin). The **knowledge** side has no equivalent. A knowledge-map row is prose in a table. It
has no identity that a constant can point at. So two silent states stay invisible:

- a sourced anchor that no constant uses (the £55 shape), and
- a constant whose CITED origin names a document, but no specific anchor in it, so the claim cannot be
  checked against the row that is supposed to support it.

## What the seat may want to consider (problems, not remedies)

- Whether the two problems share one fix. An anchor with an identity could also carry its
  publication date, and a check could then say both "this constant cites nothing" and "this decision
  uses a figure published after it".
- Where the boundary of "anchor" sits. Not every knowledge-map row is a number, and the commons
  artefacts already have structure of their own.
- How an unknown publication date should read. The external project's rule, recorded as its
  decision 0022, is "an unknown date is not an open one": a missing start must not be read as
  "since always". By the same logic, a figure with no known publication date is not knowable from
  the start of the run. The honest default is "cannot tell", and it shows on the surface, as the
  fail-closed habit already requires.

Measure before arguing: how many cited constants trace to an anchor whose publication date falls
inside 2016–2025? That count says whether this is a live leak or a latent one.

## Where this came from

The director asked what the open-source project `github.com/deeplethe/utopia` (v0.1, Apache-2.0, an
"enterprise world model") could teach Poesys. It stores every fact with two clocks, "true when" and
"believed when". It gives every fact an identity and its consumers. It treats a contradiction as a
pointer to an upstream error. The recommendation agreed with the director was to **adopt ideas, not
the software**. It is young (forward-only migrations), it would need a resident language model on a
memory-constrained host, and it would add a running service. The relevant adaptation is that, for a
supplier, the clock that sets the wall is a third one, **"published when"**, and Poesys has neither
that clock nor the other two on its anchors.

Three further ideas from the same reading were held back as lower value and are recorded only so
they are not lost: only human rulings become precedent for an automated judge (relevant to the
standing-approver seat); a fuse that disables automation after two human reversals in a week; and
"an unknown date is not an open one" as a general rule for time fields.

---

## Risk

- **Touches:** this file only. No executable path, gate, published figure or simulation output.
- **Blast radius:** seat attention. The likely failure is that this spawns a register or a new gate
  family. CLAUDE.md warns against that ("a file made of rules breeds rules"). Mitigation, inline:
  the problems are stated as problems, the seat owns the remedy, and the smallest check that can
  fail is preferred to a register.
- **Consume path:** the seat orients every three hours and read the 2026-10-09 advisor staging
  within four hours. No known blockage.
- **Proportionality:** reversible / narrow.
