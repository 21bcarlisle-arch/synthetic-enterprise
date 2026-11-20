**Severity:** RECORDED · **Lane:** A_strategy_governance · **Authority:** the director's ruling, 19 Nov 14:07 ("Repo public. Website password")

# poesys.net goes behind a login: what is gated, what stays public, how to reverse it

The K8 note for `docs/staging/advisor/DIRECTOR_RULING_REPO_STAYS_PUBLIC_AND_THE_WEBSITE_GOES_BEHIND_A_LOGIN_2026-11-19.md`.
Written before any Cloudflare change.

## What the login does and does not do

**It stops casual visitors and search engines. It does not make Poesys private.** The repository
stays public by the same ruling, so every page the site serves is still readable in `site/` and
`docs/`, and on the github.io copy (`21bcarlisle-arch.github.io/synthetic-enterprise/`), which
this work does not touch. A determined reader is not stopped. No page may describe the login as
making Poesys private.

## What gets gated (every route to the same site)

| route | how it is reached today | gate |
|---|---|---|
| `poesys.net/*` | custom domain on the Pages project `poesys-net` | an Access self-hosted application on `poesys.net` |
| `poesys-net.pages.dev/*` | the production Pages address | a second Access application on that hostname. Gating only the custom domain leaves this side door open |
| `*.poesys-net.pages.dev/*` | per-deployment preview addresses | Pages' "access policy" setting for previews, or a wildcard Access application |
| Pages Functions | served under the same hostnames | covered by the hostname-level applications. `site/` has no `functions/` directory today |
| `www.poesys.net` | does not resolve (reading below) | nothing to gate. Adding it would be a DNS change, which is reserved |

Policy: allow by e-mail, with one-time PIN codes. The director's address is the first allowed
reader. Zero Trust Free covers up to 50 users.

**No DNS change is expected.** Access applications sit on hostnames already proxied in the zone.
If the API says otherwise, the change gets named and raised, not made.

## Belt and braces, live now

These landed in `site/robots.txt` and `site/_headers` in d3025b96d0:
`User-agent: * / Disallow: /` and `X-Robots-Tag: noindex, nofollow`. The AI-training blocks from
12 Jul stay, and user-directed fetch (`Claude-User`) stays allowed. Known limit: a crawler that
obeys the disallow never fetches a page, so it never sees the noindex header. A URL can still be
listed bare from inbound links until the gate is up. After that, the Access login page is what
any crawler gets.

## What is not known yet (GAP), and how it gets answered

- **GAP: whether the deploy token can configure Access.** The only Cloudflare credential this
  machine can use is the Actions secret `CLOUDFLARE_API_TOKEN`, minted 22 Jun for Pages deploys.
  The Cloudflare MCP from the 20 Aug grant is not loaded in headless runs. The read-only
  `.github/workflows/cloudflare-access-probe.yml` answers this. It checks whether a Zero Trust
  organisation exists, and whether the token can list Access apps, identity providers and the
  Pages project's domains. It prints status and error codes, never the token or account id.
  *Answered, 19 Nov 16:45Z (Actions run 44569003701): it cannot, because Access is not enabled on
  the account at all. All three Access endpoints answer 403 `access.api.error.not_enabled`, and
  the Zero Trust organisation endpoint answers 403. The token does read the Pages project, which
  serves exactly `poesys-net.pages.dev` and `poesys.net`, so the route table above is the whole
  scope. The first step is the director's Zero Trust sign-up, raised as `for_the_director` row
  `the-site-login-you-ruled-on-19`.*
- **GAP: whether Zero Trust sign-up asks for a payment card.** Sign-up chooses a team name and a
  plan in the dashboard. If it asks for a card, even on Free, that screen is the director's, and
  it is raised as one plain instruction.
- **If the token lacks Access permissions,** a token with *Access: Apps and Policies: Edit* and
  *Access: Organizations, Identity Providers, and Groups: Edit* is the director's to mint. That is
  a credential, and credentials stay his.

## What the gate breaks inside the project, to fix in the same change

Machine readers that fetch `https://poesys.net` unauthenticated will get the login page instead
of the content once the gate is up:

- the deploy workflow's "Assert the deployed commit is what a reader gets"
- `tools/assert_deployed_bytes_are_served.py`
- `tools/retired_paths_still_served.py`
- `background/process_run_complete.py`'s post-publish readers
- `tools/insight_challenge.py`, `tools/couple_w2_11_d5.py` and `tools/generate_project_state.py`

The fix is an Access **service token** (client id and secret headers) held as Actions and local
secrets. That keeps the checks able to fail for the right reason. Lifting the gate for machines
would be the side door the ruling forbids.

## Readings

Before the gate (19 Nov 15:58Z, unauthenticated `curl` with a cache-buster):

| route | status |
|---|---|
| `https://poesys.net/` | 200 |
| `https://poesys.net/data/dashboard.json` | 200 |
| `https://poesys-net.pages.dev/` | 200 |
| `https://www.poesys.net/` | no answer (does not resolve) |

Done means every one of these routes, plus a preview URL, refuses an unauthenticated fetch, and
the director reports one successful login.

## How to reverse it

Delete the Access applications for `poesys.net` and `poesys-net.pages.dev`, and turn off the
preview access policy in the Pages project. Revert the robots and `_headers` lines. Nothing else
changes.
