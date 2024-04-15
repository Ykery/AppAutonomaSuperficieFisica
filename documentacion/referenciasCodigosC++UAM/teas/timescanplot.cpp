#include <QApplication>
#include <qwt_plot.h> 
#include <qwt_plot_marker.h>
#include <qwt_plot_curve.h>
#include <qwt_curve_fitter.h>
#include <qwt_plot_zoomer.h> 
#include <qwt_plot_panner.h>
#include <qwt_legend.h>
#include <qwt_data.h> 
#include <qwt_symbol.h> 
#include <qwt_text.h>
#include <qwt_math.h> 
#include <qwt_plot_grid.h>
#include <qwt_legend_item.h> 
#include <qwt_scale_engine.h> 
#include <qframe.h> 
#include <qcolor.h> 
#include <QInputDialog> 
#include <QDir>
#include <QTextStream> 
#include <QMessageBox> 
#include <QLabel>
#include <QTextEdit> 
#include <QGridLayout> 
#include <QPushButton> 
#include <QTime> 
#include <math.h> 
#include <stdio.h> 

#include "timescanplot.h" 
#include "nrutil.h" 
#include "NIDAQmxBase.h" 

#define DAQmxErrChk(functionCall) { if( DAQmxFailed(error=(functionCall)) ) { goto Error; } } 

//  Required by Numerical Recipes:   

#if defined(__STDC__) || defined(ANSI) || defined(NRANSI)   // ANSI 
#define SWAP(a, b) tempr = (a); (a) = (b); (b) = tempr 
#define NR_END 1 
#define FREE_ARG char* 

#define LOWLIM 0.0265         //  order of lowest element in FFT interval  
#define HILIM 0.026715        //  order of highest element in FFT interval  

//
// Variables visible to all functions 
//

const int Size = 5000;  

double xVal[Size];   
double yVal[Size]; 
double yVal2[Size]; 
double yVal3[Size]; 

// double iterationTime; 
double zeroInt; 
double* theTimeScanParams; 
int teasCurrentSize; 

QString markerLabel[20]; 
QString scanComments, timeScanPrintFile; 
QStringList theSettingsList; 
int* theIndicesList; 

QwtPlotGrid *grid; 
QwtPlotMarker *mX3; 
QFrame *commentsPopup; 
QMessageBox *msgBox; 
QTime scanTime;

TaskHandle teasTskHdl; 
TaskHandle pressTskHdl; 
TaskHandle tempTskHdl; 

uInt32 nSamplesTeas, nSamplesOther; 
int32 teasPointsToRead, teasPointsRead; 
int32 pointsToReadPress, pointsReadPress; 
int32 pointsToReadTemp, pointsReadTemp; 
 
float64 teasChanMin, teasChanMax, pressChanMin, pressChanMax; 
float64 tempChanMin, tempChanMax, sampleRate; 
float64 timeout = 10.0; 

// float teasChanMin, teasChanMax, pressChanMin, pressChanMax; 
// float tempChanMin, tempChanMax, sampleRate; 

double* DACVals;
bool shutterClosed = false; 
bool shutterOpen = false; 

void nrerror(char error_text[])         /*  Numerical Recipes standard error handler  */ 
     { 
     fprintf(stderr,"Numerical Recipes run-time error...\n"); 
	fprintf(stderr,"%s\n",error_text); 
	fprintf(stderr,"...now exiting to system...\n"); 
	exit(1); 
	} 

double *dvector(long nl, long nh)       /* allocate a double vector with subscript range v[nl..nh] */ 
     { 
	double *v; 

	v = (double *)malloc((size_t) ((nh - nl + 1 + NR_END)*sizeof(double))); 
	if (!v) nrerror ("allocation failure in dvector()"); 
	return v - nl + NR_END; 
	} 

void free_dvector(double *v, long nl, long nh)    /* free a double vector allocated with dvector() */ 
     { 
	free((FREE_ARG) (v + nl - NR_END)); 
	}

void dfour1(double data[], unsigned long nn, int isign)     /*   FFT calculation   */ 
     { 
	unsigned long n, mmax, m, j, istep, i; 
	double wtemp, wr, wpr, wpi, wi, theta; 
	double tempr, tempi; 

	n = nn << 1; 
	j = 1; 
	
	/*   Bit reversal routine   */ 
		
	for (i = 1; i < n; i += 2) 
	     { 
		if (j > i) 
		     { 
			SWAP(data[j], data[i]); 
			SWAP(data[j+1], data[i+1]); 
			} 
		m = n >> 1; 
		while (m >= 2 && j > m) 
		     { 
			j -= m; 
			m >>= 1; 
			} 
		j += m; 
		} 
	
	/*   Danielson-Laczos algorithm   */ 
	
	mmax = 2; 
	
	while (n > mmax) 
	     { 
		istep = mmax << 1; 
		theta = isign*(6.28318530717959/mmax); 
		wtemp = sin(0.5*theta); 
		wpr = -2.0*wtemp*wtemp; 
		wpi = sin(theta); 
		wr = 1.0; 
		wi = 0.0; 
		for (m = 1; m < mmax; m += 2) 
		     { 
			for (i = m; i <= n; i += istep) 
			     { 
				j = i+mmax; 
				tempr = wr*data[j] - wi*data[j + 1]; 
				tempi = wr*data[j + 1] + wi*data[j]; 
				data[j] = data[i] - tempr; 
				data[j + 1] = data[i + 1] - tempi; 
				data[i] += tempr; 
				data[i + 1] += tempi; 
				} 
			wr = (wtemp = wr)*wpr - wi*wpi + wr; 
			wi = wi*wpr + wtemp*wpi + wi; 
			} 
		mmax=istep; 
		} 
	} 

#undef SWAP 
#endif /* ANSI */ 

class Zoomer: public QwtPlotZoomer
     {
     public:
          Zoomer(int xAxis, int yAxis, QwtPlotCanvas *canvas):
               QwtPlotZoomer(xAxis, yAxis, canvas)
          {
          setSelectionFlags(QwtPicker::DragSelection | QwtPicker::CornerToCorner);
          setTrackerMode(QwtPicker::AlwaysOff);
          setRubberBand(QwtPicker::NoRubberBand);

          // RightButton: zoom out by 1
          // Ctrl+RightButton: zoom out to full size

          setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton, Qt::ControlModifier);

          setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton);
          }
     };

TimeScanPlot::TimeScanPlot(QWidget *) 
     {
     setAutoReplot(false); 
     
     QwtSplineCurveFitter* curveFitter; 
     
     setTitle("TEAS Timescan"); 
     
     QwtLegend *legend = new QwtLegend; 
     legend->setItemMode(QwtLegend::CheckableItem); 
     insertLegend(legend, QwtPlot::RightLegend); 

     setFrameStyle(QFrame::Box|QFrame::Raised); 
     setLineWidth(1); 
     setMargin(10); 
     setCanvasLineWidth(2); 

     xMapMin = 0.0; 
     xMapMax = 100.0; 
     yMapMin = -0.05; 
     yMapMax = 1.05; 

     xMap.setScaleInterval(xMapMin, xMapMax); 
     yMap.setScaleInterval(yMapMax, yMapMin); 

     setAxisScale(xBottom, xMapMin, xMapMax); 
     setAxisScale(yLeft, yMapMin, yMapMax); 

     enableAxis(QwtPlot::yRight); 

     setAxisTitle(xBottom, tr("Time [sec]")); 
     setAxisTitle(yLeft, tr("Intensity [arb. un.]")); 
     setAxisTitle(QwtPlot::yRight, tr("Pressure [mbar]")); 

     setAxisScaleEngine(QwtPlot::yRight, new QwtLog10ScaleEngine); 
     setAxisScale(yRight, 1e-10, 1e-8); 

     teasPicker = new QwtPlotPicker(QwtPlot::xBottom, QwtPlot::yLeft,
          QwtPicker::PointSelection | QwtPicker::DragSelection, 
          QwtPlotPicker::CrossRubberBand, QwtPicker::AlwaysOn, 
          canvas()); 
     teasPicker->setRubberBandPen(QColor(Qt::green)); 
     teasPicker->setRubberBand(QwtPicker::CrossRubberBand); 
     teasPicker->setTrackerPen(QColor(Qt::white)); 

     teasPanner = new QwtPlotPanner(canvas()); 
     teasPanner->setMouseButton(Qt::MidButton); 

     teasZoomer = new Zoomer(QwtPlot::xBottom, QwtPlot::yLeft, canvas()); 
     teasZoomer->setRubberBand(QwtPicker::RectRubberBand); 
     teasZoomer->setRubberBandPen(QColor(Qt::green)); 
     teasZoomer->setTrackerMode(QwtPicker::ActiveOnly); 
     teasZoomer->setTrackerPen(QColor(Qt::white)); 
    
     grid = new QwtPlotGrid; 
     grid->enableXMin(true); 
     grid->enableYMin(true); 
     grid->setMajPen(QPen(Qt::white, 0, Qt::DotLine)); 
     grid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine)); 
     grid->attach(this); 

     setCanvasBackground(QColor(29, 100, 141)); 

     curve = new QwtPlotCurve("TEAS Intensity"); 
     curve->setRenderHint(QwtPlotItem::RenderAntialiased); 
     curve->setStyle(QwtPlotCurve::Lines); 
     curve->setCurveAttribute(QwtPlotCurve::Fitted, true); 
     curveFitter = new QwtSplineCurveFitter(); 
     curveFitter->setSplineSize(150); 
     curve->setCurveFitter(curveFitter); 
     curve->setPen(QPen(Qt::yellow)); 
     curve->setYAxis(QwtPlot::yLeft); 
     curve->attach(this); 

     QwtSymbol sym; 
     sym.setStyle(QwtSymbol::Ellipse); 
     sym.setPen(QPen(Qt::black,2)); 
     sym.setSize(9); 
    
     curve->setSymbol(sym); 

     curve2 = new QwtPlotCurve("Pressure"); 
     curve2->setRenderHint(QwtPlotItem::RenderAntialiased); 
     curve2->setStyle(QwtPlotCurve::Lines); 
     curve2->setCurveAttribute(QwtPlotCurve::Fitted, true); 
     curve2->setCurveFitter(curveFitter); 
     curve2->setPen(QPen(Qt::yellow)); 
     curve2->setYAxis(QwtPlot::yRight); 
     curve2->attach(this); 

     curve3 = new QwtPlotCurve("Temperature"); 
     curve3->setRenderHint(QwtPlotItem::RenderAntialiased); 
     curve3->setStyle(QwtPlotCurve::Lines); 
     curve3->setCurveAttribute(QwtPlotCurve::Fitted, true); 
     curve3->setCurveFitter(curveFitter); 
     curve3->setPen(QPen(Qt::green)); 
     curve3->setYAxis(QwtPlot::yLeft); 
     curve3->attach(this); 

     showCurve(curve, true); 
     showCurve(curve2, false); 
     showCurve(curve3, false); 
     enableZoomMode(false); 

     connect(this, SIGNAL(legendChecked(QwtPlotItem *, bool)), SLOT(showCurve(QwtPlotItem *, bool))); 
    
     xMax = 1.0; 
     xMin = 0.0; 
     yMax = 1.0; 
     yMin = -0.05; 

     setAutoReplot(true);
     } 

void TimeScanPlot::showCurve(QwtPlotItem *item, bool on)
     {
     item->setVisible(on);
     QWidget *w = legend()->find(item);
     if ( w && w->inherits("QwtLegendItem") ) 
          {
          ((QwtLegendItem *)w)->setChecked(on);
     
          }
     replot();
     }

void TimeScanPlot::enableZoomMode(bool on)
     {
     if( on ) 
          { 
          teasPanner->setEnabled(on); 
          
          teasZoomer->setEnabled(on);
          teasZoomer->setZoomBase(true); 
          teasZoomer->zoom(0);

          teasPicker->setEnabled(!on); 
          } 
     else 
          {  
          teasZoomer->setZoomBase(true); 
          teasZoomer->zoom(0);
          teasZoomer->setEnabled(on);

          teasPanner->setEnabled(on); 

          teasPicker->setEnabled(!on); 
          } 

     // showInfo();
     }

void TimeScanPlot::startTimeScan()
     {  
     int32 error = 0;  
     char errBuff[2048]={'\0'}; 
     char source[] = "OnboardClock"; 
     char teasInputChan[25], pressInputChan[25], tempInputChan[25]; 
     uInt64 samplesPerChanTeas, samplesPerChanOther; 

     teasCurrentSize = 0; 
     markerCount = 0; 
     // iterationTime = (int)(theTimeScanParams[0]*1000); 

     sprintf(teasInputChan, "Dev1/ai%d", theIndicesList[0]); 
     sprintf(pressInputChan, "Dev1/ai%d", theIndicesList[1]); 
     sprintf(tempInputChan, "Dev1/ai%d", theIndicesList[2]); 

     printf("TEAS input channel: %s", teasInputChan); 
     printf("Pressure input channel: %s", pressInputChan); 
     printf("Temperature input channel: %s", tempInputChan); 

     teasChanMin = (float64)DACVals[0]; 
     teasChanMax = (float64)DACVals[1]; 
     pressChanMin = (float64)DACVals[2]; 
     pressChanMax = (float64)DACVals[3]; 
     tempChanMin = (float64)DACVals[4]; 
     tempChanMax = (float64)DACVals[5]; 
     sampleRate = (float64)DACVals[6]; 

     samplesPerChanTeas = (uInt64)(theTimeScanParams[0]*1.1); 
     samplesPerChanOther = (uInt64)((theTimeScanParams[0]/pow(2.0, theIndicesList[3]-2.0))*1.1); 
     nSamplesTeas = (uInt32)(theTimeScanParams[0]); 
     nSamplesOther = (uInt32)(theTimeScanParams[0]/pow(2.0, theIndicesList[3]-2.0)); 
     
     printf ("samplesPerChanTeas: %ld\n", (long int)samplesPerChanTeas); 
     printf ("samplesPerChanOther: %ld\n", (long int)samplesPerChanOther); 
     printf ("nSamplesTeas: %ld\n", (long int)nSamplesTeas); 
     printf ("nSamplesOther: %ld\n", (long int)nSamplesOther); 

     DAQmxErrChk (DAQmxBaseCreateTask ("Teas reading", &teasTskHdl)); 
     DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (teasTskHdl, teasInputChan, "", 
                    DAQmx_Val_Diff, teasChanMin, teasChanMax, DAQmx_Val_Volts, NULL)); 
     DAQmxErrChk (DAQmxBaseCfgSampClkTiming (teasTskHdl, source, sampleRate, 
                    DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samplesPerChanTeas)); 
                    
     printf ("Channel %s initialized for TEAS intensity readings\n", teasInputChan); 
     
     DAQmxErrChk (DAQmxBaseCreateTask ("Pressure reading", &pressTskHdl)); 
     DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (pressTskHdl, pressInputChan, "", 
                    DAQmx_Val_Diff, pressChanMin, pressChanMax, DAQmx_Val_Volts, NULL)); 
     DAQmxErrChk (DAQmxBaseCfgSampClkTiming (pressTskHdl, source, sampleRate, 
                    DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samplesPerChanOther)); 
                    
     printf ("Channel %s initialized for pressure intensity readings\n", pressInputChan); 

     DAQmxErrChk (DAQmxBaseCreateTask ("Temperature reading", &tempTskHdl)); 
     DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (tempTskHdl, tempInputChan, "", 
                    DAQmx_Val_Diff, tempChanMin, tempChanMax, DAQmx_Val_Volts, NULL)); 
     DAQmxErrChk (DAQmxBaseCfgSampClkTiming (tempTskHdl, source, sampleRate, 
                    DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samplesPerChanOther)); 
                    
     printf ("Channel %s initialized for temperature intensity readings\n", tempInputChan); 

     scanTime.start(); 
     timerID = startTimer(1); 

     Error:
          if (DAQmxFailed (error)) 
               DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
          if (error) 
               { 
               printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
               return; 
               } 
     }

void TimeScanPlot::stopTimeScan()
     {  
     int32 error = 0;  
     char errBuff[2048]={'\0'}; 

     (void)killTimer(timerID); 
     
     inputScanComments(); 
     setZeroLevel(); 
     save(); 

     DAQmxErrChk (DAQmxBaseClearTask (teasTskHdl)); 
     DAQmxErrChk (DAQmxBaseClearTask (pressTskHdl)); 
     DAQmxErrChk (DAQmxBaseClearTask (tempTskHdl)); 
     
     Error:
          if (DAQmxFailed (error)) 
               DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
          if (error) 
               { 
               printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
               return; 
               } 
     } 

void TimeScanPlot::setZeroLevel()
     { 
     QMessageBox *msgBox1 = new QMessageBox(this); 
     msgBox1->setWindowTitle(tr("Setting zero level")); 
     msgBox1->setIcon(QMessageBox::Warning);        
     msgBox1->setStandardButtons(QMessageBox::Ok); 
     msgBox1->setText(tr("Please press OK to measure zero intensity level")); 
     msgBox1->exec(); 

     setZeroMarker(); 

     return; 
     }      

void TimeScanPlot::setZeroMarker() 
     { 
     int32 pointsToReadZero = -1; 
     int32 pointsReadZero; 
     int32 error = 0;  
     char errBuff[2048]={'\0'}; 
     uInt32 i; 
     unsigned long peakCenter, deltak; 
     FILE *zeroOut; 
     
     // We use two arrays because the NI routines need float64 whereas 
     // four1 requires a double vector allocated by means of dvector 
     
     float64 dataZero[nSamplesTeas]; 
     double *dataFFT, fft, freq; 
     
     QwtPlotMarker *my0p = new QwtPlotMarker(); 
     my0p->setLabelOrientation(Qt::Horizontal);
     my0p->setLineStyle(QwtPlotMarker::HLine);
     my0p->setLinePen(QPen(Qt::black, 1, Qt::SolidLine)); 
     
     DAQmxErrChk (DAQmxBaseStartTask (teasTskHdl)); 
     DAQmxErrChk (DAQmxBaseReadAnalogF64(teasTskHdl, pointsToReadZero, timeout, 
                    DAQmx_Val_GroupByChannel, dataZero, nSamplesTeas, &pointsReadZero, NULL)); 
     DAQmxErrChk (DAQmxBaseStopTask (teasTskHdl)); 

     dataFFT = dvector(1, 2*nSamplesTeas); 
     dataFFT[0] = 0.0; 
          
     for (i = 1; i <= nSamplesTeas; i++) 
          { 
          dataFFT[2*i - 1] = dataZero[i - 1];     // data values are only real 
          dataFFT[2*i] = 0.0;                     // imaginary part of data = 0.0 
          } 
          
     dfour1 (dataFFT, nSamplesTeas, 1); 

	peakCenter = 0.053222656*(nSamplesTeas/2) + 1; 
	printf ("peakCenter: %ld\n", peakCenter); 
	
	// The number of samples spanning the peak depends on the length 
	// of the sampling period 
	
	deltak = (int)nSamplesTeas/8192;    
	printf ("deltak: %ld\n", deltak); 
	
	// Output results for test purposes and calculate background intensity 
	
	zeroInt = 0.0; 
	zeroOut = fopen ("/tmp/salidaZero.dat", "w"); 
	
	for (i = 1; i <= nSamplesTeas; i += 2) 
	     { 
	     fft = dataFFT[i]*dataFFT[i] + dataFFT[i + 1]*dataFFT[i + 1]; 
	     freq = 5000.0*(double)i/(double)nSamplesTeas; 
	     fprintf(zeroOut, "%lf %lf\n", freq, fft/(double)nSamplesTeas); 
	     
	     if (i >= peakCenter*2 + 1 - 6*deltak && i < peakCenter*2 + 1 - 2*deltak) 
	          {
	          printf ("LOW-ZERO: freq: %lf, Int: %lf\n", freq, fft/(double)nSamplesTeas); 
	          zeroInt += fft/(double)nSamplesTeas; 
	          } 
	     
	     // skip peak region 
	     
	     if (i > peakCenter*2 + 1 + 2*deltak && i <= peakCenter*2 + 1 + 6*deltak) 
	          {
	          printf ("HIGH-ZERO: freq: %lf, Int: %lf\n", freq, fft/(double)nSamplesTeas); 
	          zeroInt += fft/(double)nSamplesTeas; 
	          } 
	     } 
	
	zeroInt = zeroInt/(double)(4*deltak); 
	printf ("Teas intensity: %lf, # readings: %ld\n", TeasInt, 2*deltak + 1); 
	
	free_dvector(dataFFT, 1, 2*nSamplesTeas); 
	
	my0p->setLabel(tr("Background intensity level")); 
     my0p->setLabelAlignment(Qt::AlignRight | Qt::AlignTop); 
     my0p->setYValue(zeroInt); 
     my0p->attach(this); 
     
     setAutoReplot(true); 

     return; 

     Error:
          if (DAQmxFailed (error)) 
               DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
          if (error) 
               { 
               printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
               return; 
               } 
     } 

void TimeScanPlot::graphPrint()
     { 
     setTitle(timeScanPrintFile); 
     setCanvasBackground(QColor(255, 255, 255)); 
     grid->enableXMin(false);
     grid->enableYMin(false);
     grid->setMajPen(QPen(Qt::gray, 0, Qt::DotLine));  

     curve->setPen(QPen(Qt::black));
 
     if (zeroInt < yMin)
          yMin = zeroInt; 
     
     xMap.setScaleInterval(xMin, 1.15*xMax); 
     yMap.setScaleInterval(yMin - fabs(0.15*(yMax - yMin)), yMax + 0.15*(yMax - yMin)); 
     setAxisScale(xBottom, xMin, 1.15*xMax);
     setAxisScale(yLeft, yMin - fabs(0.15*(yMax - yMin)), yMax + 0.15*(yMax - yMin));

     replot(); 

     return; 
     }

void TimeScanPlot::plotReset()
     {
     delete curve;
     curve = NULL;  
     shutterOpen = false; 
     shutterClosed = false; 
     }

void TimeScanPlot::showData(int count)
     {
     curve->setData(xVal, yVal, count); 
     curve2->setData(xVal, yVal2, count); 
     curve3->setData(xVal, yVal3, count); 
     }

void TimeScanPlot::drawContents(QPainter *painter)
     {
     const QRect &r = contentsRect();

     xMap.setPaintInterval(r.left(), r.right());
     yMap.setPaintInterval(r.top(), r.bottom());
     curve->draw(painter, xMap, yMap, r);
     }

void TimeScanPlot::timerEvent(QTimerEvent *)
     {
     if (teasCurrentSize < Size-1)
          { 
          newValue(); 
          repaint(); 
          } 
     }

void TimeScanPlot::newValue()
     {
     const bool doReplot = autoReplot();
     setAutoReplot(false); 

     double TeasInt = 0.0; 
     unsigned long peakCenter, deltak; 
	
     int32 error = 0;  
     char errBuff[2048] = {'\0'}; 
     uInt32 i; 
     FILE *teasOut; 
     
     // We use two arrays because the NI routines need float64 to store the data  
     // whereas four1() requires a double vector allocated by means of dvector 
     
     double *FFTTeasData, aver, fft, freq; 
     float64 dataTeas[nSamplesTeas], dataPress[nSamplesOther], dataTemp[nSamplesOther]; 
     
     int32 pointsToReadTeas = -1; 
     int32 pointsReadTeas; 
     int32 pointsToReadPress = -1; 
     int32 pointsReadPress; 
     int32 pointsToReadTemp = -1; 
     int32 pointsReadTemp; 

     /****                   data acquisition                   *****/ 

     printf ("Acquiring TEAS intensity data...\n"); 
     
     DAQmxErrChk (DAQmxBaseStartTask (teasTskHdl)); 
     DAQmxErrChk (DAQmxBaseReadAnalogF64(teasTskHdl, pointsToReadTeas, timeout, 
                    DAQmx_Val_GroupByChannel, dataTeas, nSamplesTeas, &pointsReadTeas, NULL)); 
     
     FFTTeasData = dvector(1, 2*nSamplesTeas); 
     FFTTeasData[0] = 0.0; 
     
     for (i = 1; i <= nSamplesTeas; i++) 
          { 
          FFTTeasData[2*i - 1] = (double)dataTeas[i - 1];       // data values are only real 
          FFTTeasData[2*i] = 0.0;                               // imaginary part of data = 0.0 
          } 
          
     dfour1 (FFTTeasData, nSamplesTeas, 1); 

	peakCenter = 0.053222656*(nSamplesTeas/2) + 1; 
	printf ("peakCenter: %ld\n", peakCenter); 
	
	// The number of samples spanning the peak depends on the length 
	// of the sampling period 
	
	deltak = (int)nSamplesTeas/8192;    
	printf ("deltak: %ld\n", deltak); 
	
	// Output results for test purposes and calculate background intensity 
	
	TeasInt = 0.0; 
	teasOut = fopen ("/tmp/salidaTEAS.dat", "w"); 
	
	for (i = 1; i <= nSamplesTeas; i += 2) 
	     { 
	     fft = FFTTeasData[i]*FFTTeasData[i] + FFTTeasData[i + 1]*FFTTeasData[i + 1]; 
	     freq = 5000.0*(double)i/(double)nSamplesTeas; 
	     fprintf(teasOut, "%lf %lf\n", freq, fft/(double)nSamplesTeas); 
	     
          if (i >= peakCenter*2 + 1 - 2*deltak && i <= peakCenter*2 + 1 + 2*deltak) 
	          {
	          printf ("PEAK: freq: %lf, Int: %lf\n", freq, fft/(double)nSamplesTeas); 
	          TeasInt += fft/(double)nSamplesTeas; 
	          } 
	     } 
	
	TeasInt = TeasInt/(double)(2*deltak + 1); 
	printf ("Teas intensity: %lf, # readings: %ld\n", TeasInt, 2*deltak + 1); 
	
	free_dvector(FFTTeasData, 1, 2*nSamplesTeas); 

     yVal[teasCurrentSize] = TeasInt; 
     
     DAQmxErrChk (DAQmxBaseStopTask (teasTskHdl)); 
     
     printf ("Acquiring pressure intensity data...\n"); 
     
     DAQmxErrChk (DAQmxBaseStartTask(pressTskHdl)); 
     DAQmxErrChk (DAQmxBaseReadAnalogF64(pressTskHdl, pointsToReadPress, timeout, 
                    DAQmx_Val_GroupByChannel, dataPress, nSamplesOther, &pointsReadPress, NULL)); 

     for (i = 0, aver = 0.0; i < nSamplesOther; i++) 
          aver += (double)dataPress[i]; 
     aver = aver/(double)nSamplesOther; 
     yVal2[teasCurrentSize] = aver; 
     DAQmxErrChk (DAQmxBaseStopTask (pressTskHdl)); 

     printf ("Acquiring temperature intensity data...\n"); 
     
     DAQmxErrChk (DAQmxBaseStartTask(tempTskHdl)); 
     DAQmxErrChk (DAQmxBaseReadAnalogF64(tempTskHdl, pointsToReadTemp, timeout, 
                    DAQmx_Val_GroupByChannel, dataTemp, nSamplesOther, &pointsReadTemp, NULL)); 

     for (i = 0, aver = 0.0; i < nSamplesOther; i++) 
          aver += (double)dataTemp[i]; 
     aver = aver/(double)nSamplesOther; 
     yVal3[teasCurrentSize] = aver; 
     DAQmxErrChk (DAQmxBaseStopTask (tempTskHdl)); 

     xVal[teasCurrentSize] = scanTime.elapsed()/double(1000.0); 
     
     printf ("# acquired datapoints: %d - Elapsed time: %lf\n", teasCurrentSize + 1, xVal[teasCurrentSize]); 

     if (xVal[teasCurrentSize] > xMax)
          xMax = xVal[teasCurrentSize]; 
     if (xVal[teasCurrentSize] < xMin)
          xMin = xVal[teasCurrentSize]; 
     if (yVal[teasCurrentSize] > yMax)
          yMax = yVal[teasCurrentSize]; 
     if (yVal[teasCurrentSize] < yMin)
          yMin = yVal[teasCurrentSize]; 

     if (xMax >= xMapMax) 
          xMapMax = 1.15*xMax; 
     if (xMin <= xMapMin) 
          xMapMin = 1.15*xMin; 
     if (yMax >= yMapMax) 
          yMapMax = 1.15*yMax; 
     if (yMin <= yMapMin) 
          yMapMin = 1.15*yMin; 

     xMap.setScaleInterval(xMapMin, xMapMax); 
     yMap.setScaleInterval(yMapMax, yMapMin); 
     setAxisScale(xBottom, xMapMin, xMapMax);
     setAxisScale(yLeft, yMapMin, yMapMax);

     curve->setRawData(xVal, yVal, teasCurrentSize); 
     curve2->setRawData(xVal, yVal2, teasCurrentSize); 
     curve3->setRawData(xVal, yVal3, teasCurrentSize); 
 
     teasCurrentSize++;

     showData(teasCurrentSize); 

     setAutoReplot(doReplot);
     teasUpdateNumLabel(); 
     emit newScanPointAdded(true); 
     replot(); 

     Error:
          if (DAQmxFailed (error)) 
               DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
          if (error) 
               { 
               printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
               return; 
               } 
     } 

void TimeScanPlot::openShutter()
     { 
     shutterOpen = true; 
     QwtPlotMarker *mX = new QwtPlotMarker(); 
     mX->setLabel(tr("Shutter open")); 
     mX->setLabelAlignment(Qt::AlignRight | Qt::AlignTop);
     mX->setLabelOrientation(Qt::Horizontal);
     mX->setLineStyle(QwtPlotMarker::VLine);
     mX->setLinePen(QPen(Qt::black, 1, Qt::DashLine)); 
     shutterOpenTime = scanTime.elapsed()/double(1000.0); 
     mX->setXValue(shutterOpenTime);
     mX->attach(this); 
     
     setAutoReplot(true);

     return; 
     } 

void TimeScanPlot::closeShutter()
     { 
     shutterClosed = true; 
     QwtPlotMarker *mX2 = new QwtPlotMarker(); 
     mX2->setLabel(tr("Shutter closed")); 
     mX2->setLabelAlignment(Qt::AlignRight | Qt::AlignBottom);
     mX2->setLabelOrientation(Qt::Horizontal);
     mX2->setLineStyle(QwtPlotMarker::VLine);
     mX2->setLinePen(QPen(Qt::black, 1, Qt::DashLine)); 
     shutterCloseTime = scanTime.elapsed()/double(1000.0); 
     mX2->setXValue(shutterCloseTime);
     mX2->attach(this); 
     
     setAutoReplot(true);

     return; 
     } 

void TimeScanPlot::inputScanComments()
     {   
     bool ok; 
     QString scanCommentLabel; 
     scanCommentLabel.insert(0, tr("Enter comments for this scan                                  ")); 
           
     scanComments = QInputDialog::getText(this, tr("Scan comments"), scanCommentLabel, 
               QLineEdit::Normal, "", &ok); 
     }

void TimeScanPlot::setVMarker()
     { 
     mX3 = new QwtPlotMarker(); 
     mX3->setLineStyle(QwtPlotMarker::VLine); 
     mX3->setLinePen(QPen(Qt::red, 1, Qt::DashDotLine)); 
     markerTime[markerCount] = scanTime.elapsed()/double(1000.0); 
     mX3->setXValue(markerTime[markerCount]); 
     mX3->attach(this); 

     bool ok; 
     QString dialogLabel; 
     dialogLabel.insert(0, tr("Enter description of marker Nr. ")); 
     dialogLabel.append(QString::number(markerCount+1)); 
     dialogLabel.append("                          "); 
      
     QString text = QInputDialog::getText(this, tr("Marker description"), dialogLabel, QLineEdit::Normal, "", &ok); 
     
     if ( ok ) 
          {
          markerLabel[markerCount] = text; 
          }

     markerCount++;      

     setAutoReplot(true);
     } 

QString TimeScanPlot::teasUpdateNumLabel()
     {
     QString numText; 
     numText.sprintf("                Number of datapoints: %d", teasCurrentSize); 
     
     return numText; 
     }

void TimeScanPlot::paintEvent(QPaintEvent *event)
     {
     QFrame::paintEvent(event);

     QPainter thisPainter(this);
     thisPainter.setClipRect(contentsRect());
     }

void TimeScanPlot::getSettings(QStringList settings, double* scanParams, int* indices, double* DACSettings) 
     { 
     theSettingsList = settings; 
     theTimeScanParams = scanParams; 
     theIndicesList = indices; 
     DACVals = DACSettings; 
     }

void TimeScanPlot::save() 
     { 
     QFile outFile(theSettingsList[0]); 
     if (!outFile.open(QIODevice::WriteOnly | QIODevice::Text)) 
          return; 

     QStringList pressUnits; 
     pressUnits << " " << "mBar" << "Pascal" << "Torr" ; 

     QTextStream out(&outFile); 

     out << "# " << theSettingsList[1] << ", " << theSettingsList[2] << "\n"; 
     out << "# TEAS time scan \n"; 
     out << "# Second header line \n"; 
     out << "# TEAS Intensity input channel: Analog Input " << theIndicesList[0]+1 << "\n"; 
     out << "# TEAS DAC input voltage range: " << QChar(0x00B1) << teasChanMax << "V \n"; 
     out << "# Pressure input channel: Analog Input " << theIndicesList[1]+1 << "\n"; 
     out << "# Pressure DAC input voltage range: " << QChar(0x00B1) << pressChanMax << "V \n"; 
     out << "# Pressure units: " << pressUnits[theIndicesList[4]] << "\n"; 
     out << "# AML Gauge sensitivity factor: " << theTimeScanParams[1] << " 1/" \
          << pressUnits[theIndicesList[4]] << "\n"; 
     out << "# AML Gauge emission current: " << theTimeScanParams[2] << " mA\n"; 
     out << "# Temperature input channel: Analog Input " << theIndicesList[2]+1 << "\n"; 
     out << "# Temperature DAC input voltage range: " << QChar(0x00B1) << tempChanMax << "V \n"; 
     out << "# Sampling rate: " << sampleRate << " Hz" << "\n"; 
     out << "# Number of samples per data point: " << theSettingsList[3] << "\n"; 
     out << "# Number of samples per data point: " << theTimeScanParams[0] << " sec\n"; 
     out << "# Sample/System: " << theSettingsList[4] << "\n"; 
     out << "# Channeltron bias voltage: " << theSettingsList[5] << " V\n"; 

     out << "# Shutter open at t = " ; 
     if ( shutterOpen == true ) 
          out << shutterOpenTime << " sec \n"; 
     else 
          out << " n/a \n"; 
     out << "# Shutter closed at t = " ; 
     if ( shutterClosed == true ) 
          out << shutterCloseTime << " sec \n"; 
     else 
          out << " n/a \n"; 

     out << "Background intensity: " << zeroInt << "\n"; 
     
     for (int i = 0; i < markerCount; i++)
          { 
          out << "# Marker # " << i+1 << " @ t = " << markerTime[i] << " sec \n"; 
          out << "# Description of Marker # " << i+1 << ": " ; 
               out << markerLabel[i] ; 
          out << "\n"; 
          } 

     out << "# Scan comments: \n"; 
     out << "# " << scanComments << "\n"; 
     out << "# t \t TEAS Intensity \t Pressure \t Temperature \n";      

     for (int j = 0; j < teasCurrentSize; j++) 
          {
          out << xVal[j] << "\t" << yVal[j] << "\t" << yVal2[j] << "\t" << yVal3[j] << "\n";           
          }

     outFile.close(); 
     timeScanPrintFile = theSettingsList[0]; 

     if( theSettingsList[0].endsWith(".dat") )
          {
          theSettingsList[0].chop(4); 
          }
     bool ok; 
     int fileNumber = theSettingsList[0].right(3).toInt(&ok, 10); 
     if ( ok )
          {
          fileNumber++; 
          theSettingsList[0].chop(3); 
          char str[4]; 
          sprintf(str, "%03d", fileNumber); 
          QString fileNumberString = QString::fromAscii(str);                
          theSettingsList[0].append(fileNumberString); 
          theSettingsList[0].append(".dat"); 
          }          
     else
          {
          theSettingsList[0].append("_001.dat"); 
          } 

     QFile dataFile("./FILENAME"); 
     if (dataFile.open(QIODevice::ReadWrite | QIODevice::Text))
          { 
          QTextStream inout( &dataFile ); 
          dataFile.resize(theSettingsList[0].length()); 
          inout << theSettingsList[0]; 
          dataFile.close(); 
          } 

     emit scanCompleted(true); 

     return;  
     } 

