"""Tests for background/tree_lock.py -- cross-process working-tree lock."""
import multiprocessing
import time

import pytest

from background import tree_lock as tl


def test_lock_is_reentrant_safe_sequential(tmp_path, monkeypatch):
    """Acquiring and releasing the lock twice in sequence (not nested) works."""
    monkeypatch.setattr(tl, "LOCK_FILE", tmp_path / ".tree.lock")
    with tl.tree_lock():
        pass
    with tl.tree_lock():
        pass


def test_lock_creates_parent_dir(tmp_path, monkeypatch):
    lock_path = tmp_path / "nested" / "dir" / ".tree.lock"
    monkeypatch.setattr(tl, "LOCK_FILE", lock_path)
    with tl.tree_lock():
        assert lock_path.parent.is_dir()


def _hold_lock_in_subprocess(lock_path_str, hold_seconds, ready_flag_path):
    import fcntl
    with open(lock_path_str, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        with open(ready_flag_path, "w") as rf:
            rf.write("ready")
        time.sleep(hold_seconds)
        fcntl.flock(fh, fcntl.LOCK_UN)


def test_lock_blocks_concurrent_holder(tmp_path, monkeypatch):
    """A second process holding the lock blocks tree_lock() until it releases."""
    lock_path = tmp_path / ".tree.lock"
    ready_flag = tmp_path / "ready.flag"
    monkeypatch.setattr(tl, "LOCK_FILE", lock_path)

    proc = multiprocessing.Process(
        target=_hold_lock_in_subprocess, args=(str(lock_path), 1.0, str(ready_flag))
    )
    proc.start()
    deadline = time.monotonic() + 5
    while not ready_flag.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert ready_flag.exists(), "subprocess never signalled it held the lock"

    start = time.monotonic()
    with tl.tree_lock(timeout=5):
        elapsed = time.monotonic() - start
    proc.join()
    assert elapsed >= 0.5, "tree_lock() should have blocked while the subprocess held the lock"


def test_lock_times_out_if_held_too_long(tmp_path, monkeypatch):
    lock_path = tmp_path / ".tree.lock"
    ready_flag = tmp_path / "ready.flag"
    monkeypatch.setattr(tl, "LOCK_FILE", lock_path)

    proc = multiprocessing.Process(
        target=_hold_lock_in_subprocess, args=(str(lock_path), 3.0, str(ready_flag))
    )
    proc.start()
    deadline = time.monotonic() + 5
    while not ready_flag.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert ready_flag.exists()

    with pytest.raises(tl.TreeLockTimeout):
        with tl.tree_lock(timeout=0.3):
            pass
    proc.join()


def test_lock_released_on_exception(tmp_path, monkeypatch):
    """The lock must release even if the `with` block raises, so a failed
    writer doesn't strand every other process forever."""
    monkeypatch.setattr(tl, "LOCK_FILE", tmp_path / ".tree.lock")

    with pytest.raises(ValueError):
        with tl.tree_lock():
            raise ValueError("boom")

    # If the lock wasn't released, this would time out.
    with tl.tree_lock(timeout=2):
        pass
