"""Translate the selected Spider questions to Spanish with opus-mt-en-es.

Quoted values ('Treasury', "Fail", emails) are swapped for placeholders before
translating and restored afterwards, so the question still matches the SQL.
Questions already translated by hand (lote_01_es.jsonl) are kept as they are.
The "Devuelve:" part is built from the real column names, not translated.
"""
import json
import re
import sys
from pathlib import Path

from transformers import MarianMTModel, MarianTokenizer

ROOT = Path(__file__).resolve().parent.parent
SELECCION = ROOT / "datos" / "generados" / "spider_seleccion.jsonl"
MANUAL = ROOT / "datos" / "generados" / "traduccion" / "lote_01_es.jsonl"
SALIDA = ROOT / "datos" / "generados" / "spider_es.jsonl"
MODELO = "Helsinki-NLP/opus-mt-en-es"
TAM_LOTE = 16

LITERAL = re.compile(r"""'[^']*'|"[^"]*"|\S+@\S+""")

# opus-mt answers in the formal register; the project uses the informal one.
IMPERATIVOS = {
    "Liste": "Lista", "Encuentre": "Encuentra", "Muestre": "Muestra",
    "Mostrar": "Muestra", "Dé": "Da", "Devuelva": "Devuelve", "Cuente": "Cuenta",
    "Indique": "Indica", "Seleccione": "Selecciona", "Enumere": "Enumera",
    "Busque": "Busca", "Proporcione": "Proporciona", "Calcule": "Calcula",
    "Ordene": "Ordena", "Obtenga": "Obtén", "Averigüe": "Averigua",
    "Dígame": "Dime", "Cuéntame": "Cuenta", "Recupere": "Recupera",
    # Infinitives: the model sometimes translates "List ..." as "Listar ...".
    "Listar": "Lista", "Encontrar": "Encuentra", "Contar": "Cuenta",
    "Enumerar": "Enumera", "Dar": "Da", "Seleccionar": "Selecciona",
    "Obtener": "Obtén", "Mostrar": "Muestra", "Informe": "Informa",
    "Devolver": "Devuelve", "Buscar": "Busca", "Calcular": "Calcula",
    "Indicar": "Indica", "Ordenar": "Ordena", "Averiguar": "Averigua",
}
VOCABULARIO = [
    (re.compile(r"\bidentificaciones\b", re.I), "ids"),
    (re.compile(r"\bidentificadores\b", re.I), "ids"),
    (re.compile(r"\b(?:identificación|identificador)\b", re.I), "id"),
]
AGREGADOS = {"COUNT": "cantidad", "AVG": "promedio", "MAX": "máximo",
             "MIN": "mínimo", "SUM": "suma"}
AGREGADO_RE = re.compile(r"^(COUNT|AVG|MAX|MIN|SUM)\((DISTINCT\s+)?(.*)\)$", re.I)


def proteger(texto):
    literales = []

    def sub(m):
        literales.append(m.group(0).strip("'\""))
        return f"«{len(literales) - 1}»"

    return LITERAL.sub(sub, texto), literales


def restaurar(texto, literales):
    for i, lit in enumerate(literales):
        texto = re.sub(rf"«\s*{i}\s*»", f"'{lit}'", texto)
    return texto


def pulir(texto):
    primera, _, resto = texto.partition(" ")
    texto = (IMPERATIVOS.get(primera, primera) + (" " + resto if resto else ""))
    for patron, reemplazo in VOCABULARIO:
        texto = patron.sub(reemplazo, texto)
    return texto.strip()


def nombre_columna(col: str) -> str:
    col = col.replace("`", "")
    m = AGREGADO_RE.match(col)
    if m:
        funcion, _, interior = m.groups()
        interior = re.sub(r"^T\d+\.", "", interior.strip())
        if interior == "*":
            return "cantidad"
        return f"{AGREGADOS[funcion.upper()]} de {interior}"
    return re.sub(r"^T\d+\.", "", col)


def devuelve(columnas) -> str:
    vistos, nombres = set(), []
    for c in columnas:
        n = nombre_columna(c)
        if n not in vistos:
            vistos.add(n)
            nombres.append(n)
    return "Devuelve: " + ", ".join(nombres)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    pares = [json.loads(l) for l in open(SELECCION, encoding="utf-8")]
    manual = {}
    if MANUAL.exists():
        manual = {j["id"]: j["pregunta"] for j in map(json.loads, open(MANUAL, encoding="utf-8"))}

    pendientes = [p for p in pares if p["id"] not in manual]
    protegidos = {p["id"]: proteger(p["pregunta_en"]) for p in pendientes}
    # Sorting by length keeps each batch homogeneous, so padding wastes little.
    orden = sorted(pendientes, key=lambda p: len(protegidos[p["id"]][0]))

    tok = MarianTokenizer.from_pretrained(MODELO)
    model = MarianMTModel.from_pretrained(MODELO).eval()
    traducidas = {}
    for i in range(0, len(orden), TAM_LOTE):
        trozo = orden[i:i + TAM_LOTE]
        batch = tok([protegidos[p["id"]][0] for p in trozo], return_tensors="pt", padding=True)
        out = model.generate(**batch, num_beams=4, max_length=160)
        for p, s in zip(trozo, tok.batch_decode(out, skip_special_tokens=True)):
            traducidas[p["id"]] = pulir(restaurar(s, protegidos[p["id"]][1]))
        if (i // TAM_LOTE) % 25 == 0:
            print(f"  {min(i + TAM_LOTE, len(orden))}/{len(orden)}")

    perdidos = 0
    with open(SALIDA, "w", encoding="utf-8") as f:
        for p in pares:
            if p["id"] in manual:
                pregunta, origen = manual[p["id"]], "manual"
            else:
                pregunta, origen = f"{traducidas[p['id']]} {devuelve(p['columnas'])}", "mt"
                lits = protegidos[p["id"]][1]
                if any(f"'{l}'" not in pregunta for l in lits):
                    perdidos += 1
            f.write(json.dumps({
                "id": p["id"], "db_id": p["db_id"], "fuente": "spider", "nivel": p["nivel"],
                "esquema": p["esquema"], "pregunta": pregunta, "sql": p["sql"],
                "traduccion": origen,
            }, ensure_ascii=False) + "\n")
    print(f"Total: {len(pares)}  manual: {len(manual)}  mt: {len(pendientes)}")
    print(f"Frases con algun literal perdido: {perdidos}")


if __name__ == "__main__":
    main()
