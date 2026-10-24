**Severity:** RECORDED · **Lane:** delivery (lane 0) · **Direction item:** `refresh-to-head-reads-a-copy-whose-diff-the-target-contains` · **Claim:** released on landing

# refresh_to_head now reads a copy's diff against its own HEAD, and the base holding it is a licence

**Premise re-measured at draw (2026-10-24).** Both cited commits (1c65267f8, 4bc21e920) are on
origin, but the work had not landed by another route. `tools/refresh_to_head.py` was last changed
in September, and the shared checkout was 74 behind origin with 4bc21e920 not an ancestor of HEAD.
So the premise was live.

**The defect.** Every rule in `_judge_copy` compares the copy with `base` as two WHOLE files. A copy
that is a landing's own draft, sitting on a HEAD the trunk has since moved past, still lacks
everything OTHER lanes landed beside it. So against `origin/main` it grades as an ordinary edit
(`NOT_SUPERSEDED`) or a `REPLACEMENT`, and the fast-forward stays refused. What the fast-forward
actually destroys is the copy's diff against HEAD.

**The leg.** `diff_held(head, work, base)`: for every non-equal run of HEAD to the copy, `base`
must hold MORE occurrences of the added run than HEAD does and FEWER of the deleted run. That is
`git log -S`'s own reading, so a copy that just repeats a run HEAD already has is not held. When
the whole diff is held, the verdict is `REFRESHABLE` with `contained=True`, and `judge_copy`'s
whole-file guards (`WHITELIST_GAIN`, `PROSE_GAIN`) are skipped. They read HEAD's own lines that the
trunk reworded as if they were the copy's writing. Preservation and the verified `-S` recovery in
`refresh()` are unchanged.

**Measured on the gas floor's shared-tree copies** (`--base origin/main`, which is what
`background.origin_reconcile` passes). Nine are on disk; the two new files are already gone from
the tree:

| path | before | after |
|---|---|---|
| company/billing/monthly_bill_assembly.py | not_superseded | refreshable (held) |
| company/billing/unread_month_estimate.py | already_at_head | already_at_head |
| company/policy/decision_policy.py | not_superseded | refreshable (held) |
| docs/market_research/unbilled_energy_and_revenue_assurance.md | replacement | refreshable (held) |
| simulation/run_phase4c_on_phase2b.py | not_superseded | refreshable (held) |
| tests/.../test_the_estimate_reads_the_annualised_advance_when_switched_on.py | not_superseded | refreshable (held) |
| tests/company/policy/test_policy_field_consumption.py | refreshable | refreshable (held) |
| tools/read_instruction_arms.py | refreshable | refreshable (old rule) |
| tests/tools/test_read_instruction_arms.py | replacement | **replacement, still refused** |

Six refused before, one after. The one left is correctly refused. That copy is the gas lane's draft
from BEFORE it rebased onto 82f4b20bc (the annualised advance switched on by default), and the
landed tests were rewritten to the default-on ruling. Its tests are a different implementation of
the property, held nowhere on origin. `--base-wins` does not reach it either: the clock says `predates_landing_carrying_some`, and the flag takes only a clean predates. The landed version is the gas lane's final word, so discarding the copy is the expected outcome, but that has to be decided by hand.
Its bytes are at `refs/preserved/gas-floor-shared-copy/test_read_instruction_arms.py`.

**Without the guard skip, `decision_policy.py` refuses as PROSE_GAIN** on three of HEAD's own
comment lines that origin reworded. That was measured before the skip was kept, and it is the
reason the skip exists. `test_a_held_copy_is_not_refused_for_prose_that_is_heads_and_not_its_own`
keys it.

**Controls, every one mutation-proven:**
- leg removed: 2 red
- presence instead of occurrence count: 1 red
- deletion leg removed: 1 red
- guards applied to held copies: 1 red
- blank-line-only diff read as held: 1 red

A `base == "HEAD"` shortcut was drafted and DELETED as an equivalence: the counts already make a
diff against HEAD unholdable by HEAD.

**Not done here:** no byte of the shared tree was written. Refreshing the eight held or refreshable
copies is `origin_reconcile`'s next advance, and that advance is still all-or-nothing, so the one
REPLACEMENT keeps holding it until someone decides it.
