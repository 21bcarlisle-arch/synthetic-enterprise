# BRAND_RULES.md — load before generating any Poesys visual surface

Short, imperative, testable. The full rationale is `docs/design/BRAND_CONSTITUTION.md`; this
file is the operational checklist an agent obeys **before** it emits a site page, chart, bill
PDF, report, board pack, deck, digest, or NTFY. Colour/type/spacing values live in exactly one
place: `site/brand/tokens.json`. Do not hardcode a value that a token already names.
Enforced by `tests/tools/test_brand_compliance.py` (`python3 -m pytest tests/tools/test_brand_compliance.py`).

## Ground: light by default, dark as a sparing accent (BRAND_CONSTITUTION.md §3a — non-negotiable)

**Born light.** The DEFAULT ground for every surface — site page, document, export, chart,
board pack, deck — is **black on white**: `background:var(--surface-base)` (white),
`color:var(--ink-base)` (structural black). Use `var(--surface-sunken)` (grey-05) for recessed
backdrops. Never set a page's base/`body` background to a dark colour.

**Dark is an ACCENT, used sparingly, for impact only** — the named `var(--surface-accent-dark)`
role (black ground, `var(--ink-on-accent)` white). Legitimate: ONE hero moment, a single
statement panel, a deliberate full-bleed break, a headline figure. It is punctuation, not
paper. **If dark is the base of a page it has become a theme — a compliance defect.** The
canonical example of correct sparing use is the `.term` terminal block in
`site/brand/proof.html` / the §7 exemplar: one small black panel on an otherwise white page.
Enforced: `tools/brand_compliance.base_surface_is_dark` FAILS a page whose base surface is dark
(mutation-tested — a synthetic dark-base page fails, a light page with a sparing dark accent
passes).

## The 6 laws (BRAND_CONSTITUTION.md §4 — non-negotiable)

1. **Colour is information, never decoration.** If it is coloured, it is a defined status or a
   named data category. Everything else is black, white, or grey.
2. **Bright = live/current. Soft = historical, backgrounds, fills, projections.**
3. **Soft colours never appear as text or a thin line.** Soft is a fill behind black text only
   (pastel-on-white fails contrast). Text and hairlines are black, grey, or a bright status.
4. **One typeface.** A single neo-grotesque sans (token `font.family.house`). Hierarchy comes
   from weight, size and space — never a second face, never ornament, never a monospace second
   family. The glyph grammar carries the technical flavour.
5. **Glyphs are information, never decoration** (§6 below). Six glyphs is the ceiling. Each has
   exactly one meaning, everywhere, forever. A `~` that ever means anything but "estimated"
   destroys the grammar.
6. **Type-only identity.** Wordmark is lowercase `poesys.` — with the full stop — in the house
   face, black (white on black). No symbol, no drawn logo. Tiny marks (favicon/avatar): solid
   black square, white lowercase `p`, same face.

## BRAG palette + status semantics (§3)

- Four status colours, each **bright** + **soft** (12 status values), plus black/white/greys.
  Values come from `site/brand/tokens.json` only — never write a hex literal on a surface.
- **blue = verified done** (earned: expert-hour-passed / at target, never self-declared).
- **green = on track / in build.**
- **amber = at risk / provisional / estimated.**
- **red = blocked / failing.**
- Greys are tints of black for hairlines and secondary text only — never a status.

## Glyph grammar (§6 — six characters, held absolutely)

Native house-face characters. No image assets. They must survive in plain text (NTFY, digest,
commit message, markdown) so status reads without colour.

| Glyph | Name      | The only meaning                                        | Colour twin |
|-------|-----------|---------------------------------------------------------|-------------|
| `.`   | full stop | Done. Verified, final, closed. The wordmark's own mark. | blue        |
| `_`   | cursor    | In build. Live now, being written, on track.            | green       |
| `~`   | tilde     | Estimated, provisional, approximate.                    | amber       |
| `!`   | bang      | Blocked, failing, needs attention.                      | red         |
| `>`   | prompt    | Action, go, next. Links, CTAs, instructions.            | —           |
| `//`  | comment   | The working: basis, provenance, clock labels.           | —           |

Canonical plain-text status line: `billing . | trading _ | gas read ~ | settlement !`

Ratified functional uses: provisional headline figures carry a leading `~` (`~£1,505,250`);
every basis/clock annotation is a `//` comment; estimated meter reads are `~ ESTIMATED` with `~`
on the consumption figure; CTAs end `>`. (Every published figure still carries its clock — R14.)

## Before you emit a surface — checklist

- [ ] Base/`body` surface is light — `var(--surface-base)` + `var(--ink-base)`; dark only as a
      sparing `var(--surface-accent-dark)` accent, never the page base. (`base_surface_is_dark` = False)
- [ ] Every colour is a `var(--…)` / token reference, not a hex literal. (`find_raw_hex` = 0)
- [ ] No soft colour used as `color:`, border, outline or stroke. (`find_soft_as_text` = 0)
- [ ] Any coloured thing is a status or a named data category (law 1); everything else B/W/grey.
- [ ] One typeface; hierarchy via weight/size/space (law 4).
- [ ] Wordmark is `poesys.` with the stop, house face (law 6).
- [ ] Each glyph carries its single meaning (§6); status also reads in plain text.
- [ ] Every financial figure carries its clock/basis; provisional figures lead with `~` (R14).
- [ ] Copy is plain English, precise, no superlatives — the honesty conventions ARE the voice.

## Canonical reference — copy, do not reinterpret

`site/brand/exemplar.html` is the ratified §7 mock (front door + customer bill + glyph grammar),
preserved verbatim. Generation copies from it. When in doubt about a pattern (BRAG chip, figure
block with `//` clock, `~ ESTIMATED` read, glyph table), lift it from the exemplar.

## Open dial — do not self-decide

The self-hosted typeface (if any) that would replace the system Helvetica stack is a **director
dial** (§9), same law as an R13 curriculum change: the agent may *propose*, only the director
ratifies. Until then the house token stays the system stack. Any palette value change is
likewise director-ratified only — never tune a brand value autonomously.
