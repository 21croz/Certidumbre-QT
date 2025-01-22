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
        """
        Constructor de la ventana principal.
        """
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

        self.entry_mcost_min = self.findChild(QtWidgets.QLineEdit, "entry_mcost_min")
        self.entry_mcost_max = self.findChild(QtWidgets.QLineEdit, "entry_mcost_max")
        self.entry_mcost_step = self.findChild(QtWidgets.QLineEdit, "entry_mcost_step")

        self.entry_pcost_min = self.findChild(QtWidgets.QLineEdit, "entry_pcost_min")
        self.entry_pcost_max = self.findChild(QtWidgets.QLineEdit, "entry_pcost_max")
        self.entry_pcost_step = self.findChild(QtWidgets.QLineEdit, "entry_pcost_step")

        self.entry_recovery_min = self.findChild(QtWidgets.QLineEdit, "entry_recovery_min")
        self.entry_recovery_max = self.findChild(QtWidgets.QLineEdit, "entry_recovery_max")
        self.entry_recovery_step = self.findChild(QtWidgets.QLineEdit, "entry_recovery_step")

        self.entry_discount_min = self.findChild(QtWidgets.QLineEdit, "entry_discount_min")
        self.entry_discount_max = self.findChild(QtWidgets.QLineEdit, "entry_discount_max")
        self.entry_discount_step = self.findChild(QtWidgets.QLineEdit, "entry_discount_step")

        self.entry_scost_min = self.findChild(QtWidgets.QLineEdit, "entry_scost_min")
        self.entry_scost_max = self.findChild(QtWidgets.QLineEdit, "entry_scost_max")
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
        if self.alert_message_iterations():
            print("Ok")
        else:
            print("Nao Nao")
        
        return
    

    def alert_message_iterations(self):
        """
        Esta función muestra una alerta a la hora de crear las iteraciones, ya que es un proceso que puede
        demorar mucho y generar muchos Gb en archivos.
        """
        file_number, file_size = self.iterations_result_files()
        self.number_of_files = file_number

        string_file_number = f"{file_number:,}".replace(",", ".")

        if file_size < 1024:
            string_files_size = f'{file_size:,.2f}'.replace(',', '.')
            string_files_size += ' Gb'
        else:
            string_files_size = f'{(file_size/1024):,.2f}'.replace(',', '.')
            string_files_size += ' Tb'
        
        iterate_time = self.convert_time(file_number*0.25)

        mensaje = QMessageBox(self)
        mensaje.setWindowTitle("Confirmación")
        mensaje.setText(
            "¿Estás seguro?\n"
            f"Se crearán {string_file_number} archivos.\n"
            f"El peso total será {string_files_size} aproximadamente.\n"
            f"Demorará aproximadamente {iterate_time}")
        mensaje.setIcon(QMessageBox.Icon.Warning)
        mensaje.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        
        respuesta = mensaje.exec()

        return respuesta == QMessageBox.StandardButton.Ok
    

    def iterations_result_files(self):
        """
        Entrega el número de archivos que se crearán al realizar las iteraciones, además de un aproximado
        del peso de la carpeta que los contendrá.
        """
        self.list_entries = []
        self.list_entries_append()
        print(self.list_entries)

        elements_in_range = []

        for elem in self.list_entries:
            elements_in_range.append(self.define_list(elem[0], elem[1], elem[2]))
        
        total_length = len(elements_in_range[0])*len(elements_in_range[1])*len(elements_in_range[2])*len(elements_in_range[3])*len(elements_in_range[4])*len(elements_in_range[5])

        return total_length, ((total_length + 5)*1200/1024)/1024
    

    def define_list(self, min:int|float, max:int|float, step:int|float):
        """
        Funcion que crea una lista desde un valor minimo hasta un valor máximo con un paso definido.
        
        Inputs:
        * min: Valor minimo de la lista.
        * max: Valor maximo de la lista.
        * ste: salto entre cada elemento de la lista.
        
        Outputs:
        * Si los valores de minimo y máximo son iguales, retorna una lista con 1 elemento (el minimo).
        Si el minimo y el máximo son distintos, crea una lista con n elementos, con n igual al espacio
        entre el min y max con un salto igual a step.

        Ejemplo de uso:
        >>> self.define_list(3, 9, 1)
        [3, 4, 5, 6, 7, 8, 9]

        >>> self.define_list(5, 5, 1)
        [5]
        """
        if min == max:
            return [min]
        else:
            return np.arange(min, max + step, step)


    def list_entries_append(self):
        """
        Agrega las entradas a una lista para su posterior uso.
        """
        self.list_entries.append([])
        self.list_entries[0].append(float(self.entry_price_min.text()))
        self.list_entries[0].append(float(self.entry_price_max.text()))
        self.list_entries[0].append(float(self.entry_price_step.text()))

        self.list_entries.append([])
        self.list_entries[1].append(float(self.entry_mcost_min.text()))
        self.list_entries[1].append(float(self.entry_mcost_max.text()))
        self.list_entries[1].append(float(self.entry_mcost_step.text()))

        self.list_entries.append([])
        self.list_entries[2].append(float(self.entry_pcost_min.text()))
        self.list_entries[2].append(float(self.entry_pcost_max.text()))
        self.list_entries[2].append(float(self.entry_pcost_step.text()))

        self.list_entries.append([])
        self.list_entries[3].append(float(self.entry_discount_min.text()))
        self.list_entries[3].append(float(self.entry_discount_max.text()))
        self.list_entries[3].append(float(self.entry_discount_step.text()))

        self.list_entries.append([])
        self.list_entries[4].append(float(self.entry_recovery_min.text()))
        self.list_entries[4].append(float(self.entry_recovery_max.text()))
        self.list_entries[4].append(float(self.entry_recovery_step.text()))

        self.list_entries.append([])
        self.list_entries[5].append(float(self.entry_scost_min.text()))
        self.list_entries[5].append(float(self.entry_scost_max.text()))
        self.list_entries[5].append(float(self.entry_scost_step.text()))
        return
    

    def convert_time(self, time: int):
        """
        Funcion que transforma un tiempo en segundos a dias, horas, minutos, segundos.
        
        Inputs:
            * time: Tiempo en segundos.
        
        Outputs:
            * string_time: String que contiene el tiempo de la siguiente forma: [  ]d [  ]h [  ]m [  ]s
        
        Ejemplo de uso:
            >>> self.convert_time(90061)
            "1d 1h 1m 1s"
        """
        days = time // 86400
        time %= 86400
        hours = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        string_time_days = f'{int(days):,}'.replace(',', '.')
        string_time_hours = f'{int(hours):,}'.replace(',', '.')
        string_time_minutes = f'{int(minutes):,}'.replace(',', '.')
        string_time_seconds = f'{int(time):,}'.replace(',', '.')
        string_time = f'{string_time_days}d {string_time_hours}h {string_time_minutes}m {string_time_seconds}s'
        return string_time


