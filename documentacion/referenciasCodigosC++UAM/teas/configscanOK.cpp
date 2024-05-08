#include <QtGui>

#include <qwt_thermo.h>
#include <qwt_knob.h> 
#include <qwt_slider.h> 
#include <math.h>

#include "configscan.h" 
#include "teasplot.h" 
#include "NIDAQmxBase.h" 

#define DAQmxErrChk(functionCall) { if( DAQmxFailed(error=(functionCall)) ) { goto Error; } }

class TeasPlot; 

double parametersList[3]; 
const int deltat = 100; 
double t = 0.0; 

QString dataFileName; 
QCheckBox *lockincheckBox; 
QCheckBox *DACcheckBox; 
QwtKnob *iterTimeKnob; 
QwtSlider *samplingRate; 
QRadioButton *scanEmission1; 
QRadioButton *scanEmission2; 
QLineEdit *teasSysIDLineEdit; 
QLineEdit *teasChanneltronLineEdit; 
QLineEdit *fileLineEdit; 
QLineEdit *scanSensLineEdit; 
QGroupBox *teasLockinBox; 
QGroupBox *teasDACBox; 
QStringList scanChannelsDAC; 
QStringList scanVRange; 
QStringList scanLockinSensVals; 
QStringList scanLockinTimeConsVals; 

QComboBox *teas; 
QComboBox *temperature; 
QComboBox *teasVRange; 
QComboBox *tempVRange; 
QComboBox *scanAMLUnitsComboBox; 
QGroupBox *scanAMLGaugeBox; 
QComboBox *scanAMLGaugeDACComboBox; 
QComboBox *scanAMLGaugeVRangeComboBox; 

QComboBox *lockinSens; 
QComboBox *lockinTimeCons; 
QwtThermo *lockinSignal1; 
QTime theTime; 

TaskHandle lockinTskHdl; 
double DACParams[7]; 

QStringList settingsList; 
int indicesList[6]; 

configScan::configScan(QWidget *parent)
     : QWidget(parent)
     {
     QGridLayout *grid = new QGridLayout; 

     QPushButton *runButton = new QPushButton(tr("&Run")); 
     runButton->setFont(QFont("Helvetica", 11)); 
     connect(runButton, SIGNAL(clicked()), this, SLOT(runTimeScan())); 

     QPushButton *closeButton = new QPushButton(tr("&Close")); 
     closeButton->setFont(QFont("Helvetica", 11)); 
     connect(closeButton, SIGNAL(clicked()), SLOT(closeTimeScan())); 

     scanVRange << "   --- Select ---   " 
          << "20 V (*)" << "10 V" << "5 V" << "4 V" << "2.5 V" << "2 V" << "1.25 V" << "1 V"; 
     for (int k = 1; k < 9; k++) 
          scanVRange[k].insert(0, QChar(0x00B1)); 

     scanChannelsDAC << "   --- Select ---   " 
          << "Analog input #1" << "Analog input #2" << "Analog input #3" << "Analog input #4" ; 

     scanLockinSensVals << "   --- Select ---   " 
          << "1 " << "2.5 " << "10 " << "25 " << "100 " << "250 " 
          << "1 mV" << "2.5 mV" << "10 mV" << "25 mV" << "100 mV" << "250 mV" ; 
     QString voltUnits; 
     voltUnits.insert(0, QChar(0x03BC)); 
     voltUnits.append("V"); 
     for (int k = 1; k < 7; k++) 
          scanLockinSensVals[k].append(voltUnits); 

     scanLockinTimeConsVals << "   --- Select ---   " 
          << "1 msec" << "10 msec" << "0.1 sec" << "0.3 sec" << "1 sec" << "3 sec" 
          << "10 sec" << "30 sec"  << "100 sec" ;  

     QHBoxLayout *buttonsLayout = new QHBoxLayout; 
     buttonsLayout->addSpacing(0); 
     buttonsLayout->addWidget(closeButton); 
     buttonsLayout->addSpacing(10); 
     buttonsLayout->addWidget(runButton); 
     buttonsLayout->setAlignment(Qt::AlignRight); 

     grid->addWidget(createTeasDACBox(), 0, 0, 3, 3); 
     grid->addWidget(createTeasLockinBox(), 0, 3, 2, 2); 
     grid->addWidget(createScanAMLGaugeBox(), 3, 0, 1, 3); 
     grid->addWidget(createlockinThermo(), 4, 0, 1, 3); 
     grid->addWidget(createTeasTimeBox(), 2, 3, 2, 2); 
     grid->addWidget(teasSystemIDBox(), 5, 0, 1, 2); 
     grid->addWidget(createTeasChanneltronBox(), 4, 3, 1, 2); 
     grid->addWidget(setDataFile(), 5, 2, 1, 3); 
     grid->addLayout(buttonsLayout, 7, 3, 1, 2); 
     grid->setColumnStretch(3, 10); 
     grid->setRowMinimumHeight(6, 20); 
     grid->setRowStretch(8, 10); 
     setLayout(grid); 

     setWindowTitle(tr("TEAS timescan configuration"));
     
     teasPlot = new TeasPlot; 
     teasPlot->resize(750, 600); 

     connect(teasPlot, SIGNAL(newScan(bool)), this, SLOT(resetScan(bool)));

     return; 
     }

QGroupBox *configScan::createTeasLockinBox()
     {
     teasLockinBox = new QGroupBox(tr("Lock-in settings"));
     teasLockinBox->setFont(QFont("Helvetica", 11));     
     teasLockinBox->setCheckable(true); 
     teasLockinBox->setChecked(false); 
   
     lockinSens = new QComboBox;
     lockinSens->setGeometry(QRect(10, 50, 200, 50));
     lockinSens->insertItems(0, scanLockinSensVals); 

     QLabel *sensLabel = new QLabel(tr("Sensitivity (/div)")); 

     lockinTimeCons = new QComboBox; 
     lockinTimeCons->setGeometry(QRect(10, 110, 200, 50)); 
     lockinTimeCons->insertItems(0, scanLockinTimeConsVals); 

     QLabel *timeConsLabel = new QLabel(tr("Time Constant")); 

     lockincheckBox = new QCheckBox(tr("Check when correct values set"));
     lockincheckBox->setFont(QFont("Helvetica", 10.5));   
     lockincheckBox->setChecked(false);

     connect(lockincheckBox, SIGNAL(stateChanged(int)), this, SLOT(disableLockinCombo(int))); 

     QVBoxLayout *layout1 = new QVBoxLayout;
     layout1->addWidget(sensLabel); 
     layout1->addWidget(lockinSens);
     layout1->addWidget(timeConsLabel); 
     layout1->addWidget(lockinTimeCons);
     layout1->addWidget(lockincheckBox);
     teasLockinBox->setLayout(layout1);

     return teasLockinBox;
     }

QGroupBox *configScan::createTeasDACBox()
     {
     teasDACBox = new QGroupBox(tr("DAC channel selection"));
     teasDACBox->setFont(QFont("Helvetica", 11));  
     teasDACBox->setCheckable(true);
     teasDACBox->setChecked(false);

     teas = new QComboBox;
     teas->setGeometry(QRect(10, 50, 100, 50));
     teas->insertItems(0, scanChannelsDAC); 
     teas->setCurrentIndex(0); 

     QLabel *teasLabel = new QLabel(tr("TEAS intensity:")); 

     teasVRange = new QComboBox; 
     teasVRange->setGeometry(200, 50, 100, 50); 
     teasVRange->insertItems(0, scanVRange); 
     teasVRange->setCurrentIndex(0);  

     QLabel *teasVRangeLabel = new QLabel(tr("TEAS DAC Voltage range:")); 

     temperature = new QComboBox; 
     temperature->setGeometry(QRect(10, 50, 100, 50));
     temperature->insertItems(0, scanChannelsDAC); 
     temperature->setCurrentIndex(0); 

     QLabel *temperatureLabel = new QLabel(tr("Sample temperature:")); 

     tempVRange = new QComboBox; 
     tempVRange->setGeometry(200, 50, 100, 50); 
     tempVRange->insertItems(0, scanVRange); 
     tempVRange->setCurrentIndex(0);  

     QLabel *tempVRangeLabel = new QLabel(tr("Temperature DAC Voltage range:")); 

     samplingRate = new QwtSlider(this, Qt::Horizontal, QwtSlider::TopScale, QwtSlider::BgSlot); 
     samplingRate->setRange(0, 10, 0.05, 0); 
     samplingRate->setScaleMaxMinor(4); 
     samplingRate->setThumbWidth(20); 
     samplingRate->setFocusPolicy(Qt::StrongFocus); 
     samplingRate->setValue(10); 

     QLabel *samplingRateLabel = new QLabel(tr("Sampling Rate (kHz):")); 

     QLCDNumber *samplingRateDisplay = new QLCDNumber(5); 
     samplingRateDisplay->setSegmentStyle(QLCDNumber::Filled); 
     samplingRateDisplay->setMode(QLCDNumber::Dec); 
     samplingRateDisplay->setSmallDecimalPoint(true); 
     samplingRateDisplay->setMaximumSize(100, 50); 
     samplingRateDisplay->display(10); 
     
     connect(samplingRate, SIGNAL(valueChanged(double)), samplingRateDisplay, SLOT(display(double))); 

     DACcheckBox = new QCheckBox(tr("Check when all channels set"));
     DACcheckBox->setFont(QFont("Helvetica", 10.5));       
     DACcheckBox->setChecked(false);

     connect(DACcheckBox, SIGNAL(clicked()), this, SLOT(setDAQParams())); 
     connect(DACcheckBox, SIGNAL(clicked()), this, SLOT(startThermo())); 
     connect(DACcheckBox, SIGNAL(stateChanged(int)), this, SLOT(disableDACCombo(int))); 

     QGridLayout *layout2 = new QGridLayout;
     layout2->addWidget(teasLabel, 0, 0, 1, 2);
     layout2->addWidget(teas, 1, 0, 1, 2); 
     layout2->addWidget(teasVRangeLabel, 0, 2, 1, 2); 
     layout2->addWidget(teasVRange, 1, 2, 1, 2); 
     layout2->addWidget(temperatureLabel, 2, 0, 1, 2);
     layout2->addWidget(temperature, 3, 0, 1, 2); 
     layout2->addWidget(tempVRangeLabel, 2, 2, 1, 2); 
     layout2->addWidget(tempVRange, 3, 2, 1, 2); 
     layout2->addWidget(samplingRateLabel, 4, 0, 1, 1); 
     layout2->addWidget(samplingRate, 5, 0, 1, 3); 
     layout2->addWidget(samplingRateDisplay, 5, 3, 1, 1);   
     layout2->addWidget(DACcheckBox, 6, 0, 1, 1);
     teasDACBox->setLayout(layout2);

     return teasDACBox;
     }

QGroupBox *configScan::createScanAMLGaugeBox() 
     { 
     scanAMLGaugeBox = new QGroupBox(tr("AML Pressure gauge")); 
     scanAMLGaugeBox->setFont(QFont("Helvetica", 11)); 
     scanAMLGaugeBox->setCheckable(true); 
     scanAMLGaugeBox->setChecked(false); 

     QLabel *scanBoxLabel = new QLabel(tr("Input channel:")); 
     scanBoxLabel->setFont(QFont("Helvetica", 10)); 

     scanAMLGaugeDACComboBox = new QComboBox; 
     scanAMLGaugeDACComboBox->insertItems(0, scanChannelsDAC); 
     scanAMLGaugeDACComboBox->setCurrentIndex(0); 

     QLabel *scanVRangeLabel = new QLabel(tr("Channel voltage range (V)     ")); 
     scanVRangeLabel->setFont(QFont("Helvetica", 10)); 

     scanAMLGaugeVRangeComboBox = new QComboBox; 
     scanAMLGaugeVRangeComboBox->insertItems(0, scanVRange); 
     scanAMLGaugeVRangeComboBox->setCurrentIndex(0); 

     QLabel *scanSensLineEditLabel = new QLabel(tr("Gauge sensitivity (1/[Pres]): ")); 
     scanSensLineEditLabel->setFont(QFont("Helvetica", 10)); 

     scanSensLineEdit = new QLineEdit; 
     scanSensLineEdit->setMinimumSize(180, 32); 
     scanSensLineEdit->setMaximumSize(200, 32); 

     QLabel *scanAMLUnitsLabel = new QLabel(tr("Pressure gauge units: ")); 
     scanAMLUnitsLabel->setFont(QFont("Helvetica", 10)); 

     scanAMLUnitsComboBox = new QComboBox; 
     scanAMLUnitsComboBox->insertItems(0, QStringList() 
          << "   --- Select ---   " << "mBar" << "Pascal" << "Torr"); 
     scanAMLUnitsComboBox->setCurrentIndex(0); 

     QLabel *emissionLabel = new QLabel(tr("Emission current:")); 
     emissionLabel->setFont(QFont("Helvetica", 10)); 
     scanEmission1 = new QRadioButton("0.5 mA"); 
     scanEmission2 = new QRadioButton("5.0 mA"); 
     scanEmission2->setChecked(true); 

     QGridLayout *emissionLayout = new QGridLayout; 
     emissionLayout->addWidget(emissionLabel, 0, 0); 
     emissionLayout->addWidget(scanEmission1, 2, 0); 
     emissionLayout->addWidget(scanEmission2, 3, 0); 
     emissionLayout->setRowMinimumHeight(1, 10); 
     emissionLayout->itemAtPosition(0, 0)->setAlignment(Qt::AlignHCenter); 
     emissionLayout->itemAtPosition(2, 0)->setAlignment(Qt::AlignHCenter); 
     emissionLayout->itemAtPosition(3, 0)->setAlignment(Qt::AlignHCenter); 

     QGridLayout *layout3 = new QGridLayout; 
     layout3->addWidget(scanBoxLabel, 0, 0); 
     layout3->addWidget(scanAMLGaugeDACComboBox, 1, 0); 
     layout3->addWidget(scanVRangeLabel, 0, 1); 
     layout3->addWidget(scanAMLGaugeVRangeComboBox, 1, 1); 
     layout3->addWidget(scanSensLineEditLabel, 2, 0); 
     layout3->addWidget(scanSensLineEdit, 3, 0); 
     layout3->addWidget(scanAMLUnitsLabel, 2, 1); 
     layout3->addWidget(scanAMLUnitsComboBox, 3, 1); 
     layout3->addLayout(emissionLayout, 0, 2, 3, 1); 
     layout3->setHorizontalSpacing(20); 
     scanAMLGaugeBox->setLayout(layout3); 

     return scanAMLGaugeBox; 
     } 

QGroupBox *configScan::createlockinThermo()
     {
     QGroupBox *lockinThermoBox = new QGroupBox(tr("Current lock-in signal level")); 
     lockinThermoBox->setFont(QFont("Helvetica", 11));  
     
     lockinSignal1 = new QwtThermo(this);
     lockinSignal1->setOrientation(Qt::Horizontal, QwtThermo::BottomScale);
     lockinSignal1->setRange(0.0, 10.0);
     lockinSignal1->setPipeWidth(8); 
     lockinSignal1->setFillColor(Qt::green);
     lockinSignal1->setAlarmColor(Qt::red);
     lockinSignal1->setAlarmLevel(9.0);
     lockinSignal1->setAlarmEnabled(true);
     lockinSignal1->setScaleMaxMajor(5); 
     lockinSignal1->setScaleMaxMinor(5); 
     lockinSignal1->setFont(QFont("Helvetica", 10)); 
     lockinSignal1->setValue(0); 

     QHBoxLayout *layout4 = new QHBoxLayout; 
     layout4->addWidget(lockinSignal1); 
     lockinThermoBox->setLayout(layout4);           

     return lockinThermoBox; 
     }

QGroupBox *configScan::createTeasTimeBox()
     {
     QGroupBox *teasTimeBox = new QGroupBox(tr("Integration time per datapoint"));
     teasTimeBox->setFont(QFont("Helvetica", 11));  

     iterTimeKnob = new QwtKnob;
     iterTimeKnob->setRange(0, 10.0, 0.001, 1);
     iterTimeKnob->setScaleMaxMajor(10);
     iterTimeKnob->setKnobWidth(40); 
     iterTimeKnob->setFont(QFont("Helvetica", 10)); 
     iterTimeKnob->setFocusPolicy(Qt::StrongFocus); 

     QLabel *iterTimeLabel = new QLabel(tr("Time (sec)"));
     iterTimeLabel->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     QLCDNumber *iterTimeDisplay = new QLCDNumber(5); 
     iterTimeDisplay->setSegmentStyle(QLCDNumber::Filled); 
     iterTimeDisplay->setMode(QLCDNumber::Dec); 
     iterTimeDisplay->setSmallDecimalPoint(true); 
     iterTimeDisplay->setMinimumSize(110, 40); 
     
     connect(iterTimeKnob, SIGNAL(valueChanged(double)), iterTimeDisplay, SLOT(display(double))); 

     QGridLayout *layout5 = new QGridLayout; 

     layout5->addWidget(iterTimeLabel, 0, 0); 
     layout5->addWidget(iterTimeKnob, 1, 0); 
     layout5->addWidget(iterTimeDisplay, 2, 0); 
     layout5->itemAtPosition(0, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignBottom); 
     layout5->itemAtPosition(1, 0)->setAlignment(Qt::AlignCenter); 
     layout5->itemAtPosition(2, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 
     teasTimeBox->setLayout(layout5); 

     return teasTimeBox;
     }

QGroupBox *configScan::teasSystemIDBox()
     {
     QGroupBox *teasSysIDBox = new QGroupBox(tr("Sample/system description"));
     teasSysIDBox->setFont(QFont("Helvetica", 11)); 

     teasSysIDLineEdit = new QLineEdit; 
 
     QHBoxLayout *layout7 = new QHBoxLayout; 
     layout7->addWidget(teasSysIDLineEdit); 
     
     teasSysIDBox->setLayout(layout7); 

     return teasSysIDBox; 
     } 

QGroupBox *configScan::createTeasChanneltronBox()
     {
     QGroupBox *teasChanneltronBox = new QGroupBox(tr("Channeltron bias voltage (V)"));
     teasChanneltronBox->setFont(QFont("Helvetica", 11)); 

     teasChanneltronLineEdit = new QLineEdit; 
 
     QHBoxLayout *layout8 = new QHBoxLayout; 
     layout8->addWidget(teasChanneltronLineEdit); 
     
     teasChanneltronBox->setLayout(layout8); 

     return teasChanneltronBox; 
     } 

QGroupBox *configScan::setDataFile()
     {
     QGroupBox *dataFileBox = new QGroupBox(tr("Datafile selection"));
     dataFileBox->setFont(QFont("Helvetica", 11)); 

     fileLineEdit = new QLineEdit; 

     setDataFileName(); 
     
     QPushButton *browseButton = new QPushButton("Browse"); 
     connect(browseButton, SIGNAL(clicked()), SLOT(getFilePath())); 

     QHBoxLayout *layout6 = new QHBoxLayout; 
     layout6->addWidget(fileLineEdit); 
     layout6->addWidget(browseButton); 
     dataFileBox->setLayout(layout6); 

     return dataFileBox; 
     }

void configScan::setDataFileName()
     {
     QFile dataFile("./FILENAME"); 

     if (dataFile.open(QIODevice::ReadOnly | QIODevice::Text))
          {     
          QTextStream in( &dataFile ); 
          QString savedFileName; 
          in >> savedFileName;    
          fileLineEdit->setText(savedFileName); 
          dataFile.close(); 
          } 
     } 

void configScan::setDAQParams()
     { 
     /****                      Tasks parameters                      *****/ 

     int k; 

     switch (k = teasVRange->currentIndex()) 
          { 
          case 1: 
               DACParams[0] = 0.0; 
               DACParams[1] = 20.0; 
               break; 
          case 2: 
               DACParams[0] = -10.0; 
               DACParams[1] = 10.0; 
               break; 
          case 3: 
               DACParams[0] = -5.0; 
               DACParams[1] = 5.0; 
               break; 
          case 4: 
               DACParams[0] = -4.0; 
               DACParams[1] = 4.0; 
               break; 
          case 5: 
               DACParams[0] = -2.5; 
               DACParams[1] = 2.5; 
               break; 
          case 6: 
               DACParams[0] = -2.0; 
               DACParams[1] = 2.0; 
               break; 
          case 7: 
               DACParams[0] = -1.25; 
               DACParams[1] = 1.25; 
               break; 
          case 8: 
               DACParams[0] = -1.0; 
               DACParams[1] = 1.0; 
               break;     
          } 

     switch (k = scanAMLGaugeVRangeComboBox->currentIndex()) 
          { 
          case 1: 
               DACParams[2] = 0.0; 
               DACParams[3] = 20.0; 
               break; 
          case 2: 
               DACParams[2] = -10.0; 
               DACParams[3] = 10.0; 
               break; 
          case 3: 
               DACParams[2] = -5.0; 
               DACParams[3] = 5.0; 
               break; 
          case 4: 
               DACParams[2] = -4.0; 
               DACParams[3] = 4.0; 
               break; 
          case 5: 
               DACParams[2] = -2.5; 
               DACParams[3] = 2.5; 
               break; 
          case 6: 
               DACParams[2] = -2.0; 
               DACParams[3] = 2.0; 
               break; 
          case 7: 
               DACParams[2] = -1.25; 
               DACParams[3] = 1.25; 
               break; 
          case 8: 
               DACParams[2] = -1.0; 
               DACParams[3] = 1.0; 
               break;     
          } 

     switch (k = tempVRange->currentIndex()) 
          { 
          case 1: 
               DACParams[4] = 0.0; 
               DACParams[5] = 20.0; 
               break; 
          case 2: 
               DACParams[4] = -10.0; 
               DACParams[5] = 10.0; 
               break; 
          case 3: 
               DACParams[4] = -5.0; 
               DACParams[5] = 5.0; 
               break; 
          case 4: 
               DACParams[4] = -4.0; 
               DACParams[5] = 4.0; 
               break; 
          case 5: 
               DACParams[4] = -2.5; 
               DACParams[5] = 2.5; 
               break; 
          case 6: 
               DACParams[4] = -2.0; 
               DACParams[5] = 2.0; 
               break; 
          case 7: 
               DACParams[4] = -1.25; 
               DACParams[5] = 1.25; 
               break; 
          case 8: 
               DACParams[4] = -1.0; 
               DACParams[5] = 1.0; 
               break;     
          } 
     }

void configScan::startThermo()
     { 
     int32 error = 0;  
     char errBuff[2048]={'\0'}; 
     char source[] = "OnboardClock"; 
     char lockinInputChan[25]; 
     float64 samplingRate = 10000.0; 
     uInt64 samplesPerChan = 1000; 
     
     sprintf(lockinInputChan, "Dev1/ai%d", teas->currentIndex() - 1); 

     DAQmxErrChk (DAQmxBaseCreateTask ("Lock-in check", &lockinTskHdl)); 
     DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (lockinTskHdl, lockinInputChan, "", 
                    DAQmx_Val_Diff, DACParams[0], DACParams[1], DAQmx_Val_Volts, NULL)); 
     DAQmxErrChk (DAQmxBaseCfgSampClkTiming (lockinTskHdl, source, samplingRate, 
                    DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samplesPerChan)); 

     if ( DACcheckBox->isChecked() ) 
          lockinTimerID = startTimer(deltat); 

     Error:
          if (DAQmxFailed (error)) 
               DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
          if (error) 
               { 
               printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
               return; 
               } 
     } 

void configScan::timerEvent(QTimerEvent *)
     { 
     int32 error = 0;  
     char errBuff[2048]={'\0'}; 
     uInt32 i; 
     double aver; 

     float64 timeout = 10.0; 
     uInt32 nSamplesThermo = 500; 
     float64 dataThermo[nSamplesThermo]; 
     int32 pointsToReadThermo = -1;
     int32 pointsReadThermo; 

     DAQmxErrChk (DAQmxBaseStartTask (lockinTskHdl)); 
     DAQmxErrChk (DAQmxBaseReadAnalogF64(lockinTskHdl, pointsToReadThermo, timeout, 0, 
                    dataThermo, nSamplesThermo, &pointsReadThermo, NULL));

     for (i = 0, aver = 0.0; i < nSamplesThermo; i++) 
          aver += (double)dataThermo[i]; 

     aver = 10.0*aver/(double)(DACParams[1]*nSamplesThermo); 

     lockinSignal1->setValue(aver); 

     DAQmxErrChk (DAQmxBaseStopTask (lockinTskHdl)); 

     Error:
          if (DAQmxFailed (error)) 
               DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
          if (error) 
               { 
               printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
               return; 
               } 
     } 

void configScan::setTimeScanParameters()
     {
     parametersList[0] = iterTimeKnob->value(); 
     parametersList[1] = (scanSensLineEdit->text()).toDouble();  
     if ( scanEmission1->isChecked() ) 
          parametersList[2] = 0.5; 
     else if ( scanEmission2->isChecked() ) 
          parametersList[2] = 5.0; 
     }

void configScan::getFilePath()
     {   
     dataFileName = QFileDialog::getSaveFileName(this,
                                 tr("QFileDialog::getSaveFileName()"),
                                 fileLineEdit->text(),
                                 tr("Data Files (*.dat)")); 

     fileLineEdit->setText(checkFileName(dataFileName)); 
     }

QString configScan::checkFileName(QString dataFileName)
     {
     // Check if the first datafile in the series has numeric ending and, 
     // if not, add it to start at filename_001.dat 
                             
     if (!dataFileName.isEmpty()) 
          {   
          if( dataFileName.endsWith(".dat") )
               dataFileName.chop(4); 
          
          bool ok; 
          dataFileName.right(3).toInt(&ok, 10); 
          
          if ( !ok )
               dataFileName.append("_001.dat"); 
          else 
               dataFileName.append(".dat"); 
          } 

     return dataFileName; 
     }     

void configScan::disableLockinCombo(int c)
     { 
     if ( c ) 
          {
          lockinSens->setEnabled(false); 
          lockinTimeCons->setEnabled(false); 
          } 
     else if ( teasLockinBox->isChecked() && !lockincheckBox->isChecked() )
          { 
          lockinSens->setEnabled(true); 
          lockinTimeCons->setEnabled(true); 
          }  
     } 

void configScan::disableDACCombo(int c)
     { 
     if ( c ) 
          {
          teas->setEnabled(false); 
          temperature->setEnabled(false); 
          teasVRange->setEnabled(false); 
          tempVRange->setEnabled(false); 
          } 
     else if ( teasDACBox->isChecked() && !DACcheckBox->isChecked() )
          { 
          teas->setEnabled(true); 
          temperature->setEnabled(true); 
          teasVRange->setEnabled(true); 
          tempVRange->setEnabled(true); 
          }  
     }

void configScan::disableAMLGaugeCombo(int c) 
     { 
     if ( c ) 
          { 
          scanAMLGaugeDACComboBox->setEnabled(false); 
          scanAMLGaugeVRangeComboBox->setEnabled(false); 
          scanAMLUnitsComboBox->setEnabled(false); 
          } 
     else if ( scanAMLGaugeBox->isChecked() ) 
          { 
          scanAMLGaugeDACComboBox->setEnabled(true); 
          scanAMLGaugeVRangeComboBox->setEnabled(true); 
          scanAMLUnitsComboBox->setEnabled(true); 
          } 
     } 

void configScan::resetScan(bool flag)
     { 
     if (flag)
          {
          lockinSens->setCurrentIndex(0); 
          lockinSens->setEnabled(true); 
          lockinTimeCons->setCurrentIndex(0); 
          lockinTimeCons->setEnabled(true); 
          teasLockinBox->setChecked(false); 
          lockincheckBox->setChecked(false); 
          teas->setEnabled(true); 
          temperature->setEnabled(true); 
          teasVRange->setEnabled(true); 
          tempVRange->setEnabled(true); 
          teasDACBox->setChecked(false);
          DACcheckBox->setChecked(false); 
          // scanAMLGaugeDACComboBox->setCurrentIndex(0); 
          // scanAMLGaugeVRangeComboBox->setCurrentIndex(0); 
          // scanSensLineEdit->clear(); 
          // scanAMLUnitsComboBox->setCurrentIndex(0); 
          scanAMLGaugeBox->setChecked(false); 
          (void)killTimer(lockinTimerID); 
          lockinSignal1->setValue(0.0); 
          setDataFileName(); 
          teasPlot->close(); 
          updateSettings(); 
          teasPlot = new TeasPlot; 
          teasPlot->resize(750, 600); 

          connect(teasPlot, SIGNAL(newScan(bool)), this, SLOT(resetScan(bool)));  
          }
     }

void configScan::runTimeScan() 
     { 
     int32 error = 0;  
     char errBuff[2048]={'\0'}; 

     QMessageBox *msgBox = new QMessageBox(this); 
     msgBox->setWindowTitle(tr("Warning!")); 
     msgBox->setIcon(QMessageBox::Warning);        
     msgBox->setStandardButtons(QMessageBox::Ok); 

     // Check that all experimental parameters are correctly set 
     // otherwise issue a warning 

     if ( !DACcheckBox->isChecked() ) 
          {   
          msgBox->setText(tr("Please set DAC parameters and check box")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( teas->currentIndex() == temperature->currentIndex() || 
               teas->currentIndex() == scanAMLGaugeDACComboBox->currentIndex() || 
               temperature->currentIndex() == scanAMLGaugeDACComboBox->currentIndex() ) 
          { 
          msgBox->setText(tr("Two variables have been assigned the same DAC input channel. Please correct")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( teas->currentIndex() == 0 ) 
          { 
          msgBox->setText(tr("Please set DAC channel for TEAS intensity input")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( teasVRange->currentIndex() == 0 ) 
          { 
          msgBox->setText(tr("Please set voltage range for TEAS intensity DAC channel")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( temperature->currentIndex() == 0 ) 
          { 
          msgBox->setText(tr("Please set DAC channel for sample temperature input")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( tempVRange->currentIndex() == 0 ) 
          { 
          msgBox->setText(tr("Please set voltage range for temperature DAC channel")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( scanAMLGaugeDACComboBox->currentIndex() == 0 ) 
          { 
          msgBox->setText(tr("Please set DAC channel for pressure input")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( scanAMLGaugeVRangeComboBox->currentIndex() == 0 ) 
          { 
          msgBox->setText(tr("Please set voltage range for pressure DAC channel")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( scanSensLineEdit->text().isEmpty() || scanSensLineEdit->text().isNull() ) 
          { 
          msgBox->setText(tr("Please specify AML Gauge sensitivity factor")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( !lockincheckBox->isChecked() ) 
          {         
          msgBox->setText(tr("Please set lock-in parameters and check box")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( !lockinSens->currentIndex() ) 
          { 
          msgBox->setText(tr("Please set lock-in sensitivity")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( !lockinTimeCons->currentIndex() ) 
          { 
          msgBox->setText(tr("Please set lock-in time constant")); 
          msgBox->exec(); 
          return; 
          } 
     else if (iterTimeKnob->value() == 0)
          { 
          msgBox->setText(tr("Please select non-zero iteration time")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( teasSysIDLineEdit->text().isEmpty() || teasSysIDLineEdit->text().isNull() ) 
          {
          msgBox->setText(tr("Please enter system and/or sample description")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( teasChanneltronLineEdit->text().isEmpty() || teasChanneltronLineEdit->text().isNull() ) 
          {
          msgBox->setText(tr("Please enter channeltron bias voltage")); 
          msgBox->exec(); 
          return; 
          } 
     else if( fileLineEdit->text().isNull() ) 
          {
          msgBox->setText(tr("Please select path and filename to save scan data")); 
          msgBox->exec(); 
          }
     else  
          {
          updateSettings(); 

          QFile dataFile(dataFileName);   
          if ( dataFile.exists() ) 
               { 
               QMessageBox::StandardButton reply;
               reply = QMessageBox::question(this, tr("Warning!"),
                                    tr("Data file already exists! \nDo you want to overwrite?"),  
                                    QMessageBox::Yes | QMessageBox::No); 
               if (reply == QMessageBox::No) 
                    return; 
               } 

          (void)killTimer(lockinTimerID); 

          DAQmxErrChk (DAQmxBaseClearTask (lockinTskHdl)); 

          teasPlot->passSettings(settingsList, parametersList, indicesList, DACParams); 
          teasPlot->show(); 

          Error:
               if (DAQmxFailed (error)) 
                    DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
               if (error) 
                    { 
                    printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
                    return; 
                    } 
          } 
     } 

void configScan::updateSettings() 
     { 
     settingsList.clear(); 

     setTimeScanParameters(); 

     QString dataFileName = checkFileName(fileLineEdit->text()); 
     fileLineEdit->setText(dataFileName); 

     QDate thisDate = QDate::currentDate(); 
     QString dd; 
     dd.sprintf( "%2d ", thisDate.day()); 

     QString mmm = QDate::shortMonthName(thisDate.month()); 
     dd.append(mmm); 

     QString yyyy; 
	yyyy.sprintf( " %4d", thisDate.year()); 
     dd.append(yyyy); 

     QTime thisTime = QTime::currentTime(); 
	QString h; 
	h.sprintf( "%02d:%02d", thisTime.hour(), thisTime.minute()); 

     indicesList[0] = teas->currentIndex() - 1; 
     indicesList[1] = scanAMLGaugeDACComboBox->currentIndex() - 1; 
     indicesList[2] = temperature->currentIndex() - 1; 
     indicesList[3] = lockinSens->currentIndex(); 
     indicesList[4] = lockinTimeCons->currentIndex(); 
     indicesList[5] = scanAMLUnitsComboBox->currentIndex(); 

     settingsList << dataFileName; 
     settingsList << dd; 
     settingsList << h; 
     settingsList << lockinSens->currentText(); 
     settingsList << lockinTimeCons->currentText(); 
     settingsList << teasSysIDLineEdit->text(); 
     settingsList << teasChanneltronLineEdit->text(); 

     DACParams[6] = (double)(1000.0*samplingRate->value()); 
     } 

void configScan::closeTimeScan() 
     { 
     teasPlot->close(); 
     close(); 
     } 

