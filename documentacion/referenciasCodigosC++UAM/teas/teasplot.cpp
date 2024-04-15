#include <QApplication> 
#include <QGridLayout>  
#include <QString> 
#include <QTextStream> 
#include <QStatusBar> 
#include <qtoolbar.h>
#include <qtoolbutton.h>
#include <qlabel.h> 
#include <qprintdialog.h>
#include <qprinter.h> 
#include <qdatetime.h> 

// #include <qfileinfo.h>

#include "pixmaps.h" 
#include "teasplot.h" 
#include "timescanplot.h" 
//#include "save.xpm" 
#include "start.xpm" 
//#include "quit.xpm" 

#include "NIDAQmxBase.h" 

QString timeScanFileName;  
QStatusBar *timeScanStatusBar; 
QLabel *timeScanDataFileLabel, *timeScanSaveWarning, *teasNumberPoints; 
QToolButton *btnNewTimeScan; 

TeasPlot::TeasPlot(QWidget *) 
     {	     
     miPlot = new TimeScanPlot; 
 
	QToolBar *toolBar = new QToolBar(miPlot);
     toolBar->setAllowedAreas(Qt::TopToolBarArea | Qt::BottomToolBarArea);
     toolBar->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

     btnStart = new QToolButton(miPlot);
	btnStart->setText(tr("&Start")); 
     btnStart->setIcon(QIcon(start_xpm)); 
	btnStart->setCheckable(true);
	btnStart->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

	toolBar->addWidget(btnStart); 

     toolBar->addSeparator(); 
     
     btnShtOpen = new QToolButton(miPlot); 
     btnShtOpen->setText("Shutter &Open");
	btnShtOpen->setIcon(QIcon(start_xpm)); 
     btnShtOpen->setCheckable(true); 
	btnShtOpen->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

     toolBar->addWidget(btnShtOpen);  

     btnMarker = new QToolButton(miPlot); 
     btnMarker->setText("Set &Marker");
	btnMarker->setIcon(QIcon(start_xpm)); 
     btnMarker->setCheckable(false); 
	btnMarker->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

     toolBar->addWidget(btnMarker);  

     toolBar->addSeparator(); 

	QToolButton *btnZoom = new QToolButton(miPlot);
	btnZoom->setText("Zoom");
	btnZoom->setIcon(QIcon(zoom_xpm));
	btnZoom->setCheckable(true);
	btnZoom->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

	toolBar->addWidget(btnZoom);

	btnNewTimeScan = new QToolButton(toolBar);
	btnNewTimeScan->setText(tr("&New Scan"));
	btnNewTimeScan->setIcon(QIcon(start_xpm));
	btnNewTimeScan->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

	toolBar->addWidget(btnNewTimeScan); 

	QToolButton *btnPrint = new QToolButton(toolBar);
	btnPrint->setText("Print");
	btnPrint->setIcon(QIcon(print_xpm));
	btnPrint->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);

	toolBar->addWidget(btnPrint); 

	toolBar->addSeparator(); 

     connect(btnStart, SIGNAL(toggled(bool)), this, SLOT(runScan(bool)));
     connect(btnStart, SIGNAL(toggled(bool)), this, SLOT(isRunning(bool))); 

     connect(btnShtOpen, SIGNAL(toggled(bool)), this, SLOT(markShutterOpen(bool))); 
     connect(btnMarker, SIGNAL(clicked()), miPlot, SLOT(setVMarker())); 

	connect(btnZoom, SIGNAL(toggled(bool)), miPlot, SLOT(enableZoomMode(bool))); 
	connect(btnPrint, SIGNAL(clicked()), this, SLOT(preparePrint())); 
	connect(btnNewTimeScan, SIGNAL(clicked()), this, SLOT(launchNewScan())); 

     timeScanStatusBar = new QStatusBar(miPlot); 

     teasNumberPoints = new QLabel; 
     teasNumberPoints->setFont(QFont("Helvetica", 10)); 
     teasNumberPoints->setAlignment(Qt::AlignHCenter); 
     teasNumberPoints->setText(miPlot->teasUpdateNumLabel()); 

     timeScanDataFileLabel = new QLabel; 
     timeScanDataFileLabel->setFont(QFont("Helvetica", 10)); 
     timeScanDataFileLabel->setAlignment(Qt::AlignLeft); 

     timeScanSaveWarning = new QLabel; 
     timeScanSaveWarning->setTextFormat(Qt::RichText); 
     timeScanSaveWarning->setText("<font color=white>&nbsp;&nbsp;&nbsp;Datafile not saved!&nbsp;&nbsp;&nbsp;</font>"); 
     timeScanSaveWarning->setFont(QFont("Helvetica", 10)); 
     timeScanSaveWarning->setFrameStyle(QFrame::Panel | QFrame::Raised); 
     timeScanSaveWarning->setIndent(0); 
     timeScanSaveWarning->setAlignment(Qt::AlignHCenter); 
     timeScanSaveWarning->setPalette(QPalette(qRgb(255,25,15)));
     timeScanSaveWarning->setAutoFillBackground(true);

     timeScanStatusBar->addWidget(timeScanSaveWarning); 
     timeScanStatusBar->addWidget(teasNumberPoints); 
     timeScanStatusBar->addPermanentWidget(timeScanDataFileLabel); 

	QVBoxLayout *plotLayout = new QVBoxLayout;
	
	plotLayout->addWidget(toolBar); 
	plotLayout->addWidget(miPlot); 
     plotLayout->addWidget(timeScanStatusBar); 
     
	setLayout(plotLayout); 

     connect(miPlot, SIGNAL(scanCompleted(bool)), this, SLOT(blockButtons())); 
     connect(miPlot, SIGNAL(newScanPointAdded(bool)), this, SLOT(updateScanNumberPoints())); 
     }

void TeasPlot::passSettings(QStringList expSettings, double* params, int* indices, double *DACSettings) 
     { 
     timeScanFileName = expSettings[0]; 
     timeScanDataFileLabel->setText(expSettings[0]); 
     miPlot->getSettings(expSettings, params, indices, DACSettings); 
     } 

void TeasPlot::runScan(bool on)
     {
     if ( on ) 
          miPlot->startTimeScan(); 
     else
          miPlot->stopTimeScan(); 
     }

void TeasPlot::isRunning(bool on)
     {
     if ( on ) 
          btnStart->setText("&Stop"); 
     else 
          btnStart->setText("&Start"); 
     }

void TeasPlot::updateScanNumberPoints() 
     { 
     teasNumberPoints->setText(miPlot->teasUpdateNumLabel()); 
     timeScanStatusBar->update(); 
     }

void TeasPlot::blockButtons()
     {
     btnStart->setEnabled(false); 
     btnNewTimeScan->setEnabled(true); 
     btnShtOpen->setEnabled(false); 
     btnMarker->setEnabled(false); 
     timeScanSaveWarning->setText("<font color=black>&nbsp;&nbsp;&nbsp;Datafile saved!&nbsp;&nbsp;&nbsp;</font>"); 
     timeScanSaveWarning->setPalette(QPalette(qRgb(25,255,75))); 
     timeScanStatusBar->update(); 
     }

void TeasPlot::launchNewScan() 
     { 
     miPlot->plotReset(); 
     emit newScan(true); 
     }

void TeasPlot::markShutterOpen(bool on) 
     {
     if ( on )
          { 
          miPlot->openShutter(); 
          btnShtOpen->setText("Shutter &Closed"); 
          btnShtOpen->setIcon(QIcon(start_xpm));  
          } 
     else 
          {
          miPlot->closeShutter();           
          btnShtOpen->setText("Shutter &Open");  
          btnShtOpen->setIcon(QIcon(start_xpm));  
          }  
     }

/*
void MiWidget::showInfo(QString text)
{
    if ( text == QString::null )
    {
        if ( d_picker->rubberBand() )
            text = "Cursor Pos: Press left mouse button in plot region";
        else
            text = "Zoom: Press mouse button and drag";
    }

#ifndef QT_NO_STATUSBAR
    statusBar()->showMessage(text); 
#endif
}
*/ 

void TeasPlot::preparePrint()
     { 
     miPlot->graphPrint(); 
     print(); 
     }

void TeasPlot::print()
     {
     QPrinter printer(QPrinter::HighResolution); 

     if( timeScanFileName.endsWith(".dat") )
          timeScanFileName.chop(4); 

     timeScanFileName.append(".pdf"); 

     printer.setOutputFileName(timeScanFileName);

     QString docName = miPlot->title().text();
     if ( !docName.isEmpty() )
          {
          docName.replace (QRegExp (QString::fromLatin1 ("\n")), tr (" -- "));
          printer.setDocName (docName);
          }

     printer.setCreator("Test example");
     printer.setOrientation(QPrinter::Landscape);

     QPrintDialog dialog(&printer);
     if ( dialog.exec() )
          {
          QwtPlotPrintFilter filter;
          if ( printer.colorMode() == QPrinter::GrayScale )
               {
               int options = QwtPlotPrintFilter::PrintAll;
               options &= ~QwtPlotPrintFilter::PrintBackground;
               options |= QwtPlotPrintFilter::PrintFrameWithScales;
               filter.setOptions(options);
               }
          miPlot->print(printer, filter);
          }
     }

