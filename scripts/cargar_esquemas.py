"""Create one MySQL database per schema file in datos/esquemas/<grupo>/.

Training schemas become tr_<name> and validation schemas va_<name>. The prefix
keeps the two groups apart, so the leakage check can tell them apart.
"""
import argparse
from pathlib import Path

import pymysql
from pymysql.constants import CLIENT

ROOT = Path(__file__).resolve().parent.parent
GRUPOS = {"entrenamiento": "tr", "validacion": "va"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--password", default="root")
    ap.add_argument("--grupo", choices=list(GRUPOS), default="entrenamiento")
    args = ap.parse_args()

    conn = pymysql.connect(host=args.host, user="root", password=args.password,
                           charset="utf8mb4", client_flag=CLIENT.MULTI_STATEMENTS)
    cur = conn.cursor()
    prefijo = GRUPOS[args.grupo]
    for archivo in sorted((ROOT / "datos" / "esquemas" / args.grupo).glob("*.sql")):
        db = f"{prefijo}_{archivo.stem}"
        cur.execute(f"DROP DATABASE IF EXISTS `{db}`")
        cur.execute(f"CREATE DATABASE `{db}` CHARACTER SET utf8mb4")
        cur.execute(f"USE `{db}`")
        cur.execute(archivo.read_text(encoding="utf-8"))
        while cur.nextset():  # drain the remaining statements of the script
            pass
        cur.execute("SHOW TABLES")
        print(f"{db}: {len(cur.fetchall())} tablas")
    conn.close()


if __name__ == "__main__":
    main()
