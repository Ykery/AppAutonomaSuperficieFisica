import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
import numpy as np


from src.vista import moke_config, teasMain, vistaExperimentos

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import Qwt
from PyQt6.Qwt import *
import time
from datetime import date
from .componentes.boton import BotonModificado, BotonModificadoExit

class MenuInicio(QWidget):
    def __init__(self, ):
        """
        Inicializa la ventana principal del menú de inicio.

        Esta clase crea una ventana principal para el menú de inicio de la aplicación. La ventana muestra la fecha y 
        hora actual, junto con opciones para realizar diferentes experimentos y ver experimentos realizados previamente.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            menu_inicio = MenuInicio()
            menu_inicio.show()

        """
        super().__init__()
        self.setWindowTitle("Menu Inicio")
        self.fuenteHelvetica = QFont("Helvetica", 11)
        self.setStyleSheet("background-color: rgb(176, 213, 212);" "color: black;") # Estilo de la ventana
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.setLayout(layout)

        self.child_window = None
        self.lb_hora= QLCDNumber()
        self.lb_hora.setFixedSize(100, 50)
        self.lb_hora.setDigitCount(8)
        self.lb_hora.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lb_hora.setStyleSheet(" color: black")
        self.lb_fecha = QLabel("")
        self.lb_fecha.setFont(self.fuenteHelvetica)
        self.lb_fecha.setStyleSheet(" color: black")
        lb_label = QLabel("Elija una opción:")
        btn_teas = BotonModificado("Realizar Experimento TEAS TimeScan")
        elemento_fecha_hora = QWidget()
        elemento_fecha_hora.setLayout( QHBoxLayout() )
        elemento_fecha_hora.layout().addWidget(self.lb_fecha)
        elemento_fecha_hora.layout().addWidget(self.lb_hora)
        self.lb_fecha.setFont(QFont("Helvetica", 18))
        

        btn_moke = BotonModificado("Realizar Experimento MOKE Loop")
        btn_experimentos = BotonModificado("Ver Experimentos Realizados")
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
               
        btn_quit = BotonModificadoExit("QUIT")

        lb_label.setFont(self.fuenteHelvetica)
        btn_teas.setFont(self.fuenteHelvetica)
        btn_moke.setFont(self.fuenteHelvetica)
        btn_experimentos.setFont(self.fuenteHelvetica)
        btn_quit.setFont(self.fuenteHelvetica)
        layout.addWidget(elemento_fecha_hora)
        layout.addWidget(lb_label)
        layout.addWidget(btn_teas)
        layout.addWidget(btn_moke)
        layout.addWidget(btn_experimentos)
        layout.addWidget(linea) 
        layout.addWidget(btn_quit)

        self.actualizar_fecha_hora()
        # Si se borra la ventana principal, se cierra la aplicación
        btn_quit.clicked.connect(QApplication.instance().quit)

        btn_teas.clicked.connect(lambda: self.open_child_window(teasMain.TeasWindow))
        btn_moke.clicked.connect(lambda: self.open_child_window(moke_config.VistaPrincipal))
        btn_experimentos.clicked.connect(lambda: self.open_child_window(vistaExperimentos.ExperimentosWindow))


    def open_child_window(self, window_class):
        """
        Abre una ventana secundaria basada en la clase de la ventana proporcionada.

        Este método cierra todas las ventanas secundarias abiertas y luego abre una nueva ventana secundaria 
        basada en la clase de ventana proporcionada como argumento.

        :param window_class: La clase de la ventana secundaria que se abrirá.
        :type window_class: class
        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            menu_inicio.open_child_window(teasMain.TeasWindow)

        """
        # Cerrar todas las ventanas hijas abiertas
        if self.child_window:
            self.child_window.close()

        # Abrir una nueva ventana hija
        new_window = window_class()
        self.child_window = new_window
        new_window.show()
        print(self.child_window)

    def actualizar_fecha_hora(self):
        """
        Actualiza continuamente la hora mostrada en la ventana y la fecha actual.

        Este método actualiza continuamente la hora mostrada en la ventana utilizando un temporizador, 
        así como la fecha actual.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            menu_inicio.actualizar_fecha_hora()

        """
        hora = time.strftime("%H:%M:%S")
        self.lb_hora.display(hora)
        self.get_dia()
        QTimer.singleShot(200, self.actualizar_fecha_hora)

    def get_dia(self):
        """
        Obtiene y muestra la fecha actual en la ventana.

        Este método obtiene la fecha actual y la muestra en la ventana.

        :return: None
        :rtype: None

        Ejemplo de uso:

        .. code-block:: python

            menu_inicio.get_dia()

        """
        hoy = date.today()
        d1 = hoy.strftime("%d/%m/%Y")
        self.lb_fecha.setText(d1)
    

def main():
    """
    Función principal para ejecutar la aplicación.

    Esta función inicia la base de datos, crea la aplicación y la ventana principal del menú de inicio, y luego 
    ejecuta la aplicación.

    :return: None
    :rtype: None

    Ejemplo de uso:

    .. code-block:: python

        main()

    """
    app = QApplication(sys.argv)
    window = MenuInicio()
    window.show()
    sys.exit(app.exec())