**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what the field-keyed sweep will find, written before it ran

**Filed:** 2026-09-08, delivery seat (isolated worktree), claim
`the-branch-half-of-the-multi-home-sweep`.

Written **before** the probe measurement, so the numbers below can refute the design rather than
be fitted to it. The descriptive facts already in hand (the eleven zero-home strings, the 26 raw
producer literals) are re-measurements of things the tree already states and are NOT predictions.

---

## The design under test

`site/test_a_here_relative_pointer_has_one_home.py` derives a payload string's homes by rendering
each door against `site/data/*.json` and matching the *published value* into the rendered regions.
It says so on its own surface: *"a producer branch today's data does not drive renders nowhere and
is judged nowhere"*. Measured at draw time: **eleven** here-relative payload strings render in zero
regions (its docstring says twelve; the tree has moved and eleven is the count today). Zero of the
31 multi-home strings are here-relative, so the rule passes — over a corpus it can only judge where
today's data happens to reach.

The generalisation: **a home is a property of the FIELD, not of the value that happens to be in it
today.** Derive it by injecting a unique marker into each string field and re-rendering the door's
own boot path. A producer branch is only observable through the value it writes into a field, and
the harness (`site/_live_harness.mjs`) stubs `querySelectorAll` and dispatches no events, so
*door*-script branches are not drivable at all — the producer's are, by injection. That is the
`_every_pointer_this_page_can_publish` shape at site scale, without 29 bespoke branch drivers.

## The predictions

**P1 — probing finds strictly more multi-home FIELDS than value-matching finds multi-home
STRINGS.** Value-matching finds 31. I predict the field probe finds **> 31**, point estimate
45–90. *Refuted if ≤ 31* — which would say the probe adds nothing and the value match was never
the blind side.

**P2 — some, not most, of the eleven are recoverable.** Of the eleven zero-home here-relative
strings, I predict **between 2 and 7 inclusive** have a field with ≥1 home under probe. Below 2
says the zero-home set is genuinely unrendered (indices past a slice cap, feeds read by a door
that renders other keys) and the probe buys nothing for them; above 7 says the containment match
is far more broken than a truncation-and-markup story explains.

**P3 — at most one live latent defect.** I predict **at most 1** of the eleven has a field with
**≥2** homes — a here-relative pointer sitting in a multi-home field today, invisible to the
value-keyed sweep. If it is 2 or more, the existing control's blindness is materially worse than
its own docstring admits, and that is the finding rather than the control.

**P4 — the producer census is small and at least one literal is untied.** Excluding docstrings, I
predict **between 5 and 20** here-relative string literals across `tools/generate_*.py`, and that
**at least one** of them appears in no feed field today — i.e. it lives on a branch today's data
does not drive, which is the exact class this rung exists for.

## What done means for the turn

Not a number. A landed control that judges a here-relative sentence by **its field's** homes and
by **the producer's** ability to emit it, with the reachability legs that stop it passing on
blindness, and a mutation rung proving both directions. If P1 is refuted the design is wrong and
the finding says so instead.
