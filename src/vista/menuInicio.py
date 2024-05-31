import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
import numpy as np


from src.vista import teasMain, vistaExperimentos, mokeLoopMain

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import Qwt
from PyQt6.Qwt import *
import time
from datetime import date
from .componentes.boton import *

class MenuInicio(QWidget):
    def __init__(self, ):
        super().__init__()
        self.setWindowTitle("Menu Inicio")
        self.fuenteHelvetica = QFont("Helvetica", 11)
        self.setStyleSheet("background-color: rgb(176, 213, 212);" "color: black;") # Estilo de la ventana
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.setLayout(layout)

        self.child_window = None
        self.lb_hora= QLCDNumber()
        self.lb_hora.setFixedSize(100, 50)
        self.lb_hora.setDigitCount(8)
        self.lb_hora.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lb_hora.setStyleSheet(" color: black")
        self.lb_fecha = QLabel("")
        self.lb_fecha.setFont(self.fuenteHelvetica)
        self.lb_fecha.setStyleSheet(" color: black")
        lb_label = QLabel("Elija una opción:")
        btn_teas = boton_modificado("Realizar Experimento TEAS TimeScan")
        elemento_fecha_hora = QWidget()
        elemento_fecha_hora.setLayout( QHBoxLayout() )
        elemento_fecha_hora.layout().addWidget(self.lb_fecha)
        elemento_fecha_hora.layout().addWidget(self.lb_hora)
        self.lb_fecha.setFont(QFont("Helvetica", 18))
        

        btn_moke = boton_modificado("Realizar Experimento MOKE Loop")
        btn_experimentos = boton_modificado("Ver Experimentos Realizados")
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
               
        btn_quit = boton_modificado_exit("QUIT")

        lb_label.setFont(self.fuenteHelvetica)
        btn_teas.setFont(self.fuenteHelvetica)
        btn_moke.setFont(self.fuenteHelvetica)
        btn_experimentos.setFont(self.fuenteHelvetica)
        btn_quit.setFont(self.fuenteHelvetica)
        layout.addWidget(elemento_fecha_hora)
        layout.addWidget(lb_label)
        layout.addWidget(btn_teas)
        layout.addWidget(btn_moke)
        layout.addWidget(btn_experimentos)
        layout.addWidget(linea) 
        layout.addWidget(btn_quit)

        self.actualizar_fecha_hora()
        # Si se borra la ventana principal, se cierra la aplicación
        btn_quit.clicked.connect(QApplication.instance().quit)

        btn_teas.clicked.connect(lambda: self.open_child_window(teasMain.TeasWindow))
        btn_moke.clicked.connect(lambda: self.open_child_window(mokeLoopMain.VistaPrincipal))
        btn_experimentos.clicked.connect(lambda: self.open_child_window(vistaExperimentos.ExperimentosWindow))


    def open_child_window(self, window_class):
        # Cerrar todas las ventanas hijas abiertas
        if self.child_window:
            self.child_window.close()

        # Abrir una nueva ventana hija
        new_window = window_class()
        self.child_window = new_window
        new_window.show()
        print(self.child_window)

    def actualizar_fecha_hora(self):
        hora = time.strftime("%H:%M:%S")
        self.lb_hora.display(hora)
        self.get_dia()
        QTimer.singleShot(200, self.actualizar_fecha_hora)

    def get_dia(self):
        hoy = date.today()
        d1 = hoy.strftime("%d/%m/%Y")
        self.lb_fecha.setText(d1)
    

def main():
    app = QApplication(sys.argv)
    window = MenuInicio()
    window.show()
    sys.exit(app.exec())