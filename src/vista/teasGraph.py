#!/usr/bin/python3

import sys
import math
#import Qwt
from PyQt6 import Qwt
import numpy as np
from ..modelo.dao import ResultadoTeasDAO, ExperimentoDAO, MarcadorDAO
from ..modelo.clases import ResultadoTeas
from datetime import datetime
from PyQt6.QtCore import Qt,  QSize, QTimer
from PyQt6.QtGui import QColor,  QPixmap, QIcon, QFont
from PyQt6.QtWidgets import QMainWindow,  QWidget,  QToolBar,  QToolButton,  QHBoxLayout, QVBoxLayout,  QLabel,  QApplication, QInputDialog, QSplitter, QSizePolicy
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from ..utilidades.utilidades import pedir_ruta_exportar_pdf, escribir_csv
from .componentes.grafica import Plot, Zoomer
from PyQt6.QtWidgets import QMessageBox
from ..modelo.clases import Marcador
 

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
mark_xpm = ["32 32 2 1",
"  c None",
". c black",
"                                ",
"                                ",
"                                ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"................................",
"................................",
"................................",
"................................",
"................................",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"             ......             ",
"                                ",
"                                ",
"                                ",
"                                "]
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
finish_xpm = ["32 32 2 1",
"  c None",
". c red",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"    ........................    ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                ",
"                                "]
              



class TeasGraph( QWidget ):
    def __init__(self, id, load_results = False, *args):
        super().__init__(self, *args) 
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing( 0 )
        self.layout.setContentsMargins( 0, 0, 0, 0 )
        self.experimento = ExperimentoDAO.obtener_por_id(id)
        self.finished = False
        if self.experimento is None:
            raise ValueError("El experimento con id " + str(id) + " no existe") 
        self.load_results = load_results
        self.tiempo = datetime.now()
        if self.load_results:
            resultados_cargados = ResultadoTeasDAO.obtener_por_id_experimento(self.experimento.id)
            self.datax = []
            self.datay = []
            for resultado in resultados_cargados:
                self.datax.append(resultado.time)
                self.datay.append(resultado.intensity)
        else:
            escribir_csv(self.experimento.rutaCsv, "time", "intensity")
            self.datax = [0]
            self.datay = [0]
            self.timer = QTimer()
            self.timer.timeout.connect(self.actualizarDatos)
            self.timer.start(100)
        
        self.d_plot = Plot("TEAS Timescan", "Time[sec]", "Intensity [arb. un.]", self )
        
        margin = 5;
        self.d_plot.setContentsMargins( margin, margin, margin, 0 )
        self.setContextMenuPolicy( Qt.ContextMenuPolicy.NoContextMenu )

        self.d_zoomer = Zoomer( 2,0, self.d_plot.canvas() )

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
        self.mostrar_btn_pause()

        self.btnZoom = QToolButton( self.toolBar )
        self.btnZoom.setText( "Zoom" )
        self.btnZoom.setIcon( QIcon(QPixmap( zoom_xpm ) ))
        self.btnZoom.setCheckable( True )
        self.btnZoom.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnZoom )
        
        self.btnMark = QToolButton( self.toolBar )
        self.btnMark.setText( "Añadir marcador" )
        self.btnMark.setIcon( QIcon(QPixmap( mark_xpm ) ))
        self.btnMark.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnMark )
        self.btnMark.clicked.connect(self.manejar_anadir_marcador)
        
        
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

        self.btnFinish = QToolButton( self.toolBar )
        self.btnFinish.setText( "FInish" )
        self.btnFinish.setIcon( QIcon(QPixmap( finish_xpm ) ) )
        self.btnFinish.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        self.toolBar.addWidget( self.btnFinish )        
        self.btnFinish.clicked.connect(self.finish_experiment)

        self.toolBar.addSeparator()
        
        self.lb_estado = QLabel("Paused" if self.paused else "Running")
        self.lb_estado.setAlignment( Qt.AlignmentFlag.AlignCenter)
        self.lb_estado.setFont( QFont("Helvetica", 14) )
        self.lb_estado.setMinimumWidth( 100 )
        self.lb_estado.setSizePolicy( QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum )
        self.toolBar.addWidget( self.lb_estado )

        self.bottom_bar = QWidget( self )
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setDirection( QHBoxLayout.Direction.LeftToRight )
        bottom_bar_layout.addWidget( QLabel("Time: "))
        bottom_bar_layout.addWidget( QSplitter() )
        self.datapoints_number = QLabel("Number of datapoints: 0")
        bottom_bar_layout.addWidget( self.datapoints_number )
        bottom_bar_layout.addWidget( QSplitter() )
        bottom_bar_layout.addWidget( QLabel(self.experimento.rutaCsv))
        self.bottom_bar.setLayout(bottom_bar_layout)

        self.layout.addWidget( self.toolBar )
        self.layout.addWidget( self.d_plot )
        self.layout.addWidget( self.bottom_bar )
        self.zooming = False
        self.enableZoomMode( False )
        if self.load_results:
            self.paused = True
            self.mostrar_btn_pause()
            self.btnPause.setEnabled(False)
            self.btnFinish.setEnabled(False)
            self.btnMark.setEnabled(False)
            self.actualizarDatos()

    def finish_experiment(self):
        self.timer.stop()
        self.btnPause.setEnabled(False)
        self.btnMark.setEnabled(False)
        self.btnFinish.setEnabled(False)
        self.lb_estado.setText("Finished")
        self.finished = True


    def pause(self):
        self.paused = not self.paused
        marcador = Marcador()
        marcador.eje_x_id = self.datax[-1]
        marcador.id_experimento = self.experimento.id
        marcador.descripcion = "Paused" if self.paused else "Resumed"
        MarcadorDAO.crear(marcador)
        self.lb_estado.setText("Paused" if self.paused else "Running")
        
        self.mostrar_btn_pause()
        
    def mostrar_btn_pause(self):
        self.btnPause.setText("Resume" if self.paused else "Pause")
        self.btnPause.setIcon( QIcon(QPixmap( play_xpm ) ) if self.paused else QIcon(QPixmap( pause_xpm )))
        

    def manejar_anadir_marcador(self):
        valor_x = self.datax[-1]
        
        text, ok = QInputDialog.getText(self, 'Entrada de texto', 'Ingrese su texto:')
        if ok:
            marcador = Marcador()
            marcador.eje_x_id = valor_x
            marcador.id_experimento = self.experimento.id
            marcador.descripcion = text
            try:
                MarcadorDAO.crear(marcador)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


    def actualizarDatos(self):
        if not self.load_results and not self.finished:
            self.datay.append(np.random.rand(1000)[0])
            self.datax.append(self.datax[-1]+1)
            # Persistir los datos
            resultado = ResultadoTeas()
            resultado.id_experimento = self.experimento.id
            resultado.time = self.datax[-1]
            resultado.intensity = self.datay[-1]
            escribir_csv(self.experimento.rutaCsv, resultado.time, resultado.intensity)
            ResultadoTeasDAO.crear(resultado)
        self.datapoints_number.setText("Number of datapoints: " + str(len(self.datay)))
        self.d_plot.showData(self.datax, self.datay)

    def mprint(self):
        printer = QPrinter()
        printer.setCreator( "UAM app" )
        

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
        pedir_ruta_exportar_pdf(self, self.experimento.id)

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
        self.d_plot.deleteLater()
        self.setLayout(QVBoxLayout(self))      
        self.layout.setSpacing( 0 )
        self.layout.setContentsMargins( 0, 0, 0, 0 )
        
        self.d_plot = Plot("TEAS Timescan", "Time[sec]", "Intensity [arb. un.]", self )
        margin = 5
        self.d_plot.setContentsMargins( margin, margin, margin, 0 )
        
        self.setContextMenuPolicy( Qt.ContextMenuPolicy.NoContextMenu )

        self.d_zoomer = Zoomer( 2,0, self.d_plot.canvas() )

        self.d_panner = Qwt.QwtPlotPanner( self.d_plot.canvas() )
        self.d_panner.setMouseButton( Qt.MouseButton.MiddleButton )

        self.d_picker = Qwt.QwtPlotPicker( 2,0,
            Qwt.QwtPlotPicker.RubberBand.CrossRubberBand, Qwt.QwtPicker.DisplayMode.AlwaysOn, self.d_plot.canvas() )
        self.d_picker.setStateMachine( Qwt.QwtPickerDragPointMachine() )
        self.d_picker.setRubberBandPen( QColor( Qt.GlobalColor.green ) )
        self.d_picker.setRubberBand( Qwt.QwtPicker.RubberBand.CrossRubberBand )
        self.d_picker.setTrackerPen( QColor( Qt.GlobalColor.white ) )

        self.layout.addWidget( self.toolBar )
        self.layout.addWidget( self.d_plot )
        self.layout.addWidget( self.bottom_bar )
        self.zooming = False
        self.enableZoomMode( False )
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizarDatos)
        self.timer.start(100)
        
        if self.load_results:
            self.paused = True
            self.mostrar_btn_pause()
            self.btnPause.setEnabled(False)
            self.btnFinish.setEnabled(False)
            self.btnMark.setEnabled(False)


    def closeEvent(self, event):
        if self.load_results or self.finished:
            event.accept()
            return
        reply = QMessageBox.warning(self, 'Warning', "¿Estás seguro que deseas salir y terminar el experimento?", 
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            self.timer.stop()
            self.d_plot.deleteLater()
            self.toolBar.deleteLater()
            self.bottom_bar.deleteLater()
            self.deleteLater()
        else:
            event.ignore()

def main():
    a = QApplication(sys.argv)
    m = TeasGraph(1, True)
    m.resize( 540, 400 )
    m.show()

    sys.exit(a.exec())


