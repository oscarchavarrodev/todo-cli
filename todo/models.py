"""
models.py — Define la estructura de una tarea.

Esta es la capa 'domain' — las reglas del negocio puro.
No importa nada externo: ni JSON, ni consola, ni base de datos.
Esta independencia es lo que hace el código testeable y mantenible.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


VALID_PRIORITIES = {"low", "normal", "high"}


@dataclass
class Task:
    """
    Representa una tarea en el sistema.

    Atributos:
        title:       Título de la tarea (obligatorio)
        description: Detalle opcional
        priority:    low | normal | high
        completed:   False por defecto
        id:          ID único de 8 caracteres generado automáticamente
        created_at:  Fecha/hora de creación en formato ISO
    """

    title: str
    description: str = ""
    priority: str = "normal"
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    def __post_init__(self):
        """Validaciones que corren automáticamente al crear una Task."""
        if not self.title or not self.title.strip():
            raise ValueError("El título no puede estar vacío.")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Prioridad inválida '{self.priority}'. "
                f"Usa: {', '.join(sorted(VALID_PRIORITIES))}"
            )
        # Normalizamos el título (sin espacios al inicio/final)
        self.title = self.title.strip()

    def to_dict(self) -> dict:
        """
        Convierte la Task a diccionario plano.
        Usado para serializar a JSON.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Crea una Task desde un diccionario.
        Usado al leer desde JSON.

        El 'classmethod' nos permite llamarlo como:
        task = Task.from_dict({"title": "...", ...})
        sin necesitar una instancia previa.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "normal"),
            completed=data.get("completed", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )

    def __str__(self) -> str:
        """Representación visual en la terminal."""
        status = "✅" if self.completed else "⬜"
        priority_icon = {"high": "🔴", "normal": "🟡", "low": "🟢"}[self.priority]
        return f"[{self.id}] {status} {priority_icon}  {self.title}"