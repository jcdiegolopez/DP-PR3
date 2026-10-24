# Proyecto 3: Text-to-SQL con LoRA

Universidad del Valle de Guatemala, Facultad de Ingeniería. Deep Learning 2026.

Fine-tuning con LoRA de `Qwen/Qwen2.5-Coder-1.5B-Instruct` para generar consultas MySQL 8.4.10 a partir del
esquema de una base de datos y una pregunta en español.

> **Estado:** la parte de datos está terminada. El entrenamiento, `solucion.py`, la evaluación y la
> presentación están pendientes y se documentan en las secciones marcadas como *pendiente*.

## Estructura

```
datos/
  entrenamiento.jsonl      2,403 pares de entrenamiento
  eval_loss.jsonl          142 pares de 8 bases de Spider, solo para la curva de loss
  descartes.csv            pares descartados y motivo
  revision_manual.csv      muestra para revisión humana
  esquemas/
    entrenamiento/         12 esquemas propios (.sql)
    spider_carga.csv       resultado de cargar las bases de Spider en MySQL
  generados/               pares intermedios (Spider filtrado, traducido, propios)
scripts/                   pipeline de datos
notebooks/01_datos.ipynb   resumen del dataset
```

## Cómo reproducir los datos

Requiere Docker y Python 3.11.

```bash
docker run -d --name mysql84 -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8.4.10
# usuario de solo lectura, como el del evaluador
docker exec mysql84 mysql -uroot -proot -e "CREATE USER 'lector'@'%' IDENTIFIED BY 'lector'; GRANT SELECT, SHOW VIEW ON *.* TO 'lector'@'%';"

pip install sqlglot pymysql faker pandas matplotlib transformers sentencepiece sacremoses torch gdown

# Spider (7,000 pares): descargar y descomprimir en spider_data/extracted/spider_data/
python scripts/spider_a_mysql.py        # carga 140 bases en MySQL (prefijo sp_)
python scripts/filtrar_spider.py        # convierte a MySQL y compara resultados con SQLite
python scripts/seleccionar_spider.py    # elige 2,000 pares
python scripts/traducir_spider.py       # traduce las preguntas al español

# Esquemas propios
python scripts/cargar_esquemas.py       # crea tr_<esquema>
python scripts/poblar_esquemas.py       # datos ficticios, semilla 2026
python scripts/filtrar_propios.py       # valida los pares escritos en datos/generados/propios/

python scripts/dividir.py               # ensambla datos/entrenamiento.jsonl y revisa fuga de esquemas
```

## Dataset

| Fuente | Pares | Fáciles | Medios | Difíciles |
|---|---|---|---|---|
| Spider traducido | 1,858 | 465 | 746 | 647 |
| Esquemas propios | 545 | 108 | 201 | 236 |
| **Total** | **2,403** | **573** | **947** | **883** |

(Los 142 pares de las 8 bases reservadas para la curva de loss no están en esta tabla.)

**Spider.** De 7,000 pares de entrenamiento, 6,380 pasaron el filtro. Se descartaron 620:

| Motivo | Pares |
|---|---|
| `resultado_vacio`: la consulta es válida pero no devuelve filas | 238 |
| `resultado_distinto`: SQLite y MySQL devuelven filas diferentes | 218 |
| `error_mysql`: falla en MySQL, sobre todo por `ONLY_FULL_GROUP_BY` | 164 |

Las 140 bases de Spider se cargaron sin errores. Dos ajustes en la conversión fueron necesarios: los textos entre
comillas dobles de Spider se pasan a comillas simples (`sqlglot` los leía como columnas) y cada tabla se renombra a su
mayúscula real, porque MySQL en Linux distingue mayúsculas en nombres de tabla. Sin ellos pasaba solo el 60 %.

**Esquemas propios.** 12 bases de 8 o 9 tablas con `COMMENT` en tablas y columnas, en tres estilos de nombres:
español (supermercado, universidad, banco, hospital), inglés (telecom, aerolínea, tienda en línea, cine) y abreviado
(inventario, planilla, delivery, seguros). Los datos son ficticios y se generan con semilla 2026; dos corridas dan
exactamente los mismos totales. De 565 pares escritos se descartaron 20, todos por devolver vacío.

**Traducción.** 100 preguntas de Spider se tradujeron a mano y 1,900 con `Helsinki-NLP/opus-mt-en-es`, protegiendo
los valores entre comillas para que sigan coincidiendo con el SQL y corrigiendo el registro formal ("Liste" →
"Lista"). Cada pregunta termina con `Devuelve: columna1, columna2`.

**Largo.** Mediana de 822 tokens por ejemplo, p99 de 2,595 y máximo de 4,980. Con `max_length = 2048` entra el
95.5 %; los más largos son de bases enormes de Spider como `baseball_1`.

### Limitaciones conocidas

- El filtro por ejecución comprueba que el SQL corre y devuelve filas, **no** que responda a la pregunta. La tasa de
  error real se mide con `datos/revision_manual.csv` (50 pares propios y 30 traducciones). *Pendiente de revisión humana.*
- Las traducciones automáticas tienen errores de sentido (por ejemplo "as long as" traducido como "tanto como").
  No se midió su tasa.
- Los datos propios no tienen tildes, y los pares propios los escribió un asistente de IA (ver más abajo).
- La mayoría de los pares de Spider vienen de bases con nombres en inglés y esquemas sin `COMMENT`.

## Entrenamiento y evaluación

*Pendiente.* Se documentarán aquí la validación propia, el baseline, las dos configuraciones de LoRA, el experimento
de inferencia, el análisis de errores y la predicción de EX.

## Ejecución de `solucion.py`

*Pendiente.*

## Licencias

- **Spider:** CC BY-SA 4.0 (verificar en https://yale-lily.github.io/spider antes de entregar).
- **Qwen2.5-Coder-1.5B-Instruct:** verificar la licencia en la página del modelo en Hugging Face antes de entregar.
- **opus-mt-en-es:** CC BY 4.0 (verificar en su página en Hugging Face).
- Los esquemas, datos ficticios y pares propios son de los autores.

## Uso de IA

Se usó un asistente de IA (Claude Code) en estas tareas, y se declara conforme al enunciado:

- Escribir los 12 esquemas SQL propios y los 565 pares pregunta–SQL sobre ellos.
- Traducir al español 100 preguntas de Spider, y escribir los scripts de conversión, filtrado, traducción y población.
- Redactar la documentación del dataset.
- Escribir `prompt.py`, `solucion.py`, `scripts/entrenar.py` y los notebooks de entrenamiento y de prueba en Colab, y
  ayudar a depurar el entrenamiento de las configuraciones LoRA A y B.

Se usó además un modelo de traducción automática (`opus-mt-en-es`) para 1,900 preguntas. Ningún modelo ni API
externa interviene al generar consultas en `solucion.py`. Toda consulta del dataset se ejecutó en MySQL 8.4.10 antes
de aceptarse.
