#ifndef TEASMENU1_H
#define TEASMENU1_H

#include <QWidget>
#include <QGroupBox>

#include "configscan.h" 
// #include "configmoke.h" 
// #include "configmonitor.h" 
// #include "configprofile.h" 
// #include "configtemp.h" 

class QGroupBox;

class teasMenu : public QWidget
 {
     Q_OBJECT

 public:
	teasMenu(QWidget *parent = 0); 
	
 private slots: 
	void chooseOption1(); 
     void chooseOption2(); 
     void chooseOption3(); 
     void chooseOption4(); 
     void chooseOption5(); 
     void unCheckButtons(); 
     
 private: 
     QGroupBox *createGroupBox(); 
     // configMonitor *procMonitor; 
     configScan *timeScan; 
     // configMoke *mokeLoop; 
     // configProfile *profScan; 
     // configTemp *tempScan; 
 };

#endif 

