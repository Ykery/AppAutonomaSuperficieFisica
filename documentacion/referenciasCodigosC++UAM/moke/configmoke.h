 #ifndef CONFIGMOKE_H 
 #define CONFIGMOKE_H 

 #include <QWidget> 
 #include <QFrame> 

 #include "mokeplot.h" 

 class QGroupBox; 
 class MokePlot; 

 class configMoke : public QWidget 
     { 
     Q_OBJECT 

 public: 
     configMoke(QWidget *parent = 0); 

 public slots: 
     void getFilePath(); 
     void runTimeScan(); 
     void closeTimeScan(); 
     void startThermo(); 
     void mokeCreateDAQTasks(); 

 private: 
     QGroupBox *createLockinBox(); 
     QGroupBox *createMokeDACBox(); 
     QGroupBox *createLockinThermo(); 
     QGroupBox *createMokeTimeBox(); 
     QGroupBox *createMokeLoopBox(); 
     QGroupBox *mokeSystemIDBox(); 
     QGroupBox *setDataFile(); 
     QGroupBox *mokeGeometryBox(); 

     void updateSettings();  
     void setDataFileName(); 
     int lockinTimerID; 
     void paintThermo(); 
     QString checkFileName(QString filename); 

     MokePlot *mokePlot; 

 private slots: 
     void setLoopParameters(); 
     void resetScan(bool); 
     void disableDACCombo(int c); 
     void disableLockinCombo(int c); 

 protected: 
     void timerEvent(QTimerEvent *t); 

 }; 

 #endif 
