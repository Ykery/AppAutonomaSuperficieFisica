#!/usr/bin/python3

import math
import sys
from datetime import datetime, time, timedelta

import numpy as np
# import Qwt
from PyQt6 import Qwt
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QInputDialog, QLabel,
                             QMessageBox, QSizePolicy, QSplitter, QToolBar,
                             QToolButton, QVBoxLayout, QWidget)

from src.modelo.clases import Marcador, ResultadoMoke
from src.modelo.dao import ExperimentoDAO, MarcadorDAO, ResultadoMokeDAO
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
    ". c white",
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
    ". c white",
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
    ". c white",
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
    def __init__(self, id, load_results=False, *args):
        super().__init__(*args)
        self.TIEMPO_ACTUALIZACION_GRAFICA = 100
        self.cargando_resultados = load_results
        self.terminado = False
        self.haciendo_zoom = False
        self.subir = False

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
            self.datos_y = [0]
            self.temporizador = QTimer()
            self.temporizador.timeout.connect(self.actualizar_datos)
            self.temporizador.start(self.TIEMPO_ACTUALIZACION_GRAFICA)

        self.layout.addWidget(self.crear_toolbar())
        self.layout.addWidget(self.crear_cuerpo())
        self.layout.addWidget(self.crear_footer())
        self.enable_zoom_mode(False)
        if self.cargando_resultados:
            self.pausado = True
            self.mostrar_btn_pause()
            self.btn_pausar.setEnabled(False)
            self.btn_marcador.setEnabled(False)
            self.btn_terminar.setEnabled(False)
            self.lb_estado.setText("Visualizyng results")
            self.actualizar_datos()

    def cargar_resultados(self):
        """
        Carga los resultados del experimento actual desde la base de datos.

        Este método obtiene los resultados del experimento actual utilizando el identificador del experimento
        almacenado en la variable `self.experimento.id`. Luego, extrae los datos de campo magnético e intensidad
        de cada resultado y los almacena en las listas `self.datos_x` y `self.datos_y`, respectivamente.

        :return: None
        :rtype: None

        Los resultados se cargan en las siguientes listas:

        - `self.datos_x`: Lista de datos de campo magnético.
        - `self.datos_y`: Lista de datos de intensidad.

        Este método asume que existe una clase `ResultadoMokeDAO` con un método estático `obtener_por_id_experimento`
        que recibe el identificador de un experimento y devuelve una lista de resultados asociados a ese experimento.

        Ejemplo de uso:

        .. code-block:: python

            cargar_resultados()

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
        Crea una barra de herramientas con varios controles para interactuar con el sistema.

        Este método configura una barra de herramientas con botones para pausar, habilitar el modo de zoom,
        añadir marcadores, imprimir, exportar y finalizar el experimento. Además, muestra el estado actual
        del sistema, ya sea "Paused" o "Running".

        :return: La barra de herramientas configurada.
        :rtype: QToolBar

        Configura los siguientes controles:

        - `btn_pausar`: Botón para pausar el sistema.
        - `btn_zoom`: Botón para habilitar el modo de zoom.
        - `btn_marcador`: Botón para añadir marcadores.
        - `btn_imprimir`: Botón para imprimir los resultados.
        - `btn_exportar`: Botón para exportar los resultados.
        - `btn_terminar`: Botón para finalizar el experimento.

        Se conectan varios eventos a sus correspondientes manejadores para realizar acciones específicas
        cuando se interactúa con los controles.

        Ejemplo de uso:

        .. code-block:: python

            toolbar = self.crear_toolbar()
            layout.addWidget(toolbar)

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

        self.btn_zoom.toggled.connect(self.enable_zoom_mode)

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
        self.btn_exportar.clicked.connect(self.export_document)

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
        Crea el cuerpo principal del widget para mostrar el gráfico del experimento MOKE.

        Este método inicializa un objeto de tipo Plot para mostrar el gráfica del experimento MOKE.
        Configura el título del gráfico, las etiquetas de los ejes y el color del gráfico.
        Además, establece márgenes en el gráfico, deshabilita el menú contextual y configura herramientas
        de zoom, desplazamiento y selección.

        :return: El objeto Plot configurado para mostrar el gráfico del experimento MOKE.
        :rtype: Plot

        Ejemplo de uso:

        .. code-block:: python

            cuerpo = self.crear_cuerpo()
            layout.addWidget(cuerpo)

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
        self.lb_tiempo_experimento = QLabel("Time: 0")
        if not self.cargando_resultados:
            self.temporizador.timeout.connect(self.actualizar_tiempo)
        self.footer_datos = QWidget(self)
        layout_footer_datos = QHBoxLayout()
        layout_footer_datos.setDirection(QHBoxLayout.Direction.LeftToRight)
        layout_footer_datos.addWidget(self.lb_tiempo_experimento)
        layout_footer_datos.addWidget(QSplitter())
        self.datapoints_number = QLabel("Number of datapoints: 0")
        layout_footer_datos.addWidget(self.datapoints_number)
        layout_footer_datos.addWidget(QSplitter())
        layout_footer_datos.addWidget(QLabel(self.experimento.rutaCsv))
        self.footer_datos.setLayout(layout_footer_datos)
        return self.footer_datos

    def actualizar_tiempo(self):
        """
        Actualiza el tiempo transcurrido desde el inicio del experimento.

        Este método calcula el tiempo transcurrido desde el inicio del experimento y lo muestra en el pie de página
        del widget. El tiempo se muestra en formato HH:MM:SS.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python 
        actualizar_tiempo()
    
        """ 
        tiempo_experimento = datetime.now() - self.tiempo
        horas = int(tiempo_experimento.total_seconds() // 3600)
        tiempo_experimento = tiempo_experimento - timedelta(hours=horas)
        minutos = int(tiempo_experimento.total_seconds() // 60)
        tiempo_experimento = tiempo_experimento - timedelta(minutes=minutos)
        segundos = int(tiempo_experimento.total_seconds())
        self.lb_tiempo_experimento.setText(
            "Time: "
            + time(
                hour=horas,
                minute=minutos,
                second=segundos,
            ).strftime("%H:%M:%S")
        )

    def finish_experiment(self):
        """
        Finaliza el experimento actual.

        Este método detiene el temporizador utilizado para seguir el tiempo transcurrido del experimento,
        y deshabilita algunos controles como el botón de pausa, el botón para añadir marcadores y el botón
        para finalizar el experimento. Además, cambia el texto del estado a "Finished" y establece la bandera
        `terminado` en True.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            finish_experiment()

        """
        self.temporizador.stop()
        self.btn_pausar.setEnabled(False)
        self.btn_marcador.setEnabled(False)
        self.btn_terminar.setEnabled(False)
        self.lb_estado.setText("Finished")
        self.terminado = True

    def pause(self):
        """
        Pausa o reanuda el experimento actual.

        Este método alterna entre pausar y reanudar el experimento actual cambiando el estado de la variable
        `pausado`. Además, crea un marcador en la base de datos indicando el momento en que se pausa o se reanuda
        el experimento. Actualiza el texto del estado en función del estado de pausa, mostrando "Paused" si el
        experimento está pausado y "Running" si está en curso.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            pause()

        """
        self.pausado = not self.pausado
        marcador = Marcador()
        marcador.eje_x_id = self.datos_x[-1]
        marcador.id_experimento = self.experimento.id
        marcador.descripcion = "Paused" if self.pausado else "Resumed"
        MarcadorDAO.crear(marcador)
        self.lb_estado.setText("Paused" if self.pausado else "Running")

        self.mostrar_btn_pause()

    def mostrar_btn_pause(self):
        """
        Actualiza el texto y el ícono del botón de pausa según el estado del experimento.

        Este método cambia el texto y el ícono del botón de pausa en función del estado del experimento.
        Si el experimento está pausado, el texto del botón se establece como "Resume" y se muestra un ícono
        de reproducción. Si el experimento está en curso, el texto del botón se establece como "Pause" y se
        muestra un ícono de pausa.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            mostrar_btn_pause()

        """
        self.btn_pausar.setText("Resume" if self.pausado else "Pause")
        self.btn_pausar.setIcon(
            QIcon(QPixmap(play_xpm)) if self.pausado else QIcon(QPixmap(pause_xpm))
        )

    def manejar_anadir_marcador(self):
        """
        Maneja la acción de añadir un marcador al experimento.

        Este método obtiene el valor del eje x del último punto de datos del experimento.
        Luego, solicita al usuario que ingrese el texto del marcador mediante un cuadro de diálogo.
        Si el usuario confirma la entrada, crea un nuevo marcador con el valor del eje x, el identificador
        del experimento y el texto ingresado. Si se produce algún error durante la creación del marcador,
        muestra un mensaje de error al usuario.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            manejar_anadir_marcador()

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

    def actualizar_datos(self):
        """
        Actualiza los datos del experimento.
        
        Este método actualiza los datos del experimento MOKE. Si el experimento no está cargando resultados y no ha
        finalizado, genera un nuevo par de valores aleatorios para el campo magnético y la intensidad. Luego, persiste
        los datos en un archivo CSV y en la base de datos. Finalmente, actualiza el número de puntos de datos y muestra
        el gráfico actualizado.
        
        :return: None
        :rtype: None
        
        Ejemplo de uso:
        
        .. code-block:: python
        
            actualizar_datos()
            
        """
        if not self.cargando_resultados and not self.terminado:
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
        Imprime el gráfico actual.

        Este método muestra un cuadro de diálogo de impresión estándar de Qt para permitir al usuario seleccionar
        las opciones de impresión. Luego, utiliza un renderizador de gráficos para renderizar el contenido del gráfico
        actual en la impresora seleccionada.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            mprint()

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

    def export_document(self):
        """
        Exporta el documento asociado al experimento actual.

        Este método inicia el proceso de exportación del documento asociado al experimento actual. Para completar
        la exportación, delega la tarea de solicitar al usuario la ruta de exportación a la función
        `pedir_ruta_exportar_pdf`.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            export_document()

        """
        pedir_ruta_exportar_pdf(self, self.experimento.id)

    def enable_zoom_mode(self, on):
        """
        Habilita o deshabilita el modo de zoom en el gráfico.

        Este método permite habilitar o deshabilitar el modo de zoom en el gráfico. Cuando el parámetro `on`
        es True, se habilita el modo de zoom y se deshabilitan otras funcionalidades como la selección de puntos.
        Si `on` es False y el modo de zoom estaba activado anteriormente, se recarga el gráfico. Además, actualiza
        el estado de los objetos `picker_experimento`, `panner_experimento` y `zoomer_experimento` para reflejar
        el cambio en el modo de zoom.

        :param on: Indica si se debe activar o desactivar el modo de zoom.
        :type on: bool
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            enable_zoom_mode(True)

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
        Recarga el gráfico del experimento.

        Este método borra y recrea el gráfico del experimento, restaurando la configuración inicial. Se utiliza
        cuando se desactiva el modo de zoom para volver al estado original del gráfico. Además, se reinicia el
        temporizador para actualizar los datos del experimento.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            recargar_grafica()

        """
        self.plt_experimento.deleteLater()
        self.haciendo_zoom = False
        self.setLayout(QVBoxLayout(self))
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.toolBar)
        self.layout.addWidget(self.crear_cuerpo())
        self.layout.addWidget(self.footer_datos)
        self.enable_zoom_mode(False)
        self.temporizador = QTimer()
        self.temporizador.timeout.connect(self.actualizar_datos)
        self.temporizador.start(100)

    def closeEvent(self, event):
        """
        Maneja el evento de cierre de la ventana.

        Este método es invocado cuando se intenta cerrar la ventana. Si el proceso de carga de resultados está
        en curso o el experimento ha finalizado, se cierra la ventana sin mostrar ningún mensaje. De lo contrario,
        se muestra un mensaje de advertencia solicitando confirmación antes de cerrar la ventana y detener el experimento.
        Si el usuario confirma la acción, se detiene el temporizador, se borran los elementos gráficos y se cierra la ventana.
        Si el usuario cancela la acción, se ignora el evento de cierre y la ventana permanece abierta.

        :param event: El evento de cierre.
        :type event: QCloseEvent
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            closeEvent(event)

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
