import sys
import numpy as np
import random
from ..modelo.dao import ExperimentoDAO
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import Qwt
from PyQt6.Qwt import *
from datetime import datetime
from threading import Thread
from ..utilidades.utilidades import crear_pdf_experimento, mostrar_pdf

class ExperimentosWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EXPERIMENTOS REALIZADOS")
        self.experimentos = None
        self.main_layout = QGridLayout()
        self.fuenteHelvetica = QFont("Helvetica", 11)
        btn_volver = QPushButton("Volver")
        self.filtro_tipo = None
        self.filtro_fecha_desde = None
        self.filtro_fecha_hasta = None
        self.experimento_seleccionado = None
        self.main_layout.addLayout(self.crear_scroll_area(), 0, 0, 4, 6)
        self.main_layout.addWidget(self.crear_filtros_tipo_experimento(), 4, 0, 1, 2)
        self.main_layout.addWidget(self.crear_filtros_fechas(), 4, 3, 1, 3)
        self.main_layout.addLayout(self.crear_zona_acciones(), 5, 0, 1, 6)
        self.main_layout.addWidget(btn_volver, 7, 5, 1, 1)
        
        self.setLayout(self.main_layout)


    def crear_scroll_area(self):
        layout = QGridLayout()
        self.tb_experimentos = QTableWidget(0, 4) 
        self.tb_experimentos.setHorizontalHeaderLabels(["Tipo experimento", "Fecha creación", "Descripción", "Nombre/Ruta"])
        self.tb_experimentos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tb_experimentos.itemClicked.connect(lambda x: self.seleccionar_experimento(x.data(Qt.ItemDataRole.UserRole)))
        self.cargar_lista_experimentos()

        layout.addWidget(self.tb_experimentos, 0, 0, 4, 6)

        ultima_columna = self.tb_experimentos.horizontalHeader()
        for i in range(self.tb_experimentos.columnCount() - 1):
            ultima_columna.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        ultima_columna.setSectionResizeMode(self.tb_experimentos.columnCount() - 1, QHeaderView.ResizeMode.Stretch)
        
        self.tb_experimentos.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tb_experimentos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tb_experimentos.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tb_experimentos.horizontalHeader().setStretchLastSection(True)
        

        self.tb_experimentos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tb_experimentos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tb_experimentos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tb_experimentos.setAlternatingRowColors(True)
        self.tb_experimentos.setSortingEnabled(True)
        self.tb_experimentos.setShowGrid(True)
        self.tb_experimentos.setGridStyle(Qt.PenStyle.SolidLine)
        self.tb_experimentos.setWordWrap(True)
        self.tb_experimentos.setCornerButtonEnabled(False)
        return layout    


    def cargar_lista_experimentos(self):
        if not self.experimentos:
            self.experimentos = ExperimentoDAO.obtener_todos()

        for experimento in self.experimentos:
            self.tb_experimentos.insertRow(self.tb_experimentos.rowCount())
            self.tb_experimentos.setItem(self.tb_experimentos.rowCount() - 1, 0, QTableWidgetItem(experimento.tipo))
            self.tb_experimentos.setItem(self.tb_experimentos.rowCount() - 1, 1, QTableWidgetItem(experimento.fecha_creacion.strftime("%d/%m/%Y - %H:%M:%S")))
            self.tb_experimentos.setItem(self.tb_experimentos.rowCount() - 1, 2, QTableWidgetItem(experimento.descripcion))
            self.tb_experimentos.setItem(self.tb_experimentos.rowCount() - 1, 3, QTableWidgetItem(experimento.rutaCsv))
            # Añadir el id del experimento como data de toda la fila
            self.tb_experimentos.item(self.tb_experimentos.rowCount() - 1, 0).setData(Qt.ItemDataRole.UserRole, experimento.id)
            self.tb_experimentos.item(self.tb_experimentos.rowCount() - 1, 1).setData(Qt.ItemDataRole.UserRole, experimento.id)
            self.tb_experimentos.item(self.tb_experimentos.rowCount() - 1, 2).setData(Qt.ItemDataRole.UserRole, experimento.id)
            self.tb_experimentos.item(self.tb_experimentos.rowCount() - 1, 3).setData(Qt.ItemDataRole.UserRole, experimento.id)
            
            
    def filtrar_lista_experimentos(self):
        # self.tb_experimentos.clearContents()
        for index in range(self.tb_experimentos.rowCount()):
            tipo = self.tb_experimentos.item(index, 0)
            fecha_creacion = self.tb_experimentos.item(index, 1)
            if self.filtro_tipo != None and tipo.text().lower() != self.filtro_tipo.lower():
                self.tb_experimentos.setRowHidden(index, True)
                continue
            if self.filtro_fecha_desde != None and datetime.strptime(fecha_creacion.text(), "%d/%m/%Y - %H:%M:%S") < datetime.combine(self.filtro_fecha_desde, datetime.min.time()):
                self.tb_experimentos.setRowHidden(index, True)
                continue
            if self.filtro_fecha_hasta != None and datetime.strptime(fecha_creacion.text(), "%d/%m/%Y - %H:%M:%S") > datetime.combine(self.filtro_fecha_hasta, datetime.max.time()):
                self.tb_experimentos.setRowHidden(index, True)
                continue
            self.tb_experimentos.setRowHidden(index, False)
            
    def mostrar_id_experimento(self, id_experimento):
        print(str(id_experimento))


    def seleccionar_experimento(self, id_experimento):
        self.experimento_seleccionado = id_experimento


    def verificar_experimento_seleccionado(self):
        if not self.experimento_seleccionado:
            QMessageBox.warning(self, "Error", "No se ha seleccionado ningún experimento", QMessageBox.StandardButton.Ok)
            return False
        return True


    def filtrar_por_tipo(self, tipo):
        self.filtro_tipo = tipo
        self.filtrar_lista_experimentos()


    def filtrar_desde(self, fecha):
        self.filtro_fecha_desde = fecha
        self.filtrar_lista_experimentos()


    def filtrar_hasta(self, fecha):
        self.filtro_fecha_hasta = fecha
        self.filtrar_lista_experimentos()


    def crear_filtros_tipo_experimento(self):
        #layout = QGridLayout()
        gb_filtrado_tipo_experimento = QGroupBox("Filtrar por tipo experimento")
        radio_buttons_layout = QGridLayout()

        rb_teas = QRadioButton("TEAS")
        rb_moke = QRadioButton("MOKE")
        rb_todos = QRadioButton("Todo")
        rb_teas.clicked.connect(lambda: self.filtrar_por_tipo("teas"))
        rb_moke.clicked.connect(lambda: self.filtrar_por_tipo("moke"))
        rb_todos.clicked.connect(lambda: self.filtrar_por_tipo(None))
        #rb_teas.setChecked(True)

        radio_buttons_layout.addWidget(rb_teas, 0, 0, Qt.AlignmentFlag.AlignCenter)
        radio_buttons_layout.addWidget(rb_moke, 0, 1, Qt.AlignmentFlag.AlignCenter)
        radio_buttons_layout.addWidget(rb_todos, 0, 2, Qt.AlignmentFlag.AlignCenter)

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

        layout.addWidget(self.btn_desde, 0, 0)
        layout.addWidget(self.btn_hasta, 1, 0)
        layout.addWidget(self.le_desde, 0, 1, 1, 2)
        layout.addWidget(self.le_hasta, 1, 1, 1 ,2)

        # Conectamos los botones con el calendario
        self.btn_desde.clicked.connect(self.control_fechas)
        self.btn_hasta.clicked.connect(self.control_fechas)
        
        gb_filtrado_fecha.setLayout(layout)
        return gb_filtrado_fecha

    def lambdarara(self, fecha):
        return self.mostrar_fecha(fecha, "desde")
    

    def control_fechas(self):

        self.calendario.show()
        self.calendario.setGridVisible(True)
        if self.sender() == self.btn_desde:
            self.calendario.clicked.connect(self.lambdarara)
        elif self.sender() == self.btn_hasta:
            self.calendario.clicked.connect(lambda fecha: self.mostrar_fecha(fecha, "hasta"))

        #self.calendario.clicked.connect(self.mostrar_fecha)
        self.calendario.clicked.connect(self.calendario.hide)
        # eliminar el evento de click para que no se ejecute varias veces
        self.calendario.clicked.connect(self.calendario.clicked.disconnect)


        return self.calendario
    

    def mostrar_fecha(self, fecha, tipo_fecha):
        
        #control de fechas para que no se pueda seleccionar una fecha "hasta" anterior a la fecha "desde"
        if tipo_fecha == "hasta":
            fecha_desde = QDate.fromString(self.le_desde.text(), "dd/MM/yyyy")
            if fecha < fecha_desde:
                fecha = fecha_desde

        #control de fechas para que no se pueda seleccionar una fecha futura
        if fecha > QDate.currentDate():
            fecha = QDate.currentDate()

        if tipo_fecha == "desde":
            self.le_desde.setText(self.formatear_fecha(fecha))
            self.le_desde.setStyleSheet("color: black")
            self.filtrar_desde(fecha.toPyDate())
        elif tipo_fecha == "hasta":
            self.le_hasta.setText(self.formatear_fecha(fecha))
            self.le_hasta.setStyleSheet("color: black")       
            self.filtrar_hasta(fecha.toPyDate())  
         
        #return fecha.toString("dd/MM/yyyy")


    def formatear_fecha(self, fecha):
        return fecha.toString("dd/MM/yyyy")
    

    def crear_zona_acciones(self):
        layout = QGridLayout()
    
        btn_exportar = QPushButton("Exportar a PDF")
        btn_visualizar = QPushButton("Visualizar experimento")
        btn_configuraciones = QPushButton("Cargar configuraciones")
        
        btn_exportar.clicked.connect(self.manejar_exportar_pdf)
        
        layout.addWidget(btn_exportar, 0, 0, 1, 2)    
        layout.addWidget(btn_visualizar, 0, 2, 1, 2)
        layout.addWidget(btn_configuraciones, 0, 4, 1, 2)
        return layout


    def manejar_exportar_pdf(self):
        # Preguntar la ruta donde guardar el pdf
        if not self.verificar_experimento_seleccionado():
            return
        pdf_path = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF Files (*.pdf)")
        if pdf_path[0] == "":
            return
        hilo = Thread(target=exportar_mostrar_pdf, args=(self.experimento_seleccionado, pdf_path[0])) # pdf_path[0] es la ruta del pdf
        hilo.start()
        
def exportar_mostrar_pdf(id_experimento, pdf_path):
    crear_pdf_experimento(id_experimento, pdf_path)
    mostrar_pdf(pdf_path)

    
    



def main():
    #Conexion.iniciar_bbdd()
    app = QApplication(sys.argv)
    experimentos_window = ExperimentosWindow()
    experimentos_window.show()
    sys.exit(app.exec())