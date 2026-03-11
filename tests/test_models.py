"""
test_models.py — Tests de la clase Task.

Probamos que el modelo funciona correctamente de forma aislada,
sin depender de archivos ni de la consola.
"""

import pytest
from todo.models import Task


class TestTaskCreation:
    """Tests de creación de tareas."""

    def test_crear_tarea_basica(self):
        """Una tarea con solo título debe crearse correctamente."""
        task = Task(title="Aprender Python")

        assert task.title == "Aprender Python"
        assert task.completed is False
        assert task.priority == "normal"
        assert task.description == ""

    def test_id_generado_automaticamente(self):
        """Cada tarea debe tener un ID único de 8 caracteres."""
        task = Task(title="Tarea")

        assert task.id is not None
        assert len(task.id) == 8

    def test_dos_tareas_tienen_ids_diferentes(self):
        """Dos tareas distintas nunca deben tener el mismo ID."""
        task1 = Task(title="Tarea 1")
        task2 = Task(title="Tarea 2")

        assert task1.id != task2.id

    def test_fecha_creacion_generada_automaticamente(self):
        """La fecha de creación debe generarse automáticamente."""
        task = Task(title="Tarea")

        assert task.created_at is not None
        assert len(task.created_at) > 0

    def test_crear_tarea_con_todos_los_campos(self):
        """Una tarea con todos los campos debe crearse correctamente."""
        task = Task(
            title="Leer Clean Code",
            description="Capítulos 1 al 5",
            priority="high",
        )

        assert task.title == "Leer Clean Code"
        assert task.description == "Capítulos 1 al 5"
        assert task.priority == "high"


class TestTaskValidation:
    """Tests de validaciones del modelo."""

    def test_titulo_vacio_lanza_error(self):
        """Un título vacío debe lanzar ValueError."""
        with pytest.raises(ValueError, match="título"):
            Task(title="")

    def test_titulo_solo_espacios_lanza_error(self):
        """Un título con solo espacios debe lanzar ValueError."""
        with pytest.raises(ValueError, match="título"):
            Task(title="     ")

    def test_prioridad_invalida_lanza_error(self):
        """Una prioridad inválida debe lanzar ValueError."""
        with pytest.raises(ValueError, match="Prioridad"):
            Task(title="Tarea", priority="urgente")

    def test_titulo_se_normaliza(self):
        """Los espacios al inicio y final del título deben eliminarse."""
        task = Task(title="  Aprender Python  ")

        assert task.title == "Aprender Python"


class TestTaskSerialization:
    """Tests de serialización — to_dict y from_dict."""

    def test_to_dict_contiene_todos_los_campos(self):
        """to_dict debe retornar todos los campos necesarios."""
        task = Task(title="Tarea", priority="high")
        d = task.to_dict()

        assert d["title"] == "Tarea"
        assert d["priority"] == "high"
        assert d["completed"] is False
        assert "id" in d
        assert "created_at" in d

    def test_from_dict_crea_task_correctamente(self):
        """from_dict debe recrear un Task idéntico al original."""
        task_original = Task(title="Tarea", priority="high")
        d = task_original.to_dict()
        task_recreado = Task.from_dict(d)

        assert task_recreado.id == task_original.id
        assert task_recreado.title == task_original.title
        assert task_recreado.priority == task_original.priority
        assert task_recreado.completed == task_original.completed

    def test_ida_y_vuelta(self):
        """
        Un Task convertido a dict y de vuelta a Task
        debe ser idéntico al original.
        """
        task = Task(title="Test ida y vuelta", priority="low")
        task_recreado = Task.from_dict(task.to_dict())

        assert task.id == task_recreado.id
        assert task.title == task_recreado.title


class TestTaskStr:
    """Tests de representación visual."""

    def test_str_tarea_pendiente(self):
        """Una tarea pendiente debe mostrar el ícono correcto."""
        task = Task(title="Pendiente")
        resultado = str(task)

        assert "⬜" in resultado
        assert "Pendiente" in resultado

    def test_str_tarea_completada(self):
        """Una tarea completada debe mostrar el ícono correcto."""
        task = Task(title="Completada")
        task.completed = True
        resultado = str(task)

        assert "✅" in resultado