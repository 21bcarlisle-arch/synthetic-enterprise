**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# `26d4120ab` enters through `publish_provenance.showing_run.run_id`, and the two sides differ because the gate's extract points `HEAD` at the PARENT commit

Claim id: `trace-where-26d4120ab-enters-the-value-arms-comparison`.
Answers the question left open — and explicitly left as `None` rather than guessed — by
`docs/staging/done/SEAT_FINDING_THE_ONLY_DOOR_THAT_CLOSES_GAP_TWO_IS_WEDGED_BY_A_CONTROL_THAT_ANSWERS_DIFFERENTLY_IN_A_CLEAN_EXTRACT_2026-09-24.md`
(landed as `8db5d9c92`, since reset away with `d5f71b0ef` and `c0091062a`; see the last section).

That finding retracted its own mtime-glob story in place and wrote: *"the run id in that comparison
does not come from this glob at all, and the path it does come from has not been traced. The next
invocation should start by tracing where `26d4120ab` enters the comparison, not by editing the
reducer."* This is that trace, and it lands somewhere neither story pointed at.

## PRE-REGISTERED, before the measurement below was run

Written before opening `tools/surgical_land.py`, so that the answer could refute it:

> The run id reaches the compared string through one of the two declared inputs, not through
> `docs/reports/`. The asymmetry (red in a clean extract, green in a working tree) is a property of
> how the extract is BUILT, not of the producer.

Both halves held. The second half is the load-bearing one and it is the part that decides the
remedy, so it is recorded here having been written down first.

## Where `26d4120ab` enters — the whole chain, no glob in it

```
site/data/publish_provenance.json   ->  showing_run.run_id
  -> gva._last_verified_run()["run_id"]
  -> gva._same_run_verdict()        ->  identity["last_verified_run_id"]
  -> gva._withheld_statement()      ->  the `{v}` slot of the STALE branch
  -> is_the_published_supplier["statement"]   <- the field the control compares
```

Measured in this worktree at `origin/main` (`4c3b90230`):

```
site/data/dashboard.json          meta.source_file -> run_output_87b25d6da_20260921T152931Z.json
site/data/publish_provenance.json showing_run.run_id -> run_output_26d4120ab_20260924T002107Z.json
```

The dashboard's run STARTED on 09-21 and the last verified run STARTED on 09-24, so
`_same_run_verdict` returns `stale` — and the stale branch is **the only branch whose statement
embeds `last_verified_run_id`**. That is why the run id is visible in this comparison and in no
other: take any other branch and `26d4120ab` never reaches a compared string at all.

`docs/reports/run_output_*.json`, `_find_latest_run_json`, mtime and `.gitignore` are absent from
the chain above. The previous finding's retraction was right to retract; the replacement mechanism
is not in that file's neighbourhood.

## Why the two sides disagree in the gate and agree in every working tree

`tools/surgical_land._make_standalone_repo`, verbatim:

```python
_git_text(checkout, "init", "-q", env=env)
...
(checkout / ".git" / "HEAD").write_text(parent + "\n")
_git_text(checkout, "read-tree", parent, env=env)
```

**The extract's working tree is `result_tree` — the tree the commit would create — and its `HEAD`
is the PARENT commit.** That is deliberate and correct for the gate's own purpose: it is what makes
`git diff --cached` in step 4 read as *this commit*.

The control does this:

```python
blob = subprocess.run(["git", "show", "HEAD:{}".format(rel.as_posix())], cwd=str(PROJECT), ...)
```

So inside the gate, `from_head` is built from **the commit BEFORE the one being gated**, and `live`
is built from the commit being gated. The control believes it is comparing *a clean checkout*
against *the shared tree*. It is actually comparing *the parent* against *this commit*.

That reads directly onto the gate's own red:

| side | run id | which commit |
|---|---|---|
| `live` (working tree = `result_tree`) | `26d4120ab_20260924T002107Z` (09-24) | the merge being gated, carrying `origin/main`'s provenance |
| `from_head` (`git show HEAD:` = parent) | `b2b233ef7_20260922T043219Z` (09-22) | the lane's local commit, base predating the value-arms landing |

`origin/main`'s committed `publish_provenance.json` names `26d4120ab` — confirmed above. A merge of
`origin/main` into a base that predates it brings that newer file into the result tree while the
parent still carries the older one. **The two sides therefore differ by construction, for every such
merge.** In an ordinary worktree `HEAD` *is* the checkout, both sides read the same bytes, and the
control is green for a reason that has nothing to do with its subject.

## What the control actually asserts, stated plainly

**"This commit does not change the feed's own inputs."** No commit can be required to satisfy that,
and a publish commit exists precisely to violate it. It is keyed to today's bytes rather than to the
property — the failure mode `CLAUDE.md` names as going red when the code becomes more honest — with
the extra twist that the only place it is enforced is the one place `HEAD` does not mean what it
says.

Three consequences, all already paid for:

1. It is **red by construction** on every merge whose base predates the value-arms landing, which is
   every seat's fast-forward. Three byte-identical reproductions on two origin bases.
2. It is **unreachable** for the lane that owns its subject, because a daemon reconciliation merge
   moves no value-arms path and the gate selects by changed-module stem — so `origin_reconcile`
   sails through while every seat is refused.
3. It names an innocent file to every lane that meets it, which reads as a stale working copy — the
   diagnosis both prior invocations reached for, and it cost three gate cycles between them.

## The remedy, and why it is not "compare a different revision"

In the extract the only three revisions available are parent (`HEAD`), result (index), and result
(working tree). Index-vs-working is **equal by construction there** — a control that cannot fail in
the only place it is enforced. Parent-vs-result is the current defect. There is no pair of revisions
in that extract whose comparison means what this control wants, so the repair is to stop comparing
revisions.

The property that was actually wanted, from the control's own history: *the verdict is a property of
the commit and not of the tree that regenerated the feed* — i.e. **no input reaches the claim from
outside the two declared paths.** That is assertable directly, from one revision, identically in a
clean extract and in any working tree:

> Build the verdict from a given `(dashboard, provenance)` pair and require that every run the
> verdict NAMES is a run that PAIR names — `run_identity.dashboard_run_id` is the dashboard blob's
> own `meta.source_file`, `run_identity.last_verified_run_id` is the provenance blob's own
> `showing_run.run_id`, `dashboard_net_gbp` is the dashboard blob's own figure.

It fires on exactly the nine-day defect it was written for and fires *sooner*: the day any third
input reaches the claim, the verdict names a run its inputs do not, and this reds — under the old
shape that was only visible when the third path's committed and working copies happened to have
drifted apart. It is run against HEAD's committed bytes, so the committed surface is still exercised.

## Correction to the record: the three commits are not "unpromotable", they are GONE

The drawn item says `d5f71b0ef`, `c0091062a` and `8db5d9c92` are gated-green and cannot promote.
They are none of those things now. The reflog of `/var/tmp/se-seat-executor` shows
`HEAD@{4}: reset: moving to 72b1d1d7f` after `HEAD@{6}: surgical-land` (`8db5d9c92`) — all three
were **reset away**, and `git branch --contains 8db5d9c92` names no ref. Their content is in no
commit on `origin/main`. Left as a separate finding rather than folded in: recovering three
orphaned commits is different work from unwedging the control, and each is landable alone.

The shared tree `/home/rich/synthetic-enterprise` is, at the time of writing, **13 behind and 4
ahead** of `origin/main` — gap two is still open, and this control is still the reason the only door
that closes it is refused.
