"""
main.py — Entry point del programa.

En Java esto sería:
    public static void main(String[] args)

Solo hace UNA cosa: arrancar la CLI.
Nunca pongas lógica de negocio aquí.
"""

from todo.cli import run

if __name__ == "__main__":
    run()
