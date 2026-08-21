**Severity:** RECORDED · **Lane:** H_harness

**Discharged:** `tests/background/test_publish_provenance_banner_adoption.py::test_the_typed_five_were_blind_to_nineteen_pages`, `tests/background/test_publish_provenance_banner_adoption.py::test_a_live_data_page_without_the_banner_is_reported`, `tests/background/test_publish_provenance_banner_adoption.py::test_a_site_with_no_live_data_page_fails_rather_than_passing`, `background/publish_provenance.py`, `tools/pre_commit_test_gate.py` — the population is derived from the pages instead of typed, the banner is on all twelve live-data pages, and any staged site page now selects the rule.

# FINDING — the provenance banner is on no page at all, and the control that would say so has been asking five deleted doors about it since the tabs landed

**Found by:** the 2026-08-21 seat-claim tick, while landing the sink guard. Not the drawn work —
`tests/background/test_publish_provenance.py` came into the landing's pathspec by filename stem
(`background/publish_provenance.py` was in it for a one-line docstring), the gate refused the
commit on its red, and the red turned out not to be about the guard at all.

**Rank requested:** top of the H_harness queue. BLOCKING under clause 2, and on the narrow
ground the clause names rather than a general sense of importance: **a control in this area is
untrustworthy**. It fails, so it is not silently green — but it fails for a reason that has
nothing to do with the property it exists to protect, and the property is in fact violated.

## Observed, with evidence

Every claim in this section is `observed-with-evidence` (R9). The two inferences are labelled as
such and kept out of it.

**1. No page in the published site loads the freshness banner.** At HEAD (`5b0c7dbc8`):

```
$ git grep -l "freshness-banner" HEAD -- site/
HEAD:site/assets/_freshness_harness.mjs
HEAD:site/assets/freshness-banner.js
HEAD:site/test_freshness_banner_publish_state.py
```

The script, a harness module, and a test. **Zero `.html` files** — of eighteen committed under
`site/` (`git ls-tree -r --name-only HEAD site/ | grep -c '\.html$'` → `18`).

**2. The five doors the control names do not exist, and were deleted on purpose.** All five went
in one commit:

```
$ for d in company proof world now project; do git log --oneline -1 --diff-filter=D -- "site/$d/index.html"; done
03dd8c49e The five tabs are the site now: eleven pages deleted, their content moved, and 25,700 lines of surface nobody could reach are gone
```

**3. The control still asks for them by name.**
`tests/background/test_publish_provenance.py:172`, `test_every_live_data_door_opts_into_the_banner`:

```python
for door in ["company", "proof", "world", "now", "project"]:
    html = (site / door / "index.html").read_text()
    assert "freshness-banner.js" in html, door
```

Its red is `FileNotFoundError: .../site/company/index.html` — a *missing page*, not a *missing
banner*. Observed in the refused landing, 2026-08-21: `1 failed, 340 passed in 14.80s`.

**4. The banner's data half is still being published, every cycle.** `c43439739` is
`chore(provenance): verification paused banner (git=2c0ba712b) -- the site keeps serving the last
VERIFIED run and now says so`. `background/publish_provenance.py` writes
`site/data/publish_provenance.json`, and `process_run_complete._publish_provenance_banner` commits
that path alone on a red cycle. The producer runs; the reader does not exist.

## What this means

The director's ruling of 2026-08-10 (`DIRECTOR_RULING_PUBLISH_DECOUPLING`, property 3) is quoted
verbatim at the top of `background/publish_provenance.py`: *"A visitor can always tell WHAT they
are seeing and HOW current it is."* **A visitor currently cannot.** The state file is published,
the sentence is composed, `banner_line()` is logged on every cycle — and no page fetches any of
it. The module's own docstring says "this module publishes the one thing that must never freeze:
the statement of how frozen everything else is", and that statement reaches no reader.

This is the R11 clause about orphan transitions, arriving from the other side: the release exists,
the effect is nothing.

**Why it survived.** The control that encodes exactly this property was *already red* when the
tabs landed, so its going red proved nothing to anyone — and it is outside the publish gate's
scoped selection (it appears in no scoped run in `docs/observability/`; the gate selects by
filename stem, and nothing routinely touches a `publish_provenance`-stemmed path). A control that
is red for an unrelated reason, in a file nothing routinely selects, is indistinguishable from a
control that is absent. It is the FAIL-SILENT killer pattern reached by a route R15 does not
enumerate: not "the checker was unavailable", but "the checker was answering a question about a
subject that no longer exists, and its answer was never read."

**It also wedges its own module.** `background/publish_provenance.py` cannot be committed by any
lane while this test is red, because the gate selects the test by the module's stem — the shape
already filed as *a wedged test file makes its production module unwireable*. One of this tick's
own edits (a docstring correction) was reverted rather than landed for exactly this reason, which
is how the finding was found.

## The class, and why the instance fix is refused (R10)

The class is **a control whose subject was retired by a ruling**, already on the register as
`WORKER_FINDING_A_FALSIFIER_CAN_BE_RETIRED_WITH_ITS_SUBJECT` (cited in
`background/finding_severity.py`). This is a new instance, so per R10 the closure is the class.

Deleting the five names and moving on would be the instance fix, and it would be worse than
nothing: it would turn a control that is loudly wrong into one that is quietly absent, on a
published property the director ruled by name.

**Candidate closure, in the shape that class already has:** a retired subject needs a **third
state between FAILED and CLEAN — WITHDRAWN**, carrying its own falsifier, and the mutation is made
against the bytes at `<ruling>^` (here `03dd8c49e^`, where the five doors still exist). Concretely
for this instance:

1. **Re-point the property at the surface that exists** — the tabs, enumerated from the site's own
   IA register (`site/ia_register.py`) rather than a hand-typed list, so the next structural
   ruling cannot orphan it the same way. This is the part that makes the control true again.
2. **Then decide the banner's actual placement**, which is a director-facing question about the
   published surface and not a harness one: the banner has to appear on every page that renders a
   live figure. That is a SITE-lane change with an R11 close (fetch the live page, assert the
   rendered sentence), not a test edit.

**Not fixed on sight, deliberately** (SELF_INTERRUPT_DISCIPLINE): step 2 is a published-surface
change needing a live-fetch close, two suites were in flight against this shared tree throughout,
and the machine is not blocked on it — the site is serving, just silently. Doc-only this tick.

## What this does NOT claim

- **Not** that any published figure is wrong. The numbers are what they are; what is missing is the
  statement of how old they are.
- **Not** that the banner script itself is broken. `site/assets/freshness-banner.js` was not read
  or executed here — only its absence from every page was measured. Whether it would work if a page
  loaded it is *unknown* from this tick.
- **Not** that the tab deletion was a mistake. `03dd8c49e` is a deliberate, reasoned consolidation;
  the defect is that a control was left pointing at what it removed. (*inferred*, from the commit
  subject and the fact that content was moved rather than dropped — the commit itself was not read
  in full.)
- **Not** established: whether the banner reached readers at any point *before* `03dd8c49e`. The
  five doors carried the script then, by §3's own assertion, but no fetch of the live site from
  that era exists here to confirm it rendered. (*inferred*.)

---

## CLOSED 2026-08-21, `8a0199b21` — both steps, and one thing this finding got wrong

Every claim below is `observed-with-evidence` (R9); the commands are quoted where the value came
from a fetch or a run.

**Step 1, the control.** The population is now DERIVED from the shipped pages rather than typed:
`background/publish_provenance.py::live_data_pages` / `banner_adoption_violations`, moved out of
`test_publish_provenance.py` into `tests/background/test_publish_provenance_banner_adoption.py`.

**Step 2, the placement — done, not deferred.** The finding parked this as a SITE-lane change
owing an R11 close. It is a four-line head insert on twelve pages, and leaving it would have left
the property violated while the control went green about the wrong thing, so it went with step 1.

**Step 3, which the finding did not ask for and is the reason this survived a day.** Nothing
routinely selects a `publish_provenance`-stemmed path — the finding's own diagnosis — so the rule
is now in `tools/pre_commit_test_gate.py::SITE_SURFACE_TESTS`. Adding or editing any page under
`site/` runs the rule about pages. Both selection edges were measured by calling `select_targets`
directly: a staged site page selects it, and so does the module.

### WHERE THIS FINDING WAS WRONG

It says the front door is *"deliberately absent: it renders no live figure"*, quoting the old
control's own exemption. **That exemption was false, and had been since before the ruling.** Run
the derived rule over `03dd8c49e^` — the tree the five typed names were right about — and it finds
**24 live-data pages, of which those five carried the banner and 19 did not**, the front door
among them: it reads `dashboard.json` and carried nothing. The typed list was not merely stale
*after* the ruling; it was green on a tree where four fifths of its own population was uncovered.
That measurement is a test node, not a remark: `test_the_typed_five_were_blind_to_nineteen_pages`.

Two further corrections to this document's framing:

* **The closure is NOT the WITHDRAWN third state this finding proposed.** That shape is for a
  subject a ruling *deleted*. Here the subject MOVED — `03dd8c49e` says so itself ("world,
  company → Capabilities; proof, evidence → Harness; now → Home"), and the content came with it.
  Retiring the property would have withdrawn a rule whose subject is alive on five tabs.
* **`fetch(` is the wrong detector, and the finding's own §3 contains the counter-example.**
  `site/company/index.html` at `03dd8c49e^` read all five of its feeds through
  `function jget(url){ return fetch(url+"?t="+Date.now()); }` and contains the literal `fetch(`
  exactly once, on a URL it never names. The rule therefore keys on the REFERENCE to a published
  JSON artefact, with `href=`/`src=` values stripped first so an evidence LINK is not mistaken for
  a rendered figure. Both directions are pinned by tests.

### R11 CLOSE — fetched from the live site, 2026-08-21T16:06:50Z

All twelve pages serve the layer (`curl -s https://poesys.net<path> | grep -c freshness-banner.js`
→ `2` on each of `/`, `/capabilities/`, `/explore/`, `/harness/` and the eight `/knowledge/`
topics), and `https://poesys.net/assets/freshness-banner.js` returns `200`.

The rendered VALUE, not the tag: the asset fetched FROM THE LIVE SITE, driven through
`site/assets/_freshness_harness.mjs` against `publish_provenance.json` and `tick_heartbeat.json`
also fetched from the live site, produces `state=paused`, `error=None`, and the sentence

> Verification paused since 2026-08-20T21:10:26Z · showing run
> run_output_a892df011_20260820T180449Z.json (last verified 2026-08-20T18:34:35Z) — Published with
> 100 open findings and 68 non-blocking test reds elsewhere in the repository…

which is the director's property 3 satisfied: a visitor can now tell what they are seeing and how
current it is. The pages carry `cache-control: no-cache, must-revalidate` and answered
`cf-cache-status: DYNAMIC`, so this is the deployed surface and not an edge-cache ghost.

**Evidence:** 14 tests in the new file, each mutation departing from a null-control fixture proven
clean; 344 passed across the provenance suite, the site suite and site reachability.

**Still open, same class, NOT fixed here** (untouched by this commit, and pre-existing at
`7fcf5182d`): 11 reds in `tests/tools/test_site_structure.py` and
`tests/tools/test_site_lane_gate.py` naming `site/company`, `site/customers`, `site/project` and
`site/proof`. `03dd8c49e` reports converting 87 controls off literal page lists; these and the one
above are what it missed.
