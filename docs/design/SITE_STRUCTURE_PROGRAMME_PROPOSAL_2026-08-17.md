# Proposal — the website structure programme

**Answers:** `docs/staging/DIRECTOR_BRIEF_WEBSITE_STRUCTURE_2026-08-17.md` §9.5 ("Proposal before build.
The first draw is not construction: it is the worker returning a proposed sequence, a blast-radius
assessment per step, and any part of this brief it judges wrong").

**Status:** DISCOVER/FRAME only. No level moved, no atom minted, nothing under `site/` touched.
Measured at HEAD `a376c7b8c`, 2026-08-17, against the committed tree — not against the brief's census.

**Verdict on the brief:** accept the diagnosis, accept the five tabs, accept the ruled order, accept
the Explore specification in full. **Three things in it are wrong and one is dangerous**, all
because the brief's census of the current site is roughly half-size. Corrections C1–C6 below.
The recommended sequence differs from the brief's implied one in exactly one place, and the reason
is C3.

---

## 1. What is actually on the public surface

The brief reads "the nav reaches four areas; eight exist." Measured: **sixteen areas carry an
`index.html`**, and they are in **three states**, not two. The third state is the one the brief has
no slot for, and it is why §7's first control cannot be built as written.

| state | areas | count |
|---|---|---|
| **ADVERTISED** — in `site/sitemap.xml`, served, crawlable | `/`, `world`, `company`, `proof`, `customers`, `now`, `glossary`, `evidence`, `knowledge`, `privacy` | 10 |
| **INTERNAL** — deployed and served 200, deliberately absent from the sitemap, named in `site/live_pixel_verify.py::INTERNAL_DOORS` | `director`, `shadow` | 2 |
| **RETIRED** — 301 to `/proof/`, page kept in-repo for reference, noindex | `method`, `project`, `simplified`, `tours`, `wip-flow` | 5 |

The top nav reaches four: Home, World, Company, Proof.

**So the real no-caller class on the public surface is six**, not eight: `customers`, `now`,
`glossary`, `evidence`, `knowledge`, `privacy` are advertised to crawlers with no route from the
nav. Two of the six the brief names (`method`, `director`) are not in that class at all — `method`
has 301'd to `/proof/` since 2026-07-23, and `director` is deliberately internal. Two the brief
misses (`now`, `privacy`) are in it.

**There is no shared nav.** Sixteen pages carry **twelve distinct nav shapes**, and `evidence` —
98KB, the largest content page after `customers` — carries **no `<nav>` element at all**. Every
statement in the brief that reads as one edit ("five tabs, in a ruled order") is sixteen
independent hand edits against twelve different starting points.

Confirmed from the brief, unchanged: six identical `Evidence behind this stage →` labels on the
homepage — exactly six, word for word.

Corrected upward from the brief:
- **Eight pages carry zero `<h1>`–`<h4>`**, not four: `company`, `director`, `glossary`, `method`,
  **`proof`**, `simplified`, `tours`, `wip-flow`. `proof` being one of them matters — it is a
  current nav destination, 84KB, with no heading structure whatsoever.
- **Seven pages carry their own `:root` block**, not two: `customers`, `director`, `now`, `privacy`,
  `shadow`, `tours`, `wip-flow`. (`site/test_brand_token_adoption.py` already tracks these as a
  named debt register, so this is known debt, not a discovery.)

---

## 2. Knowledge is not a stub. It is nine copies of one stub.

This is the finding that changes the sequence, and it is worse than the brief's "`knowledge` is a
5.7KB stub."

`site/knowledge/` is 324KB across eleven pages: an index plus ten topic directories —
`gb-electricity-market`, `wholesale-price-formation`, `electricity-wholesale`, `gas-wholesale`,
`hedging-forward-market`, `imbalance-cashout-settlement`, `price-cap`, `carbon-price`,
`merit-order-residual-demand`, and `_stub`.

**Eight of them render byte-identical visible text.** MD5 of the tag-stripped text is `2ad82c7405`
for all eight, 292 characters each:

> Poesys — Knowledge (stub) … What this page will cover · Related topics · This page · A stub: it
> names the topic and its place in the domain graph, and says honestly that the full explanation is
> not yet written. It is not a to-do list in costume.

Three things follow. First, the page's own promise is false in the render: **it does not name the
topic.** A reader who clicks "Price cap" from the Knowledge index arrives at a page whose every
visible word is identical to the one behind "Carbon price", and neither says which is which. Second,
`wholesale-price-formation` is 14 words, zero headings, and **is not linked from the Knowledge
index** — an orphan inside an orphan. Third, `electricity-wholesale` is 20KB but 54 visible words:
its bulk is script and style, not prose, and it is the only Knowledge page linked from anywhere
outside the area (`world` links to it).

**No Knowledge page carries a last-reviewed date in any form** — so §4's "every page carries a
last-reviewed date" and §7's review-due control start from zero, not from a threshold change.

The brief prices Knowledge as a precondition to be cleared before the real work. It is the largest
content piece in the programme after Explore, and its current state is a live public-surface defect:
an advertised area serving nine pages of identical boilerplate to a crawler and a reader.

---

## 3. Corrections to the brief

**C1 — the census.** §1's numbers are half-size: sixteen areas not eight, six orphans not eight
(and two of the eight named are misclassified). Everything below follows from this.

**C2 — deleting `/proof/` is not deleting one page. It is deleting the destination of five 301s.**
This is the dangerous one. `/proof/` is where `method`, `project`, `simplified`, `tours` and
`wip-flow` were re-homed by the two prior IA migrations (Campaign A 2026-07-18, SITE_V5 2026-07-23),
and it renders their absorbed content at `#method-anchor`, `#project-anchor`, `#simplified-anchor`,
`#economics-anchor`, `#timeline-anchor`. Deleting it as §3 words it ("`proof` is **deleted, not
moved**") points five live redirects at a 404 and destroys the only rendered copy of five retired
areas' content.

**Recommendation:** `/proof/` is *dissolved*, not deleted — it becomes a redirect source like the
five before it (`/proof → /harness/ 301`), the five existing 301s are re-pointed to their new homes
in the same commit, and the anchor content moves before the redirect lands. Nothing leaves the tree.
This is the convention `site/_redirects` already states in its own comments ("Old page directories
are NOT deleted; absorbed content stays in-repo for reference"), and it satisfies §9.1
("nothing is deleted until its replacement is live") more literally than deletion does.

**C3 — §7 control #1 cannot be built as written; it needs the three-state register.** "A published
area with no route from the nav fails" is **red on twelve of sixteen areas today**, and for seven of
them (five RETIRED, two INTERNAL) that is correct behaviour the project chose deliberately. As
written the control's only green state is deleting pages the retirement convention says to keep.

**The failable version** — and it is failable, which the written version is not:
- an area in `sitemap.xml` **must** have a route from the nav (today: fails on six — the real defect);
- an area not in `sitemap.xml` **must** be either 301'd in `_redirects` **or** named in
  `INTERNAL_DOORS` (today: passes on all seven — the deliberate ones);
- an area in neither is the failure (today: none — and that is the state a careless migration creates).

This shape has a working precedent in the same file: `canonical_doors()` derives from the sitemap
rather than a hand-typed list, and fails closed on an empty or unreadable one. The control should
extend that register, not open a second one. Mutation for R15: point a sitemap entry at an area with
no nav route → red; drop an area from both the sitemap and `_redirects` → red.

**C4 — "method is deleted" is already true.** `/method` has 301'd to `/proof/` since 2026-07-23.
The residual is removing the file, which the retirement convention says not to do. Treat `method` as
done on arrival; the work is `glossary` only.

**C5 — the Knowledge precondition is the biggest piece, not the warm-up.** §2 above. §3's
sequencing constraint is right and should be strengthened: Knowledge must carry real content before
the *glossary* is deleted, and the nine identical stubs must be either written or unpublished
before Knowledge is put in the nav — promoting them to a top-level tab as they stand would take a
defect currently reachable only by crawler and put it one click from Home.

**C6 — `evidence` is the hardest single page and the brief does not name it.** 98KB, 145 headings,
no `<nav>`, advertised in the sitemap, and per §4 it is the machine dump to be dissolved. It is the
one page where "add the five-tab nav" is a from-zero edit, and it is the only advertised area whose
content is generated (`background/process_run_complete.py:2803` writes
`site/evidence/index.html` on every publish, ~half-hourly). **Editing that page by hand is
overwritten within the hour** — its restructure is a change to the generator, not to the file. No
other advertised area has this property; the rest are hand-committed and static.

---

## 4. Proposed sequence

The brief's §9.2 (one tab at a time, each independently publishable) and §9.3 (controls land with
the thing they govern) are accepted and drive this. One step is added before the brief's first, for
the reason in §1: without it every later step is a sixteen-file hand edit and §9.2 is unenforceable.

**Step 0 — one IA register, and the nav derives from it.** Extend the sitemap-derived register in
`site/live_pixel_verify.py` to the three states in C3; make every page's nav render from it. Land
C3's control here, red-listing the six real orphans without yet fixing them. No visible change; this
is the step that makes every later step one edit instead of sixteen.
*Blast radius:* `site/live_pixel_verify.py` and its six importers — `test_brand_token_adoption.py`,
`test_glossary_layer.py`, `test_no_links_to_redirected_urls.py`, `test_live_pixel_verify.py`,
`test_no_customer_portal_claim_outside_the_exhibit.py`, `tests/tools/test_site1_proof_crawlability.py`.
Sixteen `index.html` nav blocks rewritten mechanically. `site/link_walk.py` and `test_link_walk.py`
assert the resulting graph, so this step is self-checking. Highest coupling in the programme, zero
reader-visible risk.

**Step 1 — Knowledge, written.** Nine topics written for real, each with a last-reviewed date; the
review-due control lands with them; `wholesale-price-formation` either written or removed from the
tree. Knowledge is *not* yet in the nav.
*Blast radius:* `site/knowledge/**` only; no test currently asserts anything about Knowledge's
content, which is itself why nine identical pages shipped. The review-due control is new and needs
its own mutation (set a date past threshold → page must render review-due, not silently stale).

**Step 2 — Knowledge into the nav; delete the glossary.** Only now. Glossary becomes a 301 to
Knowledge; its 26 definitions move into the prose that needs them (§3's "plain language structural
rather than aspirational"). `site/data/glossary.json` has a live consumer in the glossary *layer*
(`test_glossary_layer.py`, 13 tests, L1: "definitions stay in ONE place") — the layer is a
term-inspection mechanism separate from the page, and killing the page must not kill the layer.
Decide that explicitly rather than by accident.
*Blast radius:* `test_glossary_layer.py` (13 tests) is the whole risk; `test_no_links_to_redirected_urls.py`
already guards the class of defect this step can create.

**Step 3 — Capabilities.** New area, no deletion, no redirect, no existing consumer. The cheapest
step in the programme and the one that most improves the first-time reader's path.
*Blast radius:* additive. New page + nav entry via Step 0's register. `tools/generate_capabilities_json.py`
already exists and writes capability data — check before building whether it feeds this or something else.

**Step 4 — Home reordered; link-label control.** The 6× label and §7 control #3 land together.
Diagram moved to the foot per §4.
*Blast radius:* `site/test_home_door.py` (6 tests) asserts the home nav and evidence links
structurally — expect all six to need updating, and read them before editing, since they encode
prior migration decisions.

**Step 5 — Harness, with `director` folded in.** Note the publication decision hidden in §4:
`director` is currently INTERNAL — deployed, noindex, off-nav by choice. Folding it into an
advertised tab **publishes the director record to crawlers for the first time.** That is very likely
intended (§4 calls it "a striking exhibit"), but it is a publication act and should be said out loud
rather than arrive as a side effect of a nav change.
*Blast radius:* `INTERNAL_DOORS` loses an entry; `tests/tools/test_site1_proof_crawlability.py`
asserts the never-advertised set and will go red by design.

**Step 6 — Explore.** The largest piece, per §5, at the presentation bar §4 sets. Draws as its own
commitment set. `site/customers/` (134KB, the existing wall exhibit) is the substrate and the two
should be reconciled rather than built beside each other — the brief's own "the earlier CRM-style
view set the standard" is describing a page that still exists.

**Step 7 — Proof dissolved last**, per C2: content re-homed, `/proof → /harness/`, five 301s
re-pointed, nothing deleted from the tree.
*Blast radius:* the five re-pointed redirects, `test_no_links_to_redirected_urls.py`, and every
in-page link to `/proof/#*-anchor` — six pages carry them today.

**Why Step 3 (Capabilities) sits after Knowledge rather than first**, against the temptation to bank
the cheap win: §3's sequencing constraint binds the *deletions* to Knowledge, and Steps 1–2 are the
only pair with a hard ordering between them. Capabilities could move earlier at no cost if the
director prefers visible progress sooner; it is the one step in this sequence with no ordering
argument attached, and I am not going to pretend otherwise.

---

## 5. What I am not proposing

Not proposing a mint yet — §9.4 says this does not jump the queue, and the publish-gate wiring and
PB3 ADD path are in flight. This document is the proposal §9.5 asked for; the commitment set gets
minted when capacity exists, with Step 0 as its first drawable item.

Not proposing to fix any of C1–C6's findings on sight. The nine identical Knowledge pages are a live
public defect and I have left them alone — SELF-INTERRUPT DISCIPLINE: they are Step 1's subject,
not a reason to interrupt the queue.

---

## 6. Open questions for the director — **ALL FOUR RULED 2026-08-18**

> **RULED, director console, 2026-08-18.** *"All four recommendations accepted, with one condition on
> the director record: show me its rendered content before it becomes crawlable — it was written
> internally and I want to read it as a stranger would first. Everything else proceed on your
> sequence, Step 0 first. Good catch on /proof/; my instruction would have broken five live
> redirects."*
>
> Full record: `docs/staging/done/DIRECTOR_RULING_SITE_STRUCTURE_PROGRAMME_ACCEPTED_2026-08-18.md`.
> The commitment set is minted as `SITE4`–`SITE11`; **Step 0 is built** (`site/ia_register.py`,
> `tools/render_site_nav.py`, `site/test_ia_register.py`). Q3's condition is binding and **silence
> does not release it** — a deliberate carve-out from THE_STANDARD, his, made in the same breath as
> accepting the recommendation; it is mechanised in
> `site/ia_register.py::director_record_publication_violations`, not left as prose.


Recommendations attached to each, per NEVER_ASK_WITHOUT_RECOMMENDING. **Silence is validation —
absent an objection I will proceed on the recommendation.**

1. **`/proof/` dissolved rather than deleted (C2).** *Recommendation: dissolve.* Deletion breaks five
   live redirects and destroys five areas' only rendered content, for no gain the brief asks for.
2. **Control #1 becomes the three-state register (C3).** *Recommendation: yes* — as written it is red
   on twelve areas and its only green state is deleting pages we chose to keep. The three-state
   version is failable and has a working precedent in the same module.
3. **Publishing the director record (Step 5).** *Recommendation: publish*, since §4 explicitly wants
   it as an exhibit — but flagged rather than silently executed, because it moves a deliberately
   unadvertised surface into the crawlable set.
4. **The glossary layer survives the glossary page (Step 2).** *Recommendation: keep the layer.*
   §3's argument is against the *page* — a warehouse of definitions a reader must already know to
   find. Inline term inspection is the opposite of that and serves §6.7 directly.

— Worker, 2026-08-17. Measured at `a376c7b8c`. R9: every count in §1–§2 is observed-with-evidence
from the committed tree; the reader-impact readings in §2 and the intent reading in Step 5 are
inferred and labelled as such.
