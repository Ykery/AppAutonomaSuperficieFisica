#ifndef TIMESCANPLOT_H
#define TIMESCANPLOT_H

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

class TimeScanPlot : public QwtPlot
{
     Q_OBJECT 

 public:
     TimeScanPlot(QWidget *parent = 0); 

     QwtScaleMap xMap; 
     QwtScaleMap yMap;
     
     double xMax, xMin, yMax, yMin;  
     double xMapMin, xMapMax, yMapMin, yMapMax; 
     
     void appendData(double x, double y);
     void appendData(double *x, double *y, int size); 

signals:
     void scanCompleted(bool);
     void newScanPointAdded(bool);      

 public slots: 
     void save(); 
     void startTimeScan(); 
     void getSettings(QStringList list, double* params, int* iList, double* voltRanges); 
     void stopTimeScan(); 
     void openShutter(); 
     void closeShutter(); 
     void inputScanComments(); 
     void setVMarker(); 
     void plotReset(); 
     void setZeroLevel();
     void setZeroMarker(); 
     void showCurve(QwtPlotItem *item, bool on); 
     void graphPrint(); 
     void enableZoomMode(bool);  
     QString teasUpdateNumLabel(); 

 private:
     int i, currentSize; 
     int timerID, markerCount; 
     double markerTime[20];   
     
     double shutterOpenTime, shutterCloseTime;  

     QwtPlotPicker *teasPicker; 
	QwtPlotZoomer *teasZoomer;
	QwtPlotPanner *teasPanner; 

     QwtPlotCurve *curve, *curve2, *curve3; 

     void showData(int count); 
     void newValue(); 

 protected: 
     virtual void paintEvent(QPaintEvent *);
     void drawContents(QPainter *thisPainter);
     virtual void timerEvent(QTimerEvent *t);
 };

#endif

