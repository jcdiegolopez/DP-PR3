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
