**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [ADVISOR-NOTE] How it's built: two advisor chats staged for the same page this morning; build it as one page (2026-10-23)

**Type:** sequencing note from the advisor, on the director's standing delegation of 15 Oct. It changes no intent. It says how two sets of director-attributed steers fit together on one page.

**The overlap.** Two advisor chats staged steers for `site/harness/` this morning:
- `DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR_2026-10-23.md`, §4. It quotes him at 07:18: "Make more appropriate for energy or tech person who is not familiar with the detail".
- `DIRECTOR_STEER_SHOW_THE_HARNESS_AS_A_LIVE_CONTROL_STACK_2026-10-23.md`, and its follow-ons on meaning and learning, and on doors, pace and balance. It quotes him at 09:20.
- `DIRECTOR_STEER_SHOW_EVERYTHING_WE_HAVE_LEARNED_FROM_THE_RECORD_NOT_FROM_MEMORY_2026-10-23.md`, which quotes him at 09:27.

They agree. Build them as one page, in this shape:

1. **The control stack is §4's diagram.** The eight-layer stack, running from intent to the published page, replaces the simpler "loop" diagram in §4. Draw one diagram, not two.
2. **The page stays newcomer-first (07:18).** The top of the page carries:
   - the one-sentence purpose and the "In brief" box;
   - the stack, with a plain-English label per layer;
   - the generated scale numbers;
   - last week's highlights.

   Each box's live evidence (30-day firings, last fired, able to fail) sits on the box. The full detail sits one tap down.
3. **The follow-on sections come after the highlights.** That means meaning and learning, what it refuses, doors, pace and balance, and the record-mined learning when it lands. Each starts with its own "In brief", and each is collapsed by default. The war stories become the lesson cards §4 asks for, and they are the evidence for the stack's "learning" layer, not a separate list.
4. **One cold-reader pass covers the whole page,** as §4's checks require. If either reader's summary leads with the failings, or gets lost in the machinery, the page has not met either steer.
5. **Timing is unchanged.** Items 1–3 of the control-stack series ship with Monday's rework. The record-mined learning (the fourth file) follows that publish.

**Also noted.** One advisor commit this morning (`1597db0d`) carries the author `advisor@poesys.local`, which GitHub shows as unverified. The channel's provenance check reads the pinned signing key, not the email, so the file is still valid. Report it if the check ever disagrees.

— Advisor, on the director's standing delegation of 15 Oct.

## Done

*Worker tick, 23 Oct 2026.* Built to this shape. It is one page with one diagram: the eight-layer stack is §4's diagram. The top of the page stays newcomer-first. The two follow-on sections come after the lessons, each collapsed and opening with its own In brief. The record-mined learning steer follows the publish, as this note sets out. The parent steer, `DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR_2026-10-23.md`, stays in the advisor channel because its Explore section (§6) is not yet done.

**Cold-reader pass over the whole page (23 Oct), one energy reader and one tech reader, blind, with the extra question.** Both said the page is for showing how AI builds and runs a simulated supplier through eight layers of checks. The tech reader led with achievements and answered the extra question: "live per-layer evidence that each check can fail, with sample sizes, instead of boxes and arrows", a measured error rate for the AI reviewers, failure stories, a number only a simulation can produce, and "an explicit rule against tuning itself to a score". The energy reader led with neither, opening with purpose and scale, and said the most concrete content was the lessons, the reviewers misses and the low product share. Fixed from their confusions: "Four classes of decision are the director's" contradicted the "7 kinds of action" read from `background/one_way_door.py`, and the prose was wrong against the code, so it now lists the seven; "A refused one leaves no record" now reads "Refusals are not logged, so they are not counted". Not fixed here, and left open: both readers read the HTML source, so sections the page fills from its feeds looked empty to them; the one that a reader without JavaScript also sees empty is the belief-and-truth number, which the parent steer asks to render at publish and which is still filled by script. The low product share (4% to 24% a week) is shown as it reads, as the doors-and-pace steer asks.
