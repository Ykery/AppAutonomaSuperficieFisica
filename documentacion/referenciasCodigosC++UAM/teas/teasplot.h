#ifndef TEASPLOT_H
#define TEASPLOT_H

#include <QWidget>
#include <QPushButton> 
#include <QTextEdit> 
#include <QSpinBox> 
#include <QSlider> 
#include <QAction>
#include <qtoolbutton.h>
#include <qwt_plot_curve.h>

#include "timescanplot.h" 
#include "NIDAQmxBase.h" 

class TeasPlot : public QWidget
 {
     Q_OBJECT

 public:
	TeasPlot(QWidget *parent = 0); 

     QwtScaleMap xMap;
     QwtScaleMap yMap; 

 signals: 
     void newScan(bool); 

 public slots: 
     void passSettings(QStringList list, double* pList, int* iList, double* f64List); 

 protected:

 private slots: 
	void print(); 
     void runScan(bool);  
     void markShutterOpen(bool); 
     void isRunning(bool); 
     void launchNewScan(); 
     void blockButtons(); 
     void preparePrint(); 
     void updateScanNumberPoints(); 

 private: 
	TimeScanPlot *miPlot; 
 
     QToolButton *btnStart; 
     QToolButton *btnShtOpen; 
     QToolButton *btnMarker; 
     QToolButton *btnNewTimeScan; 

	//   void showInfo(QString text = QString::null);

     int currentSize; 
     double iterTime; 
     double xMax, xMin, yMax, yMin;  
     double xMapMin, xMapMax, yMapMin, yMapMax; 

 };

#endif

