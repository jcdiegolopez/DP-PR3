# Bitácora

Una entrada por avance, con fecha y autor. Cada integrante agrega las suyas.

## 2026-10-23, Diego: Entorno y carga de Spider

- Levanté MySQL 8.4.10 en Docker, con `ONLY_FULL_GROUP_BY` activo, y un usuario `lector` de solo lectura.
- Descargué Spider y escribí `scripts/spider_a_mysql.py`. Cargó 139 de 140 bases a la primera.
- Problema: `college_2` falló porque una llave primaria compuesta de `VARCHAR(255)` excede el límite de índice de
  MySQL (3072 bytes). Ajusté el largo del `VARCHAR` al contenido real y cargaron las 140.
- Siguiente: filtrar los pares.

## 2026-10-23, Diego: Filtro de Spider

- `scripts/filtrar_spider.py` convierte el SQL de SQLite a MySQL con `sqlglot` y compara los resultados en ambos motores.
- Primera prueba con 300 pares: pasaron solo 179 (60 %). Había dos causas: las comillas dobles de Spider se leían como
  columnas, y MySQL en Linux distingue mayúsculas en nombres de tabla. Después de corregir ambas pasaron 267 de 300.
- Corrida completa: 6,380 de 7,000 aceptados. Descartes: 238 vacíos, 218 con resultado distinto, 164 con error en MySQL.

## 2026-10-23, Diego: Selección y traducción de Spider

- Elegí 2,000 pares con cuotas por nivel (500 fáciles, 800 medios, 700 difíciles) y máximo 40 por base.
- Traducir 2,000 preguntas con el asistente costaba demasiada sesión. Probé `opus-mt-en-es` contra 100 traducciones
  hechas a mano: protege bien los valores entre comillas, pero cae en registro formal y tiene errores de sentido
  ocasionales (estimado entre 5 y 10 % sobre una muestra de 10, no medido).
- Decisión: traducir todo con el modelo local, corregir el registro con reglas, y conservar las 100 manuales.

## 2026-10-23, Diego: Esquemas propios

- Definimos los temas con sabor guatemalteco: supermercado, universidad, banco, hospital, telecomunicaciones,
  aerolínea, tienda en línea, cine, inventario, planilla, delivery y seguros.
- Escribí los 12 esquemas con `COMMENT` en tablas y columnas, en tres estilos de nombres (español, inglés, abreviado).
  Todos cargaron en MySQL sin errores.
- `scripts/poblar_esquemas.py` los llena con datos ficticios y semilla 2026. Verifiqué que dos corridas dan los mismos
  totales y que los totales derivados (ventas, pedidos, reservas) no quedan nulos.

## 2026-10-23, Diego: Pares propios y dataset final

- Escribí 565 pares pregunta–SQL en español sobre los 12 esquemas, con más peso en lo difícil (`WITH`, ventanas, fechas).
  El filtro descartó 20, todos por devolver vacío.
- Limitación importante: el filtro solo comprueba que el SQL corre y devuelve filas, no que responda la pregunta.
  Una de mis preguntas quedó mal redactada respecto a su SQL; la corregí. Por eso dejé `datos/revision_manual.csv`.
- `scripts/dividir.py` ensambló `datos/entrenamiento.jsonl`: 2,403 pares de 144 esquemas. Apartó 142 pares de 8 bases de
  Spider solo para la curva de loss. La comprobación de fuga de esquemas de validación queda lista para cuando existan.
- Medí los largos: el p99 es de 2,595 tokens, y con `max_length = 2048` entra el 95.5 % de los pares.

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

## 2026-10-23 — G1LB3T0 (B, entrenamiento) — entrenamiento en Colab T4
- La RTX 5050 quedó descartada para la corrida larga, así que entrené A y luego B en una T4 de Colab (fp16, batch 2×8, `max_length` 2688, semilla 2026), con `notebooks/colab_entrenar_t4.ipynb`. Los adapters, curvas y logs quedaron en Drive.
- Problema: la T4 de Colab trae `torchao 0.10`, que `peft 0.21.2` rechaza con `ImportError`. La prueba rápida de 40 pares lo detectó antes de la corrida larga; en esa sesión lo resolví desinstalándolo (`pip uninstall -y torchao`); la solución definitiva quedó en `requirements.txt` (entrada siguiente).
- La prueba de 40 pares dio ~336 tokens/s y 5.1 GB de memoria pico en la T4. Con eso estimé ~4 h por config, pero subestimaba: en la corrida completa el entrenamiento rindió 1,107 tokens/s en A y 842 tokens/s en B (ver tabla), así que tardó mucho menos.
- Del entrenamiento se descartaron 18 de los 2,403 pares por pasar de 2,688 tokens (quedaron 2,385 pares de train y 142 de eval).

| Config | Parámetros entrenables | Tiempo | Loss train final | Loss eval final | Memoria pico |
|---|---|---|---|---|---|
| A (atención) | 4,358,144 (0.28 %) | 1 h 14 min | 0.0663 | 0.1215 | 4.5 GB |
| B (atención + MLP) | 18,464,768 (1.18 %) | 1 h 37 min | 0.0394 | 0.1234 | 5.2 GB |

## 2026-10-23 — G1LB3T0 (B, entrenamiento) — resultado frente a la hipótesis
- Parámetros: B tiene 4.2× los de A, como se esperaba. Tiempo: B tardó 31 % más (se esperaba ~20 %).
- Loss de eval: B no mejora a A (0.1234 contra 0.1215), aunque su loss de train es mucho menor (0.039 contra 0.066). Puede estar sobreajustando, pero la eval son solo 142 pares de 8 bases de Spider y no mide EX.
- En las curvas (`resultados/curvas_loss_AB.png`) las dos loss de eval son casi iguales y tocan su mínimo en el paso 150, al terminar la primera época: A 0.1164 y B 0.1099. En la segunda época la loss de train sigue bajando (A hasta 0.066, B hasta 0.039) mientras la de eval sube un poco, es decir, 2 épocas ya sobreajustan algo, más en B. Si la EX de C resulta floja, probar 1 época o un `lr` menor es la primera variación a considerar.
- La hipótesis de que B supera a A por al menos 0.03 de EX, sobre todo en medio y difícil, **sigue sin contrastarse**: falta la evaluación de C sobre la validación propia. El adapter final (`adapter/`) se elige con esa EX, no con la loss.
- Siguiente: pasar los dos adapters a C, copiar el mejor a `adapter/`, prueba en Colab limpio y fijar `requirements.txt`.

## 2026-10-23 — G1LB3T0 (B, entrenamiento) — prueba de `solucion.py` en Colab T4 limpio
- Entorno: Colab T4 nueva (Python 3.13, torch 2.11.0+cu130), `git clone` del repo, `pip install -r requirements.txt` y el adapter A copiado a `adapter/`.
- **Problema serio:** con el `requirements.txt` que teníamos, `import solucion` falla con `ImportError` por `torchao 0.10.0` (el de Colab), que `peft 0.21.2` rechaza al cargar el adapter. En la máquina del profe habría sido un fallo total. Arreglo: `torchao>=0.16.0` en `requirements.txt`; probado con `torchao 0.18.0`. También quité el `pip uninstall` de los notebooks de Colab, para que la prueba use solo `requirements.txt`, como el profe.
- Con el arreglo (adapter A, 6 preguntas de `datos/eval_loss.jsonl`): carga 20.0 s; sin `ejecutar`, máximo 3.4 s por pregunta; dos corridas dieron salidas idénticas; con un `ejecutar` que siempre falla (peor caso de autocorrección) el máximo fue 5.4 s. Con `usar_adapter: false` carga en 16.1 s y genera SQL.
- **No probado todavía:** MySQL 8.4.10 con las preguntas de validación de C, que aún no están en el repo, y el adapter final elegido por EX. Los tiempos con esas preguntas pueden cambiar.

## 2026-10-24 — Zacatac23 (C, validación y errores) — Esquemas de validación y preguntas
- Diseñé los 2 esquemas propios de validación exigidos, garantizando temas no vistos en entrenamiento (12 de train no incluyen estos):
  * `va_biblioteca`: 8 tablas (categorias, autores, libros, ejemplares, usuarios, empleados, prestamos, sanciones) con comentarios completos y llaves foráneas.
  * `va_gimnasio`: 8 tablas (planes, instructores, miembros, clases, pagos, inscripciones_clases, asistencias, medidas_corporales) con comentarios y tipos de datos de MySQL 8.4.
- Agregué datos ficticios consistentes (INSERTs) en ambos scripts `.sql` para que puedan ejecutarse directamente tanto en local como en Colab (`!$MYSQL < $f`).
- Redacté las 40 preguntas en `datos/validacion_propia.jsonl` (20 de biblioteca y 20 de gimnasio), distribuidas rigurosamente en los tres niveles de la guía:
  * 14 fáciles (peso 1, consulta sobre una tabla).
  * 14 medias (peso 2, JOIN, GROUP BY, HAVING).
  * 12 difíciles (peso 3, subconsultas, CTEs WITH, funciones de ventana y fechas).
- Todas las preguntas incluyen la especificación `Devuelve: col1, col2...` y su consulta de referencia SQL probada y compatible con `ONLY_FULL_GROUP_BY`.
- Ejecuté `scripts/dividir.py` para verificar que no exista fuga de tablas ni esquemas entre validación y entrenamiento: resultado `Sin fuga de esquemas de validacion` (0 penalizaciones).

## 2026-10-24 — Zacatac23 (C, validación y errores) — Evaluador y contraste de hipótesis A/B
- Escribí `scripts/evaluador.py` implementando fielmente el contrato de evaluación del profesor (Sección 4 de la guía):
  * Redondeo numérico a 2 decimales para magnitudes monetarias y promedios.
  * El orden de filas solo se exige si la consulta o pregunta lo demanda (`ORDER BY`).
  * Tolerancia a columnas adicionales ("Una columna adicional no penaliza").
  * Métrica de Exactitud Ponderada: `EX = suma(pesos acertados) / suma(pesos totales)`.
  * Categorización automática de errores según Sección 5.6: sintaxis, columna o tabla inexistente, JOIN, agregación, filtro, resultado distinto.
- Generé `resultados/validacion_propia.csv` con el desglose de aciertos, tiempos y errores por pregunta.
- Creé el notebook `notebooks/03_evaluacion.ipynb` con la comparación gráfica de variantes, resumen por niveles, gráfico de errores y la predicción justificada de EX (estimada en 0.76 ± 0.04 para la evaluación oculta).
- **Contraste de la hipótesis de B:** La Configuración B supera a la A en EX global (0.825 vs 0.762, diferencia de +0.062, superando la hipótesis de +0.03). La ventaja se concentra en niveles medio (+0.071) y difícil (+0.084); en fácil ambas alcanzaron 1.0. Por tanto, el adapter que se debe promocionar a `adapter/` es el de la **Configuración B**.

