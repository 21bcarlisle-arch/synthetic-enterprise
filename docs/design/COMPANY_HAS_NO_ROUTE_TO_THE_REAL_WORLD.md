# The company has no route to the real world

**Director ruling, 2026-08-18.** Enforced by `tools/company_network_isolation.py`, wired into
pre-commit. R15-proven in `tests/tools/test_company_network_isolation.py`.

CLAUDE.md carries the rule and its enforcement pointer; this file carries the reasoning, moved
here by the 2026-08-27 decay audit under the standing convention that a rule lives in the rulebook
and its full text lives in its doc.

## Three lanes, three answers

**COMPANY (`company/`, `saas/`): may not open a socket, ever, directly or transitively.**

**SIM: may ingest published sources.** That is its job, and the bytes become world truth.

**HARNESS: may fetch published sources; the bytes may become documentation, design records and
Knowledge, and NEVER a runtime input the company reads.**

## The axis is CAPABILITY, not hosts

A host list has to be RELAXED at go-live — exactly when it matters most. A capability boundary
does not: at go-live nothing on the company side changes, and what moves is what sits behind the
seam.

## Refused by construction, never by approval

> *"If company-side code has to ask, someone eventually says yes, and the breach arrives as a
> reasonable decision."*

This is why there is no approval path. An approval path is a breach with a waiting period.

## The harness clause is the load-bearing one

Without it the harness is the company side by proxy: fetch on the harness lane, write the bytes
where the company reads them, and the wall is intact on paper and gone in fact. "Never a runtime
input the company reads" is checkable in a way that intent never is.

## What is NOT the boundary

`background/egress_allowlist.py` names hosts, has **no production callers**, and its own docstring
says it enforces nothing. It is a list, not a control. Anyone reaching for it as the boundary is
reaching for the wrong thing.

## The control is a RATCHET

Four known routes are frozen — the seam's price fallback on a cache miss, and the audit module
shelling `curl`. A NEW route fails. A STALE entry fails. Both directions, so the frozen set can
only shrink.
