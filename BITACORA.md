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
