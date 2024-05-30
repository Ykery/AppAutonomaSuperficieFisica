from PyQt6.QtWidgets import QComboBox

class QComboBox_modificado(QComboBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(200, 255, 255); color: black;")
        self.insertItems(0, [" -- Select -- "])
        self.setCurrentIndex(0)

