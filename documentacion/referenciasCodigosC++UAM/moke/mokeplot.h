#ifndef MOKEPLOT_H 
#define MOKEPLOT_H 

#include <QWidget> 
#include <QPushButton> 
#include <QTextEdit> 
#include <QSpinBox> 
#include <QSlider> 
#include <QAction> 
#include <qtoolbutton.h> 
#include <qwt_plot_curve.h> 

#include "mokeloopplot.h" 

class MokePlot : public QWidget 
 { 
     Q_OBJECT 

 public: 
	MokePlot(QWidget *parent = 0); 

     QwtScaleMap xMap; 
     QwtScaleMap yMap; 

 signals: 
     void newScan(bool); 

 public slots: 
     void setScanParameters(double* parameterList); 
     void passSettings(QStringList list, double* parameters, int* mokeIList, double* f64List); 

 protected: 

 private slots: 
	void print(); 
     void runScan(bool); 
     void isRunning(bool); 
     void launchNewScan(); 
     void blockButtons(); 
     void preparePrint(); 

 private: 
	MokeLoopPlot *miPlot; 

     QToolButton *btnStart; 

	//   void showInfo(QString text = QString::null); 

     int currentSize; 
     double iterTime; 
     double xMax, xMin, yMax, yMin; 
     double xMapMin, xMapMax, yMapMin, yMapMax; 

 }; 

#endif 

