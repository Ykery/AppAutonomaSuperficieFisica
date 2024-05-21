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
        btn_volver = QPushButton("Volver")

        self.main_layout.addLayout(self.crear_scroll_area(), 0, 0, 4, 6)
        self.main_layout.addWidget(self.crear_filtros_tipo_experimento(), 4, 0, 1, 2)
        self.main_layout.addWidget(self.crear_filtros_fechas(), 4, 3, 1, 3)
        self.main_layout.addWidget(btn_volver, 7, 5, 1, 1)
        
        self.setLayout(self.main_layout)


    def crear_scroll_area(self):
        layout = QGridLayout()
        scroll_area_experimentos = QScrollArea()
        scroll_area_experimentos.setBackgroundRole(QPalette.ColorRole.Dark)
        layout.addWidget(scroll_area_experimentos, 0, 0, 4, 6)
        return layout    


    def crear_filtros_tipo_experimento(self):
        #layout = QGridLayout()
        gb_filtrado_tipo_experimento = QGroupBox("Filtrar por tipo experimento")
        radio_buttons_layout = QGridLayout()

        rb_teas = QRadioButton("TEAS")
        rb_moke = QRadioButton("MOKE")
        rb_teas.setChecked(True)

        radio_buttons_layout.addWidget(rb_teas, 0, 0, Qt.AlignmentFlag.AlignCenter)
        radio_buttons_layout.addWidget(rb_moke, 0, 1, Qt.AlignmentFlag.AlignCenter)

        gb_filtrado_tipo_experimento.setLayout(radio_buttons_layout)
        return gb_filtrado_tipo_experimento


    def crear_filtros_fechas(self):
        layout = QGridLayout()
        gb_filtrado_fecha = QGroupBox("Filtrar por fecha")
        
        btn_desde = QPushButton("Desde")
        btn_hasta = QPushButton("Hasta")

        le_desde = QLineEdit()
        le_desde.setPlaceholderText("dd/mm/aaaa")
        le_desde.setStyleSheet("background-color: #f0f0f0")
        le_desde.setAlignment(Qt.AlignmentFlag.AlignCenter)
       
        le_hasta = QLineEdit()
        le_hasta.setPlaceholderText("dd/mm/aaaa")
        le_hasta.setStyleSheet("background-color: #f0f0f0")
        le_hasta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        

        layout.addWidget(btn_desde, 0, 0)
        layout.addWidget(btn_hasta, 1, 0)
        layout.addWidget(le_desde, 0, 1, 1, 2)
        layout.addWidget(le_hasta, 1, 1, 1 ,2)
        
        gb_filtrado_fecha.setLayout(layout)
        return gb_filtrado_fecha




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