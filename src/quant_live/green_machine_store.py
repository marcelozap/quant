"""Private local storage for Green Machine research and journal records."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import subprocess
from typing import Any, Callable, Dict, Iterable, Optional
from uuid import uuid4


KEYCHAIN_SERVICE = "com.green-machine.local-store"
KEYCHAIN_ACCOUNT = "database-key"


class KeychainStore:
    """Reads the SQLCipher key from the logged-in macOS Keychain."""

    def get_or_create_key(self) -> str:
        find = subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", KEYCHAIN_ACCOUNT, "-w"],
            capture_output=True,
            text=True,
            check=False,
        )
        if find.returncode == 0 and find.stdout.strip():
            return find.stdout.strip()

        key = uuid4().hex + uuid4().hex
        create = subprocess.run(
            [
                "/usr/bin/security",
                "add-generic-password",
                "-U",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                KEYCHAIN_ACCOUNT,
                "-w",
                key,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if create.returncode != 0:
            raise RuntimeError("unable to create Green Machine database key in macOS Keychain")
        return key


ConnectionFactory = Callable[[str], Any]


class GreenMachineStore:
    """SQLCipher-backed local store. Raw broker files are never copied into the database."""

    def __init__(
        self,
        data_dir: str,
        keychain: Optional[KeychainStore] = None,
        connection_factory: Optional[ConnectionFactory] = None,
    ) -> None:
        self.data_dir = Path(data_dir).expanduser()
        self.database_path = self.data_dir / "green_machine.db"
        self.raw_dir = self.data_dir / "raw_imports"
        self.keychain = keychain or KeychainStore()
        self.connection_factory = connection_factory

    def initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.chmod(0o700)
        self.raw_dir.chmod(0o700)
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY,
                    record_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_records_type_updated
                    ON records(record_type, updated_at DESC);
                CREATE TABLE IF NOT EXISTS imports (
                    id TEXT PRIMARY KEY,
                    source_path TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    sha256 TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    row_count INTEGER,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS raw_imports (
                    import_id TEXT PRIMARY KEY,
                    content BLOB NOT NULL,
                    FOREIGN KEY(import_id) REFERENCES imports(id)
                );
                """
            )

    def put(self, record_type: str, payload: Dict[str, Any], record_id: Optional[str] = None) -> Dict[str, Any]:
        if not record_type or not record_type.replace("_", "").replace("-", "").isalnum():
            raise ValueError("record_type must contain only letters, numbers, hyphens, and underscores")
        now = datetime.now(timezone.utc).isoformat()
        item_id = record_id or str(uuid4())
        encoded = json.dumps(payload, sort_keys=True)
        with self._connection() as connection:
            existing = connection.execute("SELECT created_at FROM records WHERE id = ?", (item_id,)).fetchone()
            created_at = existing[0] if existing else now
            connection.execute(
                """
                INSERT INTO records(id, record_type, payload_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    record_type = excluded.record_type,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (item_id, record_type, encoded, created_at, now),
            )
        return {"id": item_id, "record_type": record_type, "payload": payload, "created_at": created_at, "updated_at": now}

    def list(self, record_type: str, limit: int = 100) -> list[Dict[str, Any]]:
        safe_limit = max(1, min(limit, 10_000))
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, record_type, payload_json, created_at, updated_at FROM records WHERE record_type = ? ORDER BY updated_at DESC LIMIT ?",
                (record_type, safe_limit),
            ).fetchall()
        return [
            {"id": row[0], "record_type": row[1], "payload": json.loads(row[2]), "created_at": row[3], "updated_at": row[4]}
            for row in rows
        ]

    def register_import(self, source_path: str, content: bytes, row_count: int) -> Dict[str, Any]:
        import hashlib

        digest = hashlib.sha256(content).hexdigest()
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT id, source_name, sha256, status, row_count, created_at FROM imports WHERE sha256 = ?",
                (digest,),
            ).fetchone()
            if existing:
                return {
                    "id": existing[0],
                    "source_name": existing[1],
                    "sha256": existing[2],
                    "status": existing[3],
                    "row_count": existing[4],
                    "created_at": existing[5],
                    "is_duplicate": True,
                }
            import_id = str(uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            connection.execute(
                "INSERT INTO imports(id, source_path, source_name, sha256, status, row_count, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (import_id, source_path, Path(source_path).name, digest, "imported", row_count, created_at),
            )
            connection.execute("INSERT INTO raw_imports(import_id, content) VALUES (?, ?)", (import_id, content))
        return {
            "id": import_id,
            "source_name": Path(source_path).name,
            "sha256": digest,
            "status": "imported",
            "row_count": row_count,
            "created_at": created_at,
            "is_duplicate": False,
        }

    def put_many(self, record_type: str, items: Iterable[tuple[str, Dict[str, Any]]]) -> int:
        now = datetime.now(timezone.utc).isoformat()
        rows = [(record_id, record_type, json.dumps(payload, sort_keys=True), now, now) for record_id, payload in items]
        if not rows:
            return 0
        with self._connection() as connection:
            connection.executemany(
                """
                INSERT INTO records(id, record_type, payload_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    record_type = excluded.record_type,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                rows,
            )
        return len(rows)

    def _connection(self) -> Any:
        if self.connection_factory:
            connection = self.connection_factory(str(self.database_path))
            return connection
        try:
            from sqlcipher3 import dbapi2 as sqlcipher  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "Green Machine requires SQLCipher for encrypted storage. Install with: pip install '.[green-machine-secure-store]'"
            ) from exc
        connection = sqlcipher.connect(str(self.database_path))
        key = self.keychain.get_or_create_key().replace("'", "''")
        connection.execute(f"PRAGMA key = '{key}'")
        connection.execute("PRAGMA cipher_memory_security = ON")
        return connection


def sqlite_development_connection(path: str) -> sqlite3.Connection:
    """Explicit test-only connection factory; never pass this in production."""
    return sqlite3.connect(path)
