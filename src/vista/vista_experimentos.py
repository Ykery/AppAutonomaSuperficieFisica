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


        Ejemplo de uso:

        .. code-block:: python

            ventana_principal.volver()

        """
        self.close()

    def cerrar_ventana(self):
        """
        Cierra la ventana actual.

        Este método cierra la ventana actual cuando es llamado

        Ejemplo de uso:

        .. code-block:: python

            # Cerrar la ventana actual
            self.cerrar_ventana()
        """
        self.close()

    def crear_scroll_area(self):
        """
        Crea un área de desplazamiento con una tabla de experimentos.

        Este método configura un área de desplazamiento que contiene una tabla de experimentos.
        La tabla incluye columnas para el tipo de experimento, fecha de creación, descripción y nombre/ruta.
        La tabla permite la selección de filas, tiene alternancia de colores en las filas y está habilitada para la clasificación.

        :return: Un layout de cuadrícula que contiene la tabla de experimentos.
        :rtype: QGridLayout

        Configura los siguientes widgets:

        - :class:`QGridLayout`: Layout principal que contiene la tabla de experimentos.
        - :class:`QTableWidget`: Tabla para mostrar los experimentos.
        - :class:`QHeaderView`: Configura el modo de ajuste de las secciones del encabezado horizontal y vertical.

        Las señales conectadas incluyen:

        - `self.tb_experimentos.itemClicked`: Conectada a `self.seleccionar_experimento` para manejar la selección de un experimento.
        - `indices_tabla.sectionClicked`: Conectada a `self.manejar_indices_tabla` para manejar la selección de una sección de la tabla.

        Ejemplo de uso:

        .. code-block:: python

            layout = self.crear_scroll_area()
            self.setLayout(layout)
        """
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
        """
        Carga la lista de experimentos en la tabla de experimentos.

        Este método obtiene todos los experimentos utilizando el `ExperimentoDAO` si no están ya cargados,
        y los muestra en la tabla `self.tb_experimentos`. Cada fila de la tabla incluye el tipo de experimento,
        fecha de creación, descripción y ruta del CSV. Además, se añade el ID del experimento como dato asociado
        a cada celda de la fila

        Ejemplo de uso:

        .. code-block:: python

            self.cargar_lista_experimentos()

        """
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
        """
        Filtra la lista de experimentos en la tabla según los filtros aplicados.

        Este método filtra las filas de la tabla `self.tb_experimentos` basándose en el tipo de experimento
        y el rango de fechas proporcionados por los atributos `self.filtro_tipo`, `self.filtro_fecha_desde`,
        y `self.filtro_fecha_hasta`. Las filas que no cumplen con los criterios de filtro son ocultadas

        Ejemplo de uso:

        .. code-block:: python

            self.filtrar_lista_experimentos()

        """
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
        """
        Muestra el ID del experimento en la consola.

        Este método imprime el ID del experimento proporcionado a la consola.

        :param id_experimento: El ID del experimento a mostrar.
        :type id_experimento: i

        Ejemplo de uso:

        .. code-block:: python

            # Mostrar el ID del experimento 123
            self.mostrar_id_experimento(123)

        """
        print(str(id_experimento))

    def seleccionar_experimento(self, id_experimento):
        """
        Selecciona un experimento.

        Este método asigna el ID del experimento proporcionado como el experimento seleccionado
        en la ventana.

        :param id_experimento: El ID del experimento a seleccionar.
        :type id_experimento: i

        Ejemplo de uso:

        .. code-block:: python

            # Seleccionar el experimento con ID 123
            self.seleccionar_experimento(123)

        """
        self.experimento_seleccionado = id_experimento

    def verificar_experimento_seleccionado(self):
        """
        Verifica si se ha seleccionado un experimento.

        Este método verifica si un experimento ha sido seleccionado en la ventana. Si no se ha seleccionado
        ningún experimento, muestra un mensaje de advertencia y devuelve False. De lo contrario, devuelve True.

        :return: True si se ha seleccionado un experimento, False de lo contrario.
        :rtype: bool

        Ejemplo de uso:

        .. code-block:: python

            if self.verificar_experimento_seleccionado():
                # Realizar alguna acción si se ha seleccionado un experimento
                pass
            else:
                # Realizar alguna acción si no se ha seleccionado un experimento
                pass

        """
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
        """
        Filtra la lista de experimentos por tipo.

        Este método establece el tipo de filtro para la lista de experimentos y luego
        filtra la lista en función del tipo especificado.

        :param tipo: El tipo de experimento por el cual filtrar la lista.
        :type tipo: s

        Ejemplo de uso:

        .. code-block:: python

            # Filtrar la lista de experimentos por el tipo "Física"
            ventana.filtrar_por_tipo("Física")

        """
        self.filtro_tipo = tipo
        self.filtrar_lista_experimentos()

    def filtrar_desde(self, fecha):
        """
        Filtra la lista de experimentos desde una fecha específica.

        Este método establece el filtro de fecha de inicio para la lista de experimentos y luego
        filtra la lista para mostrar solo los experimentos realizados a partir de esa fecha.

        :param fecha: La fecha de inicio desde la cual filtrar los experimentos (en formato `datetime.date`).
        :type fecha: datetime.da

        Ejemplo de uso:

        .. code-block:: python

            from datetime import date

            # Filtrar la lista de experimentos desde el 1 de enero de 2023
            ventana.filtrar_desde(date(2023, 1, 1))

        """
        self.filtro_fecha_desde = fecha
        self.filtrar_lista_experimentos()

    def filtrar_hasta(self, fecha):
        """
        Filtra la lista de experimentos hasta una fecha específica.

        Este método establece el filtro de fecha de fin para la lista de experimentos y luego
        filtra la lista para mostrar solo los experimentos realizados hasta esa fecha.

        :param fecha: La fecha de fin hasta la cual filtrar los experimentos (en formato `datetime.date`).
        :type fecha: datetime.da

        Ejemplo de uso:

        .. code-block:: python

            from datetime import date

            # Filtrar la lista de experimentos hasta el 31 de diciembre de 2023
            ventana.filtrar_hasta(date(2023, 12, 31))

        """
        self.filtro_fecha_hasta = fecha
        self.filtrar_lista_experimentos()

    def crear_filtros_tipo_experimento(self):
        """
        Crea un grupo de botones de radio para filtrar por tipo de experimento.

        Este método configura un grupo de botones de radio dentro de un QGroupBox
        para permitir al usuario filtrar los experimentos por tipo: TEAS, MOKE o Todos.

        :return: Un QGroupBox con botones de radio para filtrar por tipo de experimento.
        :rtype: QGroupBox

        Los botones de radio configurados son:

        - `rb_teas`: Filtrar por tipo de experimento TEAS.
        - `rb_moke`: Filtrar por tipo de experimento MOKE.
        - `rb_todos`: Mostrar todos los tipos de experimentos sin filtrar.

        Se conectan señales a los botones de radio para llamar a la función `filtrar_por_tipo`
        con el tipo de experimento correspondiente cuando se selecciona un botón.

        Ejemplo de uso:

        .. code-block:: python

            filtros_tipo_experimento = self.crear_filtros_tipo_experimento()
            layout.addWidget(filtros_tipo_experimento)

        """
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
        """
        Crea un grupo de filtros para seleccionar fechas de inicio y fin.

        Este método configura un grupo de widgets dentro de un QGroupBox
        para permitir al usuario filtrar los experimentos por fechas de inicio y fin.

        :return: Un QGroupBox con filtros para seleccionar fechas de inicio y fin.
        :rtype: QGroupBox

        Los controles configurados son:

        - `btn_desde`: Botón para seleccionar la fecha de inicio.
        - `btn_hasta`: Botón para seleccionar la fecha de fin.
        - `le_desde`: LineEdit para mostrar y editar la fecha de inicio.
        - `le_hasta`: LineEdit para mostrar y editar la fecha de fin.
        - `calendario`: Calendario para seleccionar las fechas.

        Los LineEdit `le_desde` y `le_hasta` están inicialmente deshabilitados y
        se activan cuando se hace clic en los botones correspondientes.

        Se conectan señales a los botones para llamar a la función `control_fechas`
        cuando se hace clic en ellos, para mostrar el calendario y seleccionar la fecha.

        Ejemplo de uso:

        .. code-block:: python

            filtros_fecha = self.crear_filtros_fechas()
            layout.addWidget(filtros_fecha)

        """
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
        """
        Controla la interacción con el calendario para seleccionar fechas.

        Este método muestra el calendario y configura la interacción con los botones
        'Desde' y 'Hasta' para seleccionar fechas de inicio y fin respectivamente.

        :return: El calendario para seleccionar fechas.
        :rtype: QCalendarWidget

        Cuando se hace clic en el botón 'Desde', se muestra el calendario y se conecta
        la señal de clic a la función `mostrar_fecha` con el parámetro "desde".
        De manera similar, cuando se hace clic en el botón 'Hasta', se conecta la señal
        de clic a la función `mostrar_fecha` con el parámetro "hasta".

        Una vez seleccionada la fecha, el calendario se oculta automáticamente.

        Ejemplo de uso:

        .. code-block:: python

            calendario = self.control_fechas()
            calendario.show()

        """
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
        """
        Muestra la fecha seleccionada en el campo correspondiente y filtra según el tipo de fecha.

        Este método recibe la fecha seleccionada y el tipo de fecha ('desde' o 'hasta') y muestra
        la fecha en el campo correspondiente ('Desde' o 'Hasta'). También realiza el filtrado según
        el tipo de fecha seleccionado.

        :param fecha: La fecha seleccionada en el calendario.
        :type fecha: QDate
        :param tipo_fecha: El tipo de fecha ('desde' o 'hasta').
        :type tipo_fecha: s

        Si se selecciona una fecha "hasta" anterior a la fecha "desde", se ajusta la fecha seleccionada
        para que sea igual o posterior a la fecha "desde". Además, se controla que no se pueda seleccionar
        una fecha futura.

        Ejemplo de uso:

        .. code-block:: python

            fecha_seleccionada = QDate.currentDate()
            mostrar_fecha(fecha_seleccionada, "desde")

        """
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
        """
        Formatea la fecha en el formato "dd/MM/yyyy".

        Este método toma un objeto de fecha y lo formatea en el formato "dd/MM/yyyy".

        :param fecha: La fecha a formatear.
        :type fecha: QDate
        :return: La fecha formateada en el formato "dd/MM/yyyy".
        :rtype: str

        Ejemplo de uso:

        .. code-block:: python

            fecha = QDate.currentDate()
            fecha_formateada = formatear_fecha(fecha)

        """
        return fecha.toString("dd/MM/yyyy")

    def crear_zona_acciones(self):
        """
        Crea una zona de acciones con botones personalizados.

        Este método configura una zona de acciones que contiene botones personalizados
        para realizar diferentes acciones, como exportar a PDF, visualizar experimentos
        y cargar configuraciones.

        :return: Un layout que contiene los botones de acción.
        :rtype: QGridLayout

        Configura los siguientes botones:

        - `btn_exportar`: Botón para exportar a PDF.
        - `btn_visualizar`: Botón para visualizar experimentos.
        - `btn_configuraciones`: Botón para cargar configuraciones.

        Se conectan las señales de clic de los botones a sus correspondientes manejadores de eventos.

        Ejemplo de uso:

        .. code-block:: python

            zona_acciones = crear_zona_acciones()
            layout.addWidget(zona_acciones)

        """
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
        """
        Maneja la exportación del experimento actual a un archivo PDF.

        Este método verifica si se ha seleccionado un experimento antes de proceder
        con la exportación a PDF. Si no se ha seleccionado ningún experimento, muestra
        un mensaje de advertencia. Si hay un experimento seleccionado, invoca la función
        para pedir la ruta donde guardar el PDF

        Ejemplo de uso:

        .. code-block:: python

            ventana_principal.manejar_exportar_pdf()

        """
        # Preguntar la ruta donde guardar el pdf
        if not self.verificar_experimento_seleccionado():
            return
        pedir_ruta_exportar_pdf(self, self.experimento_seleccionado)

    def cargar_configuraciones(self):
        """
        Carga las configuraciones para el experimento seleccionado.

        Este método verifica si se ha seleccionado un experimento antes de proceder
        con la carga de configuraciones. Si no se ha seleccionado ningún experimento, muestra
        un mensaje de advertencia. Si hay un experimento seleccionado, determina el tipo de
        experimento y abre una nueva ventana correspondiente para cargar las configuraciones
        específicas

        Ejemplo de uso:

        .. code-block:: python

            ventana_principal.cargar_configuraciones()

        """
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
        """
        Visualiza los resultados del experimento seleccionado.

        Este método verifica si se ha seleccionado un experimento antes de proceder
        con la visualización de resultados. Si no se ha seleccionado ningún experimento, muestra
        un mensaje de advertencia. Si hay un experimento seleccionado, determina el tipo de
        experimento y abre una nueva ventana correspondiente para visualizar los resultados

        Ejemplo de uso:

        .. code-block:: python

            ventana_principal.visualizar_resultados()

        """
        # Preguntar la ruta donde guardar el pdf
        if not self.verificar_experimento_seleccionado():
            return
        experimento = ExperimentoDAO.obtener_por_id(self.experimento_seleccionado)
        if experimento.tipo.lower() == "teas":
            self.abrir_nueva_ventana(TeasGraph(self.experimento_seleccionado, True))
        elif experimento.tipo.lower() == "moke":
            self.abrir_nueva_ventana(MokeGraph(self.experimento_seleccionado, True))

    def abrir_nueva_ventana(self, nueva_ventana):
        """
        Abre una nueva ventana y cierra la ventana actual.

        Este método abre una nueva ventana especificada y cierra la ventana actual.

        :param nueva_ventana: La instancia de la nueva ventana a abrir.
        :type nueva_ventana: QWidg

        Ejemplo de uso:

        .. code-block:: python

            nueva_ventana = MiNuevaVentana()
            ventana_actual.abrir_nueva_ventana(nueva_ventana)

        """
        self.nuevaVentana = nueva_ventana
        self.nuevaVentana.show()
        self.close()


def main():
    """
    Función principal para iniciar la aplicación.

    Esta función crea una aplicación QApplication, instancia la ventana de Experimentos,
    la muestra y ejecuta el bucle de eventos de la aplicación hasta que se cierra la ventana

    Ejemplo de uso:

    .. code-block:: python

        if __name__ == "__main__":
            main()

    """
    app = QApplication(sys.argv)
    experimentos_window = ExperimentosWindow()
    experimentos_window.show()
    sys.exit(app.exec())
