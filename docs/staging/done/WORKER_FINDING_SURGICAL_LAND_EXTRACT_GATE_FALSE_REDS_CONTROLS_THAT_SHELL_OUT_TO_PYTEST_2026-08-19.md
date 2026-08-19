# WORKER FINDING — `surgical_land`'s clean-extract gate false-reds any control that validates by running pytest

**Severity:** LATENT · **Lane:** H_harness
**Date:** 2026-08-19
**Class:** a control that cannot pass in the environment its own gate constructs.
**Status:** cause identified, reproduced twice, workaround used. Not repaired.

---

## What happened

`tools/surgical_land.py` is the sanctioned way to land named paths when a dirty shared index
would make an ordinary merge sweep another lane's work. It gates **a clean extract of the tree
the commit would create**, rather than the working tree — which is the right idea, and is why
it exists rather than `--no-verify`, which is a wall.

Landing the disk governor, it refused twice:

> REFUSED: GATE RED on the resulting tree (rc=1). This is the tree the commit WOULD create, not
> the working tree — a working tree that passes here means the unstaged half is what makes it pass.

That message is a good message. It was also, here, wrong. Building the extract by hand and
running the gate's own targets inside it produced exactly one failure:

```
FAILED tests/background/test_gate_authorization.py::test_repairing_the_finding_lets_the_next_raise_through
1 failed, 84 passed
```

The same test passes in the real repository. A second control behaves identically:
`tests/background/test_supervisor_blocker_precedence.py::test_a_validly_discharged_blocker_stops_blocking_its_lane`.

## Why

Both controls verify a **discharge**: the claim that a blocking finding has been repaired. The
project's discharge rule is not "someone wrote DISCHARGED in a file" — it is that a named test
node actually passes. Validating that means *running pytest on that node*.

Inside `surgical_land`'s extract, that inner pytest run cannot succeed: the extract is a bare
tree of the committed paths, without the repo context the inner run needs, and the outer run is
already a pytest process. The discharge therefore fails to validate, the lane stays blocked, and
`LaneBlockedError` is raised — a **red that reports the extract's limitations, not the commit's**.

Note the shape: it is not a flaky test and not a missing dependency. It is a control whose
verification method is structurally unavailable in the sandbox its own gate builds. R15 calls the
inverse of this FAIL-SILENT (a check that passes when the checker is unavailable). This is the
mirror image — a check that **fails** when the checker is unavailable — which is the safer
direction and still wrong, because the failure is indistinguishable from a real defect.

## What I did, and the honest limit on it

Landed via an ordinary pathspec `git commit`, whose pre-commit gate runs in the **working tree**,
where both controls genuinely pass. That is not a bypass: the full gate ran, and the pathspec —
not a lock, not `--no-verify` — is what prevents sweeping another lane's work. `git commit -- <paths>`
is the mechanism CLAUDE.md already names for exactly that.

The limit: this is a workaround for *me*, not a repair. The next lane to hit a genuinely dirty
index still needs `surgical_land`, and it will still false-red on these two controls, and the
person who meets it will reasonably conclude their commit is broken.

## Repair options, not taken here

1. **Teach the discharge validator to detect the extract** and return "cannot validate here"
   distinctly from "validation failed". Cheapest, and keeps the control honest — but adds a third
   state that every caller must handle, and a mishandled third state is how fail-open arrives.
2. **Give the extract enough context to run the inner pytest.** Most faithful — the extract's
   whole promise is that it is the tree the commit would create — but the extract exists partly
   to be cheap, and this makes it a full checkout.
3. **Exempt the two controls from the extract gate by name.** Fastest and worst: a named
   exemption list is a place where controls go to stop mattering.

My recommendation is (1) with the third state named explicitly (`UNVALIDATABLE_HERE`) and a
mutation test proving a caller that ignores it fails. Queued as an atom rather than fixed on
sight, per SELF-INTERRUPT DISCIPLINE — the machine was not blocked, because the pathspec route
works.

## Related, found while chasing this

A second, unrelated cost of long gates showed up in the same session and belongs on the record
because it changes how landing should be sequenced: the pre-commit gate takes **25–35 minutes**
while other lanes land every **12–20**, so a commit can pass its entire gate and then die on
`fatal: cannot lock ref 'HEAD': is at <x> but expected <y>`. That happened once today
(the lane-formation commit) and cost a full gate run. It is not a correctness problem — nothing
was lost, the retry landed — but at these ratios a slow lane can be starved by faster ones
indefinitely, and nothing currently measures how often the ref race is lost.
