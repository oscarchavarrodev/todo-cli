"""
storage.py — Responsable ÚNICAMENTE de persistir datos en disco.

Esta es la capa 'infrastructure' — todo lo que toca el mundo exterior
(archivos, bases de datos, APIs externas) vive aquí.

Regla de oro: este archivo NO sabe nada de lógica de negocio.
Solo sabe leer y escribir. Nada más.
"""

import json
import os
from typing import List

from todo.models import Task


# Nombre del archivo por defecto
DEFAULT_FILE = "tasks.json"


def load_tasks(filepath: str = DEFAULT_FILE) -> List[Task]:
    """
    Carga tareas desde el archivo JSON.

    Si el archivo no existe → retorna lista vacía (no es un error,
    simplemente es la primera vez que se usa el programa).

    Si el archivo está corrupto → avisa al usuario y retorna lista vacía
    en lugar de crashear todo el programa.

    Args:
        filepath: Ruta al archivo JSON. Default: 'tasks.json'

    Returns:
        Lista de objetos Task.
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(item) for item in data]

    except json.JSONDecodeError:
        print(f"⚠️  El archivo {filepath} está corrupto. Empezando desde cero.")
        return []

    except KeyError as e:
        print(f"⚠️  Datos inválidos en {filepath}. Campo faltante: {e}")
        return []


def save_tasks(tasks: List[Task], filepath: str = DEFAULT_FILE) -> None:
    """
    Guarda la lista de tareas en el archivo JSON.

    Usa indent=2 para que el JSON sea legible si alguien
    abre el archivo directamente.

    Args:
        tasks:    Lista de objetos Task a guardar.
        filepath: Ruta al archivo JSON. Default: 'tasks.json'

    Raises:
        OSError: Si no se puede escribir en disco (permisos, disco lleno).
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                [task.to_dict() for task in tasks],
                f,
                indent=2,
                ensure_ascii=False,  # Para que los acentos se guarden bien
            )

    except OSError as e:
        print(f"❌ Error al guardar las tareas: {e}")
        raise