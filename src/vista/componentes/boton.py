from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPushButton


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
        self.setProperty("class", "danger")

        self.setStyleSheet(
            """
                QPushButton {background-color: #dc3545; color: #31363b;}
                QPushButton:hover {background-color: transparent;color: #dc3545;}
                QPushButton:pressed {background-color: #dc3545; color: #31363b;}
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

        self.setProperty("class", "success")
        self.setStyleSheet(
            """
                QPushButton {background-color: #17a2b8; color: #31363b;} 
                QPushButton:hover {background-color: transparent;color: #17a2b8;}
                QPushButton:pressed {background-color: #17a2b8; color: #31363b;}
            """
        )
