"""Map a function over items in forked worker processes, results in input order.

WHY FORK, AND WHY NOT `tools/tournament_runner.py`'s ProcessPoolExecutor. The work this exists for
is the per-premise fabric trace (`fabric_demand_path.build_fabric_series_for_site`): 175 s of a
331 s 40-founder run (cProfile, 2026-10-08), independent of every company decision, and seeded per
premise from a hash (`premise_trace._base_seed_for`), so it is the same trace whichever process
builds it and in whatever order. Its callers hand it CLOSURES over the run's state
(`household_at_date`, the weather source), which a pickling pool cannot send. A forked worker
inherits them. Python 3.14 defaults to `forkserver` on Linux, so fork is asked for by name.

DETERMINISM IS THE CALLER'S CLAIM, NOT THIS MODULE'S. This only guarantees order. A function that
draws from a shared random stream would give a different answer in parallel; the controls that
call it compare the parallel book with the serial one.

Serial when there is nothing to gain or no way to fork: fewer than two items, one worker, or a
platform without fork. `SE_FORK_WORKERS` overrides the worker count (1 = serial, for a control or a
bisect).
"""
from __future__ import annotations

import multiprocessing
import os
from typing import Callable, Sequence

#: Cores left for the rest of the box. Eight cores, sixteen threads (i5-13400F); the seat, the
#: daemons and a neighbouring run share them. Not a domain constant: it bounds contention only.
RESERVED_CPUS = 4

_FN: Callable | None = None
_ITEMS: Sequence | None = None


def _call(i: int):
    return _FN(_ITEMS[i])


#: What one forked trace worker adds to the box, by PSS. ORIGIN: measured 2026-10-08 on a 40-founder
#: run to 2017: the whole tree peaked at 1,880 MB PSS against the parent's 1,691 MB, with 12 workers,
#: so ~16 MB each (copy-on-write keeps the parent's pages shared). Re-measure if traces grow.
WORKER_PSS_MB = 16

#: Free memory a speed-up must never take: the box's undeclared reserve plus room for a commit
#: gate, so forked workers cannot crowd out a landing (director, 2026-10-09). The gate's weight is
#: the box budget's measured class weight, read, not copied.
def _memory_floor_mb() -> float:
    from background.resource_headroom import CLASS_WEIGHTS_MB, RESERVE_FOR_UNDECLARED_MB
    return RESERVE_FOR_UNDECLARED_MB + CLASS_WEIGHTS_MB["commit_gate"]


def workers_for(n_items: int, available_mb: float | None = None) -> int:
    """Worker count: the fewest of the items, the spare cores, and what FREE MEMORY allows above
    the floor (director, 2026-10-09: "Size forked trace workers by free memory, not a fixed count,
    so a speed-up can't crowd out a landing"). Unreadable memory is the serial path."""
    env = os.environ.get("SE_FORK_WORKERS", "").strip()
    if env:
        return max(1, min(int(env), n_items))
    by_cpu = (os.cpu_count() or 1) - RESERVED_CPUS
    if available_mb is None:
        try:
            from background.resource_headroom import sample
            available_mb = sample().get("available_mb")
        except Exception:  # noqa: BLE001 -- no reading is the cautious answer: serial
            available_mb = None
    if available_mb is None:
        return 1
    by_memory = int((available_mb - _memory_floor_mb()) // WORKER_PSS_MB)
    return max(1, min(by_cpu, by_memory, n_items))


def fork_map(fn: Callable, items: Sequence) -> list:
    """`[fn(x) for x in items]`, computed in forked workers when that can help."""
    global _FN, _ITEMS
    items = list(items)
    workers = workers_for(len(items))
    if workers <= 1 or "fork" not in multiprocessing.get_all_start_methods():
        return [fn(x) for x in items]
    _FN, _ITEMS = fn, items
    try:
        with multiprocessing.get_context("fork").Pool(processes=workers) as pool:
            return pool.map(_call, range(len(items)), chunksize=1)
    finally:
        _FN, _ITEMS = None, None
