#!/usr/bin/python3

import sys
import math

# import Qwt
from PyQt6 import Qwt
import numpy as np
from src.modelo.dao import ResultadoMokeDAO, ExperimentoDAO, MarcadorDAO
from src.modelo.clases import ResultadoMoke, Marcador
from datetime import datetime, time
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QColor, QPixmap, QIcon, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QToolBar,
    QToolButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QApplication,
    QInputDialog,
    QSplitter,
    QSizePolicy,
)
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from src.utilidades.utilidades import pedir_ruta_exportar_pdf, escribir_csv
from src.vista.componentes.grafica import Plot, Zoomer
from PyQt6.QtWidgets import QMessageBox


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


class MokeGraph(QWidget):
    """
    Representa una gráfica Moke en una interfaz de usuario.

    :param id: Identificador del experimento en la base de datos.
    :type id: int
    :param load_results: Indica si se deben cargar resultados previos, defaults to False.
    :type load_results: bool, optional
    """

    def __init__(self, id, load_results=False, *args):
        """
        Creación de una instancia de MokeGraph.

        Se crea una instancia de la clase MokeGraph con un identificador de experimento y se configura
        para cargar resultados previos desde la base de datos.

        :param id: Identificador del experimento en la base de datos.
        :type id: int
        :param load_results: Indica si se deben cargar resultados previos, por defecto False.
        :type load_results: bool, opcional

        Ejemplo de uso:

        .. code-block:: python

            # Crear una instancia de MokeGraph con un identificador de experimento y cargar resultados previos
            moke_graph = MokeGraph(id=experiment_id, load_results=True)

        """

        super().__init__(*args)
        self.TIEMPO_ACTUALIZACION_GRAFICA = 100
        self.cargando_resultados = load_results
        self.terminado = False
        self.haciendo_zoom = False

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.experimento = ExperimentoDAO.obtener_por_id(id)
        if self.experimento is None:
            raise ValueError("The experiment with id " + str(id) + " does not exist.")
        self.tiempo = datetime.now()
        if self.cargando_resultados:
            self.cargar_resultados()
        else:
            escribir_csv(self.experimento.rutaCsv, "magnetic_field", "intensity")
            self.datos_x = [0]
            self.datos_y = [self.TIEMPO_ACTUALIZACION_GRAFICA / 1000]
            self.temporizador = QTimer()
            self.temporizador.timeout.connect(self.actualizarDatos)
            self.temporizador.start(self.TIEMPO_ACTUALIZACION_GRAFICA)

        self.layout.addWidget(self.crear_toolbar())
        self.layout.addWidget(self.crear_cuerpo())
        self.layout.addWidget(self.crear_footer())
        self.enableZoomMode(False)
        if self.cargando_resultados:
            self.pausado = True
            self.mostrar_btn_pause()
            self.btn_pausar.setEnabled(False)
            self.btn_marcador.setEnabled(False)
            self.btn_terminar.setEnabled(False)
            self.lb_estado.setText("Visualizing results")
            self.actualizarDatos()

    def cargar_resultados(self):
        """
        Carga los resultados del experimento desde la base de datos.
        """
        resultados_cargados = ResultadoMokeDAO.obtener_por_id_experimento(
            self.experimento.id
        )
        self.datos_x = []
        self.datos_y = []
        for resultado in resultados_cargados:
            self.datos_x.append(resultado.magnetic_field)
            self.datos_y.append(resultado.intensity)

    def crear_toolbar(self):
        """
        Crea y configura la barra de herramientas.

        :return: La barra de herramientas configurada.
        :rtype: QToolBar
        """
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
        self.mostrar_btn_pause()

        self.btn_zoom = QToolButton(self.toolBar)
        self.btn_zoom.setText("Zoom")
        self.btn_zoom.setIcon(QIcon(QPixmap(zoom_xpm)))
        self.btn_zoom.setCheckable(True)
        self.btn_zoom.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_zoom)

        self.btn_marcador = QToolButton(self.toolBar)
        self.btn_marcador.setText("Add marker")
        self.btn_marcador.setIcon(QIcon(QPixmap(mark_xpm)))
        self.btn_marcador.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_marcador)
        self.btn_marcador.clicked.connect(self.manejar_anadir_marcador)

        self.btn_zoom.toggled.connect(self.enableZoomMode)

        self.btn_imprimir = QToolButton(self.toolBar)
        self.btn_imprimir.setText("Print")
        self.btn_imprimir.setIcon(QIcon(QPixmap(print_xpm)))
        self.btn_imprimir.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_imprimir)
        self.btn_imprimir.clicked.connect(self.mprint)

        self.btn_exportar = QToolButton(self.toolBar)
        self.btn_exportar.setText("Export")
        self.btn_exportar.setIcon(QIcon(QPixmap(print_xpm)))
        self.btn_exportar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolBar.addWidget(self.btn_exportar)
        self.btn_exportar.clicked.connect(self.exportDocument)

        self.btn_terminar = QToolButton(self.toolBar)
        self.btn_terminar.setText("Finish")
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
        """
        Crea y configura el cuerpo de la gráfica.

        :return: El widget de la gráfica configurado.
        :rtype: Plot
        """
        self.plt_experimento = Plot(
            "Moke Loop Graph",
            "Magnetic field (Oe)",
            "Intensity [arb. un.]",
            self,
            color=QColor(131, 25, 70),
        )

        margin = 5
        self.plt_experimento.setContentsMargins(margin, margin, margin, 0)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.zoomer_experimento = Zoomer(2, 0, self.plt_experimento.canvas())

        self.panner_experimento = Qwt.QwtPlotPanner(self.plt_experimento.canvas())
        self.panner_experimento.setMouseButton(Qt.MouseButton.MiddleButton)

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
        Crea y configura el pie de página de la gráfica.

        :return: El widget del pie de página configurado.
        :rtype: QWidget
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
        self.footer_datos = QWidget(self)
        layout_footer_datos = QHBoxLayout()
        layout_footer_datos.setDirection(QHBoxLayout.Direction.LeftToRight)
        layout_footer_datos.addWidget(lb_tiempo_experimento)
        layout_footer_datos.addWidget(QSplitter())
        self.datapoints_number = QLabel("Number of datapoints: 0")
        layout_footer_datos.addWidget(self.datapoints_number)
        layout_footer_datos.addWidget(QSplitter())
        layout_footer_datos.addWidget(QLabel(self.experimento.rutaCsv))
        self.footer_datos.setLayout(layout_footer_datos)
        return self.footer_datos

    def finish_experiment(self):
        """
        Finaliza el experimento, deteniendo el temporizador y actualizando la interfaz de usuario.
        """
        self.temporizador.stop()
        self.btn_pausar.setEnabled(False)
        self.btn_marcador.setEnabled(False)
        self.btn_terminar.setEnabled(False)
        self.lb_estado.setText("Finished")
        self.terminado = True

    def pause(self):
        """
        Pausa o reanuda la actualización de la gráfica.
        """
        self.pausado = not self.pausado
        marcador = Marcador()
        marcador.eje_x_id = self.datos_x[-1]
        marcador.id_experimento = self.experimento.id
        marcador.descripcion = "Paused" if self.pausado else "Resumed"
        MarcadorDAO.crear(marcador)
        self.lb_estado.setText(marcador.descripcion)

        self.mostrar_btn_pause()

    def mostrar_btn_pause(self):
        """
        Actualiza el texto e ícono del botón de pausa.
        """
        self.btn_pausar.setText("Resume" if self.pausado else "Pause")
        self.btn_pausar.setIcon(
            QIcon(QPixmap(play_xpm)) if self.pausado else QIcon(QPixmap(pause_xpm))
        )

    def manejar_anadir_marcador(self):
        """
        Maneja la adición de un marcador en la gráfica.
        """
        valor_x = self.datos_x[-1]

        texto, ok = QInputDialog.getText(
            self, "Text entry", "Introduce the text of the marker:"
        )
        if ok:
            marcador = Marcador()
            marcador.eje_x_id = valor_x
            marcador.id_experimento = self.experimento.id
            marcador.descripcion = texto
            try:
                MarcadorDAO.crear(marcador)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def actualizarDatos(self):
        """
        Actualiza los datos de la gráfica con nuevos valores.
        """
        if not self.cargando_resultados and not self.terminado:
            self.datos_y.append(np.random.rand(1000)[0])
            self.datos_x.append(
                self.datos_x[-1] + self.TIEMPO_ACTUALIZACION_GRAFICA / 1000
            )
            # Persistir los datos
            resultado = ResultadoMoke()
            resultado.id_experimento = self.experimento.id
            resultado.magnetic_field = self.datos_x[-1]
            resultado.intensity = self.datos_y[-1]
            escribir_csv(
                self.experimento.rutaCsv, resultado.magnetic_field, resultado.intensity
            )
            ResultadoMokeDAO.crear(resultado)
        self.datapoints_number.setText(
            "Number of datapoints: " + str(len(self.datos_y))
        )
        self.plt_experimento.showData(self.datos_x, self.datos_y)

    def mprint(self):
        """
        Imprime la gráfica utilizando un diálogo de impresión.
        """
        printer = QPrinter()
        printer.setCreator("UAM app")

        dialog = QPrintDialog(printer)
        if dialog.exec():
            renderer = Qwt.QwtPlotRenderer()
            if printer.colorMode() == QPrinter.ColorMode.GrayScale:
                renderer.setDiscardFlag(Qwt.QwtPlotRenderer.DiscardBackground)
                renderer.setDiscardFlag(Qwt.QwtPlotRenderer.DiscardCanvasBackground)
                renderer.setDiscardFlag(Qwt.QwtPlotRenderer.DiscardCanvasFrame)
                renderer.setLayoutFlag(Qwt.QwtPlotRenderer.FrameWithScales)
            renderer.renderTo(self.plt_experimento, printer)

    def exportDocument(self):
        """
        Exporta la gráfica como un documento PDF.
        """
        pedir_ruta_exportar_pdf(self, self.experimento.id)

    def enableZoomMode(self, on):
        """
        Habilita o deshabilita el modo zoom en la gráfica.

        :param on: Indica si el modo zoom debe estar habilitado o deshabilitado.
        :type on: bool
        """
        if on:
            self.haciendo_zoom = True
        if not on and self.haciendo_zoom:
            self.recargar_grafica()
        self.picker_experimento.setEnabled(not on)
        self.panner_experimento.setEnabled(on)
        self.zoomer_experimento.setEnabled(on)
        self.zoomer_experimento.zoom(0)

    def recargar_grafica(self):
        """
        Recarga la gráfica, reiniciando sus componentes.
        """
        self.plt_experimento.deleteLater()
        self.haciendo_zoom = False
        self.setLayout(QVBoxLayout(self))
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.crear_cuerpo())
        self.layout.addWidget(self.footer_datos)
        self.enableZoomMode(False)
        self.temporizador = QTimer()
        self.temporizador.timeout.connect(self.actualizarDatos)
        self.temporizador.start(100)

    def closeEvent(self, event):
        """
        Sobreescribe el evento de cierre de la ventana.

        :param event: Evento de cierre de la ventana.
        :type event: QCloseEvent
        """
        if self.cargando_resultados or self.terminado:
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
            self.footer_datos.deleteLater()
            self.deleteLater()
        else:
            event.ignore()


def main():
    a = QApplication(sys.argv)
    m = MokeGraph(1, False)
    m.resize(540, 400)
    m.show()

    sys.exit(a.exec())
