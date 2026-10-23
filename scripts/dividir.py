"""Assemble the final training set and check that no validation schema leaks into it.

Inputs:  datos/generados/spider_es.jsonl         Spider pairs, Spanish questions
         datos/generados/propios_filtrado.jsonl  hand-written pairs for the 12 own schemas
         datos/esquemas/validacion/*.sql         validation schemas (written by the validation owner)
         datos/validacion_propia.jsonl           validation questions, if present
Outputs: datos/entrenamiento.jsonl   pairs used to train
         datos/eval_loss.jsonl       pairs from held-out schemas, only for the eval-loss curve

The split is by schema: every pair of a database goes to the same side. The
script exits with an error if a validation table definition also appears in
training (the course penalizes that with -15).
"""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPIDER = ROOT / "datos" / "generados" / "spider_es.jsonl"
PROPIOS = ROOT / "datos" / "generados" / "propios_filtrado.jsonl"
VAL_ESQUEMAS = ROOT / "datos" / "esquemas" / "validacion"
VAL_PARES = ROOT / "datos" / "validacion_propia.jsonl"
ENTRENAMIENTO = ROOT / "datos" / "entrenamiento.jsonl"
EVAL_LOSS = ROOT / "datos" / "eval_loss.jsonl"
CAMPOS = ("id", "db_id", "fuente", "nivel", "esquema", "pregunta", "sql")
N_BASES_EVAL = 8
SEMILLA = 2026


def leer(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def tablas(texto: str) -> dict:
    """Map table name -> normalized definition (no comments, spaces or case)."""
    resultado = {}
    for bloque in re.split(r";\s*(?=CREATE TABLE)|;\s*$", texto):
        m = re.match(r"\s*CREATE TABLE\s+`?(\w+)`?", bloque, re.I)
        if not m:
            continue
        cuerpo = re.sub(r"COMMENT\s*=?\s*'(?:[^']|'')*'", "", bloque, flags=re.I)
        cuerpo = re.sub(r"(ENGINE|DEFAULT CHARSET|COLLATE|AUTO_INCREMENT)\s*=\s*\S+", "", cuerpo, flags=re.I)
        cuerpo = re.sub(r"`|\s+", "", cuerpo).lower()
        resultado[m.group(1).lower()] = cuerpo
    return resultado


def esquemas_validacion() -> dict:
    esquemas = {}
    if VAL_ESQUEMAS.exists():
        for f in sorted(VAL_ESQUEMAS.glob("*.sql")):
            esquemas[f.stem] = tablas(f.read_text(encoding="utf-8"))
    if VAL_PARES.exists():
        for p in leer(VAL_PARES):
            esquemas.setdefault(p["db_id"], tablas(p["esquema"]))
    return esquemas


def main() -> None:
    pares = leer(SPIDER) + leer(PROPIOS)

    train_tablas = {}  # normalized definition -> db_id where it appears
    nombres_por_db = {}
    for p in pares:
        t = tablas(p["esquema"])
        nombres_por_db[p["db_id"]] = set(t)
        for definicion in t.values():
            train_tablas.setdefault(definicion, p["db_id"])

    errores = []
    for nombre, t in esquemas_validacion().items():
        for tabla, definicion in t.items():
            if definicion in train_tablas:
                errores.append(f"validacion '{nombre}': la tabla '{tabla}' es identica a una de '{train_tablas[definicion]}'")
        for db, nombres in nombres_por_db.items():
            if t and len(set(t) & nombres) / len(t) >= 0.5 and len(set(t) & nombres) >= 3:
                print(f"AVISO: '{nombre}' comparte {len(set(t) & nombres)} nombres de tabla con '{db}' (no es fuga si las columnas difieren)")
    if errores:
        print("FUGA DE ESQUEMAS DE VALIDACION:")
        for e in errores:
            print("  -", e)
        sys.exit(1)

    spider_dbs = sorted({p["db_id"] for p in pares if p["fuente"] == "spider"})
    eval_dbs = set(random.Random(SEMILLA).sample(spider_dbs, N_BASES_EVAL))
    train = [p for p in pares if p["db_id"] not in eval_dbs]
    evalu = [p for p in pares if p["db_id"] in eval_dbs]

    for ruta, filas in ((ENTRENAMIENTO, train), (EVAL_LOSS, evalu)):
        with open(ruta, "w", encoding="utf-8") as f:
            for p in filas:
                f.write(json.dumps({k: p[k] for k in CAMPOS}, ensure_ascii=False) + "\n")

    print(f"Entrenamiento: {len(train)}  eval de loss: {len(evalu)}  (bases de eval: {', '.join(sorted(eval_dbs))})")
    print("Por fuente:", dict(Counter(p["fuente"] for p in train)))
    print("Por nivel:", dict(Counter(p["nivel"] for p in train)))
    print("Esquemas distintos en entrenamiento:", len({p["db_id"] for p in train}))
    print("Sin fuga de esquemas de validacion." if esquemas_validacion() else "AVISO: aun no hay esquemas de validacion contra los que comparar.")


if __name__ == "__main__":
    main()
