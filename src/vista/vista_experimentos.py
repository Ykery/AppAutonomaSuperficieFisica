import sys
from datetime import datetime

from PyQt6 import Qwt
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.Qwt import *

from src.modelo.dao import ExperimentoDAO
from src.utilidades.utilidades import pedir_ruta_exportar_pdf
from src.vista.componentes.boton import BotonModificadoExit, BotonModificadoRun
from src.vista.moke_config import MokeWindow
from src.vista.moke_graph import MokeGraph
from src.vista.teas_config import TeasWindow
from src.vista.teas_graph import TeasGraph


class ExperimentosWindow(QWidget):
    """
    Ventana para mostrar una lista de experimentos realizados.

    Esta ventana proporciona una interfaz para mostrar una lista de experimentos realizados,
    filtrar los experimentos por tipo y fecha, exportar experimentos a PDF, visualizar experimentos
    y cargar configuraciones asociadas a los experimentos.

    :param parent: El widget padre de la ventana.
    :type parent: QWidget
    """

    def __init__(self):
        """
        Inicializa la ventana de Experimentos.

        Se establece el título de la ventana, se configura el diseño principal, se crean los filtros
        para tipo de experimento y fecha, se crea la zona de acciones y se conectan los eventos de los botones.

        :type parent: QWidget
        """
        super().__init__()
        self.setWindowTitle("EXPERIMENTOS REALIZADOS")
        self.experimentos = None
        self.main_layout = QGridLayout()
        self.setStyleSheet("background-color: rgb(176, 213, 212); color: black;")
        btn_volver = BotonModificadoExit("Volver")
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
        btn_volver.clicked.connect(self.volver)

    def volver(self):
        """
        Cierra la ventana actual.

        Este método cierra la ventana actual en la que se encuentra el usuario.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            ventana_principal.volver()

        """
        self.close()

    def cerrar_ventana(self):
        self.close()

    def crear_scroll_area(self):

        layout = QGridLayout()
        self.tb_experimentos = QTableWidget(0, 4)
        self.tb_experimentos.setHorizontalHeaderLabels(
            ["Tipo experimento", "Fecha creación", "Descripción", "Nombre/Ruta"]
        )
        self.tb_experimentos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.tb_experimentos.itemClicked.connect(
            lambda x: self.seleccionar_experimento(x.data(Qt.ItemDataRole.UserRole))
        )

        indices_tabla = self.tb_experimentos.verticalHeader()
        indices_tabla.sectionClicked.connect(self.manejar_indices_tabla)

        self.cargar_lista_experimentos()

        layout.addWidget(self.tb_experimentos, 0, 0, 4, 6)

        ultima_columna = self.tb_experimentos.horizontalHeader()

        for i in range(self.tb_experimentos.columnCount() - 1):
            ultima_columna.setSectionResizeMode(
                i, QHeaderView.ResizeMode.ResizeToContents
            )

        ultima_columna.setSectionResizeMode(
            self.tb_experimentos.columnCount() - 1, QHeaderView.ResizeMode.Stretch
        )

        self.tb_experimentos.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.tb_experimentos.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tb_experimentos.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.tb_experimentos.horizontalHeader().setStretchLastSection(True)

        self.tb_experimentos.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tb_experimentos.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tb_experimentos.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
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
            row = self.tb_experimentos.rowCount()
            self.tb_experimentos.insertRow(row)
            self.tb_experimentos.setItem(row, 0, QTableWidgetItem(experimento.tipo))
            self.tb_experimentos.setItem(
                row,
                1,
                QTableWidgetItem(
                    experimento.fecha_creacion.strftime("%d/%m/%Y - %H:%M:%S")
                ),
            )
            self.tb_experimentos.setItem(
                row, 2, QTableWidgetItem(experimento.descripcion)
            )
            self.tb_experimentos.setItem(row, 3, QTableWidgetItem(experimento.rutaCsv))

            # Añadir el id del experimento como data en toda la fila
            for col in range(self.tb_experimentos.columnCount()):
                self.tb_experimentos.item(row, col).setData(
                    Qt.ItemDataRole.UserRole, experimento.id
                )  # Obtener el id del experimento seleccionado

    def manejar_indices_tabla(self, row):
        """
        Maneja los eventos de clic en los índices de la tabla.

        Este método se encarga de manejar los clics del usuario en los índices verticales
        de la tabla de experimentos. Cuando el usuario hace clic en un índice, se selecciona
        el experimento correspondiente en función del identificador asociado al índice.

        :param int row: El índice de la fila en la tabla donde se hizo clic.

        Este método obtiene el identificador del experimento asociado al índice de la fila
        y lo utiliza para seleccionar dicho experimento mediante el método
        ``seleccionar_experimento``.

        Ejemplo de uso:

        .. code-block:: python

            self.tb_experimentos.verticalHeader().sectionClicked.connect(self.manejar_indices_tabla)
        """
        experiment_id = None
        item = self.tb_experimentos.item(row, 0)
        experiment_id = item.data(Qt.ItemDataRole.UserRole)
        self.seleccionar_experimento(experiment_id)

    def filtrar_lista_experimentos(self):
        for index in range(self.tb_experimentos.rowCount()):
            tipo = self.tb_experimentos.item(index, 0)
            fecha_creacion = self.tb_experimentos.item(index, 1)
            if (
                self.filtro_tipo != None
                and tipo.text().lower() != self.filtro_tipo.lower()
            ):
                self.tb_experimentos.setRowHidden(index, True)
                continue
            if self.filtro_fecha_desde != None and datetime.strptime(
                fecha_creacion.text(), "%d/%m/%Y - %H:%M:%S"
            ) < datetime.combine(self.filtro_fecha_desde, datetime.min.time()):
                self.tb_experimentos.setRowHidden(index, True)
                continue
            if self.filtro_fecha_hasta != None and datetime.strptime(
                fecha_creacion.text(), "%d/%m/%Y - %H:%M:%S"
            ) > datetime.combine(self.filtro_fecha_hasta, datetime.max.time()):
                self.tb_experimentos.setRowHidden(index, True)
                continue
            self.tb_experimentos.setRowHidden(index, False)

    def mostrar_id_experimento(self, id_experimento):
        print(str(id_experimento))

    def seleccionar_experimento(self, id_experimento):
        self.experimento_seleccionado = id_experimento

    def verificar_experimento_seleccionado(self):
        if not self.experimento_seleccionado:
            QMessageBox.warning(
                self,
                "Error",
                "No se ha seleccionado ningún experimento",
                QMessageBox.StandardButton.Ok,
            )
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
        # layout = QGridLayout()
        gb_filtrado_tipo_experimento = QGroupBox("Filtrar por tipo experimento")
        radio_buttons_layout = QGridLayout()

        rb_teas = QRadioButton("TEAS")
        rb_moke = QRadioButton("MOKE")
        rb_todos = QRadioButton("Todo")
        rb_teas.clicked.connect(lambda: self.filtrar_por_tipo("teas"))
        rb_moke.clicked.connect(lambda: self.filtrar_por_tipo("moke"))
        rb_todos.clicked.connect(lambda: self.filtrar_por_tipo(None))
        # rb_teas.setChecked(True)

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
        layout.addWidget(self.le_hasta, 1, 1, 1, 2)

        # Conectamos los botones con el calendario
        self.btn_desde.clicked.connect(self.control_fechas)
        self.btn_hasta.clicked.connect(self.control_fechas)

        gb_filtrado_fecha.setLayout(layout)
        return gb_filtrado_fecha

    def control_fechas(self):

        self.calendario.show()
        self.calendario.setGridVisible(True)
        if self.sender() == self.btn_desde:
            self.calendario.clicked.connect(
                lambda fecha: self.mostrar_fecha(fecha, "desde")
            )
        elif self.sender() == self.btn_hasta:
            self.calendario.clicked.connect(
                lambda fecha: self.mostrar_fecha(fecha, "hasta")
            )

        # self.calendario.clicked.connect(self.mostrar_fecha)
        self.calendario.clicked.connect(self.calendario.hide)
        # eliminar el evento de click para que no se ejecute varias veces
        self.calendario.clicked.connect(self.calendario.clicked.disconnect)

        return self.calendario

    def mostrar_fecha(self, fecha, tipo_fecha):

        # control de fechas para que no se pueda seleccionar una fecha "hasta" anterior a la fecha "desde"
        if tipo_fecha == "hasta":
            fecha_desde = QDate.fromString(self.le_desde.text(), "dd/MM/yyyy")
            if fecha < fecha_desde:
                fecha = fecha_desde

        # control de fechas para que no se pueda seleccionar una fecha futura
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

        # return fecha.toString("dd/MM/yyyy")

    def formatear_fecha(self, fecha):
        return fecha.toString("dd/MM/yyyy")

    def crear_zona_acciones(self):
        layout = QGridLayout()

        btn_exportar = BotonModificadoRun("Exportar a PDF")
        btn_visualizar = BotonModificadoRun("Visualizar experimento")
        btn_configuraciones = BotonModificadoRun("Cargar configuraciones")

        btn_exportar.clicked.connect(self.manejar_exportar_pdf)
        btn_visualizar.clicked.connect(self.visualizar_resultados)
        btn_configuraciones.clicked.connect(self.cargar_configuraciones)

        layout.addWidget(btn_exportar, 0, 0, 1, 2)
        layout.addWidget(btn_visualizar, 0, 2, 1, 2)
        layout.addWidget(btn_configuraciones, 0, 4, 1, 2)
        return layout

    def manejar_exportar_pdf(self):
        # Preguntar la ruta donde guardar el pdf
        if not self.verificar_experimento_seleccionado():
            return
        pedir_ruta_exportar_pdf(self, self.experimento_seleccionado)

    def cargar_configuraciones(self):
        # Preguntar la ruta donde guardar el pdf
        if not self.verificar_experimento_seleccionado():
            return
        if (
            ExperimentoDAO.obtener_por_id(self.experimento_seleccionado).tipo.lower()
            == "teas"
        ):
            self.abrir_nueva_ventana(TeasWindow(self.experimento_seleccionado))
        elif (
            ExperimentoDAO.obtener_por_id(self.experimento_seleccionado).tipo.lower()
            == "moke"
        ):
            self.abrir_nueva_ventana(MokeWindow(self.experimento_seleccionado))

    def visualizar_resultados(self):
        # Preguntar la ruta donde guardar el pdf
        if not self.verificar_experimento_seleccionado():
            return
        experimento = ExperimentoDAO.obtener_por_id(self.experimento_seleccionado)
        if experimento.tipo.lower() == "teas":
            self.abrir_nueva_ventana(TeasGraph(self.experimento_seleccionado, True))
        elif experimento.tipo.lower() == "moke":
            self.abrir_nueva_ventana(MokeGraph(self.experimento_seleccionado, True))

    def abrir_nueva_ventana(self, nueva_ventana):
        self.nuevaVentana = nueva_ventana
        self.nuevaVentana.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    experimentos_window = ExperimentosWindow()
    experimentos_window.show()
    sys.exit(app.exec())
