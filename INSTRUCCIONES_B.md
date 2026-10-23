# Persona B — cómo terminar (entrenamiento)

Estado al **2026-10-23**: el código de B ya está en el repo y probado. Falta todo lo que depende de entrenar con el dataset real.

## Ya hecho

| Entregable | Archivo | Estado |
|---|---|---|
| Prompt único | `prompt.py` | listo |
| Contrato del profe | `solucion.py`, `config.json` | listo y probado (determinista, < 2 s por pregunta, filtro de solo-lectura, autocorrección) |
| Script de entrenamiento | `scripts/entrenar.py` | listo, probado con datos sintéticos |
| Notebook de entrenamiento | `notebooks/02_entrenamiento.ipynb` | listo, **sin ejecutar con datos reales** |
| Prueba en Colab | `notebooks/colab_prueba_t4.ipynb` | escrito, **sin ejecutar** |
| Dependencias | `requirements.txt` (provisional), `requirements-entrenamiento.txt` | falta fijar versiones con Colab |
| Hipótesis A/B | `BITACORA.md` | registrada antes de entrenar |

## Falta

1. Entrenar config A y config B con `datos/entrenamiento.jsonl` (paso 2).
2. Subir curvas, métricas y el notebook ejecutado (paso 3).
3. Pasarle los dos adapters a C, que elige el mejor por EX (paso 4).
4. Copiar el mejor a `adapter/` y subirlo (paso 5).
5. Prueba en Colab T4 limpio y fijar `requirements.txt` (paso 6).
6. Entradas en `BITACORA.md` y filas en `CONTRIBUCIONES.md` (paso 7).

---

## 1. Preparar el PC (solo si es otro PC)

Necesitas Git, Python 3.11 y drivers NVIDIA recientes.

```powershell
git clone https://github.com/jcdiegolopez/DP-PR3.git
cd DP-PR3
py -3.11 -m venv .venv
.venv\Scripts\activate
# CUDA 12.8: necesario en GPUs serie 50 (Blackwell), también funciona en las demás NVIDIA
pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements-entrenamiento.txt
python -m ipykernel install --user --name dp-pr3 --display-name "DP-PR3 (.venv 3.11)"
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Si no tienes Python 3.11: `pip install uv` y luego `python -m uv venv .venv --python 3.11` (descarga 3.11 solo).

El modelo base (`Qwen/Qwen2.5-Coder-1.5B-Instruct`, ~3 GB) se descarga solo la primera vez.

## 2. Entrenar A y B

Datos (de Diego): `datos/entrenamiento.jsonl` (2,403 pares) y `datos/eval_loss.jsonl` (142 pares de 8 bases de Spider que no están en train; solo para la curva de loss).

### Opción recomendada: el notebook

Abrir `notebooks/02_entrenamiento.ipynb` con el kernel **DP-PR3 (.venv 3.11)** y ejecutar todo. Hace, en orden:

1. Mide largos en tokens y fija `MAX_LENGTH` = p99 redondeado a 128 (con los datos actuales: p99 = 2,610 → **2,688**).
2. Imprime la **estimación de horas**. Con la RTX 5050 (8 GB, ~410 tokens/s) da ~3.3 h por config → **~7 h en total**.
3. Entrena A, luego B (cada una en un subproceso para liberar la GPU).
4. Tabla comparativa, curva conjunta y unos ejemplos generados con cada adapter.

Parámetros en la primera celda. Defaults pensados para una GPU de 8 GB:

| Parámetro | Valor | Cuándo cambiarlo |
|---|---|---|
| `BATCH, ACCUM` | `1, 16` | GPU ≥ 12 GB: `2, 8` (más rápido) |
| `FP16` | `False` (usa bf16) | `True` si entrenas en T4 (Kaggle/Colab) |
| `TOKENS_POR_SEG` | `410` | solo afecta la estimación; ajústalo a tu GPU |
| `LIMITE` | `None` | `200` para una prueba rápida (~5 min) |

No apagar ni suspender el PC durante el entrenamiento (en Windows: Configuración → Energía → Suspender = Nunca).

### Alternativa: por consola (si el notebook se cuelga o quieres dejarlo corriendo)

```powershell
.venv\Scripts\activate
$env:PYTHONIOENCODING = "utf-8"
python scripts/entrenar.py --config A --max-length 2688 *> resultados/log_A.txt
python scripts/entrenar.py --config B --max-length 2688 *> resultados/log_B.txt
```

Luego ejecutar el notebook solo desde la sección 7 (comparación) para generar la curva conjunta, o volver a correrlo completo con datos ya entrenados si hay tiempo.

### Si pasa de ~5 h por config o se queda sin memoria

- **Sin memoria (CUDA OOM):** bajar `MAX_LENGTH` a 2,048 (se pierde ~5 % de pares, los más largos) y avisar a Diego.
- **Muy lento:** Kaggle (GPU T4 gratis, 30 h/semana). Subir el repo como dataset o clonarlo, `pip install -r requirements-entrenamiento.txt` (torch ya viene), y correr con `FP16 = True`, `BATCH, ACCUM = 2, 8`. Descargar `checkpoints/config_A` y `config_B` al terminar.

### Qué produce

| Archivo | En git | Qué es |
|---|---|---|
| `checkpoints/config_A/`, `checkpoints/config_B/` | **no** (están en `.gitignore`) | adapters entrenados |
| `resultados/entrenamiento_config_A.json` / `_B.json` | sí | parámetros entrenables, tiempo, loss final, tokens/s, memoria |
| `resultados/log_config_A.json` / `_B.json` | sí | historial completo de loss |
| `resultados/curvas_loss_A.png` / `_B.png` / `_AB.png` | sí | curvas de loss (entregable) |

## 3. Subir resultados del entrenamiento

```powershell
git add resultados/ notebooks/02_entrenamiento.ipynb
git commit -m "Entrenar configs LoRA A y B: curvas, tiempos y parámetros"
git push
```

Antes de commitear el notebook, revisar que no tenga salidas gigantes (no debería: oculta las barras de progreso).

## 4. Pasar los adapters a C

`checkpoints/` no está en git. Opciones:

- **C evalúa en tu PC:** `SOLUCION_CFG` permite cambiar de variante sin editar `config.json`:

  ```powershell
  $env:SOLUCION_CFG = '{"usar_adapter": false}'                                  # baseline
  $env:SOLUCION_CFG = '{"usar_adapter": true, "adapter": "checkpoints/config_A"}' # config A
  $env:SOLUCION_CFG = '{"usar_adapter": true, "adapter": "checkpoints/config_B"}' # config B
  ```

- **C evalúa en su PC:** comprimir `checkpoints/config_A` y `checkpoints/config_B` (solo hacen falta `adapter_config.json` y `adapter_model.safetensors`: ~17 MB la A y ~74 MB la B, se guardan en fp32) y mandárselos por Drive.

Ojo: mientras no exista `adapter/`, `import solucion` con `config.json` tal cual **falla** (pide el adapter). Para el baseline usar `SOLUCION_CFG='{"usar_adapter": false}'`.

## 5. Adapter final

Cuando C diga cuál config tiene mayor **EX ponderada** en la validación propia:

1. En la última celda del notebook: `MEJOR = "A"` o `"B"` y ejecutarla (copia los dos archivos a `adapter/`).
2. Verificar tamaño (< 100 MB, límite de GitHub; la B pesa ~74 MB, cabe) y que cargue:

   ```powershell
   python -c "import solucion; print(solucion.generar_sql('CREATE TABLE t (a int)', 'Cuántas filas hay? Devuelve: cantidad'))"
   ```

3. Subirlo:

   ```powershell
   git add adapter/
   git commit -m "Agregar adapter final (config X)"
   git push
   ```

Si C no llega a tiempo: elegir por menor `loss_eval_final` y anotarlo en la bitácora como criterio provisional.

## 6. Prueba final en Colab T4 (domingo, antes de entregar)

Solo hay **una** corrección en 24 h y cuesta −10: esta prueba es obligatoria.

1. `adapter/` y `datos/validacion_propia.jsonl` (de C) tienen que estar ya en GitHub.
2. Colab → Subir notebook → `notebooks/colab_prueba_t4.ipynb` → Entorno de ejecución → **GPU T4**.
3. Si el PDF del proyecto da otro enlace del binario de MySQL 8.4.10, reemplazar `MYSQL_URL` en la celda de MySQL.
4. Los `.sql` de `datos/esquemas/validacion/` (de C) deben crear su base y sus datos; si no, la celda de carga hay que adaptarla.
5. Ejecutar todo. Debe confirmar:
   - carga < 5 min,
   - cada pregunta < 30 s, sin y con autocorrección,
   - dos corridas idénticas,
   - `usar_adapter: false` funciona.
6. Copiar las versiones de la última celda (`pip freeze`) a `requirements.txt`, quitar la línea `PROVISIONAL`, commit y push.

## 7. Documentación de B

**`BITACORA.md`**: agregar al menos dos entradas con fecha y autor:

- Entrenamiento: tiempos reales, parámetros, loss final de A y B, problemas (memoria, velocidad).
- Resultado vs hipótesis: con la EX de C, ¿se cumplió que B supera a A por ≥ 0.03 y sobre todo en medio y difícil?
- (Opcional) Prueba en Colab: tiempos medidos y versiones.

**`CONTRIBUCIONES.md`**: filas de B con evidencia (enlaces a commit o archivo):
`prompt.py`, `solucion.py`, `config.json`, `requirements.txt`, `scripts/entrenar.py`, `notebooks/02_entrenamiento.ipynb`, `resultados/curvas_loss_*.png`, `adapter/`, prueba en Colab.

**Presentación** (diapositivas 7 y 8): tabla A vs B (parámetros, tiempo, loss) y `resultados/curvas_loss_AB.png`.

## Checklist de B antes de entregar

- [ ] `resultados/entrenamiento_config_A.json` y `_B.json` en git
- [ ] `resultados/curvas_loss_A.png`, `_B.png`, `_AB.png` en git
- [ ] `notebooks/02_entrenamiento.ipynb` ejecutado con datos reales en git
- [ ] `adapter/` con la mejor config en git, < 100 MB
- [ ] `config.json` con `"usar_adapter": true` y `"adapter": "adapter/"`
- [ ] Colab T4: carga < 5 min, < 30 s por pregunta, determinista, baseline funciona
- [ ] `requirements.txt` con versiones de Colab (sin `PROVISIONAL`)
- [ ] Entradas de B en `BITACORA.md` y filas en `CONTRIBUCIONES.md`
- [ ] Commits desde tu propia cuenta

## Nota para Diego (datos)

En algunos pares de Spider, `Devuelve:` usa nombres en español pero el SQL no pone alias (p. ej. `Devuelve: año de creación, nombre, presupuesto` con `SELECT creation, name, budget_in_billions`). El evaluador empareja columnas por valores, así que no baja la EX, pero el modelo aprende a ignorar los nombres de `Devuelve:`. No es urgente.
