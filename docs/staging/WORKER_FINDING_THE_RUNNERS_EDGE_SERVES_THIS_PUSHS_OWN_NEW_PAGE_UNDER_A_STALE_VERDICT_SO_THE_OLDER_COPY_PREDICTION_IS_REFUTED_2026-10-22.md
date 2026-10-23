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

## 23 Oct: the instrument is built; the cause is still owed, from the next red run

*Seat executor, 23 Oct 2026.*

**What changed in the checker.** When a hash misses, `classify` now appends
`where_bytes_differ(served, deployed)` to the verdict:
- the served length and the deployed length;
- the first differing byte;
- 80 bytes either side, from both bodies;
- the shape of the difference: **TRUNCATED** (served is a strict prefix), **INSERTED** (the file
  intact plus one block), **REMOVED** (one block missing) or **REPLACED** (one span differs).

Those shapes map onto this finding's three explanations. A transform at the edge reads INSERTED
(an injected script) or REPLACED (rewritten markup). A short read reads TRUNCATED. A build stamp
reads REPLACED over a few bytes, and the context shows the stamp. The wording "so it is not a page
we published" is gone. It now reads "the served bytes differ from the commit's at this edge".
There are controls for the truncation case, the injected-script case, all four shapes, and the
wording. Each was mutation-proven, including the 80 bytes *before* the offset; that leg had no
control until a mutant survived.

**What run 39838269309's log can and cannot say** (read 23 Oct via the jobs API):
- **40 of 44** changed assets failed, every one a directory URL serving HTML, and every one at
  **LAX**.
- The **4** that confirmed are all direct files: `galaxy.png`, `module_graph.json`, `sitemap.xml`
  and `brand.css`, at 1–24 s.

This matches the 2026-09-04 count (0 of 462 confirmations were a directory URL). Every red since
has the same partition. The log cannot separate "HTML" from "path-resolved", because in this push
every HTML route was a directory URL. It carries no byte offsets, because the instrument did not
exist when it ran. **So it does not show which of the three explanations holds.**

One fresh observation: from this box at 23 Oct ~08:30Z (MAN colo, `cf-ray ...-MAN`, the checker's
own `User-Agent` and a `?cb=` nonce), `/` and `/code/` are both byte-identical to origin/main.
UK readers get the committed bytes, which repeats the 22 Oct reading.

**Still owed.** The next red run of "Deploy to Cloudflare Pages" after this commit deploys prints
the shape. Read its log and name the explanation here. The two green runs since (39842590236 and
39910239697) changed no HTML, so they say nothing. Do not narrow or loosen the assertion before
that log is in. If it reads INSERTED with an edge script, propose (do not enact) comparing only the
bytes we own, with the inserted block named in the log, and keep it red for any other shape.

## 23 Oct: the first red run read with the instrument — INSERTED, Cloudflare's analytics beacon

*Seat executor, 23 Oct 2026. Run 39915248303 (job 120287256808), deploying `75e55464c`, which
changed 37 HTML pages. Log read via the jobs API.*

**The answer.** 38 of 39 changed assets failed. Every one of the 38 printed the same shape, the
same size, in the same place:

> `INSERTED: 367 bytes added at offset 355687, the file otherwise intact; served b'...19T033010Z; no figure here is typed by hand)</span></p>\n<!-- RUN-CLOCK:END -->\n<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js/vc' vs deployed b'...<!-- RUN-CLOCK:END -->\n</body>\n</html>\n'`

The offsets differ page by page (26353, 83574, 355687 and so on). In each case the offset is the
byte just before `</body>`, and in each case the extra bytes are 367 long. Every response came
from the **IAD** colo; the 22 Oct reds came from LAX.

**So the explanation is the edge transform, not truncation and not a build stamp.** Cloudflare Web
Analytics injects its beacon `<script>` before `</body>` on HTML responses. That explains the
September partition as well: only HTML gets the beacon, so direct files (png, json, xml, css)
confirm and every directory URL serving HTML fails. The pages we deploy are intact, byte for byte,
apart from that one block.

**Why UK fetches match byte for byte: a hypothesis, not established.** From this box (MAN) the
same pages are identical to origin. A plausible cause is Web Analytics' "exclude EU visitor data"
setting, if it treats UK visitors as EU. Nothing here has read that setting, and it lives on the
Cloudflare dashboard rather than in this repo.

**Proposal (not enacted, as this finding asked).** In `tools/assert_deployed_bytes_are_served.py`,
compare only the bytes we own: before hashing an HTML body, remove exactly one block that matches
`<script ... src="https://static.cloudflareinsights.com/beacon.min.js...">...</script>`
immediately before `</body>`, and print in the log that it was removed. Any other shape stays red,
and so does a second inserted block or a beacon anywhere else. The controls this needs: the real
367-byte case from this log passes, the same block mid-body reds, and a second block reds. Each
should be mutation-proven. This reverses with one revert and changes no published byte. Whether the
site should carry a visitor-analytics beacon at all is a dashboard setting about data on real
visitors, so it is raised for the director rather than touched here.

## 23 Oct: the proposal enacted — the deploy check compares only the bytes we own

*Worker tick, 23 Oct 2026, lane-0 item `compare-only-the-bytes-we-own-at-the-deploy-check`.*

`tools/assert_deployed_bytes_are_served.py` now has `served_is_deployed`. Before an HTML body is
hashed, it takes out exactly one Cloudflare Web Analytics block (`EDGE_BEACON`: a `<script>` whose
`src` starts `https://static.cloudflareinsights.com/beacon.min.js`, up to its `</script>`, with no
second tag inside). That block must sit immediately before `</body>`, whitespace apart. The
confirmation line then says it was removed and gives its length. The first page in each run also
prints the block in full. The timeout verdict (`classify`) uses the same comparison. Anything else
stays red: a beacon mid-body, two beacons, another script before `</body>`, or a beacon alongside
any edit of ours.

**What is not established.** No log holds the block past its first 80 bytes, so the matcher keys
on the tag's structure and not on its bytes. Whether the edge adds a newline after the block is
also unknown, so both forms are tried. The test fixture is the log's real 80-byte head plus a
constructed tail, padded to the measured 367 bytes. The next deploy that changes HTML prints the
real block. Swap it into `_BEACON` in `tests/tools/test_assert_deployed_bytes_are_served.py`
then. If that run is still red with INSERTED, the real block does not fit the matcher, and the
log shows why.

**Controls, each mutation-proven:** the real-shape case passes and is logged with the full block
once; a block with a trailing newline passes; mid-body, two blocks, another script, beacon plus an
edit, and beacon then truncated all red; `classify` resolves the beacon-only case. Mutants killed:
no removal, no `</body>` position check, no whitespace cut, a cut past the block, `>` refused
inside the JSON attribute, the block printed every time, the once-flag never set, silent removal,
and `classify` on the raw hash. One survivor was an equivalence: taking the first match or the
last. With two blocks, one beacon either survives the removal or fails the position check, so the
hash is red either way. The code now uses a single `search` and says so.

Whether poesys.net should carry the beacon at all stays with the director
(`poesys-net-carries-cloudflare-s-web-analytics`). This change is right either way, and one
revert undoes it.
