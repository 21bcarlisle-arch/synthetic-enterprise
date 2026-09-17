# Pre-registration: what a browser meets on the LIVE deployed doors

*Filed 2026-09-17, BEFORE the first reading was taken. The measurement's answer is not known: no
control in this repository has ever loaded `https://poesys.net/<door>` in a browser.*

## The gap being closed

Two halves exist and their union has a hole exactly where the reader is:

| control | subject | what it proves |
|---|---|---|
| `site/live_pixel_verify.py` (G1/G2/G3) | the **live deployed host** | the host served these bytes, the live feeds were reachable and parsed, and the door's own script turned them into strings — **in node's `vm`**. No pixel. |
| `site/test_the_browser_reading.py` | the **published index copy**, served over local http | a person with chromium can see the element: it exists, survives the stylesheet, survives every later script, has a box. |

Neither proves **a person can read the LIVE page**, which is the only claim R11 and CLAUDE.md's
"done means the rendered value changed" actually make. The three breakages measured on 2026-09-17
(`docs/design/WHAT_THE_VM_DOORS_GRADE.md`) are all deployable and all invisible to the vm verifier.

## How the element list will be derived, and why that is the whole design

**Not hand-typed.** The vm harness already reports every element id the door's own script wrote
content into. That set is the derivation: *the elements the door wrote to are exactly the ones a
reader must be able to read.* This makes the browser leg a strict addition to the vm leg rather
than a second opinion, and it lines the three measured breakages up against it by construction:

- **C (renamed container)** — the vm's `getElementById` MINTS an element for any id, so the vm
  reports content written to `#deployment` while the live DOM has none. `exists: false`.
- **A (`display:none` in the page's own `<style>`)** — the vm parses no CSS. `visible: false`.
- **B (a later inline `<script>` clearing the section)** — the vm's regex takes only the FIRST
  inline script. `visible: false` / `innerLength: 0`.

## The predictions, recorded before the run

1. **Every door will serve 200 to chromium.** Low information — G1 already establishes this today.
   Recorded so that a failure here is attributable to the browser path (a blocked subresource, a
   CSP, an edge behaviour that differs by User-Agent) rather than to the host.

2. **At least one door will have at least one element the vm reports as WRITTEN that a browser
   reports as NOT VISIBLE.** Roughly 30 doors have never been read this way. I do not predict
   which, and I do not predict it is a defect — see 3.

3. **The dominant cause of (2) will be DELIBERATELY HIDDEN CONTENT, not a broken page** — a panel
   behind a tab, an `aria-hidden` detail block, a section a click expands. If that is what the
   reading shows, then "every written element must be visible" is the WRONG rule and shipping it
   would wedge the live tool on correct pages, which is the false-positive class this project has
   stalled on before. **The rule is therefore NOT being chosen in advance.** The table gets printed
   at real inputs first (CLAUDE.md: "print the numbers at real inputs before you ship a formula"),
   and the rule is chosen from it.

4. **`exists` will hold universally and is safe to make a hard clause whatever the table says.**
   If the door's script wrote to `#x` and `#x` is not in the live DOM, the browser raised a
   `TypeError` inside a `.then()` and the rest of that callback is dead. There is no legitimate
   page on which that is fine. I predict **zero** doors fail this — and if any does, it is a live
   reader-facing defect found on its first look, which is the outcome that would most justify the
   work.

5. **Cache-busting the page URL alone is not enough for this control**, unlike G1/G2/G3. Those
   conclude about the page and its feeds; G4 concludes about *visibility*, which is decided by the
   **stylesheet** — an uncached subresource. A stale `assets/*.css` can only make an element look
   visible that the current one hides, i.e. a false GREEN. I predict every subresource must be
   busted through the browser's own request interception for the absence conclusions to be sound,
   and that doing so changes no reading on a healthy page.

---

# THE RESULT, filed beside the predictions — 2026-09-17

**The reading, taken before any rule was chosen** (element list derived from what the vm harness
reports each door's script wrote into; chromium against `https://poesys.net/<door>`):

| door | elements the vm says it WROTE | not in the live DOM | on the page but not visible |
|---|---:|---:|---:|
| `/` | 4 | 0 | 0 |
| `/knowledge/` | 16 | 0 | 0 |
| `/capabilities/` | 41 | 0 | 0 |
| `/explore/` | 8 | 0 | 0 |
| `/harness/` | 17 | 0 | 0 |
| `/privacy/` | 0 (static — no client render) | — | — |
| **total** | **86** | **0** | **0** |

Zero page errors on every door. Every door served 200 to chromium.

**Prediction 1 — CONFIRMED.** Every door serves 200 to a browser; no UA-gated or CSP difference.

**Prediction 2 — REFUTED, and it was mine.** I predicted at least one written-but-invisible
element across ~30 doors. There are 6 doors, not ~30, and across all 86 written elements there is
not one. Recorded rather than revised: the prediction was wrong in both its magnitude and its
direction, and the mechanism was built anyway because the gap is structural, not incidental.

**Prediction 3 — MOOT, and that is what decided the rule.** There is no deliberately-hidden
written content on this site, so the false-positive risk I was hedging against does not exist
today. The STRICT rule — every written element must exist, be visible, and carry words — was
therefore chosen, at zero cost. Had the table been chosen in advance I would have shipped the
weaker rule out of a fear the evidence refutes.

**Prediction 4 — CONFIRMED.** `exists` holds universally: 0/86 missing. No live reader-facing
defect was found on the first look. The control has therefore never had to fire on a real defect,
which is a weaker thing than one caught in the wild — so it is mutation-proved offline instead,
on each clause it names, and the mutations are recorded below.

**Prediction 5 — CONFIRMED in mechanism, unobservable in effect.** Every subresource is now
cache-busted through the browser's own request interception, and doing so changed no reading on
any door — exactly as predicted for a healthy page. The value is in what it makes SOUND: G4's
conclusions are absence-shaped ("not visible", "not in the DOM"), and CLAUDE.md's own cache
incident says absence and staleness are indistinguishable through an edge copy.

## The mutations, run in this worktree

| # | mutation | expected | result |
|---|---|---|---|
| M1 | drop the `visible` clause from `_judge_reading` | the stylesheet leg reds | **fired** |
| M2 | let an unreadable page return an empty reading instead of raising | the fail-silent leg reds | **fired** |
| M3 | hand-type the element list instead of deriving it from G2 | the derivation leg reds | **fired** |
| M4 | widen the `:body` carve-out by dropping its `display` clause | the whole-page leg reds | **did NOT fire** |

**M4 is an equivalence, established rather than assumed.** A `display:none` body collapses its box
to 0×0, so the `box.width > 0 && box.height > 0` clause already catches it and the `display` clause
could never change a verdict. It has been DELETED — a clause no mutation can distinguish is a
clause that reads as protection and provides none — and the deletion is recorded in the probe
beside the carve-out it was written to narrow.

## What the live run now reports

`6/6 doors verified on the LIVE surface`, exit 0, with `read_by_a_browser` printed next to
`rendered_elements` on every line. The gap between those two numbers is the distance between "the
page computed it" and "a person can read it", and it is now on the surface of every run instead of
being assumed to be zero.

## What would refute the work

- If the table shows **no** written-but-invisible element anywhere, prediction 2 is refuted and I
  will say so beside it. The mechanism is still owed — it would then be a control that has never
  had to fire, which is a different and weaker thing than one proved on a real defect, and it must
  be mutation-proved offline regardless.
- If prediction 4 fails on a door, that is a finding with its own severity header, not a footnote.

## Done means

A control that loads the LIVE deployed URL in chromium, derives its element list from the door's
own render, states its reading fail-closed, is proved able to fail offline on each clause it
names, and has been RUN against the live host with the result recorded here beside these
predictions.
