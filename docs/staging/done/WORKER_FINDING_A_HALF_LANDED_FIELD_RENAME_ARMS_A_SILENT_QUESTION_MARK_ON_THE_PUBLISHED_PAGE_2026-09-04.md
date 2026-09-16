**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A field rename that is complete in the code and absent from the artefacts arms a silent "?" on the published page, and the control that should catch it asserts the column HEADER

**Found:** 2026-09-04, autonomous worker, immediately after landing `7d33c1986` (the deployment
reading). Observed in the shared tree, not inferred — the interleave happened mid-gate.

---

## The state, as measured

A concurrent lane is renaming `behind_s` to `unincorporated_for_s`. At the moment of writing the
rename is **complete in every code file and present in no artefact**:

| file | field |
|---|---|
| `background/deploy_restart.py` (producer) | `unincorporated_for_s` |
| `tools/generate_proof_data.py` (generator) | `unincorporated_for_s` |
| `site/harness/index.html` (renderer, working tree) | `unincorporated_for_s` |
| `site/harness/test_...reaches_the_reader.py` (control, working tree) | `unincorporated_for_s` |
| `docs/observability/daemon_deployment.json` (artefact) | `behind_s` |
| `site/data/proof.json` (artefact) | `behind_s` |
| **`site/harness/index.html` AT HEAD** | **`behind_s`** |

That last row is the whole finding. `7d33c1986` is internally consistent — `surgical_land`
snapshotted before the rename reached the working tree, so its renderer, generator and feed all
say `behind_s` together. The working tree has since moved past it on one side only.

## Why it goes wrong on its own, with nobody making a mistake

`background/process_run_complete.py` stages the publish surface as a **glob over
`site/data/*.json`** (line ~4575) and **never stages `site/harness/index.html`** — grep for
`harness` in that module returns only commentary. It also regenerates the feed from the SHARED
TREE's code, not from HEAD's.

So the next successful publish cycle:

1. runs the working tree's generator, which emits `unincorporated_for_s`;
2. commits the regenerated `site/data/proof.json` carrying that key;
3. leaves `site/harness/index.html` at HEAD, still reading `r.behind_s`.

`ageStr(undefined)` returns `"?"`. **The live page renders a `?` in the "behind" column for every
daemon**, and nothing anywhere is red.

This is the known publish-daemon shape — *"the publish daemon commits your uncommitted output
without your source, rendered by the OLD renderer"* — reached from the other direction: not new
output against an old renderer, but a **renamed** output against an old renderer.

## The control does not catch it, and the reason is worth keeping

`site/harness/test_the_deployment_reading_reaches_the_reader.py` has the right leg for this:

```python
assert "running age" in html and "loaded-code age" in html
...
assert "behind" in html
```

Those assert the **column headers**, which are literal strings in `renderDeployment` and do not
move when the field name does. The cell contents are never asserted against the feed's own values.
So the section can render `? ? ? ?` down a column and every leg stays green — a *constant verdict*
in the one place this file's own docstring says it was guarding against.

The null control (`test_a_stale_daemon_and_a_current_one_do_not_render_the_same`) does not save it
either: it builds its own fixture rows, so it renames cleanly with the code and never meets the
committed feed.

**The property the control is missing: for the live feed, every age the artefact declares must
appear as a rendered VALUE, not merely as a heading.** A header is markup; a value is a reading.

## What I first wrote here, and why it was wrong

This section originally said the repair was the other lane's to land and that I would not touch it.
Then I read that lane's in-flight `surgical_land` argv directly: its pathspec is
`background/deploy_restart.py`, `tests/background/test_deploy_restart.py`, `CLAUDE.md`,
`docs/observability/daemon_deployment.json`. **The generator and the renderer are not in it**, and
its commit message reads as a completed rename. So the gap was not going to close on its own — it
was going to be left behind a commit that reasonably believed itself finished. Kept rather than
revised away, because "someone else will land it" is the assumption that produces this class.

## Repair 1, landed with this finding

`tools/generate_proof_data.py` (via `--content`, the deployment half only — its working-tree copy
still carries the unfinished reason-mix rename), `site/harness/index.html`, and the control's
fixtures, all moved to `unincorporated_for_s`. Both non-generator diffs were verified rename-only
before landing; the generator override diffs to exactly one line against HEAD.

Verified in a clean extract: 557 passed, the generator emits `unincorporated_for_s`, and the single
failure is `test_no_control_the_site_lane_executes_is_missing_from_the_repository` failing **closed**
because the extract is not a git work tree — which is that control behaving correctly.

## Repair 2, NOT done, and it is the one that outlives this instance

Add a leg asserting each daemon's rendered row carries the **values** the artefact declares, not the
column headers. Keyed to the property, so any future field rename landing on one side only reds
immediately instead of publishing `?`.

**It is not landed here, and the reason is a real constraint rather than a preference.** The leg
must be green at its own commit, and at this commit `site/data/proof.json` still carries `behind_s`
while the renderer now reads `unincorporated_for_s` — so an honest leg is RED until the publisher
regenerates the feed. Writing it to skip in that state would be the fail-open shape this file is
about. The next tick can add it green once one publish cycle has run.

So the section is currently protected against being deleted, and still not against being emptied.

## Cost if it lands unnoticed

One published column of `?` on the Proof harness page, on the very section whose stated purpose is
that *"ten of eleven are stale" is a reading and not a discovery* — reporting nothing, while every
control over it stays green.
