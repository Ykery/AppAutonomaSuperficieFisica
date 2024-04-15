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

#include "mokeloopplot.h" 
#include "NIDAQmxBase.h" 

#define DAQmxErrChk(functionCall) { if( DAQmxFailed(error=(functionCall)) ) { goto Error; } } 
#define FIELD_CAL 5.0/600.0   // Calibration factor for magnetic field 

//
// Variables visible to all functions 
// 

// int i1st, iPoint, iLoop, ns; 
int iScan, iPoint, nP; 
int nPoints, nScans, mokeIterTime, mokeWaitTime;  
bool firstMag; 

double *mokeInt1st, *mokeDC1st, *mokeNormal1st, *mokeTemp1st; 
double **mokeInt, **mokeDCLevel, **mokeNormal, **mokeTemp; 
double *fieldH, *fieldH1st, *mokeIntAver; 

double *mokeLoopParameters; 
double mokeZeroPlus, mokeZeroMinus; 
double mokeDCZeroPlus, mokeDCZeroMinus; 
double mokeNormalZeroPlus, mokeNormalZeroMinus; 
double maxHField, dH, partial; 
double* mokeDACVals; 

QString mokeScanComments, mokePrintFile; 
QStringList mokeTheSettingsList; 
int* mokeTheIndicesList; 

QwtPlotGrid *mokeGrid; 
QwtPlotMarker *mokeMX3; 
QMessageBox *mokeMsgBox; 
QTime dwellTime; 

TaskHandle mokeTskHdl = 0; 
TaskHandle mokeDCTskHdl = 0; 
TaskHandle mokeTempTskHdl = 0; 
TaskHandle mokeFieldTskHdl = 0; 

uInt32 nSamplesMoke, nSamplesMokeTemp; 
float64 mokeIntChanMin, mokeIntChanMax, mokeDCLevelChanMin, mokeDCLevelChanMax; 
float64 mokeTempChanMin, mokeTempChanMax, mokeSampleRate; 
float64 mokeTimeout = 10.0; 

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
      
      setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton, 
                     Qt::ControlModifier); 

      setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton); 
      } 
   }; 

MokeLoopPlot::MokeLoopPlot(QWidget *) 
   { 
   setAutoReplot(false); 
   
   QwtSplineCurveFitter* curveFitter; 
   
   setTitle("MOKE Hysteresis Loop"); 
   
   QwtLegend *legend = new QwtLegend; 
   legend->setItemMode(QwtLegend::CheckableItem); 
   insertLegend(legend, QwtPlot::RightLegend); 
   
   setFrameStyle(QFrame::Box|QFrame::Raised); 
   setLineWidth(1); 
   setMargin(10); 
   setCanvasLineWidth(2); 
   
   xMapMin = -1.0; 
   xMapMax = 1.0; 
   yMapMin = -1.0; 
   yMapMax = 1.0; 
   
   xMap.setScaleInterval(xMapMin, xMapMax); 
   yMap.setScaleInterval(yMapMax, yMapMin); 
   
   setAxisScale(xBottom, xMapMin, xMapMax); 
   setAxisScale(yLeft, yMapMin, yMapMax); 
   
   setAxisTitle(xBottom, tr("Magnetic Field (Oe)")); 
   setAxisTitle(yLeft, tr("Intensity (arb. un.)")); 
   
   mokePicker = new QwtPlotPicker(QwtPlot::xBottom, QwtPlot::yLeft, 
                  QwtPicker::PointSelection | QwtPicker::DragSelection, 
                  QwtPlotPicker::CrossRubberBand, QwtPicker::AlwaysOn, 
                  canvas()); 
   mokePicker->setRubberBandPen(QColor(Qt::green)); 
   mokePicker->setRubberBand(QwtPicker::CrossRubberBand); 
   mokePicker->setTrackerPen(QColor(Qt::white)); 
   
   mokePanner = new QwtPlotPanner(canvas()); 
   mokePanner->setMouseButton(Qt::MidButton); 
   
   mokeZoomer = new Zoomer(QwtPlot::xBottom, QwtPlot::yLeft, canvas()); 
   mokeZoomer->setRubberBand(QwtPicker::RectRubberBand); 
   mokeZoomer->setRubberBandPen(QColor(Qt::green)); 
   mokeZoomer->setTrackerMode(QwtPicker::ActiveOnly); 
   mokeZoomer->setTrackerPen(QColor(Qt::white)); 
   
   mokeGrid = new QwtPlotGrid; 
   mokeGrid->enableXMin(true); 
   mokeGrid->enableYMin(true); 
   mokeGrid->setMajPen(QPen(Qt::white, 0, Qt::DotLine)); 
   mokeGrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine)); 
   mokeGrid->attach(this); 
   
   setCanvasBackground(QColor(131, 25, 70)); 
   
   curve = new QwtPlotCurve("1st Magnetization"); 
   curve->setRenderHint(QwtPlotItem::RenderAntialiased); 
   curve->setStyle(QwtPlotCurve::Lines); 
   curve->setCurveAttribute(QwtPlotCurve::Fitted, true); 
   curveFitter = new QwtSplineCurveFitter(); 
   curveFitter->setSplineSize(150); 
   curve->setCurveFitter(curveFitter); 
   curve->setPen(QPen(Qt::yellow)); 
   curve->setYAxis(QwtPlot::yLeft); 
   curve->attach(this); 

   curve2 = new QwtPlotCurve("Loop series"); 
   curve2->setRenderHint(QwtPlotItem::RenderAntialiased); 
   curve2->setStyle(QwtPlotCurve::Lines); 
   curve2->setCurveAttribute(QwtPlotCurve::Fitted, true); 
   curve2->setCurveFitter(curveFitter); 
   curve2->setPen(QPen(Qt::green)); 
   curve2->setYAxis(QwtPlot::yLeft); 
   curve2->attach(this); 

   curve3 = new QwtPlotCurve("Averaged loop"); 
   curve3->setRenderHint(QwtPlotItem::RenderAntialiased); 
   curve3->setStyle(QwtPlotCurve::Lines); 
   curve3->setCurveAttribute(QwtPlotCurve::Fitted, true); 
   curve3->setCurveFitter(curveFitter); 
   curve3->setPen(QPen(Qt::blue)); 
   curve3->setYAxis(QwtPlot::yLeft); 
   curve3->attach(this); 

   QwtSymbol sym3; 
   sym3.setStyle(QwtSymbol::Ellipse); 
   sym3.setPen(QPen(Qt::black,2)); 
   sym3.setSize(9); 

   curve3->setSymbol(sym3); 

   showCurve(curve, true); 
   showCurve(curve2, true); 
   showCurve(curve3, true); 
   enableZoomMode(false); 

   connect(this, SIGNAL(legendChecked(QwtPlotItem *, bool)), 
            SLOT(showCurve(QwtPlotItem *, bool))); 

   xMax = 1.0; 
   xMin = 0.0; 
   yMax = 1.0; 
   yMin = -1.0; 

   setAutoReplot(true); 
   } 

void MokeLoopPlot::resetXScale(double xMax) 
   { 
   xMap.setScaleInterval(-xMax, xMax); 
   setAxisScale(xBottom, -xMax, xMax); 
   } 

void MokeLoopPlot::showCurve(QwtPlotItem *item, bool on) 
   { 
   item->setVisible(on); 
   QWidget *w = legend()->find(item); 
   if ( w && w->inherits("QwtLegendItem") ) 
         ((QwtLegendItem *)w)->setChecked(on); 

   replot(); 
   } 

void MokeLoopPlot::enableZoomMode(bool on) 
   { 
   if ( on ) 
      { 
      mokePanner->setEnabled(on); 

      mokeZoomer->setEnabled(on); 
      mokeZoomer->setZoomBase(true); 
      mokeZoomer->zoom(0); 

      mokePicker->setEnabled(!on); 
      } 
   else 
      { 
      mokeZoomer->setZoomBase(true); 
      mokeZoomer->zoom(0); 
      mokeZoomer->setEnabled(on); 

      mokePanner->setEnabled(on); 

      mokePicker->setEnabled(!on); 
      } 

      // showInfo(); 
   } 

void MokeLoopPlot::startLoopScan() 
   { 
   int32 error = 0; 
   char errBuff[2048]={'\0'}; 
   float64 minAOVol = 0.0;
   float64 maxAOVol = 5.0; 

   maxHField = mokeLoopParameters[0]; 
   double points = mokeLoopParameters[1]; 
   nScans = (int)mokeLoopParameters[2]; 
   mokeWaitTime = (int)(mokeLoopParameters[3]*1000); // time in milliseconds 
   mokeIterTime = (int)(mokeLoopParameters[4]*1000); // time in milliseconds 

   // Make sure that the loop contains an odd number of points to account for 
   // two datapoints at +HMax (initial and final), one at -HMax and two at H=0 

   nPoints = (int)(points + 4*(1 - fabs ((points-5)/4 - (int)((points-5)/4))));  

   dH = 4*maxHField/(nPoints-1);       // magnetic field step between points 
     
   // Allocate memory for data arrays 

   mokeInt1st = (double*)calloc(nPoints, sizeof(double)); 
   mokeDC1st = (double*)calloc(nPoints, sizeof(double)); 
   mokeNormal1st = (double*)calloc(nPoints, sizeof(double)); 
   mokeTemp1st = (double*)calloc(nPoints, sizeof(double)); 
   fieldH1st = (double*)calloc(nPoints, sizeof(double)); 
   fieldH = (double*)calloc(nPoints, sizeof(double)); 
   mokeInt = (double**)calloc(nScans, sizeof(double)); 
   mokeDCLevel = (double**)calloc(nScans, sizeof(double)); 
   mokeNormal = (double**)calloc(nScans, sizeof(double)); 
   mokeTemp = (double**)calloc(nScans, sizeof(double)); 
   
   for (iScan = 0; iScan < nScans; iScan++) 
      { 
      mokeInt[iScan] = (double*)calloc(nPoints, sizeof(double)); 
      mokeDCLevel[iScan] = (double*)calloc(nPoints, sizeof(double)); 
      mokeNormal[iScan] = (double*)calloc(nPoints, sizeof(double)); 
      mokeTemp[iScan] = (double*)calloc(nPoints, sizeof(double)); 
      } 
   mokeIntAver = (double*)calloc(nPoints, sizeof(double)); 

   // Generate the corresponding field values 

   // 1st magnetization curve: first pad the rest of the loop field values with 
   // zeros, then generate the field values starting at 0 and ending at +Hmax 

   for (iPoint = 0; iPoint < 3*(nPoints-5)/4 + 3; iPoint++) 
      { 
      fieldH1st[iPoint] = 0.0; 
      mokeInt1st[iPoint] = 0.0; 
      } 

   for (iPoint = 3*(nPoints-5)/4 + 3; iPoint < nPoints; iPoint++) 
      fieldH1st[iPoint] = dH*(iPoint - (3*(nPoints-5)/4 + 3)); 

   // field values for the complete loop, starting and finishing at +Hmax 

   for (iPoint = 0; iPoint < (nPoints-5)/2 + 3; iPoint++) 
      fieldH[iPoint] = maxHField - dH*iPoint; 

   for (iPoint = 0; iPoint < (nPoints-5)/2 + 2; iPoint++) 
      fieldH[iPoint + (nPoints-5)/2 + 3] = -maxHField + dH*(iPoint + 1); 

   firstMag = true; 

   // Create DAQ Tasks 

   uInt64 samplesPerChanMoke, samplesPerChanMokeTemp; 
   float64 *dataMoke, *dataMokeTemp; 

   mokeIntChanMin = (float64)mokeDACVals[0]; 
   mokeIntChanMax = (float64)mokeDACVals[1]; 
   mokeDCLevelChanMin = (float64)mokeDACVals[2]; 
   mokeDCLevelChanMax = (float64)mokeDACVals[3]; 
   mokeTempChanMin = (float64)mokeDACVals[4]; 
   mokeTempChanMax = (float64)mokeDACVals[5]; 
   mokeSampleRate = (float64)(mokeDACVals[6]); 

   char source[] = "OnboardClock"; 
   char mokeIntInputChan[25], mokeTempInputChan[25]; 
   char mokeDCLevelInputChan[25], mokeFieldOutputChan[25]; 

   samplesPerChanMoke = (uInt64)(mokeLoopParameters[4]*mokeSampleRate*1.1); 
   samplesPerChanMokeTemp = (uInt64)(mokeLoopParameters[4]*mokeSampleRate*1.1/20.0); 
   nSamplesMoke = (uInt32)(mokeLoopParameters[4]*mokeSampleRate); 
   nSamplesMokeTemp = (uInt32)(mokeLoopParameters[4]*mokeSampleRate/20); 

   dataMoke = (float64*)calloc(nSamplesMoke, sizeof(float64)); 
   dataMokeTemp = (float64*)calloc(nSamplesMokeTemp, sizeof(float64)); 
     
   sprintf(mokeIntInputChan, "Dev1/ai%d", mokeTheIndicesList[0]-1); 
   sprintf(mokeDCLevelInputChan, "Dev1/ai%d", mokeTheIndicesList[1]-1); 
   sprintf(mokeTempInputChan, "Dev1/ai%d", mokeTheIndicesList[2]-1); 
   sprintf(mokeFieldOutputChan, "Dev1/ao%d", mokeTheIndicesList[3]-1); 

   DAQmxErrChk (DAQmxBaseCreateTask ("Temperature reading", &mokeTempTskHdl)); 
   DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (mokeTempTskHdl, 
               mokeTempInputChan, "", DAQmx_Val_Diff, mokeTempChanMin, 
               mokeTempChanMax, DAQmx_Val_Volts, NULL)); 
   DAQmxErrChk (DAQmxBaseCfgSampClkTiming (mokeTempTskHdl, source, 
               mokeSampleRate, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 
               samplesPerChanMokeTemp)); 

   DAQmxErrChk (DAQmxBaseCreateTask ("MOKE DC level", &mokeDCTskHdl)); 
   DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (mokeDCTskHdl, 
               mokeDCLevelInputChan, "", DAQmx_Val_Diff, mokeDCLevelChanMin, 
               mokeDCLevelChanMax, DAQmx_Val_Volts, NULL)); 
   DAQmxErrChk (DAQmxBaseCfgSampClkTiming (mokeDCTskHdl, source, mokeSampleRate, 
               DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samplesPerChanMoke)); 

   DAQmxErrChk (DAQmxBaseCreateTask ("MOKE intensity", &mokeTskHdl)); 
   DAQmxErrChk (DAQmxBaseCreateAIVoltageChan (mokeTskHdl, mokeIntInputChan, "", 
               DAQmx_Val_Diff, mokeIntChanMin, mokeIntChanMax, DAQmx_Val_Volts, 
               NULL)); 
   DAQmxErrChk (DAQmxBaseCfgSampClkTiming (mokeTskHdl, source, mokeSampleRate, 
               DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, samplesPerChanMoke)); 

   DAQmxErrChk (DAQmxBaseCreateTask("Field output",&mokeFieldTskHdl));
   DAQmxErrChk (DAQmxBaseCreateAOVoltageChan (mokeFieldTskHdl, 
               mokeFieldOutputChan, "", minAOVol, maxAOVol, DAQmx_Val_Volts, 
               NULL));
   DAQmxErrChk (DAQmxBaseStartTask(mokeFieldTskHdl)); 
   
   nP = 0; 
   firstMag = true; 
   iPoint = 3*(nPoints-5)/4 + 3; 
   iScan = 0; 

   mokeTimerID = startTimer(1); 

   Error:
      if (DAQmxFailed (error)) 
         DAQmxBaseGetExtendedErrorInfo (errBuff, 2048);
 
      if (error) 
         { 
         printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
            return; 
         } 
   } 

void MokeLoopPlot::timerEvent(QTimerEvent *) 
   { 
   newValue(); 
   repaint(); 
   } 

void MokeLoopPlot::newValue() 
   { 
   int32 error = 0; 
   uInt32 j; 
   char errBuff[2048]={'\0'}; 
   double aver; 
   int partial; 
   float64 fieldData; 
   float64 dataMoke[nSamplesMoke]; 
   float64 dataMokeTemp[nSamplesMokeTemp]; 

   const bool doReplot = autoReplot(); 
   setAutoReplot(false); 

   int32 pointsToReadMoke = -1; 
   int32 pointsReadMoke; 
   int32 pointsToReadMokeDC = -1; 
   int32 pointsReadMokeDC; 
   int32 pointsToReadMokeTemp = -1; 
   int32 pointsReadMokeTemp; 
   uInt64 pointsToWriteField = 1; 
   int32 pointsWrittenField; 

   // Start measurement loop 

   if ( firstMag )    // First magnetization curve starts at H = 0 
      { 
      // Generate magnetic field first 

      fieldData = fabs((float64)fieldH1st[iPoint]*FIELD_CAL); 
      
      DAQmxErrChk (DAQmxBaseWriteAnalogF64 (mokeFieldTskHdl, 
                  pointsToWriteField, 0, mokeTimeout, DAQmx_Val_GroupByChannel, 
                  &fieldData, &pointsWrittenField, NULL)); 

      // Start timer and wait dwellTime for stabilization 

      dwellTime.start(); 
      do 
         { 
         if (dwellTime.elapsed() >= mokeWaitTime) 
            break; 
         } 
            while (1); 

      // Read sample temperature first 
      // to allow for further stabilization of MOKE signal  

      DAQmxErrChk (DAQmxBaseStartTask (mokeTempTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeTempTskHdl, 
                  pointsToReadMokeTemp, mokeTimeout, 0, dataMokeTemp, 
                  nSamplesMokeTemp, &pointsReadMokeTemp, NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeTempTskHdl)); 

      for (j = 0, aver = 0.0; j < nSamplesMokeTemp; j++) 
         aver += (double)dataMokeTemp[j]; 
      aver = aver/(double)nSamplesMokeTemp; 
      mokeTemp1st[iPoint] = aver; 

      // Then read MOKE DC level 

      DAQmxErrChk (DAQmxBaseStartTask (mokeDCTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeDCTskHdl, pointsToReadMokeDC, 
                  mokeTimeout, 0, dataMoke, nSamplesMoke, &pointsReadMokeDC, 
                  NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeDCTskHdl)); 

      for (j = 0, aver = 0.0; j < nSamplesMoke; j++) 
         aver += (double)dataMoke[j]; 
      aver = aver/(double)nSamplesMoke; 
      mokeDC1st[iPoint] = aver; 

      // Finally read MOKE intensity 

      DAQmxErrChk (DAQmxBaseStartTask (mokeTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeTskHdl, pointsToReadMoke, 
                  mokeTimeout, 0, dataMoke, nSamplesMoke, &pointsReadMoke, 
                  NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeTskHdl)); 

      for (j = 0, aver = 0.0; j < nSamplesMoke; j++) 
         aver += (double)dataMoke[j]; 
      aver = aver/(double)nSamplesMoke; 
      mokeInt1st[iPoint] = aver; 

      // Normalize MOKE intensity to DC level 

      if (mokeDC1st[iPoint] != 0.0) 
         mokeNormal1st[iPoint] = mokeInt1st[iPoint]/mokeDC1st[iPoint]; 

      if (mokeNormal1st[iPoint] > yMax) 
         yMax = mokeNormal1st[iPoint]; 
      if (mokeNormal1st[iPoint] < yMin) 
         yMin = mokeNormal1st[iPoint]; 

      if (yMax >= yMapMax) 
         yMapMax = 1.15*yMax; 
      if (yMin <= yMapMin) 
         yMapMin = 1.15*yMin; 

      yMap.setScaleInterval(yMapMax, yMapMin); 
      setAxisScale(yLeft, yMapMin, yMapMax); 

      partial = 100*((nP + 1)/(double)(nPoints*nScans + (nPoints - 5)/4 + 2)); 

      emit progress((int)partial); 

      curve->setRawData(fieldH1st, mokeNormal1st, iPoint + 1); 

      showMokeData(curve, fieldH1st, mokeNormal1st, iPoint + 1); 

      setAutoReplot(doReplot); 

      replot(); 

      if (fieldH1st[iPoint] >= maxHField) 
         { 
         nP++; 
         firstMag = false; 
         iPoint = 0; 

         return; 
         } 
      else 
         { 
         nP++; 
         iPoint++; 
         } 
      return; 
      } 
   else     // full loops sweep from +Hmax down to -Hmax and back to +Hmax again 
      { 

      // Generate magnetic field first 
      
      fieldData = fabs((float64)fieldH[iPoint]*FIELD_CAL); 

      DAQmxErrChk (DAQmxBaseWriteAnalogF64 (mokeFieldTskHdl, 
                  pointsToWriteField, 0, mokeTimeout, DAQmx_Val_GroupByChannel, 
                  &fieldData, &pointsWrittenField, NULL));

      // Start timer and wait dwellTime for stabilization 

      dwellTime.start(); 
      do 
         { 
         if (dwellTime.elapsed() >= mokeWaitTime) 
            break; 
         } 
            while (1); 

      // Read sample temperature first 
      // to allow for further stabilization of MOKE signal 

      DAQmxErrChk (DAQmxBaseStartTask (mokeTempTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeTempTskHdl, 
                  pointsToReadMokeTemp, mokeTimeout, 0, dataMokeTemp, 
                  nSamplesMokeTemp, &pointsReadMokeTemp, NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeTempTskHdl)); 

      for (j = 0, aver = 0.0; j < nSamplesMokeTemp; j++) 
         aver += (double)dataMokeTemp[j]; 
      aver = aver/(double)nSamplesMokeTemp; 
      mokeTemp[iScan][iPoint] = aver; 

      // Then read MOKE DC level 

      DAQmxErrChk (DAQmxBaseStartTask (mokeDCTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeDCTskHdl, pointsToReadMokeDC, 
                  mokeTimeout, 0, dataMoke, nSamplesMoke, &pointsReadMokeDC, 
                  NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeDCTskHdl)); 

      for (j = 0, aver = 0.0; j < nSamplesMoke; j++) 
         aver += (double)dataMoke[j]; 
      aver = aver/(double)nSamplesMoke; 
      mokeDCLevel[iScan][iPoint] = aver; 

      // Finally read MOKE intensity 

      DAQmxErrChk (DAQmxBaseStartTask (mokeTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeTskHdl, pointsToReadMoke, 
                  mokeTimeout, 0, dataMoke, nSamplesMoke, &pointsReadMoke, 
                  NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeTskHdl)); 

      for (j = 0, aver = 0.0; j < nSamplesMoke; j++) 
         aver += (double)dataMoke[j]; 
      aver = aver/(double)nSamplesMoke; 
      // mokeInt[iScan][iPoint] = aver; 
      mokeInt[iScan][iPoint] = aver*(iScan + 1); 

      // Normalize MOKE intensity to DC level 

      if (mokeDCLevel[iScan][iPoint] != 0.0) 
         mokeNormal[iScan][iPoint] = mokeInt[iScan][iPoint]/mokeDCLevel[iScan][iPoint]; 

      partial = 100*((nP + 1)/(double)(nPoints*nScans + (nPoints - 5)/4 + 2)); 

      emit progress((int)partial); 

      if (mokeNormal[iScan][iPoint] > yMax) 
         yMax = mokeNormal[iScan][iPoint]; 
      if (mokeNormal[iScan][iPoint] < yMin) 
         yMin = mokeNormal[iScan][iPoint]; 

      if (yMax >= yMapMax) 
         yMapMax = 1.15*yMax; 
      if (yMin <= yMapMin) 
         yMapMin = 1.15*yMin; 

      yMap.setScaleInterval(yMapMax, yMapMin); 
      setAxisScale(yLeft, yMapMin, yMapMax);        
      curve2->setRawData(fieldH, mokeNormal[iScan], iPoint + 1); 
      showMokeData(curve2, fieldH, mokeNormal[iScan], iPoint + 1); 

      curve3->setRawData(fieldH, mokeIntAver, nPoints); 
      showMokeData(curve3, fieldH, mokeIntAver, nPoints); 

      setAutoReplot(doReplot); 

      replot(); 
      nP++; 
      iPoint++; 
      if ( iPoint == nPoints) 
         { 
         iPoint = 0; 
         averageScans(iScan); 
         iScan++; 
         } 
      if ( iScan == nScans ) 
         { 
         // averageScans(iScan); 
         iPoint = iScan = 0; 
         stopLoopScan(); 
         } 
      } 

   Error: 
      if (DAQmxFailed (error)) 
         DAQmxBaseGetExtendedErrorInfo (errBuff, 2048); 

      if (error) 
         { 
         printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
            return; 
         } 
   } 

void MokeLoopPlot::averageScans(int scan) 
   { 
   // After finishing each sweep, first correct the signal drift by assuming 
   // that it is linear in time - make the two datapoints at +Hmax coincide, 
   // then average all the completed sweeps into a resulting loop 

   // double drift; 
   printf ("Averaging scans ... \n"); 

   const bool doReplot = autoReplot(); 
   setAutoReplot(false); 

   for (i = 0; i < nPoints; i++) 
      mokeIntAver[i] += mokeNormal[scan][i]; 
/* 
   drift = (mokeNormal[scan][nPoints - 1] - 
            mokeNormal[scan][0])/(double)(nPoints - 1); 
   printf ("drift: %lf\n", drift); 

   const bool doReplot = autoReplot(); 
   setAutoReplot(false); 

   for (i = 0; i < nPoints; i++) 
      mokeIntAver[i] += mokeNormal[scan][i]; 
*/ 
   setAutoReplot(doReplot); 

   replot(); 
   
   printf ("Exiting averageScans\n"); 
   return; 
   } 

void MokeLoopPlot::stopLoopScan() 
   { 
   int32 error = 0; 
   char errBuff[2048]={'\0'}; 
   uInt64 pointsToWriteField = 1; 
   int32 pointsWrittenField; 
   float64 fieldData = 0.0; 
     
   printf ("Stopping loop...\n"); 

   // set analog output channel to 0 V before shutting down 
      
   DAQmxErrChk (DAQmxBaseWriteAnalogF64 (mokeFieldTskHdl, pointsToWriteField, 
               0, mokeTimeout, DAQmx_Val_GroupByChannel, &fieldData, 
               &pointsWrittenField, NULL));
   DAQmxErrChk (DAQmxBaseStopTask (mokeFieldTskHdl)); 
   
   (void)killTimer(mokeTimerID); 

   inputScanComments(); 
   getLockinZeros(); 
   save(); 

   DAQmxErrChk (DAQmxBaseClearTask (mokeTskHdl)); 
   DAQmxErrChk (DAQmxBaseClearTask (mokeDCTskHdl)); 
   DAQmxErrChk (DAQmxBaseClearTask (mokeTempTskHdl)); 
   DAQmxErrChk (DAQmxBaseClearTask (mokeFieldTskHdl)); 

   Error: 
      if (DAQmxFailed (error)) 
         DAQmxBaseGetExtendedErrorInfo (errBuff, 2048); 

      if (error) 
         { 
         printf ("DAQmxBase Error %ld: %s\n", (long)error, errBuff); 
            return; 
         } 
   } 

void MokeLoopPlot::getLockinZeros() 
   { 
   QMessageBox *mokeMsgBox1 = new QMessageBox(this); 
   mokeMsgBox1->setWindowTitle(tr("Set Lock-in zero levels")); 
   mokeMsgBox1->setIcon(QMessageBox::Warning); 
   mokeMsgBox1->setStandardButtons(QMessageBox::Ok); 
   bool isPlus = true; 
   mokeMsgBox1->setText(tr("Please set +90 deg. phase in the Lock-in amplifier \nand press OK")); 
   mokeMsgBox1->exec(); 

   setZeroMarker(isPlus); 

   QMessageBox *mokeMsgBox2 = new QMessageBox(this); 
   mokeMsgBox2->setWindowTitle(tr("Set Lock-in zero levels")); 
   mokeMsgBox2->setIcon(QMessageBox::Warning); 
   mokeMsgBox2->setStandardButtons(QMessageBox::Ok); 
   isPlus = false; 
   mokeMsgBox2->setText(tr("Now please set -90 deg. phase in the Lock-in amplifier \nand press OK again")); 
   mokeMsgBox2->exec(); 

   setZeroMarker(isPlus); 

   return; 
   } 

void MokeLoopPlot::setZeroMarker(bool plus) 
   { 
   int32 pointsToReadMokeZero = -1; 
   int32 pointsReadMokeZero; 
   int32 error = 0; 
   char errBuff[2048]={'\0'}; 
   float64 dataZeroMoke[nSamplesMoke]; 
   uInt32 i; 

   printf ("Acquiring Lock-in zeros\n"); 

   QwtPlotMarker *my0p = new QwtPlotMarker(); 
   my0p->setLabelOrientation(Qt::Horizontal); 
   my0p->setLineStyle(QwtPlotMarker::HLine); 
   my0p->setLinePen(QPen(Qt::black, 1, Qt::SolidLine)); 

   if ( plus ) 
      { 
      DAQmxErrChk (DAQmxBaseStartTask (mokeTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeTskHdl, 
                  pointsToReadMokeZero, mokeTimeout, 0, dataZeroMoke, 
                  nSamplesMoke, &pointsReadMokeZero, NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeTskHdl)); 

      for (i = 0, mokeZeroPlus = 0.0; i < nSamplesMoke; i++) 
         mokeZeroPlus += (double)dataZeroMoke[i]; 
      mokeZeroPlus = mokeZeroPlus/(double)nSamplesMoke; 

      DAQmxErrChk (DAQmxBaseStartTask (mokeDCTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeDCTskHdl, 
                  pointsToReadMokeZero, mokeTimeout, 0, dataZeroMoke, 
                  nSamplesMoke, &pointsReadMokeZero, NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeDCTskHdl)); 

      for (i = 0, mokeDCZeroPlus = 0.0; i < nSamplesMoke; i++) 
         mokeDCZeroPlus += (double)dataZeroMoke[i]; 
      mokeDCZeroPlus = mokeDCZeroPlus/(double)nSamplesMoke; 

      if (mokeDCZeroPlus != 0.0) 
         mokeNormalZeroPlus = mokeZeroPlus/mokeDCZeroPlus; 

      my0p->setLabel(tr("Lock-in plus 90 deg. zero level")); 
      my0p->setLabelAlignment(Qt::AlignRight | Qt::AlignTop); 
      my0p->setYValue(mokeZeroPlus); 
      } 
   else 
      { 
      DAQmxErrChk (DAQmxBaseStartTask (mokeTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeTskHdl, 
                  pointsToReadMokeZero, mokeTimeout, 0, dataZeroMoke, 
                  nSamplesMoke, &pointsReadMokeZero, NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeTskHdl)); 

      for (i = 0, mokeZeroMinus = 0.0; i < nSamplesMoke; i++) 
         mokeZeroMinus += (double)dataZeroMoke[i]; 
      mokeZeroMinus = mokeZeroMinus/(double)nSamplesMoke; 

      DAQmxErrChk (DAQmxBaseStartTask (mokeDCTskHdl)); 
      DAQmxErrChk (DAQmxBaseReadAnalogF64 (mokeDCTskHdl, 
                  pointsToReadMokeZero, mokeTimeout, 0, dataZeroMoke, 
                  nSamplesMoke, &pointsReadMokeZero, NULL)); 
      DAQmxErrChk (DAQmxBaseStopTask (mokeDCTskHdl)); 

      for (i = 0, mokeDCZeroMinus = 0.0; i < nSamplesMoke; i++) 
         mokeDCZeroMinus += (double)dataZeroMoke[i]; 
      mokeDCZeroMinus = mokeDCZeroMinus/(double)nSamplesMoke; 

      if (mokeDCZeroMinus != 0.0) 
         mokeNormalZeroMinus = mokeZeroMinus/mokeDCZeroMinus; 

      my0p->setLabel(tr("Lock-in minus 90 deg. zero level")); 
      my0p->setLabelAlignment(Qt::AlignRight | Qt::AlignBottom); 
      my0p->setYValue(mokeZeroMinus); 
      } 
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

void MokeLoopPlot::graphPrint() 
   { 
   printf ("Printing graph \n"); 
     
   setTitle(mokePrintFile); 
   setCanvasBackground(QColor(255, 255, 255)); 
   mokeGrid->enableXMin(false); 
   mokeGrid->enableYMin(false); 
   mokeGrid->setMajPen(QPen(Qt::gray, 0, Qt::DotLine)); 

   curve->setPen(QPen(Qt::black)); 

   yMap.setScaleInterval(1.15*yMax, 1.15*yMin); 
   setAxisScale(yLeft, 1.15*yMin, 1.15*yMax); 

   replot(); 

   return; 
   } 

void MokeLoopPlot::plotReset() 
   { 
   delete curve; 
   curve = NULL; 
   } 

void MokeLoopPlot::showMokeData(QwtPlotCurve *c, double *x, double *y, int count) 
   { 
   c->setData(x, y, count); 
   } 

void MokeLoopPlot::drawContents(QPainter *painter) 
   { 
   const QRect &r = contentsRect(); 

   xMap.setPaintInterval(r.left(), r.right()); 
   yMap.setPaintInterval(r.top(), r.bottom()); 
   curve->draw(painter, xMap, yMap, r); 
   } 

void MokeLoopPlot::inputScanComments() 
   { 
   bool ok; 
   QString scanCommentLabel; 
   scanCommentLabel.insert(0, tr("Enter comments for this scan                                  ")); 
   mokeScanComments = QInputDialog::getText(this, tr("Scan comments"), 
               scanCommentLabel, QLineEdit::Normal, "", &ok); 
   } 

void MokeLoopPlot::paintEvent(QPaintEvent *event) 
   { 
   QFrame::paintEvent(event); 

   QPainter thisPainter(this); 
   thisPainter.setClipRect(contentsRect()); 
   } 

void MokeLoopPlot::getSettings(QStringList settings, double* parameters, 
                              int* mokeIndices, double* mokeDACConfigSettings) 
   { 
   mokeTheSettingsList = settings; 
   mokeTheIndicesList = mokeIndices; 
   mokeLoopParameters = parameters; 
   // for (i = 0; i < 5; i++) 
   //      mokeLoopParameters[i] = parameters[i]; 
   mokeDACVals = mokeDACConfigSettings; 
   } 

void MokeLoopPlot::save() 
   { 
   printf("Saving data\n"); 
   QFile outFile(mokeTheSettingsList[0]); 
   if (!outFile.open(QIODevice::WriteOnly | QIODevice::Text)) 
      return; 

   QTextStream out(&outFile); 

   out << "# " << mokeTheSettingsList[1] << ", " << mokeTheSettingsList[2] << "\n"; 
   out << "# MOKE Hysteresis loop scan \n"; 
   out << "# Second header line \n"; 
   out << "# Maximum magnetic field: " << maxHField << " Oe \n"; 
   out << "# Number of data points per loop: " << nPoints << "\n"; 
   out << "# Number of scans to average: " << nScans << "\n"; 
   out << "# Dwell time: " << mokeWaitTime << " msec\n"; 
   out << "# Integration time: " << mokeIterTime << " msec\n"; 

   out << "# MOKE Intensity input channel: Analog Input " << mokeTheIndicesList[0]+1 << "\n"; 
   out << "# MOKE DAC input voltage range: " << QChar(0x00B1) << mokeIntChanMax << "V \n"; 
   out << "# MOKE DC level input channel: Analog Input " << mokeTheIndicesList[1]+1 << "\n"; 
   out << "# MOKE DC level voltage range: " << QChar(0x00B1) << mokeDCLevelChanMax << "V \n"; 
   out << "# Sample Temperature input channel: Analog Input " << mokeTheIndicesList[2]+1 << "\n"; 
   out << "# Temperature DAC input voltage range: " << QChar(0x00B1) << mokeTempChanMax << "V \n"; 
   out << "# Magnetic Field output channel: Analog Output " << mokeTheIndicesList[3]+1 << "\n"; 
   out << "# Sampling rate: " << mokeSampleRate << " Hz" << "\n"; 
   out << "# Lock-in sensitivity: " << mokeTheSettingsList[3] << "\n"; 
   out << "# Lock-in time constant: " << mokeTheSettingsList[4] << "\n"; 
   out << "# System/sample description: " << mokeTheSettingsList[5] << "\n"; 
   out << "# Experimental MOKE geometry: " << mokeTheSettingsList[6] << "\n"; 

   out << "# Lock-in +90 deg. zero level: " << mokeZeroPlus << "\n"; 
   out << "# Lock-in +90 deg. zero DC level: " << mokeDCZeroPlus << "\n"; 
   out << "# Lock-in -90 deg. zero level: " << mokeZeroMinus << "\n"; 
   out << "# Lock-in -90 deg. zero DC level: " << mokeDCZeroMinus << "\n"; 

   out << "# Scan comments: \n"; 
   out << "# " << mokeScanComments << "\n"; 

   out << "# Field 1st \t I Moke 1st \t Temp 1st \t H Field \t Average I Moke "; 
   out << "\t (I Moke[Scan] \t Temp[Scan)xN " << "\n"; 

   // Write measured data 

   for (int j = 0; j < nPoints; j++) 
      { 
      out << fieldH1st[j] << "\t" << mokeInt1st[j] << "\t"; 
      out << mokeDC1st[j] << "\t" << mokeTemp1st [j] << "\t"; 
      out << fieldH[j] << "\t" << mokeIntAver[j] << "\t" << "\t"; 
      for (int k = 0; k < nScans; k++) 
         { 
         out << mokeInt[k][j] << "\t" << mokeDCLevel[k][j] << "\t"; 
         out << mokeTemp[k][j] << "\n"; 
         } 
      } 

   outFile.close(); 
   mokePrintFile = mokeTheSettingsList[0]; 

   if( mokeTheSettingsList[0].endsWith(".dat") ) 
      mokeTheSettingsList[0].chop(4); 
   bool ok; 
   int fileNumber = mokeTheSettingsList[0].right(3).toInt(&ok, 10); 
   if ( ok ) 
      { 
      fileNumber++; 
      mokeTheSettingsList[0].chop(3); 
      char str[4]; 
      sprintf(str, "%03d", fileNumber); 
      QString fileNumberString = QString::fromAscii(str);                  
      mokeTheSettingsList[0].append(fileNumberString); 
      mokeTheSettingsList[0].append(".dat"); 
      } 
   else 
      mokeTheSettingsList[0].append("_001.dat"); 

   QFile dataFile("./FILENAME"); 
   if (dataFile.open(QIODevice::ReadWrite | QIODevice::Text)) 
      { 
      QTextStream inout( &dataFile );  
      dataFile.resize(mokeTheSettingsList[0].length()); 
      inout << mokeTheSettingsList[0]; 
      dataFile.close(); 
      } 

   free(mokeInt1st); 
   free(mokeDC1st); 
   free(mokeNormal1st); 
   free(mokeTemp1st); 
   free(fieldH1st); 
   free(fieldH); 
   free(mokeInt); 
   free(mokeDCLevel); 
   free(mokeNormal); 
   free(mokeTemp); 

   emit scanCompleted(true); 

   return;  
   } 

