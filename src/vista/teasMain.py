import sys
import numpy as np
import random

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import Qwt
from PyQt6.Qwt import *

from ..modelo.dao import *
from ..modelo.clases import *
from .mokeLoopMain import Display_LCD_modificado, Thermometer_modificado
import random

class TeasWindow(QWidget):
    
    def __init__(self, ):
        super().__init__()

        self.setWindowTitle("TEAS MANAGEMENT")
        #self.setContentsMargins(10, 10, 10, 10)

        #variables generales
        self.teasDACParams = [None] * 6
        self.indicesList = [None] * 6

        #Se crea el objeto 'configuracion' vacío y el objeto 'experimento' vacío de la clase ConfiguracionTeas y Experimento
        self.configuracion = ConfiguracionTeas()
        self.experimento = Experimento()

        self.main_layout = QGridLayout()
        self.fuenteHelvetica = QFont("Helvetica", 11)

        self.scanVrange = [" -- Select -- ", "20 V", "10 V", "5 V", "4 V", "2.5 V", "2 V", "1.25 V", "1 V"]
        self.scanChannelsDAC = [" -- Select -- ", "Analog Input #1", "Analog Input #2", "Analog Input #3", "Analog Input #4"]
        self.unitsAML = [" -- Select -- ", "mBar", "Pascal", "Torr"]
        self.scanLockinTimeConsVals = [" --- Select --- ", "1 msec", "10 msec", "0.1 sec", "0.3 sec", "1 sec", "3 sec", "10 sec", "30 sec", "100 sec"]
        self.scanLockinSensVals = [" --- Select --- ", "1", "2.5", "10", "25", "100", "250", "1 mV", "2.5 mV", "10 mV", "25 mV", "100 mV", "250 mV"]  
          

        self.setLayout(self.main_layout)

        btn_run = QPushButton("Run")
        btn_run.setFont(self.fuenteHelvetica)
        btn_close = QPushButton("Close")
        btn_close.setFont(self.fuenteHelvetica)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(btn_close)
        buttons_layout.addWidget(btn_run)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        
        self.main_layout.addWidget(self.createTeasDACbox(), 0, 0, 3, 3)
        self.main_layout.addWidget(self.createTeasLockinBox(), 0, 3, 2, 1)
        self.main_layout.addWidget(self.createScanAMLgaugeBox(), 3, 0, 2, 3)
        self.main_layout.addWidget(self.createTeasTimeBox(), 2, 3, 3, 1)
        self.main_layout.addWidget(self.createLockinThermo(), 5, 0, 1, 3)
        self.main_layout.addWidget(self.createTeasChanneltronBox(), 5, 3, 1, 1)
        self.main_layout.addWidget(self.teasSystemIDBox(), 6, 0, 1, 2)
        self.main_layout.addWidget(self.setDataFile(), 6, 2, 1, 2)
        self.main_layout.addLayout(buttons_layout, 7, 3, 1, 1)



        print(self.configuracion)
               
        btn_run.clicked.connect(self.creaObjetoConfiguracionEinsertaEnBBDD)

    #Función que crea los objetos experimento y configuración y lo inserta en la BBDD
    def creaObjetoConfiguracionEinsertaEnBBDD(self):

        self.experimento.rutaCsv = "C:/Users/Usuario/Desktop/TEAS/TEAS.csv"
        self.experimento.descripcion = "TEAS experiment"
        self.experimento.tipo = "TEAS"
        print(" ------------------------------------------------------------ ")
        self.experimento = ExperimentoDAO.crear(self.experimento)
        print(" ------------------------------------------------------------ ")
        print(self.experimento)
        
        

        self.configuracion.id_experimento = self.experimento.id
        self.configuracion.dac_input_intensity = self.cb_teasVrange.currentText()
        self.configuracion.dac_teas_voltaje_range = self.cb_teasVrange.currentText()
        self.configuracion.dac_input_temperature = self.cb_tempVrange.currentText()
        self.configuracion.dac_temperature_voltaje_range = self.cb_tempVrange.currentText()
        self.configuracion.dac_sampling_rate = self.slider_samplingRate.value()
        self.configuracion.aml_input_pressure = self.cb_scanAMLGaugeVrangeComboBox.currentText()
        self.configuracion.aml_voltage_range = self.cb_scanAMLGaugeVrangeComboBox.currentText()
        self.configuracion.aml_sensitivity = "1"
        self.configuracion.aml_presure_units = self.cb_scanAMLUnitsComboBox.currentText()
        self.configuracion.aml_emission_current = "5.0 mA"
        self.configuracion.lock_sensitivity = "1"
        self.configuracion.lock_time_constant = "1 msec"
        self.configuracion.integration_time = 0.1
        self.configuracion.channeltron_voltage = "0.0"
        
        print(self.configuracion)
        ConfiguracionTeasDAO.crear(self.configuracion)

        

    def createTeasLockinBox(self):

        layout = QVBoxLayout()

        gb_teasLockinBox = QGroupBox("Lock-in settings")
        gb_teasLockinBox.setFont(self.fuenteHelvetica)
        gb_teasLockinBox.setCheckable(True)
        gb_teasLockinBox.setChecked(False)

        lb_sensLabel = QLabel("Sensitivity (/div)")
        lb_timeConsLabel = QLabel("Time constant")

        self.cb_lockinTimeCons = QComboBox()
        self.cb_lockinSens = QComboBox()

        self.cb_lockinTimeCons.insertItems(0, self.scanLockinSensVals)
        self.cb_lockinTimeCons.setCurrentIndex(0)
        self.cb_lockinTimeCons.currentTextChanged.connect(self.manejar_cb_lockinTimeCons)

        self.cb_lockinSens.insertItems(0, self.scanLockinTimeConsVals)
        self.cb_lockinSens.setCurrentIndex(0)
        self.cb_lockinSens.currentTextChanged.connect(self.manejar_cb_lockinSens)

        chb_lockincheckBox = QCheckBox("Check when correct values set")
        chb_lockincheckBox.setChecked(False)

        layout.addWidget(lb_sensLabel)
        layout.addWidget(self.cb_lockinTimeCons)
        layout.addWidget(lb_timeConsLabel)
        layout.addWidget(self.cb_lockinSens)
        layout.addWidget(chb_lockincheckBox)

        gb_teasLockinBox.setLayout(layout)
        return gb_teasLockinBox


    def createTeasDACbox(self):

        layout = QGridLayout()

        gb_teasDACbox = QGroupBox("DAC channel selection")
        #gb_teasDACbox.setFont(QFont("Helvetica", 11))
        gb_teasDACbox.setCheckable(True)
        gb_teasDACbox.setChecked(False)
        #font = QFont()
        #font.setBold(True)
        gb_teasDACbox.setFont(self.fuenteHelvetica)

        self.cb_teasVrange = QComboBox()
        self.cb_tempVrange = QComboBox()
        self.cb_teas = QComboBox()
        self.cb_temperature = QComboBox()
        

        lb_teasLabel = QLabel("TEAS intensity:")
        lb_teasVrangeLabel = QLabel("TEAS DAC Voltage range:")
        lb_temperatureLabel = QLabel("Sample temperature:")
        lb_tempVrangeLabel = QLabel("Temperature DAC Voltage range:")
        lb_samplingRateLabel = QLabel("Sampling Rate (kHz):")
        
        self.slider_samplingRate = Qwt.QwtSlider()

        lcd_samplingRateDisplay = Display_LCD_modificado()

        self.slider_samplingRate.valueChanged.connect(self.manejar_silder_samplingRate)
        self.slider_samplingRate.valueChanged.connect(lcd_samplingRateDisplay.display)
        
        ckb_DACcheckBox = QCheckBox()
        ckb_DACcheckBox.setChecked(False)

        self.cb_teas.insertItems(0, self.scanChannelsDAC)
        self.cb_teas.setCurrentIndex(0)
        self.cb_teas.currentIndexChanged.connect(self.manejar_cb_teas)

        self.cb_teasVrange.insertItems(0, self.scanVrange)
        self.cb_teasVrange.setCurrentIndex(0)
        self.cb_teasVrange.currentIndexChanged.connect(self.setDACparameters)
        self.cb_teasVrange.currentTextChanged.connect(self.manejar_cb_teasVrange)

        self.cb_temperature.insertItems(0, self.scanChannelsDAC)
        self.cb_temperature.setCurrentIndex(0)
        self.cb_temperature.currentIndexChanged.connect(self.manejar_cb_temperature)

        self.cb_tempVrange.insertItems(0, self.scanVrange)
        self.cb_tempVrange.setCurrentIndex(0)
        self.cb_tempVrange.currentIndexChanged.connect(self.setDACparameters)
        self.cb_tempVrange.currentIndexChanged.connect(self.manejar_cb_tempVrange)

        self.slider_samplingRate.setOrientation(Qt.Orientation.Horizontal)
        self.slider_samplingRate.setScalePosition(Qwt.QwtSlider.ScalePosition.TrailingScale)
        self.slider_samplingRate.setTrough(True)
        self.slider_samplingRate.setGroove(True)
        #self.slider_samplingRate.setValue(0.05)
        self.slider_samplingRate.setSpacing(10)
        self.slider_samplingRate.setHandleSize(QSize(30, 16))
        self.slider_samplingRate.setScale(0, 10.0) 
        self.slider_samplingRate.setTotalSteps(100)  
        self.slider_samplingRate.setWrapping(False)
        self.slider_samplingRate.setScaleMaxMinor(8)
        
        #self.main_layout.addWidget(sampling_rate, 0, 0, 1, 2)

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
        layout.addWidget(ckb_DACcheckBox, 6, 0, 1, 1)

        
        
        gb_teasDACbox.setLayout(layout)
        return gb_teasDACbox


    def createScanAMLgaugeBox(self):

        layout = QGridLayout()

        gb_scanAMLgaugeBox = QGroupBox("AML Pressure gauge")
        gb_scanAMLgaugeBox.setCheckable(True)
        gb_scanAMLgaugeBox.setChecked(False)
        #font = QFont()
        #font.setBold(True)
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
        #rb_scanEmission_2.setChecked(True)
        self.rb_scanEmission_1.clicked.connect(self.seleccionar_rb_scanEmission)
        self.rb_scanEmission_2.clicked.connect(self.seleccionar_rb_scanEmission)
        
        scanEmission_layout = QGridLayout()
        scanEmission_layout.addWidget(self.lb_emissionLabel, 0, 0, Qt.AlignmentFlag.AlignCenter)
        scanEmission_layout.addWidget(self.rb_scanEmission_1, 2, 0, Qt.AlignmentFlag.AlignCenter)
        scanEmission_layout.addWidget(self.rb_scanEmission_2, 3, 0, Qt.AlignmentFlag.AlignCenter)


        self.cb_scanAMLGaugeVrangeComboBox = QComboBox()
        self.cb_scanAMLGaugeDACcomboBox = QComboBox()
        self.cb_scanAMLUnitsComboBox = QComboBox()

        self.cb_scanAMLGaugeDACcomboBox.insertItems(0, self.scanChannelsDAC)
        self.cb_scanAMLGaugeDACcomboBox.setCurrentIndex(0)
        self.cb_scanAMLGaugeDACcomboBox.currentIndexChanged.connect(self.manejar_cb_scanAMLGaugeDACcomboBox)

        self.cb_scanAMLGaugeVrangeComboBox.insertItems(0, self.scanVrange)
        self.cb_scanAMLGaugeVrangeComboBox.setCurrentIndex(0)
        self.cb_scanAMLGaugeVrangeComboBox.currentIndexChanged.connect(self.setDACparameters)
        self.cb_scanAMLGaugeVrangeComboBox.currentIndexChanged.connect(self.manejar_cb_scanAMLGaugeVrangeComboBox)

        self.cb_scanAMLUnitsComboBox.insertItems(0, self.unitsAML)
        self.cb_scanAMLUnitsComboBox.setCurrentIndex(0)
        self.cb_scanAMLUnitsComboBox.currentIndexChanged.connect(self.manejar_cb_scanAMLUnitsComboBox)



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
    
    def createTeasTimeBox(self):
        
        layout = QGridLayout()

        gb_teasTimeBox =QGroupBox("Integration time per datapoint")
        #font = QFont()
        #font.setBold(True)
        gb_teasTimeBox.setFont(self.fuenteHelvetica)

        knb_iterTimeKnob = Qwt.QwtKnob()
        lb_iterTimeLabel = QLabel()
        lcd_iterTimerDisplay = Display_LCD_modificado()

        knb_iterTimeKnob.valueChanged.connect(lcd_iterTimerDisplay.display)

        layout.addWidget(lb_iterTimeLabel, 0, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(knb_iterTimeKnob, 1, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_iterTimerDisplay, 2, 0, Qt.AlignmentFlag.AlignCenter)

        gb_teasTimeBox.setLayout(layout)
        return gb_teasTimeBox


    def createLockinThermo(self):
        
        layout = QGridLayout()

        gb_lockinThermoBox = QGroupBox("Current lock-in signal level")
        gb_lockinThermoBox.setFont(self.fuenteHelvetica)

        thermo_lockinSignal = Thermometer_modificado()
        thermo_lockinSignal.setValue(random.randint(0, 100))
        

        layout.addWidget(thermo_lockinSignal)
        gb_lockinThermoBox.setLayout(layout)
        return gb_lockinThermoBox


    def createTeasChanneltronBox(self):

        layout = QGridLayout()

        gb_teasChanneltronBox = QGroupBox("Channeltron bias voltage (V)")
        gb_teasChanneltronBox.setFont(self.fuenteHelvetica)

        le_teasChanneltronLineEdit = QLineEdit()

        layout.addWidget(le_teasChanneltronLineEdit)
        gb_teasChanneltronBox.setLayout(layout)
        return gb_teasChanneltronBox


    def teasSystemIDBox(self):

        layout = QGridLayout()

        gb_teasSysIDbox = QGroupBox("Sample/system description")
        gb_teasSysIDbox.setFont(self.fuenteHelvetica)

        le_teasSysIDboxLineEdit = QLineEdit()

        layout.addWidget(le_teasSysIDboxLineEdit)
        gb_teasSysIDbox.setLayout(layout)
        return gb_teasSysIDbox  


    def open_file_dialog(self):
        file = QFileDialog(self)
        file.setFileMode(QFileDialog.FileMode.AnyFile)
        file.setViewMode(QFileDialog.ViewMode.List)
        file.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        
        # Si se escribe una ruta y existe, que apareza en el cuadro de diálogo del sistema de gestor de archivos
        self.archivo_incio = self.le_fileLineEdit.text()
        if len(self.archivo_incio) != 0 and os.path.exists(self.archivo_incio):
            file.setDirectory(self.archivo_incio)
       
        #Comprobar si el diálogo se cerró con una selección válida de archivo
        if file.exec():
            self.nombre_file = file.selectedFiles()[0]
            self.le_fileLineEdit.setText(self.nombre_file)

        file.close()
        print(file)
    

    def setDataFile(self):
        layout = QHBoxLayout()
        gb_dataFileBox = QGroupBox("Datafile selection")
        gb_dataFileBox.setFont(self.fuenteHelvetica)

        self.le_fileLineEdit = QLineEdit()
        self.le_fileLineEdit.setFont(QFont("Helvetica", 9))
        btn_browseButton = QPushButton("Browse")

        layout.addWidget(self.le_fileLineEdit)
        layout.addWidget(btn_browseButton)

        btn_browseButton.clicked.connect(self.open_file_dialog)

        gb_dataFileBox.setLayout(layout)
        return gb_dataFileBox


    #función para actualizar los datos del termómetro de forma aleatoria, solo para pruebas
    def actualizarDatos(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizarDatos)
        self.timer.start(100)
        import random
        thermo = Qwt.QwtThermo()
        thermo.setValue(random.randint(0, 100))


    def manejar_silder_samplingRate(self, value):
        self.configuracion.dac_sampling_rate = value
        print(value)
    def manejar_cb_teas(self, texto):
        self.configuracion.dac_input_intensity = texto
        print(texto)
    def manejar_cb_teasVrange(self,texto):
        self.configuracion.dac_teas_voltaje_range = texto
        print(texto)
    def manejar_cb_temperature(self, texto):
        self.configuracion.dac_input_temperature = texto
        print(texto)
    def manejar_cb_tempVrange(self, texto):
        self.configuracion.dac_temperature_voltaje_range = texto
        print(texto)
    def manejar_cb_lockinTimeCons(self, texto):
        self.configuracion.lock_time_constant = texto
        print(texto)
    def manejar_cb_lockinSens(self, texto):
        self.configuracion.lock_sensitivity = texto
        print(texto)
    def manejar_le_scanSensLineEdit(self, texto):
        self.configuracion.aml_sensitivity = texto
        print(texto)
    def manejar_cb_scanAMLGaugeVrangeComboBox(self, texto):
        self.configuracion.aml_voltage_range = texto
        print(texto)
    def seleccionar_rb_scanEmission(self):
        if self.rb_scanEmission_1.isChecked():
            self.manejar_rb_emision_1()
        elif self.rb_scanEmission_2.isChecked():
            self.manejar_rb_emision_2()
    def manejar_rb_emision_1(self):
        self.configuracion.aml_emission_current = "0.5 mA"
        print("0.5 mA")
    def manejar_rb_emision_2(self):
        self.configuracion.aml_emission_current = "5.0 mA"
        print("5.0 mA")
    def manejar_cb_scanAMLGaugeDACcomboBox(self, texto):
        self.configuracion.aml_input_pressure = texto
        print(texto)
    def manejar_cb_scanAMLUnitsComboBox(self, texto):
        self.configuracion.aml_presure_units = texto
        print(texto)



    #función para establecer los parámetros del DAC
    def setDACparameters(self):

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

        print(self.teasDACParams)

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

        print(self.teasDACParams)

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

        print(self.teasDACParams)

def main():
    Conexion.iniciar_bbdd()
    app = QApplication(sys.argv)
    teas_window = TeasWindow()
    teas_window.show()
    sys.exit(app.exec())