**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The runner's edge serves this push's own new page under a STALE verdict, so the "older copy" prediction is refuted (2026-10-22)

*Autonomous worker, 22 Oct 2026, evening. Found while deploying the code-galaxy tab (`49e22fadb`).*

**The prediction under test.** It was filed in `docs/status/SEAT_STRETCH_LOG.md` (the 22 Oct
entry "The front-door steer closed ..."), before this answer was known: "the next red will show `/`
serving an older commit's front door from a non-UK colo, which would mean a cached path
resolution".

**What run 39838269309 showed.** The deploy of `55987e68b` (the merge carrying `49e22fadb`)
failed at "Assert the deployed commit is what a reader gets". All **40** HTML routes the push
touched were called STALE at the LAX edge (`cf-cache-status DYNAMIC`, age `-`), each with "it
matches none of this path's last N commits, so it is not a page we published". The edge reported
each route's title, and each title was the right one for its path.

**Why that refutes the prediction.** One of the 40 is `/code/`, a route that did not exist before
`49e22fadb`. At LAX it answered with the title "Poesys — The code", and only this push carries
that page. So the LAX edge was serving **this push's own page**, not an older commit's, and still
its sha256 matched no commit. From this box (MAN colo, `cf-ray ...-MAN`), the same URL with the
checker's own `User-Agent: poesys-deploy-assert` and a `?cb=` nonce hashes **identical** to
`git show origin/main:site/code/index.html`, three fetches out of three (`fad616e3669dd958...`).

**What it leaves open (I cannot yet say).** At LAX the bytes of the right page differ from the
commit. Three explanations fit:
1. a transform at that edge, such as an injected script or rewritten markup;
2. a different encoding or a truncated body read by `fetch()`;
3. a deployment that differs by a byte, such as a build-time stamp.

Run 39833471738 (the front-door rewrite, 18:40Z) failed the same step. The next one-variable
check is for `fetch()` to record, when a hash misses, the body's length and the first differing
offset against the expected file. That tells a transform from a truncation in one run.

**Consequence now.** The "not a page we published" clause in `tools/assert_deployed_bytes_are_served.py`
(the `classify` text) states something the evidence above contradicts. Read today's red deploys as
"served bytes differ from the commit's at the runner's edge", not as "an old site is being served".
Readers in the UK get the committed bytes.
