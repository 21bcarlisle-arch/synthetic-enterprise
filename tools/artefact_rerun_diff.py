"""Decide whether a re-run of a measurement artefact IS that measurement, re-instrumented.

THE QUESTION THIS EXISTS TO ANSWER. A run artefact is re-run to add a block to it. Before the new
file is published over the old one, someone must establish that the re-run reproduced the
measurement rather than made a different one. `tools/run_arms_with_the_skill_funnel_20260830.sh`
asked that question inline and got it wrong in both directions on its first live use, which is
what this module is a repair of.

  IT NAMED THE NEW KEYS AND THE LIST WENT STALE. Its `strip()` popped `method_skill.drop_out` and
  `method_skill.dropped_sample` before comparing. The re-run in fact carried NINE new keys, from
  four lanes landing in one night, so seven of them read as "a different measurement". An
  allowlist of additions is a control that goes red exactly when the tree is busiest.

  A KEY THAT DID NOT EXIST BEFORE HAS NO OLD VALUE TO CONTRADICT. So this module needs no
  allowlist: it reports additions as their own category and never as a change. That is the whole
  fix for the first half, and it cannot go stale.

  IT COMPARED SERIALISED JSON WITH `==`. Two `*_elsewhere` figures moved by 3 and 22 ULPs — the
  bottom bits of a double — while their `*_on_those_accounts` siblings, summed over one account
  rather than 166, stayed bit-identical. That is summation ORDER. Exact string equality on floats
  cannot survive a reordering that changes no quantity, and demanding it means the check can only
  ever be satisfied by luck.

  THE TOLERANCE IS IN ULPs, NEVER IN POUNDS. A tolerance of "£0.01" is a different tolerance at
  £10,000 than at £0.50, and the figure that needs protecting most is the small one. ULPs scale
  with the magnitude by construction. `MAX_ULPS = 64` is ~1.2e-9 on a £10k aggregate and ~4e-15
  on a £0.50 one: far above any reordering, far below any quantity this repository publishes.
  INTS AND STRINGS GET NO TOLERANCE AT ALL — a count that moved, moved.

THE CLAUSE NO DIFF BETWEEN TWO ARTEFACTS CAN SUPPLY. Both halves above compare the new file to the
old one, and neither can see that the NEW file was written by mixed-vintage code. The 08-30 run
started at 04:47:45Z and Python binds its modules at process start, so it ran the working tree of
that instant: it carried three lanes' instrumentation and NOT `f9866cd2a`, which was still being
written. Its `book_identity` is therefore the pre-fix shape — resolved once at artefact-assembly
instead of snapshotted beside each arm — and promoting it would publish that block under a commit
whose tree contains the newer labeller. `stale_shape()` is that third clause, and it is keyed to
what the CODE emits rather than to a literal, so it cannot certify a shape the code has moved past.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

# The clock is expected to move on any re-run. It is the ONLY key excluded by name, because it is
# the only one whose whole purpose is to differ.
THE_CLOCK = "generated_at"

# See the module docstring: chosen to sit far above summation-order noise and far below any
# quantity this repository publishes. Applies to floats only.
MAX_ULPS = 64


def ulp_distance(a: float, b: float) -> int:
    """Number of representable doubles between `a` and `b`.

    Signed-magnitude to two's-complement first, so the comparison stays correct across zero
    rather than reporting a vast distance between -0.0 and +0.0.
    """
    def ordinal(x: float) -> int:
        bits = struct.unpack("<q", struct.pack("<d", x))[0]
        return bits if bits >= 0 else -(bits & 0x7FFFFFFFFFFFFFFF) - (1 << 63)

    return abs(ordinal(a) - ordinal(b))


def _same_number(a, b) -> tuple[bool, str]:
    """FAIL CLOSED on anything that is not two ordinary comparable numbers."""
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b, "bool"
    if isinstance(a, int) and isinstance(b, int):
        # Exact by construction. A count that moved, moved.
        return a == b, "int (exact, no tolerance)"
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return False, "not both numeric"
    a, b = float(a), float(b)
    if math.isnan(a) or math.isnan(b):
        # NaN is never equal to itself; saying "unchanged" here would be a fail-open.
        return False, "NaN present -- cannot compare"
    if math.isinf(a) or math.isinf(b):
        return a == b, "infinite"
    d = ulp_distance(a, b)
    return d <= MAX_ULPS, f"{d} ULP"


def walk(old, new, path: str, out: dict) -> None:
    if isinstance(old, dict) and isinstance(new, dict):
        for k in new.keys() - old.keys():
            out["added"].append(f"{path}/{k}")
        for k in old.keys() - new.keys():
            out["removed"].append(f"{path}/{k}")
        for k in sorted(old.keys() & new.keys()):
            walk(old[k], new[k], f"{path}/{k}", out)
        return
    if isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            out["changed"].append((f"{path} [length]", len(old), len(new), "list length"))
            return
        for i, (x, y) in enumerate(zip(old, new)):
            walk(x, y, f"{path}[{i}]", out)
        return
    if isinstance(old, (int, float)) or isinstance(new, (int, float)):
        same, why = _same_number(old, new)
        if not same:
            out["changed"].append((path, old, new, why))
        elif why.endswith("ULP") and why != "0 ULP":
            out["within_tolerance"].append((path, old, new, why))
        return
    if old != new:
        out["changed"].append((path, old, new, type(old).__name__))


def compare(old_doc: dict, new_doc: dict) -> dict:
    """Structural comparison. Additions are their own category and are never a change."""
    old_doc = {k: v for k, v in old_doc.items() if k != THE_CLOCK}
    new_doc = {k: v for k, v in new_doc.items() if k != THE_CLOCK}
    out = {"added": [], "removed": [], "changed": [], "within_tolerance": []}
    walk(old_doc, new_doc, "", out)
    out["same_measurement"] = not out["removed"] and not out["changed"]
    return out


# --- the provenance clause -------------------------------------------------------------------

def _shape_the_code_emits() -> set[str]:
    """The `book_identity` keys the CURRENT runner emits, read from the runner itself.

    Keyed to the code, not to a literal, so this cannot keep certifying a shape the code has
    moved past -- the failure mode that put a pre-fix block one commit away from the live page.
    """
    import tools.run_value_cycle_ab as runner

    required = set()
    if hasattr(runner, "same_book_across_arms"):
        required.add("same_book_across_arms")
    return required


def stale_shape(doc: dict) -> list[str]:
    """Return the `book_identity` keys the current code emits that this artefact LACKS.

    Non-empty means the artefact was written by an older labeller than the tree it would land in,
    whatever its filename or promotion date says.
    """
    book = doc.get("book_identity")
    if not isinstance(book, dict):
        return ["book_identity absent entirely"]
    return sorted(_shape_the_code_emits() - book.keys())


def _report(old_path: str, new_path: str, check_shape: bool) -> int:
    old_doc = json.loads(Path(old_path).read_text(encoding="utf-8"))
    new_doc = json.loads(Path(new_path).read_text(encoding="utf-8"))
    r = compare(old_doc, new_doc)

    print(f"published : {old_path}\nrerun     : {new_path}\n")
    print(f"ADDED   {len(r['added'])} key(s) -- instrumentation, never a re-measurement")
    for p in r["added"]:
        print(f"    + {p}")
    if r["within_tolerance"]:
        print(f"\nWITHIN TOLERANCE  {len(r['within_tolerance'])} float(s) "
              f"(<= {MAX_ULPS} ULP -- summation order, not a quantity)")
        for p, a, b, why in r["within_tolerance"]:
            print(f"    ~ {p}\n        {a!r} -> {b!r}  ({why})")
    print(f"\nREMOVED {len(r['removed'])} key(s)")
    for p in r["removed"]:
        print(f"    - {p}")
    print(f"CHANGED {len(r['changed'])} value(s) beyond tolerance")
    for p, a, b, why in r["changed"]:
        print(f"    ~ {p}\n        {a!r} -> {b!r}  ({why})")

    rc = 0
    if r["same_measurement"]:
        print("\nSAME MEASUREMENT -- the re-run reproduces the published artefact.")
    else:
        print("\nRE-MEASUREMENT -- the re-run is a different measurement. Do NOT publish it "
              "over the old artefact; re-run both legs together.")
        rc = 1

    if check_shape:
        missing = stale_shape(new_doc)
        if missing:
            print(f"\nSTALE SHAPE -- the re-run's `book_identity` lacks {missing}, which the "
                  "runner in this tree emits. It was written by an older labeller than the tree "
                  "it would land in. Do NOT promote it.")
            rc = 1
        else:
            print("\nSHAPE OK -- `book_identity` carries what the runner in this tree emits.")
    return rc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("published")
    ap.add_argument("rerun")
    ap.add_argument("--check-shape", action="store_true",
                    help="also require the artefact's book_identity to match this tree's runner")
    a = ap.parse_args(argv)
    return _report(a.published, a.rerun, a.check_shape)


if __name__ == "__main__":
    sys.exit(main())
