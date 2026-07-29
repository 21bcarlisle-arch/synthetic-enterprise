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
