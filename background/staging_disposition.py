"""Canonical staging-disposition detection — the ONE definition of the mis-park anti-pattern
(2026-07-20). Used by BOTH the supervisor draw (`_real_staged_instructions` → the tick SEES and
SELF-RECOVERS mis-parked actionable work) AND the deadman `[BLOCKED]` net (→ it also pages fast).
Single source of truth so the self-recovery and the alarm can never disagree.

WHY THIS EXISTS — the 2026-07-20 3-hour silent stall. `docs/staging/in_progress/` is ONLY for items
BLOCKED on a wall (a genuinely-open sub-item + what unblocks it); it is deliberately EXCLUDED from the
supervisor draw AND (before this) from the deadman queued-work scan. A worker tick consumed two
director steers and PARKED them there declaring their open sub-items "authorised NOW" — actionable
work, not blocked — which it never executed. The draw could not see it (in_progress/ excluded) and the
tick rested over it; nothing paged for 3h except the weak commit-clock STALL. Making the tick itself
DRAW such work (this module, wired into the draw) is the durable fix: it self-recovers instead of
relying on an alarm plus a human.

THE ANTI-PATTERN IS WORKER-LEGIBLE — it keys on the workers' OWN disposition-banner language, not a
fuzzy read of arbitrary prose:
  - a WORKER-written disposition banner (`[IN-PROGRESS DISPOSITION ...]`), AND
  - an actionable-now marker (the worker itself declared the open sub-item doable NOW).
NOT flagged: director-parked multi-part items (no worker banner) and genuinely-blocked worker parks
(a real wall — "awaiting director", "director-reserved", not "authorised NOW"). So a legitimately
parked-blocked item (e.g. a done analysis whose only remainder is a director [ACT]) stays quiet.
"""
from __future__ import annotations

from pathlib import Path

# The worker-written disposition banner (lower-cased match). Director-authored staged docs do not
# carry this — it is written by a worker tick when it parks a multi-part item.
WORKER_DISPOSITION_BANNER = "[in-progress disposition"

# Markers by which a worker itself declared the open sub-item ACTIONABLE NOW (not blocked). If a
# worker wrote one of these AND then parked the doc, the work is mis-parked (invisible but doable).
ACTIONABLE_NOW_MARKERS = (
    "authorised now", "authorized now",
    "discover/frame, authorised", "discover/frame, authorized",
    "discover-workable", "workable now", "actionable now",
)

_HEAD_CHARS = 1500  # the banner/disposition sits at the very top of the doc


def misparked_actionable_in_progress(in_progress_dir: Path) -> list[str]:
    """Basenames of in_progress/ docs a worker mis-parked as blocked when their open sub-item is
    actionable NOW. Report-only; NEVER raises (a detection must not crash the draw or the deadman)."""
    try:
        if not in_progress_dir.is_dir():
            return []
        candidates = sorted(in_progress_dir.glob("*.md"))
    except OSError:
        return []
    out: list[str] = []
    for p in candidates:
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:_HEAD_CHARS].lower()
        except OSError:
            continue
        if WORKER_DISPOSITION_BANNER in head and any(m in head for m in ACTIONABLE_NOW_MARKERS):
            out.append(p.name)
    return out


# ---------------------------------------------------------------------------
# The 20:00Z parked-CAMPAIGN blind spot (2026-07-23 NIGHT_ENFORCEMENT ruling ADDENDUM).
#
# A SECOND way the in_progress/ blind spot swallows drawable work, distinct from the worker-mispark
# net above. At 20:00Z a DIRECTOR-authored campaign continuation doc (DIRECTOR_CAMPAIGN_SITE_MODEL_
# SPINE) with an OPEN, explicitly PROCEED-ABLE sub-item (§B, marked "[proceed-able now]") was parked
# into in_progress/. It carries no worker `[IN-PROGRESS DISPOSITION` banner, so the net above misses
# it; its open items are NOT in CAMPAIGN_REGISTER.yaml (SITE_V5 there is `closed`), so
# `_open_campaign_draw` misses it too. The draw saw "nothing drawable" and the tick idled 56+ min
# beside an open campaign -- the system filed its own to-do list into its own blind spot.
#
# Director's named failing test (addendum): "parked-campaign-with-open-items must be drawable ...
# either the classifier reads open items wherever they are parked, or open campaign items are never
# parked into the excluded directory -- pick the mechanism, prove it both ways." MECHANISM (option a):
# the classifier READS the parked doc's OWN language -- a campaign doc that declares a remaining
# sub-item PROCEED-ABLE NOW has drawable work hidden -> surface it so the draw self-recovers.
#
# SELF-TERMINATING (no 2-min re-grant churn -- the anti-pattern CLAUDE.md warns of): a surfaced doc
# leaves the set the moment EITHER the work lands and the doc is archived out of in_progress/, OR the
# campaign is reconciled into an OPEN CAMPAIGN_REGISTER.yaml entry that references it (then the
# register draws it, not this net). A genuinely fully-blocked park carries NO proceed-able marker and
# stays quiet -- so the invariant also FORCES park-honesty: declare a sub-item proceed-able => it gets
# drawn; if it is really blocked, say so (don't claim proceed-able) and it stays parked.

# Positive-sense phrases by which a doc declares a remaining sub-item DRAWABLE NOW. A fully-blocked
# park ("awaiting director", "director-reserved", "cannot land until") carries none of these.
CAMPAIGN_DRAWABLE_MARKERS = (
    "proceed-able", "proceedable",
    "may now proceed",
    "drawable now",
)


def _open_campaign_referenced_docs(register_path: Path) -> set[str]:
    """Basenames referenced by any OPEN campaign in CAMPAIGN_REGISTER.yaml (its ruling/doc/source/dod
    string fields). Such a doc is already drawn via the register, so this net must not double-surface
    it. Fail-open: any read/parse error -> empty set (never suppress a real find on a bad register)."""
    try:
        import yaml  # local import: a detection must never hard-fail the draw on an import error
        doc = yaml.safe_load(register_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return set()
    out: set[str] = set()
    for camp in (doc.get("campaigns") or []):
        if not isinstance(camp, dict):
            continue
        if str(camp.get("status", "")).strip().lower() != "open":
            continue
        for v in camp.values():
            if isinstance(v, str) and v.strip():
                out.add(Path(v.strip()).name)
    return out


def misparked_open_campaign_in_progress(
    in_progress_dir: Path, register_path: Path | None = None
) -> list[str]:
    """Basenames of in_progress/ CAMPAIGN docs that declare a remaining sub-item PROCEED-ABLE NOW
    (drawable work parked in the excluded dir) and are NOT already tracked by an OPEN campaign in the
    register. Whole-doc scan (a campaign's proceed-able §B sits well past the head). Report-only;
    NEVER raises (a detection must not crash the draw or the deadman)."""
    try:
        if not in_progress_dir.is_dir():
            return []
        candidates = sorted(in_progress_dir.glob("*.md"))
    except OSError:
        return []
    tracked = _open_campaign_referenced_docs(register_path) if register_path else set()
    out: list[str] = []
    for p in candidates:
        if p.name in tracked:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        # "is a campaign" keys on the FILENAME or the TITLE/intro (first 200 chars), NOT anywhere in
        # the body -- else any director doc that merely mentions "campaign authority" in prose false-
        # fires. Director campaign docs are named DIRECTOR_CAMPAIGN_* / titled "# ... campaign ...".
        # The proceed-able marker is matched over the WHOLE doc (a campaign's §B sits deep in the body).
        is_campaign = "campaign" in p.name.lower() or "campaign" in text[:200]
        if is_campaign and any(m in text for m in CAMPAIGN_DRAWABLE_MARKERS):
            out.append(p.name)
    return out


# ---------------------------------------------------------------------------
# The waived-mint self-drawable-next-step blind spot (2026-07-24, RUNG-7 planner mint
# `inprogress_mint_next_step_draw_visibility`, FRAME-confirmed on disk).
#
# A THIRD way in_progress/ swallows drawable work, distinct from the two nets above. A worker
# advancing a director-WAIVED planner mint parks it here between sub-steps with a genuinely
# SELF-DRAWABLE next step (no wall — "UNBLOCKS: self", "next drawable BUILD step ... reversible").
# It carries NO `[in-progress disposition` banner (the actionable-net misses it) and is not a
# campaign (the campaign-net keys on the word "campaign" — a mint is not one). So the self-drawable
# BUILD step is invisible to EVERY draw rung. FRAME evidence (2026-07-24): 6 PLANNER_MINTED_* docs
# open in in_progress/, 2 with self-drawable next steps (ssp_negative_lift_cells scope-2,
# value_chain_observation_window_cap) surfaced by NONE of the existing nets -> rungs 1-6 draw
# nothing -> rung-7 fires and MINTS a fresh batch (3 more docs this very tick) while authorised,
# self-drawable work sits parked. That is the treadmill (consumed-not-absorbed) and a candidate
# R17 breach-of-class.
#
# STRUCTURED, not prose (R3 — no fragile free-form-English substring matcher; the primary draw was
# redesigned onto structured fields for exactly this reason). The worker writes ONE canonical,
# machine-legible marker line into the doc's disposition block, mirroring how an atom carries
# `loop_stage`/`blocked_on`. FAIL-CLOSED on both axes: a doc is surfaced ONLY if it carries the
# self-drawable marker AND does not carry the blocked marker; an unmarked doc, or one marked blocked,
# stays parked (a mistaken park costs at most a doable step going undrawn until the marker is added,
# never a walled/director-reserved step being force-drawn).
#
# PARK-HONESTY forcing function (same as the campaign-net's, lines 79-84): mark a next step
# self-drawable => it gets drawn; if it is really walled (director-reserved, CDN/deploy-wait,
# roadmap-gated), mark it blocked and it stays parked. SELF-TERMINATING: the marker leaves the
# drawable set the moment the work lands and the doc is archived out of in_progress/, OR the worker
# flips the marker to blocked when the NEXT step becomes walled — no 2-min re-grant churn while the
# work is genuinely undrawable, and legitimate persistence while it IS drawable is exactly R17.
SELF_DRAWABLE_MARKER = "<!-- supervisor_draw: self-drawable -->"
BLOCKED_MARKER = "<!-- supervisor_draw: blocked -->"


def selfdrawable_mint_in_progress(
    in_progress_dir: Path, register_path: Path | None = None
) -> list[str]:
    """Basenames of in_progress/ docs a worker parked with an explicit SELF-DRAWABLE next-step marker
    (drawable work hidden in the excluded dir) that carry NO blocked marker and are NOT already tracked
    by an OPEN campaign in the register. Whole-doc scan (the marker sits in the disposition block near
    the top, but scanning the whole doc costs nothing and tolerates placement). Report-only; NEVER
    raises (a detection must not crash the draw or the deadman). Fail-closed: unmarked -> parked;
    blocked marker present -> parked (blocked wins over self-drawable if both are somehow present)."""
    try:
        if not in_progress_dir.is_dir():
            return []
        candidates = sorted(in_progress_dir.glob("*.md"))
    except OSError:
        return []
    tracked = _open_campaign_referenced_docs(register_path) if register_path else set()
    out: list[str] = []
    for p in candidates:
        if p.name in tracked:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        if SELF_DRAWABLE_MARKER in text and BLOCKED_MARKER not in text:
            out.append(p.name)
    return out


# ---------------------------------------------------------------------------
# MINT-MARKER BLOCK HYGIENE (2026-07-28, atom `unstated_reason_block_impossible` §3 -- the SIBLING
# of the maturity-map `check_block_hygiene`). DIRECTOR_RULING_BLOCKED_MINT_BATCH §3 verbatim: "Every
# block carries its reason and its release condition, or it is not a valid block. ... A block without
# a recorded reason cannot be escalated, unblocked or judged -- it is invisible work wearing a status.
# Mechanise it so an unstated-reason block cannot be written."
#
# The map check enforces this on a bare YAML atom (which has no prose, so it needs an explicit
# `block_reason` field). A PLANNER_MINTED_*.md is a whole document -- its REASON is structurally the
# doc body (title + Serves + FRAME), always present, unlike a bare atom. The field genuinely AT RISK
# of being missing/unresolvable on a mint is the machine-legible RELEASE CONDITION -- so this check
# enforces a dedicated, non-fragile, STRUCTURED marker line (R3 -- no free-form prose parsing that a
# quote of some OTHER atom's `blocked_on:` could false-trip):
#
#     <!-- BLOCK_RELEASE: <releaser> -- <reason> -->
#
# The releaser (before the em/en/`--` dash) MUST resolve to a canonical MINT_RELEASER_TOKEN (director
# act / self-releasing window) OR an existing maturity-map atom id (an atom-landing releaser, e.g.
# ssp -> W1_6b). The reason (after the dash) MUST be non-empty. FAIL-CLOSED on both axes: a missing
# marker, an unresolvable releaser (the feedback_nonempty_config_referent_existence fail-open -- a
# release condition that resolves to nothing), or an empty reason is a VIOLATION, never waved.
# FAIL-SILENT: an unreadable/undecodable doc is itself a violation (an unparseable marker is a FAILED
# check, never a pass).
#
# SCOPE = a PLANNER_MINTED_*.md parked in in_progress/ that the DRAW treats as blocked: it carries the
# BLOCKED_MARKER, OR carries NEITHER draw marker (unmarked -> the draw fail-closes it to blocked, so
# hygiene must too). A doc marked SELF_DRAWABLE (and not blocked) is NOT a block -> exempt. The
# `PLANNER_MINTED_` prefix scope also excludes DIRECTOR_*/ADVISOR_* SOURCE docs that merely QUOTE a
# marker in prose (they are inbound instructions, not blocks-wearing-a-status) -- the mint doc's own
# named exclusion, achieved by the filename prefix rather than a fragile content sniff.
import re as _re  # local alias -- a detection must never shadow a caller's `re`

MINT_MARKED_PREFIX = "PLANNER_MINTED_"

# Canonical release-condition tokens a mint block may resolve to. MIRRORS the maturity-map
# KNOWN_RELEASER_TOKENS (tests/design/test_maturity_map_facets.py) -- pinned as a subset by
# test_mint_releaser_tokens_superset_of_map -- PLUS two mint-specific releasers the map atoms do not
# use: a self-releasing propose-then-proceed window, and a director ratification of a proposal (a
# director decision beyond a level/build move, e.g. ratifying a ranked gap set or a money-type
# migration). Matched as a lower-cased substring (a long-form releaser that carries its token still
# resolves), so `director_build_open_ledger_entry` resolves via `director_build_open`.
MINT_RELEASER_TOKENS = (
    "director_level_up",
    "director_build_open",
    "build_open",
    "front_open",
    "director_live_run",
    "director_systemd_deploy",
    "coupled_triad_measured",
    "watching_brief",
    "forward_register",
    "propose_then_proceed",
    "propose-then-proceed",
    "director_ratification",
)

_BLOCK_RELEASE_RE = _re.compile(
    r"<!--\s*block_release:\s*(?P<body>.+?)\s*-->", _re.IGNORECASE | _re.DOTALL
)
# The releaser is the text before the FIRST dash separator (em/en/`--`); the reason is the rest.
_RELEASE_SPLIT_RE = _re.compile(r"\s+(?:--|—|–)\s+")


def _load_map_atom_ids() -> set[str]:
    """Best-effort set of live maturity-map atom ids, for resolving an atom-landing releaser. Local
    yaml import so a detection never hard-fails on an environment quirk. Fail-CLOSED semantics: a
    read/parse error returns an EMPTY set, so an atom-id releaser then resolves to nothing and is
    correctly flagged (never fabricates a phantom releaser)."""
    try:
        import yaml
        from pathlib import Path as _P
        map_path = _P(__file__).resolve().parent.parent / "docs" / "design" / "maturity_map.yaml"
        atoms = yaml.safe_load(map_path.read_text(encoding="utf-8")) or []
    except Exception:
        return set()
    return {a.get("id") for a in atoms if isinstance(a, dict) and a.get("id")}


def _releaser_resolves(releaser: str, known_atom_ids: set[str]) -> bool:
    low = releaser.strip().strip("`").lower()
    if not low:
        return False
    if any(tok in low for tok in MINT_RELEASER_TOKENS):
        return True
    # an atom-id releaser (exact id, case-sensitive as ids are) -- allow it appearing as a substring
    # so a `blocked_on: W1_6b_merit_order_reconstruction (its target)` form still resolves.
    return any(aid and aid.lower() in low for aid in known_atom_ids)


def mint_block_hygiene_violations(
    in_progress_dir: Path, known_atom_ids: set[str] | None = None
) -> list[str]:
    """Return violation strings (empty == pass) for every PLANNER_MINTED_*.md parked in in_progress/
    that the draw treats as BLOCKED (BLOCKED_MARKER present, or NO draw marker at all) but does not
    carry a valid `<!-- BLOCK_RELEASE: <releaser> -- <reason> -->` marker: a missing marker, an
    unresolvable releaser, or an empty reason each yield a violation. Self-drawable mints are exempt.
    FAIL-CLOSED (missing/empty/unresolvable -> violation) and FAIL-SILENT (unreadable doc ->
    violation) per §3. Report-only; NEVER raises (a detection must not crash the draw, the deadman,
    or a commit gate)."""
    try:
        if not in_progress_dir.is_dir():
            return []
        candidates = sorted(in_progress_dir.glob(MINT_MARKED_PREFIX + "*.md"))
    except OSError:
        return []
    if known_atom_ids is None:
        known_atom_ids = _load_map_atom_ids()
    violations: list[str] = []
    for p in candidates:
        try:
            raw = p.read_text(encoding="utf-8", errors="strict")
        except (OSError, ValueError, UnicodeDecodeError):
            violations.append(
                f"{p.name}: unreadable/undecodable -- an unparseable mint marker is a FAILED "
                "check (FAIL-SILENT closed), never a pass."
            )
            continue
        low = raw.lower()
        # exempt: a genuinely self-drawable mint is not a block (blocked wins if both are present)
        if SELF_DRAWABLE_MARKER in low and BLOCKED_MARKER not in low:
            continue
        m = _BLOCK_RELEASE_RE.search(raw)
        if not m:
            violations.append(
                f"{p.name}: blocked mint carries no `<!-- BLOCK_RELEASE: <releaser> -- <reason> -->` "
                "marker -- an unstated-reason/-release block is invisible work wearing a status (§3)."
            )
            continue
        body = m.group("body").strip()
        parts = _RELEASE_SPLIT_RE.split(body, maxsplit=1)
        releaser = parts[0].strip()
        reason = parts[1].strip() if len(parts) > 1 else ""
        if not _releaser_resolves(releaser, known_atom_ids):
            violations.append(
                f"{p.name}: BLOCK_RELEASE releaser {releaser[:60]!r} resolves to no known releaser "
                f"{MINT_RELEASER_TOKENS} and no existing atom id -- an unresolvable release condition "
                "cannot be unblocked or judged (§3)."
            )
        if not reason:
            violations.append(
                f"{p.name}: BLOCK_RELEASE carries a releaser but no reason after the dash -- state "
                "why the block exists (§3: a block without a recorded reason cannot be judged)."
            )
    return violations


# ---------------------------------------------------------------------------
# RULING-CONSUMPTION → BLOCK-RELEASE surfacing (2026-07-28, atom
# `ruling_consumption_ledger_release`, DISCOVER §2 (c) + §6). The gap the atom closes: a ruling that
# DECLARES a build-release (via the canonical `LEDGER: <ACTION> <target>` directive line) but whose
# authenticated ledger entry does NOT yet exist must be SURFACED as still-open work, never silently
# archived as consumed -- that silent gap is why three BUILD-opening rulings sat blocked 3+h. This
# detector reads each staged doc, parses its LEDGER directives, and confirms each against the ledger
# via gate_authorization.report_ruling_release (READ-ONLY -- it NEVER writes authority; R16 holds by
# construction). A doc with >=1 UNRELEASED directive is surfaced by basename so the tick draws it
# and either the director acts or the doc states plainly it is unreleased. A doc whose every
# directive is authenticated (or that carries no directive) is NOT surfaced -- no false churn. Fail-
# closed toward surfacing on any read/parse error (an undetectable release is treated as unreleased);
# report-only, NEVER raises (a detection must not crash the draw or the deadman).
def unreleased_ledger_directive_in_staging(
    staging_dirs, ledger_path: Path | None = None
) -> list[str]:
    """Basenames of staged docs carrying a `LEDGER: <ACTION> <target>` directive whose declared
    release is NOT backed by an authenticated ledger entry (block stays -- needs a director act).
    `staging_dirs` is one Path or an iterable of Paths (e.g. staging root + in_progress). De-duped,
    sorted. Never raises."""
    try:
        from background.gate_authorization import parse_ledger_directives, report_ruling_release
    except Exception:
        return []
    if isinstance(staging_dirs, (str, Path)):
        staging_dirs = [Path(staging_dirs)]
    seen: set[str] = set()
    out: list[str] = []
    for d in staging_dirs:
        try:
            d = Path(d)
            if not d.is_dir():
                continue
            candidates = sorted(d.glob("*.md"))
        except OSError:
            continue
        for p in candidates:
            if p.name in seen:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            try:
                if not parse_ledger_directives(text):
                    continue  # no directive at all -> nothing to surface (no false churn)
                report = report_ruling_release(text, ledger_path=ledger_path)
                unreleased = report.get("unreleased") or []
            except Exception:
                # fail-closed toward surfacing: an undetectable release is treated as unreleased
                unreleased = [{"target": "?"}]
            if unreleased:
                seen.add(p.name)
                out.append(p.name)
    return sorted(out)
