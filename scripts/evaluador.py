"""Evaluador de exactitud por ejecucion (EX) ponderada segun las reglas del curso.

Criterios del docente (Guia Seccion 4 y 5):
- Niveles y pesos:
    * facil: peso 1 (una sola tabla)
    * media: peso 2 (JOIN, GROUP BY, HAVING)
    * dificil: peso 3 (subconsultas, WITH, funciones de ventana, fechas)
- Criterio de acierto:
    * Se compara el resultado de la consulta predicha contra la de referencia.
    * El orden de las filas solo cuenta si la pregunta lo pide (o la referencia tiene ORDER BY).
    * Los numeros se redondean a 2 decimales.
    * Una columna adicional no penaliza.
- Metrica: EX = suma(pesos acertados) / suma(pesos totales).
- Clasificacion de errores:
    * sintaxis, columna o tabla inexistente, JOIN, agregacion, filtro, resultado_distinto.

Uso:
  python scripts/evaluador.py --variante baseline
  python scripts/evaluador.py --variante config_A --autocorreccion
  python scripts/evaluador.py --variante config_B
"""
import argparse
import csv
import decimal
import json
import os
import re
import sys
import time
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PESOS = {"facil": 1, "media": 2, "dificil": 3}


def normalizar_valor(val):
    """Normaliza un valor de celda para comparacion: redondea floats/decimals a 2 decimales."""
    if val is None:
        return None
    if isinstance(val, (float, decimal.Decimal)):
        return round(float(val), 2)
    if isinstance(val, (bytes, bytearray)):
        return val.decode("utf-8", errors="ignore")
    # Fechas / datetimes a string ISO
    if hasattr(val, "isoformat"):
        return str(val)
    if isinstance(val, str):
        val = val.strip()
        # Intentar convertir a float numerico por si viene formateado
        try:
            return round(float(val), 2)
        except ValueError:
            return val
    return val


def ordenar_filas(filas):
    """Convierte filas a representacion ordenable para comparar como multiconjunto."""
    def clave_fila(f):
        return tuple(str(x) for x in f)
    return sorted(filas, key=clave_fila)


def coincide_con_columnas_extra(filas_ref, filas_pred, orden_importa):
    """Verifica si filas_pred contiene todas las columnas de filas_ref.
    
    Regla del profesor: 'Una columna adicional no penaliza'.
    """
    if len(filas_ref) != len(filas_pred):
        return False
    if len(filas_ref) == 0:
        return True

    num_cols_ref = len(filas_ref[0])
    num_cols_pred = len(filas_pred[0])
    if num_cols_pred < num_cols_ref:
        return False

    # Probar si existe un subconjunto de columnas en pred que iguale a ref
    indices_pred = list(range(num_cols_pred))
    for cols_seleccionadas in permutations(indices_pred, num_cols_ref):
        sub_pred = [[f[c] for c in cols_seleccionadas] for f in filas_pred]
        if orden_importa:
            if sub_pred == filas_ref:
                return True
        else:
            if ordenar_filas(sub_pred) == ordenar_filas(filas_ref):
                return True
    return False


def comparar_resultados(filas_ref, filas_pred, orden_importa=False):
    """Compara resultados aplicando redondeo a 2 decimales y tolerancia a columnas extra."""
    norm_ref = [[normalizar_valor(c) for c in f] for f in filas_ref]
    norm_pred = [[normalizar_valor(c) for c in f] for f in filas_pred]

    return coincide_con_columnas_extra(norm_ref, norm_pred, orden_importa)


def clasificar_error(sql_pred, sql_ref, err_msg) -> str:
    """Clasifica el error en una de las categorias requeridas por la guia."""
    if err_msg:
        err_lower = err_msg.lower()
        if "syntax" in err_lower or "you have an error in your sql syntax" in err_lower:
            return "sintaxis"
        if "unknown column" in err_lower or "doesn't exist" in err_lower or "table" in err_lower and "exist" in err_lower:
            return "columna o tabla inexistente"
        if "group by" in err_lower or "aggregated" in err_lower or "sum" in err_lower or "count" in err_lower:
            return "agregacion"
        return "sintaxis"

    # Si corrio pero el resultado difiere:
    pred_upper = sql_pred.upper()
    ref_upper = sql_ref.upper()

    if ("JOIN" in ref_upper and "JOIN" not in pred_upper) or ("JOIN" not in ref_upper and "JOIN" in pred_upper):
        return "JOIN"
    if ("GROUP BY" in ref_upper and "GROUP BY" not in pred_upper) or ("HAVING" in ref_upper and "HAVING" not in pred_upper):
        return "agregacion"
    if ("WHERE" in ref_upper and "WHERE" not in pred_upper) or ("LIKE" in ref_upper and "LIKE" not in pred_upper):
        return "filtro"
    return "resultado_distinto"


def ejecutar_consulta(cur, sql: str, timeout_s=5):
    """Ejecuta una consulta SQL y retorna dict con ok, columnas, filas y error."""
    try:
        cur.execute(f"SET SESSION max_execution_time={timeout_s * 1000}")
        cur.execute(sql)
        filas = cur.fetchall()
        columnas = [d[0] for d in cur.description] if cur.description else []
        return {
            "ok": True,
            "columnas": columnas,
            "filas": list(filas)[:10],
            "filas_completas": list(filas),
            "error": None
        }
    except Exception as e:
        return {
            "ok": False,
            "columnas": [],
            "filas": [],
            "filas_completas": [],
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Evaluador EX de Text-to-SQL")
    parser.add_argument("--variante", choices=["baseline", "config_A", "config_B"], default="baseline")
    parser.add_argument("--autocorreccion", action="store_true", help="Usa callback ejecutar para autocorreccion")
    parser.add_argument("--preguntas", default="datos/validacion_propia.jsonl")
    parser.add_argument("--salida", default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--user", default="lector")
    parser.add_argument("--password", default="lector")
    parser.add_argument("--limite", type=int, default=None, help="Limite de preguntas a evaluar")
    args = parser.parse_args()

    # Configurar variable de entorno para solucion.py
    if args.variante == "baseline":
        cfg = {"usar_adapter": False}
    elif args.variante == "config_A":
        cfg = {"usar_adapter": True, "adapter": "checkpoints/config_A"}
    elif args.variante == "config_B":
        cfg = {"usar_adapter": True, "adapter": "checkpoints/config_B"}
    os.environ["SOLUCION_CFG"] = json.dumps(cfg)

    print(f"=== Evaluando variante: {args.variante} (autocorreccion={args.autocorreccion}) ===")
    
    # Cargar solucion.py
    inicio_carga = time.time()
    try:
        import solucion
    except Exception as e:
        print(f"ERROR al cargar solucion.py: {e}", file=sys.stderr)
        sys.exit(1)
    tiempo_carga = time.time() - inicio_carga
    print(f"Modelo cargado en {tiempo_carga:.2f} s")

    # Leer preguntas
    ruta_preguntas = ROOT / args.preguntas
    if not ruta_preguntas.exists():
        print(f"No existe el archivo de preguntas: {ruta_preguntas}", file=sys.stderr)
        sys.exit(1)

    preguntas = [json.loads(l) for l in open(ruta_preguntas, encoding="utf-8") if l.strip()]
    if args.limite:
        preguntas = preguntas[:args.limite]

    # Conectar a MySQL
    try:
        import pymysql
        conn = pymysql.connect(host=args.host, user=args.user, password=args.password,
                               charset="utf8mb4", autocommit=True)
        cur = conn.cursor()
    except Exception as e:
        print(f"No se pudo conectar a MySQL ({args.host}): {e}", file=sys.stderr)
        print("Asegurate de que MySQL 8.4 este corriendo y las bases va_* esten creadas.")
        sys.exit(1)

    resultados = []
    pesos_totales = {"total": 0, "facil": 0, "media": 0, "dificil": 0}
    pesos_acertados = {"total": 0, "facil": 0, "media": 0, "dificil": 0}
    conteo_errores = {}

    for idx, p in enumerate(preguntas, 1):
        db_id = p["db_id"]
        cur.execute(f"USE `{db_id}`")

        nivel = p.get("nivel", "media")
        peso = PESOS.get(nivel, 2)
        pesos_totales["total"] += peso
        pesos_totales[nivel] += peso

        # Callback opcional de ejecucion
        def callback_ejecutar(sql_candidato):
            return ejecutar_consulta(cur, sql_candidato)

        ejecutar_cb = callback_ejecutar if args.autocorreccion else None

        t0 = time.time()
        sql_pred = solucion.generar_sql(p["esquema"], p["pregunta"], ejecutar=ejecutar_cb)
        duracion = time.time() - t0

        # Ejecutar referencia
        res_ref = ejecutar_consulta(cur, p["sql"])
        # Ejecutar predicha
        res_pred = ejecutar_consulta(cur, sql_pred)

        orden_importa = "ORDER BY" in p["sql"].upper() or "orden" in p["pregunta"].lower()
        acierto = False
        categoria_err = None

        if res_pred["ok"] and res_ref["ok"]:
            acierto = comparar_resultados(res_ref["filas_completas"], res_pred["filas_completas"], orden_importa)
            if not acierto:
                categoria_err = clasificar_error(sql_pred, p["sql"], None)
        else:
            categoria_err = clasificar_error(sql_pred, p["sql"], res_pred.get("error"))

        if acierto:
            pesos_acertados["total"] += peso
            pesos_acertados[nivel] += peso
        else:
            conteo_errores[categoria_err] = conteo_errores.get(categoria_err, 0) + 1

        estado = "ACIERTO" if acierto else f"FALLO ({categoria_err})"
        print(f"[{idx:02d}/{len(preguntas):02d}] {p['id']} ({nivel}, peso {peso}): {estado} - {duracion:.2f}s")

        resultados.append({
            "id": p["id"],
            "db_id": db_id,
            "nivel": nivel,
            "peso": peso,
            "pregunta": p["pregunta"],
            "sql_ref": p["sql"],
            "sql_pred": sql_pred,
            "acierto": 1 if acierto else 0,
            "categoria_error": "" if acierto else categoria_err,
            "tiempo_segundos": round(duracion, 3)
        })

    conn.close()

    # Calcular EX
    ex_global = pesos_acertados["total"] / max(pesos_totales["total"], 1)
    ex_facil = pesos_acertados["facil"] / max(pesos_totales["facil"], 1)
    ex_media = pesos_acertados["media"] / max(pesos_totales["media"], 1)
    ex_dificil = pesos_acertados["dificil"] / max(pesos_totales["dificil"], 1)

    print("\n" + "=" * 50)
    print("RESUMEN DE EVALUACION")
    print("=" * 50)
    print(f"EX Ponderada Global: {ex_global:.4f} ({pesos_acertados['total']}/{pesos_totales['total']})")
    print(f"  - Facil   (peso 1): {ex_facil:.4f} ({pesos_acertados['facil']}/{pesos_totales['facil']})")
    print(f"  - Media   (peso 2): {ex_media:.4f} ({pesos_acertados['media']}/{pesos_totales['media']})")
    print(f"  - Dificil (peso 3): {ex_dificil:.4f} ({pesos_acertados['dificil']}/{pesos_totales['dificil']})")
    print(f"Distribucion de errores:")
    for cat, cnt in sorted(conteo_errores.items(), key=lambda x: x[1], reverse=True):
        print(f"  * {cat}: {cnt}")

    # Guardar CSV
    if not args.salida:
        sufijo_auto = "_auto" if args.autocorreccion else ""
        archivo_salida = ROOT / "resultados" / f"eval_{args.variante}{sufijo_auto}.csv"
        # Si es la corrida final de validacion propia requerida:
        if args.variante != "baseline" and not args.autocorreccion:
            archivo_oficial = ROOT / "resultados" / "validacion_propia.csv"
            with open(archivo_oficial, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
                w.writeheader()
                w.writerows(resultados)
            print(f"Guardado entregable oficial: {archivo_oficial}")
    else:
        archivo_salida = Path(args.salida)

    with open(archivo_salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
        w.writeheader()
        w.writerows(resultados)
    print(f"Guardado reporte detallado: {archivo_salida}")


if __name__ == "__main__":
    main()
