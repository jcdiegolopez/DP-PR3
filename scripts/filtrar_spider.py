"""Filter the Spider training pairs against MySQL 8.4.10.

For every pair: convert the SQLite query to MySQL with sqlglot, run the original
on SQLite and the converted one on MySQL (as the read-only user, default
sql_mode), and keep the pair only if both give the same rows.

Writes:
  datos/generados/spider_filtrado.jsonl   pairs that passed (English question)
  datos/descartes.csv                     discarded pairs with the reason
"""
import argparse
import csv
import json
import re
import sqlite3
import time
from collections import Counter
from decimal import Decimal
from pathlib import Path

import pymysql
import sqlglot
from sqlglot import exp

ROOT = Path(__file__).resolve().parent.parent
SPIDER = ROOT / "spider_data" / "extracted" / "spider_data"
SALIDA = ROOT / "datos" / "generados" / "spider_filtrado.jsonl"
DESCARTES = ROOT / "datos" / "descartes.csv"
CARGA = ROOT / "datos" / "esquemas" / "spider_carga.csv"
TIMEOUT_S = 5


def normalizar(valor):
    """Make SQLite and MySQL values comparable (round numbers, text as is)."""
    if valor is None:
        return None
    if isinstance(valor, (int, float, Decimal)):
        return round(float(valor), 2)
    return str(valor)


def filas_normalizadas(filas):
    # Multiset comparison: row order is not part of the check here.
    return sorted((tuple(normalizar(v) for v in f) for f in filas), key=repr)


def ejecutar_sqlite(path, sql):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.text_factory = lambda b: b.decode("utf-8", errors="replace")
    inicio = time.time()
    con.set_progress_handler(lambda: 1 if time.time() - inicio > TIMEOUT_S else 0, 100000)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def a_mysql(sql_sqlite: str, tablas: dict) -> str:
    """SQLite -> MySQL, fixing two things sqlglot cannot know about Spider.

    Spider writes text values in double quotes ("Village"), which sqlglot reads as
    identifiers, so they become single-quoted strings first. MySQL on Linux is
    case-sensitive for table names, so each table is renamed to its real casing.
    """
    sql = re.sub(r'"([^"]*)"', lambda m: "'" + m.group(1).replace("'", "''") + "'", sql_sqlite)
    tree = sqlglot.parse_one(sql, read="sqlite")
    for tabla in tree.find_all(exp.Table):
        real = tablas.get(tabla.name.lower())
        if real:
            tabla.set("this", exp.to_identifier(real))
    return tree.sql(dialect="mysql")


def nivel(sql_mysql: str) -> str:
    """Rough difficulty from the AST, aligned with the project's three levels."""
    tree = sqlglot.parse_one(sql_mysql, read="mysql")
    n_select = len(list(tree.find_all(exp.Select)))
    dificil = (
        tree.find(exp.With) or tree.find(exp.Window)
        or tree.find(exp.Union) or tree.find(exp.Intersect) or tree.find(exp.Except)
        or n_select > 1 or len(list(tree.find_all(exp.Join))) >= 3
    )
    if dificil:
        return "dificil"
    if tree.find(exp.Join) or tree.find(exp.Group) or tree.find(exp.Having):
        return "media"
    return "facil"


def nombres_tablas(cur, db_id: str) -> list:
    cur.execute(f"USE `sp_{db_id}`")
    cur.execute("SHOW TABLES")
    return [r[0] for r in cur.fetchall()]


def esquema_de(cur, db_id: str) -> str:
    tablas = nombres_tablas(cur, db_id)
    textos = []
    for t in tablas:
        cur.execute(f"SHOW CREATE TABLE `{t}`")
        textos.append(cur.fetchone()[1] + ";")
    return "\n\n".join(textos)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--limite", type=int, default=0, help="only the first N pairs (testing)")
    args = ap.parse_args()

    pares = json.load(open(SPIDER / "train_spider.json", encoding="utf-8"))
    if args.limite:
        pares = pares[: args.limite]

    bases_malas = set()
    if CARGA.exists():
        with open(CARGA, encoding="utf-8") as f:
            bases_malas = {r["db_id"] for r in csv.DictReader(f) if r["estado"] != "ok"}

    # Read-only user and the server's default sql_mode, like the hidden evaluation.
    conn = pymysql.connect(host=args.host, user="lector", password="lector",
                           charset="utf8mb4", autocommit=True)
    cur = conn.cursor()
    cur.execute(f"SET SESSION max_execution_time={TIMEOUT_S * 1000}")

    esquemas, mapa_tablas = {}, {}
    aceptados, descartes = [], []
    for i, p in enumerate(pares):
        pid, db_id, sql_orig = f"spider_{i:05d}", p["db_id"], p["query"]

        def descartar(motivo, detalle=""):
            descartes.append((pid, "spider", motivo, detalle[:200].replace("\n", " ")))

        if db_id in bases_malas:
            descartar("base_no_carga", db_id)
            continue
        if not sql_orig.lstrip().upper().startswith(("SELECT", "WITH")):
            descartar("no_select")
            continue
        try:
            if db_id not in mapa_tablas:
                mapa_tablas[db_id] = {t.lower(): t for t in nombres_tablas(cur, db_id)}
            sql_mysql = a_mysql(sql_orig, mapa_tablas[db_id])
        except Exception as e:
            descartar("conversion_error", f"{type(e).__name__}: {e}")
            continue
        try:
            filas_mysql = None
            cur.execute(f"USE `sp_{db_id}`")
            cur.execute(sql_mysql)
            filas_mysql = cur.fetchall()
            columnas = [d[0] for d in cur.description]
        except pymysql.MySQLError as e:
            motivo = "timeout" if e.args and e.args[0] == 3024 else "error_mysql"
            descartar(motivo, f"{e.args}")
            continue
        try:
            filas_sqlite = ejecutar_sqlite(SPIDER / "database" / db_id / f"{db_id}.sqlite", sql_orig)
        except sqlite3.Error as e:
            descartar("error_sqlite", str(e))
            continue
        if not filas_mysql:
            descartar("resultado_vacio")
            continue
        if filas_normalizadas(filas_mysql) != filas_normalizadas(filas_sqlite):
            descartar("resultado_distinto")
            continue
        if db_id not in esquemas:
            esquemas[db_id] = esquema_de(cur, db_id)
        aceptados.append({
            "id": pid, "db_id": db_id, "fuente": "spider",
            "nivel": nivel(sql_mysql), "esquema": esquemas[db_id],
            "pregunta_en": p["question"], "sql": sql_mysql, "columnas": columnas,
        })
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(pares)}  aceptados={len(aceptados)}")
    conn.close()

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        for a in aceptados:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    with open(DESCARTES, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "fuente", "motivo", "detalle"])
        w.writerows(descartes)

    print(f"\nProcesados: {len(pares)}  Aceptados: {len(aceptados)}  Descartados: {len(descartes)}")
    for motivo, n in Counter(d[2] for d in descartes).most_common():
        print(f"  {motivo}: {n}")
    for niv, n in Counter(a["nivel"] for a in aceptados).most_common():
        print(f"  nivel {niv}: {n}")


if __name__ == "__main__":
    main()
