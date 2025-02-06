import pandas as pd                                                                         # Paquete de ayuda para cargar y leer archivos .csv.
import numpy as np                                                                          # Paquete de ayuda para operaciones matemáticas.
import os                                                                                   # Paquete para inspeccionar archivos en distintos directorios.

from PyQt6 import QtWidgets, uic, QtGui                                                     # Paquetes parte de PyQt6 que ayudan a facilitar la ejecución del código.
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QGraphicsScene                        # Paquetes parte de PyQt6 > QtWidgets que facilitan la sintaxis del código.
from PyQt6.QtCore import QCoreApplication                                                   # Permite actualizar la interfaz para hacer que la barra de progreso sea dinámica.
from PyQt6.QtCore import QThread, pyqtSignal                                                # Permite trabajar en la interfaz usando diferentes hilos del procesador.
from matplotlib.figure import Figure                                                        # Permite hacer gráficos.
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas            # Permite poner en la interfaz los gráficos creados.
from itertools import product                                                               # Paquete parte de itertools. Permite hacer combinaciones entre los elementos de una lista.
from time import time                                                                       # Permite calcular el tiempo de ejecución de ciertas líneas de código.

from view.fp_window import FootprintWindow                                                  # Importe de la clase de la ventana ubicada en, View / Footprint Window.



class WorkerThread(QThread):
    """
    Esta clase permite hacer el proceso de las iteraciones en un hilo aparte, de este modo, se
    puede detener el proceso en caso de ser necesario.
    """
    update_progress = pyqtSignal(int)
    iterations_finished = pyqtSignal()

    def __init__(self, parent = None):
        """
        Constructor de la clase del hilo.
        """
        self.main_window = parent
        self.activo = True

        
    def run(self):
        """
        Método para iniciar las iteraciones.
        """
        self.stopped = False
        
        self.main_window.iterations()

        self.finished.emit()
        return
    

    def stop(self):
        """
        Método para detener las iteraciones.
        """
        self.stopped = True
        return