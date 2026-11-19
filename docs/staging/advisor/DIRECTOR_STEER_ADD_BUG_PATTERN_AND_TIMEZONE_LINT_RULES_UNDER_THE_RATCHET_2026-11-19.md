**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Add two lint rule families, bug patterns and timezone-naive dates, under the existing ratchet

**Type:** STEER, through the advisor channel. Finish what you're doing first, then take this next. It is a small backlog item, ranked in Friday's balance review.

## The director's words (chat, Thu 19 Nov, verbatim)

- 14:03: "Do we or should we have lint rules"
- 14:09: "On the lint? Add the 2 you suggested"

The two the advisor suggested, from a quick count with a newer ruff (0.16.9) than the pinned one, so the figures are rough:

1. **Bug patterns (flake8-bugbear, ruff `B`).** Rules that catch real defects, not style. Examples: a loop variable captured late in a closure (about 65 hits), mutable default arguments, `raise` inside `except` without `from`, and `zip` without `strict`.
2. **Timezone-naive dates (ruff `DTZ`).** Settlement turns on BST and GMT, and this project has had clock-change defects. A naive `datetime` is a defect class, not a style point.

## The problem (the machine owns the design)

- **New code only, through the existing ratchet** (`tests/architecture/test_static_quality_ratchet.py`): no new violations in a changed file, and a shrink-only baseline. No mass clean-up and no bulk `--fix` sweep across lanes.
- **Choose the rules inside each family.** Leave out any that are noise for this codebase, and say why in a line each. Example: `B905` (`zip` strict) has hundreds of hits and may be worth it only where lengths can genuinely differ.
- **The baseline is per ruff version.** Add the families at the pinned version (`requirements.txt`: 0.15.16), and re-freeze the baseline in the same commit.
- **Check whether existing hits are live defects.** The late-binding closures especially: some may already be producing wrong results. Any that change money or a customer outcome are a serious class under the correctness rule. Fix them as a class, not one by one.
- **Do not add style families** (magic numbers, too-many-arguments and the like). The constant-origin test already does the magic-number job better.

## Risk

- **Touches:** `ruff.toml` and the ratchet's frozen baseline.
- **Blast radius:** every lane's commits, through the ratchet.
- **Probable failure mode:** a baseline frozen wrongly, or at the wrong version, reds every lane and names files nobody touched.
- **Mitigation, inline:** freeze and land in one commit at the pinned version. Run the ratchet on a clean worktree of origin before landing. Reverse by reverting the two `select` entries and the baseline.

**Proportionality:** reversible and narrow, so just do it.
