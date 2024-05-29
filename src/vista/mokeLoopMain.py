import sys
import numpy as np
from PyQt6 import QtWidgets
from PyQt6.uic import loadUi
import os

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from PyQt6 import Qwt
from ..modelo.clases import Conexion, Experimento, ConfiguracionMoke
from ..modelo.dao import ExperimentoDAO, ConfiguracionMokeDAO
import random   


class Display_LCD_modificado(QLCDNumber):
    def __init__(self, initial_value=0, digit_count = None):
        super().__init__()
        self.setStyleSheet("background-color: white; color: black;")
        if digit_count:
            self.setDigitCount(digit_count)
        self.setSmallDecimalPoint(True)
        self.display(initial_value)
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        # Dar un tamaño
        self.setFixedSize(100, 50)

class Thermometer_modificado(Qwt.QwtThermo):
    def __init__(self):
        super().__init__()
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setScalePosition(Qwt.QwtThermo.ScalePosition.TrailingScale)
        colorMap = Qwt.QwtLinearColorMap() 
        colorMap.setColorInterval(Qt.GlobalColor.green, Qt.GlobalColor.red)
        self.setColorMap(colorMap)
        self.setAlarmBrush( Qt.GlobalColor.red)
        self.setAlarmLevel(80)
        self.valor_inicial=random.randint(0, 100)

        self.setValue(Thermometer_modificado.numero_flutuante(self.valor_inicial,4))
        self.temporizador=QTimer() 
        self.temporizador.timeout.connect(lambda: self.setValue(Thermometer_modificado.numero_flutuante(self.valor_inicial,5)))
        self.temporizador.start(50)

    def numero_flutuante(numero,numero2):
        x=random.uniform(-numero2,numero2) + numero
        x_redondeado = round(x, 2)
        return x_redondeado
        


class VistaPrincipal(QWidget):
    def __init__(self,id_experimento=None):
        super().__init__()
        self.configuracion = ConfiguracionMoke()
        self.experimento = Experimento()

        self.setWindowTitle("MOKE LOOP")
        #self.setContentsMargins(5, 5, 5, 5)

        self.main_layout = QGridLayout()
        self.fuenteHelvetica = QFont("Helvetica", 11)
        self.scanVrange = [" -- Select -- ", "20 V", "10 V", "5 V", "4 V", "2.5 V", "2 V", "1.25 V", "1 V"]
        self.scanChannelsDAC = [" -- Select -- ", "Analog Input #1", "Analog Input #2", "Analog Input #3", "Analog Input #4"]
        self.unitsAML = [" -- Select -- ", "mBar", "Pascal", "Torr"]

        self.mokeVRange = [" -- Select -- ", "20 V", "10 V", "5 V", "4 V", "2.5 V", "2 V", "1.25 V", "1 V"]
        self.mokeChannelsDAC = [" -- Select -- ", "Analog Input #1", "Analog Input #2", "Analog Input #3", "Analog Input #4"]
        self.mokeLockinSensVals = [" -- Select -- ", "1", "2.5", "10", "25", "100 ", "250 ", "1 mV", "2.5 mV", "10 mV", "25 mV", "100 mV", "250 mV"]
        self.mokeLockinTimeConsVals = [" -- Select -- ", "1 msec", "10 msec", "0.1 sec", "0.3 sec", "1 sec", "3 sec", "10 sec", "30 sec", "100 sec" ]


        self.setLayout(self.main_layout)

        btn_run = QPushButton("Run")
        btn_close = QPushButton("Close")
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btn_close)
        buttons_layout.addWidget(btn_run)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.main_layout.addWidget(self.createMokeDACBox(), 0, 0, 3, 3)
        self.main_layout.addWidget(self.createLockinBox(), 0, 3, 1, 1)
        self.main_layout.addWidget(self.createMokeLoopBox(), 0, 4, 6, 1)
        self.main_layout.addWidget(self.createMokeTimeBox(), 1, 3, 5, 1)
        self.main_layout.addWidget(self.createLockinThermo(), 3, 0, 1, 3)
        self.main_layout.addWidget(self.mokeSystemIDBox(), 4, 0, 1, 2)
        self.main_layout.addWidget(self.mokeGeometryBox(), 4, 2, 1, 1)
        self.main_layout.addWidget(self.setDataFile(), 5, 0, 1, 3)
        
        self.main_layout.addLayout(buttons_layout, 7, 3, 1, 2)

        btn_close.clicked.connect(self.close)
        btn_run.clicked.connect(self.run)
        
        if id_experimento != None:
            self.cargar_configuracion(id_experimento=id_experimento)
        
    def createMokeDACBox(self):
        
        layout = QGridLayout()
        gb_MokeDACBox = QGroupBox("DAC channel selection")
        gb_MokeDACBox.setCheckable(True)
        gb_MokeDACBox.setChecked(False)

        #Input
        self.cb_moke_intensity = QComboBox()
        self.cb_moke_intensity.insertItems(0, self.mokeChannelsDAC)
        self.cb_moke_intensity.setCurrentIndex(0)
        self.cb_moke_intensity.currentTextChanged.connect(lambda texto: self.manejar_cb_moke_intensity(texto))
        #Input
        self.cb_moke_dc_level = QComboBox()
        self.cb_moke_dc_level.insertItems(0, self.mokeChannelsDAC)
        self.cb_moke_dc_level.setCurrentIndex(0)
        self.cb_moke_dc_level.currentTextChanged.connect(lambda texto: self.manejar_cb_moke_dc_level(texto))

        self.cb_moke_voltage_range = QComboBox()
        self.cb_moke_voltage_range.insertItems(0,self.mokeVRange)
        self.cb_moke_voltage_range.setCurrentIndex(0)
        self.cb_moke_voltage_range.currentTextChanged.connect(self.manejar_cb_moke_volage_range)

        self.cb_dc_level_voltage_range= QComboBox()
        self.cb_dc_level_voltage_range.insertItems(0,self.mokeVRange)
        self.cb_dc_level_voltage_range.setCurrentIndex(0)
        self.cb_dc_level_voltage_range.currentTextChanged.connect(self.manejar_cb_dc_level_voltage_range)
        #Input
        self.cb_temperature = QComboBox()
        self.cb_temperature.insertItems(0,self.mokeChannelsDAC)
        self.cb_temperature.setCurrentIndex(0)
        self.cb_temperature.currentTextChanged.connect(lambda texto: self.manejar_cb_temperature(texto))
        
        self.cb_tempVrange = QComboBox()
        self.cb_tempVrange.insertItems(0,self.mokeLockinSensVals)
        self.cb_tempVrange.setCurrentIndex(0)
        self.cb_tempVrange.currentTextChanged.connect(self.manejar_cb_tempVrange)

        self.cb_timeFieldDriving = QComboBox()
        self.cb_timeFieldDriving.insertItems(0,self.mokeLockinTimeConsVals)
        self.cb_timeFieldDriving.setCurrentIndex(0)
        self.cb_timeFieldDriving.currentTextChanged.connect(self.manejar_cb_timeFieldDriving)

        lb_moke_intensity = QLabel("MOKE intensity:")
        lb_moke_voltage_range = QLabel("MOKE Voltage range:")
        lb_moke_dc_level = QLabel("MOKE DC level:")
        lb_dc_level_voltage_range = QLabel("DC level Voltage range:")
        lb_sample_temperature = QLabel("Sample temperature:")
        lb_temperature_voltage_range = QLabel("Temperature Voltage range:")
        lb_field_driving_current = QLabel("Field driving current:")
        lb_samplig_rate = QLabel("Sampling Rate (khz):")

        #barra
        self.slider_samplingRate = Qwt.QwtSlider()

        #DISPLAY
        lcd_samplingRateDisplay = Display_LCD_modificado(initial_value=0, digit_count=4)

        
        self.slider_samplingRate.setOrientation(Qt.Orientation.Horizontal)
        self.slider_samplingRate.setScalePosition(Qwt.QwtSlider.ScalePosition.TrailingScale)
        self.slider_samplingRate.setTrough(True)
        self.slider_samplingRate.setGroove(True)
        self.slider_samplingRate.setSpacing(10)
        self.slider_samplingRate.setHandleSize(QSize(30, 16))
        self.slider_samplingRate.setScale(0, 10.0) 
        self.slider_samplingRate.setTotalSteps(100)  
        self.slider_samplingRate.setWrapping(False)
        self.slider_samplingRate.setScaleMaxMinor(8)


        #Conexion display con la barra
        self.slider_samplingRate.valueChanged.connect(self.manejar_value_sampling_rate)
        self.slider_samplingRate.valueChanged.connect(lcd_samplingRateDisplay.display)
        layout.addWidget(lb_moke_intensity, 0, 0, 1, 3)
        layout.addWidget(self.cb_moke_intensity, 1, 0, 1, 3)
        layout.addWidget(lb_moke_voltage_range, 0, 3, 1,3)
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
        layout.addWidget(lcd_samplingRateDisplay, 9, 4, 1, 2, Qt.AlignmentFlag.AlignCenter)

        gb_MokeDACBox.setLayout(layout)
        return gb_MokeDACBox
    
    #lock-in settings 
    def createLockinBox(self):
        
        layout = QVBoxLayout()

        gb_lock_in_box = QGroupBox(" Lock-in stting ")
        gb_lock_in_box.setCheckable(True)
        gb_lock_in_box.setChecked(False)

        lb_sensitivity = QLabel("Sensitivity (/div)")
        self.cb_sensitivity = QComboBox()
        self.cb_sensitivity.insertItems(0, self.mokeVRange)
        self.cb_sensitivity.setCurrentIndex(0)
        self.cb_sensitivity.currentTextChanged.connect(self.manejar_cb_sensitivity)

        lb_time = QLabel("Time Constant")
        self.cb_time = QComboBox()
        self.cb_time.insertItems(0, self.mokeLockinTimeConsVals)
        self.cb_time.setCurrentIndex(0)
        self.cb_time.currentTextChanged.connect(self.manejar_cb_time_constant)

        chb_verified = QCheckBox("Check when correct values set")


        layout.addWidget(lb_sensitivity)
        layout.addWidget(self.cb_sensitivity)
        layout.addWidget(lb_time)
        layout.addWidget(self.cb_time)
        layout.addWidget(chb_verified)

        gb_lock_in_box.setLayout(layout)
        return gb_lock_in_box
    
    def createMokeLoopBox(self):
        layout = QGridLayout()

        gb_moke_loop =QGroupBox("MOKE loop parameters")


        lb_magnetic = QLabel("Magnetic Field (Oe)")
        self.knb_magnetic_field = Qwt.QwtKnob()
        self.knb_magnetic_field.setScale(0,600)
        lcd_magnetic_Display = Display_LCD_modificado()

        self.knb_magnetic_field.valueChanged.connect(lcd_magnetic_Display.display)
        self.knb_magnetic_field.valueChanged.connect(self.manejas_magnetic_field)

        lb_loop = QLabel("Points per loop")
        self.knb_per_loop = Qwt.QwtKnob()
        self.knb_per_loop.setScale(0,500)
        lcd_loop_Display = Display_LCD_modificado()

        self.knb_per_loop.valueChanged.connect(lcd_loop_Display.display)
        self.knb_per_loop.valueChanged.connect(self.manejar_per_loop)

        lb_sweeps = QLabel("Number of sweeps")
        self.knb_number_sweeps = Qwt.QwtKnob()
        self.knb_number_sweeps.setScale(0,30)
        lcd_sweeps_Display = Display_LCD_modificado()

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
        
    def createMokeTimeBox(self):
        layout = QGridLayout()

        gb_MokeTimeBox =QGroupBox("Time intervals for the experiment")

        lb_dweel_time = QLabel("Dwell Time (sec)")
        self.knb_dweel_time = Qwt.QwtKnob()
        lcd_dweel_Time = Display_LCD_modificado()
        self.knb_dweel_time.valueChanged.connect(lcd_dweel_Time.display)
        self.knb_dweel_time.valueChanged.connect(self.manjar_dwell_time)


        lb_integration_time = QLabel("Integration Time (sec)")
        self.knb_integration_time = Qwt.QwtKnob()
        lcd_integration_time = Display_LCD_modificado()
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

    def createLockinThermo(self): 
        layout = QGridLayout()

        gb_lock_in = QGroupBox("Current lock-in signal level")

        thermo_lock_in = Thermometer_modificado()

        layout.addWidget(thermo_lock_in)
        gb_lock_in.setLayout(layout)
        return gb_lock_in
      
    def mokeSystemIDBox(self):
        layout = QGridLayout()
        gb_description = QGroupBox("Sample/system description")

        self.le_description = QLineEdit()
        self.le_description.textChanged.connect(self.manejar_lb_description)
        layout.addWidget(self.le_description)
        gb_description.setLayout(layout)
        return gb_description
    
    def mokeGeometryBox(self):
        layout = QGridLayout()

        gb_moke_geomery = QGroupBox("Moke geometry")

        self.cb_geometry = QComboBox()
        self.cb_geometry.insertItems(0, self.mokeVRange)
        self.cb_geometry.setCurrentIndex(0)
        self.cb_geometry.currentTextChanged.connect(self.manejar_geometry)

        layout.addWidget(self.cb_geometry)

        gb_moke_geomery.setLayout(layout)
        return gb_moke_geomery

    #Abre el sistema de gestor de archivos para seleccionar un archivo
    def open_file_dialog(self):
        file = QFileDialog(self)
        file.setFileMode(QFileDialog.FileMode.AnyFile)
        file.setViewMode(QFileDialog.ViewMode.List)
        file.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        
        # Si se escribe una ruta y existe, que apareza en el cuadro de diálogo del sistema de gestor de archivos
        self.archivo_incio = self.le_datafile.text()
        if len(self.archivo_incio) != 0 and os.path.exists(self.archivo_incio):
            file.setDirectory(self.archivo_incio)
       
        #Comprobar si el diálogo se cerró con una selección válida de archivo
        if file.exec():
            self.nombre_file = file.selectedFiles()[0]
            self.le_datafile.setText(self.nombre_file)

        file.close()
        print(file)


    def setDataFile(self):    
        layout = QHBoxLayout()

        gb_datafile_selection = QGroupBox("Datafile selection")

        self.le_datafile = QLineEdit()
        btn_browse_button = QPushButton("Browse")

        layout.addWidget(self.le_datafile)
        layout.addWidget(btn_browse_button)
        btn_browse_button.clicked.connect(self.open_file_dialog)
        self.le_datafile.textChanged.connect(self.manejar_le_datafile)

        gb_datafile_selection.setLayout(layout)
        return gb_datafile_selection 
    
     #función para actualizar los datos del termómetro de forma aleatoria, solo para pruebas
    def termo_dato_aleatorio(self):
        import random
        numero = random.randint(0, 100)
        return numero
    
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de moke intensity, dc level y temperature
    def mostrar_error(self):
        # Crear y configurar la ventana de error
        #error_dialog = QMessageBox().warning(self, "Error de Input", "Input selecdionado no valido.")
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Input")
        error_dialog.setText("Input selecionado no valido.")
        #aumentar tamaño de la letra 
        error_dialog.setStyleSheet("font: 12pt")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok) 
        # Mostrar la ventana de error
        error_dialog.exec()

    def mostrar_error_ruta_CSV(self):
        # Crear y configurar la ventana de error
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Datafile")
        error_dialog.setText("Ingrese la ruta del archivo.")
        #aumentar tamaño de la letra 
        error_dialog.setStyleSheet("font: 12pt")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok) 
        # Mostrar la ventana de error
        error_dialog.exec()

    def mostrar_error_faltan_datos(self):
        # Crear y configurar la ventana de error
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Datos")
        error_dialog.setText("Ingrese todos los datos necesarios para correr el experimento.")
        #aumentar tamaño de la letra 
        error_dialog.setStyleSheet("font: 12pt")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok) 
        # Mostrar la ventana de error
        error_dialog.exec()

    def error_input(self,combobox):
        self.mostrar_error()
        combobox.setCurrentIndex(0)

    #fuincion que se ejecuta para comprobar que todos los datos esten ingresados
    def control_validar_datos(self):
        if  self.configuracion.dac_input_intensity == None or \
            self.configuracion.dac_dc_level == None or \
            self.configuracion.dac_input_temperature == None or \
            self.configuracion.dac_voltaje_range == None or \
            self.configuracion.dac_dc_voltage_range == None or \
            self.configuracion.dac_temperature_voltaje_range == None or \
            self.configuracion.dac_field_driving_current == None or \
            self.configuracion.lock_sensitivity == None or \
            self.configuracion.lock_time_constant == None or \
            self.configuracion.geometry == None:

            return False
        return True

    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de moke voltage range
    def manejar_cb_moke_volage_range(self, texto):
        self.configuracion.dac_voltaje_range = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de dc level voltage range
    def manejar_cb_dc_level_voltage_range(self, texto):
        self.configuracion.dac_dc_voltage_range = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de temperature voltage range
    def manejar_cb_tempVrange(self, texto):
        self.configuracion.dac_temperature_voltaje_range = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de field driving current
    def manejar_cb_timeFieldDriving(self, texto):
        self.configuracion.dac_field_driving_current = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de sampling rate
    def manejar_value_sampling_rate(self, valor):
        self.configuracion.dac_sampling_rate = valor
        print(valor)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de sensitivity
    def manejar_cb_sensitivity(self, texto):
        self.configuracion.lock_sensitivity = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de time constant
    def manejar_cb_time_constant(self, texto):
        self.configuracion.lock_time_constant = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de magnetic field
    def manejas_magnetic_field(self, valor):
        self.configuracion.magnetic_field = valor
        print(valor)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de points per loop
    def manejar_per_loop(self, valor):
        self.configuracion.points_per_loop = valor
        print(valor)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de number of sweeps
    def manejar_number_sweeps(self, valor):
        self.configuracion.number_of_sweeps = valor
        print(valor)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de dwell time
    def manjar_dwell_time(self, valor):
        self.configuracion.dwell_time = valor
        print(valor)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de integration time
    def manejar_integration_time(self, valor):
        self.configuracion.integration_time = valor
        print(valor)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de integration time
    def manejar_lb_description(self, texto):
        texto = texto.strip()
        if texto == "":
            texto = None
        self.experimento.descripcion = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de geometry
    def manejar_geometry(self, texto):
        self.configuracion.geometry = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la barra de datafile
    def manejar_le_datafile(self, texto):
        self.experimento.rutaCsv = texto
        print(texto)
    def manejar_cb_moke_intensity(self, texto):
        if texto == " -- Select -- ":
            return
        if texto !=  self.cb_moke_dc_level.currentText() and texto != self.cb_temperature.currentText() and texto != self.cb_timeFieldDriving.currentText():
            self.configuracion.dac_input_intensity = texto
            print(texto)
        else:
            self.error_input(self.cb_moke_intensity)
    def manejar_cb_moke_dc_level(self, texto):
        if texto == " -- Select -- ":
            return
        if texto != self.cb_moke_intensity.currentText() and texto != self.cb_temperature.currentText() and texto != self.cb_timeFieldDriving.currentText():
            self.configuracion.dac_dc_level = texto 
            print(texto)
        else:
            self.error_input(self.cb_moke_dc_level)       
    def manejar_cb_temperature(self, texto):
        if texto == " -- Select -- ":
            return
        if texto != self.cb_moke_intensity.currentText() and texto != self.cb_moke_dc_level.currentText() and texto != self.cb_timeFieldDriving.currentText():
            self.configuracion.dac_input_temperature = texto
            print(texto)
        else:
            self.error_input(self.cb_temperature)
    #funcion que se ejecuta al dar click en el boton run
    def run (self):
        if self.experimento.rutaCsv== None:
            self.mostrar_error_ruta_CSV()
        elif self.control_validar_datos() == False:
            self.mostrar_error_faltan_datos()
        else:
            self.experimento.tipo = "MOKE"
            self.experimento = ExperimentoDAO.crear(self.experimento)
            self.configuracion.id_experimento = self.experimento.id
            ConfiguracionMokeDAO.crear(self.configuracion)


    def cargar_configuracion(self, id_experimento):

        experimento_cargado = ExperimentoDAO.obtener_por_id(id_experimento)

        configuracion_cargada = ConfiguracionMokeDAO.obtener_por_id(id_experimento)
        if configuracion_cargada == None:
            return

        self.le_description.setText(experimento_cargado.descripcion)
        self.le_datafile.setText(experimento_cargado.rutaCsv)
        self.cb_moke_intensity.setCurrentText(configuracion_cargada.dac_input_intensity)
        self.cb_moke_voltage_range.setCurrentText(configuracion_cargada.dac_voltaje_range)
        self.cb_moke_dc_level.setCurrentText(configuracion_cargada.dac_dc_level)
        self.cb_dc_level_voltage_range.setCurrentText(configuracion_cargada.dac_dc_voltage_range)
        self.cb_temperature.setCurrentText(configuracion_cargada.dac_input_temperature)
        self.cb_tempVrange.setCurrentText(configuracion_cargada.dac_temperature_voltaje_range)
        self.cb_timeFieldDriving.setCurrentText(configuracion_cargada.dac_field_driving_current)
        self.cb_sensitivity.setCurrentText(configuracion_cargada.lock_sensitivity)
        self.cb_time.setCurrentText(configuracion_cargada.lock_time_constant)
        self.knb_magnetic_field.setValue(configuracion_cargada.magnetic_field)
        self.knb_per_loop.setValue(configuracion_cargada.points_per_loop)
        self.knb_number_sweeps.setValue(configuracion_cargada.number_of_sweeps)
        self.knb_dweel_time.setValue(configuracion_cargada.dwell_time)
        self.knb_integration_time.setValue(configuracion_cargada.integration_time)
        self.cb_geometry.setCurrentText(configuracion_cargada.geometry)
        self.slider_samplingRate.setValue(configuracion_cargada.dac_sampling_rate)


def main():
    Conexion.iniciar_bbdd()
    app = QApplication([])
    vista_moke_loop = VistaPrincipal()
    vista_moke_loop.show()
    sys.exit(app.exec())