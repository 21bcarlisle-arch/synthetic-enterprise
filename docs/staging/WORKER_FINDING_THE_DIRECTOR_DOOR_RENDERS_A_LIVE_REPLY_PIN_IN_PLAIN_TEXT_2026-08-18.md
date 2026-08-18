**Severity:** LATENT · **Lane:** H_harness

# The director door renders a live reply-PIN in plain text, and Step 5 proposes indexing it

**Found:** 2026-08-18, rendering `/director/` as a reader meets it for the director's
condition on `SITE9` (`docs/observability/director_record_render_2026-08-18.txt`).

**Class:** the thing a page says out loud that nobody re-read after it was written.

---

## Observed, with evidence

The live `/director/` door (HTTP 200, fetched 2026-08-18, driven by its own feeds through
`site/_live_harness.mjs`) renders, inside the reserved-queue panel:

> `executor-wall_escalated-f13e76f1` **RESERVED**
> …
> **Reply to CLOSE: start your NTFY with PIN 8883 (e.g. 'PIN 8883 PROCEED').**

The PIN is not decoration and it is not in the repo — it is minted per escalation by
`background/action_needed.pin_for(item_id)` and rendered by
`background/executor_governor.py:245`. Its consumer is
`background/ntfy_responder.py::resolve_by_pin`: a message on the director's ntfy topic
beginning `PIN 8883` **resolves that escalation** — it is closed, marked `[RECORDED]`, and
deliberately NOT re-staged as a fresh command.

So the string is a **capability token with an action attached**, rendered in plain text on a
page. `observed-with-evidence`: the render, the mint site, and the consumer are all named
above and all read from the committed tree.

## Why it is LATENT and not BLOCKING — stated, because the temptation runs the other way

First draft of this document said BLOCKING. That was wrong against the ruling's own words:
BLOCKING is *"a control or instrument in this area is untrustworthy, or a published figure
may be wrong."* Neither holds. No control's verdict is affected, no published figure is
wrong, and `/director/` is not advertised — so nothing published is invalidated today.
LATENT is *"real defect; does not invalidate anything published or any control's verdict"*,
which is exactly this.

The severity parser's docstring warns about the opposite error — *"deciding one's own
finding is not BLOCKING in order to keep a lane open"* — so the reasoning is written down
rather than left to look like convenience. BLOCKING would have frozen level raises across
`H_harness`, the project's largest lane at 125 atoms, for a defect that gates exactly one
act. That act is already refused by a tighter mechanism than a lane-wide freeze:
`site/ia_register.py::director_record_publication_violations` plus the reserved-class item
`SITE9_director_record_publication`. A broad freeze here would buy nothing and stop a lot.

If the director publishes the door with the PIN still on it, this becomes BLOCKING that
day, and the finding should be re-graded rather than re-argued.

## Why it needed saying before the director answers, not after

Nothing about today's state is new — `/director/` has always served 200 to anyone with the
URL, and the PIN has always been on it. What is new is that **Step 5 (`SITE9`) proposes
folding this door into an advertised tab**, which puts the token in front of a crawler and
into an index. `noindex` removal is not retractable by re-adding `noindex` later.

The page's own copy says *"the view itself is not behind a lock: it renders read-only repo
state, and a client-side PIN that opened with any key would be theatre"* — which is true of
the PIN's **authentication** role and silent about its **correlation-with-an-action** role.
`resolve_by_pin` is a write. The page is honest about the lock it does not have and quiet
about the one affordance it does.

## What this does NOT claim (R9)

- It does **not** claim a compromise, an external actor, or that anyone has used a PIN.
  Nothing was checked that would support any of those and no such check was run.
- It does **not** claim the ntfy topic is otherwise unprotected — that was not examined.
- The reading that indexing raises the exposure is `inferred`, though the mechanism
  (crawl → index → cache) is not in dispute.

## Disposition

**QUEUED against `SITE9`, not fixed on sight** (SELF-INTERRUPT DISCIPLINE). It is not
blocking any current draw: `SITE4` is landed and `SITE5`–`SITE8` do not touch this door.
It blocks exactly one thing, which is the thing the director is being asked to decide, so
he has been told before he answers rather than after.

**Candidate remedies, for whoever draws `SITE9` — none chosen here:**
1. Render the reserved queue's `how` field with the PIN clause stripped on any surface that
   is or may become advertised (the PIN reaches the director by NTFY already; the page is
   a second copy of something he has in his hand).
2. Give `resolve_by_pin` a second factor, or scope the PIN to a single use.
3. Keep `/director/` internal and fold only a curated, PIN-free view into Harness — which
   is arguably what "a striking exhibit" in the brief actually wants: the *shape* of what a
   human decided, not the live ops queue with its live tokens.

Remedy 3 costs the least and loses the least; it is not a recommendation until someone has
read the whole door with Step 5's eyes rather than this finding's.
