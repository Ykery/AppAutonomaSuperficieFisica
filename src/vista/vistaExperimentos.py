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
        self.main_layout.addLayout(self.crear_zona_acciones(), 5, 0, 1, 6)
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
        self.calendario = QCalendarWidget()

        self.btn_desde = QPushButton("Desde")
        self.btn_hasta = QPushButton("Hasta")

        self.le_desde = QLineEdit()
        self.le_desde.setPlaceholderText("dd/mm/aaaa")
        self.le_desde.setStyleSheet("background-color: #f0f0f0")
        self.le_desde.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.le_desde.setDisabled(True)

        self.le_hasta = QLineEdit()
        self.le_hasta.setPlaceholderText("dd/mm/aaaa")
        self.le_hasta.setStyleSheet("background-color: #f0f0f0")
        self.le_hasta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.le_hasta.setDisabled(True)



        self.btn_desde.clicked.connect(self.control_fechas)
        self.btn_desde.clicked.connect(self.calendario.hide)

        self.btn_hasta.clicked.connect(self.control_fechas)
        self.btn_hasta.clicked.connect(self.calendario.hide)
        
        



        layout.addWidget(self.btn_desde, 0, 0)
        layout.addWidget(self.btn_hasta, 1, 0)
        layout.addWidget(self.le_desde, 0, 1, 1, 2)
        layout.addWidget(self.le_hasta, 1, 1, 1 ,2)
        
        gb_filtrado_fecha.setLayout(layout)
        return gb_filtrado_fecha




    def crear_zona_acciones(self):
        layout = QGridLayout()
    
        btn_exportar = QPushButton("Exportar a PDF")
        btn_visualizar = QPushButton("Visualizar experimento")
        btn_configuraciones = QPushButton("Cargar configuraciones")
        
        layout.addWidget(btn_exportar, 0, 0, 1, 2)    
        layout.addWidget(btn_visualizar, 0, 2, 1, 2)
        layout.addWidget(btn_configuraciones, 0, 4, 1, 2)
        return layout


    def control_fechas(self):
        self.calendario.setGridVisible(True)
        self.calendario.setGeometry(100, 100, 200, 200)
        self.calendario.clicked.connect(self.mostrar_fecha)
        #self.calendario.clicked.connect(self.calendario.hide)
        return self.calendario
    
    def mostrar_fecha(self, fecha):
        self.le_desde.setText(fecha.toString("dd/MM/yyyy"))
        self.le_hasta.setText(fecha.toString("dd/MM/yyyy"))
        return fecha.toString("dd/MM/yyyy")
    
    
    



def main():
    #Conexion.iniciar_bbdd()
    app = QApplication(sys.argv)
    experimentos_window = ExperimentosWindow()
    experimentos_window.show()
    sys.exit(app.exec())