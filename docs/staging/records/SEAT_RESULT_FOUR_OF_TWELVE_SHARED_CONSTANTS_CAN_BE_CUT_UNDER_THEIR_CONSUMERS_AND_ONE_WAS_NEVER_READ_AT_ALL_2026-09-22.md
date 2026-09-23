**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Claim id:** a-shared-canonical-constant-with-three-consumers-and-no-leg-that-reds-when-it-narrows

# RESULT — four of twelve shared constants can be cut under their consumers, and one of them was
# never read by any code at all

**Measured 2026-09-22** on `origin/main` at `d28b3e11f`, in a detached worktree so no mutation ever
touched the shared tree. The commissioning item asked how many siblings are in the state
`_ITEM_PROSE_KEYS` was in that morning. **Twelve constants, twenty-two mutations, eleven red,
eleven green — and the split is DIRECTIONAL.**

## The headline is the asymmetry, not the count

**Narrowing is well guarded: 8 of 12 red. Widening is nearly blind: 3 of 10 red.** Every guard in
this family was written after a NARROWING was observed, so each one reproduces the shape of the
defect that produced it. `_ITEM_PROSE_KEYS` is the clearest case and it is the item's own premise:
the commissioning note says it *"is now covered (0b1898452, 14dc33969)"*, and it is — **in one
direction.** Adding a fifth key leaves all 113 tests green. That matters here specifically, because
the fourth-door finding of the same morning measured what widening this exact tuple does: fold it
into `premise_note` and six live entries acquire a false spent premise. **Widening is the known
expensive direction for this constant and it is the unguarded one.**

This is not an argument for ten more legs. It is one question to ask of a control at the moment it
is written: *the mutation I just proved is the one I had already seen — which is the other one?*

## The premise, re-measured first — and the draw's own note was a false positive

The doorbell reported all three cited commits (`0b1898452`, `14dc33969`, `c9bb7bd34`) already
ancestors of `origin/main` and suggested the item might be spent. **It was not.** Those SHAs are
**completion markers** — the item's `why` says `_ITEM_PROSE_KEYS` *"is now covered"* by them and
asks about its **siblings**, which nothing had touched.

This is exactly the false-positive class
`SEAT_FINDING_A_FOURTH_DOOR_CARRIES_THE_SAME_NARROW_READ...` predicted — with one correction to it.
That finding established the remedy as *keep `premise_note` reading `what + why` and never widen it
to `_ITEM_PROSE_KEYS`*, on the measurement that no **later-field** citation in the live population
is a dependency. True, and the narrowness is still right. **But the defect is not confined to the
later fields:** this item carries its completion markers in `why`, inside the narrow read, and the
note fired anyway. Narrow scope bounds how often this happens; it does not prevent it. The residue
is named at the foot of this note.

## The census

Consumers counted by AST load, not by name match — the three `_PATH_TOKEN` hits in `tools/` are
**rival definitions** of "what a path token is", not consumers of `delivery_lane`'s.

| constant | module | consumers | narrowed | widened |
|---|---|---|---|---|
| `_ITEM_PROSE_KEYS` *(positive control)* | `delivery_lane` | 4 + `direction_path_check` | RED (3) | **GREEN** |
| `_NAMED_PATH` | `delivery_lane` | 1 + `direction_path_check` | RED (7) | RED (1) |
| `_SPENT_TAGS` | `direction_path_check` | 1 | RED (2) | RED (3) |
| `_WRONG_BYTES_TAGS` | `direction_path_check` | 1 | RED (4) | RED (1) |
| `_CHANGE_GOVERNORS` | `delivery_lane` | 3 + `_path_roles`'s importer | RED (1) | **GREEN** |
| `_READ_ONLY_GOVERNORS` | `delivery_lane` | 1 | RED (4) | not run |
| `_MAX_GRADED_PATHS` | `delivery_lane` | 3 | RED (5) | **GREEN** |
| `_REPO_ROOTS` | `delivery_lane` | 1 | RED (8) | **GREEN** |
| **`REQUIRED_FIELDS`** | `seat_continuation` | **0** | **GREEN** | **GREEN** |
| **`NOTHING_TO_LAND`** | `direction_path_check` | 2 + `decisions.jsonl` | **GREEN** (reword) | n/a |
| **`_ARTEFACT_ROOTS`** | `delivery_lane` | 1 | **GREEN** | **GREEN** |
| **`_MAX_STORED_PATHS`** | `direction_path_check` | 1 | **GREEN** | **GREEN** |

`not run` is not a green: `_READ_ONLY_GOVERNORS`' widening was not measured and is the one cell in
this table nobody has looked at.

The positive control matters: the harness detects a red, so a green is a measurement and not a
broken runner. Confirmation counts are the failing-test counts.

## The worst of the four, and it is worse than the shape we went looking for

`seat_continuation.REQUIRED_FIELDS` is **read by nothing but its own error message.** `hand_off`
built a second literal — `{"id": ..., "what": ..., "why": ..., "done_means": ...}` — and validated
*that*; the test proving the refusal works held a **third** copy of the same four names. Three
copies, two load-bearing, and the one the module publishes as its declaration was decorative.
Narrowing it to `("id",)` and widening it with `note` each left **113 tests green**, and no test
anywhere in the tree reads the constant or the message it appears in — so that green is conclusive
for the whole repo, not an artefact of suite selection.

This is the `_ITEM_PROSE_KEYS` defect with an extra turn of the screw. There, one definition was
read by three doors with no guard. Here the definition had **no reader at all** while looking
exactly like the canonical one.

## What landed

* `background/seat_continuation.py` — `hand_off` now derives `missing` from `REQUIRED_FIELDS`, so
  the declaration IS the enforcement. `REQUIRED_FIELDS`' comment records the measurement.
* `tests/background/test_seat_continuation.py::test_EVERY_FIELD_DECLARED_REQUIRED_IS_THE_ONE_THE_WRITER_DEMANDS`
  — keyed to `hand_off`'s **signature** (a parameter with no default is a field the caller must
  supply), never to the constant, which would be the constant vouching for its own value.
  Mutation-proven: narrowing RED, widening RED, and the **composite** — separate literal restored
  *and* constant narrowed, which is the pre-repair code — RED. Restoring the literal alone is
  GREEN and is an **equivalence** at the correct value, not a blind spot.
* `tests/background/test_the_direction_record_is_graded_before_it_is_filed.py::test_A_CLASS_STRING_ALREADY_IN_THE_APPEND_ONLY_RECORD_STAYS_JOINABLE_TO_ITS_VOCABULARY`
  — `delivery_seat._record` writes these class strings into `docs/direction/decisions.jsonl`, which
  is append-only. Every other test refers to the class **by symbol**, so a reword was invisible.
  Mutation-proven: rewording `NOTHING_TO_LAND` RED.

  **The commit gate refuted my first draft of this leg and the correction is the better half of it.**
  The draft walked the live `decisions.jsonl`, asserting the evidence set non-empty before asserting
  the subset. It was green in the shared tree and **RED in the gate's isolated extract**: the one
  live record is another lane's **uncommitted** append, and the COMMITTED store carries zero
  `path_concerns` rows. A control whose evidence exists only in one worktree's dirty bytes is green
  for a reason unrelated to its subject — I wrote the non-empty assertion *against* exactly that
  failure mode and then supplied the evidence from a place the gate cannot see. The observed string
  is now pinned as data, which is legitimate here and only here: the subject is a frozen past write,
  so what a record already says can never change. Re-verified green in a clean extract with zero
  records, and RED on the reword there.

## Residue — named, not closed

1. **`_ARTEFACT_ROOTS` (`delivery_lane`) has no leg.** Narrowing it to `("tools",)` stops
   `_artefacts_naming_claim` reading `docs/staging` — the root where a turn's findings are filed —
   so a seat's filed finding stops being credited to its claim by NAME and falls back to the weaker
   time-attributed reading. That is a silent downgrade of the discriminator `_names_claim_in_field`
   exists to provide. A leg needs an independent witness for where findings live
   (`background/staging_rooms.py` declares it); iterating the tuple would be the tautology.
2. **`_MAX_STORED_PATHS` narrowing is an EQUIVALENCE, not a missing test.** The bound truncates and
   `not_graded` carries the count, so the conservation law holds at any bound — narrowing loses
   detail and tells no lie. What is genuinely unguarded is the two properties the docstring claims:
   that truncation is never silent (`len(paths) + not_graded == total`, with truncation proven
   reachable), and that the stored bound never exceeds `_MAX_GRADED_PATHS`. Neither has a leg.
3. **The widening direction is unguarded across the family, including on `_ITEM_PROSE_KEYS`.** Seven
   of ten measured widenings are green. This is not seven atoms of work: it is one question to ask
   when writing any control over a shared definition, and the finding above is where it is recorded.
4. **`premise_note` fires on completion markers inside `what`/`why`.** Measured above on this very
   item. The narrow field read does not prevent it; a shape test on the citing sentence would
   (`is now covered by X` is not `depends on X`), and the fourth-door finding's own remedy —
   *do not widen* — remains correct and does not reach this.

## Method

`~/.cache/seat_census/{census2,mutate}.py`. Each mutation applied in a detached worktree at
`origin/main`, suite of the seven files that exercise all three modules' doors (113 tests, ~9s),
reverted after every run. Greens re-confirmed by grep over the whole tree for any reader of the
constant, so a green is not a suite-selection artefact.
