"""BEHIND, NEVER FROZEN, NEVER SILENT — the published provenance/staleness banner.

DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10, properties 1 and 3, sequenced to the front by
DIRECTOR_PRIORITY_BUILD_THE_BREATHING_2026-08-10.

Verbatim: *"If even the scoped gate is red, the site keeps serving the last verified snapshot
under a dated banner ('verification paused since T; showing run R'). A visitor can always tell
WHAT they are seeing and HOW current it is. Freshness claims are provenance claims; fake-fresh
(re-stamping stale runs) remains the cardinal sin."*

THE DEFECT THIS NAMES
---------------------
When the gate reds, the publisher returns before `git_commit_push`, so the live site keeps
serving the last pushed snapshot. That half was always right — last-known-good is the correct
thing to serve. What was missing is that the site said NOTHING about it. The published stamp
read 2026-08-09T12:41:51Z for 25 hours, and from outside, a site frozen because verification
is paused is indistinguishable from a site frozen because the machine is dead, or from a site
that is simply current. Silence is the defect, not the staleness.

So this module publishes the one thing that must never freeze: the statement of how frozen
everything else is.

TWO STATES, AND WHAT MAY MOVE IN EACH
-------------------------------------
  VERIFIED — a publish completed with the scoped gate green. `last_verified` and `showing_run`
             advance to that run. `paused_since` clears.
  PAUSED   — the scoped gate is red. `last_verified` and `showing_run` MUST NOT MOVE (they
             describe a run that is still the newest verified one, and it is still what the
             visitor is looking at). `paused_since` is stamped ONCE, at the transition.

THE CARDINAL SIN, MECHANISED (R15)
----------------------------------
"Fake-fresh" is not prevented here by intent or by convention — it is prevented by the two
recorders having disjoint write sets, and by tests that mutate each one and assert the other's
fields are byte-identical (`tests/background/test_publish_provenance.py`):

  * `record_verified()` is the ONLY writer of `last_verified` / `showing_run`, and it is
    reachable only from a completed publish. No caller can advance freshness without one.
  * `record_paused()` cannot touch either. Called a hundred times, the served run's stamp does
    not move by a byte — which is the property the four-times-republished figure violated.
  * `paused_since` is stamped at the TRANSITION only. Re-stamping it every cycle would be the
    same sin wearing the opposite coat: a banner reading "paused since 30 seconds ago" for 25
    hours is a fresh-looking lie about staleness. A test asserts it survives repeated calls.

WHY IT IS ITS OWN FILE, AND ITS OWN PUSH
----------------------------------------
`site/data/publish_provenance.json` is deliberately NOT a key inside `dashboard.json`. The
banner has to reach origin on exactly the cycles the dashboard MUST NOT — the whole point is
that the numbers stay put while the statement about them updates. Sharing a file would make
publishing the banner mean publishing the unverified numbers with it. The publisher therefore
commits this path alone on a red cycle (see
`process_run_complete._publish_provenance_banner`), the same narrow-pathspec shape as the
liveness heartbeat refresh.

REUSE: background/publish_provenance.py
CLASS: CUSTOM
INDEX: searched "provenance", "freshness", "staleness banner" -- 22 rows mention provenance
       and none covers this. `tools.map_assertion_provenance` (AO11) is the closest name and
       a different subject entirely: when a MATURITY-MAP CELL was asserted, internal, never
       rendered to a visitor. The published-surface half is `site/data/dashboard.json`'s
       `meta` block, which records when a snapshot was GENERATED and has no concept of
       whether it was VERIFIED or of a pause -- and it is precisely the file this one must
       not share, because the banner has to publish on the cycles the dashboard must not.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
PROVENANCE_FILE = PROJECT_DIR / "site" / "data" / "publish_provenance.json"

SCHEMA_VERSION = 1
STATE_VERIFIED = "verified"
STATE_PAUSED = "paused"

# Bounded: the banner is a page, not a directory listing (same reasoning as
# PUBLISH_GATE_MAX_CITED_FINDINGS).
MAX_ANNOTATED_REDS = 8


# ===========================================================================================
# THE PUBLISHED PROVENANCE MUST BE A REAL RUN AND A REAL COMMIT (2026-08-11, director P1)
# ===========================================================================================
# THE DEFECT THIS CLOSES, observed on the live surface:
#
#   [08:58Z] Provenance banner: Verification paused since 2026-08-11T08:58:57Z
#            . showing run run_verified.json (last verified 2026-08-11T08:58:57Z)
#   [08:58Z] Provenance banner published to origin.
#
# `run_verified.json` is a TEST FIXTURE literal. A fabricated run id was, for a period, the
# public claim about how current this site was. The gate being wedged is an availability
# problem; this is an INTEGRITY problem, and it published in silence.
#
# WHY THIS ASSERTS ON THE VALUE, NOT ON THE WRITER. The mechanism that put that literal there
# is NOT ESTABLISHED (WORKER_FINDING_TEST_FIXTURE_VALUES_REACHED_THE_LIVE_PUBLISH_STATE_
# 2026-08-11 rules out the three obvious candidates and says so). A control keyed to a writer
# would therefore be a control keyed to a guess. This one asks the only question that has a
# knowable answer -- *is what we are about to publish a real run and a real commit?* -- so it
# closes the class whatever the source turns out to be, and its refusals will name the cycle
# for whoever runs the mechanism down.
#
# FAIL-CLOSED, deliberately (R15, and the director's "an honest pause outranks a full page").
# If the repo cannot be asked whether a commit exists, the answer is REFUSE, not publish: an
# unavailable check is a FAILED check. The cost of that direction is a pause the banner is
# built to state honestly. The cost of the other direction is a false public claim.

#: `run_output_<sha>_<UTC stamp>.json` -- the only shape the runner ever produces.
RUN_ID_RE = re.compile(r"^run_output_[0-9a-f]{7,40}_\d{8}T\d{6}Z\.json$")
#: An abbreviated-or-full hex sha. Shape only; existence is checked separately.
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")

# Named fixtures seen on, or adjacent to, the live surface. The regexes above already reject
# every one of these, and they are listed ANYWAY: a shape check silently admits the next
# fixture that happens to look real, and this list is what makes the intent legible and
# testable. Belt and braces on the one surface where a wrong value is a public lie.
FIXTURE_VOCABULARY = frozenset({
    "run_verified.json", "run_paused.json", "abc1234", "deadbeef", "unknown",
    "v" * 40, "0" * 40, "1234567", "fixture", "dummy", "example",
})


class ProvenanceRefused(Exception):
    """A provenance value that must never reach a published surface. Loud by construction."""


def _commit_exists(sha: str, repo_root: Path = None) -> bool:
    """Does `sha` name a real commit in this repo? Unavailable git => False (fail-closed)."""
    try:
        proc = subprocess.run(
            ["git", "cat-file", "-e", sha + "^{commit}"],
            cwd=str(repo_root or PROJECT_DIR),
            capture_output=True, timeout=30,
        )
        return proc.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


#: What the page has to be able to say about the run it names. See `population_of`.
POPULATION_FIELDS = ("accounts", "bills", "total_revenue_gbp")

#: Where a run artefact would live if it were retained.
RUN_DIR = PROJECT_DIR / "docs" / "reports"


def population_of(run: dict) -> dict:
    """The three counts that make a published surface CHECKABLE against the run it came from.

    WHY A POPULATION AND NOT THE RUN ITSELF (2026-08-31). The provenance record already names the
    run -- `showing_run.run_id` -- and already refuses a run_id that is fixture vocabulary or a
    git_commit that names no commit. It never asked whether the RUN existed. Measured on
    `origin/main`: the page published `verification_state: "verified"` and
    `showing_run: run_output_5ccc0e0c8_20260831T130500Z.json`, and **that file is in no commit**.
    The newest run artefact the tree tracks is dated 18 June; the newest publish commit that
    carried one is 2026-07-29. So the public claim was "verified, showing run X" where X was
    unfindable, and the derived surfaces had drifted a month ahead of the inputs on origin --
    `site/data/customers.json` publishing 251 households while `run_output_latest.json` in the same
    commit holds 19.

    RETAINING THE RUN IS NOT THE ANSWER: the live artefact is **27 MB**, and committing one per
    publish would put a gigabyte of machine output into git within a month. That is why nobody's
    pathspec sweeps it, and no amount of discipline will change the arithmetic.

    So the page carries the run's POPULATION instead -- three numbers, a few dozen bytes -- and the
    claim becomes falsifiable without the artefact: `site/data/customers.json` must publish the
    account count this says the run had. A reader can check the page against itself. That is
    strictly weaker than reproducing the run and strictly stronger than naming a file nobody can
    open, and the difference between those two is the whole of this change.
    """
    pcl = run.get("per_customer_lifetime") or {}
    return {
        "accounts": len(pcl),
        "bills": len(run.get("bills") or []),
        "total_revenue_gbp": round(float(run.get("total_revenue_gbp") or 0.0), 2),
    }


def run_is_retained(run_id, root: Path = None) -> bool:
    """Is the named run artefact actually present? Absent/unreadable reads as NOT retained."""
    if not isinstance(run_id, str) or not run_id:
        return False
    try:
        return (Path(root or RUN_DIR) / run_id).is_file()
    except (OSError, ValueError):
        return False


def publishable_violations(state, *, repo_root: Path = None, check_commit_exists=True) -> list:
    """Every reason `state` must not be published. Empty list == publishable.

    Checks the freshness stamps only. `paused_since`/`annotation` carry no run identity, and a
    PAUSED state with nothing ever verified (`showing_run is None`) is legitimate -- it is what
    a fresh machine looks like -- so it is not a violation to publish it.
    """
    out = []
    if not isinstance(state, dict):
        return ["provenance is not an object: {!r}".format(type(state).__name__)]

    for field in ("showing_run", "last_verified"):
        stamp = state.get(field)
        if stamp is None:
            continue
        if not isinstance(stamp, dict):
            out.append("{}: not an object".format(field))
            continue

        run_id = stamp.get("run_id")
        if not isinstance(run_id, str) or not RUN_ID_RE.match(run_id):
            out.append("{}.run_id is not a real run id: {!r}".format(field, run_id))
        elif run_id in FIXTURE_VOCABULARY:
            out.append("{}.run_id is fixture vocabulary: {!r}".format(field, run_id))

        sha = stamp.get("git_commit")
        if not isinstance(sha, str) or not COMMIT_RE.match(sha):
            out.append("{}.git_commit is not a sha: {!r}".format(field, sha))
        elif sha in FIXTURE_VOCABULARY:
            out.append("{}.git_commit is fixture vocabulary: {!r}".format(field, sha))
        elif check_commit_exists and not _commit_exists(sha, repo_root):
            out.append("{}.git_commit names no commit in this repo: {!r} (an unavailable git "
                       "reads as absent -- fail-closed)".format(field, sha))

        # THE PAGE MUST BE ABLE TO SAY WHAT THE RUN CONTAINED (2026-08-31). Everything above
        # checks the run's NAME; nothing checked that the name meant anything. A stamp naming a
        # run nobody can open is publishable only if it also carries the run's population, which
        # is what makes the claim checkable against the surfaces shipped beside it. See
        # `population_of` for the measurement that forced this and why the artefact itself cannot
        # be retained.
        pop = stamp.get("population")
        if not isinstance(pop, dict):
            out.append("{}.population is missing: the page would name a run and say nothing "
                       "about what was in it, so no reader could check the figures beside it "
                       "against it".format(field))
        else:
            missing = [k for k in POPULATION_FIELDS if not isinstance(pop.get(k), (int, float))]
            if missing:
                out.append("{}.population is incomplete: {}".format(field, ", ".join(missing)))
            elif not pop.get("accounts"):
                out.append("{}.population.accounts is zero -- a publish of nothing is not a "
                           "verification".format(field))
        if "run_retained" not in stamp:
            out.append("{}.run_retained is unstated: whether the run is in the tree is the "
                       "difference between a reproducible claim and a citation, and the page "
                       "may not leave a reader to assume the better one".format(field))
    return out


def dashboard_meta_violations(meta, *, repo_root: Path = None, check_commit_exists=True) -> list:
    """Every reason a `dashboard.json` `meta` block must not be published. Empty == publishable.

    THE GENERALISATION (2026-08-11, director: "generalise to anywhere else a test fixture could
    reach a published surface"). Measured: `tests/conftest.py::_PROTECTED_WRITE_PATHS` guards 9
    paths, of which exactly ONE is a published surface -- while the publisher commits fourteen.
    The guard was extended one file at a time, to whichever file happened to get caught.

    A blanket directory guard is NOT the answer and that is not a guess: the earlier author
    measured that protecting `site/data/` reds the generator tests that legitimately rewrite
    those files, which is why the list is scoped to one path. So the general control cannot live
    at the write.

    It lives here instead, on the VALUE, where a legitimate generator write and a fixture write
    are finally distinguishable: `meta.source_file` and `meta.git_commit` are the same identity
    claim the provenance makes, in the file that carries every published FIGURE. A dashboard
    stamped with a run that does not exist is a page of numbers attributed to nothing.
    """
    out = []
    if not isinstance(meta, dict):
        return ["dashboard meta is not an object: {!r}".format(type(meta).__name__)]

    src = meta.get("source_file")
    if src is not None:
        if not isinstance(src, str) or not RUN_ID_RE.match(src):
            out.append("meta.source_file is not a real run id: {!r}".format(src))
        elif src in FIXTURE_VOCABULARY:
            out.append("meta.source_file is fixture vocabulary: {!r}".format(src))

    sha = meta.get("git_commit")
    if sha is not None:
        if not isinstance(sha, str) or not COMMIT_RE.match(sha):
            out.append("meta.git_commit is not a sha: {!r}".format(sha))
        elif sha in FIXTURE_VOCABULARY:
            out.append("meta.git_commit is fixture vocabulary: {!r}".format(sha))
        elif check_commit_exists and not _commit_exists(sha, repo_root):
            out.append("meta.git_commit names no commit in this repo: {!r}".format(sha))
    return out


def assert_publishable(state, *, repo_root: Path = None, check_commit_exists=True) -> None:
    """Raise `ProvenanceRefused` if `state` must not be published. Loud, never a bare bool."""
    violations = publishable_violations(
        state, repo_root=repo_root, check_commit_exists=check_commit_exists)
    if violations:
        raise ProvenanceRefused(
            "REFUSING TO PUBLISH A FALSE PROVENANCE -- " + "; ".join(violations))


def _now_iso(now=None) -> str:
    return (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _blank() -> dict:
    return {
        "schema": SCHEMA_VERSION,
        "verification_state": STATE_PAUSED,
        "showing_run": None,
        "last_verified": None,
        "paused_since": None,
        "annotation": {"open_findings": 0, "nonblocking_reds": [], "checked_at": None},
        "written_at": None,
    }


def read(path: Path = None) -> dict:
    """Current provenance. A missing or corrupt file reads as PAUSED with nothing verified.

    FAIL-CLOSED on purpose: the honest reading of "I cannot tell you what was verified" is
    "nothing is verified", never "everything is fine". A corrupt file that read as VERIFIED
    would publish a fresh-looking banner over an unknown state — the cardinal sin by accident.
    """
    path = path or PROVENANCE_FILE
    try:
        loaded = json.loads(path.read_text())
    except (OSError, ValueError):
        return _blank()
    if not isinstance(loaded, dict):
        return _blank()
    base = _blank()
    base.update(loaded)
    return base


def _write(state: dict, path: Path = None, now=None) -> dict:
    path = path or PROVENANCE_FILE
    state["schema"] = SCHEMA_VERSION
    state["written_at"] = _now_iso(now)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    return state


def record_verified(*, run_id, git_commit, generated_at=None, population=None,
                    path: Path = None, now=None) -> dict:
    """A publish completed with the scoped gate GREEN. The ONLY freshness advance there is."""
    state = read(path)
    stamp = {
        "run_id": run_id,
        "git_commit": git_commit,
        "generated_at": generated_at or _now_iso(now),
        "verified_at": _now_iso(now),
        # STATED, NEVER ASSUMED. `population` makes the claim checkable against the surfaces
        # published beside it; `run_retained` says whether the run itself can be opened. A
        # publisher that cannot supply the population is refused below rather than allowed to
        # publish a name with nothing behind it.
        "population": dict(population) if isinstance(population, dict) else None,
        "run_retained": bool(run_is_retained(run_id)),
    }
    # REFUSE AT THE WRITE, as well as at the commit (below, in the publisher). This is the
    # shape check only -- deliberately NOT the commit-existence check, because this runs inside
    # the publish path and must stay cheap and repo-independent. It costs nothing and it turns
    # "a fixture reached the file" into a loud failure at the moment it happens, which is the
    # difference between a diagnosable event and the silent one that started this.
    assert_publishable({"showing_run": stamp, "last_verified": stamp},
                       check_commit_exists=False)
    state["verification_state"] = STATE_VERIFIED
    state["showing_run"] = stamp
    state["last_verified"] = stamp
    state["paused_since"] = None
    # AND THE REASON GOES WITH IT (2026-08-26). Clearing `paused_since` alone left the sentence
    # that EXPLAINED the pause sitting on the public endpoint after the pause was over. Observed:
    # `poesys.net/data/publish_provenance.json` served `paused_reason = "scoped publish-path suite
    # red at git=4683e68f7; blocking tests: ..."` -- a 2026-08-24 red -- alongside
    # `paused_since: null` and `verification_state: verified`, through every green publish for two
    # days. A reader fetching that file was told the gate was red and green in the same object.
    # R11's no-orphan-transitions clause read the other way round: the release of a hold must
    # clear everything the hold asserted, not just the flag the code happens to check.
    state["paused_reason"] = None
    return _write(state, path, now)


def record_paused(*, reason=None, path: Path = None, now=None) -> dict:
    """The scoped gate is RED. Stamps the pause once; moves no freshness field, ever.

    Returns the written state. `paused_since` is preserved across repeated calls — see the
    module docstring on why re-stamping it is the same sin in the opposite direction.
    """
    state = read(path)
    state["verification_state"] = STATE_PAUSED
    if not state.get("paused_since"):
        state["paused_since"] = _now_iso(now)
    if reason:
        state["paused_reason"] = str(reason)[:400]
    # showing_run / last_verified deliberately untouched: what the visitor is looking at has
    # not changed, and saying it has would be the fake-fresh sin.
    return _write(state, path, now)


def record_annotation(*, open_findings=None, nonblocking_reds=None, path: Path = None,
                      now=None) -> dict:
    """The honest repo-health line: "published with N open findings — see health".

    Separate from the two state recorders because it is a different KIND of claim: those say
    how current the numbers are, this says what is known to be wrong elsewhere while they are
    published. It never touches `verification_state` — an annotation must not be able to
    pause or unpause the site, or a noisy finding count would become an outage.
    """
    state = read(path)
    annotation = dict(state.get("annotation") or {})
    if open_findings is not None:
        annotation["open_findings"] = int(open_findings)
    if nonblocking_reds is not None:
        reds = [str(r) for r in nonblocking_reds]
        annotation["nonblocking_reds"] = reds[:MAX_ANNOTATED_REDS]
        annotation["nonblocking_reds_total"] = len(reds)
    annotation["checked_at"] = _now_iso(now)
    state["annotation"] = annotation
    return _write(state, path, now)


def banner_line(state=None, now=None) -> str:
    """The sentence a visitor reads. Rendered client-side too (site/assets/freshness-banner.js);
    this is the same sentence in Python so the publisher can log exactly what the site says and
    a test can assert the two agree rather than drifting apart."""
    state = read() if state is None else state
    showing = state.get("showing_run") or {}
    run = showing.get("run_id") or "unknown"
    if state.get("verification_state") == STATE_VERIFIED:
        # WHAT THE RUN CONTAINED, AND WHETHER IT CAN BE OPENED (2026-08-31). "showing run X" was
        # a citation to a 27 MB artefact that is not retained, and for a month X named nothing at
        # all. The population makes the sentence checkable against the figures beside it; the
        # not-retained clause stops a reader assuming they could go and look.
        pop = showing.get("population") or {}
        detail = ""
        if pop.get("accounts"):
            detail = " over {:,} accounts and {:,} bills".format(
                int(pop["accounts"]), int(pop.get("bills") or 0))
        if showing.get("run_retained") is False:
            detail += " (the run itself is not retained in the repository)"
        return "Verified {} · showing run {}{}".format(
            showing.get("verified_at") or "unknown", run, detail)
    since = state.get("paused_since") or "unknown"
    return "Verification paused since {} · showing run {} (last verified {})".format(
        since, run, (state.get("last_verified") or {}).get("verified_at") or "never")


# ── WHICH PAGES OWE A BANNER — DERIVED, NEVER TYPED ──────────────────────────
# WHY THIS EXISTS AT ALL (2026-08-21, WORKER_FINDING_THE_FRESHNESS_BANNER_REACHES_NO_PAGE).
# The rule used to be a hand-typed list of five doors -- company, proof, world, now, project.
# `03dd8c49e` deleted all five on the director's ruling ("the five tabs are the site now"), and
# the check went on asking those five names for a further day. Its red then said FileNotFoundError
# -- a MISSING PAGE -- while the property it exists to protect was in fact violated: the banner
# was on no page at all, of any name. A control that is red for the wrong reason is not a louder
# control, it is an ABSENT one, because nobody reading its red learns the thing it knows.
#
# So the population is DERIVED from the shipped site: a page that fetches anything under `data/`
# is a page that renders live figures, and a page that renders live figures must be able to tell
# a visitor how old they are. That is the property in the director's own words, and it is the
# same repair `03dd8c49e` applied to the other 87 controls it reddened -- "every one is now
# DERIVED from the built site". This one was missed because nothing selected it.
#
# THE EXEMPTION REGISTER IS SHRINK-ONLY AND SELF-FALSIFYING. An exemption naming a page that is
# not a live-data page (or does not exist) is a VIOLATION, not a no-op -- otherwise the register
# becomes the place a page goes to escape the rule, and a stale entry is indistinguishable from
# a live one. Same discipline as `site/ia_register.py`'s debt registers.
BANNER_ASSET = "assets/freshness-banner.js"

# WHAT COUNTS AS "RENDERS LIVE FIGURES", AND WHY IT IS NOT `fetch(`.
# The first draft of this matched `fetch("…data/x.json")` and would have been FAIL-OPEN on the
# very page that motivated it: `site/company/index.html` at `03dd8c49e^` read all five of its
# feeds through a one-line wrapper -- `function jget(url){ return fetch(url+"?t="+Date.now()); }`
# -- and contains the literal `fetch(` exactly once, on a URL it never names. A detector that
# knows ONE CALL SHAPE is a detector any refactor can walk out of silently.
#
# So the subject is the REFERENCE, not the call: a published JSON artefact named anywhere in the
# page's script. `href="…"` / `src="…"` attribute values are stripped FIRST, because a page may
# legitimately LINK to an evidence file ("see capabilities.json →") without rendering a figure
# from it, and that link is not a freshness claim. Over-inclusion here is cheap (a banner is
# never wrong to carry); under-inclusion is the defect being closed.
_ATTR_URL_RE = re.compile(r"""\b(?:href|src)\s*=\s*["'][^"']*["']""")
_DATA_REF_RE = re.compile(r"""(?:^|["'./])(?:data|state)/[A-Za-z0-9_./-]+\.json""")

BANNER_EXEMPT: dict[str, str] = {
    "snapshots/DASHBOARD_20260623_120151.html": (
        "a DATED ARCHIVE, not a live door: the filename is its own timestamp, it is off the nav "
        "and out of the sitemap, and its fetches resolve to a data/ directory that does not "
        "exist beside it. A freshness banner here would state the age of figures the page is "
        "not showing. It is exempt because it is frozen ON PURPOSE and says so in its own URL."
    ),
}


def _site_dir(site: Path = None) -> Path:
    return (PROJECT_DIR / "site") if site is None else Path(site)


def _renders_live_figures(text: str) -> bool:
    """Does this page's markup read a published JSON artefact for display?"""
    return bool(_DATA_REF_RE.search(_ATTR_URL_RE.sub("", text)))


def live_data_pages(site: Path = None, exempt: dict = None) -> tuple:
    """Every shipped page that renders live figures, as site-relative posix paths.

    Derived by reading the pages, so a page added tomorrow is in the population tomorrow and a
    page deleted by a ruling leaves it without anyone re-typing a list.

    `exempt` defaults to the SHIPPED register. It is a parameter because the register describes
    this site and nothing else -- a caller measuring a different tree (a fixture, or the bytes at
    a pre-ruling commit) must be able to say so, rather than have the shipped list silently
    misapply. The shipped assertion passes nothing and therefore checks the real register."""
    root = _site_dir(site)
    exempt = BANNER_EXEMPT if exempt is None else exempt
    found = []
    for page in sorted(root.rglob("*.html")):
        rel = page.relative_to(root).as_posix()
        if rel in exempt:
            continue
        try:
            text = page.read_text(encoding="utf-8")
        except OSError:
            continue
        if _renders_live_figures(text):
            found.append(rel)
    return tuple(found)


def banner_adoption_violations(site: Path = None, exempt: dict = None) -> list:
    """Pages that render live figures and cannot say how old they are.

    FAIL-CLOSED THREE WAYS (R15), because this control's natural failure is to find nothing and
    call that clean -- which is precisely how it spent a day being wrong:

      * VACUITY FLOOR. An empty derived population is a VIOLATION, not a pass. If the site has
        no live-data page the derivation is broken (or pointed at the wrong tree), and a rule
        about live-data pages that has no subject proves nothing about the site.
      * THE SRC IS RESOLVED ON DISK. `freshness-banner.js` present as a substring is not the
        property -- a wrong hop count (`../assets/` from a two-deep page) is a silent 404, the
        exact fail-silent the layer's own docstring names as its cardinal failure mode. The
        reference is resolved against the page's own directory and the target must exist.
      * STALE EXEMPTIONS FAIL. An entry naming a page that is absent, or that no longer fetches
        live data, is reported -- an exemption register nobody can be wrong in is a hole.
    """
    root = _site_dir(site)
    exempt = BANNER_EXEMPT if exempt is None else exempt
    problems = []

    pages = live_data_pages(root, exempt)
    if not pages:
        problems.append(
            f"no live-data page found under {root} -- the banner rule has no subject, which "
            "means the derivation is broken, not that the site is clean")

    for rel in pages:
        page = root / rel
        text = page.read_text(encoding="utf-8")
        srcs = re.findall(r"""<script[^>]*\bsrc=["']([^"']+)["']""", text)
        hits = [s for s in srcs if s.split("?")[0].endswith("freshness-banner.js")]
        if not hits:
            problems.append(
                f"{rel} fetches live data and loads no freshness banner -- a visitor cannot "
                "tell how old its figures are")
            continue
        for src in hits:
            # ROOT-ABSOLUTE AND PAGE-RELATIVE ARE BOTH LEGAL, and both are on this site's record:
            # the five doors retired by `03dd8c49e` all wrote `/assets/freshness-banner.js`, while
            # today's pages follow the `../brand/brand.css` hop-count convention beside them.
            # Resolving an absolute src against the PAGE's directory reported every one of those
            # five as a broken link -- a false positive that would have made this control red on
            # a tree where the property held. The doc root is the site root; resolve there.
            ref = src.split("?")[0]
            base = root if ref.startswith("/") else page.parent
            target = (base / ref.lstrip("/")).resolve()
            if not target.is_file():
                problems.append(
                    f"{rel} references the banner at {src!r}, which resolves to a file that "
                    "does not exist -- a wrong hop count is a silent 404")

    for rel in sorted(exempt):
        page = root / rel
        if not page.is_file():
            problems.append(
                f"BANNER_EXEMPT names {rel}, which is not a page on this site -- a stale "
                "exemption is a hole nobody can see")
            continue
        text = page.read_text(encoding="utf-8")
        if not _renders_live_figures(text):
            problems.append(
                f"BANNER_EXEMPT names {rel}, which renders no live figure -- it was never in "
                "the population, so the exemption claims credit for nothing")

    return problems
