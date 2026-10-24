# Persona C: cómo usar lo que dejó B (validación y errores)

Estado al **2026-10-23**: B entrenó las dos configuraciones de LoRA (A y B) y dejó `solucion.py` listo. Lo que falta para elegir el adapter final depende de tu evaluación.

## Qué te toca

1. 2 esquemas de validación y 40 preguntas (`datos/esquemas/validacion/`, `datos/validacion_propia.jsonl`).
2. `scripts/evaluador.py` con las reglas del profe (guía, sección 4.3).
3. Correr las cinco variantes de la guía (sección 4.4) y devolverle a B la **EX ponderada global y por nivel** de A y de B.
4. Análisis de errores, predicción de EX y presentación.

## Empieza ya, sin esperar los adapters

Casi todo lo tuyo no depende del entrenamiento:

- **Hoy:** esquemas de validación, las 40 preguntas, `evaluador.py` y poblar las bases (guía, 4.1 a 4.3). Los temas tienen que ser distintos de los 12 esquemas de `datos/esquemas/entrenamiento/` (hospital, universidad, banco, supermercado, telecom, aerolínea, tienda en línea, cine, inventario, planilla, delivery y seguros).
- **Baseline:** ya se puede correr con `solucion.py` y `{"usar_adapter": false}` (ver más abajo). No necesita adapter.
- **Cuando B te pase los adapters:** correr A, B y las variantes con autocorrección.

Haz `git pull` antes de empezar: `requirements.txt` y `solucion.py` ya están corregidos para Colab T4.

Con tu EX, B elige cuál adapter va a `adapter/`. Si no hay EX a tiempo, B elige por la loss de eval (A: 0.1215, B: 0.1234) y lo anota en la bitácora.

## Lo que ya está en el repo

| Archivo | Para qué |
|---|---|
| `prompt.py` | El único prompt (entrenamiento, baseline y `solucion.py`). No lo cambies. |
| `solucion.py` | `generar_sql(esquema, pregunta, ejecutar=None) -> str`. Carga el modelo al importarlo. |
| `config.json` | Modelo base, adapter, `usar_adapter`, semilla. |
| `resultados/` | Métricas, logs y curvas de loss de A y B. |

El formato de `datos/validacion_propia.jsonl` está en la guía, sección 1.5. El esquema siempre sale de `SHOW CREATE TABLE`, nunca escrito a mano.

## Los adapters (no están en git)

Pídele a B la carpeta de Drive con `config_A/` y `config_B/`. De cada una solo hacen falta dos archivos:
`adapter_config.json` y `adapter_model.safetensors` (~17 MB la A y ~74 MB la B).
Déjalos en `checkpoints/config_A/` y `checkpoints/config_B/` (esa carpeta está en `.gitignore`).

## Elegir la variante sin editar `config.json`

La variable de entorno `SOLUCION_CFG` pisa las claves de `config.json` (el evaluador del profe no la usa).

```powershell
# Baseline (sin adapter, mismo prompt)
$env:SOLUCION_CFG = '{"usar_adapter": false}'
# Config A
$env:SOLUCION_CFG = '{"usar_adapter": true, "adapter": "checkpoints/config_A"}'
# Config B
$env:SOLUCION_CFG = '{"usar_adapter": true, "adapter": "checkpoints/config_B"}'
```

En bash: `SOLUCION_CFG='{"usar_adapter": false}' python tu_script.py`.

Luego, en Python: `import solucion` (carga el modelo, ~30 s en una RTX y menos de 5 min en la T4) y `solucion.generar_sql(esquema, pregunta)`.

## Autocorrección (experimento de inferencia)

Si pasas `ejecutar`, `solucion.py` reintenta hasta 2 veces con el error de MySQL. `ejecutar(sql)` debe devolver:

```python
{"ok": bool, "columnas": [...], "filas": [...],  # máx. 10 filas
 "error": None | "mensaje de MySQL"}
```

Sin `ejecutar`, genera una sola vez. Corre cada variante con y sin `ejecutar`, como pide la guía.

## Requisitos de máquina

- Hace falta GPU NVIDIA para que sea rápido. Sin GPU corre en CPU, pero lento.
- El modelo pesa ~3 GB en fp16, así que una GPU de 4 GB debería alcanzar para generar (no se ha probado en 4 GB).
- En Colab T4: basta `pip install -r requirements.txt`. Ya incluye un `torchao` nuevo, porque el que trae Colab es viejo y `peft` lo rechaza con `ImportError`. Verificado en una T4 limpia.
- Dos corridas con la misma configuración deben dar la misma salida (es determinista). Si no, avísale a B.

## Qué devolverle a B

- EX ponderada global de baseline, A, B, y las dos con autocorrección.
- EX por nivel (fácil, media, difícil) de A y de B. La hipótesis de B es que B supera a A por al menos 0.03 y sobre todo en media y difícil.
- Tu `resultados/validacion_propia.csv` y `datos/validacion_propia.jsonl` ya en GitHub, para que B haga la prueba final en un Colab limpio.
