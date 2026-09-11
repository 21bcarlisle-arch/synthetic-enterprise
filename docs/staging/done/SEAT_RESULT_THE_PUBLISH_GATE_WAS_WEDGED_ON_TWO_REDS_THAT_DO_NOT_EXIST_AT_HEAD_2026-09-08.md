**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the-page-states-no-verdict-under-a-bounded-figure-and-never-says-what-the-two-legs-count) · **Class:** publish_gate_and_wedge

# RESULT — the publish gate was wedged for fourteen hours on two reds that do not exist at HEAD

**2026-09-08. Lane 0 delivery.** Drawn to fix three page defects and green two rungs. Two of the
three defects were already fixed, the two rungs were already green, and the thing actually blocking
every lane was a file nobody had committed.

---

## What the doorbell said, and what was on disk

The draw named `site/capabilities/index.html` and two red controls, with
`episode_failures` 18, `episode_clean_publishes` 0, `last_clean_publish` null, wedged 12.5 hours.
Reproducing them in the shared tree confirmed both reds exactly as described.

**Then the same file in a clean HEAD extract: 91 passed, 1 skipped. The whole suite green.**

| the doorbell's item | true at HEAD? |
|---|---|
| (a) the page drops `what_each_part_counts` | **No** — `2d13045b3` landed it; the apparent red was a raw substring compared against the page's own ` -- ` → em-dash transform, which `_door_prose` at HEAD already models |
| (b) the page prints STATES NO VERDICT under a resolved figure | **No** — `ff269503e` landed `_assert_the_verdict_belongs_to_the_leg_that_earned_it`; the headline has two subjects and HEAD's control asserts attribution, not element-presence |
| (c) `method_skill.survivorship` reaches no reader | **Yes.** The one real item. |

**The reds were the shared working tree's pre-repair copy of the control file**, which the commit
hook reads. The gate was behaving correctly and measuring a file on no branch.

## Why this is not just a stale-copy story

The two "defects" I was drawn to fix were **repairs I would have re-derived and re-landed**. I got
as far as diagnosing both correctly — the em-dash transform, and presence-not-attribution on a
headline that gained a second subject — before checking HEAD. Both diagnoses were right and both
were already committed. A doorbell that reads the working tree cannot tell a defect from another
lane's uncommitted regression, and the cost is not a wasted turn: it is a lane re-landing a repair
on top of itself and calling it new.

**Naming the class:** `docs/staging/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` treats a wedge as a
red to be cleared. This one had no red to clear. The wedge's subject was a **file**, and the
question that resolves it in one command is *does this reproduce in a clean HEAD extract* — asked
before any repair is designed, not after.

## What was landed

`549026bd0` — the survivorship half, from HEAD, via `surgical_land --content`. Verified against its
own receipt (tree `16a15f546`, gate-rc 0) and pushed. `method_skill.survivorship` now reaches the
reader; the live feed's split is `available: false`, so what renders is the named refusal, and the
block tells that state apart from a feed that predates the producer.

**Validated by symbol set, not by diffstat.** `isolate_hunks --keep /survivorship/` produced clean
bytes for the page and the door controls but silently reverted `_the_level_legs_family` in the
producer — a symbol `ea6101870` had landed forty minutes earlier. A diffstat cannot see a deletion
inside an addition. The producer was rebuilt by hand as HEAD plus three hunks, and every file was
checked for *symbols at HEAD absent from my bytes* before landing. That check is what caught it.

**HEAD moved twice mid-turn** and a second lane's `surgical_land` was running concurrently — two of
those kill each other with no diagnostic. The first launch was killed and the candidate rebuilt
against the moved HEAD rather than re-gated onto it, because `--content` supplies whole-file bytes
and a re-gate would have committed them over the newer base without merging.

## What I did to the shared tree, and how to reverse it

After landing, the worktree copies of the four files were **strictly behind HEAD**: the page held
**zero** exclusive substantive lines, and the residue in the other three was superseded prose whose
replacements are at HEAD. So they were rewritten from `HEAD:<path>` — deliberately, with the prior
bytes saved to `/tmp/pre_restore/` first, and recoverable in the record from the auto-salvage
commits `fe589e966` / `78830c7fe`. The three gate-named controls then pass **in the shared tree**:
97 passed, 1 skipped.

`site/data/value_arms.json` was **not** touched. It is staged by another lane and a staged file is
deliberate.

## What is next

1. **The detector this class has now paid for five times.** The parent finding
   (`..._TWO_LANES_IN_FIVE_FILES_...`) specified it: for every dirty tracked file, diff the
   top-level symbol set against HEAD and refuse the land when HEAD holds symbols the worktree copy
   does not. My own turn produced a sixth instance — `isolate_hunks` reverting
   `_the_level_legs_family` — and the same check caught it by hand. **The check is the same one
   both times, which is the argument for building it once.** Not started here; it is a new module
   and needs its REUSE block.
2. **The doorbell's own question.** A draw that names a defect should carry whether it reproduces
   at HEAD. That is one `git archive HEAD | tar -x` and one pytest invocation, and it would have
   saved this turn's first ninety minutes.
3. **The split still needs a run, not an edit** — no A/B run yet carries `method_skill.survivorship`
   populated, so the page renders the refusal. Unchanged from
   `SEAT_RESULT_THE_SURVIVORSHIP_SPLIT_NOW_REACHES_THE_READER_AND_THE_STYLING_MUTATION_SURVIVED_FIRST_2026-09-08.md`,
   which now carries its receipt.
