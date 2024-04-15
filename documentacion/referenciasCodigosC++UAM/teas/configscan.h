 #ifndef CONFIGSCAN_H 
 #define CONFIGSCAN_H 

 #include <QWidget> 
 #include <QFrame> 

 #include "teasplot.h" 

 class QGroupBox; 
 class TeasPlot; 

 class configScan : public QWidget 
     { 
     Q_OBJECT 

 public: 
     configScan(QWidget *parent = 0); 

 public slots: 
     void getFilePath(); 
     void runTimeScan(); 
     void closeTimeScan(); 
     void startThermo(); 
     void setDAQParams(); 

 private: 
     QGroupBox *createTeasSamplingBox(); 
     QGroupBox *createTeasDACBox(); 
     QGroupBox *createScanAMLGaugeBox(); 
     QGroupBox *createlockinThermo(); 
     QGroupBox *createTeasChanneltronBox(); 
     QGroupBox *teasSystemIDBox(); 
     QGroupBox *setDataFile(); 

     void updateSettings(); 
     void setDataFileName(); 
     int lockinTimerID; 
     void paintThermo(); 
     QString checkFileName(QString filename); 

     TeasPlot *teasPlot; 

 private slots: 
     void setTimeScanParameters(); 
     void resetScan(bool); 
     void disableDACCombo(int c); 
     void disableFFTSamplesCombo(int c); 
     void disableAMLGaugeCombo(int c); 

 protected: 
     void timerEvent(QTimerEvent *t); 

 }; 

 #endif 
