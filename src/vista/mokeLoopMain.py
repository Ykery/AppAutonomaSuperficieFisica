import sys
import numpy as np
from PyQt6 import QtWidgets
from PyQt6.uic import loadUi

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from PyQt6 import Qwt
from ..modelo.clases import Conexion, Experimento, ConfiguracionMoke



class VistaPrincipal(QWidget):
    def __init__(self):
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
        btn_run.setFont(self.fuenteHelvetica)
        btn_close = QPushButton("Close")
        btn_close.setFont(self.fuenteHelvetica)
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
        
        
    def createMokeDACBox(self):
        
        layout = QGridLayout()
        gb_MokeDACBox = QGroupBox("DAC channel selection")
        gb_MokeDACBox.setCheckable(True)
        gb_MokeDACBox.setChecked(False)
        gb_MokeDACBox.setFont(self.fuenteHelvetica)

        self.cb_moke_intensity = QComboBox()
        self.cb_moke_intensity.insertItems(0, self.mokeChannelsDAC)
        self.cb_moke_intensity.setCurrentIndex(0)
        self.cb_moke_intensity.currentTextChanged.connect(self.manejar_cb_moke_intensity)

        self.cb_moke_dc_level = QComboBox()
        self.cb_moke_dc_level.insertItems(0, self.mokeChannelsDAC)
        self.cb_moke_dc_level.setCurrentIndex(0)
        self.cb_moke_dc_level.currentTextChanged.connect(self.manejar_cb_moke_dc_level)

        self.cb_moke_voltage_range = QComboBox()
        self.cb_moke_voltage_range.insertItems(0,self.mokeVRange)
        self.cb_moke_voltage_range.setCurrentIndex(0)
        self.cb_moke_voltage_range.currentTextChanged.connect(self.manejar_cb_moke_volage_range)

        self.cb_dc_level_voltage_range= QComboBox()
        self.cb_dc_level_voltage_range.insertItems(0,self.mokeVRange)
        self.cb_dc_level_voltage_range.setCurrentIndex(0)
        self.cb_dc_level_voltage_range.currentTextChanged.connect(self.manejar_cb_dc_level_voltage_range)

        self.cb_temperature = QComboBox()
        self.cb_temperature.insertItems(0,self.mokeChannelsDAC)
        self.cb_temperature.setCurrentIndex(0)
        self.cb_temperature.currentTextChanged.connect(self.manejar_cb_temeperature)
        
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
        slider_samplingRate = Qwt.QwtSlider()

        #DISPLAY
        lcd_samplingRateDisplay = QLCDNumber()
        lcd_samplingRateDisplay.setDigitCount(4)
        lcd_samplingRateDisplay.setSmallDecimalPoint(True)
        lcd_samplingRateDisplay.display(10)

        
        slider_samplingRate.setOrientation(Qt.Orientation.Horizontal)
        slider_samplingRate.setScalePosition(Qwt.QwtSlider.ScalePosition.TrailingScale)
        slider_samplingRate.setTrough(True)
        slider_samplingRate.setGroove(True)
        slider_samplingRate.setSpacing(10)
        slider_samplingRate.setHandleSize(QSize(30, 16))
        slider_samplingRate.setScale(0, 10.0) 
        slider_samplingRate.setTotalSteps(100)  
        slider_samplingRate.setWrapping(False)
        slider_samplingRate.setScaleMaxMinor(8)


        #Conexion display con la barra
        slider_samplingRate.valueChanged.connect(self.manejar_value_sampling_rate)
        slider_samplingRate.valueChanged.connect(lcd_samplingRateDisplay.display)

        layout.addWidget(lb_moke_intensity, 0, 0, 1, 2)
        layout.addWidget(self.cb_moke_intensity, 1, 0, 1, 2)
        layout.addWidget(lb_moke_voltage_range, 0, 2, 1,2)
        layout.addWidget(self.cb_moke_voltage_range, 1, 2, 1, 2)
        layout.addWidget(lb_moke_dc_level, 2, 0, 1, 2)
        layout.addWidget(self.cb_moke_dc_level, 3, 0, 1, 2)
        layout.addWidget(lb_dc_level_voltage_range, 2, 2, 1, 2)
        layout.addWidget(self.cb_dc_level_voltage_range, 3, 2, 1, 2)
        layout.addWidget(lb_sample_temperature, 4, 0, 1, 2)
        layout.addWidget(self.cb_temperature, 5, 0, 1, 2)
        layout.addWidget(lb_temperature_voltage_range, 4, 2, 1, 2)
        layout.addWidget(self.cb_tempVrange, 5, 2, 1, 2)
        layout.addWidget(lb_field_driving_current, 6, 0, 1, 2)
        layout.addWidget(self.cb_timeFieldDriving, 7, 0, 1, 2)
        layout.addWidget(lb_samplig_rate, 8, 0, 1, 2)
        layout.addWidget(slider_samplingRate, 9, 0, 1, 3)
        layout.addWidget(lcd_samplingRateDisplay, 9, 3, 1, 3)

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
        font = QFont()
        font.setBold(True)
        gb_moke_loop.setFont(self.fuenteHelvetica)


        lb_magnetic = QLabel("Magnetic Field (Oe)")
        self.knb_magnetic_field = Qwt.QwtKnob()
        self.knb_magnetic_field.setScale(0,600)
        lcd_magnetic_Display = QLCDNumber()

        self.knb_magnetic_field.valueChanged.connect(lcd_magnetic_Display.display)
        self.knb_magnetic_field.valueChanged.connect(self.manejas_magnetic_field)

        lb_loop = QLabel("Points per loop")
        self.knb_per_loop = Qwt.QwtKnob()
        self.knb_per_loop.setScale(0,500)
        lcd_loop_Display = QLCDNumber()

        self.knb_per_loop.valueChanged.connect(lcd_loop_Display.display)
        self.knb_per_loop.valueChanged.connect(self.manejar_per_loop)

        lb_sweeps = QLabel("Number of sweeps")
        self.knb_number_sweeps = Qwt.QwtKnob()
        self.knb_number_sweeps.setScale(0,30)
        lcd_sweeps_Display = QLCDNumber()

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
        font = QFont()
        font.setBold(True)
        gb_MokeTimeBox.setFont(self.fuenteHelvetica)

        lb_dweel_time = QLabel("Dwell Time (sec)")
        self.knb_dweel_time = Qwt.QwtKnob()
        lcd_dweel_Time = QLCDNumber()
        self.knb_dweel_time.valueChanged.connect(lcd_dweel_Time.display)
        self.knb_dweel_time.valueChanged.connect(self.manjar_dwell_time)


        lb_integration_time = QLabel("Integration Time (sec)")
        self.knb_integration_time = Qwt.QwtKnob()
        lcd_integration_time = QLCDNumber()
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
        gb_lock_in.setFont(self.fuenteHelvetica)

        thermo_lock_in = Qwt.QwtThermo()
        thermo_lock_in.setOrientation(Qt.Orientation.Horizontal)
        thermo_lock_in.setScalePosition(Qwt.QwtThermo.ScalePosition.TrailingScale) 
        #uwu peniente
        #
        #
        #
        #uwu
        layout.addWidget(thermo_lock_in)
        gb_lock_in.setLayout(layout)
        return gb_lock_in
      
    def mokeSystemIDBox(self):
        layout = QGridLayout()
        gb_description = QGroupBox("Sample/system description")
        gb_description.setFont(self.fuenteHelvetica)

        self.le_description = QLineEdit()
        self.le_description.textChanged.connect(self.manejar_lb_description)
        layout.addWidget(self.le_description)
        gb_description.setLayout(layout)
        return gb_description
    
    def mokeGeometryBox(self):
        layout = QGridLayout()

        gb_moke_geomery = QGroupBox("Moke geometry")
        gb_moke_geomery.setFont(self.fuenteHelvetica)

        self.cb_geometry = QComboBox()
        self.cb_geometry.insertItems(0, self.mokeVRange)
        self.cb_geometry.setCurrentIndex(0)
        self.cb_geometry.currentTextChanged.connect(self.manejar_geometry)

        layout.addWidget(self.cb_geometry)

        gb_moke_geomery.setLayout(layout)
        return gb_moke_geomery
    
    def setDataFile(self):    
        layout = QHBoxLayout()

        gb_datafile_selection = QGroupBox("Datafile selection")
        gb_datafile_selection.setFont(self.fuenteHelvetica)

        self.le_datafile = QLineEdit()

        #setDataFileName()  --> llama a la función. SIN CREAR AUN

        btn_browse_button = QPushButton("Browse")

        layout.addWidget(self.le_datafile)
        self.le_datafile.textChanged.connect(self.manejar_le_datafile)
        layout.addWidget(btn_browse_button)

        gb_datafile_selection.setLayout(layout)
        return gb_datafile_selection 
    
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de moke intensity, dc level y temperature
    def mostrar_error(self):
        # Crear y configurar la ventana de error
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle("Error de Input")
        error_dialog.setText("Input selecdionado no valido.")
        #aumentar tamaño de la letra 
        error_dialog.setStyleSheet("font: 12pt")
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok) 
        # Mostrar la ventana de error
        error_dialog.exec()

    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de moke intensity, dc level y temperature
    def control_Input(self,texto,tipo):
        if texto == " -- Select -- ":
            return
        if tipo == self.cb_moke_intensity:
            if texto !=  self.cb_moke_dc_level.currentText() and texto != self.cb_temperature.currentText() and texto != self.cb_timeFieldDriving.currentText():
                self.configuracion.dac_input_intensity = texto
                print(texto)
            else:
                self.mostrar_error()
                self.cb_moke_intensity.setCurrentIndex(0)
        if tipo == self.cb_moke_dc_level:
            if texto != self.cb_moke_intensity.currentText() and texto != self.cb_temperature.currentText() and texto != self.cb_timeFieldDriving.currentText():
                self.configuracion.dac_dc_level = texto 
                print(texto)
            else:
                self.mostrar_error()
                self.cb_moke_dc_level.setCurrentIndex(0)
        if tipo == self.cb_temperature:
            if texto != self.cb_moke_intensity.currentText() and texto != self.cb_moke_dc_level.currentText() and texto != self.cb_timeFieldDriving.currentText():
                self.configuracion.dac_input_temperature = texto
                print(texto)
            else:
                self.mostrar_error()
                self.cb_temperature.setCurrentIndex(0)

    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de moke voltage range
    def manejar_cb_moke_volage_range(self, texto):
        self.configuracion.dac_voltaje_range = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de dc level voltage range
    def manejar_cb_dc_level_voltage_range(self, texto):
        self.configuracion.dac_dc_voltage_range = texto
        print(texto)
    #funcion que se ejecuta cada vez que se cambia el valor de la combobox de sample temperature
    def manejar_cb_temeperature(self, texto):
        self.configuracion.dac_input_temperature = texto
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
    

def main():
    Conexion.iniciar_bbdd()
    app = QApplication([])
    vista_moke_loop = VistaPrincipal()
    vista_moke_loop.show()
    sys.exit(app.exec())