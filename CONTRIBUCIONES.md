# Contribuciones

| Área | Tarea | Responsable | Evidencia | Estado |
|---|---|---|---|---|
| Datos | Cargar Spider en MySQL 8.4.10 | Diego | `scripts/spider_a_mysql.py`, `datos/esquemas/spider_carga.csv` | Hecho |
| Datos | Filtrar y convertir pares de Spider | Diego | `scripts/filtrar_spider.py`, `datos/descartes.csv` | Hecho |
| Datos | Traducir preguntas al español | Diego | `scripts/traducir_spider.py`, `datos/generados/spider_es.jsonl` | Hecho |
| Datos | 12 esquemas propios y su población | Diego | `datos/esquemas/entrenamiento/`, `scripts/poblar_esquemas.py` | Hecho |
| Datos | Pares propios y filtro | Diego | `datos/generados/propios/`, `scripts/filtrar_propios.py` | Hecho |
| Datos | Dataset final y verificación de fuga | Diego | `scripts/dividir.py`, `datos/entrenamiento.jsonl`, `notebooks/01_datos.ipynb` | Hecho |
| Entrenamiento | Prompt, `solucion.py`, `config.json`, `requirements.txt` | B (G1LB3T0) | `prompt.py`, `solucion.py`, `config.json`, `requirements.txt` (commit `5ffb891`) | Hecho (`requirements.txt` provisional hasta la prueba en Colab) |
| Entrenamiento | Dos configuraciones de LoRA, curvas de loss, `adapter/` | B (G1LB3T0) | `scripts/entrenar.py`, `notebooks/02_entrenamiento.ipynb`, `notebooks/colab_entrenar_t4.ipynb`, `resultados/` (A y B entrenadas; `adapter/` pendiente de la EX de C) | En curso |
| Entrenamiento | Prueba en Colab T4 | B (G1LB3T0) | `notebooks/colab_prueba_t4.ipynb`, `requirements.txt` (carga, tiempos, determinismo y baseline probados en T4 limpia con el adapter A; falta MySQL y las preguntas de C) | Parcial |
| Validación y errores | 2 esquemas de validación y 40 preguntas | C (Zacatac23) | `datos/esquemas/validacion/`, `datos/validacion_propia.jsonl` | Hecho |
| Validación y errores | Evaluador, baseline y experimento de inferencia | C (Zacatac23) | `scripts/evaluador.py`, `resultados/validacion_propia.csv` | Hecho |
| Validación y errores | Análisis de errores y predicción de EX | C (Zacatac23) | `notebooks/03_evaluacion.ipynb` | Hecho |
| Todos | Presentación | B y C | `presentacion.pdf` | En curso |
