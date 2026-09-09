"""Which published sentences a promote-by-copy would falsify.

A **promote-by-copy** moves BYTES onto a canonical path: the newest run of some shape is copied
over `foo.json`, and the dated original stays beside it as `foo_20260908.json`. Nothing else
changes. No constant moves, no import changes, no source file is touched -- the producing module's
`git diff` is EMPTY while the meaning of the page it generates can invert.

That is why this census exists and why it is not a constant checker. `77d92e0d1` found three
instances of one mechanism in one file, and **all three passed every "does the constant point at
the right file" control in the tree**, because every one of those controls is keyed to a constant
and a promotion changes no constant. The question this asks instead is:

    IF THE BYTES AT THIS PATH WERE REPLACED BY A NEWER RUN OF THE SAME SHAPE,
    WOULD ANY SENTENCE ON THE PAGE BECOME FALSE?

## What is in scope, and why it is discovered rather than listed

A path is a promote-by-copy target **iff a dated sibling of the same stem sits beside it**. That is
the mechanical signature of the convention: `value_cycle_ab_s1_three_arm.json` next to
`..._20260908.json` and `..._20260909.json` says, without any register having to say it, that runs
get copied onto this name. Discovering the targets from the tree rather than naming two filenames
is the difference between a control keyed to the PROPERTY and one keyed to today's answer: a fifth
target appearing next month is picked up for free, and a target retired stops being asked about.

## The two things it reports, and why they are separate

**STALE (`--check` fails on these).** A run-identity literal -- a date, a UTC stamp, a world digest
-- written into a module that reads a promote target, where that literal matches NOTHING in the
artefact currently at that path and matches no dated sibling the module also names. The sentence is
false *as the tree stands*, not merely fragile. This leg is what reds on a promotion **with no
source edit at all**, which is the one thing a constant-keyed control structurally cannot do.

**UNANCHORED (reported, not refused).** A run-identity literal in a module that names a promote
target and names no dated sibling of that stem. The literal cannot be describing anything except
"whichever run happens to be there", so it is fragile by construction -- but it may be currently
true, and refusing on currently-true prose would be keying the control to today's answer from the
other end. Reported for disposition; only the stale ones refuse.

A module that names BOTH the canonical path and a dated sibling of the same stem is reported as
MIXED and dispositioned by hand: its literals may legitimately be about the dated pin. Attributing
a literal to the nearer of two paths by line distance was considered and rejected -- proximity is
not reference, and a rule fitted to the one file we already know about is a rule fitted to its
answer.

Comments and docstrings count. A path in a prose comment is a reachability edge, and the third
instance in `77d92e0d1` was a docstring naming the sole witness that satisfied a guard -- true when
written, false the moment that path became a promotion target.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import tokenize
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: Directories censused. `tools/` builds the page feeds and `site/` holds the doors that read them;
#: between them they are every place a sentence about a run reaches a reader. `company/` and
#: `saas/` are deliberately out: they may not read observability artefacts at all, and the
#: epistemic wall is the control for that, not this one.
CENSUS_ROOTS = ("tools", "site")

#: Where an artefact can sit. Discovery walks these rather than the whole tree so that a dated
#: fixture inside `tests/` cannot mint a phantom promote target.
ARTEFACT_ROOTS = ("docs", "site", "data")

#: The stamp shapes a run artefact's filename carries here: `_20260908`, `_20260908b`,
#: `_2026-09-08`, `_2026-08-26T0802Z`, and the run-output form `_<sha>_20260618T054253Z`.
_STAMPED_NAME = re.compile(
    r"^(?P<stem>.+?)[_-]"
    r"(?:[0-9a-f]{7,9}_)?"
    r"(?:20\d{6}[a-z]?|20\d{2}-\d{2}-\d{2})"
    r"(?:T[\dZ:]+)?"
    r"\.json$"
)

#: A canonical name may be the bare stem (`foo.json`) or the `_latest` convention
#: (`run_output_latest.json`). Both mean "whatever run is current sits here".
_CANONICAL_SUFFIXES = ("{stem}.json", "{stem}_latest.json")

#: Tokens that identify WHICH RUN: a calendar date, a UTC wall-clock stamp, the 16-hex world
#: identity these artefacts carry.
_RUN_IDENTITY = re.compile(
    r"(?P<iso>\b20\d{2}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z?)?\b)"
    r"|(?P<compact>\b20\d{6}[a-z]?\b)"
    r"|(?P<clock>\b\d{2}:\d{2}:\d{2}Z\b)"
    r"|(?P<digest>\b[0-9a-f]{16}\b)"
)

#: Words that assert an ORDER or a UNIQUENESS between runs. These are the other half of the class
#: and the half that has no date in it at all: the sentence `77d92e0d1` repaired said the current
#: panel was "a LARGER advantage than the GBP 17,453 below", which carries no run identity and was
#: false anyway because the run below was twenty-one hours LATER. An ordering claim cannot be
#: decided against an artefact by a regex, so these are REPORTED and never refused -- the refusing
#: leg is the dated one.
_ORDERING_CLAIM = re.compile(
    r"\b(?:new(?:er|est)|old(?:er|est)|later|latest|earlier|most recent|"
    r"as it is now|below|above|beside|sole witness|only witness|supersed\w*|"
    r"the run (?:above|below))\b",
    re.IGNORECASE,
)

#: THE NARROWING THAT MAKES THIS A MECHANISM DETECTOR AND NOT A DATE DETECTOR, and the reason it
#: is written down. Run unnarrowed, this census reported 406 "stale" claims across 27 modules --
#: every `# measured 2026-08-19` in any file that happens to also read a run output. That is the
#: aimed-left failure: it matched the concept (a date) rather than the mechanism (a claim about
#: WHICH RUN SITS AT A PROMOTED PATH).
#:
#: A claim is in the class only when ONE string carries BOTH a reference to the target -- its
#: filename, or a module constant bound to it -- AND a run-identity token or an ordering claim.
#: That is what makes the sentence *about* the artefact, and it is the property all three instances
#: in `77d92e0d1` share: a date literal beside "published beside the ... run", a docstring naming
#: the target as a guard's sole witness, and an ordering claim about the panel below.
#:
#: A NARROWING ADDED TO KILL FALSE POSITIVES CAN ONLY HIDE, so it was scored on the NAMED
#: instances and not on the count: `tests/tools/test_promoted_artefact_claim_census.py` replays all
#: three pre-repair instances out of `77d92e0d1^` and requires the narrowed census to catch each
#: one. Losing any of them would mean the narrowing bought its quiet with the defect it exists for.
_CLAIM_NEEDS_BOTH_HALVES = True


def promote_targets(root: Path | None = None) -> list[dict]:
    """Canonical artefact paths that have at least one dated sibling of the same stem.

    Returns one row per target, each carrying the dated siblings that establish it. A path with no
    dated sibling is NOT a target however canonical its name looks: nothing is copied onto it, so
    no reader of it can be pinned to "whichever run is there". Nine such stems exist in this tree
    and none of them is in the class.
    """
    base = PROJECT if root is None else root
    stems: dict[tuple[Path, str], list[Path]] = defaultdict(list)
    for d in ARTEFACT_ROOTS:
        top = base / d
        if not top.is_dir():
            continue
        for p in top.rglob("*.json"):
            m = _STAMPED_NAME.match(p.name)
            if m:
                stems[(p.parent, m.group("stem").rstrip("_-"))].append(p)
    out: list[dict] = []
    for (parent, stem), dated in sorted(stems.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        for shape in _CANONICAL_SUFFIXES:
            canon = parent / shape.format(stem=stem)
            if canon.exists() and canon not in dated:
                out.append({
                    "canonical": canon.relative_to(base).as_posix(),
                    "name": canon.name,
                    "stem": stem,
                    "dated_siblings": sorted(p.name for p in dated),
                })
    return out


def _module_strings(path: Path, source: str | None = None) -> list[tuple[int, str, str]]:
    """Every string a module carries, as `(lineno, kind, text)`.

    `kind` is `comment` or `code`. Docstrings arrive as `code`: a docstring IS a string constant in
    the AST and there is no reason to grade a claim differently for sitting at the head of a body.
    Comments are recovered by tokenising because they are not in the AST at all, and a path in a
    comment is a reachability edge here.
    """
    text = path.read_text(encoding="utf-8") if source is None else source
    out: list[tuple[int, str, str]] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append((node.lineno, "code", node.value))
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                out.append((tok.start[0], "comment", tok.string))
    except (tokenize.TokenError, IndentationError):
        pass
    return sorted(out)


def _artefact_dates(path: Path) -> set[str]:
    """The run-identity tokens an artefact carries AS METADATA -- what run it is, not what it says.

    READING THE WHOLE PAYLOAD MADE THIS LEG VACUOUS, and the number is worth keeping. Graded
    against its raw text, `docs/reports/run_output_latest.json` yields **28,676** distinct
    run-identity tokens -- every customer's `acquisition_date`, every bill date, thousands of them.
    Against a set that size ANY date claim is "supported", so the leg returned quiet for every
    reader of the most-read promote target in the tree. That is a control that is useless without
    ever being fail-open in a way anyone would notice: it went green because it could not fail.

    The repair is structural rather than a threshold. Run identity lives in a payload's shallow
    METADATA -- `generated_at`, `world_identity.digest`, `producing_commit.commit` -- while dates
    that are DATA live inside its collections. So this walks scalars to a shallow depth and refuses
    to descend into lists, which is where per-customer and per-period rows live. `three_arm.json`
    goes from 131 tokens to its handful of stamps; `run_output_latest.json` goes to none, which is
    the correct answer and not a failure: that artefact publishes no run identity at all, so no
    claim about which run it is can be checked against it. `_UNGRADABLE` names that on the surface
    rather than letting an unanswerable question read as a pass.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    found: set[str] = set()

    # WHY THIS CARRIES A ROW IN `substring_source_scan_baseline.json` AND THE ROW IS A DISMISSAL.
    # The code-as-text census flags this function because it runs a regex over strings. Its subject
    # is a JSON PAYLOAD, not Python source -- there is no parse tree to route it through, and
    # `tools/python_code_text.py` would have nothing to offer it. The module's one place that DOES
    # read Python source, `_module_strings`, already goes through `ast` and `tokenize` and is
    # correctly not flagged. Added by hand rather than by `--freeze`, which would have rewritten
    # every other lane's rows from a dirty tree.
    def walk(node, depth: int) -> None:
        if depth > 2 or isinstance(node, list):
            return
        if isinstance(node, str):
            found.update(m.group(0) for m in _RUN_IDENTITY.finditer(node))
        elif isinstance(node, dict):
            for v in node.values():
                walk(v, depth + 1)

    walk(payload, 0)
    # A BARE CLOCK CAN NEVER MATCH AN ARTEFACT WITHOUT THIS, and it took a false STALE to notice.
    # An artefact writes `2026-09-08T21:01:30Z`; prose cites the run as "the 21:01:30Z run". The
    # `\b` before the clock alternative cannot fire inside the full stamp -- the preceding `T` is a
    # word character -- and the ISO alternative consumes the whole thing first anyway. So the
    # clock leg matched prose, never payloads, and every bare-clock citation was stale by
    # construction. Emit the clock sub-token of every full stamp so the two can meet.
    # The same applies to a bare DATE: prose cites "the 2026-09-08 run" and the payload writes
    # `2026-09-08T04:00:00Z`. Both sub-tokens are emitted, so a citation can meet a stamp whichever
    # precision it was written at. Found by the poison round, not by reading the regex.
    for stamp in list(found):
        parts = re.match(r"^(20\d{2}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}Z?)$", stamp)
        if parts:
            date, clock = parts.groups()
            found |= _normalise(date)
            found.add(clock)
            found.add(clock.rstrip("Z") + "Z")
    return found


def _normalise(token: str) -> set[str]:
    """The forms one run-identity token can be written in, so `20260908` matches `2026-09-08`."""
    forms = {token}
    iso = re.match(r"^(20\d{2})-(\d{2})-(\d{2})", token)
    if iso:
        forms.add("".join(iso.groups()))
    compact = re.match(r"^(20\d{2})(\d{2})(\d{2})[a-z]?$", token)
    if compact:
        forms.add("-".join(compact.groups()))
    return forms


def _constants_bound_to(tree: ast.AST, names: set[str]) -> dict[str, str]:
    """Module constants whose value is a path expression ending in one of `names`.

    `THREE_ARM_PATH = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"`
    binds a NAME to a promote target, and prose about the target overwhelmingly refers to it by
    that name rather than by its filename -- `_current_world_bound`'s docstring is the example.
    A census that only matched filenames would miss every one of them.
    """
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        tail = [c.value for c in ast.walk(node.value)
                if isinstance(c, ast.Constant) and isinstance(c.value, str)]
        hit = next((n for n in names if n in tail), None)
        if hit is None:
            continue
        for t in node.targets:
            if isinstance(t, ast.Name):
                out[t.id] = hit
    return out


def _references(text: str, name: str, aliases: set[str]) -> bool:
    """Does this one string refer to the target -- by filename, by stem, or by a bound constant?"""
    if name in text or name.removesuffix(".json") in text:
        return True
    return any(re.search(rf"\b{re.escape(a)}\b", text) for a in aliases)


#: A sentence ends at `. `, `? `, `! `, a newline, or a `--` aside. Crude on purpose: the unit only
#: has to be small enough that "the artefact and the claim are in the same breath" means something.
_SENTENCE_SPLIT = re.compile(r"(?<=[.?!:;])\s+|\n|\s--\s|\s—\s")


def _sentences(text: str) -> list[str]:
    """THE CLAIM UNIT, and the second narrowing this census needed.

    A module docstring is ONE `ast.Constant` -- two hundred lines of it. Scanning that as a single
    string paired every date in the file's history with every artefact named anywhere in it, and
    produced eight of the first ten hits on `generate_value_arms_data` alone, all of them the file's
    own REUSE header sitting near an unrelated date. The question the census asks is whether a
    SENTENCE becomes false, so the sentence is what has to carry both halves.
    """
    return [s for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def census(root: Path | None = None, sources: dict[str, str] | None = None) -> dict:
    """Every claim about WHICH RUN sits at a promote-by-copy target, graded against the bytes.

    A module is a READER of a target when it names the target's filename anywhere -- a `Path`
    chain, a bare literal, a docstring or a comment. Matching on the filename rather than on a
    resolved `Path` expression is deliberate: a prose mention is exactly the kind of claim that
    goes false on a promotion, and a resolver would see none of them.

    A row is raised only where ONE string carries both halves -- see `_CLAIM_NEEDS_BOTH_HALVES`.
    `sources` replaces on-disk module text with `{path: source}`, which is how the pre-repair
    instances out of `77d92e0d1^` are replayed against this census without checking them back in.
    """
    base = PROJECT if root is None else root
    targets = promote_targets(base)
    by_name = {t["name"]: t for t in targets}
    dated_names = {d for t in targets for d in t["dated_siblings"]}
    live_tokens = {t["name"]: _artefact_dates(base / t["canonical"]) for t in targets}

    if sources is None:
        mods = [(m, None) for d in CENSUS_ROOTS if (base / d).is_dir()
                for m in sorted((base / d).rglob("*.py"))]
    else:
        mods = [(base / p, src) for p, src in sorted(sources.items())]

    rows: list[dict] = []
    for mod, override in mods:
        try:
            strings = _module_strings(mod, override)
        except OSError:
            continue
        blob = " ".join(s for _, _, s in strings)
        named = {n for n in by_name if n in blob}
        if not named:
            continue
        try:
            tree = ast.parse(override if override is not None
                             else mod.read_text(encoding="utf-8"))
            aliases_by_name = _constants_bound_to(tree, named)
        except (SyntaxError, OSError):
            aliases_by_name = {}
        pinned = {n for n in dated_names if n in blob}
        for lineno, kind, whole in strings:
          for text in _sentences(whole):
            ids = [m.group(0) for m in _RUN_IDENTITY.finditer(text)]
            # An ordering word that IS part of the target's own filename asserts nothing:
            # `LATEST.json` is a NAME, not a claim that this run is the latest. Stripped for the
            # ordering scan only -- `text` itself stays whole, because the filename is exactly what
            # makes the sentence a reference to the target.
            bare = text
            for n in by_name:
                bare = bare.replace(n, " ").replace(n.removesuffix(".json"), " ")
            orderings = [m.group(0) for m in _ORDERING_CLAIM.finditer(bare)]
            if not ids and not orderings:
                continue
            for name in sorted(named):
                tgt = by_name[name]
                aliases = {a for a, v in aliases_by_name.items() if v == name}
                if not _references(text, name, aliases):
                    continue
                same_stem_pins = {p for p in pinned if p in set(tgt["dated_siblings"])}
                pin_forms: set[str] = set()
                for p in same_stem_pins:
                    pin_forms |= _normalise_all(p)
                    pin_forms |= _artefact_dates((base / tgt["canonical"]).parent / p)
                for token in ids or [None]:
                    forms = _normalise(token) if token else set()
                    rows.append({
                        "module": mod.relative_to(base).as_posix(),
                        "line": lineno,
                        "kind": kind,
                        "target": tgt["canonical"],
                        "token": token,
                        "ordering": sorted(set(orderings)),
                        "mixed": bool(same_stem_pins),
                        "matches_current_run": bool(forms & live_tokens[name]),
                        "matches_a_pinned_sibling": bool(forms & pin_forms),
                        "text": " ".join(text.split())[:200],
                    })
    # A target that publishes NO run identity cannot grade any claim about which run it is. That
    # is "we cannot tell", and it belongs on the surface as its own category rather than silently
    # among the stale (where it would read as a defect) or among the quiet (where it would read as
    # a pass). `run_output_latest.json` is in exactly this state.
    ungradable = sorted(n for n, toks in live_tokens.items() if not toks)
    stale = [r for r in rows if r["token"]
             and not r["matches_current_run"] and not r["matches_a_pinned_sibling"]
             and r["target"].rsplit("/", 1)[-1] not in ungradable]
    cannot_tell = [r for r in rows if r["token"]
                   and r["target"].rsplit("/", 1)[-1] in ungradable]
    ordering_only = [r for r in rows if r["token"] is None]
    return {
        "targets": targets,
        "readers": sorted({r["module"] for r in rows}),
        "rows": rows,
        "ordering_only": ordering_only,
        "stale": stale,
        "ungradable_targets": ungradable,
        "cannot_tell": cannot_tell,
    }


def _normalise_all(filename: str) -> set[str]:
    """Run-identity forms recoverable from a dated sibling's FILENAME."""
    out: set[str] = set()
    for m in _RUN_IDENTITY.finditer(filename):
        out |= _normalise(m.group(0))
    return out


#: Feeds the site renders. A published sentence lives here as a string VALUE, already composed.
FEED_ROOT = "site/data"


def feed_claims(root: Path | None = None) -> list[dict]:
    """Run-identity tokens in a PUBLISHED feed that no artefact the feed declares can support.

    THE HALF THE SOURCE CENSUS CANNOT SEE, and the reason this second leg exists. Replaying the
    three instances of `77d92e0d1` through `census()` catches ONE -- the docstring naming
    `value_cycle_ab_s1_noise_floor.json` as a guard's sole witness. It misses the other two, and it
    misses them for a structural reason rather than a tuning one: both were sentences that REACHED
    THE READER, and a reader-facing sentence never names a file path. "It is a LARGER advantage
    than the GBP 17,453 below" and "published beside the 2026-08-31 run" refer to the artefact as
    *the panel below* and *the run*. No amount of narrowing or widening over module text can pair
    those with a promote target, because the pairing is not in the text.

    So this leg does not read source at all. It reads the FEED, takes the artefacts the feed itself
    declares in `sources`, and asks whether every run-identity token the feed publishes is present
    in at least one of them. A promote-by-copy followed by a regenerate leaves any hard-coded
    literal behind while every derived figure moves -- which is precisely the signature.

    THIS LEG REPORTS AND DOES NOT REFUSE, AND THE REASON IS A LIMIT RATHER THAN A PREFERENCE.
    Run over `site/data/value_arms.json` it raises 23 rows, and every one of them is legitimate:
    `withdrawn_claim.withdrawn_on`, `decisions.auc_attribution.history[].on` and
    `polarity_check.by_run[].on` are DATED HISTORICAL RECORDS -- a wrong claim kept beside the
    result, which this project requires rather than tolerates -- and `market_reaction.legs[].date`
    is a simulation probe date that describes 2019, not a run.

    A record of what was true on 2026-08-29 is SUPPOSED not to track the artefact. A claim about
    which run is on the page is supposed to track it exactly. The two are indistinguishable from
    the text, and separating them by field name would be an allowlist excusing the very mechanism
    the control points at. So the honest state is: this leg cannot tell the populations apart, it
    fails open, and it says so here and on the surface rather than in a footnote. Making it refuse
    would need each feed field to declare which population it is in -- that is a real repair and it
    is not this turn's.
    """
    base = PROJECT if root is None else root
    targets = {t["canonical"] for t in promote_targets(base)}
    out: list[dict] = []
    feed_dir = base / FEED_ROOT
    if not feed_dir.is_dir():
        return out
    for feed in sorted(feed_dir.glob("*.json")):
        try:
            payload = json.loads(feed.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(payload, dict):
            continue
        declared = [s for s in (payload.get("sources") or []) if isinstance(s, str)]
        if not any(s in targets for s in declared):
            continue
        supported: set[str] = set()
        for s in declared:
            for tok in _artefact_dates(base / s):
                supported |= _normalise(tok)
        for path, text in _walk_strings(payload):
            for m in _RUN_IDENTITY.finditer(text):
                token = m.group(0)
                if _normalise(token) & supported:
                    continue
                out.append({
                    "feed": feed.relative_to(base).as_posix(),
                    "field": path,
                    "token": token,
                    "declared_sources": declared,
                    "text": " ".join(text.split())[:200],
                })
    return out


def _walk_strings(node, path: str = "") -> list[tuple[str, str]]:
    """Every string value in a feed, with the dotted field path that reaches it."""
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out += _walk_strings(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += _walk_strings(v, f"{path}[{i}]")
    elif isinstance(node, str):
        out.append((path, node))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when any run-identity literal is STALE against the artefact "
                         "currently sitting at the promote-by-copy target it describes. The feed "
                         "leg is REPORTED and never refuses -- it fails open, by construction")
    ap.add_argument("--json", action="store_true", help="emit the whole census as JSON")
    args = ap.parse_args(argv)

    result = census()
    result["feed"] = feed_claims()
    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if (args.check and (result["stale"] or result["feed"])) else 0

    print(f"PROMOTE-BY-COPY TARGETS  {len(result['targets'])}")
    for t in result["targets"]:
        print(f"  {t['canonical']}  <- {len(t['dated_siblings'])} dated sibling(s)")
    print(f"\nREADERS  {len(result['readers'])}")
    for m in result["readers"]:
        print(f"  {m}")
    print(f"\nCLAIMS ABOUT WHICH RUN IS THERE  {len(result['rows'])}"
          f"   ordering-only {len(result['ordering_only'])}   STALE {len(result['stale'])}")
    for r in result["stale"]:
        print(f"  STALE {r['module']}:{r['line']} ({r['kind']}) token={r['token']!r} "
              f"vs {r['target']}\n        {r['text']}")
    if result["ungradable_targets"]:
        print(f"\nWE CANNOT TELL  {len(result['cannot_tell'])} claim(s) against "
              f"{len(result['ungradable_targets'])} target(s) that publish NO run identity:")
        for n in result["ungradable_targets"]:
            print(f"  {n} -- carries no generated_at/digest/commit, so no claim about WHICH RUN "
                  f"sits here can be checked against it")
        for r in result["cannot_tell"]:
            print(f"  UNCHECKABLE {r['module']}:{r['line']} token={r['token']!r}\n"
                  f"        {r['text']}")
    for r in result["ordering_only"]:
        print(f"  ORDERING {r['module']}:{r['line']} ({r['kind']}) {r['ordering']} "
              f"vs {r['target']}\n        {r['text']}")
    print(f"\nPUBLISHED FEED CLAIMS NO DECLARED SOURCE SUPPORTS  {len(result['feed'])}"
          "   (REPORT ONLY -- this leg cannot tell a dated historical record from a claim about "
          "the current run, so it fails open; see `feed_claims`)")
    for r in result["feed"]:
        print(f"  UNSUPPORTED {r['feed']}:{r['field']} token={r['token']!r}\n        {r['text']}")

    if args.check and result["stale"]:
        print("\nREFUSED: a sentence keyed to which run sits at a promoted path is false as the "
              "tree stands. Derive it from the artefact's payload, or pin the dated sibling.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
