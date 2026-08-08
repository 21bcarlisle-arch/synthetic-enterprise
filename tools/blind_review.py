"""AO9 — blind review by restricted context, not by relay.

WHAT THE BOARD ACTUALLY WAS
---------------------------
The blind board worked, and the director named why: not the human courier, and
not a better reviewer — the property was WHAT THE REVIEWER COULD NOT SEE. The
courier was only the enforcement, and a mechanism that runs a few times because
a person has to cut and paste it is a mechanism that mostly does not run.

So this replaces the courier, and nothing else. A fresh-context agent is given
ONLY the plain-words capability description and the domain — never code, never
design notes, never an earlier verdict — and produces the practitioner battery:
the questions a working practitioner would use to DISQUALIFY the capability.

BLINDNESS BY CONSTRUCTION, NOT BY PROMISE
-----------------------------------------
"The reviewer was blind" is worthless as an assertion, because the one person
who cannot check it is the one making it. Two structural choices instead:

  1. The packet shown to the reviewer is ASSEMBLED, from a whitelist of two
     fields (plain words, domain) plus a fixed template. It is not narrated by
     the caller, so there is no seam through which build context arrives.
  2. That exact text is stored VERBATIM in the same record as the battery it
     produced, with its own digest. Transcript and result cannot be separated,
     because they are one record — and `--audit` re-derives the blindfold
     verdict FROM THE STORED TEXT, never from what the record claims about
     itself. A record asserting `leaks: []` over a transcript full of source
     is caught, which is the whole point: the audit and the recorder must be
     able to DISAGREE.

THE HONEST LIMIT (3c) IS A WALL, NOT A CAVEAT
---------------------------------------------
Restricted context gives BLINDNESS, NOT INDEPENDENCE. The reviewer is the same
model family as the builder; shared priors and shared blind spots survive the
blindfold intact. Genuinely external review — the director relaying to a
different model or a human — stays reserved for the few highest-stakes verdicts
per epoch, at his choosing. This tool may never be described as delivering
independence, so every record carries `independence: false` by construction and
`--audit` FAILS any record claiming otherwise. The limit is not in a comment
where it can be forgotten; it is in the data where it can be checked.

WHAT THIS IS NOT
----------------
A second review mechanism. `.claude/skills/cold-eyes-walk/SKILL.md` is the ONE
protocol — priors before pixels, persona priming, same-page reconciliation,
verdict before builder context. It has two subjects: a RENDERED ARTEFACT (a
page, a door, a headline figure), where the blindfold is the URL, and a
CAPABILITY (a map atom), where the blindfold is this tool. Same five steps,
mechanised at the one step that used to run on the honour system.

A REFUSAL THAT WILL LOOK LIKE A BUG, AND IS NOT
-----------------------------------------------
Most real docstrings mention a module, a path, or a phase. Rendered into a
packet, those tell the reviewer where to look and what the build already
believes, which is exactly the leak the atom exists to prevent — so `--packet`
REFUSES and names the rule that fired. The answer is `--plain-words "..."`: a
blind-safe restatement, recorded as `restated` rather than `index`, so that the
substitution is visible to anyone auditing the record. What the tool cannot
check is whether a restatement is FAITHFUL to the capability; that is stated
here rather than hidden, and it is why the source field is recorded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEDGER_PATH = ROOT / "docs" / "observability" / "blind_review_ledger.jsonl"

DEFAULT_DOMAIN = "UK energy retail supply"
DEFAULT_PERSONA = "veteran energy retail operator"

HONEST_LIMIT = (
    "Restricted context gives BLINDNESS, NOT INDEPENDENCE -- the reviewer is the "
    "same model family as the builder. Genuinely external review is reserved for "
    "the few highest-stakes verdicts per epoch, at the director's choosing."
)

# ---------------------------------------------------------------------------
# the blindfold
#
# Each rule names ONE thing a blind reviewer must not be able to see. They are
# separate rather than one big pattern so that a leak is reported as the class
# it belongs to -- "you showed it source code" is actionable, "leak detected"
# is not -- and so a mutation test can prove a NAMED rule fires rather than
# proving that something, somewhere, objected.
# ---------------------------------------------------------------------------
LEAK_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "SOURCE_CODE",
        re.compile(r"(?m)^\s*(?:def|class|import|from|@|#!)\s+\S|\bself\.\w|```"),
        "implementation source reached the reviewer",
    ),
    (
        "FILE_PATH",
        re.compile(r"\b[\w.\-/]*\w\.(?:py|ya?ml|json|jsonl|md|html|txt|csv)\b"),
        "a filename tells the reviewer where the answer lives",
    ),
    (
        "REPO_LOCATION",
        re.compile(r"(?<![\w-])(?:docs|tools|tests|company|saas|sim|simulation|background|site|scripts)/"),
        "a repository location exposes the build's own structure",
    ),
    (
        "PRIOR_JUDGEMENT",
        re.compile(r"(?i)\bfindings?\b|\bdefects?\b|\bregressions?\b|\bR1[0-9]\b|\bmutation test\b|\bskeptic\b"),
        "an earlier verdict anchors the reviewer instead of letting it form its own",
    ),
    (
        "MAP_INTERNALS",
        re.compile(r"(?i)\bmaturity\s*map\b|\blevel_current\b|\bloop_stage\b|\batoms?\b|\bepoch\s*\d|\bL[0-3]\s*(?:->|→)"),
        "the build's own bookkeeping is not part of the domain",
    ),
    (
        # Found by running the tool against a real derived description rather
        # than by reasoning about it: "Direct Debit Mandate Register (Phase GD)"
        # passed every other rule. The label is internal bookkeeping — it tells
        # a practitioner nothing about the capability, and tells them plenty
        # about there being a build behind it. Deliberately case-sensitive on
        # the label so that three-phase supply, a real domain term here,
        # survives.
        "PHASE_LABEL",
        re.compile(r"\bPhase\s+(?:[A-Z]{1,3}\d*|\d+[A-Za-z]?)\b"),
        "an internal phase label is the build's bookkeeping, not the capability",
    ),
    (
        "BUILD_CONTEXT",
        re.compile(r"(?i)\bcommits?\b|\bgit\b|\bdiffs?\b|\bbranch(?:es)?\b|\bpull request\b|\bwe (?:built|added|changed|fixed)\b|\bTODO\b|\brefactor"),
        "the intention behind the build is precisely what a cold reviewer must not have",
    ),
    (
        "IDENTIFIER",
        re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b|\b[a-z_]+\.[a-z_]+\.[a-z_]+\b"),
        "a code identifier names the implementation rather than the capability",
    ),
)

# The template is rendered into the SAME text the rules run over, so it is held
# to its own standard: no path, no identifier, no build vocabulary. It also
# avoids the word "commit" -- BUILD_CONTEXT would fire on the tool's own packet,
# which is the correct behaviour of the rule and the wrong wording of the ask.
PACKET_TEMPLATE = """\
DOMAIN: {domain}
YOU ARE: a {persona}.

THE CAPABILITY, IN PLAIN WORDS
{plain_words}

That description is the whole of what you have been given. You have not been
shown how it is put together, why it was undertaken, or what anyone has already
concluded about it, and you should not ask for any of that. Judge it as you
would judge a supplier's claim made to you across a table.

1. PRIORS BEFORE THE THING ITSELF. Before you assess the description, write
   down what a {persona} expects of a capability like this in {domain}: the
   ranges, magnitudes, rates, timings and behaviours. State numbers wherever
   numbers apply. Do this first, so your own expectations are on the record
   before the description has a chance to set them.
2. FIRST DOUBT. As that {persona}: what would you doubt first here, and why?
   A doubt counts even if the underlying work turns out to be right -- how a
   claim reads to a practitioner is itself the thing being tested.
3. THE PRACTITIONER BATTERY. Write the questions a practitioner would use to
   DISQUALIFY this capability: each one a question whose wrong answer would
   make you say "then it is not really doing the job". Mark each DISQUALIFYING
   or SUPPORTING, and say what answer you would need to hear.
"""


def blindfold_leaks(shown: str | None) -> list[str]:
    """Every blindfold breach in `shown`, as "RULE: reason -- 'snippet'".

    FAIL-CLOSED on absence. A missing or empty transcript is a FAILED audit,
    not a quiet pass: "we recorded nothing about what the reviewer saw" and
    "the reviewer saw nothing improper" are opposite states, and a control that
    conflates them reports calm exactly when the record has been lost.
    """
    if shown is None:
        return ["EMPTY_TRANSCRIPT: no record of what the reviewer was shown"]
    if not isinstance(shown, str) or not shown.strip():
        return ["EMPTY_TRANSCRIPT: the record of what the reviewer was shown is blank"]

    out: list[str] = []
    for name, pattern, reason in LEAK_RULES:
        hits = pattern.findall(shown)
        if not hits:
            continue
        snippet = next((h for h in hits if isinstance(h, str) and h.strip()), "")
        out.append(f"{name}: {reason} -- {snippet.strip()!r}")
    return out


def digest(shown: str) -> str:
    return hashlib.sha256(shown.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# the packet
# ---------------------------------------------------------------------------

def index_plain_words(capability: str, root: Path | None = None) -> str | None:
    """The plain-words description AO1 derives for `capability`.

    Imported lazily: the index walks the tree and costs seconds, and the common
    path here (`--plain-words` supplied) never needs it.
    """
    # Run as `python3 tools/blind_review.py`, sys.path[0] is tools/, not the
    # repo root -- so the sibling package import fails at exactly the moment a
    # human is using the CLI, while every test (imported as tools.blind_review)
    # stays green. Repair it here rather than at module scope: the import is
    # lazy on purpose and this is the only path that needs the root.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import capability_index

    rows = capability_index.build_rows(root)
    for row in rows:
        if row.get("module") == capability or row.get("path") == capability:
            return row.get("plain_words")
    return None


def render_shown(plain_words: str, domain: str, persona: str) -> str:
    return PACKET_TEMPLATE.format(
        plain_words=plain_words.strip(), domain=domain, persona=persona
    )


def build_packet(
    capability: str,
    plain_words: str | None = None,
    domain: str = DEFAULT_DOMAIN,
    persona: str = DEFAULT_PERSONA,
    root: Path | None = None,
) -> dict:
    """Assemble the restricted-context packet for one capability.

    `capability` names the subject for the RECORD, and is deliberately kept out
    of `shown`: a module path is itself a map of the implementation, so telling
    the reviewer which module it is judging would undo the blindfold in the act
    of applying it.
    """
    source = "restated"
    if plain_words is None:
        plain_words = index_plain_words(capability, root)
        source = "index"
    if not plain_words or not plain_words.strip():
        return {
            "capability": capability,
            "domain": domain,
            "persona": persona,
            "plain_words": None,
            "plain_words_source": source,
            "shown": None,
            "shown_sha256": None,
            "leaks": [
                "NO_DESCRIPTION: nothing plain-words exists for "
                f"{capability!r}, so there is nothing blind-safe to show"
            ],
        }

    shown = render_shown(plain_words, domain, persona)
    return {
        "capability": capability,
        "domain": domain,
        "persona": persona,
        "plain_words": plain_words.strip(),
        "plain_words_source": source,
        "shown": shown,
        "shown_sha256": digest(shown),
        "leaks": blindfold_leaks(shown),
    }


# ---------------------------------------------------------------------------
# the record
# ---------------------------------------------------------------------------

def _resolve_ledger(path: Path | None) -> Path:
    """LEDGER_PATH read at CALL time so a test can point it at tmp_path."""
    return path if path is not None else LEDGER_PATH


def record_review(
    packet: dict,
    battery: list[dict],
    recorded_at: str,
    ledger_path: Path | None = None,
) -> dict:
    """Append transcript-and-battery as ONE record. Raises rather than degrade.

    The refusals are the mechanism. A packet that leaked must not be recordable
    at all, because a ledger that accepts leaked reviews and flags them later
    has already published a verdict that was never blind. An empty battery is
    refused for the same reason a green suite with no tests is refused.
    """
    leaks = blindfold_leaks(packet.get("shown"))
    if leaks:
        raise ValueError(
            "refusing to record a review whose reviewer was not blind: "
            + "; ".join(leaks)
        )
    if not battery:
        raise ValueError("refusing to record a review with an empty battery")

    record = {
        "recorded_at": recorded_at,
        "capability": packet["capability"],
        "domain": packet["domain"],
        "persona": packet["persona"],
        "plain_words_source": packet["plain_words_source"],
        "shown": packet["shown"],
        "shown_sha256": packet["shown_sha256"],
        "battery": battery,
        # 3c, carried in the data rather than in prose that can be dropped.
        "independence": False,
        "honest_limit": HONEST_LIMIT,
    }

    target = _resolve_ledger(ledger_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def load_records(ledger_path: Path | None = None) -> list[dict]:
    """Every record, or raise. A ledger that cannot be parsed is not an empty
    ledger — returning [] there would turn an unreadable record into a clean
    audit, which is the FAIL-SILENT pattern exactly."""
    target = _resolve_ledger(ledger_path)
    if not target.exists():
        return []
    records = []
    for n, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{target}:{n} is not readable as a record: {exc}") from exc
    return records


def audit_records(records: list[dict]) -> list[str]:
    """Re-derive every record's blindfold verdict FROM ITS STORED TRANSCRIPT.

    Deliberately ignores anything the record says about itself. A record
    carrying `leaks: []` proves only that whatever wrote it believed that; the
    audit exists to be able to disagree, and if it read that field it would be
    the record checked against itself — a tautology wearing a control's clothes.
    """
    findings: list[str] = []
    for n, record in enumerate(records, 1):
        where = f"record {n} ({record.get('capability', 'unnamed')})"

        for leak in blindfold_leaks(record.get("shown")):
            findings.append(f"{where}: {leak}")

        shown = record.get("shown")
        stored = record.get("shown_sha256")
        if isinstance(shown, str) and shown.strip():
            if not stored:
                findings.append(f"{where}: transcript carries no digest, so tampering leaves no trace")
            elif stored != digest(shown):
                findings.append(f"{where}: TAMPERED -- the transcript no longer matches its digest")

        if not record.get("battery"):
            findings.append(f"{where}: transcript recorded with no battery -- a review that produced nothing")

        if record.get("independence") is not False:
            findings.append(
                f"{where}: claims independence. Restricted context is blindness only (3c); "
                "the reviewer is the same model family."
            )
        if not record.get("honest_limit"):
            findings.append(f"{where}: the 3c limit is missing from the record")

    return findings


def audit(ledger_path: Path | None = None) -> tuple[int, list[str]]:
    """(records audited, findings). The count is returned, and printed by the
    CLI, so that "no findings" can never be read as "everything was checked" —
    a vacuous pass over an empty ledger looks identical otherwise."""
    records = load_records(ledger_path)
    return len(records), audit_records(records)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _run_audit(ledger: Path | None) -> int:
    try:
        count, findings = audit(ledger)
    except (ValueError, OSError) as exc:
        print(f"AUDIT UNAVAILABLE: {exc}", file=sys.stderr)
        return 2  # an unavailable check is a FAILED check, never a pass
    if findings:
        print(f"{len(findings)} finding(s) across {count} recorded review(s):")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"{count} recorded review(s) audited, blindfold intact in each.")
    if count == 0:
        print("NOTE: nothing has been recorded yet -- this is an empty pass, not a clean one.")
    return 0


def _report_refusal(capability: str, leaks: list[str]) -> int:
    print(f"REFUSED -- this packet would not leave the reviewer blind ({capability}):",
          file=sys.stderr)
    for leak in leaks:
        print(f"  {leak}", file=sys.stderr)
    print("\nSupply a blind-safe restatement with --plain-words; it is recorded as "
          "'restated' so the substitution stays visible.", file=sys.stderr)
    return 1


def _run_record(packet: dict, args, ledger: Path | None) -> int:
    if not args.battery_file:
        print("--record needs --battery-file: the battery the blind reviewer produced",
              file=sys.stderr)
        return 1
    if not args.at:
        print("--record needs --at: the caller supplies the timestamp", file=sys.stderr)
        return 1
    battery = json.loads(Path(args.battery_file).read_text(encoding="utf-8"))
    try:
        record_review(packet, battery, args.at, ledger)
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(f"recorded: {packet['capability']} -- {len(battery)} battery question(s), "
          "transcript attached.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--packet", metavar="CAPABILITY",
                    help="render the restricted-context packet for a capability")
    ap.add_argument("--plain-words", metavar="TEXT",
                    help="blind-safe restatement, when the derived description is not blind-safe")
    ap.add_argument("--domain", default=DEFAULT_DOMAIN)
    ap.add_argument("--persona", default=DEFAULT_PERSONA)
    ap.add_argument("--record", metavar="CAPABILITY",
                    help="record a battery against the packet for a capability")
    ap.add_argument("--battery-file", metavar="PATH",
                    help="JSON list of battery questions produced by the blind reviewer")
    ap.add_argument("--at", metavar="TIMESTAMP",
                    help="timestamp for the record (the caller supplies it; replay stays deterministic)")
    ap.add_argument("--audit", action="store_true",
                    help="re-derive the blindfold verdict for every recorded review")
    ap.add_argument("--ledger", metavar="PATH", help="ledger location (default: the repo ledger)")
    args = ap.parse_args(argv)

    ledger = Path(args.ledger) if args.ledger else None

    if args.audit:
        return _run_audit(ledger)

    if args.packet or args.record:
        capability = args.packet or args.record
        packet = build_packet(capability, args.plain_words, args.domain, args.persona)
        if packet["leaks"]:
            return _report_refusal(capability, packet["leaks"])
        if args.packet:
            print(packet["shown"])
            return 0
        return _run_record(packet, args, ledger)

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
