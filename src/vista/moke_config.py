import os
import random
import sys

import numpy as np
from PyQt6 import QtWidgets, Qwt
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi

from src.modelo.clases import Conexion, ConfiguracionMoke, Experimento
from src.modelo.dao import ConfiguracionMokeDAO, ExperimentoDAO
from src.vista.componentes.boton import (BotonModificado, BotonModificadoExit,
                                         BotonModificadoRun)
from src.vista.componentes.combobox import QComboBoxModificado
from src.vista.componentes.displayLCD import DisplayLCDModificado
from src.vista.componentes.line_edit import LineEditModificado
from src.vista.componentes.thermometer import ThermometerModificado
from src.vista.moke_graph import MokeGraph


class MokeWindow(QWidget):
    def __init__(self, id_experimento=None):
        super().__init__()
        self.configuracion = ConfiguracionMoke()
        self.experimento = Experimento()
        self.setWindowTitle("MOKE LOOP")
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

        self.mokeVRange = [
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
        self.mokeChannelsDAC = [
            " -- Select -- ",
            "Analog Input #1",
            "Analog Input #2",
            "Analog Input #3",
            "Analog Input #4",
        ]
        self.mokeLockinSensVals = [
            " -- Select -- ",
            "1",
            "2.5",
            "10",
            "25",
            "100 ",
            "250 ",
            "1 mV",
            "2.5 mV",
            "10 mV",
            "25 mV",
            "100 mV",
            "250 mV",
        ]
        self.mokeLockinTimeConsVals = [
            " -- Select -- ",
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
        btn_run = BotonModificadoRun("Run")
        btn_run.clicked.connect(self.run)
        btn_close = BotonModificadoExit("Close")
        btn_close.clicked.connect(self.close)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btn_close)
        buttons_layout.addWidget(btn_run)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.create_moke_dac_box(), 0, 0, 3, 3)
        self.main_layout.addWidget(self.create_lock_in_box(), 0, 3, 1, 1)
        self.main_layout.addWidget(self.create_moke_loop_box(), 0, 4, 6, 1)
        self.main_layout.addWidget(self.create_moke_time_box(), 1, 3, 5, 1)
        self.main_layout.addWidget(self.create_lock_in_thermo(), 3, 0, 1, 3)
        self.main_layout.addWidget(self.moke_system_id_box(), 4, 0, 1, 2)
        self.main_layout.addWidget(self.moke_geometry_box(), 4, 2, 1, 1)
        self.main_layout.addWidget(self.set_data_file(), 5, 0, 1, 3)
        self.main_layout.addLayout(buttons_layout, 7, 3, 1, 2)

        if id_experimento != None:
            self.cargar_configuracion(id_experimento=id_experimento)

    def create_moke_dac_box(self):
        """
        Crea un cuadro de selección de canal DAC para el MOKE.

        Este método configura un grupo de widgets para la selección y configuración
        de canales DAC, niveles de DC, rangos de voltaje, temperatura, y tasa de
        muestreo para un sistema de medición MOKE.

        :return: Un QGroupBox configurado con varios controles para la selección de canal DAC.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLabel`: Etiquetas para cada selección.
        - :class:`BotonModificado`: Comboboxes personalizados para seleccionar diferentes parámetros.
        - :class:`Qwt.QwtSlider`: Slider personalizado para ajustar la tasa de muestreo.
        - :class:`DisplayLCDModificado`: Display LCD para mostrar la tasa de muestreo.

        Los controles configurados son:

        - `self.cb_moke_intensity`: Selección de intensidad MOKE.
        - `self.cb_moke_dc_level`: Selección de nivel DC MOKE.
        - `self.cb_moke_voltage_range`: Selección de rango de voltaje MOKE.
        - `self.cb_dc_level_voltage_range`: Selección de rango de voltaje del nivel DC.
        - `self.cb_temperature`: Selección de temperatura de la muestra.
        - `self.cb_tempVrange`: Selección de rango de voltaje para la temperatura.
        - `self.cb_timeFieldDriving`: Selección de corriente de conducción de campo.
        - `self.slider_samplingRate`: Ajuste de la tasa de muestreo (khz).

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del sistema MOKE cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            moke_dac_box = self.create_moke_dac_box()
            layout.addWidget(moke_dac_box)

        """
        layout = QGridLayout()
        gb_MokeDACBox = QGroupBox("DAC channel selection")
        gb_MokeDACBox.setCheckable(True)
        gb_MokeDACBox.setChecked(False)

        self.cb_moke_intensity = QComboBoxModificado()
        self.cb_moke_intensity.insertItems(0, self.mokeChannelsDAC)
        self.cb_moke_intensity.setCurrentIndex(0)
        self.cb_moke_intensity.currentTextChanged.connect(
            lambda texto: self.manejar_cb_moke_intensity(texto)
        )

        self.cb_moke_dc_level = QComboBoxModificado()
        self.cb_moke_dc_level.insertItems(0, self.mokeChannelsDAC)
        self.cb_moke_dc_level.setCurrentIndex(0)
        self.cb_moke_dc_level.currentTextChanged.connect(
            lambda texto: self.manejar_cb_moke_dc_level(texto)
        )

        self.cb_moke_voltage_range = QComboBoxModificado()
        self.cb_moke_voltage_range.insertItems(0, self.mokeVRange)
        self.cb_moke_voltage_range.setCurrentIndex(0)
        self.cb_moke_voltage_range.currentTextChanged.connect(
            self.manejar_cb_moke_volage_range
        )

        self.cb_dc_level_voltage_range = QComboBoxModificado()
        self.cb_dc_level_voltage_range.insertItems(0, self.mokeVRange)
        self.cb_dc_level_voltage_range.setCurrentIndex(0)
        self.cb_dc_level_voltage_range.currentTextChanged.connect(
            self.manejar_cb_dc_level_voltage_range
        )

        self.cb_temperature = QComboBoxModificado()
        self.cb_temperature.insertItems(0, self.mokeChannelsDAC)
        self.cb_temperature.setCurrentIndex(0)
        self.cb_temperature.currentTextChanged.connect(
            lambda texto: self.manejar_cb_temperature(texto)
        )

        self.cb_tempVrange = QComboBoxModificado()
        self.cb_tempVrange.insertItems(0, self.mokeLockinSensVals)
        self.cb_tempVrange.setCurrentIndex(0)
        self.cb_tempVrange.currentTextChanged.connect(
            self.manejar_cb_temp_voltage_range
        )

        self.cb_timeFieldDriving = QComboBoxModificado()
        self.cb_timeFieldDriving.insertItems(0, self.mokeLockinTimeConsVals)
        self.cb_timeFieldDriving.setCurrentIndex(0)
        self.cb_timeFieldDriving.currentTextChanged.connect(
            self.manejar_cb_time_field_driving
        )

        lb_moke_intensity = QLabel("MOKE intensity:")
        lb_moke_voltage_range = QLabel("MOKE Voltage range:")
        lb_moke_dc_level = QLabel("MOKE DC level:")
        lb_dc_level_voltage_range = QLabel("DC level Voltage range:")
        lb_sample_temperature = QLabel("Sample temperature:")
        lb_temperature_voltage_range = QLabel("Temperature Voltage range:")
        lb_field_driving_current = QLabel("Field driving current:")
        lb_samplig_rate = QLabel("Sampling Rate (khz):")

        self.slider_samplingRate = Qwt.QwtSlider()
        lcd_samplingRateDisplay = DisplayLCDModificado(initial_value=0, digit_count=4)
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
        self.slider_samplingRate.valueChanged.connect(self.manejar_value_sampling_rate)
        self.slider_samplingRate.valueChanged.connect(lcd_samplingRateDisplay.display)

        layout.addWidget(lb_moke_intensity, 0, 0, 1, 3)
        layout.addWidget(self.cb_moke_intensity, 1, 0, 1, 3)
        layout.addWidget(lb_moke_voltage_range, 0, 3, 1, 3)
        layout.addWidget(self.cb_moke_voltage_range, 1, 3, 1, 3)
        layout.addWidget(lb_moke_dc_level, 2, 0, 1, 3)
        layout.addWidget(self.cb_moke_dc_level, 3, 0, 1, 3)
        layout.addWidget(lb_dc_level_voltage_range, 2, 3, 1, 3)
        layout.addWidget(self.cb_dc_level_voltage_range, 3, 3, 1, 3)
        layout.addWidget(lb_sample_temperature, 4, 0, 1, 3)
        layout.addWidget(self.cb_temperature, 5, 0, 1, 3)
        layout.addWidget(lb_temperature_voltage_range, 4, 3, 1, 3)
        layout.addWidget(self.cb_tempVrange, 5, 3, 1, 3)
        layout.addWidget(lb_field_driving_current, 6, 0, 1, 3)
        layout.addWidget(self.cb_timeFieldDriving, 7, 0, 1, 3)
        layout.addWidget(lb_samplig_rate, 8, 0, 1, 3)
        layout.addWidget(self.slider_samplingRate, 9, 0, 1, 4)
        layout.addWidget(
            lcd_samplingRateDisplay, 9, 4, 1, 2, Qt.AlignmentFlag.AlignCenter
        )

        gb_MokeDACBox.setLayout(layout)
        return gb_MokeDACBox

    def create_lock_in_box(self):
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

        - `self.cb_sensitivity`: Selección de sensibilidad.
        - `self.cb_time`: Selección de constante de tiempo.

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del sistema Lock-in cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            lock_in_box = self.create_lock_in_box()
            layout.addWidget(lock_in_box)

        """
        layout = QVBoxLayout()

        gb_lock_in_box = QGroupBox(" Lock-in stting ")
        gb_lock_in_box.setCheckable(True)
        gb_lock_in_box.setChecked(False)

        lb_sensitivity = QLabel("Sensitivity (/div)")
        self.cb_sensitivity = QComboBoxModificado()
        self.cb_sensitivity.insertItems(0, self.mokeVRange)
        self.cb_sensitivity.setCurrentIndex(0)
        self.cb_sensitivity.currentTextChanged.connect(self.manejar_cb_sensitivity)

        lb_time = QLabel("Time Constant")
        self.cb_time = QComboBoxModificado()
        self.cb_time.insertItems(0, self.mokeLockinTimeConsVals)
        self.cb_time.setCurrentIndex(0)
        self.cb_time.currentTextChanged.connect(self.manejar_cb_time_constant)

        layout.addWidget(lb_sensitivity)
        layout.addWidget(self.cb_sensitivity)
        layout.addWidget(lb_time)
        layout.addWidget(self.cb_time)

        gb_lock_in_box.setLayout(layout)
        return gb_lock_in_box

    def create_moke_loop_box(self):
        """
        Crea un cuadro de parámetros para el bucle MOKE.

        Este método configura un grupo de widgets para la configuración de los parámetros
        del bucle MOKE, incluyendo el campo magnético, puntos por bucle y número de barridos.

        :return: Un QGroupBox configurado con varios controles para los parámetros del bucle MOKE.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLabel`: Etiquetas para cada parámetro.
        - :class:`Qwt.QwtKnob`: Perillas para ajustar los valores de los parámetros.
        - :class:`DisplayLCDModificado`: Displays LCD para mostrar los valores seleccionados.

        Los controles configurados son:

        - `self.knb_magnetic_field`: Perilla para ajustar el campo magnético (Oe).
        - `self.knb_per_loop`: Perilla para ajustar los puntos por bucle.
        - `self.knb_number_sweeps`: Perilla para ajustar el número de barridos.
        - `lcd_magnetic_Display`: Display LCD para mostrar el valor del campo magnético.
        - `lcd_loop_Display`: Display LCD para mostrar los puntos por bucle.
        - `lcd_sweeps_Display`: Display LCD para mostrar el número de barridos.

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del bucle MOKE cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            moke_loop_box = self.create_moke_loop_box()
            layout.addWidget(moke_loop_box)

        """
        layout = QGridLayout()

        gb_moke_loop = QGroupBox("MOKE loop parameters")

        lb_magnetic = QLabel("Magnetic Field (Oe)")
        self.knb_magnetic_field = Qwt.QwtKnob()
        self.knb_magnetic_field.setScale(0, 600)
        lcd_magnetic_Display = DisplayLCDModificado()

        self.knb_magnetic_field.valueChanged.connect(lcd_magnetic_Display.display)
        self.knb_magnetic_field.valueChanged.connect(self.manejas_magnetic_field)

        lb_loop = QLabel("Points per loop")
        self.knb_per_loop = Qwt.QwtKnob()
        self.knb_per_loop.setScale(0, 500)
        lcd_loop_Display = DisplayLCDModificado()

        self.knb_per_loop.valueChanged.connect(lcd_loop_Display.display)
        self.knb_per_loop.valueChanged.connect(self.manejar_per_loop)

        lb_sweeps = QLabel("Number of sweeps")
        self.knb_number_sweeps = Qwt.QwtKnob()
        self.knb_number_sweeps.setScale(0, 30)
        lcd_sweeps_Display = DisplayLCDModificado()
        self.knb_number_sweeps.valueChanged.connect(lcd_sweeps_Display.display)
        self.knb_number_sweeps.valueChanged.connect(self.manejar_number_sweeps)

        layout.addWidget(lb_magnetic, 0, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.knb_magnetic_field, 1, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_magnetic_Display, 2, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lb_loop, 3, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.knb_per_loop, 4, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_loop_Display, 5, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lb_sweeps, 6, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.knb_number_sweeps, 7, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_sweeps_Display, 8, 0, Qt.AlignmentFlag.AlignCenter)

        gb_moke_loop.setLayout(layout)
        return gb_moke_loop

    def create_moke_time_box(self):
        """
        Crea un cuadro de configuración de intervalos de tiempo para el experimento MOKE.

        Este método configura un grupo de widgets para la selección de tiempos de permanencia
        y tiempos de integración para un experimento MOKE.

        :return: Un QGroupBox configurado con varios controles para los intervalos de tiempo del experimento MOKE.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLabel`: Etiquetas para cada parámetro.
        - :class:`Qwt.QwtKnob`: Perillas para ajustar los valores de los parámetros.
        - :class:`DisplayLCDModificado`: Displays LCD para mostrar los valores seleccionados.

        Los controles configurados son:

        - `self.knb_dweel_time`: Perilla para ajustar el tiempo de permanencia (segundos).
        - `lcd_dweel_Time`: Display LCD para mostrar el valor del tiempo de permanencia.
        - `self.knb_integration_time`: Perilla para ajustar el tiempo de integración (segundos).
        - `lcd_integration_time`: Display LCD para mostrar el valor del tiempo de integración.

        Se conectan varias señales a sus correspondientes manejadores para actualizar
        los parámetros del experimento MOKE cuando los valores seleccionados cambian.

        Ejemplo de uso:

        .. code-block:: python

            moke_time_box = self.create_moke_time_box()
            layout.addWidget(moke_time_box)

        """
        layout = QGridLayout()

        gb_MokeTimeBox = QGroupBox("Time intervals for the experiment")

        lb_dweel_time = QLabel("Dwell Time (sec)")
        self.knb_dweel_time = Qwt.QwtKnob()
        lcd_dweel_Time = DisplayLCDModificado()
        self.knb_dweel_time.valueChanged.connect(lcd_dweel_Time.display)
        self.knb_dweel_time.valueChanged.connect(self.manjar_dwell_time)

        lb_integration_time = QLabel("Integration Time (sec)")
        self.knb_integration_time = Qwt.QwtKnob()
        lcd_integration_time = DisplayLCDModificado()
        self.knb_integration_time.valueChanged.connect(lcd_integration_time.display)
        self.knb_integration_time.valueChanged.connect(self.manejar_integration_time)

        layout.addWidget(lb_dweel_time, 0, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.knb_dweel_time, 1, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_dweel_Time, 2, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lb_integration_time, 3, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.knb_integration_time, 4, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_integration_time, 5, 0, Qt.AlignmentFlag.AlignCenter)

        gb_MokeTimeBox.setLayout(layout)
        return gb_MokeTimeBox

    def create_lock_in_thermo(self):
        """
        Crea un cuadro de visualización del nivel de señal Lock-in actual.

        Este método configura un grupo de widgets para mostrar el nivel de señal Lock-in
        actual usando un termómetro modificado.

        :return: Un QGroupBox configurado con un termómetro para mostrar el nivel de señal Lock-in.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`ThermometerModificado`: Un termómetro personalizado para mostrar el nivel de señal Lock-in.

        Ejemplo de uso:

        .. code-block:: python

            lock_in_thermo_box = self.create_lock_in_thermo()
            layout.addWidget(lock_in_thermo_box)

        """
        layout = QGridLayout()

        gb_lock_in = QGroupBox("Current lock-in signal level")

        thermo_lock_in = ThermometerModificado()

        layout.addWidget(thermo_lock_in)
        gb_lock_in.setLayout(layout)
        return gb_lock_in

    def moke_system_id_box(self):
        """
        Crea un cuadro de descripción para el sistema/muestra en un experimento MOKE.

        Este método configura un grupo de widgets para permitir la entrada y visualización
        de la descripción de la muestra o del sistema utilizado en el experimento MOKE.

        :return: Un QGroupBox configurado con un campo de entrada para la descripción de la muestra/sistema.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QLineEdit`: Un campo de entrada para escribir la descripción de la muestra o sistema.

        Se conecta la señal de cambio de texto del QLineEdit a un manejador para procesar
        cualquier cambio en la descripción.

        Ejemplo de uso:

        .. code-block:: python

            description_box = self.moke_system_id_box()
            layout.addWidget(description_box)

        """
        layout = QGridLayout()
        gb_description = QGroupBox("Sample/system description")

        self.le_description = LineEditModificado()
        self.le_description.textChanged.connect(self.manejar_lb_description)

        layout.addWidget(self.le_description)
        gb_description.setLayout(layout)
        return gb_description

    def moke_geometry_box(self):
        """
        Crea un cuadro de selección de geometría para el experimento MOKE.

        Este método configura un grupo de widgets para permitir la selección de la geometría
        utilizada en el experimento MOKE.

        :return: Un QGroupBox configurado con un combo box para seleccionar la geometría MOKE.
        :rtype: QGroupBox

        Configura los siguientes widgets:

        - :class:`QComboBoxModificado`: Un combo box personalizado para seleccionar la geometría MOKE.

        Se conecta la señal de cambio de texto del combo box a un manejador para procesar
        cualquier cambio en la selección de la geometría.

        Ejemplo de uso:

        .. code-block:: python

            geometry_box = self.moke_geometry_box()
            layout.addWidget(geometry_box)

        """
        layout = QGridLayout()

        gb_moke_geomery = QGroupBox("Moke geometry")

        self.cb_geometry = QComboBoxModificado()
        self.cb_geometry.insertItems(0, self.mokeVRange)
        self.cb_geometry.setCurrentIndex(0)
        self.cb_geometry.currentTextChanged.connect(self.manejar_geometry)

        layout.addWidget(self.cb_geometry)
        gb_moke_geomery.setLayout(layout)
        return gb_moke_geomery

    def open_file_dialog(self):
        """
        Abre un cuadro de diálogo para seleccionar un archivo y actualiza un campo de texto con la ruta del archivo seleccionado.

        Este método utiliza QFileDialog para abrir un cuadro de diálogo que permite al usuario seleccionar un archivo.
        Después de que el usuario haya seleccionado un archivo válido y cerrado el diálogo, la ruta del archivo seleccionado
        se mostrará en el campo de texto especificado.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.open_file_dialog()

        """
        file = QFileDialog(self)
        file.setFileMode(QFileDialog.FileMode.AnyFile)
        file.setViewMode(QFileDialog.ViewMode.List)
        file.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        # Si se escribe una ruta y existe, que apareza en el cuadro de diálogo del sistema de gestor de archivos
        self.archivo_incio = self.le_datafile.text()
        if len(self.archivo_incio) != 0 and os.path.exists(self.archivo_incio):
            file.setDirectory(self.archivo_incio)

        # Comprobar si el diálogo se cerró con una selección válida de archivo
        if file.exec():
            self.nombre_file = file.selectedFiles()[0]
            self.le_datafile.setText(self.nombre_file)

        file.close()

    def set_data_file(self):
        """
        Configura un campo de texto para la selección de un archivo de datos y un botón para abrir un cuadro de diálogo de selección de archivo.

        Este método crea un grupo de widgets que incluye un campo de texto para mostrar la ruta del archivo de datos seleccionado
        y un botón "Browse" para abrir un cuadro de diálogo de selección de archivo. Cuando se selecciona un archivo en el cuadro de
        diálogo y se cierra, la ruta del archivo seleccionado se muestra en el campo de texto.

        :return: Un QGroupBox configurado con un campo de texto y un botón para la selección de un archivo de datos.
        :rtype: QGroupBox

        Ejemplo de uso:

        .. code-block:: python

            datafile_box = self.set_data_file()
            layout.addWidget(datafile_box)

        """
        layout = QHBoxLayout()

        gb_datafile_selection = QGroupBox("Datafile selection")

        self.le_datafile = LineEditModificado()
        self.le_datafile.textChanged.connect(self.manejar_le_datafile)
        btn_browse_button = BotonModificado("Browse")
        btn_browse_button.clicked.connect(self.open_file_dialog)

        layout.addWidget(self.le_datafile)
        layout.addWidget(btn_browse_button)

        gb_datafile_selection.setLayout(layout)
        return gb_datafile_selection

    def mostrar_error(self):
        """
        Muestra un cuadro de diálogo de error con un mensaje específico.

        Este método crea un cuadro de diálogo de error utilizando QMessageBox con un ícono de error,
        un título específico, un mensaje de error y un botón "Ok" para cerrar el cuadro de diálogo.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.mostrar_error()

        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Input")
        error_dialog.setText("Input selecionado no valido.")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()

    def mostrar_error_ruta_CSV(self):
        """
        Muestra un cuadro de diálogo de error indicando que la ruta del archivo CSV no ha sido ingresada.

        Este método crea un cuadro de diálogo de error utilizando QMessageBox con un ícono de error,
        un título específico, un mensaje indicando que la ruta del archivo CSV no ha sido ingresada y un botón "Ok"
        para cerrar el cuadro de diálogo.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.mostrar_error_ruta_CSV()

        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Datafile")
        error_dialog.setText("Ingrese la ruta del archivo.")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()

    def mostrar_error_faltan_datos(self):
        """
        Muestra un cuadro de diálogo de error indicando que faltan datos necesarios para correr el experimento.

        Este método crea un cuadro de diálogo de error utilizando QMessageBox con un ícono de error,
        un título específico, un mensaje indicando que faltan datos necesarios para correr el experimento y no incluye
        un botón de cierre ya que se asume que el usuario debe tomar acción y completar los datos faltantes.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.mostrar_error_faltan_datos()

        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Datos")
        error_dialog.setText(
            "Ingrese todos los datos necesarios para correr el experimento."
        )
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()

    def error_input(self, combobox):
        """
        Muestra un cuadro de diálogo de error y restablece un QComboBox.

        Este método muestra un cuadro de diálogo de error utilizando la función `mostrar_error` y luego restablece
        el índice seleccionado del QComboBox pasado como argumento a 0, lo que efectivamente lo restablece a su valor predeterminado.

        :param combobox: El QComboBox que se restablecerá después de mostrar el error.
        :type combobox: QComboBox
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.error_input(my_combobox)

        """
        self.mostrar_error()
        combobox.setCurrentIndex(0)

    def control_validar_datos(self):
        """
        Verifica si todos los datos necesarios están presentes en la configuración.

        Este método verifica si todas las variables de configuración necesarias no son None.
        Si alguna de estas variables es None, devuelve False, lo que indica que falta algún dato.
        En caso contrario, devuelve True, indicando que todos los datos necesarios están presentes.

        :return: True si todos los datos necesarios están presentes, False de lo contrario.
        :rtype: bool

        Ejemplo de uso:

        .. code-block:: python

            if self.control_validar_datos():
                print("Todos los datos necesarios están presentes.")
            else:
                print("Faltan algunos datos necesarios.")

        """
        if (
            self.configuracion.dac_input_intensity == None
            or self.configuracion.dac_dc_level == None
            or self.configuracion.dac_input_temperature == None
            or self.configuracion.dac_voltaje_range == None
            or self.configuracion.dac_dc_voltage_range == None
            or self.configuracion.dac_temperature_voltaje_range == None
            or self.configuracion.dac_field_driving_current == None
            or self.configuracion.lock_sensitivity == None
            or self.configuracion.lock_time_constant == None
            or self.configuracion.geometry == None
        ):
            return False
        return True

    def manejar_cb_moke_volage_range(self, texto):
        """
        Maneja el cambio de selección en el combo box de rango de voltaje MOKE.

        Este método actualiza la variable de configuración `dac_voltaje_range` con el texto seleccionado en el combo box.

        :param texto: El texto seleccionado en el combo box de rango de voltaje MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_moke_volage_range("Alto")

        """
        self.configuracion.dac_voltaje_range = texto

    def manejar_cb_dc_level_voltage_range(self, texto):
        """
        Maneja el cambio de selección en el combo box de rango de voltaje para el nivel de corriente continua (DC) MOKE.

        Este método actualiza la variable de configuración `dac_dc_voltage_range` con el texto seleccionado en el combo box.

        :param texto: El texto seleccionado en el combo box de rango de voltaje para el nivel de corriente continua (DC) MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_dc_level_voltage_range("Alto")

        """
        self.configuracion.dac_dc_voltage_range = texto

    def manejar_cb_temp_voltage_range(self, texto):
        """
        Maneja el cambio de selección en el combo box de rango de voltaje de temperatura MOKE.

        Este método actualiza la variable de configuración `dac_temperature_voltaje_range` con el texto seleccionado en el combo box.

        :param texto: El texto seleccionado en el combo box de rango de voltaje de temperatura MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_temp_voltage_range("Alto")

        """
        self.configuracion.dac_temperature_voltaje_range = texto

    def manejar_cb_time_field_driving(self, texto):
        """
        Maneja el cambio de selección en el combo box de corriente de conducción de campo MOKE.

        Este método actualiza la variable de configuración `dac_field_driving_current` con el texto seleccionado en el combo box.

        :param texto: El texto seleccionado en el combo box de corriente de conducción de campo MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_time_field_driving("Alto")

        """
        self.configuracion.dac_field_driving_current = texto

    def manejar_value_sampling_rate(self, valor):
        """
        Maneja el cambio de valor en la tasa de muestreo del DAC.

        Este método actualiza la variable de configuración `dac_sampling_rate` con el valor seleccionado en el control deslizante.

        :param valor: El valor seleccionado en el control deslizante de la tasa de muestreo del DAC.
        :type valor: int or float
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_value_sampling_rate(10000)

        """
        self.configuracion.dac_sampling_rate = valor

    def manejar_cb_sensitivity(self, texto):
        """
        Maneja el cambio de selección en el combo box de sensibilidad del lock-in.

        Este método actualiza la variable de configuración `lock_sensitivity` con el texto seleccionado en el combo box.

        :param texto: El texto seleccionado en el combo box de sensibilidad del lock-in.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_sensitivity("Alta")

        """
        self.configuracion.lock_sensitivity = texto

    def manejar_cb_time_constant(self, texto):
        """
        Maneja el cambio de selección en el combo box de constante de tiempo del lock-in.

        Este método actualiza la variable de configuración `lock_time_constant` con el texto seleccionado en el combo box.

        :param texto: El texto seleccionado en el combo box de constante de tiempo del lock-in.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_time_constant("Alta")

        """
        self.configuracion.lock_time_constant = texto

    def manejas_magnetic_field(self, valor):
        """
        Maneja el cambio de valor en el campo magnético.

        Este método actualiza la variable de configuración `magnetic_field` con el valor seleccionado en el control de knob.

        :param valor: El valor seleccionado en el control de knob del campo magnético.
        :type valor: int or float
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejas_magnetic_field(500)

        """
        self.configuracion.magnetic_field = valor

    def manejar_per_loop(self, valor):
        """
        Maneja el cambio de valor en el número de puntos por ciclo.

        Este método actualiza la variable de configuración `points_per_loop` con el valor seleccionado en el control de knob.

        :param valor: El valor seleccionado en el control de knob del número de puntos por ciclo.
        :type valor: int or float
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_per_loop(100)

        """
        self.configuracion.points_per_loop = valor

    def manejar_number_sweeps(self, valor):
        """
        Maneja el cambio de valor en el número de barridos.

        Este método actualiza la variable de configuración `number_of_sweeps` con el valor seleccionado en el control de knob.

        :param valor: El valor seleccionado en el control de knob del número de barridos.
        :type valor: int or float
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_number_sweeps(10)

        """
        self.configuracion.number_of_sweeps = valor

    def manjar_dwell_time(self, valor):
        """
        Maneja el cambio de valor en el tiempo de espera.

        Este método actualiza la variable de configuración `dwell_time` con el valor seleccionado.

        :param valor: El valor seleccionado para el tiempo de espera.
        :type valor: int or float
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manjar_dwell_time(5)

        """
        self.configuracion.dwell_time = valor

    def manejar_integration_time(self, valor):
        """
        Maneja el cambio de valor en el tiempo de integración.

        Este método actualiza la variable de configuración `integration_time` con el valor seleccionado.

        :param valor: El valor seleccionado para el tiempo de integración.
        :type valor: int or float
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_integration_time(10)

        """
        self.configuracion.integration_time = valor

    def manejar_lb_description(self, texto):
        """
        Maneja el cambio de texto en la descripción del experimento.

        Este método actualiza la descripción del experimento con el texto proporcionado, eliminando los espacios en blanco al principio y al final.
        Si el texto está vacío después de quitar los espacios en blanco, se asigna `None` a la descripción del experimento.

        :param texto: El texto de la descripción del experimento.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_lb_description("Descripción del experimento")

        """
        texto = texto.strip()
        if texto == "":
            texto = None
        self.experimento.descripcion = texto

    def manejar_geometry(self, texto):
        """
        Maneja el cambio de selección en el combo box de geometría MOKE.

        Este método actualiza la variable de configuración `geometry` con el texto seleccionado en el combo box.

        :param texto: El texto seleccionado en el combo box de geometría MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_geometry("Circular")

        """
        self.configuracion.geometry = texto

    def manejar_le_datafile(self, texto):
        """
        Maneja el cambio de texto en el campo de ruta de archivo de datos.

        Este método actualiza la ruta del archivo CSV del experimento con el texto proporcionado.

        :param texto: La ruta del archivo CSV de datos del experimento.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_le_datafile("/path/to/datafile.csv")

        """
        self.experimento.rutaCsv = texto

    def manejar_cb_moke_intensity(self, texto):
        """
        Maneja el cambio de texto en el combo box de intensidad MOKE.

        Este método actualiza la configuración de la intensidad de entrada del DAC (Convertidor Digital-Analógico) con el texto seleccionado en el combo box, siempre que el texto seleccionado no sea igual al texto actual en otros combo boxes relevantes.

        :param texto: El texto seleccionado en el combo box de intensidad MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_moke_intensity("Alta")

        """
        if texto == " -- Select -- ":
            return
        if (
            texto != self.cb_moke_dc_level.currentText()
            and texto != self.cb_temperature.currentText()
            and texto != self.cb_timeFieldDriving.currentText()
        ):
            self.configuracion.dac_input_intensity = texto
        else:
            self.error_input(self.cb_moke_intensity)

    def manejar_cb_moke_dc_level(self, texto):
        """
        Maneja el cambio de texto en el combo box de nivel DC MOKE.

        Este método actualiza la configuración del nivel DC del DAC (Convertidor Digital-Analógico) con el texto seleccionado en el combo box, siempre que el texto seleccionado no sea igual al texto actual en otros combo boxes relevantes.

        :param texto: El texto seleccionado en el combo box de nivel DC MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_moke_dc_level("Medio")

        """
        if texto == " -- Select -- ":
            return
        if (
            texto != self.cb_moke_intensity.currentText()
            and texto != self.cb_temperature.currentText()
            and texto != self.cb_timeFieldDriving.currentText()
        ):
            self.configuracion.dac_dc_level = texto
        else:
            self.error_input(self.cb_moke_dc_level)

    def manejar_cb_temperature(self, texto):
        """
        Maneja el cambio de texto en el combo box de temperatura MOKE.

        Este método actualiza la configuración de la temperatura de entrada del DAC (Convertidor Digital-Analógico) con el texto seleccionado en el combo box, siempre que el texto seleccionado no sea igual al texto actual en otros combo boxes relevantes.

        :param texto: El texto seleccionado en el combo box de temperatura MOKE.
        :type texto: str
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.manejar_cb_temperature("Alta")

        """
        if texto == " -- Select -- ":
            return
        if (
            texto != self.cb_moke_intensity.currentText()
            and texto != self.cb_moke_dc_level.currentText()
            and texto != self.cb_timeFieldDriving.currentText()
        ):
            self.configuracion.dac_input_temperature = texto
        else:
            self.error_input(self.cb_temperature)

    def run(self):
        """
        Ejecuta el experimento MOKE.

        Este método verifica si se han proporcionado todos los datos necesarios para ejecutar el experimento MOKE. Si falta algún dato, muestra un mensaje de error correspondiente. Si todos los datos están presentes, crea un nuevo experimento MOKE en la base de datos y abre la pantalla gráfica para visualizar los resultados.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.run()

        """
        if self.experimento.rutaCsv == None:
            self.mostrar_error_ruta_CSV()
        elif self.control_validar_datos() == False:
            self.mostrar_error_faltan_datos()
        else:
            self.experimento.tipo = "MOKE"
            self.experimento = ExperimentoDAO.crear(self.experimento)
            self.configuracion.id_experimento = self.experimento.id
            ConfiguracionMokeDAO.crear(self.configuracion)
            self.abrir_pantalla_grafica()

    def cargar_configuracion(self, id_experimento):
        """
        Carga la configuración de un experimento MOKE desde la base de datos y actualiza los campos del formulario.

        Este método recupera los datos de un experimento y su configuración asociada desde la base de datos usando
        el identificador del experimento. Luego, actualiza los widgets del formulario con los valores recuperados.

        :param id_experimento: Identificador del experimento a cargar.
        :type id_experimento: int

        La configuración cargada incluye los siguientes parámetros:

        - Descripción del experimento.
        - Ruta del archivo de datos.
        - Intensidad MOKE (DAC).
        - Rango de voltaje MOKE (DAC).
        - Nivel DC MOKE (DAC).
        - Rango de voltaje del nivel DC (DAC).
        - Temperatura de entrada (DAC).
        - Rango de voltaje de la temperatura (DAC).
        - Corriente de conducción de campo (DAC).
        - Sensibilidad del Lock-in.
        - Constante de tiempo del Lock-in.
        - Campo magnético.
        - Puntos por bucle.
        - Número de barridos.
        - Tiempo de permanencia.
        - Tiempo de integración.
        - Geometría.
        - Tasa de muestreo (DAC).

        Ejemplo de uso:

        .. code-block:: python

            self.cargar_configuracion(123)

        """
        experimento_cargado = ExperimentoDAO.obtener_por_id(id_experimento)
        configuracion_cargada = ConfiguracionMokeDAO.obtener_por_id(id_experimento)

        if configuracion_cargada == None:
            return
        self.le_description.setText(experimento_cargado.descripcion)
        self.le_datafile.setText(experimento_cargado.rutaCsv)
        self.cb_moke_intensity.setCurrentText(configuracion_cargada.dac_input_intensity)
        self.cb_moke_voltage_range.setCurrentText(
            configuracion_cargada.dac_voltaje_range
        )
        self.cb_moke_dc_level.setCurrentText(configuracion_cargada.dac_dc_level)
        self.cb_dc_level_voltage_range.setCurrentText(
            configuracion_cargada.dac_dc_voltage_range
        )
        self.cb_temperature.setCurrentText(configuracion_cargada.dac_input_temperature)
        self.cb_tempVrange.setCurrentText(
            configuracion_cargada.dac_temperature_voltaje_range
        )
        self.cb_timeFieldDriving.setCurrentText(
            configuracion_cargada.dac_field_driving_current
        )
        self.cb_sensitivity.setCurrentText(configuracion_cargada.lock_sensitivity)
        self.cb_time.setCurrentText(configuracion_cargada.lock_time_constant)
        self.knb_magnetic_field.setValue(configuracion_cargada.magnetic_field)
        self.knb_per_loop.setValue(configuracion_cargada.points_per_loop)
        self.knb_number_sweeps.setValue(configuracion_cargada.number_of_sweeps)
        self.knb_dweel_time.setValue(configuracion_cargada.dwell_time)
        self.knb_integration_time.setValue(configuracion_cargada.integration_time)
        self.cb_geometry.setCurrentText(configuracion_cargada.geometry)
        self.slider_samplingRate.setValue(configuracion_cargada.dac_sampling_rate)

    def abrir_pantalla_grafica(self):
        """
        Abre la pantalla gráfica para visualizar los resultados del experimento MOKE.

        Este método oculta la ventana actual y muestra la pantalla gráfica que visualiza los resultados del experimento MOKE.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            self.abrir_pantalla_grafica()

        """
        self.hide()
        self.grafica = MokeGraph(self.experimento.id)
        self.grafica.show()


def main():
    """
    Función principal para iniciar la aplicación MOKE.

    Esta función inicia la conexión con la base de datos, crea una aplicación Qt, muestra la ventana principal de la aplicación y ejecuta el bucle de eventos de la aplicación hasta que se cierra la ventana principal.

    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        main()

    """
    Conexion.iniciar_bbdd()
    app = QApplication([])
    vista_moke_loop = MokeWindow()
    vista_moke_loop.show()
    sys.exit(app.exec())
