"""
cli.py — Interfaz de línea de comandos.

En Java esto sería tu clase 'Main' o 'App' — el punto
donde el usuario interactúa con el programa.

Aquí solo hay presentación: recibir comandos, mostrar resultados.
NUNCA lógica de negocio en este archivo.
"""

import argparse
import sys

from todo.manager import TaskManager


def build_parser() -> argparse.ArgumentParser:
    """
    Construye el parser de comandos.

    argparse es la librería estándar de Python para CLIs.
    Es como leer los 'args[]' de Java pero con superpoderes:
    valida tipos, genera --help automático, maneja subcomandos.
    """
    parser = argparse.ArgumentParser(
        prog="todo",
        description="📝 Gestor de tareas en la terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py add "Aprender Python"
  python main.py add "Leer libro" --desc "Clean Code" --priority high
  python main.py list
  python main.py list --pending
  python main.py complete a1b2c3d4
  python main.py delete a1b2c3d4
  python main.py stats
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Comando a ejecutar",
    )

    add_parser = subparsers.add_parser("add", help="Agregar una nueva tarea")
    add_parser.add_argument(
        "title",
        help="Título de la tarea (entre comillas si tiene espacios)",
    )
    add_parser.add_argument(
        "--desc",
        default="",
        help="Descripción opcional",
    )
    add_parser.add_argument(
        "--priority",
        choices=["low", "normal", "high"],
        default="normal",
        help="Prioridad: low, normal, high (default: normal)",
    )

    list_parser = subparsers.add_parser("list", help="Listar tareas")
    list_parser.add_argument(
        "--pending",
        action="store_true",
        help="Mostrar solo tareas pendientes",
    )

    complete_parser = subparsers.add_parser(
        "complete",
        help="Marcar una tarea como completada",
    )
    complete_parser.add_argument("id", help="ID de la tarea")

    delete_parser = subparsers.add_parser("delete", help="Eliminar una tarea")
    delete_parser.add_argument("id", help="ID de la tarea")

    subparsers.add_parser("stats", help="Ver estadísticas")

    return parser


def _print_task_list(manager: TaskManager, only_pending: bool = False) -> None:
    """Imprime la lista de tareas con formato."""
    tasks = manager.list_tasks(only_pending=only_pending)

    if not tasks:
        msg = (
            "📭 No hay tareas pendientes."
            if only_pending
            else "📭 No hay tareas."
        )
        print(msg)
        return

    print("\n" + "─" * 52)
    for task in tasks:
        print(f"  {task}")
        if task.description:
            print(f"     └─ {task.description}")
    print("─" * 52)

    s = manager.stats()
    print(
        f"  Total: {s['total']}  |  "
        f"✅ Completadas: {s['completed']}  |  "
        f"⬜ Pendientes: {s['pending']}\n"
    )


def run(args=None) -> None:
    """
    Punto de entrada de la CLI.

    Args:
        args: Lista de argumentos. None = lee sys.argv (la terminal).
              Pasamos args explícitamente en los tests para simular
              comandos sin abrir una terminal real.
    """
    parser = build_parser()
    parsed = parser.parse_args(args)
    manager = TaskManager()

    if parsed.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if parsed.command == "add":
            task = manager.add(
                title=parsed.title,
                description=parsed.desc,
                priority=parsed.priority,
            )
            print("\n✅ Tarea agregada exitosamente:")
            print(f"   {task}\n")

        elif parsed.command == "list":
            _print_task_list(manager, only_pending=parsed.pending)

        elif parsed.command == "complete":
            task = manager.complete(parsed.id)
            print("\n✅ Tarea completada:")
            print(f"   {task}\n")

        elif parsed.command == "delete":
            task = manager.delete(parsed.id)
            print(f"\n🗑️  Tarea eliminada: '{task.title}'\n")

        elif parsed.command == "stats":
            s = manager.stats()
            print("\n" + "─" * 30)
            print("  📊 Estadísticas")
            print("─" * 30)
            print(f"  Total:       {s['total']}")
            print(f"  Completadas: {s['completed']}")
            print(f"  Pendientes:  {s['pending']}")
            if s["total"] > 0:
                pct = (s["completed"] / s["total"]) * 100
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                progreso = f"[{bar}] {pct:.0f}%"
                print(f"  Progreso:    {progreso}")
            print("─" * 30 + "\n")

    except ValueError as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)