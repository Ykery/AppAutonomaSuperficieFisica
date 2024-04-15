#ifndef MOKELOOPPLOT_H 
#define MOKELOOPPLOT_H 

#include <QWidget> 
#include <qwt_plot.h> 
#include <qwt_array.h> 
#include <qpainter.h> 
#include <qwt_plot_curve.h> 
#include <qwt_scale_map.h> 
#include <qframe.h> 

#include "NIDAQmxBase.h" 

class QwtPlotPicker; 
class QwtPlotZoomer; 
class QwtPlotPanner; 
class QwtPlotCurve; 

class MokeLoopPlot : public QwtPlot 
{ 
     Q_OBJECT 

 public: 
     MokeLoopPlot(QWidget *parent = 0); 

     QwtScaleMap xMap; 
     QwtScaleMap yMap; 

     double xMax, xMin, yMax, yMin; 
     double xMapMin, xMapMax, yMapMin, yMapMax; 

     void appendData(double x, double y); 
     void appendData(double *x, double *y, int size); 

signals: 
     void scanCompleted(bool); 
     void progress(int); 

 public slots: 
     void save(); 
     void startLoopScan(); 
     void getSettings(QStringList list, double* parameters, int* mokeIList, double* mokeDACConfig); 
     void stopLoopScan(); 
     void inputScanComments(); 
     void plotReset(); 
     void getLockinZeros(); 
     void setZeroMarker(bool plus); 
     void showCurve(QwtPlotItem *item, bool on); 
     void averageScans(int s); 
     void graphPrint(); 
     void enableZoomMode(bool yes); 
     void resetXScale(double xMax); 

 private: 
     int i; 
     int mokeTimerID; 

     QwtPlotPicker *mokePicker; 
	QwtPlotZoomer *mokeZoomer; 
	QwtPlotPanner *mokePanner; 

     QwtPlotCurve *curve, *curve2, *curve3; 

     void showMokeData(QwtPlotCurve *c, double *x, double *y, int count); 
     void newValue(); 

 protected: 
     virtual void paintEvent(QPaintEvent *); 
     void drawContents(QPainter *thisPainter); 
     virtual void timerEvent(QTimerEvent *t); 
 }; 

#endif 

