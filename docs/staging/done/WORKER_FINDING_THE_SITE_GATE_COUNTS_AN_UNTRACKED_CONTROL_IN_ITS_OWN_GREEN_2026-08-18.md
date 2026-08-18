# FINDING — the site gate counts an untracked control in its own green, and two committed records cite that control as coverage a clone does not have

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** DISCHARGED AT THE CLASS for the site lane (`site/test_the_site_lane_runs_no_untracked_control.py`, 8b53a3517); the `tests/` half QUEUED, deliberately not built — see "What is left open" below

**Atom:** `H27_payment_belief_gap` (self-refill 2→3 HARDEN draw, Expert Hour #35, 2026-08-18)
**Class:** `uncommitted_and_orphaned_work` — consolidates as a member of
`docs/staging/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` (same lane, `H_harness`)

## The observation, `observed-with-evidence`

`site/proof/test_the_committed_generator_reproduces_the_published_door.py` had been on disk
since **2026-08-15 06:34**, was collected and GREEN on every `pytest site/` run for three
days, and existed in **no commit on any ref**:

    $ git log --all -- site/proof/test_the_committed_generator_reproduces_the_published_door.py
    (no output)
    $ git ls-files --error-unmatch site/proof/test_the_committed_generator_reproduces_the_published_door.py
    error: pathspec ... did not match any file(s) known to git
    $ git check-ignore -v site/proof/test_the_committed_generator_reproduces_the_published_door.py
    (no output — not ignored, so `--others` would have listed it, and nothing was looking)

    $ python3 -m pytest site/proof/test_the_committed_generator_reproduces_the_published_door.py -q
    4 passed in 1.50s

**Two committed records rested on it while it did not exist.**

1. `docs/staging/done/WORKER_FINDING_THE_PUBLISHED_DOOR_WAS_GENERATED_FROM_AN_UNCOMMITTED_TREE_2026-08-15.md`
   is filed **"DISCHARGED in the tick that found it"** and names that path **first** in its
   `**Discharged:**` line — a finding about an uncommitted artefact, discharged by an
   uncommitted falsifier.
2. H27 Expert Hour #34's shipped tripwire
   (`site/proof/test_the_published_door_reproduces_its_ledger.py`, commit `c7a1fdab0`,
   2026-08-18) cites it **by name** as the reason its own subject partition is safe: *"the
   site-lane control in `test_the_committed_generator_reproduces_the_published_door.py`
   compares the artefact with the GENERATOR and excludes the ledger as a subject on
   purpose."* The committed justification for one control's scope pointed at a file no clone
   of this repository contains.

**The irony is the reason this is a class defect and not a slip.** The missing file's entire
purpose is to enforce CLAUDE.md's IaC wall — *"no behaviour-determining state lives outside
the readable repo; reconstruct-from-repo-alone is the test"* — against the public Proof door.
It was itself behaviour-determining state outside the readable repo.

## Why nothing was red — a property of the gate, not an oversight

`tools/site_lane_gate.py` runs `pytest site/`, and **pytest collects from the working tree**.
An untracked green test is therefore indistinguishable from a tracked green test at the only
moment anyone looks: it is collected, it passes, it is counted, and the gate prints
`[site-lane] ✓ site tests green`. Every existing site control asserts something about a
rendered door; not one asked whether the controls themselves are things the repository has.
The assurance the gate produced was real on exactly one machine.

This is the same shape as the already-filed
`WORKER_FINDING_THE_SITE_LANE_GATES_THE_WORKING_TREE_NOT_THE_COMMIT_2026-08-13.md`, one level
in: that one is about the *subject* the gate judges, this one is about the *judges themselves*.

## What was built (R10 — the class, not the instance)

- `5bd74ff48` — the repair: the three-day-old control landed. R15 both ways against **real
  history, not a fixture**: RED at `c47221060` (2 of its 4 tests fail — the orphaned-key test
  on `basis_audit_ran`/`basis_finding_count`/`basis_findings`, and the emptied-field test on
  `company_name`/`normalisation`/`raw_gap_is`/`world_name`, 13 of 14 rows filled on that
  tree's door and 0 from that tree's generator); GREEN at HEAD (4 passed).
- `8b53a3517` — the class control: `site/test_the_site_lane_runs_no_untracked_control.py`.
  Two subjects, neither derived from the other — the **filesystem** walked directly (so a
  `.gitignore`d control is in the population, deliberately stronger than
  `git ls-files --others --exclude-standard`) and **git's index** (what the commit being made
  will carry). Population 66 files: `test_*.py`, `conftest.py`, and the `*.mjs` node render
  harnesses the door tests spawn.

**R15 both ways, and four mutations each proven to PASS on the shipped defect** (measured
2026-08-18 in an isolated worktree, defect restored):

| mutation | shape | mutant on the shipped defect |
| --- | --- | --- |
| both subjects read from `git ls-files` | TAUTOLOGY | **passed** |
| vacuity floor removed + walk root broken | FAIL-OPEN | **passed** |
| `OSError` swallowed into the disk set, `git` absent from `PATH` | FAIL-SILENT | **passed** |
| non-zero `git` exit swallowed the same way | FAIL-SILENT | **passed** |

Plus the ignored-file case measured directly: a tracked control de-indexed and `.gitignore`d
is invisible to `git ls-files --others --exclude-standard` (0 hits) and this control names it.

`pytest site/`: **776 passed, 8 skipped** (775 passed / 1 failed with the control red before
the repair landed). The control is deliberately **not** in the same commit as the repair that
greens it.

## What is left open, stated rather than implied

Ten untracked `tests/**/test_*.py` were on disk when this was written
(`test_live_payment_triad_is_the_only_bridge`, `test_producer_starvation_draw`,
`test_dd_review_seam`, `test_clv_margin_basis`, `test_dwelling_records`,
`test_policy_cost_coverage`, `test_the_dwelling_record_is_the_worlds`,
`test_the_worlds_dwelling_is_drawn_not_believed`, `test_derived_basis_parentage_gate`,
`test_no_orphan_published_customer_artefacts`), all timestamped 2026-08-17 — other lanes'
live in-flight work on a shared tree, where untracked-at-this-instant is normal and
transient. The `tests/` publish gate collects from the working tree too, so the same
fail-open exists there.

It is **not** built here. A repo-wide version would be born red on another lane's
uncommitted work and wedge a shared gate on a condition this atom cannot fix — the exact
sequencing problem H27 Expert Hour #33 recorded when it declined to ship the door-vs-ledger
tripwire, and #34 then showed had a landable form. A control that must wedge a shared gate to
be honest is a sequencing problem, not a reason to weaken the half that **can** be honest
today.

The honest `tests/` subject is not "untracked at this instant" — it is **"untracked and cited
by a committed record as a discharge or as covered scope"**, which is what actually happened
here and is checkable without racing another lane's editor. That is the next build.

## Why the level does not move

`H27_payment_belief_gap` stays at `level_current: 2`. This was a HARDEN pass working from the
build's own memory, not the fresh cold-eyes Expert Hour that Hour #31 pre-committed as the
promotion condition, and it ends with a real finding either way. Per-Hour defect rate on this
instrument remains 1.0.
