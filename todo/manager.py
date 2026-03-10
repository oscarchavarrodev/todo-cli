"""
manager.py — Toda la lógica de negocio vive aquí.

En Java esto sería tu clase 'TaskService' o 'TaskManager'.
No sabe nada de JSON ni de consola. Solo reglas de negocio.
"""

from typing import List

from todo.models import Task
from todo import storage


class TaskManager:
    """
    Gestiona todas las operaciones sobre tareas.

    En Java sería:
        public class TaskManager {
            private List<Task> tasks;
            private String filepath;
        }
    """

    def __init__(self, filepath: str = "tasks.json"):
        """
        Constructor — igual que en Java.

        En Java sería:
            public TaskManager(String filepath) {
                this.filepath = filepath;
                this.tasks = storage.loadTasks(filepath);
            }
        """
        self.filepath = filepath
        self.tasks: List[Task] = storage.load_tasks(filepath)

    # ----------------------------------------------------------------
    # MÉTODO PRIVADO — el guión bajo es la convención en Python
    # para decir "este método es interno, no lo llames desde afuera"
    # En Java sería: private void save()
    # ----------------------------------------------------------------
    def _save(self) -> None:
        """Persiste el estado actual en disco."""
        storage.save_tasks(self.tasks, self.filepath)

    # ----------------------------------------------------------------
    # MÉTODOS PÚBLICOS — la interfaz del manager
    # En Java serían: public Task add(...), public void delete(...)
    # ----------------------------------------------------------------

    def add(
        self,
        title: str,
        description: str = "",
        priority: str = "normal"
    ) -> Task:
        """
        Crea y agrega una nueva tarea.

        La validación ocurre dentro de Task.__post_init__
        así que si el título está vacío o la prioridad es inválida,
        Task lanza un ValueError automáticamente.

        Returns:
            La Task recién creada.
        """
        task = Task(
            title=title,
            description=description,
            priority=priority,
        )
        self.tasks.append(task)
        self._save()
        return task

    def list_tasks(self, only_pending: bool = False) -> List[Task]:
        """
        Retorna la lista de tareas.

        Args:
            only_pending: Si True, filtra las completadas.

        En Java sería:
            public List<Task> listTasks(boolean onlyPending)
        """
        if only_pending:
            return [t for t in self.tasks if not t.completed]
        return list(self.tasks)

    def complete(self, task_id: str) -> Task:
        """
        Marca una tarea como completada.

        Args:
            task_id: ID de 8 caracteres de la tarea.

        Returns:
            La Task actualizada.

        Raises:
            ValueError: Si no existe una tarea con ese ID.
        """
        task = self._find_by_id(task_id)
        task.completed = True
        self._save()
        return task

    def delete(self, task_id: str) -> Task:
        """
        Elimina una tarea por su ID.

        Returns:
            La Task eliminada.

        Raises:
            ValueError: Si no existe una tarea con ese ID.
        """
        task = self._find_by_id(task_id)
        self.tasks.remove(task)
        self._save()
        return task

    def stats(self) -> dict:
        """
        Retorna estadísticas del estado actual.

        Returns:
            Dict con total, completed y pending.
        """
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
        }

    def _find_by_id(self, task_id: str) -> Task:
        """
        Busca una tarea por ID.

        Método privado — solo lo usa este archivo internamente.

        En Java sería:
            private Task findById(String taskId) throws Exception

        Raises:
            ValueError: Si no existe la tarea.
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(
            f"No existe ninguna tarea con ID '{task_id}'.\n"
            f"Usa 'python main.py list' para ver los IDs disponibles."
        )