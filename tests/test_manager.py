"""
test_manager.py — Tests del cerebro del programa.

Probamos toda la lógica de negocio: agregar, listar,
completar, eliminar y estadísticas.
"""

import pytest
from todo.manager import TaskManager

# ----------------------------------------------------------------
# FIXTURE PRINCIPAL
# Crea un manager limpio para cada test y elimina el archivo
# temporal al terminar — como @BeforeEach y @AfterEach en JUnit
# ----------------------------------------------------------------


@pytest.fixture
def manager(tmp_path):
    """
    Crea un TaskManager con archivo temporal para cada test.

    Cada test arranca con un manager completamente limpio
    sin tareas — sin importar lo que hicieron los otros tests.
    """
    filepath = str(tmp_path / "test_tasks.json")
    return TaskManager(filepath=filepath)


# ----------------------------------------------------------------
# TESTS DE add()
# ----------------------------------------------------------------


class TestAdd:
    """Tests del método add."""

    def test_agregar_tarea_basica(self, manager):
        """Debe crear una tarea con los valores correctos."""
        task = manager.add("Aprender Python")

        assert task.title == "Aprender Python"
        assert task.completed is False
        assert task.priority == "normal"

    def test_agregar_tarea_con_todos_los_campos(self, manager):
        """Debe crear una tarea con todos los campos correctamente."""
        task = manager.add(
            title="Leer Clean Code",
            description="Capítulos 1 al 5",
            priority="high",
        )

        assert task.title == "Leer Clean Code"
        assert task.description == "Capítulos 1 al 5"
        assert task.priority == "high"

    def test_agregar_aumenta_el_total(self, manager):
        """Cada tarea agregada debe aumentar el total."""
        manager.add("Tarea 1")
        manager.add("Tarea 2")
        manager.add("Tarea 3")

        assert len(manager.tasks) == 3

    def test_titulo_vacio_lanza_error(self, manager):
        """Un título vacío debe lanzar ValueError."""
        with pytest.raises(ValueError):
            manager.add("")

    def test_prioridad_invalida_lanza_error(self, manager):
        """Una prioridad inválida debe lanzar ValueError."""
        with pytest.raises(ValueError):
            manager.add("Tarea", priority="urgente")

    def test_tarea_se_persiste_en_disco(self, manager):
        """
        La tarea debe guardarse en disco inmediatamente.
        Verificamos creando un segundo manager con el mismo archivo.
        """
        manager.add("Tarea persistida")

        # Creamos otro manager con el mismo archivo
        manager2 = TaskManager(filepath=manager.filepath)

        assert len(manager2.tasks) == 1
        assert manager2.tasks[0].title == "Tarea persistida"


# ----------------------------------------------------------------
# TESTS DE list_tasks()
# ----------------------------------------------------------------


class TestListTasks:
    """Tests del método list_tasks."""

    def test_lista_vacia_al_inicio(self, manager):
        """Un manager nuevo debe tener lista vacía."""
        tasks = manager.list_tasks()

        assert tasks == []

    def test_lista_todas_las_tareas(self, manager):
        """Debe retornar todas las tareas."""
        manager.add("Tarea 1")
        manager.add("Tarea 2")

        tasks = manager.list_tasks()

        assert len(tasks) == 2

    def test_lista_solo_pendientes(self, manager):
        """Con only_pending=True debe retornar solo las pendientes."""
        t1 = manager.add("Pendiente 1")
        t2 = manager.add("Pendiente 2")
        manager.add("Pendiente 3")

        # Completamos dos
        manager.complete(t1.id)
        manager.complete(t2.id)

        pendientes = manager.list_tasks(only_pending=True)

        assert len(pendientes) == 1
        assert pendientes[0].title == "Pendiente 3"

    def test_list_retorna_copia_no_original(self, manager):
        """
        list_tasks debe retornar una copia de la lista.
        Modificar la copia NO debe afectar el manager.
        """
        manager.add("Tarea")
        tasks = manager.list_tasks()

        # Vaciamos la copia
        tasks.clear()

        # El manager no debe verse afectado
        assert len(manager.tasks) == 1


# ----------------------------------------------------------------
# TESTS DE complete()
# ----------------------------------------------------------------


class TestComplete:
    """Tests del método complete."""

    def test_completar_tarea(self, manager):
        """Una tarea completada debe tener completed=True."""
        task = manager.add("Completar esto")
        manager.complete(task.id)

        assert manager.tasks[0].completed is True

    def test_completar_id_inexistente_lanza_error(self, manager):
        """Completar un ID que no existe debe lanzar ValueError."""
        with pytest.raises(ValueError):
            manager.complete("id_falso")

    def test_completar_persiste_en_disco(self, manager):
        """El estado completado debe guardarse en disco."""
        task = manager.add("Tarea")
        manager.complete(task.id)

        # Verificamos con un segundo manager
        manager2 = TaskManager(filepath=manager.filepath)

        assert manager2.tasks[0].completed is True


# ----------------------------------------------------------------
# TESTS DE delete()
# ----------------------------------------------------------------


class TestDelete:
    """Tests del método delete."""

    def test_eliminar_tarea(self, manager):
        """Eliminar una tarea debe reducir el total."""
        task = manager.add("Eliminar esto")
        manager.delete(task.id)

        assert len(manager.tasks) == 0

    def test_eliminar_id_inexistente_lanza_error(self, manager):
        """Eliminar un ID que no existe debe lanzar ValueError."""
        with pytest.raises(ValueError):
            manager.delete("id_falso")

    def test_eliminar_tarea_correcta(self, manager):
        """Debe eliminar solo la tarea indicada, no las demás."""
        manager.add("Tarea 1")
        t2 = manager.add("Tarea 2")
        manager.add("Tarea 3")

        manager.delete(t2.id)

        titles = [t.title for t in manager.tasks]
        assert "Tarea 1" in titles
        assert "Tarea 2" not in titles
        assert "Tarea 3" in titles

    def test_eliminar_persiste_en_disco(self, manager):
        """La eliminación debe guardarse en disco."""
        task = manager.add("Tarea")
        manager.delete(task.id)

        manager2 = TaskManager(filepath=manager.filepath)

        assert len(manager2.tasks) == 0


# ----------------------------------------------------------------
# TESTS DE stats()
# ----------------------------------------------------------------


class TestStats:
    """Tests del método stats."""

    def test_stats_manager_vacio(self, manager):
        """Un manager vacío debe tener todas las stats en 0."""
        s = manager.stats()

        assert s["total"] == 0
        assert s["completed"] == 0
        assert s["pending"] == 0

    def test_stats_con_tareas(self, manager):
        """Las stats deben reflejar el estado real."""
        t1 = manager.add("Tarea 1")
        t2 = manager.add("Tarea 2")
        manager.add("Tarea 3")

        manager.complete(t1.id)
        manager.complete(t2.id)

        s = manager.stats()

        assert s["total"] == 3
        assert s["completed"] == 2
        assert s["pending"] == 1

    def test_pending_es_total_menos_completed(self, manager):
        """pending siempre debe ser total - completed."""
        manager.add("T1")
        manager.add("T2")
        t3 = manager.add("T3")
        manager.complete(t3.id)

        s = manager.stats()

        assert s["pending"] == s["total"] - s["completed"]
