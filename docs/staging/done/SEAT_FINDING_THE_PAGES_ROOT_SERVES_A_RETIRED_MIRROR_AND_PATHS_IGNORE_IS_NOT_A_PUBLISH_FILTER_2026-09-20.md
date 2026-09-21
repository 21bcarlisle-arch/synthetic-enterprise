# The Pages root serves a retired mirror, and `paths-ignore` was read as a publish filter

**Severity:** BLOCKING
**Lane:** H_harness

BLOCKING is lane-scoped. It blocks here because a control in this lane
(`tools/startup_anchor_freshness._UNPUBLISHED`) asserts that a set of directories cannot be
reached by a reader, the GitHub Pages workflow serves every one of them, and anything reasoning
about what this project publishes from that list will be wrong in the same direction.

Claim: `docs-shadow-serves-ten-zero-pound-rows-from-a-retired-generator`. Drawn 2026-09-20 as
LANE 0 DELIVERY.

## Class registration

Belongs to `figures_on_a_superseded_clock`.

Declared rather than left to the title regex, which routes this document to
`measurements_that_mirror` on the word *mirror* — a false positive of the noun, exactly the shape
that module's own comment records for *blind*. The word here is the GitHub Pages **mirror**, a
deployment arrangement; nothing in this finding is an instrument reading its own subject back.

The family is the superseded clock, and this is its purest instance yet: a net margin of
£1,529,289, a treasury, an enterprise value and ten Run History rows, all stamped
`Generated: 2026-08-20T06:59:11Z | Run a5bfec712…`, served from a public root beside a live site
publishing the current figures — two clocks, one of which cannot be wound, because the only thing
that could wind it was switched off. The existing members are a frozen scalar beside re-summed
rows; this is a frozen PAGE beside a live one, which is the same defect with a larger subject.

## PREMISE RE-MEASURED AT DRAW TIME — STANDING, NOT SPENT

The draw warned that all three cited commits (`cd4da3219`, `d066d3534`, `03dd8c49e`) are already
ancestors of `origin/main` and the work may have landed by another route. It had not. Measured in
this worktree at `f8bcab881`, every leg of the item is still true:

| Leg the item asserts | Measured | Verdict |
|---|---|---|
| `docs/shadow/` exists, 5 pages | `index.html` + `{customers,project,sim,supplier}/index.html` | STANDS |
| GitHub Pages uploads `docs/` whole | `.github/workflows/github-pages.yml` → `upload-pages-artifact` with `path: docs` | STANDS |
| `docs/shadow/index.html` links `/shadow/project/` | `href="/shadow/project/"` in the nav of all five | STANDS |
| Ten Run History rows read blank/blank/£0 | exactly ten `<tr><td></td><td></td><td><span class="pos">&pound;0</span></td></tr>` | STANDS |
| Frozen at `cd4da3219` (2026-08-20) | `git log -- docs/shadow/` newest is `cd4da3219`; page stamp `Generated: 2026-08-20T06:59:11Z` | STANDS |
| The generator is retired from the cycle | `background/process_run_complete.py` — the shadow step is a bare `pass` under its 2026-08-20 retirement comment | STANDS |
| `site/shadow/` is gone (clean root) | `site/shadow` does not exist | STANDS |

The duplicate-claim warning names `docs-shadow-serves-ten-zero-pound-rows-from-a-retired-generator`
— **this very id**, held with `paths: []`. It is this item, claimed and undelivered, not a rival
under another name. No disposition is owed; the work is owed. Carried on.

## WHAT IS ACTUALLY LIVE, AND IT IS WORSE THAN THE TEN £0 ROWS

The item's headline is the ten blank/blank/£0 Run History rows on `/shadow/project/`. Reading the
other four pages, those rows are the *least* of it. `docs/shadow/index.html` is a full internal P&L
served at a public root, frozen on 2026-08-20:

- Net Margin £1,529,289 · Gross Margin £6,471,175 · Enterprise Value £1,283,770
- Treasury Start £2,467,568 → End £3,905,403 · Customer Credit Held £4,101
- a ten-row year-by-year gross/net/treasury/bills/avg-shock table
- an Executive Summary block quoting "Hedging cost £4,256,943 vs going naked (85% mandate price)"
- `Phase RX | 26731 tests | 505 modules` — the test count is 10,107 behind the real one

Every figure carries `Generated: 2026-08-20T06:59:11Z | Run a5bfec712465079b7c376c04af8a8da9bbe7f2f9`.
Nothing can move them: the only writer was switched off a month ago. A stamped figure that cannot
change is not stale, it is a **frozen assertion** — it says "as of 2026-08-20" and will keep saying
it forever, which reads to any visitor as a current position.

## THE SECOND DEFECT, AND IT IS THE ONE THAT KEPT ANYONE FROM LOOKING

`paths-ignore` in `github-pages.yml` is a **trigger** filter. It decides whether the workflow RUNS
on a given push. The upload step is `path: docs` — the **whole tree**, unfiltered. So a push
touching `docs/PROJECT_OVERVIEW.md` fires the workflow and uploads `docs/observability/`,
`docs/staging/`, `docs/design/`, `docs/state/`, `docs/instructions/`, `docs/review_gates/` with it.

Three places in the repo read `paths-ignore` as if it were a publish filter:

1. The workflow's own comment calls the excluded directories "the clearly-non-served, clearly
   high-churn directories". They are non-*triggering*, not non-served.
2. `tools/startup_anchor_freshness.py:228` — `_UNPUBLISHED`, commented *"Directories the GitHub
   Pages workflow's `paths-ignore` excludes… A path under these is not published, so a reader
   cannot be sent to it."* It is used at line 316 to **skip** those paths when deciding what a
   reader can be sent to.
3. **The same module already states the truth at line 39**: *"The GitHub Pages mirror uploads the
   whole `docs/` tree as a single artefact, so a `docs/status/` publish restamps every file in the
   mirror."* One file, two load-bearing claims, opposite, 189 lines apart — and the wrong one is
   the one wired into a control.

This is why `docs/shadow/` went a month without anyone checking it: the module whose job is to know
what a reader can reach had it on an allowlist of things readers supposedly cannot.

**This finding does not fix that.** Narrowing the Pages upload is a surface decision about what the
company publishes, not a delivery call, and it needs the director. It is filed here as its own
subject. What this landing does fix is the `docs/shadow/` entry in `_UNPUBLISHED` (the path is gone,
so the entry would rot into a name for nothing) and the false rationale sentence attached to it.

## WHY DELETION, NOT REGENERATION

The alternative — rewire the generator so the pages regenerate — acts directly against a landed
director ruling. `03dd8c49e` (2026-08-20), verbatim in its commit message:

> "I don't want hidden pages, and I don't want the maintenance and link burden that comes with
> them... no permanent limbo, no page kept because deleting it feels risky."

and the retirement comment the same ruling left in `process_run_complete.py`:

> "the `/shadow/` mirror is deleted and this call put it straight back. It was an INTERNAL surface
> that was nonetheless published at a second root on the public site, carrying the full internal
> vocabulary — exactly the hidden page the ruling is about."

`d066d3534` (2026-09-20) repaired `generate_shadow_html.build_project` so it renders the real
`git_hash`/`generated_at`/`net_margin_gbp`. That repair is correct and is **inert on the published
bytes**, because the generator it repaired is not called. The repair is left standing; it is not
this item's subject, and deleting a generator that acquired a control this morning is a separate
judgement.

The item's author declined to take the deletion, reasoning that "a public-surface deletion is the
wrong direction for a seat to be decisive in without asking". I disagree and am acting. The four
reserved classes are money, real people, an irretractable public claim, and safety.
**Removing a wrong claim is the opposite of the third**: what is irretractable here is leaving
£1.5m of frozen internal figures served under Poesys's name. The deletion is reversible by
`git revert`, and the director has already ruled on exactly this surface, by name, in writing.
Notified, not asked.

## WHAT LANDS

1. `docs/shadow/` deleted — five pages.
2. `tools/mirror_github_pages.py` — the `site/shadow/` → `docs/shadow/` half removed. Left standing
   as a no-op it is a loaded gun: the moment anything recreates `site/shadow/`, the publish cycle
   copies it straight back to the public root. The state-JSON half is live and stays.
3. `background/process_run_complete.py` — the `site_shadow` and `docs_shadow` blocks removed from
   the publish commit's file list. Both were already dead (`site/shadow` gone; `docs/shadow` about
   to be), and a path list that stages a directory is how it comes back.
4. `tools/publish_surface_gate.py` — `docs/shadow/` dropped from `PUBLISH_SURFACE_ROOTS`.
5. `tools/startup_anchor_freshness.py` — `docs/shadow/` dropped from `_UNPUBLISHED`; the false
   "`paths-ignore` means not published" rationale replaced with what the workflow actually does,
   pointing at this finding.
6. A control: `tests/tools/test_a_stamped_page_at_the_pages_root_has_a_live_writer.py`.

## THE CONTROL, AND WHY IT IS KEYED TO THE PROPERTY

The property that failed is **a generated page outliving its generator**. Not "docs/shadow does not
exist" — that is today's answer, and a control pinned to it stays green while the same defect lands
under a different directory tomorrow.

So: derive the Pages upload root from the workflow's own `path:` value; take every `*.html` under
it; keep those carrying a machine freshness stamp (`Generated: <ISO>` / `Run <sha>`); and refuse any
whose directory no module under `tools/`/`background/` still names as an output.

A static hand-written page (`docs/status/index.html`, the two `docs/site_templates/knowledge/`
templates) carries no stamp and is correctly out of scope — it makes no claim about when it was
true, so it cannot be frozen against one.

**Non-vacuity is the whole risk here.** Measured: after this landing the live stamped population
under `docs/` is **zero**, so leg 1 alone is the textbook FAIL-OPEN — an empty evidence set reading
as no complaint. Leg 2 runs the identical predicate over a fixture tree holding one stamped orphan
and asserts it is RETURNED. The predicate is therefore proven able to fire whatever the live tree
contains, and the control cannot be silenced by the population going empty.

**Pre-registered before running the gate chain** (answer not known at time of writing): I predict
the deletion reds nothing outside the five files listed above plus
`tests/tools/test_mirror_github_pages.py`, whose four cases monkeypatch `SITE_SHADOW`/`DOCS_SHADOW`
and two of which test the shadow copy directly. I predict `tests/tools/test_generate_shadow_html.py`
and `tests/tools/test_the_shadow_run_history_renderer_reads_keys_the_producer_writes.py` stay green,
because both drive the generator against fixtures and neither reads `docs/shadow/`. Recorded here
before measuring; the result is appended below the line, right or wrong.

---

### RESULT (appended after the gate chain ran)

**The prediction was half right, and the half it got wrong is the more useful half.**

RIGHT: `tests/tools/test_generate_shadow_html.py` and
`tests/tools/test_the_shadow_run_history_renderer_reads_keys_the_producer_writes.py` both stayed
green (41 passed across the adjacent suites). Both drive the generator against fixtures; neither
reads `docs/shadow/`. The generator and this morning's repair to it are untouched by this landing.

WRONG, in the direction of understating: I predicted the deletion would red nothing beyond the
listed files and the mirror's own tests. It also red
`tests/background/test_tree_divergence.py::test_generated_artefacts_are_excluded`, whose fixture
asserted `td._is_generated("docs/shadow/index.html")`. **That leg was asserting the stale claim
as correct.** The tuple it pins means "the machine rewrites this every cycle"; the writer had been
switched off for a month, so the test had been pinning a falsehood since 2026-08-20 and would have
gone on doing so. Repaired to `docs/state/customer_sample.json`, which the mirror genuinely does
still rewrite. Three further references were found the same way and cleaned:
`background/naive_organ._BUCKET_KEYWORDS`, `tools/publish_surface_gate.PUBLISH_SURFACE_ROOTS`, and
a `process_run_complete` log line still announcing a copy that had not happened for a month.

**THE CONTROL SHIPPED GREEN TWICE BEFORE IT COULD FAIL, and only the real mutation caught it.**
This is the part worth carrying forward. `frozen_pages()` passed its own fixture from the first
draft. Restoring the actual `docs/shadow/project/index.html` into the worktree and re-running found
two independent fail-opens in it:

1. **The root cleared everything.** Candidate ancestors included the Pages root itself, so any
   source mentioning `docs/` anywhere satisfied every page under it at once. The predicate returned
   `[]` for a tree with the orphan sitting in it.
2. **Prose counted as a writer.** The plain text search matched `process_run_complete`'s log line
   *"Mirrored {} file(s) to docs/shadow + docs/state for GitHub Pages"* — a sentence describing a
   copy that had stopped happening. Worse, it matched the tombstone COMMENTS this very repair had
   just written. **The control would have been silenced by the prose announcing the defect it
   watches for.** Fixed by deriving declarations from the AST (non-docstring literals and `/`
   chains) and requiring a path-shaped literal, so comments and sentences cannot vote.

Both survived a fixture and died to a real input. *Print the numbers at real inputs before you ship
the formula* — it earned its keep twice in one hour, and neither would have been caught by more
thinking about the fixture.

After the repair, with the page restored the control names it exactly
(`['docs/shadow/project/index.html']`) and with the page gone it is green. The known one-sidedness
— a path-shaped string in a list that writes nothing still reads as a writer — is stated in the
module docstring rather than left for the next reader to discover by trusting it.

**Gates run:** `finding_classes --check` PASS (after declaring the class and re-rendering),
`finding_severity` PASS, `ruff --select I001` PASS, `tests/design/` + static quality ratchet 161
passed, `substring_source_scan_census.check` clean, and 44 + 41 passed across every suite touching
the edited modules.

**Partial closure of this class's own Disposition.** The register's standing decision says the
closing mechanism is extending *every financial figure carries its clock* "from that generator's
fields to the property". The control landed here does that for one shape of the property — a
published PAGE whose stamp can no longer move — and does it at the Pages root, which the basis
gate never covered. It is not the whole extension and is not claimed as one.

**Left open, deliberately, and it is the bigger subject:** the Pages upload is `path: docs`, whole.
`docs/observability/`, `docs/staging/`, `docs/design/`, `docs/state/`, `docs/instructions/` and
`docs/review_gates/` are all served, and three places in the repo read `paths-ignore` as if they
were not. Narrowing what the company publishes is the director's call, not a delivery one.
