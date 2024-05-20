import sys
import numpy as np
import random

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import Qwt
from PyQt6.Qwt import *


class ExperimentosWindow(QWidget):
    
    def __init__(self, ):
        super().__init__()
        self.setWindowTitle("EXPERIMENTOS REALIZADOS")
        self.main_layout = QGridLayout()
        self.fuenteHelvetica = QFont("Helvetica", 11)



    def crear_scroll_area(self):
        scroll_area_experimentos = QScrollArea()
        
        btn_volver = QPushButton("Volver")
        scroll_area_experimentos.setBackgroundRole(QPalette.ColorRole.Dark)
        self.main_layout.addWidget(scroll_area_experimentos, 0, 0, 4, 6)
        self.main_layout.addWidget(btn_volver, 7, 5, 1, 1)
        self.setLayout(self.main_layout)    


    def crear_zona_filtros(self):
        gb_filtrado_fecha = QGroupBox("Filtrar por fecha")
        gb_filtrado_experimento = QGroupBox("Filtrar por tipo experimento")

        rb_teas = QRadioButton("TEAS")
        rb_moke = QRadioButton("MOKE")
        btn_desde = QPushButton("Desde")
        btn_hasta = QPushButton("Hasta")
        pass


    def crear_zona_acciones(self):
        gb_acciones = QGroupBox("Acciones")

        btn_exportar = QPushButton("Exportar a PDF")
        btn_visualizar = QPushButton("Visualizar experimento")
        btn_configuraciones = QPushButton("Cargar configuraciones")
        pass




def main():
    #Conexion.iniciar_bbdd()
    app = QApplication(sys.argv)
    experimentos_window = ExperimentosWindow()
    experimentos_window.show()
    sys.exit(app.exec())