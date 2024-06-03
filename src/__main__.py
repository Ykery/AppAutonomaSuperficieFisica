from src.modelo import *
from src.modelo.clases import *
from src.vista import *
from src.vista import menu_inicio


def verificar_dependencias():
    # Verificar si las librerias de python estan instaladas
    try:
        import PyQt6
    except ImportError:
        import ctypes
        import os

        # Mostrar mensaje de error en ventana emergente
        if os.name == "nt":
            # Para windows
            ctypes.windll.user32.MessageBoxW(
                0,
                "No se encontró la librería PyQt6, por favor instale la librería PyQt6",
                "Error",
                1,
            )
        elif os.name == "posix":
            # Para linux
            os.system(
                "zenity --error --text='No se encontró la librería PyQt6, por favor instale la librería PyQt6'"
            )
        elif os.name == "mac":
            # Para mac
            os.system(
                'osascript -e \'tell app "System Events" to display dialog "No se encontró la librería PyQt6, por favor instale la librería PyQt6"\''
            )
        # Mostrar mensaje de error por consola y añadirlo al log
        print("No se encontró la librería PyQt6, por favor instale la librería PyQt6")
        exit()


if __name__ == "__main__":

    Conexion.iniciar_bbdd()
    menu_inicio.main()
