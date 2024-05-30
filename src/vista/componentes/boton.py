from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QFont


class boton_modificado(QPushButton):
    def __init__(self,texto):
        super(boton_modificado, self).__init__(texto)
        self.setFont(QFont("Helvetica", 11))
        self.setStyleSheet("""
            QPushButton {
                background-color: rgb(135, 206, 235);
                padding: 10px;
            }
            QPushButton:hover {
            background-color: lightblue;
            }
             QPushButton:pressed {
            background-color: rgb(100, 121, 120);
            }                  
        """)
class boton_modificado_exit(boton_modificado):
    def __init__(self, texto):
        super().__init__(texto)
        self.setFont(QFont("Helvetica", 11))
        self.setStyleSheet("""
            QPushButton {
                background-color: rgb(201,112,098);
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(240, 140, 126);
            }
             QPushButton:pressed {
                background-color: rgb(167, 98, 88);
            }                  
        """)

class boton_modificado_run(boton_modificado):
    def __init__(self, texto):
        super().__init__(texto)
        self.setFont(QFont("Helvetica", 11))
        self.setStyleSheet("""
            QPushButton {
                background-color: rgb(59, 235, 156);
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(79, 255, 176);
            }
             QPushButton:pressed {
                background-color: rgb(100, 121, 120);
            }                  
        """)
