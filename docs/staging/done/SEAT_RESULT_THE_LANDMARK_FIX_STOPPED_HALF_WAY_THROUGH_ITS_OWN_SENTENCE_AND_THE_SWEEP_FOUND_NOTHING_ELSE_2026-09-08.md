# The landmark fix stopped half way through its own sentence, and the sweep found nothing else

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Lane 0 delivery, 2026-09-08.** Claim:
`a-payload-string-composed-into-two-regions-is-unverifiable-where-it-is-written`.

RECORDED rather than LATENT: the live falsehood this names is closed in this same commit, is on
the published page as of this commit, and the class is closed by a mutation-proven sweep over the
whole site rather than by a rung on one page.

## The drawn direction, and what it predicted

> *"Sweep `site/` for other feed strings composed into more than one page region, and judge each
> one's `here`-relative prose the way
> `tests/tools/test_generate_value_arms_data.py::test_a_sentence_pointing_at_the_band_table_is_true_from_EVERY_region_it_renders_in`
> now judges the band-table pointers. `composition.why_not_readable` is unlikely to be the only
> payload string with two homes — `_current_world_clause` composes several blocks into the headline
> that their own panels also render, and any of them carrying above/below/here prose has the same
> defect by construction."*

The prediction was right, and the instance it did not name is the sharper one: the defect was not
in a *neighbouring* producer, it was in the second half of the sentence the earlier fix had already
been applied to.

## What the sweep found

**One live falsehood, and it was in the fix's own sentence.** Hours before this turn,
`_redraw_band_clause` was given a LANDMARK for the table it points at — *"the band table directly
below this headline"* — precisely because the sentence has more homes than its producer can know.
The very next clause still read *"the FIGURE above sits {where} the centre of its own family"*,
which is a claim about wherever it happens to render.

That sentence has three homes by construction, and `_leg_clause` composes it into `#arms-headline`
**once per leg**, all inside one 4,013-character paragraph. On the publish this turn began from:

| home | what "the figure above" resolved to | what the sentence claimed |
|---|---|---|
| `.current_world.redraw_band` → `.headline` | £17,739, the whole advantage | sits BELOW the centre of £17,262–£20,002 — true |
| `.current_world.selection_leg.redraw_band` → `.headline` | £17,739, still — it is the last figure a reader passed | sits ABOVE the centre of **−£3,075–£1,200** |
| `.current_world.level_leg.redraw_band` → `.headline` | £17,739, still | sits BELOW the centre of £18,582–£20,337 |

The selection-leg row is the falsehood. The figure it is placing is £270; the figure a reader
meets above it is £17,739; and the family it names spans −£3,075 to £1,200, which £17,739 is
nowhere near. Nothing was red, for the same reason nothing was red about the first half: **every
control over that sentence asked whether it named the band table, and none asked what "above" was
measured from.**

**Nothing else in the whole of `site/`.** 2,057 published strings have more than one home across
130 JSON artefacts under `site/`, and after the fix above, zero of them carry a `here`-relative
pointer. `composition.why_not_readable` was not the only string with two homes — it was one of
2,057 — but it and `redraw_band` were the only two that pointed.

## What landed

1. **`tools/generate_value_arms_data._redraw_band_clause`** — `"the figure above"` → `"the
   published draw"`. A NAME, not a direction: it is the band table's own column header for exactly
   this quantity, so it means the same thing from every home the sentence has or gains. The
   docstring carries why, beside the claim.

2. **`site/data/value_arms.json` republished.** The producer had been correct since earlier on
   2026-09-08 and the feed still carried the *retired* recital, so the fix had reached no reader.
   The regeneration moves no figure — ten leaves of 1,269 differ, and they are the two band
   sentences, the headline they compose into, `generated_at` and the publishing-tree commit.

3. **`site/test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer.py`** —
   the class. Homes are DERIVED from the published bytes (a string at two paths, or inside a longer
   string at another path), so a producer that gains a home gains it here with nobody editing a
   list. A direction word is judged only when paired with a page element, so `"below the centre"`
   is untouched; an anchored direction (`"below this headline"`) is a landmark and passes; an
   unanchored one, or one anchored to `"this section"`, reds; and a direction beside a page element
   in words the classifier does not read reds as UNCLASSIFIED rather than passing on silence.

## R15 — poison round, run and reverted

Run **before** the mutation battery, because "survived" means two opposite things.

* Restore `"the figure above sits {where} the centre"` to `_redraw_band_clause` and republish →
  the sweep reds with 4 defects over 2 strings, naming `.headline`, `.current_world.redraw_band`
  and `.current_world.selection_leg.*` among the homes. **Reachable.**
* With that poison live, drop the containment leg from `_strings_with_more_than_one_home` → one of
  the two goes green. The survivor is a verbatim repeat across the whole advantage and the level
  leg; the **selection** leg's copy — the one that was actually false — is caught only by
  containment, because its second home is a longer string that folded the clause in. That is the
  exact shape the band-table defect had, so the containment leg is what this class turns on.
* The judge is poisoned on both sides in
  `test_MUTATION_a_here_relative_pointer_is_CAUGHT_and_a_landmark_is_NOT`: the retired wording is
  caught *as a misdirection and not as an unknown phrase*; both live landmark wordings pass; an
  ordinary numeric comparison passes; and an unregistered phrasing reds fail-closed.

The sweep also carries its own witness legs — ≥50 feeds read and ≥100 multi-home strings found —
because "no multi-home string points" is satisfied by finding no multi-home strings at all, which
is what a broken derivation, an empty glob and a renamed feed directory all look like.

## What is left open, and it is not this lane's

* **`_current_world_contrast` authors `"The figure above is a single realisation"`** into
  `verdict_withheld_because`. That field has one home and renders **nowhere** on the capabilities
  door — `redrawBand` collects it as `withheld:` and never prints it — so it is out of this
  control's scope by construction and is not a live falsehood. It is a published field no reader
  can reach, which is a different finding.
* **The door authors `"how far the figure above moves"`** in `#arms-redraw`'s NOT RE-DRAWN
  fallback, rendered inside a table row where the figure is in the same row to the *left*. It is
  page-authored rather than a feed string, so this sweep does not see it, and it is reachable only
  when `verdict_stability.why_not` is absent. Site lane.
