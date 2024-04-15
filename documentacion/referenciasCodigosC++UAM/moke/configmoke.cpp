 #include <QtGui>

#include <qwt_thermo.h> 
#include <qwt_slider.h> 
#include <qwt_knob.h> 
#include <math.h> 

#include "configmoke.h" 
#include "NIDAQmxBase.h" 

#define DAQmxErrChk(functionCall) { if( DAQmxFailed(error=(functionCall)) ) { goto Error; } }

class MokePlot; 

const int deltat = 100; 
double t_moke = 0.0; 
double loopParameters[5]; 
double estimatedTime; 

QString mokeDataFileName; 
QCheckBox *mokeLockincheckBox; 
QCheckBox *mokeDACcheckBox; 
QwtKnob *mokeFieldKnob; 
QwtKnob *mokeWaitTimeKnob; 
QwtKnob *mokeIterTimeKnob; 
QwtKnob *mokeDataPointsKnob; 
QwtKnob *mokeLoopSweepsKnob; 
QwtSlider *mokeSamplingRate; 
QLineEdit *mokeSysIDLineEdit; 
QLineEdit *mokeFileLineEdit; 
QGroupBox *mokeLockinBox; 
QGroupBox *mokeDACBox; 
QGroupBox *mokeTimeBox; 
QStringList mokeChannelsDAC; 
QStringList mokeVRange; 
QStringList mokeLockinSensVals; 
QStringList mokeLockinTimeConsVals; 

QComboBox *moke; 
QComboBox *mokeDC; 
QComboBox *mokeFieldCurrent; 
QComboBox *mokeTemperature; 
QComboBox *mokeIntVRange; 
QComboBox *mokeDCVRange; 
QComboBox *mokeTempVRange; 
QComboBox *mokeGeomSetBox; 

QComboBox *mokeLockinSens; 
QComboBox *mokeLockinTimeCons; 
QwtThermo *mokeLockinSignal; 

QStringList mokeSettingsList; 
int mokeIndicesList[6]; 

TaskHandle mokeLockinTskHdl; 
double mokeDACParams[7]; 

configMoke::configMoke(QWidget *parent)
     : QWidget(parent)
     {
     QGridLayout *grid = new QGridLayout; 

     QPushButton *runButton = new QPushButton(tr("&Run")); 
     runButton->setFont(QFont("Helvetica", 11)); 
     connect(runButton, SIGNAL(clicked()), SLOT(runTimeScan())); 

     QPushButton *closeButton = new QPushButton(tr("&Close")); 
     closeButton->setFont(QFont("Helvetica", 11)); 
     connect(closeButton, SIGNAL(clicked()), SLOT(closeTimeScan())); 

     mokeVRange << "   --- Select ---   " 
          << "20 V (*)" << "10 V" << "5 V" << "4 V" << "2.5 V" << "2 V" << "1.25 V" << "1 V"; 
     for (int k = 1; k < 9; k++) 
          mokeVRange[k].insert(0, QChar(0x00B1)); 

     mokeChannelsDAC << "   --- Select ---   " 
          << "Analog input #1" << "Analog input #2" << "Analog input #3" << "Analog input #4" ; 

     mokeLockinSensVals << "   --- Select ---   " 
          << "1 " << "2.5 " << "10 " << "25 " << "100 " << "250 " 
          << "1 mV" << "2.5 mV" << "10 mV" << "25 mV" << "100 mV" << "250 mV" ; 
     QString voltUnits; 
     voltUnits.insert(0, QChar(0x03BC)); 
     voltUnits.append("V"); 
     for (int k = 1; k < 7; k++) 
          mokeLockinSensVals[k].append(voltUnits); 

     mokeLockinTimeConsVals << "   --- Select ---   " 
          << "1 msec" << "10 msec" << "0.1 sec" << "0.3 sec" << "1 sec" << "3 sec" 
          << "10 sec" << "30 sec"  << "100 sec" ;  

     QHBoxLayout *buttonsLayout = new QHBoxLayout; 
     buttonsLayout->addSpacing(60); 
     buttonsLayout->addWidget(closeButton); 
     buttonsLayout->addSpacing(20); 
     buttonsLayout->addWidget(runButton); 
     buttonsLayout->setAlignment(Qt::AlignRight); 

     grid->addWidget(createMokeDACBox(), 0, 0, 3, 3); 
     grid->addWidget(createLockinBox(), 0, 3, 1, 1); 
     grid->addWidget(createMokeLoopBox(), 0, 4, 6, 1); 
     grid->addWidget(createMokeTimeBox(), 1, 3, 5, 1); 
     grid->addWidget(createLockinThermo(), 3, 0, 1, 3); 
     grid->addWidget(mokeSystemIDBox(), 4, 0, 1, 2); 
     grid->addWidget(mokeGeometryBox(), 4, 2, 1, 1); 
     grid->addWidget(setDataFile(), 5, 0, 1, 3); 
	 
     grid->addLayout(buttonsLayout, 7, 3, 1, 2); 
	 
     grid->setRowMinimumHeight(6, 20); 
     grid->setColumnStretch(5, 10); 
     grid->setRowStretch(8, 10); 
     setLayout(grid); 

     setWindowTitle(tr("MOKE hysteresis loop configuration"));
     
     mokePlot = new MokePlot; 
     mokePlot->resize(750, 600); 

     connect(mokePlot, SIGNAL(newScan(bool)), this, SLOT(resetScan(bool)));

     return; 
     }

QGroupBox *configMoke::createLockinBox()
     {
     mokeLockinBox = new QGroupBox(tr("Lock-in settings"));
     mokeLockinBox->setFont(QFont("Helvetica", 11));     
     mokeLockinBox->setCheckable(true); 
     mokeLockinBox->setChecked(false); 

     mokeLockinSens = new QComboBox;
     mokeLockinSens->setGeometry(QRect(10, 50, 100, 50));
     mokeLockinSens->insertItems(0, mokeLockinSensVals);

     QLabel *sensLabel = new QLabel(tr("Sensitivity (/div)")); 

     mokeLockinTimeCons = new QComboBox;
     mokeLockinTimeCons->setGeometry(QRect(10, 110, 100, 50));
     mokeLockinTimeCons->insertItems(0, mokeLockinTimeConsVals); 

     QLabel *timeConsLabel = new QLabel(tr("Time Constant")); 

     mokeLockincheckBox = new QCheckBox(tr("Check when correct values set"));
     mokeLockincheckBox->setFont(QFont("Helvetica", 10.5));   
     mokeLockincheckBox->setChecked(false); 
     
     connect(mokeLockincheckBox, SIGNAL(stateChanged(int)), this, SLOT(disableLockinCombo(int))); 

     QVBoxLayout *layout1 = new QVBoxLayout;
     layout1->addWidget(sensLabel); 
     layout1->addWidget(mokeLockinSens);
     layout1->addWidget(timeConsLabel); 
     layout1->addWidget(mokeLockinTimeCons);
     layout1->addWidget(mokeLockincheckBox);
     mokeLockinBox->setLayout(layout1); 

     return mokeLockinBox;
     }

QGroupBox *configMoke::createMokeDACBox()
     {
     mokeDACBox = new QGroupBox(tr("DAC channel selection"));
     mokeDACBox->setFont(QFont("Helvetica", 11));  
     mokeDACBox->setCheckable(true);
     mokeDACBox->setChecked(false);

     moke = new QComboBox;
     moke->setGeometry(QRect(10, 50, 100, 50));
     moke->insertItems(0, mokeChannelsDAC); 
     moke->setCurrentIndex(0); 

     QLabel *mokeLabel = new QLabel(tr("MOKE Intensity:")); 

     mokeIntVRange = new QComboBox; 
     mokeIntVRange->setGeometry(200, 50, 100, 50); 
     mokeIntVRange->insertItems(0, mokeVRange); 
     mokeIntVRange->setCurrentIndex(0);  

     QLabel *mokeVRangeLabel = new QLabel(tr("MOKE Voltage range:")); 

     mokeDC = new QComboBox;
     mokeDC->setGeometry(QRect(10, 50, 100, 50));
     mokeDC->insertItems(0, mokeChannelsDAC); 
     mokeDC->setCurrentIndex(0); 

     QLabel *mokeDCLabel = new QLabel(tr("MOKE DC level:")); 

     mokeDCVRange = new QComboBox; 
     mokeDCVRange->setGeometry(200, 50, 100, 50); 
     mokeDCVRange->insertItems(0, mokeVRange); 
     mokeDCVRange->setCurrentIndex(0); 

     QLabel *mokeDCVRangeLabel = new QLabel(tr("DC level voltage range:")); 

     mokeTemperature = new QComboBox; 
     mokeTemperature->setGeometry(QRect(10, 50, 200, 50)); 
     mokeTemperature->insertItems(0, mokeChannelsDAC); 
     mokeTemperature->setCurrentIndex(0); 

     QLabel *temperatureLabel = new QLabel(tr("Sample temperature:")); 

     mokeTempVRange = new QComboBox; 
     mokeTempVRange->setGeometry(200, 50, 100, 50); 
     mokeTempVRange->insertItems(0, mokeVRange); 
     mokeTempVRange->setCurrentIndex(0); 

     QLabel *mokeTempVRangeLabel = new QLabel(tr("Temperature Voltage range:")); 

     mokeFieldCurrent = new QComboBox;
     mokeFieldCurrent->setGeometry(QRect(10, 50, 200, 50));
     mokeFieldCurrent->insertItems(0, QStringList()
          << "   --- Select ---   " << "Analog output #1" << "Analog output #2" ); 
     mokeFieldCurrent->setCurrentIndex(0); 

     QLabel *mokeCurrentLabel = new QLabel(tr("Field driving current:")); 

     mokeSamplingRate = new QwtSlider(this, Qt::Horizontal, QwtSlider::TopScale, QwtSlider::BgSlot); 
     mokeSamplingRate->setRange(0, 10, 0.05, 0); 
     mokeSamplingRate->setScaleMaxMinor(4); 
     mokeSamplingRate->setThumbWidth(20); 
     mokeSamplingRate->setFocusPolicy(Qt::StrongFocus); 
     mokeSamplingRate->setValue(10); 

     QLabel *mokeSamplingRateLabel = new QLabel(tr("Sampling Rate (kHz):")); 

     QLCDNumber *mokeSamplingRateDisplay = new QLCDNumber(5); 
     mokeSamplingRateDisplay->setSegmentStyle(QLCDNumber::Filled); 
     mokeSamplingRateDisplay->setMode(QLCDNumber::Dec); 
     mokeSamplingRateDisplay->setSmallDecimalPoint(true); 
     mokeSamplingRateDisplay->setMinimumSize(120, 40); 
     mokeSamplingRateDisplay->display(10); 
     
     connect(mokeSamplingRate, SIGNAL(valueChanged(double)), 
               mokeSamplingRateDisplay, SLOT(display(double))); 

     mokeDACcheckBox = new QCheckBox(tr("Check when all channels set"));
     mokeDACcheckBox->setFont(QFont("Helvetica", 10.5)); 
     mokeDACcheckBox->setChecked(false); 

     connect(mokeDACcheckBox, SIGNAL(clicked()), this, SLOT(mokeCreateDAQTasks())); 
     connect(mokeDACcheckBox, SIGNAL(clicked()), this, SLOT(startThermo())); 
     connect(mokeDACcheckBox, SIGNAL(stateChanged(int)), this, SLOT(disableDACCombo(int))); 

     QGridLayout *layout2 = new QGridLayout;
     layout2->addWidget(mokeLabel, 0, 0, 1, 2);
     layout2->addWidget(moke, 1, 0, 1, 2); 
     layout2->addWidget(mokeVRangeLabel, 0, 2, 1, 2); 
     layout2->addWidget(mokeIntVRange, 1, 2, 1, 2); 
     layout2->addWidget(mokeDCLabel, 2, 0, 1, 2);
     layout2->addWidget(mokeDC, 3, 0, 1, 2); 
     layout2->addWidget(mokeDCVRangeLabel, 2, 2, 1, 2); 
     layout2->addWidget(mokeDCVRange, 3, 2, 1, 2); 
     layout2->addWidget(temperatureLabel, 4, 0, 1, 2);
     layout2->addWidget(mokeTemperature, 5, 0, 1, 2); 
     layout2->addWidget(mokeTempVRangeLabel, 4, 2, 1, 2); 
     layout2->addWidget(mokeTempVRange, 5, 2, 1, 2); 
     layout2->addWidget(mokeCurrentLabel, 6, 0, 1, 2);
     layout2->addWidget(mokeFieldCurrent, 7, 0, 1, 2); 
     layout2->addWidget(mokeSamplingRateLabel, 8, 0, 1, 1); 
     layout2->addWidget(mokeSamplingRate, 9, 0, 1, 4); 
     layout2->addWidget(mokeSamplingRateDisplay, 7, 3, 2, 1);   
     layout2->addWidget(mokeDACcheckBox, 10, 0, 1, 1);
     mokeDACBox->setLayout(layout2);

     return mokeDACBox;
     }

QGroupBox *configMoke::createLockinThermo()
     {
     QGroupBox *lockinThermoBox = new QGroupBox(tr("Current lock-in signal level")); 
     lockinThermoBox->setFont(QFont("Helvetica", 11));  
     
     mokeLockinSignal = new QwtThermo(this); 
     mokeLockinSignal->setOrientation(Qt::Horizontal, QwtThermo::BottomScale); 
     mokeLockinSignal->setRange(0.0, 10.0); 
     mokeLockinSignal->setPipeWidth(8); 
     mokeLockinSignal->setFillColor(Qt::green); 
     mokeLockinSignal->setAlarmColor(Qt::red); 
     mokeLockinSignal->setAlarmLevel(9.0); 
     mokeLockinSignal->setAlarmEnabled(true); 
     mokeLockinSignal->setScaleMaxMajor(5); 
     mokeLockinSignal->setScaleMaxMinor(5); 
     mokeLockinSignal->setFont(QFont("Helvetica", 10)); 
     mokeLockinSignal->setValue(0); 

     QHBoxLayout *layout3 = new QHBoxLayout; 
     layout3->addWidget(mokeLockinSignal); 
     lockinThermoBox->setLayout(layout3);           

     return lockinThermoBox; 
     }

QGroupBox *configMoke::createMokeTimeBox() 
     { 
     QGroupBox *mokeTimeBox = new QGroupBox(tr("Time intervals for the experiment")); 
     mokeTimeBox->setFont(QFont("Helvetica", 11)); 

     mokeWaitTimeKnob = new QwtKnob; 
     mokeWaitTimeKnob->setRange(0, 10.0, 0.01, 1); 
     mokeWaitTimeKnob->setScaleMaxMajor(6); 
     mokeWaitTimeKnob->setScaleMaxMinor(5); 
     mokeWaitTimeKnob->setKnobWidth(40); 
     mokeWaitTimeKnob->setFont(QFont("Helvetica", 10)); 
     mokeWaitTimeKnob->setFocusPolicy(Qt::StrongFocus); 

     QLabel *mokeWaitTimeLabel = new QLabel(tr("Dwell Time (sec)"));
     mokeWaitTimeLabel->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     QLCDNumber *mokeWaitTimeDisplay = new QLCDNumber(5); 
     mokeWaitTimeDisplay->setSegmentStyle(QLCDNumber::Filled); 
     mokeWaitTimeDisplay->setMode(QLCDNumber::Dec); 
     mokeWaitTimeDisplay->setSmallDecimalPoint(true); 
     mokeWaitTimeDisplay->setMinimumSize(120, 40); 
     
     connect(mokeWaitTimeKnob, SIGNAL(valueChanged(double)), 
               mokeWaitTimeDisplay, SLOT(display(double))); 

     mokeIterTimeKnob = new QwtKnob; 
     mokeIterTimeKnob->setRange(0, 10.0, 0.01, 1); 
     mokeIterTimeKnob->setScaleMaxMajor(6); 
     mokeIterTimeKnob->setScaleMaxMinor(5); 
     mokeIterTimeKnob->setKnobWidth(40); 
     mokeIterTimeKnob->setFont(QFont("Helvetica", 10)); 
     mokeIterTimeKnob->setFocusPolicy(Qt::StrongFocus); 

     QLabel *mokeIterTimeLabel = new QLabel(tr("Integration Time (sec)"));
     mokeIterTimeLabel->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     QLCDNumber *mokeIterTimeDisplay = new QLCDNumber(5); 
     mokeIterTimeDisplay->setSegmentStyle(QLCDNumber::Filled); 
     mokeIterTimeDisplay->setMode(QLCDNumber::Dec); 
     mokeIterTimeDisplay->setSmallDecimalPoint(true); 
     mokeIterTimeDisplay->setMinimumSize(120, 40); 
     
     connect(mokeIterTimeKnob, SIGNAL(valueChanged(double)), 
               mokeIterTimeDisplay, SLOT(display(double))); 

     QGridLayout *layout4 = new QGridLayout; 

     layout4->addWidget(mokeWaitTimeLabel, 0, 0); 
     layout4->addWidget(mokeWaitTimeKnob, 1, 0); 
     layout4->addWidget(mokeWaitTimeDisplay, 2, 0); 
     layout4->itemAtPosition(0, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignBottom); 
     layout4->itemAtPosition(1, 0)->setAlignment(Qt::AlignCenter); 
     layout4->itemAtPosition(2, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 
     layout4->setRowMinimumHeight(3, 20); 
     layout4->addWidget(mokeIterTimeLabel, 4, 0); 
     layout4->addWidget(mokeIterTimeKnob, 5, 0); 
     layout4->addWidget(mokeIterTimeDisplay, 6, 0); 
     layout4->itemAtPosition(4, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignBottom); 
     layout4->itemAtPosition(5, 0)->setAlignment(Qt::AlignCenter); 
     layout4->itemAtPosition(6, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     mokeTimeBox->setLayout(layout4);

     return mokeTimeBox; 
     } 

QGroupBox *configMoke::setDataFile()
     {
     QGroupBox *dataFileBox = new QGroupBox(tr("Datafile selection"));
     dataFileBox->setFont(QFont("Helvetica", 11)); 

     mokeFileLineEdit = new QLineEdit; 

     setDataFileName(); 
     
     QPushButton *browseButton = new QPushButton("Browse"); 
     connect(browseButton, SIGNAL(clicked()), SLOT(getFilePath())); 

     QHBoxLayout *layout5 = new QHBoxLayout; 
     layout5->addWidget(mokeFileLineEdit); 
     layout5->addWidget(browseButton); 
     dataFileBox->setLayout(layout5); 

     return dataFileBox; 
     }

QGroupBox *configMoke::createMokeLoopBox()
     { 
     QGroupBox *mokeLoopBox = new QGroupBox(tr("MOKE loop parameters"));
     mokeLoopBox->setFont(QFont("Helvetica", 11));  

     mokeFieldKnob = new QwtKnob;
     mokeFieldKnob->setRange(0, 600.0, 0.1, 1);
     mokeFieldKnob->setScaleMaxMajor(7); 
     mokeFieldKnob->setScaleMaxMinor(5); 
     mokeFieldKnob->setKnobWidth(40); 
     mokeFieldKnob->setFont(QFont("Helvetica", 10));  
     mokeFieldKnob->setFocusPolicy(Qt::StrongFocus); 

     QLabel *mokeFieldLabel = new QLabel(tr("Magnetic Field (Oe)"));
     mokeFieldLabel->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     QLCDNumber *mokeFieldDisplay = new QLCDNumber(5); 
     mokeFieldDisplay->setSegmentStyle(QLCDNumber::Filled); 
     mokeFieldDisplay->setMode(QLCDNumber::Dec); 
     mokeFieldDisplay->setSmallDecimalPoint(true); 
     mokeFieldDisplay->setMinimumSize(120, 40); 
     
     connect(mokeFieldKnob, SIGNAL(valueChanged(double)), mokeFieldDisplay, SLOT(display(double))); 

     mokeDataPointsKnob = new QwtKnob;
     mokeDataPointsKnob->setRange(0, 500, 1, 1);
     mokeDataPointsKnob->setScaleMaxMajor(5); 
     mokeDataPointsKnob->setScaleMaxMinor(5); 
     mokeDataPointsKnob->setKnobWidth(40); 
     mokeDataPointsKnob->setFont(QFont("Helvetica", 10));  
     mokeDataPointsKnob->setFocusPolicy(Qt::StrongFocus); 

     QLabel *mokeDataPointsLabel = new QLabel(tr("Points per loop"));
     mokeDataPointsLabel->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     QLCDNumber *mokeDataPointsDisplay = new QLCDNumber(5); 
     mokeDataPointsDisplay->setSegmentStyle(QLCDNumber::Filled); 
     mokeDataPointsDisplay->setMode(QLCDNumber::Dec); 
     mokeDataPointsDisplay->setSmallDecimalPoint(true); 
     mokeDataPointsDisplay->setMinimumSize(120, 40); 
     
     connect(mokeDataPointsKnob, SIGNAL(valueChanged(double)), 
               mokeDataPointsDisplay, SLOT(display(double))); 
    
     mokeLoopSweepsKnob = new QwtKnob;
     mokeLoopSweepsKnob->setRange(0, 30, 1, 1);
     mokeLoopSweepsKnob->setScaleMaxMajor(7);
     mokeLoopSweepsKnob->setScaleMaxMinor(5); 
     mokeLoopSweepsKnob->setKnobWidth(40); 
     mokeLoopSweepsKnob->setFont(QFont("Helvetica", 10));  
     mokeLoopSweepsKnob->setFocusPolicy(Qt::StrongFocus); 

     QLabel *mokeLoopSweepsLabel = new QLabel(tr("Number of sweeps"));
     mokeLoopSweepsLabel->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     QLCDNumber *mokeLoopSweepsDisplay = new QLCDNumber(5); 
     mokeLoopSweepsDisplay->setSegmentStyle(QLCDNumber::Filled); 
     mokeLoopSweepsDisplay->setMode(QLCDNumber::Dec); 
     mokeLoopSweepsDisplay->setSmallDecimalPoint(true); 
     mokeLoopSweepsDisplay->setMinimumSize(120, 40); 

     connect(mokeLoopSweepsKnob, SIGNAL(valueChanged(double)), 
               mokeLoopSweepsDisplay, SLOT(display(double))); 

     QGridLayout *layout6 = new QGridLayout; 

     layout6->addWidget(mokeFieldLabel, 0, 0); 
     layout6->addWidget(mokeFieldKnob, 1, 0); 
     layout6->addWidget(mokeFieldDisplay, 2, 0); 
     layout6->itemAtPosition(0, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignBottom); 
     layout6->itemAtPosition(1, 0)->setAlignment(Qt::AlignCenter); 
     layout6->itemAtPosition(2, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignTop); 

     layout6->addWidget(mokeDataPointsLabel, 4, 0); 
     layout6->addWidget(mokeDataPointsKnob, 5, 0);
     layout6->addWidget(mokeDataPointsDisplay, 6, 0); 
     layout6->itemAtPosition(4, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignBottom);
     layout6->itemAtPosition(5, 0)->setAlignment(Qt::AlignCenter);
     layout6->itemAtPosition(6, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignTop);

     layout6->addWidget(mokeLoopSweepsLabel, 8, 0); 
     layout6->addWidget(mokeLoopSweepsKnob, 9, 0);
     layout6->addWidget(mokeLoopSweepsDisplay, 10, 0); 
     layout6->itemAtPosition(8, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignBottom);
     layout6->itemAtPosition(9, 0)->setAlignment(Qt::AlignCenter);
     layout6->itemAtPosition(10, 0)->setAlignment(Qt::AlignHCenter | Qt::AlignTop);
     
     layout6->setVerticalSpacing(5); 

     mokeLoopBox->setLayout(layout6);

     return mokeLoopBox;
     } 

QGroupBox *configMoke::mokeGeometryBox()
     { 
     QGroupBox *mokeGeomBox = new QGroupBox(tr("MOKE geometry")); 
     mokeGeomBox->setFont(QFont("Helvetica", 11)); 
     
     mokeGeomSetBox = new QComboBox;
     mokeGeomSetBox->setGeometry(QRect(10, 50, 200, 50));
     mokeGeomSetBox->insertItems(0, QStringList() 
                              << "   --- Select ---   " << "Polar" << "Longitudinal" ); 
     mokeGeomSetBox->setCurrentIndex(0); 

     QHBoxLayout *layout8 = new QHBoxLayout; 
     layout8->addWidget(mokeGeomSetBox); 

     mokeGeomBox->setLayout(layout8); 

     return mokeGeomBox; 
     }

QGroupBox *configMoke::mokeSystemIDBox()
     {
     QGroupBox *mokeSysIDBox = new QGroupBox(tr("Sample/system description"));
     mokeSysIDBox->setFont(QFont("Helvetica", 11)); 

     mokeSysIDLineEdit = new QLineEdit; 
 
     QHBoxLayout *layout7 = new QHBoxLayout; 
     layout7->addWidget(mokeSysIDLineEdit); 
     
     mokeSysIDBox->setLayout(layout7); 

     return mokeSysIDBox; 
     } 

void configMoke::setDataFileName()
     {
     QFile dataFile("./FILENAME"); 

     if (dataFile.open(QIODevice::ReadOnly | QIODevice::Text))
          {     
          QTextStream in( &dataFile ); 
          QString savedFileName; 
          in >> savedFileName; 
          mokeFileLineEdit->setText(savedFileName); 
          dataFile.close(); 
          } 
     } 

void configMoke::mokeCreateDAQTasks() 
     { 
     int k; 

     switch (k = mokeIntVRange->currentIndex()) 
          { 
          case 1: 
               mokeDACParams[0] = 0.0; 
               mokeDACParams[1] = 20.0; 
               break; 
          case 2: 
               mokeDACParams[0] = -10.0; 
               mokeDACParams[1] = 10.0; 
               break; 
          case 3: 
               mokeDACParams[0] = -5.0; 
               mokeDACParams[1] = 5.0; 
               break; 
          case 4: 
               mokeDACParams[0] = -4.0; 
               mokeDACParams[1] = 4.0; 
               break; 
          case 5: 
               mokeDACParams[0] = -2.5; 
               mokeDACParams[1] = 2.5; 
               break; 
          case 6: 
               mokeDACParams[0] = -2.0; 
               mokeDACParams[1] = 2.0; 
               break; 
          case 7: 
               mokeDACParams[0] = -1.25; 
               mokeDACParams[1] = 1.25; 
               break; 
          case 8: 
               mokeDACParams[0] = -1.0; 
               mokeDACParams[1] = 1.0; 
               break;     
          } 

     switch (k = mokeDCVRange->currentIndex()) 
          { 
          case 1: 
               mokeDACParams[2] = 0.0; 
               mokeDACParams[3] = 20.0; 
               break; 
          case 2: 
               mokeDACParams[2] = -10.0; 
               mokeDACParams[3] = 10.0; 
               break; 
          case 3: 
               mokeDACParams[2] = -5.0; 
               mokeDACParams[3] = 5.0; 
               break; 
          case 4: 
               mokeDACParams[2] = -4.0; 
               mokeDACParams[3] = 4.0; 
               break; 
          case 5: 
               mokeDACParams[2] = -2.5; 
               mokeDACParams[3] = 2.5; 
               break; 
          case 6: 
               mokeDACParams[2] = -2.0; 
               mokeDACParams[3] = 2.0; 
               break; 
          case 7: 
               mokeDACParams[2] = -1.25; 
               mokeDACParams[3] = 1.25; 
               break; 
          case 8: 
               mokeDACParams[2] = -1.0; 
               mokeDACParams[3] = 1.0; 
               break;     
          } 

     switch (k = mokeTempVRange->currentIndex()) 
          { 
          case 1: 
               mokeDACParams[4] = 0.0; 
               mokeDACParams[5] = 20.0; 
               break; 
          case 2: 
               mokeDACParams[4] = -10.0; 
               mokeDACParams[5] = 10.0; 
               break; 
          case 3: 
               mokeDACParams[4] = -5.0; 
               mokeDACParams[5] = 5.0; 
               break; 
          case 4: 
               mokeDACParams[4] = -4.0; 
               mokeDACParams[5] = 4.0; 
               break; 
          case 5: 
               mokeDACParams[4] = -2.5; 
               mokeDACParams[5] = 2.5; 
               break; 
          case 6: 
               mokeDACParams[4] = -2.0; 
               mokeDACParams[5] = 2.0; 
               break; 
          case 7: 
               mokeDACParams[4] = -1.25; 
               mokeDACParams[5] = 1.25; 
               break; 
          case 8: 
               mokeDACParams[4] = -1.0; 
               mokeDACParams[5] = 1.0; 
               break;     
          } 
     } 

void configMoke::startThermo() 
     { 
     int32 error = 0; 
     char errBuff[2048]={'\0'}; 
     char source[] = "OnboardClock"; 
     char mokeLockinInputChan[25]; 
     float64 samplingRate = 10000.0; 
     uInt64 samplesPerChan = 1000; 

     sprintf(mokeLockinInputChan, "Dev1/ai%d", moke->currentIndex() - 1); 

     DAQmxErrChk (DAQmxBaseCreateTask ("Lock-in check", &mokeLockinTskHdl)); 
     DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (mokeLockinTskHdl, mokeLockinInputChan, "", 
                    DAQmx_Val_Diff, mokeDACParams[0], mokeDACParams[1], 
                    DAQmx_Val_Volts, NULL)); 
     DAQmxErrChk (DAQmxBaseCfgSampClkTiming (mokeLockinTskHdl, source, samplingRate, 
                    DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samplesPerChan)); 

     if ( mokeDACcheckBox->isChecked() ) 
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

void configMoke::timerEvent(QTimerEvent *) 
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

     DAQmxErrChk (DAQmxBaseStartTask (mokeLockinTskHdl)); 
     DAQmxErrChk (DAQmxBaseReadAnalogF64(mokeLockinTskHdl, pointsToReadThermo, timeout, 0, 
                    dataThermo, nSamplesThermo, &pointsReadThermo, NULL)); 

     for (i = 0, aver = 0.0; i < nSamplesThermo; i++) 
          aver += (double)dataThermo[i]; 

     aver = 10.0*aver/(double)(mokeDACParams[1]*nSamplesThermo); 

     mokeLockinSignal->setValue(aver); 

     DAQmxErrChk (DAQmxBaseStopTask (mokeLockinTskHdl)); 

     Error: 
          if (DAQmxFailed (error)) 
               DAQmxBaseGetExtendedErrorInfo (errBuff, 2048); 

          if (error) 
               { 
               printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
               return; 
               } 
     } 

void configMoke::setLoopParameters() 
     { 
     loopParameters[0] = mokeFieldKnob->value(); 
     loopParameters[1] = mokeDataPointsKnob->value(); 
     loopParameters[2] = mokeLoopSweepsKnob->value(); 
     loopParameters[3] = mokeWaitTimeKnob->value(); 
     loopParameters[4] = mokeIterTimeKnob->value(); 
     estimatedTime = (loopParameters[3] + 
                         loopParameters[4])*loopParameters[1]*(loopParameters[2] + 0.25); 

     mokePlot->setScanParameters(loopParameters); 
     } 

void configMoke::getFilePath() 
     { 
     mokeDataFileName = QFileDialog::getSaveFileName(this, 
                                 tr("Select filename for storing data"), 
                                 mokeFileLineEdit->text(), 
                                 tr("Data Files (*.dat)")); 

     mokeFileLineEdit->setText(checkFileName(mokeDataFileName)); 
     } 

QString configMoke::checkFileName(QString mokeDataFileName) 
     { 
     // Check if the first datafile in the series has numeric ending and, 
     // if not, append it to start at filename_001.dat 
                      
     if (!mokeDataFileName.isEmpty()) 
          { 
          if( mokeDataFileName.endsWith(".dat") ) 
               mokeDataFileName.chop(4); 

          bool ok; 
          mokeDataFileName.right(3).toInt(&ok, 10); 

          if ( !ok ) 
               mokeDataFileName.append("_001.dat"); 
          else 
               mokeDataFileName.append(".dat"); 
          } 

     return mokeDataFileName; 
     } 

void configMoke::disableLockinCombo(int c) 
     { 
     if ( c ) 
          { 
          mokeLockinSens->setEnabled(false); 
          mokeLockinTimeCons->setEnabled(false); 
          } 
     else if ( mokeLockinBox->isChecked() && !mokeLockincheckBox->isChecked() ) 
          { 
          mokeLockinSens->setEnabled(true); 
          mokeLockinTimeCons->setEnabled(true); 
          } 
     } 

void configMoke::disableDACCombo(int c) 
     { 
     if ( c ) 
          { 
          moke->setEnabled(false); 
          mokeDC->setEnabled(false); 
          mokeTemperature->setEnabled(false); 
          mokeFieldCurrent->setEnabled(false); 
          mokeIntVRange->setEnabled(false); 
          mokeDCVRange->setEnabled(false); 
          mokeTempVRange->setEnabled(false); 
          } 
     else if ( mokeDACBox->isChecked() && !mokeDACcheckBox->isChecked() ) 
          { 
          moke->setEnabled(true); 
          mokeDC->setEnabled(true); 
          mokeTemperature->setEnabled(true); 
          mokeFieldCurrent->setEnabled(true); 
          mokeIntVRange->setEnabled(true); 
          mokeDCVRange->setEnabled(true); 
          mokeTempVRange->setEnabled(true); 
          } 
     } 

void configMoke::resetScan(bool flag) 
     { 
     if (flag) 
          { 
          mokeLockinSens->setCurrentIndex(0); 
          mokeLockinSens->setEnabled(true); 
          mokeLockinTimeCons->setCurrentIndex(0); 
          mokeLockinTimeCons->setEnabled(true); 
          mokeLockinBox->setChecked(false); 
          mokeLockincheckBox->setChecked(false); 
          moke->setEnabled(true); 
          mokeDC->setEnabled(true); 
          mokeTemperature->setEnabled(true); 
          mokeFieldCurrent->setEnabled(true); 
          mokeIntVRange->setEnabled(true); 
          mokeTempVRange->setEnabled(true); 
          mokeDACBox->setChecked(false); 
          mokeDACcheckBox->setChecked(false); 
          (void)killTimer(lockinTimerID); 
          mokeLockinSignal->setValue(0.0); 
          mokeGeomSetBox->setCurrentIndex(0); 
          mokeSysIDLineEdit->clear(); 
          setDataFileName(); 
          mokePlot->close(); 
          updateSettings(); 
          mokePlot = new MokePlot; 
          mokePlot->resize(750, 600); 

          connect(mokePlot, SIGNAL(newScan(bool)), this, SLOT(resetScan(bool))); 
          } 
     } 

void configMoke::runTimeScan() 
     { 
     int32 error = 0; 
     char errBuff[2048]={'\0'}; 

     QMessageBox *msgBox = new QMessageBox(this); 
     msgBox->setWindowTitle(tr("Warning!")); 
     msgBox->setIcon(QMessageBox::Warning);  
     msgBox->setStandardButtons(QMessageBox::Ok); 
     QString eT; 

     if ( !mokeDACcheckBox->isChecked() ) 
          { 
          msgBox->setText(tr("Please set DAC parameters and check box")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( !mokeLockincheckBox->isChecked() ) 
          { 
          msgBox->setText("Please set lock-in parameters and check box"); 
          msgBox->exec(); 
          return; 
          } 
     if ( moke->currentIndex() == mokeDC->currentIndex() || 
               moke->currentIndex() == mokeTemperature->currentIndex() || 
               mokeTemperature->currentIndex() == mokeDC->currentIndex()) 
          { 
          msgBox->setText(tr("Two variables have been assigned the same DAC input channel. Please correct")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeLockinSens->currentIndex() == 0 ) 
          { 
          msgBox->setText("Please set lock-in sensitivity"); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeLockinTimeCons->currentIndex() == 0 ) 
          { 
          msgBox->setText("Please set lock-in time constant"); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeFieldKnob->value() == 0 ) 
          { 
          msgBox->setText("Please select maximum applied magnetic field"); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeWaitTimeKnob->value() == 0 ) 
          { 
          msgBox->setText("Please select non-zero dwell time"); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeIterTimeKnob->value() == 0 ) 
          { 
          msgBox->setText("Please select non-zero integration time"); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeDataPointsKnob->value() == 0 ) 
          { 
          msgBox->setText("Please select non-zero number of datapoints per loop"); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeLoopSweepsKnob->value() == 0 ) 
          { 
          msgBox->setText("Please select non-zero number of sweeps"); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeSysIDLineEdit->text().isEmpty() || mokeSysIDLineEdit->text().isNull() ) 
          { 
          msgBox->setText(tr("Please enter system and/or sample description")); 
          msgBox->exec(); 
          return; 
          } 
     else if ( mokeFileLineEdit->text().isNull() ) 
          { 
          msgBox->setText("Please select path and filename to save scan data"); 
          msgBox->exec(); 
          return; 
          } 
     else 
          { 
          updateSettings(); 

          QFile dataFile(mokeDataFileName); 
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

          eT.sprintf("%.2lf", estimatedTime/60.0); 
          eT.prepend(tr("the estimated time for completion of this measurement is:  ")); 
          eT.prepend(tr("With the current settings, ")); 
          eT.append(tr(" min. ")); 
          msgBox->setText(eT); 
          msgBox->setInformativeText(tr("Do you want to proceed?")); 
          msgBox->setStandardButtons(QMessageBox::Ok | QMessageBox::Cancel); 
          int ret = msgBox->exec(); 
          switch (ret) 
               { 
               case QMessageBox::Cancel: 
                    return; 
               case QMessageBox::Ok: 
                    break; 
               } 

          DAQmxErrChk (DAQmxBaseClearTask (mokeLockinTskHdl)); 

          mokePlot->passSettings(mokeSettingsList, loopParameters, mokeIndicesList, mokeDACParams); 
          mokePlot->show(); 

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

void configMoke::updateSettings() 
     { 
     mokeSettingsList.clear(); 

     setLoopParameters(); 

     QString mokeDataFileName = checkFileName(mokeFileLineEdit->text()); 
     mokeFileLineEdit->setText(mokeDataFileName); 

     QDate thisDate = QDate::currentDate(); 
     QString dd; 
     dd.sprintf( "%2d ", thisDate.day()); 

     QString mmm = QDate::shortMonthName(thisDate.month()); 
     dd.append(mmm); 

     QString yyyy; 
	yyyy.sprintf( " %4d ", thisDate.year()); 
     dd.append(yyyy); 

     QTime thisTime = QTime::currentTime(); 
	QString h; 
	h.sprintf( "%02d:%02d", thisTime.hour(), thisTime.minute()); 

     mokeIndicesList[0] = moke->currentIndex(); 
     mokeIndicesList[1] = mokeDC->currentIndex(); 
     mokeIndicesList[2] = mokeTemperature->currentIndex(); 
     mokeIndicesList[3] = mokeFieldCurrent->currentIndex(); 
     mokeIndicesList[4] = mokeLockinSens->currentIndex(); 
     mokeIndicesList[5] = mokeLockinTimeCons->currentIndex(); 

     mokeSettingsList << mokeDataFileName; 
     mokeSettingsList << dd; 
     mokeSettingsList << h; 
     mokeSettingsList << mokeLockinSens->currentText(); 
     mokeSettingsList << mokeLockinTimeCons->currentText(); 
     mokeSettingsList << mokeSysIDLineEdit->text(); 
     mokeSettingsList << mokeGeomSetBox->currentText(); 

     mokeDACParams[6] = (double)(1000.0*mokeSamplingRate->value()); 
     } 

void configMoke::closeTimeScan() 
     { 
     mokePlot->close(); 
     close(); 
     } 

