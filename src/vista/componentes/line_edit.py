from PyQt6.QtWidgets import QLineEdit

class LineEditModificado(QLineEdit):
    def __init__(self, initial_value="", placeholder_text=None):
        """
        Inicializa un line edit modificado con un estilo personalizado.

        Este método inicializa un line edit con un estilo personalizado que cambia el color de fondo a azul claro y el color del texto

        :param initial_value: El valor inicial que se mostrará en el line edit (por defecto es "").
        :type initial_value: str, optional
        :param placeholder_text: El texto de marcador de posición que se mostrará en el line edit (por defecto es None).
        :type placeholder_text: str, optional
    """
        super().__init__()
        self.setStyleSheet("color: #f0f0f0;")
        self.setText(initial_value)
        if placeholder_text:
            self.setPlaceholderText(placeholder_text)
        