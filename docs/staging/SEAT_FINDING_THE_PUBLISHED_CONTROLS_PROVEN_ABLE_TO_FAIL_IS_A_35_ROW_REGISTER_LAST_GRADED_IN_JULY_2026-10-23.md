**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The published "controls proven able to fail" is a 35-row register last graded on 13 July

**Found by** a cold tech reader of How it's built, 23 Oct 2026: "'33 of 35 controls proven' was last graded 13 Jul, over three months before the page's 23 Oct publish date, so it may be stale."

**What the figure counts.** It is `proof.json`'s `control_killlist`, read from `docs/design/control_registry.json`. That register holds 35 named controls, `last_verified` 2026-07-13, and was last changed on 2026-09-27 (a retirement). Since July the project has written its controls as tests that name their own defect and record a mutation. 2,153 test files are tracked at 63593d115. None of those tests is in the register. So the figure is both stale (three months old) and the wrong population: the stack's "proof the checks work" layer is carried by the tests, not the register.

**What the page does now.** The page prints the figure with its grading date, so it is honest about its own clock, and the figure stays. Nothing has been replaced with a placeholder.

**What would close it.** Define "a control proven able to fail" over the test population: a test that names its defect and records a mutation run in its docstring or in the mutation log. Then count it at publish, beside the register's figure or in place of it. The definition comes first, and the count follows from it. This is also the evidence the control-stack steer (`docs/staging/advisor/DIRECTOR_STEER_SHOW_THE_HARNESS_AS_A_LIVE_CONTROL_STACK_2026-10-23.md`) asks to put on layer 5 ("about 654 test files cite this rule").
