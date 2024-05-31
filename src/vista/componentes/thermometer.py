from PyQt6 import Qwt  
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import random

class ThermometerModificado(Qwt.QwtThermo):
    def __init__(self):
        """
        Inicializa un termómetro modificado con un estilo y comportamiento personalizados.

        Este método inicializa un termómetro con un estilo personalizado y un comportamiento específico. 
        El termómetro se orienta horizontalmente, muestra una escala de color que va desde verde hasta rojo, 
        tiene una alarma que se activa cuando se alcanza el 80% de la escala y se actualiza periódicamente 
        con un valor inicial aleatorio.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            termometro_modificado = ThermometerModificado()
            layout.addWidget(termometro_modificado)

        """
        super().__init__()
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setScalePosition(Qwt.QwtThermo.ScalePosition.TrailingScale)
        colorMap = Qwt.QwtLinearColorMap() 
        colorMap.setColorInterval(Qt.GlobalColor.green, Qt.GlobalColor.red)
        self.setColorMap(colorMap)
        self.setAlarmBrush( Qt.GlobalColor.red)
        self.setAlarmLevel(80)
        self.valor_inicial=random.randint(0, 100)

        self.setValue(ThermometerModificado.numero_flutuante(self.valor_inicial,4))
        self.temporizador=QTimer() 
        self.temporizador.timeout.connect(lambda: self.setValue(ThermometerModificado.numero_flutuante(self.valor_inicial,5)))
        self.temporizador.start(60)

    def numero_flutuante(numero,numero2):
        """
        Genera un número flotante aleatorio en un rango alrededor de un valor dado y lo redondea.

        :param numero: El valor alrededor del cual se generará el número aleatorio.
        :type numero: float
        :param numero2: La mitad del rango en el que se generará el número aleatorio.
        :type numero2: float
        :return: El número flotante aleatorio generado y redondeado.
        :rtype: float

        Ejemplo de uso:

        .. code-block:: python

            numero_generado = ThermometerModificado.numero_flutuante(10, 2)

        """
        x=random.uniform(-numero2,numero2) + numero
        x_redondeado = round(x, 2)
        return x_redondeado
        