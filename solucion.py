"""Text-to-SQL entry point graded by the course evaluator.

Contract:
- The model is loaded when this module is imported (limit: 5 min).
- generar_sql(esquema, pregunta, ejecutar=None) -> str (limit: 30 s per question).
- Deterministic: greedy decoding and a fixed seed from config.json.
- Always returns exactly one SELECT or WITH ... SELECT statement.
- With "usar_adapter": false it runs the base model with the same prompt.
"""
import json
import os
import re
import time

# Must be set before CUDA is initialised so cuBLAS can run deterministically.
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from prompt import build_correction, build_messages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
    CFG = json.load(f)
# Our own evaluation only (baseline / config A / config B) without editing
# config.json, e.g. SOLUCION_CFG='{"usar_adapter": false}'. The grader does not set it.
CFG.update(json.loads(os.environ.get("SOLUCION_CFG", "{}")))

MAX_NEW_TOKENS = 320
MAX_INTENTOS = 3        # 1 generation + up to 2 corrections when ejecutar is given
TIEMPO_LIMITE = 25.0    # seconds, margin under the evaluator's 30
SQL_FALLBACK = "SELECT 1"

torch.manual_seed(CFG["semilla"])
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.use_deterministic_algorithms(True, warn_only=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# fp16, not bf16: the grading GPU is a T4, which has no bf16 support.
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

tokenizer = AutoTokenizer.from_pretrained(CFG["modelo_base"])
model = AutoModelForCausalLM.from_pretrained(CFG["modelo_base"], dtype=DTYPE)
if CFG["usar_adapter"]:
    from peft import PeftModel

    adapter_dir = os.path.join(BASE_DIR, CFG["adapter"])
    model = PeftModel.from_pretrained(model, adapter_dir)
    model = model.merge_and_unload()
model.to(DEVICE)
model.eval()

# Greedy decoding; clear the sampling defaults shipped with Qwen so
# generate() does not warn about unused temperature/top_p/top_k.
model.generation_config.do_sample = False
model.generation_config.temperature = None
model.generation_config.top_p = None
model.generation_config.top_k = None
model.generation_config.repetition_penalty = None

_INICIO_SQL = re.compile(r"\b(SELECT|WITH)\b", re.IGNORECASE)
# Only one statement survives _limpiar, so the remaining ways to write are
# WITH ... UPDATE/DELETE and SELECT ... INTO OUTFILE/@var.
_PROHIBIDO = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|RENAME)\b"
    r"|\bREPLACE\s+INTO\b|\bINTO\s+(OUTFILE|DUMPFILE|@)",
    re.IGNORECASE,
)
_LITERALES = re.compile(r"'(?:[^'\\]|\\.|'')*'|\"(?:[^\"\\]|\\.)*\"|`[^`]*`")
_TOKEN = re.compile(_LITERALES.pattern + r"|;|[^'\"`;]+|['\"`]")


def _generar(messages: list[dict], max_time: float | None = None) -> str:
    texto = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(texto, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            max_time=max_time,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )
    return tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def _es_solo_lectura(sql: str) -> bool:
    # Keywords inside string literals or `quoted` identifiers do not count.
    return not _PROHIBIDO.search(_LITERALES.sub("''", sql))


def _primera_sentencia(sql: str) -> str:
    """Cut at the first ';' that is not inside a string literal."""
    partes = []
    for tok in _TOKEN.findall(sql):
        if tok == ";":
            break
        partes.append(tok)
    return "".join(partes)


def _limpiar(texto: str) -> str:
    """Extract a single read-only SELECT / WITH ... SELECT from the model output."""
    texto = re.sub(r"```(?:sql|mysql)?", "\n", texto, flags=re.IGNORECASE)
    m = _INICIO_SQL.search(texto)
    if not m:
        return SQL_FALLBACK
    sql = texto[m.start():]
    sql = _primera_sentencia(sql)
    sql = re.split(r"\n\s*\n", sql)[0]  # drop any explanation after a blank line
    sql = sql.strip()
    if not _INICIO_SQL.match(sql) or not re.search(r"\bSELECT\b", sql, re.IGNORECASE):
        return SQL_FALLBACK
    if not _es_solo_lectura(sql):
        return SQL_FALLBACK
    return sql


def _restante(inicio: float) -> float:
    return TIEMPO_LIMITE - (time.time() - inicio)


# Warm-up: the first generate() pays ~15 s of CUDA kernel initialisation.
# Paying it here moves it into the 5 min load budget instead of question 1's 30 s.
_generar(build_messages("CREATE TABLE `t` (`a` int)", "¿Cuántas filas hay? Devuelve: cantidad"))


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    inicio = time.time()
    torch.manual_seed(CFG["semilla"])
    messages = build_messages(esquema, pregunta)
    sql = _limpiar(_generar(messages, max_time=_restante(inicio)))
    if ejecutar is None:
        return sql

    # Inference experiment: feed MySQL's error back to the model and retry.
    for _ in range(MAX_INTENTOS - 1):
        if _restante(inicio) < 3:
            break
        try:
            resultado = ejecutar(sql)
        except Exception as e:  # a broken callback must not cost us the answer
            resultado = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        if resultado.get("ok"):
            break
        messages = messages + build_correction(sql, str(resultado.get("error")))
        nuevo = _limpiar(_generar(messages, max_time=_restante(inicio)))
        if nuevo == SQL_FALLBACK:
            break
        sql = nuevo
    return sql
