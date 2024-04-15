#include <QApplication> 
#include <QGridLayout>  
#include <QString> 
#include <QTextStream>  
#include <QProgressBar>
#include <QStatusBar>
#include <qtoolbar.h>
#include <qtoolbutton.h>
#include <qlabel.h> 
#include <qprintdialog.h>
#include <qprinter.h> 
#include <qdatetime.h> 
#include <qwt_plot.h>

// #include <qfileinfo.h>

#include "pixmaps.h" 
#include "mokeplot.h" 
#include "mokeloopplot.h" 
#include "save.xpm" 
// #include "start.xpm" 
#include "quit.xpm"  

double MaxField; 
double iterTime; 
QString mokeFileName;  
QStatusBar *mokeStatusBar; 
QLabel *mokeDataFileLabel, *mokeSaveWarning; 
QToolButton *btnNewScan; 

MokePlot::MokePlot(QWidget *) 
     { 
     miPlot = new MokeLoopPlot; 

	QToolBar *toolBar = new QToolBar(miPlot); 
     toolBar->setAllowedAreas(Qt::TopToolBarArea | Qt::BottomToolBarArea); 
     toolBar->setToolButtonStyle(Qt::ToolButtonTextUnderIcon); 

     btnStart = new QToolButton(miPlot); 
	btnStart->setText(tr("&Start")); 
     btnStart->setIcon(QIcon(quit_xpm)); 
	btnStart->setCheckable(true); 
	btnStart->setToolButtonStyle(Qt::ToolButtonTextUnderIcon); 

	toolBar->addWidget(btnStart); 

     toolBar->addSeparator(); 

	QToolButton *btnZoom = new QToolButton(miPlot); 
	btnZoom->setText("Zoom"); 
	btnZoom->setIcon(QIcon(zoom_xpm)); 
	btnZoom->setCheckable(true); 
	btnZoom->setToolButtonStyle(Qt::ToolButtonTextUnderIcon); 

	toolBar->addWidget(btnZoom); 

	QToolButton *btnPrint = new QToolButton(toolBar); 
	btnPrint->setText("Print"); 
	btnPrint->setIcon(QIcon(print_xpm)); 
	btnPrint->setToolButtonStyle(Qt::ToolButtonTextUnderIcon); 

	toolBar->addWidget(btnPrint); 

	toolBar->addSeparator(); 

	btnNewScan = new QToolButton(toolBar); 
	btnNewScan->setText(tr("&New Scan")); 
	btnNewScan->setIcon(QIcon(save_xpm)); 
	btnNewScan->setToolButtonStyle(Qt::ToolButtonTextUnderIcon); 
     btnNewScan->setEnabled(false); 

	toolBar->addWidget(btnNewScan); 

     toolBar->addSeparator(); 

     connect(btnStart, SIGNAL(toggled(bool)), this, SLOT(runScan(bool))); 
     connect(btnStart, SIGNAL(toggled(bool)), this, SLOT(isRunning(bool))); 

	connect(btnZoom, SIGNAL(toggled(bool)), miPlot, SLOT(enableZoomMode(bool))); 
	connect(btnPrint, SIGNAL(clicked()), this, SLOT(preparePrint())); 
	connect(btnNewScan, SIGNAL(clicked()), this, SLOT(launchNewScan())); 

     mokeStatusBar = new QStatusBar(miPlot); 

     QProgressBar *progressBar = new QProgressBar(miPlot); 
     progressBar->setRange(0, 100); 
     progressBar->setOrientation(Qt::Horizontal); 
     progressBar->setAlignment(Qt::AlignCenter); 
     progressBar->setMinimumWidth(280); 
     progressBar->setFormat(tr("Loop scan progress: %p%")); 
     progressBar->setValue(0); 
     connect(miPlot, SIGNAL(progress(int)), progressBar, SLOT(setValue(int))); 

     QLabel *blankLabel = new QLabel; 
     blankLabel->setMinimumWidth(20); 

     mokeDataFileLabel = new QLabel; 
     mokeDataFileLabel->setFont(QFont("Helvetica", 10)); 
     mokeDataFileLabel->setAlignment(Qt::AlignLeft); 

     mokeSaveWarning = new QLabel; 
     mokeSaveWarning->setTextFormat(Qt::RichText); 
     mokeSaveWarning->setText("<font color=white>&nbsp;&nbsp;&nbsp;Datafile not saved!&nbsp;&nbsp;&nbsp;</font>"); 
     mokeSaveWarning->setFont(QFont("Helvetica", 10)); 
     mokeSaveWarning->setFrameStyle(QFrame::Panel | QFrame::Raised); 
     mokeSaveWarning->setIndent(0); 
     mokeSaveWarning->setAlignment(Qt::AlignHCenter); 
     mokeSaveWarning->setPalette(QPalette(qRgb(255,25,15))); 
     mokeSaveWarning->setAutoFillBackground(true); 

     mokeStatusBar->addWidget(mokeSaveWarning); 
     mokeStatusBar->addWidget(blankLabel); 
     mokeStatusBar->addWidget(progressBar); 
     mokeStatusBar->addPermanentWidget(mokeDataFileLabel); 

	QVBoxLayout *plotLayout = new QVBoxLayout; 

	plotLayout->addWidget(toolBar); 
	plotLayout->addWidget(miPlot); 
     plotLayout->addWidget(mokeStatusBar); 

	setLayout(plotLayout); 

     connect(miPlot, SIGNAL(scanCompleted(bool)), this, SLOT(blockButtons())); 
     } 

void MokePlot::passSettings(QStringList settings, double* parameterList, int* mokeIndices, 
     double *mokeDACSettings) 
     { 
     mokeFileName = settings[0]; 
     mokeDataFileLabel->setText(settings[0]); 
     miPlot->getSettings(settings, parameterList, mokeIndices, mokeDACSettings); 
     } 

void MokePlot::setScanParameters(double* parameterList) 
     { 
     MaxField = 1.15*parameterList[0]; 

     miPlot->resetXScale(MaxField);  
     } 

void MokePlot::runScan(bool on) 
     { 
     if ( on ) 
          {
          printf ("entering runScan\n"); 
          miPlot->startLoopScan(); 
          } 
     else 
          miPlot->stopLoopScan(); 
     } 

void MokePlot::isRunning(bool on) 
     { 
     if ( on ) 
          { 
          printf ("Entering isRunning and changing btnStart label\n"); 
          btnStart->setText("&Stop"); 
          } 
     else 
          btnStart->setText("&Start"); 
     } 

void MokePlot::blockButtons() 
     { 
     btnStart->setEnabled(false); 
     btnNewScan->setEnabled(true); 
     mokeSaveWarning->setText("<font color=black>&nbsp;&nbsp;&nbsp;Datafile saved!&nbsp;&nbsp;&nbsp;</font>"); 
     mokeSaveWarning->setPalette(QPalette(qRgb(25,255,75))); 
     mokeStatusBar->update(); 
     } 

void MokePlot::launchNewScan() 
     { 
     miPlot->plotReset(); 
     emit newScan(true); 
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

void MokePlot::preparePrint() 
     { 
     miPlot->graphPrint(); 
     print(); 
     } 

void MokePlot::print() 
     { 
     QPrinter printer(QPrinter::HighResolution); 

     if( mokeFileName.endsWith(".dat") ) 
          mokeFileName.chop(4); 

     mokeFileName.append(".pdf"); 

     printer.setOutputFileName(mokeFileName); 

     QString docName = miPlot->title().text(); 
     if ( !docName.isEmpty() ) 
          { 
          docName.replace (QRegExp (QString::fromLatin1 ("\n")), tr (" -- ")); 
          printer.setDocName (docName); 
          } 

     printer.setCreator("Measurement graph"); 
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

