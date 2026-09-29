**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# FINDING — a declared `None` is the sanctioned way to carry a gap, and nothing requires the knowledge layer to know it exists

Found while landing the PB4 bill-shock seam (`2cb273bca`) on the scheduled tick of 2026-09-25.

## The defect

`CLAUDE.md` makes the declared absence the sanctioned shape: *"an honest `None` with a named reason
is worth more than a plausible number"*. Two constants carry that shape today:

| constant | its `_GAP` / reason sibling | declared in `docs/institutional/knowledge_map.md`? |
|---|---|---|
| `tools.published_route_split.SVT_INTERNAL_CONVERSION_RATE` | in-file reason + two published bounds | YES — *Active vs passive renewal* |
| `simulation.household_segments.BILL_SHOCK_ENGAGEMENT_MULTIPLIER` | `BILL_SHOCK_ENGAGEMENT_GAP` | **NO until this tick** — added to *Does the LEVEL of a household's own bill drive switching?* by the same pass that found this |

Both were correct in their own file. The second was invisible from the knowledge layer for a day,
which is the £55/£150 acquisition-cost shape with the signs swapped: there, a sourced figure reached
no code while an invented one was spent, and the map recorded both halves in one file with nothing
pointing between them. Here a gap is declared in code and the map does not know the subject is open.

**Nothing can observe it.** `tests/architecture/test_a_domain_constant_carries_its_origin.py` asks
that a rate/price/probability/threshold declares an origin — a `None` with a reason satisfies it, as
it should. `test_a_cited_constant_has_a_caller.py` asks the mirror question about *sourced* constants
and its own docstring names this exact file as the place the first instance hid. Neither asks whether
the knowledge layer declares the gap. So the property holds today because two sessions happened to
write the pointer, not because anything requires it.

## Why LATENT and not BLOCKING

No instrument is untrustworthy and no published figure is wrong. The population is **2** and both
members are now compliant, so nothing downstream is misled right now. What is missing is the
mechanism that keeps it true as the population grows — and it grows every time a session does the
right thing under the rule `CLAUDE.md` states.

## The control this wants, in one leg

A scan over `company/`, `saas/`, `simulation/` and `tools/` for a module-level constant assigned
`None` whose name matches the domain-constant vocabulary the origin gate already owns
(`tools/domain_constant_origins.py` — reuse its classifier rather than writing a second one), then:
the constant's own name must appear in `docs/institutional/knowledge_map.md`. Two properties it must
carry, both of which this repo has paid for:

* **assert the population is non-empty** before grading it — `tests/architecture/
  test_no_tree_scan_passes_on_an_empty_population.py` exists because a narrowed pattern reads green
  either way, and a census whose offender list is empty is unfalsifiable.
* **key it to the property, not to today's two members.** A literal count of 2 becomes an absent
  control the moment a third is declared.

Not built here: this tick's drawn work was the PB4 build, and a new architecture control is its own
atom rather than something to add to a build commit unasked. Filed so it can be drawn.

## The class

A rule stated in `CLAUDE.md` and enforced nowhere is an exhortation, and this project's own note on
that ("a gate that pretends otherwise is an exhortation wearing a mechanism's clothes",
`tools/next_step_gate.py`) is about a different rule with the same shape. The declared-`None` rule is
one of the few `CLAUDE.md` rules with no row in its own "Where the rules live" table.
