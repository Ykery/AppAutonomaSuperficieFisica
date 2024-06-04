#!/usr/bin/python3

import math
import sys
from datetime import datetime, time

import numpy as np
# import Qwt
from PyQt6 import Qwt
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QInputDialog, QLabel,
                             QMessageBox, QSizePolicy, QSplitter, QToolBar,
                             QToolButton, QVBoxLayout, QWidget)

from src.modelo.clases import Marcador, ResultadoTeas
from src.modelo.dao import ExperimentoDAO, MarcadorDAO, ResultadoTeasDAO
from src.utilidades.utilidades import escribir_csv, pedir_ruta_exportar_pdf
from src.vista.componentes.grafica import Plot, Zoomer


def logSpace(size, xmin, xmax):
    if (xmin <= 0.0) or (xmax <= 0.0) or (size <= 0):
        array = np.zeros(0, float)
        return array
    array = np.zeros(size, float)
    imax = size - 1
    array[0] = xmin
    array[imax] = xmax
    lxmin = math.log(xmin)
    lxmax = math.log(xmax)
    lstep = (lxmax - lxmin) / imax
    for i in range(imax):
        array[i] = math.exp(lxmin + i * lstep)
    return array


play_xpm = [
    "32 32 2 1 ",
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
    "  .                             ",
]
pause_xpm = [
    "32 32 2 1",
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
    "    .......          .......    ",
]
mark_xpm = [
    "32 32 2 1",
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
    "                                ",
]
print_xpm = [
    "32 32 12 1",
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
    "..................###...........",
]
zoom_xpm = [
    "32 32 8 1",
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
    "...########################..##.",
]
finish_xpm = [
    "32 32 2 1",
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
    "                                ",
]


class TeasGraph(QWidget):
    def __init__(self, id, load_results=False, *args):
        super().__init__(*args)
        self.TIEMPO_ACTUALIZACION_GRAFICA = 100
        self.subir = False

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.experimento = ExperimentoDAO.obtener_por_id(id)
        self.finished = False
        if self.experimento is None:
            raise ValueError("El experimento con id " + str(id) + " no existe")
        self.cargando_resultados = load_results
        self.tiempo = datetime.now()
        if self.cargando_resultados:
            resultados_cargados = ResultadoTeasDAO.obtener_por_id_experimento(
                self.experimento.id
            )
            self.datos_x = []
            self.datos_y = []
            for resultado in resultados_cargados:
                self.datos_x.append(resultado.time)
                self.datos_y.append(resultado.intensity)
        else:
            escribir_csv(self.experimento.rutaCsv, "time", "intensity")
            self.datos_x = [0]
            self.datos_y = [0]
            self.temporizador = QTimer()
            self.temporizador.timeout.connect(self.actualizar_datos)

            self.temporizador.start(self.TIEMPO_ACTUALIZACION_GRAFICA)

        self.zooming = False
        self.layout.addWidget(self.crear_toolbar())
        self.layout.addWidget(self.crear_cuerpo())
        self.layout.addWidget(self.crear_footer())
        self.enableZoomMode(False)
        if self.cargando_resultados:
            self.pausado = True
            self.actualizar_btn_pause()
            self.btn_pausar.setEnabled(False)
            self.btn_terminar.setEnabled(False)
            self.btn_marcador.setEnabled(False)
            self.lb_estado.setText("Visualizyng results")
            self.actualizar_datos()

    def crear_toolbar(self):
        self.toolBar = QToolBar(self)

        self.pausado = False
        self.btn_pausar = QToolButton(self.toolBar)
        self.btn_pausar.setText("Pause")
        self.btn_pausar.setIcon(QIcon(QPixmap(pause_xpm)))
        self.btn_pausar.setCheckable(True)
        self.btn_pausar.setMinimumWidth(60)
        self.btn_pausar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_pausar)
        self.btn_pausar.toggled.connect(self.pause)
        self.actualizar_btn_pause()

        self.btnZoom = QToolButton(self.toolBar)
        self.btnZoom.setText("Zoom")
        self.btnZoom.setIcon(QIcon(QPixmap(zoom_xpm)))
        self.btnZoom.setCheckable(True)
        self.btnZoom.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btnZoom)

        self.btn_marcador = QToolButton(self.toolBar)
        self.btn_marcador.setText("Añadir marcador")
        self.btn_marcador.setIcon(QIcon(QPixmap(mark_xpm)))
        self.btn_marcador.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_marcador)
        self.btn_marcador.clicked.connect(self.manejar_anadir_marcador)

        self.btnZoom.toggled.connect(self.enableZoomMode)

        self.btnPrint = QToolButton(self.toolBar)
        self.btnPrint.setText("Print")
        self.btnPrint.setIcon(QIcon(QPixmap(print_xpm)))
        self.btnPrint.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btnPrint)
        self.btnPrint.clicked.connect(self.mprint)

        self.btn_exportar = QToolButton(self.toolBar)
        self.btn_exportar.setText("Export")
        self.btn_exportar.setIcon(QIcon(QPixmap(print_xpm)))
        self.btn_exportar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_exportar)
        self.btn_exportar.clicked.connect(self.exportDocument)

        self.btn_terminar = QToolButton(self.toolBar)
        self.btn_terminar.setText("FInish")
        self.btn_terminar.setIcon(QIcon(QPixmap(finish_xpm)))
        self.btn_terminar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_terminar)
        self.btn_terminar.clicked.connect(self.finish_experiment)

        self.toolBar.addSeparator()

        self.lb_estado = QLabel("Paused" if self.pausado else "Running")
        self.lb_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_estado.setFont(QFont("Helvetica", 14))
        self.lb_estado.setMinimumWidth(100)
        self.lb_estado.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum
        )
        self.toolBar.addWidget(self.lb_estado)
        return self.toolBar

    def crear_cuerpo(self):
        self.plt_experimento = Plot(
            "TEAS Timescan", "Time[sec]", "Intensity [arb. un.]", self
        )

        margin = 5
        self.plt_experimento.setContentsMargins(margin, margin, margin, 0)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.zoomer_experimento = Zoomer(2, 0, self.plt_experimento.canvas())

        self.picker_experimento = Qwt.QwtPlotPicker(
            2,
            0,
            Qwt.QwtPlotPicker.RubberBand.CrossRubberBand,
            Qwt.QwtPicker.DisplayMode.AlwaysOn,
            self.plt_experimento.canvas(),
        )
        self.picker_experimento.setStateMachine(Qwt.QwtPickerDragPointMachine())
        self.picker_experimento.setRubberBandPen(QColor(Qt.GlobalColor.green))
        self.picker_experimento.setRubberBand(Qwt.QwtPicker.RubberBand.CrossRubberBand)
        self.picker_experimento.setTrackerPen(QColor(Qt.GlobalColor.white))
        return self.plt_experimento

    def crear_footer(self):
        """
        Crea el pie de página del widget que muestra información adicional sobre el experimento.

        Este método configura un QLabel para mostrar el tiempo transcurrido desde el inicio del experimento,
        otro QLabel para mostrar el número de puntos de datos del experimento y un QLabel adicional para mostrar
        la ruta del archivo CSV asociado al experimento.

        :return: El widget configurado para mostrar el pie de página.
        :rtype: QWidget

        Ejemplo de uso:

        .. code-block:: python

            footer = self.crear_footer()
            layout.addWidget(footer)

        """
        lb_tiempo_experimento = QLabel("Time: 0")
        if not self.cargando_resultados:
            self.temporizador.timeout.connect(
                lambda: lb_tiempo_experimento.setText(
                    "Time: "
                    + time(
                        second=int((datetime.now() - self.tiempo).total_seconds())
                    ).strftime("%M:%S")
                )
            )
        self.bottom_bar = QWidget(self)
        layout_footer_datos = QHBoxLayout()
        layout_footer_datos.setDirection(QHBoxLayout.Direction.LeftToRight)
        layout_footer_datos.addWidget(lb_tiempo_experimento)
        layout_footer_datos.addWidget(QSplitter())
        self.numero_puntos = QLabel("Number of datapoints: 0")
        layout_footer_datos.addWidget(self.numero_puntos)
        layout_footer_datos.addWidget(QSplitter())
        layout_footer_datos.addWidget(QLabel(self.experimento.rutaCsv))
        self.bottom_bar.setLayout(layout_footer_datos)
        return self.bottom_bar

    def finish_experiment(self):
        self.temporizador.stop()
        self.btn_pausar.setEnabled(False)
        self.btn_marcador.setEnabled(False)
        self.btn_terminar.setEnabled(False)
        self.lb_estado.setText("Finished")
        self.finished = True

    def pause(self):
        self.pausado = not self.pausado
        marcador = Marcador()
        marcador.eje_x_id = self.datos_x[-1]
        marcador.id_experimento = self.experimento.id
        marcador.descripcion = "Paused" if self.pausado else "Resumed"
        MarcadorDAO.crear(marcador)
        self.lb_estado.setText("Paused" if self.pausado else "Running")

        self.actualizar_btn_pause()

    def actualizar_btn_pause(self):
        self.btn_pausar.setText("Resume" if self.pausado else "Pause")
        self.btn_pausar.setIcon(
            QIcon(QPixmap(play_xpm)) if self.pausado else QIcon(QPixmap(pause_xpm))
        )

    def manejar_anadir_marcador(self):
        valor_x = self.datos_x[-1]

        text, ok = QInputDialog.getText(self, "Entrada de texto", "Ingrese su texto:")
        if ok:
            marcador = Marcador()
            marcador.eje_x_id = valor_x
            marcador.id_experimento = self.experimento.id
            marcador.descripcion = text
            try:
                MarcadorDAO.crear(marcador)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def actualizar_datos(self):
        if not self.cargando_resultados and not self.finished:
            self.datos_x.append(
                self.datos_x[-1] + self.TIEMPO_ACTUALIZACION_GRAFICA / 1000
            )
            if self.datos_y[-1] >= np.random.uniform(10, 15):
                self.subir = False
            elif self.datos_y[-1] <= np.random.uniform(-7, 0):
                self.subir = True
            if self.subir:
                self.datos_y.append(self.datos_y[-1] + np.random.uniform(0, 2))
            else:
                self.datos_y.append(self.datos_y[-1] - np.random.uniform(0, 2))
            # Persistir los datos
            resultado = ResultadoTeas()
            resultado.id_experimento = self.experimento.id
            resultado.time = self.datos_x[-1]
            resultado.intensity = self.datos_y[-1]
            escribir_csv(self.experimento.rutaCsv, resultado.time, resultado.intensity)
            ResultadoTeasDAO.crear(resultado)
        self.numero_puntos.setText("Number of datapoints: " + str(len(self.datos_y)))
        self.plt_experimento.showData(self.datos_x, self.datos_y)

    def mprint(self):
        printer = QPrinter()
        printer.setCreator("UAM app")

        ventana_dialog = QPrintDialog(printer)
        if ventana_dialog.exec():
            renderer = Qwt.QwtPlotRenderer()
            if printer.colorMode() == QPrinter.ColorMode.GrayScale:
                renderer.setDiscardFlag(Qwt.QwtPlotRenderer.DiscardBackground)
                renderer.setDiscardFlag(Qwt.QwtPlotRenderer.DiscardCanvasBackground)
                renderer.setDiscardFlag(Qwt.QwtPlotRenderer.DiscardCanvasFrame)
                renderer.setLayoutFlag(Qwt.QwtPlotRenderer.FrameWithScales)
            renderer.renderTo(self.plt_experimento, printer)

    def exportDocument(self):
        pedir_ruta_exportar_pdf(self, self.experimento.id)

    def enableZoomMode(self, on):
        if on:
            self.zooming = True
        if not on and self.zooming:
            self.recargar_grafica()
        self.picker_experimento.setEnabled(not on)
        self.zoomer_experimento.setEnabled(on)
        self.zoomer_experimento.zoom(0)

    def recargar_grafica(self):
        self.plt_experimento.deleteLater()
        self.setLayout(QVBoxLayout(self))
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.plt_experimento = Plot(
            "TEAS Timescan", "Time[sec]", "Intensity [arb. un.]", self
        )
        margin = 5
        self.plt_experimento.setContentsMargins(margin, margin, margin, 0)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.zoomer_experimento = Zoomer(2, 0, self.plt_experimento.canvas())

        self.picker_experimento = Qwt.QwtPlotPicker(
            2,
            0,
            Qwt.QwtPlotPicker.RubberBand.CrossRubberBand,
            Qwt.QwtPicker.DisplayMode.AlwaysOn,
            self.plt_experimento.canvas(),
        )
        self.picker_experimento.setStateMachine(Qwt.QwtPickerDragPointMachine())
        self.picker_experimento.setRubberBandPen(QColor(Qt.GlobalColor.green))
        self.picker_experimento.setRubberBand(Qwt.QwtPicker.RubberBand.CrossRubberBand)
        self.picker_experimento.setTrackerPen(QColor(Qt.GlobalColor.white))

        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.plt_experimento)
        self.layout.addWidget(self.bottom_bar)
        self.zooming = False
        self.enableZoomMode(False)
        self.temporizador = QTimer()
        self.temporizador.timeout.connect(self.actualizar_datos)
        self.temporizador.start(100)

    def closeEvent(self, event):
        if self.cargando_resultados or self.finished:
            event.accept()
            return
        reply = QMessageBox.warning(
            self,
            "Warning",
            "Are you sure you want to close the window and stop the experiment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            self.temporizador.stop()
            self.plt_experimento.deleteLater()
            self.toolBar.deleteLater()
            self.bottom_bar.deleteLater()
            self.deleteLater()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    teas_graph = TeasGraph(1, True)
    teas_graph.resize(540, 400)
    teas_graph.show()

    sys.exit(app.exec())
