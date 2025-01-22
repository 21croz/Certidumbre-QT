from PyQt6 import QtWidgets, uic



class FootprintWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi(r"ui\fp_window.ui", self)