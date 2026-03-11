"""
test_storage.py — Tests de lectura y escritura en disco.

Usamos archivos temporales para no contaminar el proyecto
con datos de prueba.
"""

import json
import os
import pytest
from todo.models import Task
from todo import storage


# ----------------------------------------------------------------
# FIXTURES — son como el @BeforeEach de JUnit en Java
# Se ejecutan antes de cada test automáticamente
# ----------------------------------------------------------------

@pytest.fixture
def temp_file(tmp_path):
    """
    Crea una ruta temporal para el archivo JSON de tests.
    
    tmp_path es una carpeta temporal que pytest crea y elimina
    automáticamente — no ensucia tu proyecto con archivos de prueba.
    """
    return str(tmp_path / "test_tasks.json")


@pytest.fixture
def tasks_de_prueba():
    """Lista de tareas listas para usar en los tests."""
    return [
        Task(title="Tarea 1", priority="high"),
        Task(title="Tarea 2", priority="normal"),
        Task(title="Tarea 3", priority="low"),
    ]


# ----------------------------------------------------------------
# TESTS DE load_tasks
# ----------------------------------------------------------------

class TestLoadTasks:
    """Tests de la función load_tasks."""

    def test_archivo_inexistente_retorna_lista_vacia(self, temp_file):
        """Si el archivo no existe, debe retornar lista vacía."""
        tasks = storage.load_tasks("archivo_que_no_existe.json")

        assert tasks == []

    def test_carga_tareas_correctamente(self, temp_file, tasks_de_prueba):
        """Las tareas guardadas deben cargarse correctamente."""
        # Primero guardamos
        storage.save_tasks(tasks_de_prueba, temp_file)

        # Luego cargamos
        tasks_cargadas = storage.load_tasks(temp_file)

        assert len(tasks_cargadas) == 3
        assert tasks_cargadas[0].title == "Tarea 1"
        assert tasks_cargadas[1].title == "Tarea 2"
        assert tasks_cargadas[2].title == "Tarea 3"

    def test_archivo_corrupto_retorna_lista_vacia(self, temp_file):
        """Un archivo JSON corrupto debe retornar lista vacía sin crashear."""
        # Escribimos contenido inválido en el archivo
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("esto no es json valido {{{")

        tasks = storage.load_tasks(temp_file)

        assert tasks == []

    def test_archivo_vacio_retorna_lista_vacia(self, temp_file):
        """Un archivo JSON vacío debe retornar lista vacía."""
        with open(temp_file, "w") as f:
            json.dump([], f)

        tasks = storage.load_tasks(temp_file)

        assert tasks == []


# ----------------------------------------------------------------
# TESTS DE save_tasks
# ----------------------------------------------------------------

class TestSaveTasks:
    """Tests de la función save_tasks."""

    def test_guarda_tareas_correctamente(self, temp_file, tasks_de_prueba):
        """Las tareas deben guardarse y el archivo debe existir."""
        storage.save_tasks(tasks_de_prueba, temp_file)

        assert os.path.exists(temp_file)

    def test_contenido_guardado_es_valido(self, temp_file, tasks_de_prueba):
        """El contenido guardado debe ser JSON válido y legible."""
        storage.save_tasks(tasks_de_prueba, temp_file)

        with open(temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 3
        assert data[0]["title"] == "Tarea 1"
        assert data[1]["priority"] == "normal"

    def test_guardar_lista_vacia(self, temp_file):
        """Guardar lista vacía debe crear un archivo con array vacío."""
        storage.save_tasks([], temp_file)

        with open(temp_file, "r") as f:
            data = json.load(f)

        assert data == []

    def test_ida_y_vuelta_completa(self, temp_file, tasks_de_prueba):
        """
        Guardar y cargar debe producir tareas idénticas a las originales.
        Este es el test más importante de storage.
        """
        # Guardamos
        storage.save_tasks(tasks_de_prueba, temp_file)

        # Cargamos
        tasks_cargadas = storage.load_tasks(temp_file)

        # Verificamos que son idénticas
        assert len(tasks_cargadas) == len(tasks_de_prueba)
        for original, cargada in zip(tasks_de_prueba, tasks_cargadas):
            assert original.id == cargada.id
            assert original.title == cargada.title
            assert original.priority == cargada.priority
            assert original.completed == cargada.completed