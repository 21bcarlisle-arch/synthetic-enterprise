"""The run's settled book held as typed columns, read through dict-like `Row` views.

WHY (run review, 2026-10-08): the daily rows `run_phase2b` retains in `all_records` were 33-key
dicts at ~1,570 bytes each -- 0.57 MB per settled leg-year and about 45% of a run's memory slope.
The same values in typed columns are ~260 bytes a row.

WHAT IS PRESERVED, EXACTLY, because every reader downstream was written against a list of dicts:

  * each value's TYPE and VALUE. A column is typed only while every value in it is the same exact
    Python type (`float` -> float64, `int` -> int64, `bool` -> int8); the first value of any other
    type -- an int in a float column, a numpy scalar, a string, None, a nested dict -- turns the
    whole column into an object list. So `type(row[k])` is never coerced: a column that holds 0
    and 0.5 hands back the int 0 and the float 0.5, as the dicts did.
  * which keys a row HAS and in what ORDER. Each row points at a schema (its key tuple, shared by
    every row with the same keys), so `"k" in row`, `row.get("k", d)`, `list(row)` and
    `json.dumps(row.to_dict())` answer as the source dict did. A missing key stays missing.
  * write-through. `row[k] = v` writes the column; the arrears engine's corrections after the
    commit land in the table, not in a detached copy.

WHAT A READER MUST NOT ASSUME. A `Row` is a `collections.abc.MutableMapping`, NOT a `dict`, and
the table is a `collections.abc.Sequence`, NOT a `list`. Neither subclasses the builtin on purpose:
a dict or list subclass with its own storage presents an EMPTY C-level container to
`json.dumps`, `dict(...)`'s fast path and `{**x}`, which would publish `{}`/`[]` without a word.
Not subclassing makes those failures LOUD (`TypeError: Object of type Row is not JSON
serializable`). The silent failure that remains is a reader that gates on `isinstance(x, dict)`
or `isinstance(x, list)` and skips what fails -- every such gate on records reads
`collections.abc.Mapping` / `Sequence` instead (`tests/simulation/test_record_table.py` names the
sites). `json_default` is the `default=` for a dump that may meet either.

Copies DETACH: `row.copy()`, `copy.copy(row)`, `copy.deepcopy(row)` and pickling a row all give
a plain dict, the semantics `dict.copy()` has. Pickling or deep-copying the TABLE gives a table.
"""

from __future__ import annotations

import sys
from array import array
from collections.abc import Mapping, MutableMapping, Sequence

_MISSING = object()
_INT64_MIN, _INT64_MAX = -(2 ** 63), 2 ** 63 - 1

#: kind -> (array typecode or None for an object list, filler for a row that lacks the key)
_FILLER = {"f": 0.0, "i": 0, "b": 0, "o": None}


def _kind(v) -> str:
    t = type(v)
    if t is float:
        return "f"
    if t is bool:
        return "b"
    if t is int and _INT64_MIN <= v <= _INT64_MAX:
        return "i"
    return "o"


def _new_store(kind: str, n: int):
    if kind == "f":
        return array("d", bytes(8 * n))
    if kind == "i":
        return array("q", bytes(8 * n))
    if kind == "b":
        return array("b", bytes(n))
    return [None] * n


def _stored(kind: str, v):
    if kind == "b":
        return 1 if v else 0
    if kind == "o" and type(v) is str:
        return sys.intern(v)
    return v


class Row(MutableMapping):
    """One settled record: a live view of row `i` of a `RecordTable`."""

    __slots__ = ("_t", "_i")

    def __init__(self, table: RecordTable, index: int) -> None:
        self._t = table
        self._i = index

    def __getitem__(self, key):
        t = self._t
        i = self._i
        if key not in t._schema_sets[t._row_schema[i]]:
            raise KeyError(key)
        kind, store = t._cols[key]
        v = store[i]
        return bool(v) if kind == "b" else v

    def get(self, key, default=None):
        t = self._t
        i = self._i
        if key not in t._schema_sets[t._row_schema[i]]:
            return default
        kind, store = t._cols[key]
        v = store[i]
        return bool(v) if kind == "b" else v

    def __contains__(self, key) -> bool:
        t = self._t
        return key in t._schema_sets[t._row_schema[self._i]]

    def __setitem__(self, key, value) -> None:
        self._t._set(self._i, key, value)

    def __delitem__(self, key) -> None:
        self._t._delete(self._i, key)

    def __iter__(self):
        t = self._t
        return iter(t._schemas[t._row_schema[self._i]])

    def __len__(self) -> int:
        t = self._t
        return len(t._schemas[t._row_schema[self._i]])

    def keys(self):
        # A KeysView over the live row, as dict.keys() is.
        return super().keys()

    def to_dict(self) -> dict:
        t = self._t
        i = self._i
        out = {}
        cols = t._cols
        for key in t._schemas[t._row_schema[i]]:
            kind, store = cols[key]
            v = store[i]
            out[key] = bool(v) if kind == "b" else v
        return out

    copy = to_dict

    def __eq__(self, other):
        if isinstance(other, Row):
            return self.to_dict() == other.to_dict()
        if isinstance(other, Mapping):
            return self.to_dict() == (other if isinstance(other, dict) else dict(other.items()))
        return NotImplemented

    __hash__ = None  # mutable, as a dict is

    def __or__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        out = self.to_dict()
        out.update(other)
        return out

    def __ror__(self, other):
        if not isinstance(other, Mapping):
            return NotImplemented
        out = dict(other)
        out.update(self.to_dict())
        return out

    def __ior__(self, other):
        self.update(other)
        return self

    def __reduce__(self):
        return (dict, (self.to_dict(),))

    def __repr__(self) -> str:
        return repr(self.to_dict())


class RecordTable(Sequence):
    """The settled book: a sequence of `Row`s over typed columns. Append-only at the row level."""

    def __init__(self, rows=()) -> None:
        self._n = 0
        #: key-order tuples, shared by every row with that exact key sequence
        self._schemas: list[tuple] = []
        self._schema_sets: list[frozenset] = []
        self._schema_index: dict[tuple, int] = {}
        self._row_schema = array("I")
        #: key -> [kind, store]; every store has exactly `_n` slots
        self._cols: dict = {}
        if rows:
            self.extend(rows)

    # ---- schema / column plumbing ------------------------------------------------------------
    def _schema_id(self, keys: tuple) -> int:
        sid = self._schema_index.get(keys)
        if sid is None:
            sid = len(self._schemas)
            self._schemas.append(keys)
            self._schema_sets.append(frozenset(keys))
            self._schema_index[keys] = sid
        return sid

    def _promote(self, key) -> None:
        col = self._cols[key]
        kind, store = col
        if kind == "o":
            return
        col[1] = [bool(x) for x in store] if kind == "b" else list(store)
        col[0] = "o"

    def _set(self, i: int, key, value) -> None:
        vk = _kind(value)
        col = self._cols.get(key)
        if col is None:
            col = self._cols[key] = [vk, _new_store(vk, self._n)]
        elif col[0] != vk:
            self._promote(key)
        col[1][i] = _stored(col[0], value)
        sid = self._row_schema[i]
        if key not in self._schema_sets[sid]:
            self._row_schema[i] = self._schema_id(self._schemas[sid] + (key,))

    def _delete(self, i: int, key) -> None:
        sid = self._row_schema[i]
        if key not in self._schema_sets[sid]:
            raise KeyError(key)
        self._row_schema[i] = self._schema_id(tuple(k for k in self._schemas[sid] if k != key))
        kind, store = self._cols[key]
        store[i] = _FILLER[kind]

    # ---- building -----------------------------------------------------------------------------
    def extend(self, rows) -> None:
        dicts = []
        for r in rows:
            if isinstance(r, Row):
                dicts.append(r.to_dict())
            elif isinstance(r, Mapping):
                dicts.append(r)
            else:
                raise TypeError(f"a RecordTable holds mappings, not {type(r).__name__}")
        if not dicts:
            return
        m = len(dicts)
        n0 = self._n
        seen: dict = {}
        for d in dicts:
            keys = tuple(d)
            self._row_schema.append(self._schema_id(keys))
            for k in keys:
                seen[k] = None
        for key in seen:
            vals = [d.get(key, _MISSING) for d in dicts]
            kinds = {_kind(v) for v in vals if v is not _MISSING}
            col = self._cols.get(key)
            if col is None:
                kind = kinds.pop() if len(kinds) == 1 else "o"
                col = self._cols[key] = [kind, _new_store(kind, n0)]
            elif kinds - {col[0]}:
                self._promote(key)
            kind, store = col
            fill = _FILLER[kind]
            if kind == "f" or kind == "i":
                store.extend([fill if v is _MISSING else v for v in vals])
            else:
                store.extend([fill if v is _MISSING else _stored(kind, v) for v in vals])
        for key, (kind, store) in self._cols.items():
            if key not in seen:
                fill = _FILLER[kind]
                store.extend([fill] * m)
        self._n = n0 + m

    def append(self, row) -> None:
        self.extend([row])

    # ---- the Sequence ---------------------------------------------------------------------------
    def __len__(self) -> int:
        return self._n

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [Row(self, i) for i in range(*index.indices(self._n))]
        n = self._n
        if index < 0:
            index += n
        if not 0 <= index < n:
            raise IndexError("RecordTable index out of range")
        return Row(self, index)

    def __setitem__(self, index, row) -> None:
        """Replace one row wholesale, as `records[i] = {...}` replaces a list element."""
        if not isinstance(row, Mapping):
            raise TypeError(f"a RecordTable holds mappings, not {type(row).__name__}")
        src = row.to_dict() if isinstance(row, Row) else dict(row)
        target = self[index]
        i = target._i
        for key in list(target):
            if key not in src:
                self._delete(i, key)
        for key, value in src.items():
            self._set(i, key, value)
        self._row_schema[i] = self._schema_id(tuple(src))

    def __iter__(self):
        i = 0
        while i < self._n:
            yield Row(self, i)
            i += 1

    def __eq__(self, other):
        if isinstance(other, (RecordTable, list, tuple)):
            return len(self) == len(other) and all(a == b for a, b in zip(self, other))
        return NotImplemented

    __hash__ = None

    def __add__(self, other):
        if isinstance(other, (RecordTable, list)):
            return list(self) + list(other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, list):
            return other + list(self)
        return NotImplemented

    def copy(self) -> list:
        """A shallow copy, as `list.copy()` is: a new list holding the same (live) rows."""
        return list(self)

    def to_dicts(self) -> list[dict]:
        return [r.to_dict() for r in self]

    def column_kinds(self) -> dict:
        """key -> 'f' | 'i' | 'b' | 'o', for a reader auditing what stayed typed."""
        return {k: c[0] for k, c in self._cols.items()}

    def nbytes(self) -> int:
        """Bytes held by the columns' own buffers (object columns count their pointer slots only)."""
        total = self._row_schema.itemsize * len(self._row_schema)
        for kind, store in self._cols.values():
            total += store.itemsize * len(store) if kind != "o" else 8 * len(store)
        return total

    def __reduce__(self):
        return (_rebuild, (self._schemas, array("I", self._row_schema),
                           {k: [c[0], c[1][:]] for k, c in self._cols.items()}, self._n))

    def __repr__(self) -> str:
        return f"<RecordTable {self._n} rows x {len(self._cols)} columns>"


def _rebuild(schemas, row_schema, cols, n) -> RecordTable:
    t = RecordTable()
    for keys in schemas:
        t._schema_id(tuple(keys))
    t._row_schema = array("I", row_schema)
    t._cols = {k: [c[0], c[1]] for k, c in cols.items()}
    t._n = n
    return t


def json_default(o, fallback=None):
    """`default=` for a json dump that may meet the book: a row as its dict, the table as a list.
    Anything else is refused exactly as json refuses it, so this cannot mask a different type --
    unless the caller already had a `default=` (`fallback`), which then sees everything else.
    A dump that had `default=str` must pass `functools.partial(json_default, fallback=str)`:
    left alone, `str` would publish the book as the one-line repr of a table."""
    if isinstance(o, Row):
        return o.to_dict()
    if isinstance(o, RecordTable):
        return o.to_dicts()
    if fallback is not None:
        return fallback(o)
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
