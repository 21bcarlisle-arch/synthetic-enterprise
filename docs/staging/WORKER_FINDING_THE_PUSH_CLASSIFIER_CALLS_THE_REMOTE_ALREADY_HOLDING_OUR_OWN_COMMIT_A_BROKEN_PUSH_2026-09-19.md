**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The push classifier calls "the remote is already at the sha I am pushing" a broken push

Found while landing `the-shared-index-holds-the-archive-reversal`. Filed rather than fixed: the
subject is `background/origin_reconcile.py`, which is not this claim's scope, and binding a daemon
repair to an index-hygiene claim would make both unreadable.

## The observation

`python3 -m background.origin_reconcile --json` on the shared tree at 15:3xZ, one commit ahead of
`origin/main`, returned:

```json
{"status": "ERROR", "behind": 0, "pushed": false,
 "detail": "local is 1 commit(s) ahead. merge gated clean but the push was rejected:
   ! [remote rejected] HEAD -> main (cannot lock ref 'refs/heads/main':
     is at d0cc753fd6f29a44820e854b5d227a2d3a381e2e but expected d181b062dc6dbe4c6a315d03a531a4a44325bbe3)"}
```

`d0cc753fd` **is the commit it was pushing.** A `git fetch` immediately afterwards put
`origin/main` at `d0cc753fd` and `HEAD...origin/main` at `0 0`. The push did not fail; the desired
state was already true when it ran.

## The mechanism

`_classify_push_failure` (`background/origin_reconcile.py:1401`) knows two shapes and keys on git's
own words for both: `non-fast-forward` and `fetch first` → `REFUSED_RACE`; everything else →
`ERROR`, deliberately, because an unrecognised push failure should get looked at.

`cannot lock ref` is a third shape and the fall-through swallows it. It is the remote's
compare-and-swap refusal, and it carries the two shas that settle the case in the message itself:

* **remote ref == the sha we pushed** — the work IS on origin. Nothing is owed and nothing is
  broken. This is what happened here, and the most likely cause is the `reconcile-watch` timer
  firing concurrently and pushing the same commit first.
* **remote ref == some other sha** — a lost race, the `REFUSED_RACE` class, cleared by the next
  cadence.
* neither parses — the existing `ERROR`.

So the current code reports `pushed: false` and `ERROR` for an outcome in which the push's whole
purpose was achieved. The fail-pessimistic direction is the right default and the docstring argues
for it correctly; the defect is that this case is not unrecognised — it is recognisable, and the
evidence needed to recognise it is inside the string already being matched.

## Why it matters more than a glance

The docstring's own cost argument assumes `ERROR` costs a reader a glance. It costs more than that
here, because the state is indistinguishable at a distance from a reconciler that genuinely cannot
push — the condition the module exists to surface — and it fires precisely when TWO reconcilers are
racing, which is the normal cadence on this machine rather than a rare event. An `ERROR` that
appears whenever the system is working correctly and concurrently is the class of alarm that gets
learned as noise.

## The remedy, and the control that would have to fail

One leg, not a register: parse the two shas out of `cannot lock ref '<ref>': is at <A> but expected
<B>`, and when `<A>` equals the sha being pushed return a success status with `pushed: true` and a
detail saying another writer pushed the identical commit first. When `<A>` is anything else, return
`REFUSED_RACE`. Unparseable stays `ERROR`.

The control must assert the partition is reachable in both directions — `<A> == ours` and
`<A> != ours` — over one test, because a classifier that returns `ERROR` for everything passes every
per-branch test written for it. That is this project's own rare-branch trap and this classifier is
already standing in it: the `ERROR` leg is its fall-through.

## What would refute this

A reading of `cannot lock ref ... is at <our sha>` in which the commit is NOT on origin — i.e. the
remote ref advanced to our sha and then moved again before the fetch. That would make the status
correct and the finding wrong. It is checkable: `git rev-list --left-right --count HEAD...origin/main`
immediately after, which read `0 0` in this instance, so it does not hold here.
