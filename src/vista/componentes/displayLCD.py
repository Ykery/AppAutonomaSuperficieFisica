from PyQt6.QtWidgets import QLCDNumber


class DisplayLCDModificado(QLCDNumber):
    def __init__(self, initial_value=0, digit_count=None):
        """
        Inicializa un display LCD modificado con un estilo personalizado.

        Este método inicializa un display LCD con un estilo personalizado que cambia el color de fondo a azul claro y el color del texto a negro. Además, permite configurar el valor inicial y el número de dígitos si se proporciona.

        :param initial_value: El valor inicial que se mostrará en el display (por defecto es 0).
        :type initial_value: int, optional
        :param digit_count: El número de dígitos que mostrará el display (por defecto es None, lo que significa que se ajustará automáticamente).
        :type digit_count: int, optional

        Ejemplo de uso:

        .. code-block:: python

            display_lcd_modificado = DisplayLCDModificado(initial_value=42, digit_count=4)
            layout.addWidget(display_lcd_modificado)

        """
        super().__init__()
        if digit_count:
            self.setDigitCount(digit_count)
        self.setSmallDecimalPoint(True)
        self.display(initial_value)
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.setFixedSize(100, 50)
