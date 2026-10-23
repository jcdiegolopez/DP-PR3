"""Load the Spider training databases (SQLite) into MySQL 8.4.

Each Spider db_id becomes a MySQL database named sp_<db_id>. Column types are
inferred from the data, and foreign keys are added after loading (best effort).
Databases that do not load cleanly are listed in datos/esquemas/spider_carga.csv
so their pairs can be discarded with the reason base_no_carga.
"""
import argparse
import csv
import json
import sqlite3
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parent.parent
SPIDER = ROOT / "spider_data" / "extracted" / "spider_data"
REPORTE = ROOT / "datos" / "esquemas" / "spider_carga.csv"
BATCH = 1000


def q(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def infer_type(declared: str, values: list) -> str:
    """Pick a MySQL type from the declared SQLite type and the real values."""
    values = [v for v in values if v is not None]
    if "CHAR" in declared or "TEXT" in declared or "CLOB" in declared:
        is_text = True
    else:
        is_text = any(isinstance(v, (str, bytes)) for v in values)
    if is_text:
        longest = max((len(str(v)) for v in values), default=0)
        # Sized to the data (not a flat 255) so composite primary keys fit in an index.
        return f"VARCHAR({min(255, max(32, longest * 2))})" if longest <= 255 else "TEXT"
    if values and all(isinstance(v, int) for v in values):
        return "BIGINT"
    if values and all(isinstance(v, (int, float)) for v in values):
        return "DOUBLE"
    return "VARCHAR(255)"


def load_db(conn, db_id: str, sqlite_path: Path) -> None:
    src = sqlite3.connect(sqlite_path)
    src.text_factory = lambda b: b.decode("utf-8", errors="replace")
    tables = [r[0] for r in src.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    fks = []
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {q('sp_' + db_id)}")
        cur.execute(f"CREATE DATABASE {q('sp_' + db_id)} CHARACTER SET utf8mb4")
        cur.execute(f"USE {q('sp_' + db_id)}")
        for t in tables:
            cols = src.execute(f"PRAGMA table_info({q(t)})").fetchall()
            rows = src.execute(f"SELECT * FROM {q(t)}").fetchall()
            defs, pks = [], []
            for i, (_, name, declared, _, _, pk) in enumerate(cols):
                mysql_type = infer_type((declared or "").upper(), [r[i] for r in rows])
                defs.append(f"{q(name)} {mysql_type}")
                if pk:
                    pks.append((pk, name))
            if pks:
                pk_cols = ", ".join(q(n) for _, n in sorted(pks))
                defs.append(f"PRIMARY KEY ({pk_cols})")
            cur.execute(f"CREATE TABLE {q(t)} ({', '.join(defs)}) CHARACTER SET utf8mb4")
            if rows:
                marks = ", ".join(["%s"] * len(cols))
                sql = f"INSERT IGNORE INTO {q(t)} VALUES ({marks})"
                for start in range(0, len(rows), BATCH):
                    cur.executemany(sql, rows[start:start + BATCH])
            for fk in src.execute(f"PRAGMA foreign_key_list({q(t)})"):
                fks.append((t, fk[3], fk[2], fk[4]))
        conn.commit()
        # Foreign keys last, so load order does not matter. A failure here only
        # means the schema text has no FOREIGN KEY line, not that the data is bad.
        for t, col, ref_t, ref_col in fks:
            if ref_col is None:
                continue
            try:
                cur.execute(
                    f"ALTER TABLE {q(t)} ADD FOREIGN KEY ({q(col)}) "
                    f"REFERENCES {q(ref_t)} ({q(ref_col)})")
            except pymysql.MySQLError:
                pass
        conn.commit()
    src.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--password", default="root")
    args = ap.parse_args()

    train = json.load(open(SPIDER / "train_spider.json", encoding="utf-8"))
    db_ids = sorted({ex["db_id"] for ex in train})

    # Non-strict only while loading: Spider has dirty values. Queries are
    # evaluated later on a separate connection with the default sql_mode.
    conn = pymysql.connect(host=args.host, user="root", password=args.password,
                           charset="utf8mb4", autocommit=False,
                           init_command="SET SESSION sql_mode=''")
    REPORTE.parent.mkdir(parents=True, exist_ok=True)
    resultados = []
    for n, db_id in enumerate(db_ids, 1):
        path = SPIDER / "database" / db_id / f"{db_id}.sqlite"
        try:
            if not path.exists():
                raise FileNotFoundError(path.name)
            load_db(conn, db_id, path)
            resultados.append((db_id, "ok", ""))
            print(f"[{n}/{len(db_ids)}] {db_id}: ok")
        except Exception as e:  # keep going; the failure is reported, not hidden
            conn.rollback()
            resultados.append((db_id, "error", f"{type(e).__name__}: {e}"[:300]))
            print(f"[{n}/{len(db_ids)}] {db_id}: ERROR {e}")
    conn.close()

    with open(REPORTE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["db_id", "estado", "detalle"])
        w.writerows(resultados)
    ok = sum(1 for r in resultados if r[1] == "ok")
    print(f"\nCargadas: {ok}/{len(db_ids)}. Reporte: {REPORTE}")


if __name__ == "__main__":
    main()
