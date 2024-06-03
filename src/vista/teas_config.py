import sys
import numpy as np
import random
import os
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import Qwt
from PyQt6.Qwt import *

from src.modelo.dao import *
from src.modelo.clases import *
from src.vista.componentes.displayLCD import DisplayLCDModificado
from src.vista.componentes.thermometer import ThermometerModificado
from src.vista.componentes.combobox import QComboBoxModificado

from src.vista.teas_graph import TeasGraph
import random
from src.vista.componentes.boton import (
    BotonModificado,
    BotonModificadoExit,
    BotonModificadoRun,
)


class TeasWindow(QWidget):
    """
    Ventana principal para la gestión de un sistema TEAS.

    Esta clase crea y configura la interfaz de usuario para gestionar un sistema TEAS,
    incluyendo la configuración de parámetros de DAC, Lock-in, canales y otras configuraciones específicas.

    :param id_experimento: ID opcional del experimento para cargar una configuración previa.
    :type id_experimento: int, optional
    """

    def __init__(self, id_experimento=None):
        """
        Inicializa una nueva instancia de la ventana de gestión de TEAS.

        Este método configura la ventana principal, inicializa las variables necesarias,
        crea y organiza los diferentes widgets y layouts necesarios para la interfaz de usuario.

        :param id_experimento: ID opcional del experimento para cargar una configuración previa.
        :type id_experimento: int, optional

        Configura los siguientes elementos:

        - Estilo de la ventana.
        - Objetos `configuracion` y `experimento` vacíos de las clases `ConfiguracionTeas` y `Experimento`.
        - Título de la ventana.
        - Variables generales `teasDACParams` e `indicesList`.
        - Diseño principal (`QGridLayout`).
        - Fuente utilizada (`QFont`).
        - Listas desplegables para varios parámetros del sistema.
        - Botones de ejecución y cierre con sus respectivos layouts.
        - Conexión de señales de botones a sus manejadores.

        Ejemplo de uso:

        .. code-block:: python

            app = QApplication([])
            window = TeasWindow(id_experimento=1)
            window.show()
            app.exec_()
        """
        super().__init__()
        self.setStyleSheet("background-color: rgb(176, 213, 212); color: black;")

        # Se crea el objeto 'configuracion' vacío y el objeto 'experimento' vacío de la clase ConfiguracionTeas y Experimento
        self.configuracion = ConfiguracionTeas()
        self.experimento = Experimento()

        self.setWindowTitle("TEAS MANAGEMENT")
        # self.setContentsMargins(10, 10, 10, 10)

        # variables generales
        self.teasDACParams = [None] * 6
        self.indicesList = [None] * 6

        self.main_layout = QGridLayout()
        self.fuenteHelvetica = QFont("Helvetica", 11)

        self.scanVrange = [
            " -- Select -- ",
            "20 V",
            "10 V",
            "5 V",
            "4 V",
            "2.5 V",
            "2 V",
            "1.25 V",
            "1 V",
        ]
        self.scanChannelsDAC = [
            " -- Select -- ",
            "Analog Input #1",
            "Analog Input #2",
            "Analog Input #3",
            "Analog Input #4",
        ]
        self.unitsAML = [" -- Select -- ", "mBar", "Pascal", "Torr"]
        self.scanLockinTimeConsVals = [
            " --- Select --- ",
            "1 msec",
            "10 msec",
            "0.1 sec",
            "0.3 sec",
            "1 sec",
            "3 sec",
            "10 sec",
            "30 sec",
            "100 sec",
        ]
        self.scanLockinSensVals = [
            " --- Select --- ",
            "1",
            "2.5",
            "10",
            "25",
            "100",
            "250",
            "1 mV",
            "2.5 mV",
            "10 mV",
            "25 mV",
            "100 mV",
            "250 mV",
        ]

        self.setLayout(self.main_layout)

        btn_run = BotonModificadoRun("Run")
        btn_close = BotonModificadoExit("Close")
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btn_close)
        buttons_layout.addWidget(btn_run)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.main_layout.addWidget(self.create_teas_DAC_box(), 0, 0, 3, 3)
        self.main_layout.addWidget(self.create_teas_lock_in_box(), 0, 3, 2, 1)
        self.main_layout.addWidget(self.create_scan_AML_gauge_box(), 3, 0, 2, 3)
        self.main_layout.addWidget(self.create_teas_time_box(), 2, 3, 3, 1)
        self.main_layout.addWidget(self.create_lock_in_thermo(), 5, 0, 1, 3)
        self.main_layout.addWidget(self.create_teas_channeltron_box(), 5, 3, 1, 1)
        self.main_layout.addWidget(self.teas_system_ID_box(), 6, 0, 1, 2)
        self.main_layout.addWidget(self.set_data_file(), 6, 2, 1, 2)
        self.main_layout.addLayout(buttons_layout, 7, 3, 1, 1)

        print(self.configuracion)

        btn_run.clicked.connect(self.run)
        btn_close.clicked.connect(self.close)

        if id_experimento != None:
            self.cargar_configuracion(id_experimento=id_experimento)

    def run(self):
        """
        Ejecuta el proceso principal de la ventana de gestión de TEAS.

        Este método valida la configuración actual y, si todo es correcto, guarda el experimento
        y su configuración en la base de datos, y luego abre la pantalla de gráficos.

        Realiza las siguientes acciones:

        - Verifica si la ruta del archivo CSV está especificada.
        - Valida los datos de configuración.
        - Establece el tipo de experimento como "TEAS".
        - Crea un nuevo registro de experimento en la base de datos.
        - Asocia la configuración con el experimento y guarda la configuración en la base de datos.
        - Abre la pantalla de gráficos para visualizar los resultados.

        Muestra mensajes de error si:

        - No se ha especificado la ruta del archivo CSV (`mostrar_error_ruta_CSV`).
        - Los datos de configuración no son válidos (`mostrar_error_faltan_datos`).

        Ejemplo de uso:

        .. code-block:: python

            window = TeasWindow()
            window.run()
        """

        if not self.experimento.rutaCsv:
            self.mostrar_error_ruta_CSV()
        elif not self.control_validar_datos():
            self.mostrar_error_faltan_datos()
        else:
            self.experimento.tipo = "TEAS"
            self.experimento = ExperimentoDAO.crear(self.experimento)
            self.configuracion.id_experimento = self.experimento.id
            ConfiguracionTeasDAO.crear(self.configuracion)
            self.abrir_pantalla_grafica()

    def mostrar_error(self):
        """
        Muestra un cuadro de diálogo de error con un mensaje de entrada no válido.

        Este método crea y configura una ventana de mensaje de error con un icono crítico,
        un título y un texto de error. La ventana de mensaje se muestra con un botón "Ok".

        Configura los siguientes elementos:

        - Icono del cuadro de diálogo como crítico.
        - Título de la ventana como "Error de Input".
        - Texto del mensaje como "Input selecionado no valido.".
        - Estilo de la fuente con tamaño 12 puntos.
        - Botón "Ok" para cerrar la ventana.

        Ejemplo de uso:

        .. code-block:: python

            window = TeasWindow()
            window.mostrar_error()
        """

        # Crear y configurar la ventana de error
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Input")
        error_dialog.setText("Input selecionado no valido.")
        # aumentar tamaño de la letra
        error_dialog.setStyleSheet("font: 12pt")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        # Mostrar la ventana de error
        error_dialog.exec()

    def mostrar_error_ruta_CSV(self):
        """
        Muestra un cuadro de diálogo de error indicando que se debe ingresar la ruta del archivo CSV.

        Este método crea y configura una ventana de mensaje de error con un ícono crítico,
        un título y un texto de error indicando al usuario que debe ingresar la ruta del archivo CSV.
        La ventana de mensaje se muestra con un botón "Ok".

        Configura los siguientes elementos:

        - Ícono del cuadro de diálogo como crítico.
        - Título de la ventana como "Error de Datafile".
        - Texto del mensaje como "Ingrese la ruta del archivo.".
        - Estilo de la fuente con tamaño 12 puntos.
        - Botón "Ok" para cerrar la ventana.

        Ejemplo de uso:

        .. code-block:: python

            window = TeasWindow()
            window.mostrar_error_ruta_CSV()
        """
        # Crear y configurar la ventana de error
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Datafile")
        error_dialog.setText("Ingrese la ruta del archivo.")
        # aumentar tamaño de la letra
        error_dialog.setStyleSheet("font: 12pt")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        # Mostrar la ventana de error
        error_dialog.exec()

    def mostrar_error_faltan_datos(self):
        """
        Muestra un cuadro de diálogo de error indicando que faltan datos para correr el experimento.

        Este método crea y configura una ventana de mensaje de error con un ícono crítico,
        un título y un texto de error indicando al usuario que deben ingresar todos los datos necesarios
        para correr el experimento. La ventana de mensaje se muestra con un botón "Ok".

        Configura los siguientes elementos:

        - Ícono del cuadro de diálogo como crítico.
        - Título de la ventana como "Error de Datos".
        - Texto del mensaje como "Ingrese todos los datos necesarios para correr el experimento.".
        - Estilo de la fuente con tamaño 12 puntos.
        - Botón "Ok" para cerrar la ventana.

        Ejemplo de uso:

        .. code-block:: python

            window = TeasWindow()
            window.mostrar_error_faltan_datos()
        """

        # Crear y configurar la ventana de error
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Datos")
        error_dialog.setText(
            "Ingrese todos los datos necesarios para correr el experimento."
        )
        # aumentar tamaño de la letra
        error_dialog.setStyleSheet("font: 12pt")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        # Mostrar la ventana de error
        error_dialog.exec()

    def control_validar_datos(self):
        """
        Verifica si se han ingresado todos los datos necesarios para correr el experimento.

        Este método verifica si todos los atributos de configuración necesarios para ejecutar
        el experimento tienen un valor distinto de `None`. Devuelve True si todos los datos
        necesarios están presentes y False en caso contrario.

        Retorna:
        -------
        bool
            True si todos los datos necesarios están presentes, False de lo contrario.

        Ejemplo de uso:

        .. code-block:: python

            window = TeasWindow()
            if window.control_validar_datos():
                window.run()
            else:
                window.mostrar_error_faltan_datos()
        """

        if (
            self.configuracion.dac_input_intensity == None
            or self.configuracion.dac_teas_voltaje_range == None
            or self.configuracion.dac_input_temperature == None
            or self.configuracion.dac_temperature_voltaje_range == None
            or self.configuracion.dac_sampling_rate == None
            or self.configuracion.aml_input_pressure == None
            or self.configuracion.aml_sensitivity == None
            or self.configuracion.aml_presure_units == None
            or self.configuracion.aml_emission_current == None
            or self.configuracion.lock_sensitivity == None
            or self.configuracion.lock_time_constant == None
            or self.configuracion.channeltron_voltage == None
        ):

            return False
        return True

    def create_teas_lock_in_box(self):
        """
        Crea un cuadro de configuración de Lock-in.

        Este método configura un grupo de widgets para la selección de sensibilidad y
        constante de tiempo para un sistema Lock-in.

        :return: Un QGroupBox configurado con varios controles para la configuración de Lock-in.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLabel`: Etiquetas para cada selección.
        - :class:`QComboBoxModificado`: Comboboxes personalizados para seleccionar diferentes parámetros.
        - :class:`QCheckBox`: Checkbox para verificar valores correctos.

        Los controles configurados son:

        - `self.cb_lockinTimeCons`: Selección de constante de tiempo.
        - `self.cb_lockinSens`: Selección de sensibilidad.

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del sistema Lock-in cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            lock_in_box = self.create_teas_lock_in_box()
            layout.addWidget(lock_in_box)
        """

        layout = QVBoxLayout()

        gb_teasLockinBox = QGroupBox("Lock-in settings")
        gb_teasLockinBox.setFont(self.fuenteHelvetica)
        gb_teasLockinBox.setCheckable(True)
        gb_teasLockinBox.setChecked(False)

        lb_sensLabel = QLabel("Sensitivity (/div)")
        lb_timeConsLabel = QLabel("Time constant")

        self.cb_lockinTimeCons = QComboBoxModificado()
        self.cb_lockinSens = QComboBoxModificado()

        self.cb_lockinTimeCons.insertItems(0, self.scanLockinSensVals)
        self.cb_lockinTimeCons.setCurrentIndex(0)
        self.cb_lockinTimeCons.currentTextChanged.connect(
            self.manejar_cb_lockinTimeCons
        )

        self.cb_lockinSens.insertItems(0, self.scanLockinTimeConsVals)
        self.cb_lockinSens.setCurrentIndex(0)
        self.cb_lockinSens.currentTextChanged.connect(self.manejar_cb_lockinSens)


        layout.addWidget(lb_sensLabel)
        layout.addWidget(self.cb_lockinTimeCons)
        layout.addWidget(lb_timeConsLabel)
        layout.addWidget(self.cb_lockinSens)

        gb_teasLockinBox.setLayout(layout)
        return gb_teasLockinBox

    def create_teas_DAC_box(self):
        """
        Crea un cuadro de configuración de selección de canal DAC.

        Este método configura un grupo de widgets para la selección de canales y rangos de voltaje
        para el DAC, así como la tasa de muestreo.

        :return: Un QGroupBox configurado con varios controles para la configuración del DAC.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLabel`: Etiquetas para cada selección.
        - :class:`QComboBoxModificado`: Comboboxes personalizados para seleccionar canales y rangos de voltaje.
        - :class:`QwtSlider`: Slider personalizado para ajustar la tasa de muestreo.
        - :class:`DisplayLCDModificado`: Pantalla LCD para mostrar la tasa de muestreo seleccionada.
        - :class:`QCheckBox`: Checkbox para verificar la configuración.

        Los controles configurados son:

        - `self.cb_teasVrange`: Selección de rango de voltaje para TEAS.
        - `self.cb_tempVrange`: Selección de rango de voltaje para temperatura.
        - `self.cb_teas`: Selección de canal DAC para TEAS.
        - `self.cb_temperature`: Selección de canal DAC para temperatura.
        - `self.slider_samplingRate`: Slider para ajustar la tasa de muestreo.

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del DAC cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            dac_box = self.create_teas_DAC_box()
            layout.addWidget(dac_box)
        """

        layout = QGridLayout()

        gb_teasDACbox = QGroupBox("DAC channel selection")

        gb_teasDACbox.setCheckable(True)
        gb_teasDACbox.setChecked(False)

        gb_teasDACbox.setFont(self.fuenteHelvetica)

        self.cb_teasVrange = QComboBoxModificado()
        self.cb_tempVrange = QComboBoxModificado()
        self.cb_teas = QComboBoxModificado()
        self.cb_temperature = QComboBoxModificado()

        lb_teasLabel = QLabel("TEAS intensity:")
        lb_teasVrangeLabel = QLabel("TEAS DAC Voltage range:")
        lb_temperatureLabel = QLabel("Sample temperature:")
        lb_tempVrangeLabel = QLabel("Temperature DAC Voltage range:")
        lb_samplingRateLabel = QLabel("Sampling Rate (kHz):")

        self.slider_samplingRate = Qwt.QwtSlider()

        lcd_samplingRateDisplay = DisplayLCDModificado()

        self.slider_samplingRate.valueChanged.connect(self.manejar_silder_samplingRate)
        self.slider_samplingRate.valueChanged.connect(lcd_samplingRateDisplay.display)


        self.cb_teas.insertItems(0, self.scanChannelsDAC)
        self.cb_teas.currentTextChanged.connect(
            lambda texto: self.manejar_cb_teas(texto)
        )

        self.cb_teasVrange.insertItems(0, self.scanVrange)
        self.cb_teasVrange.setCurrentIndex(0)
        self.cb_teasVrange.currentIndexChanged.connect(self.set_DAC_parameters)
        self.cb_teasVrange.currentTextChanged.connect(self.manejar_cb_teasVrange)

        self.cb_temperature.insertItems(0, self.scanChannelsDAC)
        self.cb_temperature.setCurrentIndex(0)
        self.cb_temperature.currentTextChanged.connect(
            lambda texto: self.manejar_cb_temperature(texto)
        )

        self.cb_tempVrange.insertItems(0, self.scanVrange)
        self.cb_tempVrange.setCurrentIndex(0)
        self.cb_tempVrange.currentIndexChanged.connect(self.set_DAC_parameters)
        self.cb_tempVrange.currentTextChanged.connect(self.manejar_cb_tempVrange)

        self.slider_samplingRate.setOrientation(Qt.Orientation.Horizontal)
        self.slider_samplingRate.setScalePosition(
            Qwt.QwtSlider.ScalePosition.TrailingScale
        )
        self.slider_samplingRate.setTrough(True)
        self.slider_samplingRate.setGroove(True)

        self.slider_samplingRate.setSpacing(10)
        self.slider_samplingRate.setHandleSize(QSize(30, 16))
        self.slider_samplingRate.setScale(0, 10.0)
        self.slider_samplingRate.setTotalSteps(100)
        self.slider_samplingRate.setWrapping(False)
        self.slider_samplingRate.setScaleMaxMinor(8)

        layout.addWidget(lb_teasLabel, 0, 0, 1, 2)
        layout.addWidget(self.cb_teas, 1, 0, 1, 2)
        layout.addWidget(lb_teasVrangeLabel, 0, 2, 1, 2)
        layout.addWidget(self.cb_teasVrange, 1, 2, 1, 2)
        layout.addWidget(lb_temperatureLabel, 2, 0, 1, 2)
        layout.addWidget(self.cb_temperature, 3, 0, 1, 2)
        layout.addWidget(lb_tempVrangeLabel, 2, 2, 1, 2)
        layout.addWidget(self.cb_tempVrange, 3, 2, 1, 2)
        layout.addWidget(lb_samplingRateLabel, 4, 0, 1, 1)
        layout.addWidget(self.slider_samplingRate, 5, 0, 1, 3)
        layout.addWidget(lcd_samplingRateDisplay, 5, 3, 1, 1)

        gb_teasDACbox.setLayout(layout)
        return gb_teasDACbox

    def create_scan_AML_gauge_box(self):
        """
        Crea un cuadro de configuración del medidor de presión AML.

        Este método configura un grupo de widgets para la selección de canales, rangos de voltaje,
        sensibilidad del medidor y unidades de presión para el medidor de presión AML, así como
        opciones de corriente de emisión.

        :return: Un QGroupBox configurado con varios controles para la configuración del medidor de presión AML.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLabel`: Etiquetas para cada selección.
        - :class:`QComboBoxModificado`: Comboboxes personalizados para seleccionar canales, rangos de voltaje y unidades de presión.
        - :class:`QLineEdit`: Campo de texto para la sensibilidad del medidor.
        - :class:`QRadioButton`: Botones de radio para seleccionar la corriente de emisión.

        Los controles configurados son:

        - `self.cb_scanAMLGaugeVrangeComboBox`: Selección de rango de voltaje para el medidor de presión.
        - `self.cb_scanAMLGaugeDACcomboBox`: Selección de canal DAC para el medidor de presión.
        - `self.cb_scanAMLUnitsComboBox`: Selección de unidades de presión para el medidor de presión.
        - `self.le_scanSensLineEdit`: Campo de texto para la sensibilidad del medidor.
        - `self.rb_scanEmission_1`: Botón de radio para seleccionar una corriente de emisión de 0.5 mA.
        - `self.rb_scanEmission_2`: Botón de radio para seleccionar una corriente de emisión de 5.0 mA.

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del medidor de presión AML cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            aml_gauge_box = self.create_scan_AML_gauge_box()
            layout.addWidget(aml_gauge_box)
        """

        layout = QGridLayout()

        gb_scanAMLgaugeBox = QGroupBox("AML Pressure gauge")
        gb_scanAMLgaugeBox.setCheckable(True)
        gb_scanAMLgaugeBox.setChecked(False)

        gb_scanAMLgaugeBox.setFont(self.fuenteHelvetica)

        lb_scanBoxLabel = QLabel("Input channel:")
        lb_scanVrangeLabel = QLabel("Channel voltage range (V)     ")
        lb_scanSensLabel = QLabel("Gauge sensitivity (1/[Pres]): ")
        lb_scanAMLunitsLabel = QLabel("Pressure gauge units: ")
        self.lb_emissionLabel = QLabel("Emission current:")

        self.le_scanSensLineEdit = QLineEdit()
        self.le_scanSensLineEdit.textChanged.connect(self.manejar_le_scanSensLineEdit)

        self.rb_scanEmission_1 = QRadioButton("0.5 mA")
        self.rb_scanEmission_2 = QRadioButton("5.0 mA")

        self.rb_scanEmission_1.clicked.connect(self.seleccionar_rb_scanEmission)
        self.rb_scanEmission_2.clicked.connect(self.seleccionar_rb_scanEmission)

        scanEmission_layout = QGridLayout()
        scanEmission_layout.addWidget(
            self.lb_emissionLabel, 0, 0, Qt.AlignmentFlag.AlignCenter
        )
        scanEmission_layout.addWidget(
            self.rb_scanEmission_1, 2, 0, Qt.AlignmentFlag.AlignCenter
        )
        scanEmission_layout.addWidget(
            self.rb_scanEmission_2, 3, 0, Qt.AlignmentFlag.AlignCenter
        )

        self.cb_scanAMLGaugeVrangeComboBox = QComboBoxModificado()
        self.cb_scanAMLGaugeDACcomboBox = QComboBoxModificado()
        self.cb_scanAMLUnitsComboBox = QComboBoxModificado()

        self.cb_scanAMLGaugeDACcomboBox.insertItems(0, self.scanChannelsDAC)
        self.cb_scanAMLGaugeDACcomboBox.setCurrentIndex(0)
        self.cb_scanAMLGaugeDACcomboBox.currentTextChanged.connect(
            lambda texto: self.manejar_cb_scanAMLGaugeDACcomboBox(texto)
        )

        self.cb_scanAMLGaugeVrangeComboBox.insertItems(0, self.scanVrange)
        self.cb_scanAMLGaugeVrangeComboBox.setCurrentIndex(0)
        self.cb_scanAMLGaugeVrangeComboBox.currentIndexChanged.connect(
            self.set_DAC_parameters
        )
        self.cb_scanAMLGaugeVrangeComboBox.currentTextChanged.connect(
            self.manejar_cb_scanAMLGaugeVrangeComboBox
        )

        self.cb_scanAMLUnitsComboBox.insertItems(0, self.unitsAML)
        self.cb_scanAMLUnitsComboBox.setCurrentIndex(0)
        self.cb_scanAMLUnitsComboBox.currentTextChanged.connect(
            self.manejar_cb_scanAMLUnitsComboBox
        )

        layout.addWidget(lb_scanBoxLabel, 0, 0)
        layout.addWidget(self.cb_scanAMLGaugeDACcomboBox, 1, 0)
        layout.addWidget(lb_scanVrangeLabel, 0, 1)
        layout.addWidget(self.cb_scanAMLGaugeVrangeComboBox, 1, 1)
        layout.addWidget(lb_scanSensLabel, 2, 0)
        layout.addWidget(self.le_scanSensLineEdit, 3, 0)
        layout.addWidget(lb_scanAMLunitsLabel, 2, 1)
        layout.addWidget(self.cb_scanAMLUnitsComboBox, 3, 1)

        layout.addLayout(scanEmission_layout, 0, 2, 3, 1)

        gb_scanAMLgaugeBox.setLayout(layout)
        return gb_scanAMLgaugeBox

    def create_teas_time_box(self):
        """
        Crea un cuadro de configuración de tiempo de integración.

        Este método configura un grupo de widgets para la selección de tiempo de integración
        por punto de datos.

        :return: Un QGroupBox configurado con varios controles para la configuración del tiempo de integración.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLabel`: Etiquetas para cada selección.
        - :class:`QwtKnob`: Knob personalizado para ajustar el tiempo de integración.
        - :class:`DisplayLCDModificado`: Pantalla LCD para mostrar el tiempo de integración seleccionado.

        Los controles configurados son:

        - `self.knb_iterTimeKnob`: Knob para ajustar el tiempo de integración.
        - `self.lcd_iterTimerDisplay`: Pantalla LCD para mostrar el tiempo de integración seleccionado.

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del tiempo de integración cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            time_box = self.create_teas_time_box()
            layout.addWidget(time_box)
        """

        layout = QGridLayout()

        gb_teasTimeBox = QGroupBox("Integration time per datapoint")
        # font = QFont()
        # font.setBold(True)
        gb_teasTimeBox.setFont(self.fuenteHelvetica)

        self.knb_iterTimeKnob = Qwt.QwtKnob()
        lb_iterTimeLabel = QLabel()
        lcd_iterTimerDisplay = DisplayLCDModificado()

        self.knb_iterTimeKnob.valueChanged.connect(lcd_iterTimerDisplay.display)
        self.knb_iterTimeKnob.valueChanged.connect(self.manejar_knb_iterTimeKnob)

        layout.addWidget(lb_iterTimeLabel, 0, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.knb_iterTimeKnob, 1, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_iterTimerDisplay, 2, 0, Qt.AlignmentFlag.AlignCenter)

        gb_teasTimeBox.setLayout(layout)
        return gb_teasTimeBox

    def create_lock_in_thermo(self):
        """
    Crea un grupo de widgets para visualizar el nivel de la señal lock-in actual.

    Este método configura un layout de cuadrícula (`QGridLayout`) que contiene un grupo de caja (`QGroupBox`)
    titulado "Current lock-in signal level". Dentro de este grupo de caja se incluye un termómetro 
    (`ThermometerModificado`) que muestra el nivel de la señal lock-in actual. Es sólo para pruebas y no tiene
    funcionalidad real.

    Retorna:
    -------
    QGroupBox
        Un grupo de widgets configurado para visualizar el nivel de la señal lock-in actual.

    Ejemplo de uso:

    .. code-block:: python

        window = TeasWindow()
        lock_in_thermo_box = window.create_lock_in_thermo()
        layout.addWidget(lock_in_thermo_box)
    """


        layout = QGridLayout()

        gb_lockinThermoBox = QGroupBox("Current lock-in signal level")
        gb_lockinThermoBox.setFont(self.fuenteHelvetica)

        thermo_lockinSignal = ThermometerModificado()
        thermo_lockinSignal.setValue(random.randint(0, 100))

        layout.addWidget(thermo_lockinSignal)
        gb_lockinThermoBox.setLayout(layout)
        return gb_lockinThermoBox

    def create_teas_channeltron_box(self):
        """
        Crea un cuadro de configuración para el voltaje de polarización del Channeltron.

        Este método configura un cuadro de grupo con un campo de entrada de línea para
        introducir el voltaje de polarización deseado para el Channeltron.

        :return: Un QGroupBox configurado con un control para la configuración del voltaje del Channeltron.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLineEdit`: Campo de texto para introducir el voltaje de polarización del Channeltron.

        Los controles configurados son:

        - `self.le_teasChanneltronLineEdit`: Campo de texto para introducir el voltaje de polarización del Channeltron.

        Se conecta la señal `textChanged` del campo de texto a su correspondiente manejador para actualizar
        el voltaje del Channeltron cuando el valor introducido cambia.

        Ejemplo de uso:

        .. code-block:: python

            channeltron_box = self.create_teas_channeltron_box()
            layout.addWidget(channeltron_box)
        """

        layout = QGridLayout()

        self.gb_teasChanneltronBox = QGroupBox("Channeltron bias voltage (V)")
        self.gb_teasChanneltronBox.setFont(self.fuenteHelvetica)

        self.le_teasChanneltronLineEdit = QLineEdit()
        self.le_teasChanneltronLineEdit.textChanged.connect(
            self.manejar_le_teasChanneltronLineEdit
        )

        layout.addWidget(self.le_teasChanneltronLineEdit)
        self.gb_teasChanneltronBox.setLayout(layout)
        return self.gb_teasChanneltronBox

    def teas_system_ID_box(self):
        """
        Crea un cuadro de descripción de muestra/sistema.

        Este método configura un cuadro de grupo con un campo de entrada de línea para
        introducir una descripción de la muestra o del sistema TEAS.

        :return: Un QGroupBox configurado con un control para la descripción de muestra/sistema.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLineEdit`: Campo de texto para introducir la descripción de muestra/sistema.

        Los controles configurados son:

        - `self.le_teasSysIDboxLineEdit`: Campo de texto para introducir la descripción de muestra/sistema.

        Se conecta la señal `textChanged` del campo de texto a su correspondiente manejador para actualizar
        la descripción cuando el valor introducido cambia.

        Ejemplo de uso:

        .. code-block:: python

            sys_id_box = self.teas_system_ID_box()
            layout.addWidget(sys_id_box)
        """

        layout = QGridLayout()

        gb_teasSysIDbox = QGroupBox("Sample/system description")
        gb_teasSysIDbox.setFont(self.fuenteHelvetica)

        self.le_teasSysIDboxLineEdit = QLineEdit()
        self.le_teasSysIDboxLineEdit.textChanged.connect(
            self.manejar_le_teasys_ID_box_line_edit
        )

        layout.addWidget(self.le_teasSysIDboxLineEdit)
        gb_teasSysIDbox.setLayout(layout)
        return gb_teasSysIDbox

    def open_file_dialog(self):
        """
        Abre un cuadro de diálogo para seleccionar un archivo de datos.

        Este método abre un cuadro de diálogo del sistema para seleccionar un archivo.
        Después de seleccionar un archivo, actualiza el campo de texto con la ruta del archivo seleccionado.

        :param self: Referencia a la instancia de la clase.
        :type self: object

        """

        file = QFileDialog(self)
        file.setFileMode(QFileDialog.FileMode.AnyFile)
        file.setViewMode(QFileDialog.ViewMode.List)
        file.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        # Si se escribe una ruta y existe, que apareza en el cuadro de diálogo del sistema de gestor de archivos
        self.archivo_incio = self.le_fileLineEdit.text()
        if len(self.archivo_incio) != 0 and os.path.exists(self.archivo_incio):
            file.setDirectory(self.archivo_incio)

        # Comprobar si el diálogo se cerró con una selección válida de archivo
        if file.exec():
            self.nombre_file = file.selectedFiles()[0]
            self.le_fileLineEdit.setText(self.nombre_file)

        file.close()

    def set_data_file(self):
        """
        Configura un cuadro de selección de archivo de datos.

        Este método configura un grupo de widgets para seleccionar un archivo de datos.
        Incluye un campo de texto para mostrar la ruta del archivo seleccionado y un botón de navegación para buscar el archivo.

        :return: Un QGroupBox configurado con un control para la selección de archivo de datos.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLineEdit`: Campo de texto para mostrar la ruta del archivo seleccionado.
        - :class:`boton_modificado`: Botón personalizado para navegar y seleccionar el archivo.

        Los controles configurados son:

        - `self.le_fileLineEdit`: Campo de texto para mostrar la ruta del archivo seleccionado.
        - `btn_browseButton`: Botón para abrir el cuadro de diálogo de selección de archivo.

        Se conecta la señal `clicked` del botón a su correspondiente manejador para abrir el cuadro de diálogo de selección de archivo.
        Se conecta la señal `textChanged` del campo de texto a su correspondiente manejador para manejar cambios en el texto.

        Ejemplo de uso:

        .. code-block:: python

            data_file_box = self.set_data_file()
            layout.addWidget(data_file_box)
        """

        layout = QHBoxLayout()
        gb_dataFileBox = QGroupBox("Datafile selection")
        gb_dataFileBox.setFont(self.fuenteHelvetica)

        self.le_fileLineEdit = QLineEdit()
        self.le_fileLineEdit.setFont(QFont("Helvetica", 9))
        btn_browseButton = BotonModificado("Browse")

        layout.addWidget(self.le_fileLineEdit)
        layout.addWidget(btn_browseButton)

        btn_browseButton.clicked.connect(self.open_file_dialog)
        self.le_fileLineEdit.textChanged.connect(self.manejar_le_fileLineEdit)

        gb_dataFileBox.setLayout(layout)
        return gb_dataFileBox

    def manejar_silder_samplingRate(self, value):
        """
        Maneja el cambio en el valor del control deslizante de la tasa de muestreo DAC.

        Este método actualiza el atributo `dac_sampling_rate` de la configuración
        con el valor proporcionado por el control deslizante de la tasa de muestreo DAC.

        :param value: El nuevo valor seleccionado en el control deslizante.
        :type value: float

        """

        self.configuracion.dac_sampling_rate = value

    def manejar_cb_teas(self, texto):
        """
        Maneja el cambio en la selección de intensidad de entrada TEAS.

        Este método actualiza el atributo `dac_input_intensity` de la configuración
        con el texto seleccionado en el combobox de intensidad de entrada TEAS.

        :param texto: El texto seleccionado en el combobox de intensidad de entrada TEAS.
        :type texto: str
        """

        self.configuracion.dac_input_intensity = texto

    def manejar_cb_teasVrange(self, texto):
        """
        Maneja el cambio en la selección del rango de voltaje TEAS.

        Este método actualiza el atributo `dac_teas_voltaje_range` de la configuración
        con el texto seleccionado en el combobox de rango de voltaje TEAS.

        :param texto: El texto seleccionado en el combobox de rango de voltaje TEAS.
        :type texto: str
        """

        self.configuracion.dac_teas_voltaje_range = texto

    def manejar_cb_temperature(self, texto):
        """
        Maneja el cambio en la selección de la temperatura de entrada.

        Este método actualiza el atributo `dac_input_temperature` de la configuración
        con el texto seleccionado en el combobox de temperatura de entrada.

        :param texto: El texto seleccionado en el combobox de temperatura de entrada.
        :type texto: str
        """

        self.configuracion.dac_input_temperature = texto

    def manejar_cb_tempVrange(self, texto):
        """
        Maneja el cambio en la selección del rango de voltaje de temperatura.

        Este método actualiza el atributo `dac_temperature_voltaje_range` de la configuración
        con el texto seleccionado en el combobox de rango de voltaje de temperatura.

        :param texto: El texto seleccionado en el combobox de rango de voltaje de temperatura.
        :type texto: str
        """

        self.configuracion.dac_temperature_voltaje_range = texto

    def manejar_cb_lockinTimeCons(self, texto):
        """
        Maneja el cambio en la selección de la constante de tiempo del Lock-in.

        Este método actualiza el atributo `lock_time_constant` de la configuración
        con el texto seleccionado en el combobox de constante de tiempo del Lock-in.

        :param texto: El texto seleccionado en el combobox de constante de tiempo del Lock-in.
        :type texto: str
        """

        self.configuracion.lock_time_constant = texto

    def manejar_cb_lockinSens(self, texto):
        """
        Maneja el cambio en la selección de la sensibilidad del Lock-in.

        Este método actualiza el atributo `lock_sensitivity` de la configuración
        con el texto seleccionado en el combobox de sensibilidad del Lock-in.

        :param texto: El texto seleccionado en el combobox de sensibilidad del Lock-in.
        :type texto: str
        """

        self.configuracion.lock_sensitivity = texto

    def manejar_le_scanSensLineEdit(self, texto):
        """
        Maneja el cambio en el valor introducido en el campo de entrada de sensibilidad AML.

        Este método actualiza el atributo `aml_sensitivity` de la configuración
        con el texto introducido en el campo de entrada de sensibilidad AML.

        :param texto: El texto introducido en el campo de entrada de sensibilidad AML.
        :type texto: str
        """

        self.configuracion.aml_sensitivity = texto

    def manejar_cb_scanAMLGaugeVrangeComboBox(self, texto):
        """
        Maneja el cambio en la selección del rango de voltaje del medidor de presión AML.

        Este método actualiza el atributo `aml_voltage_range` de la configuración
        con el texto seleccionado en el combobox de rango de voltaje del medidor de presión AML.

        :param texto: El texto seleccionado en el combobox de rango de voltaje del medidor de presión AML.
        :type texto: str
        """

        self.configuracion.aml_voltage_range = texto

    def seleccionar_rb_scanEmission(self):
        """
        Maneja la selección de la opción de emisión de corriente.

        Este método verifica cuál de las opciones de emisión de corriente está seleccionada y
        llama al método correspondiente para manejar esa selección.

        """

        if self.rb_scanEmission_1.isChecked():
            self.manejar_rb_emision_1()
        elif self.rb_scanEmission_2.isChecked():
            self.manejar_rb_emision_2()

    def manejar_rb_emision_1(self):
        """
        Maneja la selección de la opción de emisión de corriente "0.5 mA".

        Este método actualiza el atributo `aml_emission_current` de la configuración
        para indicar que la corriente de emisión es de "0.5 mA".
        """

        self.configuracion.aml_emission_current = "0.5 mA"

    def manejar_rb_emision_2(self):
        """
        Maneja la selección de la opción de emisión de corriente "5.0 mA".

        Este método actualiza el atributo `aml_emission_current` de la configuración
        para indicar que la corriente de emisión es de "5.0 mA".
        """

        self.configuracion.aml_emission_current = "5.0 mA"

    def manejar_cb_scanAMLGaugeDACcomboBox(self, texto):
        """
        Maneja el cambio en la selección del canal de entrada del medidor de presión AML.

        Este método actualiza el atributo `aml_input_pressure` de la configuración
        con el texto seleccionado en el combobox de canal de entrada del medidor de presión AML.

        :param texto: El texto seleccionado en el combobox de canal de entrada del medidor de presión AML.
        :type texto: str
        """
        self.configuracion.aml_input_pressure = texto

    def manejar_cb_scanAMLUnitsComboBox(self, texto):
        """
        Maneja el cambio en la selección de las unidades de presión del medidor AML.

        Este método actualiza el atributo `aml_presure_units` de la configuración
        con el texto seleccionado en el combobox de unidades de presión del medidor AML.

        :param texto: El texto seleccionado en el combobox de unidades de presión del medidor AML.
        :type texto: str
        """
        self.configuracion.aml_presure_units = texto

    def manejar_knb_iterTimeKnob(self, value):
        """
        Maneja el cambio en el valor del control de ajuste de tiempo de integración.

        Este método actualiza el atributo `integration_time` de la configuración
        con el valor proporcionado por el control de ajuste de tiempo de integración.

        :param value: El nuevo valor seleccionado en el control de ajuste de tiempo de integración.
        :type value: float
        """

        self.configuracion.integration_time = value

    def manejar_le_teasChanneltronLineEdit(self, texto):
        """
        Maneja el cambio en el valor introducido en el campo de entrada del voltaje del Channeltron TEAS.

        Este método actualiza el atributo `channeltron_voltage` de la configuración
        con el texto introducido en el campo de entrada del voltaje del Channeltron TEAS.

        :param texto: El texto introducido en el campo de entrada del voltaje del Channeltron TEAS.
        :type texto: str
        """
        self.configuracion.channeltron_voltage = texto

    def manejar_le_teasys_ID_box_line_edit(self, texto):
        """
        Maneja el cambio en el valor introducido en el campo de entrada de descripción del sistema en el experimento TEAS.

        Este método actualiza el atributo `descripcion` del experimento TEAS
        con el texto introducido en el campo de entrada de descripción del sistema.

        :param texto: El texto introducido en el campo de entrada de descripción del sistema.
        :type texto: str
        """
        self.experimento.descripcion = texto

    def manejar_le_fileLineEdit(self, texto):
        """
        Maneja el cambio en el valor introducido en el campo de entrada de ruta de archivo.

        Este método actualiza el atributo `rutaCsv` del experimento TEAS
        con el texto introducido en el campo de entrada de ruta de archivo.

        :param texto: El texto introducido en el campo de entrada de ruta de archivo.
        :type texto: str
        """
        self.experimento.rutaCsv = texto

    def manejar_cb_teas(self, texto):
        """
        Maneja el cambio en la selección de la intensidad de entrada para TEAS.

        Si se selecciona "-- Select --", no realiza ninguna acción.
        Si el texto seleccionado es diferente al texto actualmente seleccionado en los comboboxes de temperatura y medidor de presión AML,
        actualiza el atributo `dac_input_intensity` de la configuración con el texto seleccionado y lo imprime.
        Si el texto seleccionado es igual al texto actualmente seleccionado en alguno de los comboboxes de temperatura o medidor de presión AML,
        muestra un error.

        :param texto: El texto seleccionado en el combobox de intensidad de entrada para TEAS.
        :type texto: str
        """
        if texto == " -- Select -- ":
            return
        if (
            texto != self.cb_temperature.currentText()
            and texto != self.cb_scanAMLGaugeDACcomboBox.currentText()
        ):
            self.configuracion.dac_input_intensity = texto
            print(texto)
        else:
            self.error_input(self.cb_teas)

    def manejar_cb_scanAMLGaugeDACcomboBox(self, texto):
        """
        Maneja el cambio en la selección del canal de entrada del medidor de presión AML.

        Si se selecciona "-- Select --", no realiza ninguna acción.
        Si el texto seleccionado es diferente al texto actualmente seleccionado en los comboboxes de temperatura y TEAS,
        actualiza el atributo `aml_input_pressure` de la configuración con el texto seleccionado y lo imprime.
        Si el texto seleccionado es igual al texto actualmente seleccionado en alguno de los comboboxes de temperatura o TEAS,
        muestra un error.

        :param texto: El texto seleccionado en el combobox del canal de entrada del medidor de presión AML.
        :type texto: str
        """
        if texto == " -- Select -- ":
            return
        if (
            texto != self.cb_temperature.currentText()
            and texto != self.cb_teas.currentText()
        ):
            self.configuracion.aml_input_pressure = texto
            print(texto)
        else:
            self.error_input(self.cb_scanAMLGaugeDACcomboBox)

    def manejar_cb_temperature(self, texto):
        """
        Maneja el cambio en la selección de la temperatura de entrada.

        Si se selecciona "-- Select --", no realiza ninguna acción.
        Si el texto seleccionado es diferente al texto actualmente seleccionado en los comboboxes de medidor de presión AML y TEAS,
        actualiza el atributo `dac_input_temperature` de la configuración con el texto seleccionado y lo imprime.
        Si el texto seleccionado es igual al texto actualmente seleccionado en alguno de los comboboxes de medidor de presión AML o TEAS,
        muestra un error.

        :param texto: El texto seleccionado en el combobox de temperatura de entrada.
        :type texto: str
        """
        if texto == " -- Select -- ":
            return
        if (
            texto != self.cb_scanAMLGaugeDACcomboBox.currentText()
            and texto != self.cb_teas.currentText()
        ):
            self.configuracion.dac_input_temperature = texto
            print(texto)
        else:
            self.error_input(self.cb_temperature)

    def error_input(self, combobox):
        """
        Muestra un mensaje de error y restablece el combobox seleccionado a su índice inicial.

        Este método muestra un mensaje de error y restablece el índice del combobox especificado a su valor inicial.

        :param combobox: El combobox que se debe restablecer.
        :type combobox: QComboBox
        """
        self.mostrar_error()
        combobox.setCurrentIndex(0)

    def cargar_configuracion(self, id_experimento):
        """
        Carga la configuración asociada a un experimento.

        Este método carga la configuración asociada a un experimento identificado por su ID.
        La configuración cargada se utiliza para establecer los valores de los widgets
        en la interfaz de usuario.

        :param id_experimento: El ID del experimento cuya configuración se va a cargar.
        :type id_experimento: int
        """

        experimento_cargado = ExperimentoDAO.obtener_por_id(id_experimento)

        configuracion_cargada = ConfiguracionTeasDAO.obtener_por_id(id_experimento)
        if configuracion_cargada == None:
            return

        self.cb_teas.setCurrentText(configuracion_cargada.dac_input_intensity)
        self.cb_teasVrange.setCurrentText(configuracion_cargada.dac_teas_voltaje_range)
        self.cb_temperature.setCurrentText(configuracion_cargada.dac_input_temperature)
        self.cb_tempVrange.setCurrentText(
            configuracion_cargada.dac_temperature_voltaje_range
        )
        self.slider_samplingRate.setValue(configuracion_cargada.dac_sampling_rate)
        self.cb_scanAMLGaugeDACcomboBox.setCurrentText(
            configuracion_cargada.aml_input_pressure
        )
        self.cb_scanAMLGaugeVrangeComboBox.setCurrentText(
            configuracion_cargada.aml_voltage_range
        )
        self.le_scanSensLineEdit.setText(configuracion_cargada.aml_sensitivity)
        self.cb_scanAMLUnitsComboBox.setCurrentText(
            configuracion_cargada.aml_presure_units
        )
        if configuracion_cargada.aml_emission_current == "0.5 mA":
            self.rb_scanEmission_1.setChecked(True)
            self.configuracion.aml_emission_current = "0.5 mA"
        if configuracion_cargada.aml_emission_current == "5.0 mA":
            self.rb_scanEmission_2.setChecked(True)
            self.configuracion.aml_emission_current = "5.0 mA"
        self.knb_iterTimeKnob.setValue(configuracion_cargada.integration_time)
        self.le_teasChanneltronLineEdit.setText(
            configuracion_cargada.channeltron_voltage
        )
        self.le_teasSysIDboxLineEdit.setText(experimento_cargado.descripcion)
        self.le_fileLineEdit.setText(experimento_cargado.rutaCsv)
        self.cb_lockinTimeCons.setCurrentText(configuracion_cargada.lock_time_constant)
        self.cb_lockinSens.setCurrentText(configuracion_cargada.lock_sensitivity)

    def set_DAC_parameters(self):
        """
        .. note::

            **IMPORTANTE**
            Este codigo sólo es un ejemplo adaptado de la clase "configscan.cpp", no es funcional.

        Configura los parámetros DAC en función de las selecciones actuales en los comboboxes.

        Este método configura los parámetros DAC en función de las selecciones actuales
        en los comboboxes de voltaje de TEAS, medidor de presión AML y voltaje de temperatura.
        Los parámetros configurados se almacenan en el atributo `teasDACParams` de la clase.

        Se asignan valores específicos de acuerdo con los índices seleccionados en los comboboxes.
        Cada combobox tiene una serie de opciones predefinidas que determinan el rango de valores
        para los parámetros de los DAC.

        """

        k = self.cb_teasVrange.currentIndex()
        m = self.cb_scanAMLGaugeVrangeComboBox.currentIndex()
        n = self.cb_tempVrange.currentIndex()

        if k == 1:
            self.teasDACParams[0] = 0.0
            self.teasDACParams[1] = 20.0

        elif k == 2:
            self.teasDACParams[0] = -10.0
            self.teasDACParams[1] = 10.0

        elif k == 3:
            self.teasDACParams[0] = -5.0
            self.teasDACParams[1] = 5.0

        elif k == 4:
            self.teasDACParams[0] = -4.0
            self.teasDACParams[1] = 4.0

        elif k == 5:
            self.teasDACParams[0] = -2.5
            self.teasDACParams[1] = 2.5

        elif k == 6:
            self.teasDACParams[0] = -2.0
            self.teasDACParams[1] = 2.0

        elif k == 7:
            self.teasDACParams[0] = -1.25
            self.teasDACParams[1] = 1.25

        elif k == 8:
            self.teasDACParams[0] = -1.0
            self.teasDACParams[1] = 1.0

        if m == 1:
            self.teasDACParams[2] = 0.0
            self.teasDACParams[3] = 20.0

        elif m == 2:
            self.teasDACParams[2] = -10.0
            self.teasDACParams[3] = 10.0

        elif m == 3:
            self.teasDACParams[2] = -5.0
            self.teasDACParams[3] = 5.0

        elif m == 4:
            self.teasDACParams[2] = -4.0
            self.teasDACParams[3] = 4.0

        elif m == 5:
            self.teasDACParams[2] = -2.5
            self.teasDACParams[3] = 2.5

        elif m == 6:
            self.teasDACParams[2] = -2.0
            self.teasDACParams[3] = 2.0

        elif m == 7:
            self.teasDACParams[2] = -1.25
            self.teasDACParams[3] = 1.25

        elif m == 8:
            self.teasDACParams[2] = -1.0
            self.teasDACParams[3] = 1.0

        if n == 1:
            self.teasDACParams[4] = 0.0
            self.teasDACParams[5] = 20.0

        elif n == 2:
            self.teasDACParams[4] = -10.0
            self.teasDACParams[5] = 10.0

        elif n == 3:
            self.teasDACParams[4] = -5.0
            self.teasDACParams[5] = 5.0

        elif n == 4:
            self.teasDACParams[4] = -4.0
            self.teasDACParams[5] = 4.0

        elif n == 5:
            self.teasDACParams[4] = -2.5
            self.teasDACParams[5] = 2.5

        elif n == 6:
            self.teasDACParams[4] = -2.0
            self.teasDACParams[5] = 2.0

        elif n == 7:
            self.teasDACParams[4] = -1.25
            self.teasDACParams[5] = 1.25

        elif n == 8:
            self.teasDACParams[4] = -1.0
            self.teasDACParams[5] = 1.0

    def actualizar_datos(self):
        """
        Actualiza los datos de forma periódica.

        Este método configura un temporizador que desencadena la actualización de datos cada 100 milisegundos.
        Cada vez que se actualizan los datos, se genera un valor aleatorio entre 0 y 100 y se actualiza un termómetro Qwt
        con ese valor.

        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(100)
        import random

        thermo = Qwt.QwtThermo()
        thermo.setValue(random.randint(0, 100))

    def abrir_pantalla_grafica(self):
        """
        Abre una pantalla gráfica para visualizar datos del experimento.

        Este método oculta la ventana actual y crea una nueva instancia de la clase TeasGraph,
        que se utiliza para visualizar los datos del experimento identificado por su ID.
        La nueva ventana gráfica se muestra después de ocultar la ventana actual.

        """
        self.hide()
        self.grafica = TeasGraph(self.experimento.id)
        self.grafica.show()


def main():
    """
    Función principal para iniciar la aplicación Teas.

    Esta función inicializa la conexión con la base de datos, crea una instancia de la aplicación QApplication
    y una instancia de la ventana principal TeasWindow. Luego muestra la ventana principal y ejecuta la aplicación.

    """
    Conexion.iniciar_bbdd()
    app = QApplication(sys.argv)
    teas_window = TeasWindow()
    teas_window.show()
    sys.exit(app.exec())
