"""Filter the hand-written Spanish pairs for the twelve own schemas.

Input:  datos/generados/propios/<esquema>.jsonl  with {nivel, pregunta, sql}
Output: datos/generados/propios_filtrado.jsonl   pairs that passed
        datos/descartes.csv                      'propio' rows are replaced

A pair is kept when its query is a single SELECT/WITH, runs with the read-only
user under the default sql_mode, finishes in time and returns at least one row.
"""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parent.parent
ENTRADA = ROOT / "datos" / "generados" / "propios"
SALIDA = ROOT / "datos" / "generados" / "propios_filtrado.jsonl"
DESCARTES = ROOT / "datos" / "descartes.csv"
TIMEOUT_S = 5
NIVELES = {"facil", "media", "dificil"}
PROHIBIDO = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT)\b", re.I)


def esquema_de(cur) -> str:
    cur.execute("SHOW TABLES")
    textos = []
    for (t,) in cur.fetchall():
        cur.execute(f"SHOW CREATE TABLE `{t}`")
        textos.append(cur.fetchone()[1] + ";")
    return "\n\n".join(textos)


def clave(texto: str) -> str:
    return re.sub(r"\W+", " ", texto.lower()).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--solo", nargs="*", help="only these schemas")
    args = ap.parse_args()

    conn = pymysql.connect(host=args.host, user="lector", password="lector", charset="utf8mb4", autocommit=True)
    cur = conn.cursor()
    cur.execute(f"SET SESSION max_execution_time={TIMEOUT_S * 1000}")

    aceptados, descartes = [], []
    for archivo in sorted(ENTRADA.glob("*.jsonl")):
        nombre = archivo.stem
        if args.solo and nombre not in args.solo:
            continue
        cur.execute(f"USE `tr_{nombre}`")
        esquema = esquema_de(cur)
        vistas = set()
        for n, linea in enumerate(open(archivo, encoding="utf-8"), 1):
            if not linea.strip():
                continue
            pid = f"propio_{nombre}_{n:03d}"
            par = json.loads(linea)

            def descartar(motivo, detalle=""):
                descartes.append((pid, "propio", motivo, detalle[:200].replace("\n", " ")))

            sql = par["sql"].strip().rstrip(";")
            if par.get("nivel") not in NIVELES:
                descartar("nivel_invalido", str(par.get("nivel")))
                continue
            if not re.match(r"^(SELECT|WITH)\b", sql, re.I) or ";" in sql or PROHIBIDO.search(sql):
                descartar("no_select")
                continue
            k = clave(par["pregunta"])
            if k in vistas:
                descartar("duplicado")
                continue
            vistas.add(k)
            try:
                cur.execute(sql)
                filas = cur.fetchall()
            except pymysql.MySQLError as e:
                descartar("timeout" if e.args and e.args[0] == 3024 else "error_mysql", str(e.args))
                continue
            if not filas:
                descartar("resultado_vacio")
                continue
            aceptados.append({"id": pid, "db_id": f"tr_{nombre}", "fuente": "propio", "nivel": par["nivel"],
                              "esquema": esquema, "pregunta": par["pregunta"], "sql": sql})
    conn.close()

    previos = []
    if DESCARTES.exists():
        with open(DESCARTES, encoding="utf-8") as f:
            previos = [r for r in csv.reader(f)][1:]
        previos = [r for r in previos if r[1] != "propio" or (args.solo and not r[0].startswith(tuple(f"propio_{s}_" for s in args.solo)))]

    if args.solo and SALIDA.exists():
        # Partial run: keep pairs from the schemas that were not re-filtered.
        prefijos = tuple(f"propio_{s}_" for s in args.solo)
        aceptados = [json.loads(l) for l in open(SALIDA, encoding="utf-8") if not json.loads(l)["id"].startswith(prefijos)] + aceptados
    with open(SALIDA, "w", encoding="utf-8") as f:
        for a in sorted(aceptados, key=lambda a: a["id"]):
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    with open(DESCARTES, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "fuente", "motivo", "detalle"])
        w.writerows(previos + descartes)

    print(f"Aceptados: {len(aceptados)}  Descartados en esta corrida: {len(descartes)}")
    for motivo, n in Counter(d[2] for d in descartes).most_common():
        print(f"  {motivo}: {n}")
    for niv, n in Counter(a["nivel"] for a in aceptados).most_common():
        print(f"  nivel {niv}: {n}")
    for d in descartes[:15]:
        print("  >", d[0], d[2], d[3][:110])


if __name__ == "__main__":
    main()
