<!-- SUPERVISOR_DRAW: parked -- one genuinely-open sub-item, named below. -->
> **PARKED IN `in_progress/` 2026-07-29 (worker tick). Not absorbed silently — here is the split.**
>
> **ANSWERED, landed:** the account of why + the class named + the root cause + a sweep that found a
> previously-unknown fourth instance are all written at
> `docs/retrospectives/2026-07-29-three-silent-drawability-blind-spots.md` (commit `745c83fa3`),
> under R9 claim discipline (every claim labelled `observed-with-evidence` or `inferred`).
>
> **THE DIRECTOR'S PROPOSED DEFENCE IS RIGHT, AND IS NOW BUILT TWICE — this is the substantive news.**
> His suggestion was: *"count what exists independently of the mechanism that decides what is drawable,
> and require the two to agree."* Two independent readers of exactly that shape are now live:
> * `background/gap_register_scan.py` (atom `GAP1_gap_registers_as_mint_sources`, self-certified L3
>   2026-07-29) — reads the 8 published gap registers from PRIMARY state and imports **nothing** from
>   `supervisor`, so it cannot restate the tick's own belief. Live right now: 8 open residue rows, i.e.
>   it is actively forbidding an illegitimate rest.
> * `background/deadmans_switch.py::_check_open_mint_escalation` — reads `in_progress/*.md` off disk
>   *before and independent of* the proven-rest fold whose falsely-empty verdict it exists to catch.
>
> **STILL OPEN — the one blocking sub-item:** the director asked for the account **"published where a
> reader can follow it ... a good subject for showing your working."** A retrospective in
> `docs/retrospectives/` is an internal artefact, not a published surface. The remaining deliverable is
> a reader-facing page (the `/proof` or `/method` door, per SITE_CONSTITUTION) carrying the failure and
> its reasoning, pixel-verified live per R11. **Unblocks:** a SITE-lane draw — no permission needed, it
> is Lane-2 work on `site/**`, disjoint from BUILD.
>
> **ALSO OPEN (non-blocking, smaller):** an explicit point-by-point verdict on the advisor's 5-point
> hypothesis. Provisional reading, to be written up on that page: points 1, 2 and 4 **confirmed**
> (nothing tested that things APPEAR; the faults were silent by construction; nobody wrote *"if
> unfinished work exists, something must be drawable"*). Point 3 **partially refuted** — the tests were
> not merely written by the same reasoning as the fault; several were genuinely mutation-proven and
> *still* passed, because they proved the rule FIRED, never that the rule was the right rule. That
> distinction matters more than the agreement does, and it is the sharper version of his own point.

# [DIRECTOR-QUESTION] — How did 31 pieces of work stay invisible through all of it? (2026-07-29)

**Type:** [DIRECTOR-QUESTION]. Not a work order. The director wants the *understanding*, and he wants it published as one of the things you show your working on.

## The question

Thirty-one atoms with a real level gap yielded **zero** drawable work. Three mechanisms hid them. Every one of them passed every gate, test, rule and review we have.

**How did that happen, and what does it say about the checks themselves?**

Not "what were the three bugs" — you have already answered that well. The question is why an elaborate apparatus of rules, gates, mutation tests, hardening loops and reviews **could not see it**, for days, while the director and the advisor argued about whether you were being lazy.

## An advisor hypothesis — confirm, refute or improve it

Offered as a starting point, not a conclusion:

1. **Everything tested that things WORK; nothing tested that things APPEAR.** Every check asks "when this runs, is the answer right?" None asked "is anything missing?" You can verify every machine on a production line and never notice the warehouse is empty.
2. **All three faults were silent by construction.** An atom dropping out of consideration produces no error — it is indistinguishable from an atom with nothing left to do. "Nothing available" was the *correct* output from corrupted input, so there was no wrong answer to catch.
3. **The tests were written by the same reasoning that wrote the fault.** Whoever decided `blocked_on` should suppress every lane also wrote its test, and the test confirms the intention. **A test proves a rule fires when it should; it cannot tell you the rule was the wrong rule.**
4. **Nobody wrote the one invariant that mattered:** *if unfinished work exists, something must be drawable.* One line. It would have caught all three on day one.
5. **The advisor's share:** eight rules were added about how to *choose* work, and not one about whether the list being chosen from was true.

## What the director wants back

- **Your account of why**, in plain language, published where a reader can follow it. This is a good subject for showing your working — it is a genuinely interesting failure and the reasoning is more valuable than the fix.
- **The class, named.** If "silent absence" is a defect class we have no defence against, say so and say what defence would look like.
- **A suggestion, not a mandate:** we already solved this shape once — the watchdog was made to read reality rather than trust your own report of it. **The same idea applied to work itself**: count what exists independently of the mechanism that decides what is drawable, and require the two to agree. Is that the right defence here? Propose better if you can see better.
- **A sweep:** where else does the system trust a single count, a single derived view, or a single "nothing to report" that nothing independently contradicts? That is the same shape, wherever it lives.

## How to answer

**Act on what you conclude.** If the invariant is right, add it. If the sweep finds siblings, fix them. Do not send a proposal and wait — tell the director what you found and what you did.

**And be honest if the hypothesis above is wrong.** A refutation with evidence is worth more than agreement.

— Advisor bridge, carrying the director's question. The advisor added eight rules about choosing work and never checked the list. 2026-07-29.
