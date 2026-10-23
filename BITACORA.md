# Bitácora

## 2026-10-23 — G1LB3T0 (B, entrenamiento)
- Entorno: Python 3.11 en `.venv` (con `uv`), torch 2.11 + CUDA 12.8 (la RTX 5050 es Blackwell, sm_120), transformers 5.20, peft 0.21, TRL 1.16.
- Escribí `prompt.py` (único prompt para entrenamiento, baseline y `solucion.py`), `config.json`, `solucion.py`, `scripts/entrenar.py` y `notebooks/02_entrenamiento.ipynb`.
- `solucion.py`: fp16, decodificación greedy, semilla fija, límite de 25 s por pregunta con `max_time`, filtro que solo deja `SELECT` / `WITH ... SELECT` (bloquea `WITH ... DELETE`, `INTO OUTFILE`), autocorrección con el error de MySQL cuando hay `ejecutar`.
- Prueba temprana con 189 pares sintéticos (2 esquemas): el notebook corre de punta a punta, el adapter se guarda y `solucion.py` lo carga, la salida es SQL limpio y dos corridas dan exactamente lo mismo.
- Problema 1: la primera pregunta tardaba ~17 s (inicialización de kernels CUDA). Solución: generación de calentamiento al importar; ahora todas tardan 0.4–1.8 s y la carga ~28 s.
- Problema 2: en transformers 5, `apply_chat_template(tokenize=True)` devuelve un `BatchEncoding` y `len()` daba 2, así que el filtro por `max_length` no descartaba nada. Corregido.
- Prueba de memoria con ejemplos de ~1,900 tokens: batch 2×8 llega a 7.6 GiB de 7.9 → uso 1×16 (6.0 GiB, mismo batch efectivo). Rendimiento ~410 tokens/s: con ~3,500 pares de ~1,200 tokens serían ~5–6 h por config.
- Siguiente: entrenar A y B en cuanto esté `datos/entrenamiento.jsonl`; si la estimación del notebook pasa de ~5 h por config, entrenar en Kaggle (T4, fp16).

## 2026-10-23 — G1LB3T0 (B, entrenamiento) — hipótesis antes de entrenar
Un solo factor cambia entre configuraciones: `target_modules`. Todo lo demás igual (r=16, alpha=32, dropout=0.05, lr 2e-4 cosine, warmup 3 %, 2 épocas, batch efectivo 16, semilla 2026, mismo `max_length`).

| Config | `target_modules` | Parámetros entrenables | Hipótesis |
|---|---|---|---|
| A | `q_proj, k_proj, v_proj, o_proj` | 4.36 M (0.28 %) | Aprende el formato y el dialecto MySQL, pero mejora poco en preguntas difíciles. |
| B | A + `gate_proj, up_proj, down_proj` | 18.46 M (1.18 %) | Con ~4.2× más parámetros entrenables, mejora más en preguntas medias y difíciles. Costo esperado: ~20 % más de tiempo por paso. |

- Los conteos de parámetros salen de `print_trainable_parameters()` en la prueba temprana (no dependen de los datos).
- Predicción concreta para contrastar con la evaluación de C: B supera a A en EX ponderada por al menos 0.03, y la diferencia se concentra en nivel medio y difícil; en fácil quedan casi iguales.
