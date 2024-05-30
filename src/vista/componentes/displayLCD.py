from PyQt6.QtWidgets import QLCDNumber

class Display_LCD_modificado(QLCDNumber):
    def __init__(self, initial_value=0, digit_count = None):
        super().__init__()
        self.setStyleSheet("background-color: rgb(200, 255, 255); color: black;")
        if digit_count:
            self.setDigitCount(digit_count)
        self.setSmallDecimalPoint(True)
        self.display(initial_value)
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        # Dar un tamaño
        self.setFixedSize(100, 50)
