from PyQt6 import Qwt  
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import random

class Thermometer_modificado(Qwt.QwtThermo):
    def __init__(self):
        super().__init__()
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setScalePosition(Qwt.QwtThermo.ScalePosition.TrailingScale)
        colorMap = Qwt.QwtLinearColorMap() 
        colorMap.setColorInterval(Qt.GlobalColor.green, Qt.GlobalColor.red)
        self.setColorMap(colorMap)
        self.setAlarmBrush( Qt.GlobalColor.red)
        self.setAlarmLevel(80)
        self.valor_inicial=random.randint(0, 100)

        self.setValue(Thermometer_modificado.numero_flutuante(self.valor_inicial,4))
        self.temporizador=QTimer() 
        self.temporizador.timeout.connect(lambda: self.setValue(Thermometer_modificado.numero_flutuante(self.valor_inicial,5)))
        self.temporizador.start(60)

    def numero_flutuante(numero,numero2):
        x=random.uniform(-numero2,numero2) + numero
        x_redondeado = round(x, 2)
        return x_redondeado
        