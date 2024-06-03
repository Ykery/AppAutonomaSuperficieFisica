from PyQt6.QtWidgets import QComboBox


class QComboBoxModificado(QComboBox):
    def __init__(self):
        """
        Inicializa un combo box modificado con un estilo personalizado.

        Este método inicializa un combo box con un estilo personalizado que cambia el color de fondo a azul claro y el color del texto a negro.

        Ejemplo de uso:

        .. code-block:: python

            combo_box_modificado = QComboBoxModificado()
            layout.addWidget(combo_box_modificado)

        """
        super().__init__()
        self.setStyleSheet("background-color: rgb(200, 255, 255); color: black;")
        self.setCurrentIndex(0)
