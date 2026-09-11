**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** no_caller_and_never_runs

# A docstring path stops being an edge, and the prose holding seventeen modules up was prose denying them

Pre-registration: `docs/staging/PREREG_WHAT_PRUNING_DOCSTRING_PATH_EDGES_MOVES_2026-09-08.md`,
written before any measurement. Base `656a45f54` (== `origin/main` at draw time).

The second and larger half of `2e4fa042a`. That commit stopped `tools/capability_index` counting a
repo-relative `.py` path written in a `#` COMMENT as a reachability edge, and said in its own body
that docstrings are the same class, left out on purpose so the floor did not move for two reasons
at once. This is that half.

## The premise, re-measured before starting — and one clause of it was spent

The drawn item cited `2e4fa042a` and asked for three things. Two were live; the third was already
done, and not by anyone's judgement.

- **Live.** `_path_references` unioned only `_comment_spans`. Its own docstring said so at line 610.
- **Live.** The 128-module blast radius reproduces exactly.
- **SPENT.** The item said to "delete its held row from `docs/design/orphan_baseline.json`". That
  row was gone four commits later, erased by an unrelated re-freeze. It gets its own finding —
  `SEAT_FINDING_A_HELD_BASELINE_ROW_CANNOT_SURVIVE_A_FREEZE_AND_THE_ONE_PLACED_ON_2026-09-08_WAS_GONE_IN_FOUR_COMMITS_2026-09-08.md`
  — because the mechanism, not the instance, is the story.

## What the prose actually said

197 docstring path edges were pruned. Every one was read, which is the refutation test the
pre-registration promised. **Not one is an invocation.** Two lines mention an invocation verb and
both survive reading as prose. The first is the whole finding in a single line:

> `background/gap_ledger_reconciler.py`, inside `refresh_command`'s docstring:
> *"Found by RUNNING one rather than reading it — `python3 tools/couple_w2_4_c6.py --write-ledger`
> failed in 0.2s, `python3 -m tools.couple_w2_4_c6 --write-ledger` wrote the row in 0.5s."*

The reconciler invokes that tool by `-m dotted.module`, deliberately, because the path form dies on
`ModuleNotFoundError`. **A sentence documenting that the path cannot be run was the edge asserting
that it was.** The same shape holds the drawn item's nominated case:
`company.regulatory.epg_reconciliation_register` was reachable only through docstrings in
`simulation/svt_rates.py` and `simulation/price_cap_enforcement.py` that state the register has no
production caller — and through `company/crm/tpi_commission_desk.py`'s paragraph headed *WHAT THIS
DOOR DOES NOT CARRY*, `company.market.tpi_commission_book` was WIRED.

This is not a curiosity. It is the predictable consequence of the habit `CLAUDE.md` requires: say
where a number came from. Citing `tools/x.py` as provenance silently satisfied the control that
asks whether anything RUNS `tools/x.py` — so an editorial reword, touching no code, could refuse
every lane in the tree under *"THIS COMMIT ADDS WORK THAT NOTHING RUNS"*, naming a module the
refused lane never touched.

## The predictions, and the one that was wrong

| | Prediction | Outcome |
|---|---|---|
| P1 | floor 407 → 535 ±3 | **HELD.** 407 → 535 exactly. +128, −0 |
| P2 | `epg_reconciliation_register` among the newly orphaned | **HELD** |
| P3 | 30–60 of the 128 are company/saas-side and need a fresh ruling | **WRONG — see below** |
| P4 | every pruned edge is a citation, not a call | **HELD.** 197/197 read |
| P5 | 0 unparseable files, so that leg needs a synthetic control | **HELD.** The leg is `test_an_unparseable_caller_keeps_its_docstring_edges_too` |

**P3 was wrong, and it was wrong in the way this project's most expensive shape is always wrong: I
differenced a concept before defining it.** There are two orphan populations here and I treated
them as one.

- `orphan_ratchet.compute` — unreachable from the committed SCHEDULE, transitively. Moves 407 → 535.
  60 of the 128 arrivals are `company.`/`saas.`-side. **That is the number P3 named.**
- `capability_index.orphans` — no production module imports it and no command runs it. This is the
  population the disposition register rules on. Moves 240 → 257. **17 rulings, not 60.**

`company.billing.consumption` is the discriminator: `company.portal.app` imports it, so it is
`wired` to the index and never needs a ruling — but the portal is itself unreachable from any
entrypoint, so it is an orphan to the ratchet. The 43 modules that arrived with no direct pruned
edge are all of this kind. P3's band happened to bracket a real number; it was the wrong number,
and only defining the two populations separated them.

## What landed

One commit, because either half alone is a defect: pruning without freezing refuses every lane,
freezing without pruning records something untrue.

1. `tools/capability_index._docstring_spans` — `ast`, docstring POSITION only. Unioned into
   `_path_references` beside `_comment_spans`.
2. `docs/design/orphan_baseline.json` re-frozen, 407 → 535. **Proved equal to a clean HEAD extract
   plus this one source change** (`git archive HEAD` + the patched module → identical 535-module set,
   symmetric difference empty), rather than trusted from the working tree — the shape that wedged
   every lane on 2026-09-07.
3. 17 rulings in `docs/design/ORPHAN_DISPOSITION_REGISTER.md`, each naming the docstring that held
   it, plus §7 and a correction beside §6's now-dead claim.

## The controls, and what the poison round caught

A PARTITION in `tests/tools/test_capability_index.py`, not a leg per branch. Three legs matter more
than the two obvious ones:

- **`..._ORDINARY_string_literal_is_still_an_edge`** — a rule pruning every string literal passes
  both "a docstring path is not an edge" tests and deletes the subprocess edge model, which is the
  550-orphan fail-open `_import_edges` already records.
- **`..._em_dashes_does_not_swallow_the_code_beneath_it`** — `ast` reports `col_offset` in **bytes**;
  every other offset in the module is in **characters**. They agree in ASCII, which is exactly why
  this would never be noticed, and this repo's docstrings are full of em-dashes. A span ended at the
  raw byte column runs past the closing quotes and prunes the live edge under it.
- **`..._FUNCTION_docstring...`** — both live holders are nested docstrings. A rule reading only
  `ast.get_docstring(tree)` leaves the defect untouched while passing the module-docstring test.

**Two of the four mutations first reported SURVIVED, and both were no-op patches, not blind
controls.** My `str.replace` anchors had been invalidated by an earlier edit in the same script, so
the file was never mutated and the suite was measuring unmodified code. Re-run with
`assert old in s` before writing, all four kill. This is the ambiguity of the word "survived", and
the cheap fix is an applied-assertion on every mutation — the harness cannot tell "the control is
blind" from "your patch did nothing", and it reports them identically.

## What is next

- **The 43 transitive arrivals have a shape worth reading.** `company.portal.app` is the customer
  self-service portal with 34 tests, no importer, and a package with no external consumer at all. It
  is the sole caller of 8 modules. That is a business finding about an unbuilt door, not a harness
  one, and it is now visible for the first time because the prose that hid it was pruned.
- **`_PATH_TOKEN` still cannot see the `-m dotted.module` form.** The reconciler's real edge is
  invisible to this graph in the other direction: it invokes by dotted name and the index only reads
  paths. That is a fail-open of unknown size and it is NOT measured here.
