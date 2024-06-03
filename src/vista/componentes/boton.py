from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont


class BotonModificado(QPushButton):
    """
    Un botón personalizado con un estilo y fuente específicos.

    Esta clase extiende :class:`QPushButton` y aplica una fuente personalizada y
    un estilo de hoja de estilos (CSS) para modificar la apariencia del botón.

    :param texto: El texto que se mostrará en el botón.
    :type texto: str

    Ejemplo de uso:

    .. code-block:: python

        boton = BotonModificado("Click me")
        layout.addWidget(boton)
    """

    def __init__(self, texto):
        """
        Inicializa el botón personalizado con el texto dado.

        :param texto: El texto que se mostrará en el botón.
        :type texto: str
        """
        super(BotonModificado, self).__init__(texto)
        self.setFont(QFont("Helvetica", 11))
        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgb(135, 206, 235);
                padding: 10px;
            }
            QPushButton:hover {
            background-color: lightblue;
            }
             QPushButton:pressed {
            background-color: rgb(100, 121, 120);
            }                  
        """
        )


class BotonModificadoExit(BotonModificado):
    def __init__(self, texto):
        """
        Inicializa un botón modificado con un estilo personalizado y señales.

        Este método inicializa un botón con el texto proporcionado y aplica un estilo personalizado al botón para indicar su función de salida.

        :param texto: El texto que se mostrará en el botón.
        :type texto: str

        Ejemplo de uso:

        .. code-block:: python

            boton_salir = BotonModificadoExit("Salir")
            layout.addWidget(boton_salir)

        """
        super().__init__(texto)
        self.setFont(QFont("Helvetica", 11))
        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgb(201,112,098);
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(240, 140, 126);
            }
             QPushButton:pressed {
                background-color: rgb(167, 98, 88);
            }                  
        """
        )


class BotonModificadoRun(BotonModificado):
    def __init__(self, texto):
        """
        Inicializa un botón modificado con un estilo personalizado y señales.

        Este método inicializa un botón con el texto proporcionado y aplica un estilo personalizado al botón para indicar su función de ejecución.

        :param texto: El texto que se mostrará en el botón.
        :type texto: str

        Ejemplo de uso:

        .. code-block:: python

            boton_ejecutar = BotonModificadoRun("Ejecutar")
            layout.addWidget(boton_ejecutar)

        """
        super().__init__(texto)
        self.setFont(QFont("Helvetica", 11))
        self.setStyleSheet(
            """
            QPushButton {
                background-color: rgb(59, 235, 156);
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(79, 255, 176);
            }
             QPushButton:pressed {
                background-color: rgb(100, 121, 120);
            }                  
        """
        )
