"""Controls for `simulation.fork_map`: forked workers, a closure they could not be pickled, and the
input order kept.

The book-level claim, that the parallel trace build settles the same book as the serial one, was
measured on a 40-founder run to 2017 (2026-10-08): identical digests of all 39,178 settled
records, the events, the treasury path, the eligibility verdicts and the demand providers, wall
196 s serial against 117 s forked. Those runs are minutes long, so they are evidence for the
commit, not a test here.
"""
import os

import pytest

from simulation import fork_map as fm


def test_a_closure_is_mapped_in_FORKED_workers_and_comes_back_in_input_order(monkeypatch):
    """Defect: the pool is a pickling one (it cannot send the run's closures), or the results come
    back in completion order, so a trace lands on the wrong customer.

    THE WORKERS MUST BE OTHER PROCESSES, or "parallel" is the serial path with extra steps and the
    order assertion proves nothing about ordering under concurrency.
    """
    monkeypatch.setenv("SE_FORK_WORKERS", "4")
    offset = 1000  # captured by the closure below, which a pickling pool would refuse

    def work(x):
        return (x + offset, os.getpid())

    out = fm.fork_map(work, list(range(40)))
    assert [v for v, _ in out] == [x + offset for x in range(40)]
    assert {pid for _, pid in out} - {os.getpid()}, "nothing ran outside this process"


def test_one_worker_is_the_serial_path_in_this_process(monkeypatch):
    """The control path the book comparison runs on: `SE_FORK_WORKERS=1` must not fork."""
    monkeypatch.setenv("SE_FORK_WORKERS", "1")
    assert {pid for pid in fm.fork_map(lambda _x: os.getpid(), range(5))} == {os.getpid()}


def test_a_worker_failure_reaches_the_caller(monkeypatch):
    """Defect: a trace that raises in a worker is swallowed and the customer silently drops out."""
    monkeypatch.setenv("SE_FORK_WORKERS", "3")

    def boom(x):
        if x == 2:
            raise ValueError("premise 2 has no weather")
        return x

    with pytest.raises(ValueError, match="premise 2 has no weather"):
        fm.fork_map(boom, range(6))


def test_workers_are_sized_by_free_memory_and_never_take_a_landings_room(monkeypatch):
    """Director, 2026-10-09: "Size forked trace workers by free memory, not a fixed count, so a
    speed-up can't crowd out a landing." Both sides: plenty of memory gives the CPU-bound count;
    memory at the floor gives the serial path. A fixed count passes the first and fails this."""
    monkeypatch.delenv("SE_FORK_WORKERS", raising=False)
    floor = fm._memory_floor_mb()
    plenty = fm.workers_for(100, available_mb=floor + 10_000)
    assert plenty == max(1, (os.cpu_count() or 1) - fm.RESERVED_CPUS)
    assert fm.workers_for(100, available_mb=floor + 2 * fm.WORKER_PSS_MB) == 2
    assert fm.workers_for(100, available_mb=floor - 1) == 1
    import background.resource_headroom as rh
    monkeypatch.setattr(rh, "sample", lambda: {"available_mb": None})
    assert fm.workers_for(100) == 1, "unreadable memory must be the serial path"
