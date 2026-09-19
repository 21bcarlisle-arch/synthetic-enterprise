#!/usr/bin/env python3
"""Does a published `site/data/*.json` still match what its generator would produce?

THE DEFECT THIS EXISTS FOR, found by accident on 2026-09-19 and repaired as ONE INSTANCE in
`1d5642c35`. A false regulatory citation — `Ofgem SLC 27B`, a regulation that does not exist — was
corrected by hand in `site/data/simplified.json` and `site/data/dashboard.json` on 2026-09-03, and
never in `docs/design/simplifications/DD_seasonal_cashflow_physics.yaml`, which
`tools/generate_simplified_data` copies BYTE-IDENTICALLY. The correction was right; the source it
came from was not touched. It survived sixteen days purely as hand-edited committed bytes, and the
first regeneration reverted it — which is how anyone found out.

Nothing in this repository compared a published feed against what its generator would produce, so
that edit was correct on disk, reverted at the next run, and unobservable in between. This module is
that comparison.

HOW IT AVOIDS THE TRAP IT IS MADE OF. The obvious implementation — point a generator's `OUT_PATH` at
a temp file — fails two ways this project has already paid for: most generators compute
`PROJECT = Path(__file__).resolve().parent.parent` and take no output argument at all, and the ones
that do have a trailing `print(path.relative_to(PROJECT))` that raises AFTER a correct write. So no
path is redirected here. Instead the whole tree is CLONED at HEAD (`git clone --shared`, ~1s, no
object copy) and the generator is run with `cwd` inside the clone, where its own `__file__` makes
every relative path resolve to the clone. The shared tree is never written.

WHY A CLONE AND NOT `git archive`. Measured, not assumed: in a `git archive | tar -x` extract there
is no `.git`, and five generators fail there for that reason alone — `not a git repository` — which
is this project's catalogued "a red from an extract is artefact locality" trap. A `--shared` clone
carries the full history for ~1s and none of those five fail. The extract was tried first and
discarded on the measurement.

THE THREE-WAY VERDICT, AND WHY IT IS NOT A HAND-MAINTAINED ALLOWLIST. Regenerating everything and
demanding equality does not work: measured across all 61 feeds on 2026-09-19, 24 of the 31 that run
diverge, and almost none of them from a hand-edit. They diverge because the feed is a function of
things that are not in the commit — the live git log, the live staging directory, a gitignored
Elexon cache, a run artefact. A control that reds on those is red on the day it lands and muted by
the end of the week.

So the membership rule is MEASURED on every run rather than listed:

  NONDETERMINISTIC  two clones of the SAME commit produce two different files, so the feed is not a
                    function of the commit and no comparison against committed bytes means anything.
                    Reported as a named gap — never as a pass, and never as a red.
  DIVERGES          the generator IS deterministic at this commit and its output is not the
                    committed bytes. This is the SLC-27B shape. RED.
  AGREES            deterministic, and the committed bytes are what it produces.

The second clone is only built when the first disagrees, so the green path costs one clone.

WHICH FEED A GENERATOR OWNS IS OBSERVED, NEVER DECLARED. The generator is run and the files it
actually changed are read off the disk. A feed→generator table written down here would go stale the
first time a generator learned to write a second feed, and it would go stale silently.

READ AS COMMITTED, NEVER AS EDITED — with one named exception. The baseline is `HEAD`'s bytes, not
the working tree's: in this shared tree several lanes hold dirty copies at any moment, and a
working-tree read would compare a generator against another lane's unfinished edit. The exception is
a checkout with no resolvable HEAD, which is what `tools/surgical_land` builds to grade the tree a
commit WOULD create (`git archive | tar -x` then a fresh `git init`). There the files on disk ARE
the tree being graded, so they are the baseline — the same property reached by a different route,
exactly as `tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input` handles
it. Any OTHER git failure is a refusal, not a fallback: a control over what is committed must not go
green because it could not find out.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FEED_DIR = "site/data"

#: Per-generator ceiling. The slowest real generator measured 2026-09-19 is
#: `generate_provisional_plan_data` at 251s (`git log --reverse --follow` over the whole history).
DEFAULT_TIMEOUT_S = 300

#: The feeds that ARE a function of their commit, and the generator that writes each. Membership is
#: a PROPERTY — "regenerating this at its own commit reproduces the committed bytes" — measured
#: 2026-09-19 across all 61 published feeds, and re-derived on every run by
#: `tests/tools/test_a_published_feed_matches_what_its_generator_would_produce`'s promotion leg,
#: which reds if any feed OUTSIDE this table now reproduces. So the set can only grow, and it cannot
#: quietly become a record of what happened to pass on the day it was written.
#:
#: ONE HOME, because there are two readers: the commit-time control, and the publish path in
#: `background/process_run_complete`, which uses it to name what a regeneration is about to revert.
#: A second copy would drift, and the drift would be invisible in exactly the way this module exists
#: to prevent. The whole set grades in ~7s.
COVERED_FEEDS = {
    "company.json": "generate_company_data",
    "explore_hh_days.json": "generate_explore_hh_day",
    "fidelity.json": "generate_fidelity_data",
    "knowledge_review.json": "generate_knowledge_review",
    "premise_demand.json": "generate_premise_demand_data",
    "regulatory.json": "generate_regulatory_data",
    "simplified.json": "generate_simplified_data",
    "world.json": "generate_world_data",
}


def covered_generators() -> list[str]:
    """The generators behind `COVERED_FEEDS`, deduplicated and ordered."""
    return sorted(set(COVERED_FEEDS.values()))


class RegenerationCheckRefused(RuntimeError):
    """The check could not be performed. Never a pass, never a red — a refusal."""


def _git(root: str | Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=False, env=env)


def head_resolves(root: Path = PROJECT) -> bool:
    """Does this checkout have a commit to read? The landing checkout does not."""
    try:
        return _git(root, "rev-parse", "--verify", "HEAD").returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


class _Tree:
    """A private, writable copy of the tree under test, at the committed bytes.

    A clone when HEAD resolves; a file copy of the working tree when it does not (see the module
    docstring's named exception). Either way, writing in it cannot reach the shared tree.
    """

    def __init__(self, root: Path, tmp: Path, ordinal: int):
        self.path = tmp / f"tree{ordinal}"
        self._cloned = head_resolves(root)
        if self._cloned:
            done = subprocess.run(
                ["git", "clone", "--shared", "--quiet", str(root), str(self.path)],
                capture_output=True, text=True, check=False,
            )
            if done.returncode != 0:
                raise RegenerationCheckRefused(
                    f"could not clone the tree under test (rc {done.returncode}): "
                    f"{done.stderr.strip()[-300:]}"
                )
        else:
            # No HEAD: the disk IS the tree being graded. Copy it rather than read it in place,
            # because the generators write.
            shutil.copytree(root, self.path, symlinks=True,
                            ignore=shutil.ignore_patterns(".git"))
        if not (self.path / FEED_DIR).is_dir():
            raise RegenerationCheckRefused(
                f"the tree under test has no {FEED_DIR}/ — refusing to measure an empty feed "
                "set, because an empty set agrees with every claim ever made"
            )

    def restore_feeds(self) -> None:
        """Put the feed directory back to the committed bytes."""
        if self._cloned:
            done = _git(self.path, "checkout", "--", FEED_DIR)
            if done.returncode != 0:
                raise RegenerationCheckRefused(
                    f"could not restore {FEED_DIR} in the tree under test: {done.stderr.strip()}"
                )

    def feeds(self) -> dict[str, bytes]:
        return {p.name: p.read_bytes() for p in sorted((self.path / FEED_DIR).glob("*.json"))}

    def run(self, generator: str, timeout_s: int) -> tuple[dict[str, bytes], str]:
        """Run `tools.<generator>` inside this tree; return the feeds it CHANGED, and any error."""
        self.restore_feeds()
        before = self.feeds()
        env = dict(os.environ)
        env["PYTHONPATH"] = str(self.path)
        try:
            done = subprocess.run([sys.executable, "-m", f"tools.{generator}"],
                                  cwd=str(self.path), env=env, capture_output=True,
                                  text=True, timeout=timeout_s, check=False)
            err = "" if done.returncode == 0 else (done.stderr or "")[-400:].strip()
        except subprocess.TimeoutExpired:
            return {}, f"timed out after {timeout_s}s"
        except OSError as exc:
            return {}, f"could not run the generator: {exc}"
        after = self.feeds()
        return {n: after[n] for n in after if before.get(n) != after[n]}, err


def _verdict(committed: bytes, first: bytes, second: bytes | None) -> tuple[str, dict]:
    """AGREES / DIVERGES / NONDETERMINISTIC / UNPARSEABLE, with the diff that decided it."""
    from tools.artefact_rerun_diff import compare  # local: keeps import cost off the green path
    try:
        was, now = json.loads(committed), json.loads(first)
    except (ValueError, UnicodeDecodeError) as exc:
        return "UNPARSEABLE", {"error": str(exc)[:200]}
    against_committed = compare(was, now)
    if not (against_committed["changed"] or against_committed["removed"]):
        return "AGREES", {}
    if second is not None:
        try:
            again = json.loads(second)
        except (ValueError, UnicodeDecodeError) as exc:
            return "UNPARSEABLE", {"error": str(exc)[:200]}
        run_to_run = compare(now, again)
        if run_to_run["changed"] or run_to_run["removed"] or run_to_run["added"]:
            return "NONDETERMINISTIC", {
                "run_to_run": [list(map(str, c)) for c in run_to_run["changed"][:5]],
            }
    return "DIVERGES", {
        "changed": [list(map(str, c)) for c in against_committed["changed"][:10]],
        "removed": against_committed["removed"][:10],
        "n_changed": len(against_committed["changed"]),
        "n_removed": len(against_committed["removed"]),
    }


def check(generators, root: Path = PROJECT, timeout_s: int = DEFAULT_TIMEOUT_S,
          separate_nondeterminism: bool = True) -> list[dict]:
    """Regenerate each generator's feeds in a private tree and grade them against committed bytes.

    Returns one row per FEED the generator actually wrote — observed, not declared. A generator that
    writes nothing gets a single `WROTE_NOTHING` row, which is a gap and not a pass.

    `separate_nondeterminism=False` skips the second tree, so a feed that does not reproduce is
    reported as DIVERGES without establishing WHY. That is the wrong reading for grading a feed and
    the right one for the only question a caller may ask without it — "does this feed reproduce?",
    where AGREES is decided on the first tree alone. It roughly halves the sweep, and it may never
    be used to justify a red: DIVERGES from this mode does not distinguish a hand-edit from a
    generator that reads the clock.
    """
    generators = list(generators)
    if not generators:
        raise RegenerationCheckRefused(
            "no generators named — refusing to report a clean sweep over an empty set"
        )
    rows: list[dict] = []
    tmp = Path(tempfile.mkdtemp(prefix="feed-regen-"))
    try:
        first = _Tree(root, tmp, 1)
        second: _Tree | None = None
        committed = first.feeds()
        for generator in generators:
            written, err = first.run(generator, timeout_s)
            if not written:
                rows.append({"generator": generator, "feed": None,
                             "verdict": "WROTE_NOTHING", "detail": {"stderr": err}})
                continue
            # Only pay for the determinism tree when something actually disagrees.
            needs_second = separate_nondeterminism and any(
                committed.get(n) != b for n, b in written.items())
            again: dict[str, bytes] = {}
            if needs_second:
                if second is None:
                    second = _Tree(root, tmp, 2)
                again, _ = second.run(generator, timeout_s)
            for name in sorted(written):
                if name not in committed:
                    rows.append({"generator": generator, "feed": name,
                                 "verdict": "NOT_COMMITTED", "detail": {}})
                    continue
                verdict, detail = _verdict(committed[name], written[name], again.get(name))
                if err:
                    detail = {**detail, "stderr": err}
                rows.append({"generator": generator, "feed": name,
                             "verdict": verdict, "detail": detail})
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("generators", nargs="*",
                        help="generator module stems, e.g. generate_simplified_data. "
                             "Default: every tools/generate_*.py in the tree.")
    parser.add_argument("--json", action="store_true", help="emit the rows as JSON")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    args = parser.parse_args(argv)

    names = args.generators or sorted(p.stem for p in (PROJECT / "tools").glob("generate_*.py"))
    rows = check(names, timeout_s=args.timeout)
    if args.json:
        print(json.dumps(rows, indent=1))
    else:
        for row in rows:
            print(f"{row['verdict']:<16} {row['feed'] or '-':<28} {row['generator']}")
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 1 if any(r["verdict"] == "DIVERGES" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
