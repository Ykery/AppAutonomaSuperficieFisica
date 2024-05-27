#!/usr/bin/python3

import sys
import math
#import Qwt
from PyQt6 import Qwt
import numpy as np

from datetime import datetime
from PyQt6.QtCore import Qt,  QSize, QTimer
from PyQt6.QtGui import QColor,  QPixmap, QFont,  QIcon
from PyQt6.QtWidgets import QMainWindow,  QWidget,  QToolBar,  QToolButton,  QHBoxLayout, QVBoxLayout,  QLabel,  QApplication, QPushButton, QSplitter
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from .componentes.grafica import Plot
 

def logSpace(size, xmin, xmax ):
    if ( ( xmin <= 0.0 ) or ( xmax <= 0.0 ) or ( size <= 0 ) ):
        array = np.zeros(0,float)
        return array
    array = np.zeros(size,float)
    imax = size - 1
    array[0] = xmin
    array[imax] = xmax
    lxmin = math.log( xmin )
    lxmax = math.log( xmax )
    lstep = ( lxmax - lxmin ) / imax 
    for i in range(imax):
        array[i] = math.exp( lxmin + i * lstep )
    return array

play_xpm = ["32 32 2 1 ",
"  c None",
". c black",
"  .                             ",
"  ...                           ",
"  .....                         ",
"  ......                        ",
"  ........                      ",
"  ..........                    ",
"  ............                  ",
"  .............                 ",
"  ...............               ",
"  .................             ",
"  ..................            ",
"  ....................          ",
"  ......................        ",
"  ........................      ",
"  .........................     ",
"  ...........................   ",
"  ...........................   ",
"  .........................     ",
"  ........................      ",
"  ......................        ",
"  ....................          ",
"  ..................            ",
"  .................             ",
"  ...............               ",
"  .............                 ",
"  ............                  ",
"  ..........                    ",
"  ........                      ",
"  ......                        ",
"  .....                         ",
"  ...                           ",
"  .                             "]
pause_xpm = ["32 32 2 1",
"  c None",
". c black",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    ",
"    .......          .......    "]
print_xpm = ["32 32 12 1",
    "a c #ffffff",
    "h c #ffff00",
    "c c #ffffff",
    "f c #dcdcdc",
    "b c #c0c0c0",
    "j c #a0a0a4",
    "e c #808080",
    "g c #808000",
    "d c #585858",
    "i c #00ff00",
    "# c #000000",
    ". c None",
    "................................",
    "................................",
    "...........###..................",
    "..........#abb###...............",
    ".........#aabbbbb###............",
    ".........#ddaaabbbbb###.........",
    "........#ddddddaaabbbbb###......",
    ".......#deffddddddaaabbbbb###...",
    "......#deaaabbbddddddaaabbbbb###",
    ".....#deaaaaaaabbbddddddaaabbbb#",
    "....#deaaabbbaaaa#ddedddfggaaad#",
    "...#deaaaaaaaaaa#ddeeeeafgggfdd#",
    "..#deaaabbbaaaa#ddeeeeabbbbgfdd#",
    ".#deeefaaaaaaa#ddeeeeabbhhbbadd#",
    "#aabbbeeefaaa#ddeeeeabbbbbbaddd#",
    "#bbaaabbbeee#ddeeeeabbiibbadddd#",
    "#bbbbbaaabbbeeeeeeabbbbbbaddddd#",
    "#bjbbbbbbaaabbbbeabbbbbbadddddd#",
    "#bjjjjbbbbbbaaaeabbbbbbaddddddd#",
    "#bjaaajjjbbbbbbaaabbbbadddddddd#",
    "#bbbbbaaajjjbbbbbbaaaaddddddddd#",
    "#bjbbbbbbaaajjjbbbbbbddddddddd#.",
    "#bjjjjbbbbbbaaajjjbbbdddddddd#..",
    "#bjaaajjjbbbbbbjaajjbddddddd#...",
    "#bbbbbaaajjjbbbjbbaabdddddd#....",
    "###bbbbbbaaajjjjbbbbbddddd#.....",
    "...###bbbbbbaaajbbbbbdddd#......",
    "......###bbbbbbjbbbbbddd#.......",
    ".........###bbbbbbbbbdd#........",
    "............###bbbbbbd#.........",
    "...............###bbb#..........",
    "..................###..........."]
zoom_xpm = ["32 32 8 1",
    "# c #000000",
    "b c #c0c0c0",
    "a c #ffffff",
    "e c #585858",
    "d c #a0a0a4",
    "c c #0000ff",
    "f c #00ffff",
    ". c None",
    "..######################........",
    ".#a#baaaaaaaaaaaaaaaaaa#........",
    "#aa#baaaaaaaaaaaaaccaca#........",
    "####baaaaaaaaaaaaaaaaca####.....",
    "#bbbbaaaaaaaaaaaacccaaa#da#.....",
    "#aaaaaaaaaaaaaaaacccaca#da#.....",
    "#aaaaaaaaaaaaaaaaaccaca#da#.....",
    "#aaaaaaaaaabe###ebaaaaa#da#.....",
    "#aaaaaaaaa#########aaaa#da#.....",
    "#aaaaaaaa###dbbbb###aaa#da#.....",
    "#aaaaaaa###aaaaffb###aa#da#.....",
    "#aaaaaab##aaccaaafb##ba#da#.....",
    "#aaaaaae#daaccaccaad#ea#da#.....",
    "#aaaaaa##aaaaaaccaab##a#da#.....",
    "#aaaaaa##aacccaaaaab##a#da#.....",
    "#aaaaaa##aaccccaccab##a#da#.....",
    "#aaaaaae#daccccaccad#ea#da#.....",
    "#aaaaaab##aacccaaaa##da#da#.....",
    "#aaccacd###aaaaaaa###da#da#.....",
    "#aaaaacad###daaad#####a#da#.....",
    "#acccaaaad##########da##da#.....",
    "#acccacaaadde###edd#eda#da#.....",
    "#aaccacaaaabdddddbdd#eda#a#.....",
    "#aaaaaaaaaaaaaaaaaadd#eda##.....",
    "#aaaaaaaaaaaaaaaaaaadd#eda#.....",
    "#aaaaaaaccacaaaaaaaaadd#eda#....",
    "#aaaaaaaaaacaaaaaaaaaad##eda#...",
    "#aaaaaacccaaaaaaaaaaaaa#d#eda#..",
    "########################dd#eda#.",
    "...#dddddddddddddddddddddd##eda#",
    "...#aaaaaaaaaaaaaaaaaaaaaa#.####",
    "...########################..##."]



class Zoomer(Qwt.QwtPlotZoomer):
    def __init__(self, xAxis, yAxis, canvas ):
        Qwt.QwtPlotZoomer.__init__(self, xAxis, yAxis, canvas )
        self.setTrackerMode( Qwt.QwtPicker.DisplayMode.AlwaysOff )
        self.setRubberBand( Qwt.QwtPicker.RubberBand.NoRubberBand )
        # Disable zoom out
        self.setMousePattern( Qwt.QwtEventPattern.MousePatternCode.MouseSelect2, Qt.MouseButton.NoButton )
        

class MainWindow( QWidget ):
    def __init__(self, csv = None, configuracion = None, *args):
        QMainWindow.__init__(self, *args) 
        layout = QVBoxLayout(self)
        layout.setSpacing( 0 )
        layout.setContentsMargins( 0, 0, 0, 0 )
        
        self.tiempo = datetime.now()
        frequency = np.arange(100).tolist()
        amplitude = np.random.rand(100).tolist()
        if csv:
            self.datax = []
            self.datay = []
            for x in csv:
                self.datax.append(x[0])
            for x in csv:
                self.datay.append(x[1])
        else:
            self.datax = frequency
            self.datay = amplitude
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizarDatos)
        self.timer.start(100)
        
        self.d_plot = Plot( self )
        
        margin = 5;
        self.d_plot.setContentsMargins( margin, margin, margin, 0 )
        self.setContextMenuPolicy( Qt.ContextMenuPolicy.NoContextMenu )

        self.d_zoomer=[None,None]
        #self.d_zoomer[0] = Zoomer( Qwt.QwtPlot.Axis.xBottom, Qwt.QwtPlot.Axis.yLeft, self.d_plot.canvas() )
        self.d_zoomer[0] = Zoomer( 2,0, self.d_plot.canvas() )
        self.d_zoomer[0].setRubberBand( Qwt.QwtPicker.RubberBand.RectRubberBand )
        self.d_zoomer[0].setRubberBandPen( QColor( Qt.GlobalColor.green ) )
        self.d_zoomer[0].setTrackerMode( Qwt.QwtPicker.DisplayMode.ActiveOnly )
        self.d_zoomer[0].setTrackerPen( QColor( Qt.GlobalColor.white ) )

        # self.d_zoomer[1] = Zoomer( Qwt.QwtPlot.Axis.xTop, Qwt.QwtPlot.Axis.yRight, self.d_plot.canvas() )
        self.d_zoomer[1] = Zoomer( 3, 1, self.d_plot.canvas() )
        self.d_panner = Qwt.QwtPlotPanner( self.d_plot.canvas() )
        self.d_panner.setMouseButton( Qt.MouseButton.MiddleButton )



        self.toolBar = QToolBar( self )
        
        self.btnZoom = QToolButton( self.toolBar )
        self.btnZoom.setText( "Zoom" )
        self.btnZoom.setIcon( QIcon(QPixmap( zoom_xpm ) ))
        self.btnZoom.setCheckable( True )
        self.btnZoom.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnZoom )
        self.btnZoom.toggled.connect(self.enableZoomMode)

        self.btnPrint = QToolButton( self.toolBar )
        self.btnPrint.setText( "Print" )
        self.btnPrint.setIcon( QIcon(QPixmap( print_xpm ) ) )
        self.btnPrint.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnPrint )        
        self.btnPrint.clicked.connect(self.mprint)

        self.btnExport = QToolButton( self.toolBar )
        self.btnExport.setText( "Export" )
        self.btnExport.setIcon( QIcon(QPixmap( print_xpm ) ) )
        self.btnExport.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnExport )        
        self.btnExport.clicked.connect(self.exportDocument)

        self.toolBar.addSeparator()

        self.bottom_bar = QWidget( self )
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setDirection( QHBoxLayout.Direction.LeftToRight )
        bottom_bar_layout.addWidget( QLabel("Time: "))
        bottom_bar_layout.addWidget( QSplitter() )
        self.datapoints_number = QLabel("Number of datapoints: 0")
        bottom_bar_layout.addWidget( self.datapoints_number )
        bottom_bar_layout.addWidget( QSplitter() )
        bottom_bar_layout.addWidget( QLabel("#rutadelarchivo"))
        self.bottom_bar.setLayout(bottom_bar_layout)

        layout.addWidget( self.toolBar )
        layout.addWidget( self.d_plot )
        layout.addWidget( self.bottom_bar )

        self.zooming = False
        self.enableZoomMode( False )
        print(self.datax)
        print(self.datay)



    def actualizarDatos(self):
        self.datax.append(self.datax[-1]+1)
        self.datay.append(np.random.rand(1)[0])
        self.datapoints_number.setText("Number of datapoints: " + str(len(self.datay)))
        self.d_plot.showData(self.datax, self.datay, [3,3,3,3,3],len(self.datay))

    def mprint(self):
        printer = QPrinter()
        docName = "Humm" #self.d_plot.title().text()w
        #if ( not docName.isEmpty() ):
        #docName.replace ( QRegExp ( QString.fromLatin1 ( "\n" ) ), tr ( " -- " ) )
        printer.setDocName ( docName )

        printer.setCreator( "Bode example" )
        

        dialog = QPrintDialog( printer )
        if ( dialog.exec() ):
            renderer = Qwt.QwtPlotRenderer()
            if ( printer.colorMode() == QPrinter.ColorMode.GrayScale ):
                renderer.setDiscardFlag( Qwt.QwtPlotRenderer.DiscardBackground )
                renderer.setDiscardFlag( Qwt.QwtPlotRenderer.DiscardCanvasBackground )
                renderer.setDiscardFlag( Qwt.QwtPlotRenderer.DiscardCanvasFrame )
                renderer.setLayoutFlag( Qwt.QwtPlotRenderer.FrameWithScales )
            renderer.renderTo( self.d_plot, printer )

    def exportDocument(self):
        print("Not implemented")
        #renderer = Qwt.QwtPlotRenderer()
        #renderer.exportTo( self.d_plot, "bode.pdf" )

    def enableZoomMode( self, on ):
        if on:
            self.zooming = True
        if not on and self.zooming:
            self.recargar_grafica()
        self.d_picker.setEnabled(  not on )
        self.d_panner.setEnabled( on )
        self.d_zoomer.setEnabled( on )
        self.d_zoomer.zoom( 0 )

    def recargar_grafica(self):
        # Remove layout and create a new one
        self.d_plot.deleteLater()
        self.toolBar.deleteLater()
        self.bottom_bar.deleteLater()
        self.setLayout(QVBoxLayout(self))      
        self.layout.setSpacing( 0 )
        self.layout.setContentsMargins( 0, 0, 0, 0 )
        
        self.d_plot = Plot( self )
        margin = 5
        self.d_plot.setContentsMargins( margin, margin, margin, 0 )
        
        self.setContextMenuPolicy( Qt.ContextMenuPolicy.NoContextMenu )

        self.d_zoomer = Zoomer( 2,0, self.d_plot.canvas() )
        self.d_zoomer.setRubberBand( Qwt.QwtPicker.RubberBand.RectRubberBand )
        self.d_zoomer.setRubberBandPen( QColor( Qt.GlobalColor.green ) )
        self.d_zoomer.setTrackerMode( Qwt.QwtPicker.DisplayMode.ActiveOnly )
        self.d_zoomer.setTrackerPen( QColor( Qt.GlobalColor.white ) )
        self.d_zoomer.setZoomBase( True )

        self.d_panner = Qwt.QwtPlotPanner( self.d_plot.canvas() )
        self.d_panner.setMouseButton( Qt.MouseButton.MiddleButton )

        self.d_picker = Qwt.QwtPlotPicker( 2,0,
            Qwt.QwtPlotPicker.RubberBand.CrossRubberBand, Qwt.QwtPicker.DisplayMode.AlwaysOn, self.d_plot.canvas() )
        self.d_picker.setStateMachine( Qwt.QwtPickerDragPointMachine() )
        self.d_picker.setRubberBandPen( QColor( Qt.GlobalColor.green ) )
        self.d_picker.setRubberBand( Qwt.QwtPicker.RubberBand.CrossRubberBand )
        self.d_picker.setTrackerPen( QColor( Qt.GlobalColor.white ) )

        self.toolBar = QToolBar( self )
        
        self.paused = False
        self.btnPause = QToolButton( self.toolBar )
        self.btnPause.setText( "Pause" )
        self.btnPause.setIcon( QIcon(QPixmap( pause_xpm ) ))
        self.btnPause.setCheckable( True )
        self.btnPause.setMinimumWidth( 60 )
        self.btnPause.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnPause )
        self.btnPause.toggled.connect(self.pause)

        self.btnZoom = QToolButton( self.toolBar )
        self.btnZoom.setText( "Zoom" )
        self.btnZoom.setIcon( QIcon(QPixmap( zoom_xpm ) ))
        self.btnZoom.setCheckable( True )
        self.btnZoom.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnZoom )
        
        self.btnZoom.toggled.connect(self.enableZoomMode)

        self.btnPrint = QToolButton( self.toolBar )
        self.btnPrint.setText( "Print" )
        self.btnPrint.setIcon( QIcon(QPixmap( print_xpm ) ) )
        self.btnPrint.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnPrint )        
        self.btnPrint.clicked.connect(self.mprint)

        self.btnExport = QToolButton( self.toolBar )
        self.btnExport.setText( "Export" )
        self.btnExport.setIcon( QIcon(QPixmap( print_xpm ) ) )
        self.btnExport.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnExport )        
        self.btnExport.clicked.connect(self.exportDocument)

        self.toolBar.addSeparator()

        self.bottom_bar = QWidget( self )
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setDirection( QHBoxLayout.Direction.LeftToRight )
        bottom_bar_layout.addWidget( QLabel("Time: "))
        bottom_bar_layout.addWidget( QSplitter() )
        self.datapoints_number = QLabel("Number of datapoints: 0")
        bottom_bar_layout.addWidget( self.datapoints_number )
        bottom_bar_layout.addWidget( QSplitter() )
        bottom_bar_layout.addWidget( QLabel("#rutadelarchivo"))
        self.bottom_bar.setLayout(bottom_bar_layout)

        self.layout.addWidget( self.toolBar )
        self.layout.addWidget( self.d_plot )
        self.layout.addWidget( self.bottom_bar )
        self.zooming = False
        self.enableZoomMode( False )
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizarDatos)
        self.timer.start(100)


def main():
    a = QApplication(sys.argv)
    fichero = open("mockData.csv", "r")
    datos = fichero.readlines() # ["x,y", "0,0.2885515512807122", "1,0.45635354359464864", ....]
    fichero.close()
    cabecera = datos.pop(0) # "x,y"
    for i in range(len(datos)):
        datos[i] = datos[i].split(",") # ["0", "0.2885515512807122"]
        datos[i] = [float(datos[i][0]), float(datos[i][1])] # [0, 0.2885515512807122]
    configuracion = None
    m = MainWindow(datos, configuracion)
    m.resize( 540, 400 )
    m.show()

    sys.exit(a.exec())


