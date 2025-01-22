import sys
from PyQt6 import QtWidgets
from view.main_window import MainWindow



app = QtWidgets.QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())