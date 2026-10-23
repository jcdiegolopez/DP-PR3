"""Single source of the prompt.

Imported by solucion.py, the training notebook and the evaluator, so the model
sees exactly the same text when training, in the baseline and when graded.
"""

SYSTEM = (
    "Eres un experto en MySQL 8.4. Dado el esquema de una base de datos y una "
    "pregunta en español, responde únicamente con una consulta SQL SELECT o "
    "WITH ... SELECT válida para MySQL 8.4 con ONLY_FULL_GROUP_BY. "
    "No escribas explicaciones."
)


def build_messages(esquema: str, pregunta: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Esquema:\n{esquema}\n\nPregunta: {pregunta}"},
    ]


def build_correction(sql: str, error: str) -> list[dict]:
    """Turns appended after a failed attempt (self-correction experiment)."""
    return [
        {"role": "assistant", "content": sql},
        {"role": "user", "content": f"La consulta falló con este error: {error}. Corrígela."},
    ]
