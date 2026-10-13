from __future__ import annotations

import sqlite3
from collections.abc import Callable
from typing import Any, overload
from weakref import WeakSet


class FinalizingSQLiteConnection(sqlite3.Connection):
    """Finalize SQLAlchemy cursors even when cancellation retains their frames.

    sqlite3 connection close alone can leave an unfinished RETURNING statement
    holding the writer lock until its cursor is collected. SQLAlchemy uses
    cursor(), so track those cursors without extending their lifetime. Both
    cursor creation and close run on the existing aiosqlite worker thread.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cursors: WeakSet[sqlite3.Cursor] = WeakSet()

    @overload
    def cursor(self, factory: None = None) -> sqlite3.Cursor: ...

    @overload
    def cursor[C: sqlite3.Cursor](self, factory: Callable[[sqlite3.Connection], C]) -> C: ...

    def cursor(self, factory: Callable[[sqlite3.Connection], sqlite3.Cursor] | None = None) -> sqlite3.Cursor:
        cursor = super().cursor() if factory is None else super().cursor(factory)
        self._cursors.add(cursor)
        return cursor

    def close(self) -> None:
        try:
            for cursor in tuple(self._cursors):
                cursor.close()
        finally:
            self._cursors.clear()
            super().close()
