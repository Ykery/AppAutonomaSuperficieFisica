import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMainWindow
import numpy as np

from ..modelo.dao import ExperimentoDAO
from ..vista import teasMain, teasGraph, vistaExperimentos, mokeLoopMain



from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import Qwt
from PyQt6.Qwt import *



class MenuInicio(QWidget):
    def __init__(self, ):
        super().__init__()
        self.setWindowTitle("Menu Inicio")
        self.fuenteHelvetica = QFont("Helvetica", 11)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)
        self.setLayout(layout)

        self.child_window = None

        lb_label = QLabel("Elija una opción:")
        btn_teas = QPushButton("Realizar Experimento TEAS TimeScan")
        btn_moke = QPushButton("Realizar Experimento MOKE Loop")
        btn_experimentos = QPushButton("Ver Experimentos Realizados")
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
               
        btn_quit = QPushButton("QUIT")
        btn_quit.setStyleSheet("background-color: red; color: white")

        lb_label.setFont(self.fuenteHelvetica)
        btn_teas.setFont(self.fuenteHelvetica)
        btn_moke.setFont(self.fuenteHelvetica)
        btn_experimentos.setFont(self.fuenteHelvetica)
        btn_quit.setFont(self.fuenteHelvetica)

        layout.addWidget(lb_label)
        layout.addWidget(btn_teas)
        layout.addWidget(btn_moke)
        layout.addWidget(btn_experimentos)
        layout.addWidget(linea) 
        layout.addWidget(btn_quit)

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


def main():
    app = QApplication(sys.argv)
    window = MenuInicio()
    window.show()
    sys.exit(app.exec())