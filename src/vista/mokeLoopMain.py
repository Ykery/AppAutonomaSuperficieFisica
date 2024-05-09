import sys
import numpy as np
from PyQt6 import QtWidgets
from PyQt6.uic import loadUi

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from PyQt6 import Qwt
from ..modelo.clases import Conexion


class VistaPrincipal(QWidget):
    def __init__(self):
        super().__init__()

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
    
    def createMokeDACBox(self):
        
        layout = QGridLayout()
        gb_MokeDACBox = QGroupBox("DAC channel selection")
        gb_MokeDACBox.setCheckable(True)
        gb_MokeDACBox.setChecked(False)
        gb_MokeDACBox.setFont(self.fuenteHelvetica)

        cb_teas = QComboBox()
        cb_teas1 = QComboBox()
        cb_teasVrange = QComboBox()
        cb_dcVrange= QComboBox()
        cb_temperature = QComboBox()
        cb_tempVrange = QComboBox()
        cb_timeFieldDriving = QComboBox()


        cb_teas.insertItems(0, self.mokeChannelsDAC)
        cb_teas.setCurrentIndex(1)
        cb_teasVrange.insertItems(0,self.mokeVRange)
        cb_teasVrange.setCurrentIndex(0)
        cb_teas1.insertItems(0, self.mokeChannelsDAC)
        cb_teas1.setCurrentIndex(2)
        cb_dcVrange.insertItems(0,self.mokeVRange)
        cb_dcVrange.setCurrentIndex(0)
        cb_temperature.insertItems(0,self.mokeChannelsDAC)
        cb_temperature.setCurrentIndex(3)
        cb_tempVrange.insertItems(0,self.mokeLockinSensVals)
        cb_tempVrange.setCurrentIndex(0)
        cb_timeFieldDriving.insertItems(0,self.mokeLockinTimeConsVals)
        cb_timeFieldDriving.setCurrentIndex(0)


        lb_moke_intensity = QLabel("MOKE intensity:")
        lb_moke_voltage_range = QLabel("MOKE Voltage range:")
        lb_moke_dc_level = QLabel("MOKE DC level:")
        lb_dc_level_voltage_range = QLabel("DC level Voltage range:")
        lb_sample_temperature = QLabel("Sample temperature:")
        lb_temperature_voltage_range = QLabel("Temperature Voltage range:")
        lb_field_driving_current = QLabel("Field drivign current:")
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
        slider_samplingRate.valueChanged.connect(self.value_changed_display1)
        slider_samplingRate.valueChanged.connect(lcd_samplingRateDisplay.display)

        layout.addWidget(lb_moke_intensity, 0, 0, 1, 2)
        layout.addWidget(cb_teas, 1, 0, 1, 2)
        layout.addWidget(lb_moke_voltage_range, 0, 2, 1,2)
        layout.addWidget(cb_teasVrange, 1, 2, 1, 2)
        layout.addWidget(lb_moke_dc_level, 2, 0, 1, 2)
        layout.addWidget(cb_teas1, 3, 0, 1, 2)
        layout.addWidget(lb_dc_level_voltage_range, 2, 2, 1, 2)
        layout.addWidget(cb_dcVrange, 3, 2, 1, 2)
        layout.addWidget(lb_sample_temperature, 4, 0, 1, 2)
        layout.addWidget(cb_temperature, 5, 0, 1, 2)
        layout.addWidget(lb_temperature_voltage_range, 4, 2, 1, 2)
        layout.addWidget(cb_tempVrange, 5, 2, 1, 2)
        layout.addWidget(lb_field_driving_current, 6, 0, 1, 2)
        layout.addWidget(cb_timeFieldDriving, 7, 0, 1, 2)
        layout.addWidget(lb_samplig_rate, 8, 0, 1, 2)
        layout.addWidget(slider_samplingRate, 9, 0, 1, 3)
        layout.addWidget(lcd_samplingRateDisplay, 9, 3, 1, 3)

        gb_MokeDACBox.setLayout(layout)
        return gb_MokeDACBox
    #lock-in settings 
    def createLockinBox(self):
        
        layout = QVBoxLayout()

        gb_group_box = QGroupBox(" Lock-in stting ")
        gb_group_box.setCheckable(True)
        gb_group_box.setChecked(False)

        lb_sensitivity = QLabel("Sensitivity (/div)")
        cb_sensitivity = QComboBox()
        cb_sensitivity.insertItems(0, self.mokeVRange)
        cb_sensitivity.setCurrentIndex(0)
        
        lb_time = QLabel("Time Constant")
        cb_time = QComboBox()
        cb_time.insertItems(0, self.mokeLockinTimeConsVals)
        cb_time.setCurrentIndex(0)
        chb = QCheckBox("Check when correct values set")

        layout.addWidget(lb_sensitivity)
        layout.addWidget(cb_sensitivity)
        layout.addWidget(lb_time)
        layout.addWidget(cb_time)
        layout.addWidget(chb)

        gb_group_box.setLayout(layout)
        return gb_group_box
    
    def createMokeLoopBox(self):
        layout = QGridLayout()

        gb_group_box =QGroupBox("MOKE loop parameters")
        font = QFont()
        font.setBold(True)
        gb_group_box.setFont(self.fuenteHelvetica)


        lb_magnetic = QLabel("Magnetic Field (Oe)")
        knb_magnetic_Knob = Qwt.QwtKnob()
        lcd_magnetic_Display = QLCDNumber()

        knb_magnetic_Knob.valueChanged.connect(lcd_magnetic_Display.display)

        lb_loop = QLabel("Points per loop")
        knb_loop_Knob = Qwt.QwtKnob()
        lcd_loop_Display = QLCDNumber()

        knb_loop_Knob.valueChanged.connect(lcd_loop_Display.display)

        lb_sweeps = QLabel("Number of sweeps")
        knb_sweeps_Knob = Qwt.QwtKnob()
        lcd_sweeps_Display = QLCDNumber()

        knb_sweeps_Knob.valueChanged.connect(lcd_sweeps_Display.display)


        layout.addWidget(lb_magnetic, 0, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(knb_magnetic_Knob, 1, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_magnetic_Display, 2, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lb_loop, 3, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(knb_loop_Knob, 4, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_loop_Display, 5, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lb_sweeps, 6, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(knb_sweeps_Knob, 7, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_sweeps_Display, 8, 0, Qt.AlignmentFlag.AlignCenter)

        gb_group_box.setLayout(layout)
        return gb_group_box
        
    def createMokeTimeBox(self):
        layout = QGridLayout()

        gb_MokeTimeBox =QGroupBox("Time intervals for the experiment")
        font = QFont()
        font.setBold(True)
        gb_MokeTimeBox.setFont(self.fuenteHelvetica)

        lb_dweel_Time_Label = QLabel("Dwell Time (sec)")
        knb_dweel_Time_Knob = Qwt.QwtKnob()
        #knb_dweel_Time_Knob.setScale( 100, -100 )
        #
        #
        #
        # uwu
        lcd_dweel_Time_Display = QLCDNumber()

        knb_dweel_Time_Knob.valueChanged.connect(lcd_dweel_Time_Display.display)

        lb_iter_Time_Label = QLabel("Integration Time (sec)")
        knb_iter_Time_Knob = Qwt.QwtKnob()
        lcd_iter_Time_Display = QLCDNumber()

        knb_iter_Time_Knob.valueChanged.connect(lcd_iter_Time_Display.display)

        layout.addWidget(lb_dweel_Time_Label, 0, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(knb_dweel_Time_Knob, 1, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_dweel_Time_Display, 2, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lb_iter_Time_Label, 3, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(knb_iter_Time_Knob, 4, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lcd_iter_Time_Display, 5, 0, Qt.AlignmentFlag.AlignCenter)

        gb_MokeTimeBox.setLayout(layout)
        return gb_MokeTimeBox

    def createLockinThermo(self): 
        layout = QGridLayout()

        gb_lockinThermoBox = QGroupBox("Current lock-in signal level")
        gb_lockinThermoBox.setFont(self.fuenteHelvetica)

        thermo_lockinSignal = Qwt.QwtThermo()
        thermo_lockinSignal.setOrientation(Qt.Orientation.Horizontal)
        thermo_lockinSignal.setScalePosition(Qwt.QwtThermo.ScalePosition.TrailingScale) 

        layout.addWidget(thermo_lockinSignal)
        gb_lockinThermoBox.setLayout(layout)
        return gb_lockinThermoBox
      
    def mokeSystemIDBox(self):
        layout = QGridLayout()
        gb_mokeSystem_IDbox = QGroupBox("Sample/system description")
        gb_mokeSystem_IDbox.setFont(self.fuenteHelvetica)

        le_teasSysIDboxLineEdit = QLineEdit()

        layout.addWidget(le_teasSysIDboxLineEdit)
        gb_mokeSystem_IDbox.setLayout(layout)
        return gb_mokeSystem_IDbox
    
    def mokeGeometryBox(self):
        layout = QGridLayout()

        gb_moke_geomery_box = QGroupBox("Moke geometry")
        gb_moke_geomery_box.setFont(self.fuenteHelvetica)

        cb_sensitivity = QComboBox()
        cb_sensitivity.insertItems(0, self.mokeVRange)
        cb_sensitivity.setCurrentIndex(0)


        layout.addWidget(cb_sensitivity)

        gb_moke_geomery_box.setLayout(layout)
        return gb_moke_geomery_box
    
    def setDataFile(self):    
        layout = QHBoxLayout()

        gb_dataFileBox = QGroupBox("Datafile selection")
        gb_dataFileBox.setFont(self.fuenteHelvetica)

        le_fileLineEdit = QLineEdit()

        #setDataFileName()  --> llama a la función. SIN CREAR AUN

        btn_browseButton = QPushButton("Browse")

        layout.addWidget(le_fileLineEdit)
        layout.addWidget(btn_browseButton)

        gb_dataFileBox.setLayout(layout)
        return gb_dataFileBox 
    def value_changed_display1(self, i):
        print(i)


def main():
    Conexion.iniciar_bbdd()
    app = QApplication([])
    vista_moke_loop = VistaPrincipal()
    vista_moke_loop.show()
    sys.exit(app.exec())