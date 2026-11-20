**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Five machine readers of poesys.net will read the password page once the gate is live

The password gate (`functions/_middleware.js`, director addendum 20 Nov 07:00) answers 401 with a
password page to any request without the cookie or the `X-Poesys-Gate` header. The deploy check
and `tools/retired_paths_still_served.py` send the header (via `reader_headers()` in
`tools/assert_deployed_bytes_are_served.py`). The K8 note's list of readers
(`docs/design/POESYS_NET_BEHIND_A_LOGIN_2026-11-19.md`) also names these, not yet wired:

- `background/process_run_complete.py`'s post-publish readers
- `tools/insight_challenge.py` (`SITE_URL = "https://poesys.net/knowledge/"`)
- `tools/couple_w2_11_d5.py`
- `tools/generate_project_state.py` (prints poesys.net URLs for the advisor; it already tells the
  advisor to use github.io, which stays public)
- `tools/mirror_github_pages.py` / `tools/edge_traffic_capture.py` (to be checked: they may read
  github.io or the Cloudflare API, not the site)

A sixth reader, not on that list, was fixed on 20 Nov by the blind-audit landing:
`site/live_pixel_verify.py`'s `_http_get`, which every live site test uses. It got a 401, so
`site/test_the_published_bound_reaches_the_live_reader.py` was red and refused every commit that
triggers the whole site suite. It now sends `reader_headers()`.

Each will either read a 401 as "stale" or "missing" or compare the password page's bytes. Fix:
send `reader_headers()` on each fetch of poesys.net, and confirm on the first live publish that
none goes red for the gate's reason. Knowledge gap: no.
