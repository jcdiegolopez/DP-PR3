"""Pick ~2,000 Spider pairs for training and split them into translation batches.

Quotas favour medium and hard queries (hard ones weigh 3x in the hidden
evaluation) and cap each database so no single schema dominates training.
"""
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRADA = ROOT / "datos" / "generados" / "spider_filtrado.jsonl"
SELECCION = ROOT / "datos" / "generados" / "spider_seleccion.jsonl"
LOTES = ROOT / "datos" / "generados" / "traduccion"

CUOTAS = {"dificil": 700, "media": 800, "facil": 500}
MAX_POR_DB = 40
TAM_LOTE = 100
SEMILLA = 2026


def main() -> None:
    pares = [json.loads(l) for l in open(ENTRADA, encoding="utf-8")]
    random.Random(SEMILLA).shuffle(pares)

    por_db = Counter()
    por_nivel = Counter()
    elegidos = []
    for p in pares:
        if por_nivel[p["nivel"]] >= CUOTAS[p["nivel"]] or por_db[p["db_id"]] >= MAX_POR_DB:
            continue
        elegidos.append(p)
        por_nivel[p["nivel"]] += 1
        por_db[p["db_id"]] += 1
    elegidos.sort(key=lambda p: p["id"])

    with open(SELECCION, "w", encoding="utf-8") as f:
        for p in elegidos:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Translation batches carry only what the translator needs, not the schema.
    LOTES.mkdir(parents=True, exist_ok=True)
    for n, ini in enumerate(range(0, len(elegidos), TAM_LOTE), 1):
        with open(LOTES / f"lote_{n:02d}_en.jsonl", "w", encoding="utf-8") as f:
            for p in elegidos[ini:ini + TAM_LOTE]:
                f.write(json.dumps({k: p[k] for k in ("id", "pregunta_en", "sql", "columnas")},
                                   ensure_ascii=False) + "\n")

    print(f"Elegidos: {len(elegidos)} de {len(pares)}  ({len(por_db)} bases)")
    print("Por nivel:", dict(por_nivel))
    print("Lotes:", (len(elegidos) + TAM_LOTE - 1) // TAM_LOTE)


if __name__ == "__main__":
    main()
