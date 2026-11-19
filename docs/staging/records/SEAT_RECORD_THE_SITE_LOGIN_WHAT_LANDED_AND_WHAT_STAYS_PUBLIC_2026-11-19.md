**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `unminted`

# The site login (director ruling 19 Nov): what landed, what waits, and what stays public

Ruling: `docs/staging/advisor/DIRECTOR_RULING_REPO_STAYS_PUBLIC_AND_THE_WEBSITE_GOES_BEHIND_A_LOGIN_2026-11-19.md`.
That file stays open until the gate is proved. This record is the first increment.

## Landed (delivery seat, executor lane, 19 Nov)

- `for_the_director` row `the-github-repository-is-still-public-gh` is answered `no`, his words quoted. The repository
  stays public, and no copyright line names a company.
- `site/robots.txt` now refuses search crawlers (`User-agent: *` and `Claude-SearchBot` are `Disallow: /`). The July
  AI-training blocks are unchanged. User-directed fetch (`Claude-User`) is still allowed, as it acts for a reader.
- `site/_headers` adds `X-Robots-Tag: noindex, nofollow` on every route. Only Cloudflare Pages reads that file, so the
  github.io copy, which is the advisor's read path, is untouched.
- `tools/assert_deployed_bytes_are_served.py` and `.github/workflows/deploy-pages.yml` send an Access service token
  when the secrets `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` exist. Without this, the post-deploy check
  would read the login page as a stale deploy and go red on every publish once the gate is on. With no secret set,
  the request is unchanged.

## Waits (raised, with a recommendation)

- **The gate itself** (row `the-site-login-you-ruled-on-19`). No lane holds a Cloudflare credential that can
  configure Access. *[Note, 19 Nov, delivery seat: not yet tested. The Actions secret
  `CLOUDFLARE_API_TOKEN` (the Pages deploy token, minted 22 Jun) is a lane-usable credential, and its scopes are
  unknown. `.github/workflows/cloudflare-access-probe.yml` is read-only and answers this. If the token can see
  Access, the gate needs no new credential from him.]* The 20 Aug grant is an OAuth session held by the console. The design is one Access application
  over `poesys.net`, `poesys-net.pages.dev` and `*.poesys-net.pages.dev`, using one-time email codes with the
  director's address as the only reader, plus one service token for the deploy check. Done means:
  - an unauthenticated fetch of each of those routes is refused, recorded as a reading;
  - the director logs in once;
  - the reversal is recorded: delete the Access application, then the two GitHub secrets.

  No DNS change is expected. A payment-card screen is his.
- **Canon D11** ("the public site ... an intelligent stranger"), row `canon-d11-says-the-public-site-exists`. Page
  copy that calls the site public waits on his answer, because D11 is his wording.

## What stays public, plainly

The repository is public. Everything the site publishes is readable in `site/` and `docs/`, and on the github.io
copy. The login will stop casual visitors and search engines, not a determined reader. No page may present it as
making Poesys private.
