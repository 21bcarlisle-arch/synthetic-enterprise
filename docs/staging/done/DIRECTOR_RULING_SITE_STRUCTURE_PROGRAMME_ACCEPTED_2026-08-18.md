# [DIRECTOR-RULING] — The website structure programme is accepted (2026-08-18)

**Type:** [DECISION]. Ruled by the director in the interactive console, 2026-08-18 ~07:14 BST.

**Answers:** `docs/design/SITE_STRUCTURE_PROGRAMME_PROPOSAL_2026-08-17.md` §6, the four open questions
returned under NEVER_ASK_WITHOUT_RECOMMENDING against
`docs/staging/in_progress/DIRECTOR_BRIEF_WEBSITE_STRUCTURE_2026-08-17.md` §9.5.

---

## The ruling, verbatim in substance

> "All four recommendations accepted, with one condition on the director record: show me its rendered
> content before it becomes crawlable — it was written internally and I want to read it as a stranger
> would first. Everything else proceed on your sequence, Step 0 first. Good catch on /proof/; my
> instruction would have broken five live redirects."

## What that decides

| # | Question (proposal §6) | Recommendation | Ruled |
|---|---|---|---|
| 1 | `/proof/` dissolved rather than deleted (C2) | dissolve | **ACCEPTED.** The brief's §3 "`proof` is **deleted**, not moved" is overturned by the director's own word: deletion would have pointed five live 301s (`method`, `project`, `simplified`, `tours`, `wip-flow`) at a 404 and destroyed the only rendered copy of five retired areas' content. Step 7 dissolves it: content re-homed first, `/proof → /harness/ 301`, the five existing redirects re-pointed in the same commit, nothing removed from the tree. |
| 2 | Control #1 becomes the three-state register (C3) | yes | **ACCEPTED.** The brief's §7 control #1 as written ("a published area with no route from the nav fails") is red on twelve of sixteen areas and its only green state is deleting pages the retirement convention says to keep. It is replaced by the three-state form: ADVERTISED must have a nav route; not-advertised must be 301'd or named internal; in neither is the failure. |
| 3 | Publishing the director record (Step 5) | publish, flagged | **ACCEPTED WITH A CONDITION — see below.** |
| 4 | The glossary layer survives the glossary page (Step 2) | keep the layer | **ACCEPTED.** `test_glossary_layer.py`'s L1 ("definitions stay in ONE place") and the term-inspection mechanism survive Step 2; only the warehouse *page* dies. |

**Sequence:** the proposal's Steps 0–7 stand as ruled, **Step 0 first**.

---

## The condition (binding, and it is the one gate in this programme)

**Step 5 may not make `/director/` crawlable until the director has read its rendered content.**

Director's reason, in his words: *"it was written internally and I want to read it as a stranger
would first."*

Operationally this means, and the Step 5 atom carries it as its block:

1. Before any commit that removes `/director/` from `INTERNAL_DOORS`, adds it to `sitemap.xml`, or
   drops its `noindex`, the worker renders the page **as it will be served** — driven by its live
   feeds, not read as source — and puts that rendered content in front of the director.
2. What is shown is the reader's view: the visible text a stranger meets, not the markup and not a
   summary of it.
3. The director's word releases the block. Silence does **not** release it. This is a deliberate
   carve-out from THE_STANDARD's "silence is validation", made by the director in the same breath as
   accepting the recommendation, and it is legitimate under `one_way_door` class 3 — moving a
   deliberately unadvertised surface into the crawlable set is a public claim under Poesys's name
   that a later `noindex` does not retract from an index.
4. Everything else in Step 5 (the Harness tab, the methodology account, the failure classes, the
   folded-in *section shell*) proceeds without waiting. Only the advertisement of the director
   record is held.

**No new machinery is created for this.** It is registered as `action_needed` under reserved class 3,
which is the one queue that may legitimately hold a director ask. No gate, seam, channel or ceremony
is added to the director's path — proposing one would itself be a defect (CLAUDE.md, NTFY IS THE
DIRECTOR).

---

## Correction accepted back up the chain

The director's own instruction in the brief (§3, "`proof` is **deleted**, not moved") was wrong on
the evidence and he has said so. The correction is recorded here rather than silently applied, per
R9: the census that produced it is `SITE_STRUCTURE_PROGRAMME_PROPOSAL_2026-08-17.md` §1–§3, measured
at HEAD `a376c7b8c` against the committed tree, and every count there is observed-with-evidence.

`site/_redirects` keeps its existing convention comment as the standing precedent: *"Old page
directories are NOT deleted; absorbed content stays in-repo for reference."*

---

## WORK THIS CREATES (canonical, in-document)

1. The commitment set minted: `SITE4`–`SITE11`, one atom per proposal Step 0–7, Step 0 drawable now
   and the rest chained on their stated ordering.
2. `SITE9` (Step 5) carries the condition above as its block, with the release named.
3. Step 0 built: the three-state IA register, the nav derived from it, and C3's control landed
   red-listing the six real orphans without yet fixing them.

— Ruled 2026-08-18, director console. Recorded by the worker in the same turn it was given.
