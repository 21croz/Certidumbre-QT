import pandas as pd                                                                         # Paquete de ayuda para cargar y leer archivos .csv.
import numpy as np                                                                          # Paquete de ayuda para operaciones matemáticas.

from PyQt6 import QtWidgets, uic, QtGui                                                     # Paquetes parte de PyQt6 que ayudan a facilitar la ejecución del código
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QGraphicsScene                        # Paquetes parte de PyQt6 > QtWidgets que ayudan a 
from matplotlib.figure import Figure                                                        # 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas            # 
from mpl_toolkits.mplot3d import Axes3D                                                     # 

from view.fp_window import FootprintWindow



class MainWindow(QtWidgets.QMainWindow):
    """
    Clase de la ventana principal.
    """
    def __init__(self):
        """Constructor de la ventana principal."""
        super(MainWindow, self).__init__()

        uic.loadUi(r'ui\main_window.ui', self)      # Cargar elementos graficos de la ventana

        self.create_control_variables()
        self.define_widgets_variables()

        self.define_actions()
        return
    

    def create_control_variables(self):
        """
        Esta funcion crea las variables que se usarán en la ventana principal
        """
        self.combo_values = []
        self.loaded_dataframe = None
        self.list_entries = []
        self.number_of_files = 0
        self.iterations_done = False

        self.x_coord = None
        self.y_coord = None
        self.z_coord = None
        self.metal_value = None
        return


    def define_widgets_variables(self):
        """
        Define las variables de la ventana
        """
        self.meunbar_file_openfile = self.findChild(QtGui.QAction, "menubar_file_openfile")
        self.menubar_file_quit = self.findChild(QtGui.QAction, "menubar_file_quit")
        self.menubar_view_fp = self.findChild(QtGui.QAction, "menubar_view_fp")

        self.entry_price_min = self.findChild(QtWidgets.QLineEdit, "entry_price_min")
        self.entry_price_max = self.findChild(QtWidgets.QLineEdit, "entry_price_max")
        self.entry_price_step = self.findChild(QtWidgets.QLineEdit, "entry_price_step")

        self.entry_mcost_min = self.findChild(QtWidgets.QLineEdit, "entry_mcost_step")
        self.entry_mcost_max = self.findChild(QtWidgets.QLineEdit, "entry_mcost_step")
        self.entry_mcost_step = self.findChild(QtWidgets.QLineEdit, "entry_mcost_step")

        self.entry_pcost_min = self.findChild(QtWidgets.QLineEdit, "entry_pcost_step")
        self.entry_pcost_max = self.findChild(QtWidgets.QLineEdit, "entry_pcost_step")
        self.entry_pcost_step = self.findChild(QtWidgets.QLineEdit, "entry_pcost_step")

        self.entry_recovery_min = self.findChild(QtWidgets.QLineEdit, "entry_recovery_step")
        self.entry_recovery_max = self.findChild(QtWidgets.QLineEdit, "entry_recovery_step")
        self.entry_recovery_step = self.findChild(QtWidgets.QLineEdit, "entry_recovery_step")

        self.entry_discount_min = self.findChild(QtWidgets.QLineEdit, "entry_discount_step")
        self.entry_discount_max = self.findChild(QtWidgets.QLineEdit, "entry_discount_step")
        self.entry_discount_step = self.findChild(QtWidgets.QLineEdit, "entry_discount_step")

        self.entry_scost_min = self.findChild(QtWidgets.QLineEdit, "entry_scost_step")
        self.entry_scost_max = self.findChild(QtWidgets.QLineEdit, "entry_scost_step")
        self.entry_scost_step = self.findChild(QtWidgets.QLineEdit, "entry_scost_step")

        self.button_3d_plot = self.findChild(QtWidgets.QPushButton, "button_3d_plot")
        self.button_fp_plot = self.findChild(QtWidgets.QPushButton, "button_foot_plot")

        self.button_iterate = self.findChild(QtWidgets.QPushButton, "button_iterate")
        return


    def define_actions(self):
        """
        Esta función liga los botones a las funciones correspondientes.
        """
        self.menubar_file_openfile.triggered.connect(self.open_file)
        self.menubar_view_fp.triggered.connect(self.create_footprint_window)
        
        self.button_3d_plot.clicked.connect(self.create_3d_plot)
        self.button_fp_plot.clicked.connect(self.create_fp_plot)

        self.button_iterate.clicked.connect(self.start_iterations)
        return
    

    def open_file(self):
        """
        Funcion ligada a la apertura de archivo en la barra de menú.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo",
            "",
            "Archivos de valores separados por coma (*.csv);;Todos los archivos (*)"
        )

        if file_path:
            try:
                self.loaded_dataframe = pd.read_csv(file_path)
                QMessageBox.information(
                    self,
                    "Archivo cargado",
                    f"El archivo {file_path} se cargó correctamente.\n"
                    f"El archivo contiene {self.loaded_dataframe.shape[0]} filas y {self.loaded_dataframe.shape[1]} columnas.")
            except Exception:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo {file_path}.")
        
        self.modify_combobox()
        return


    def modify_combobox(self):
        """
        Esta función cambia las opciones disponibles en el menú desplegable de los combobox de la parte superior.
        """
        columns = self.loaded_dataframe.columns.tolist()

        self.combo_x_coordinate.clear()
        self.combo_y_coordinate.clear()
        self.combo_z_coordinate.clear()
        self.combo_metal_grade.clear()

        self.combo_x_coordinate.addItems(columns)
        self.combo_y_coordinate.addItems(columns)
        self.combo_z_coordinate.addItems(columns)
        self.combo_metal_grade.addItems(columns)
        return


    def create_footprint_window(self):
        """
        Esta función abre la ventana del footprint para analizar los resultados.
        """
        win = FootprintWindow()
        win.exec()
        return
    

    def delete_plot(self):
        """
        Esta función elimina el gráfico ya existente en el graphicsView de la parte derecha de la interfaz.
        """
        self.graphicsView.setScene(None)
        return
    

    def create_3d_plot(self):
        """
        Esta función crea el gráfico 3D del modelo de bloques seleccionado.
        """
        self.save_combobox()
        self.delete_plot()

        plotted_dataframe = self.loaded_dataframe.copy()
        plotted_dataframe = plotted_dataframe[plotted_dataframe['antes_max'] == 1]
        
        x = plotted_dataframe[self.x_coord]
        y = plotted_dataframe[self.y_coord]
        z = plotted_dataframe[self.z_coord]
        metal = plotted_dataframe[self.metal_value]

        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, projection = '3d')
        
        ax.scatter(x, y, z, c = metal, cmap = 'viridis', marker = 'o', s = 50)
        ax.set_title("Gráfico 3D")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        escena = QGraphicsScene()
        escena.addWidget(canvas)

        self.graphicsView.setScene(escena)
        return


    def create_fp_plot(self):
        """
        Esta función crea el gráfico en 2D del footprint.
        """
        self.save_combobox()
        self.delete_plot()

        plotted_dataframe = self.loaded_dataframe
        plotted_dataframe = plotted_dataframe[plotted_dataframe["antes_max"] == 1]

        x = plotted_dataframe[self.x_coord]
        y = plotted_dataframe[self.y_coord]

        fig = Figure()
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        ax.scatter(x, y, c = 'blue', marker = 'o', s = 50)
        ax.set_title("Gráfico Footprint")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        escena = QGraphicsScene()
        escena.addWidget(canvas)

        self.graphicsView.setScene(escena)
        return
    

    def save_combobox(self):
        """
        Esta función guarda los valores seleccionados en los menúes desplegables.
        """
        self.combo_x_coordinate = self.combo_x_coordinate.currentText()
        self.x_coord = self.combo_x_coordinate

        self.combo_y_coordinate = self.combo_y_coordinate.currentText()
        self.y_coord = self.combo_y_coordinate
        
        self.combo_z_coordinate = self.combo_z_coordinate.currentText()
        self.z_coord = self.combo_z_coordinate
        
        self.combo_metal_grade = self.combo_metal_grade.currentText()
        self.metal_value = self.combo_metal_grade
        return
    

    def start_iterations(self):
        """
        Esta función inicia el proceso de las iteraciones.
        """
        print("Boton iteraciones")
        return