import pandas as pd                                                                         # Paquete de ayuda para cargar y leer archivos .csv.
import numpy as np                                                                          # Paquete de ayuda para operaciones matemáticas.
import os                                                                                   # Paquete para inspeccionar archivos en distintos directorios.
import threading
import time

from PyQt6 import QtWidgets, uic, QtGui                                                     # Paquetes parte de PyQt6 que ayudan a facilitar la ejecución del código.
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QGraphicsScene                        # Paquetes parte de PyQt6 > QtWidgets que facilitan la sintaxis del código.
from PyQt6.QtCore import QCoreApplication                                                   # Permite actualizar la interfaz para hacer que la barra de progreso sea dinámica.
from PyQt6.QtCore import QThread, pyqtSignal                                                # Permite trabajar en la interfaz usando diferentes hilos del procesador.
from matplotlib.figure import Figure                                                        # Permite hacer gráficos.
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas            # Permite poner en la interfaz los gráficos creados.
from itertools import product                                                               # Paquete parte de itertools. Permite hacer combinaciones entre los elementos de una lista.

from view.fp_window import FootprintWindow                                                  # Importe de la clase de la ventana ubicada en, View / Footprint Window.
from view.iteration_thread import WorkerThread


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

        self.load_entries()
        return


    def closeEvent(self, event):
        """
        Esta función define el comportamiento del botón de cerrar la ventana.
        """
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Salir")
        message_box.setText("¿Deseas guardar los cambios antes de salir?")
        message_box.setIcon(QMessageBox.Icon.Question)

        save_button = message_box.addButton("Guardar", QMessageBox.ButtonRole.AcceptRole)
        cancel_button = message_box.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        dont_save_button = message_box.addButton("No Guardar", QMessageBox.ButtonRole.DestructiveRole)

        message_box.exec()

        if message_box.clickedButton() == save_button:
            self.button_save()
            event.accept()

        elif message_box.clickedButton() == cancel_button:
            event.ignore()

        elif message_box.clickedButton() == dont_save_button:
            event.accept()


    def button_save(self):
        """
        Esta función define el comportamiento del botón 'guardar' al cerrar la ventana.
        """
        path = "reports"
        file_name = "saved_data.txt"

        entries = [
            self.entry_price_min.text(),
            self.entry_price_max.text(),
            self.entry_price_step.text(),
        
            self.entry_mcost_min.text(),
            self.entry_mcost_max.text(),
            self.entry_mcost_step.text(),
        
            self.entry_pcost_min.text(),
            self.entry_pcost_max.text(),
            self.entry_pcost_step.text(),
        
            self.entry_recovery_min.text(),
            self.entry_recovery_max.text(),
            self.entry_recovery_step.text(),
        
            self.entry_discount_min.text(),
            self.entry_discount_max.text(),
            self.entry_discount_step.text(),
        
            self.entry_scost_min.text(),
            self.entry_scost_max.text(),
            self.entry_scost_step.text(),
            
            True if self.check_diluc.isChecked() else False,
            self.entry_diluc_min.text(),
            self.entry_diluc_max.text(),
            self.entry_diluc_step.text()]

        with open(os.path.join(path, file_name), "w", encoding = "utf-8") as archivo:
            for i, item in enumerate(entries):
                archivo.write(f"{i}, {str(item)}\n")

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

        self.check_diluc = self.findChild(QtWidgets.QCheckBox, "check_diluc")

        self.entry_diluc_min = self.findChild(QtWidgets.QLineEdit, "entry_diluc_min")
        self.entry_diluc_max = self.findChild(QtWidgets.QLineEdit, "entry_diluc_max")
        self.entry_diluc_step = self.findChild(QtWidgets.QLineEdit, "entry_diluc_step")

        self.button_3d_plot = self.findChild(QtWidgets.QPushButton, "button_3d_plot")
        self.button_fp_plot = self.findChild(QtWidgets.QPushButton, "button_foot_plot")

        self.button_iterate = self.findChild(QtWidgets.QPushButton, "button_iterate")
        self.button_stop = self.findChild(QtWidgets.QPushButton, "button_stop")
        self.button_stop.setEnabled(False)

        self.progress_bar = self.findChild(QtWidgets.QProgressBar, "progressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        return


    def define_actions(self):
        """
        Esta función liga los botones a las funciones correspondientes.
        """
        self.menubar_file_openfile.triggered.connect(self.open_file)
        self.menubar_file_quit.triggered.connect(self.quit_app)
        self.menubar_view_fp.triggered.connect(self.create_footprint_window)
        
        self.button_3d_plot.clicked.connect(self.create_3d_plot)
        self.button_fp_plot.clicked.connect(self.create_fp_plot)

        self.button_iterate.clicked.connect(self.start_iterations)
        # self.button_stop.clicked.connect()

        self.check_diluc.stateChanged.connect(self.check_dilucion)
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
                self.modify_combobox()
            except Exception:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo {file_path}.")
        
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
    

    def load_entries(self):
        """
        Esta función carga los datos de los entries guardados en el archivo 'saved_data.txt'.
        """
        if not os.path.exists(os.path.join("reports", "saved_data.txt")):
            return
        
        list_line_edits = [
            self.entry_price_min,
            self.entry_price_max,
            self.entry_price_step,
            self.entry_mcost_min,
            self.entry_mcost_max,
            self.entry_mcost_step,
            self.entry_pcost_min,
            self.entry_pcost_max,
            self.entry_pcost_step,
            self.entry_recovery_min,
            self.entry_recovery_max,
            self.entry_recovery_step,
            self.entry_discount_min,
            self.entry_discount_max,
            self.entry_discount_step,
            self.entry_scost_min,
            self.entry_scost_max,
            self.entry_scost_step,
            self.check_diluc,
            self.entry_diluc_min,
            self.entry_diluc_max,
            self.entry_diluc_step
        ]
        empty = ["", "\n"]
        widget_id = []
        widget_text = []

        with open(os.path.join("reports", "saved_data.txt"), "r") as archivo:
            for line in archivo:
                splited_line = line.split(", ")

                if line in empty:
                    break
                else:
                    if splited_line[1] not in empty:
                        try:
                            widget_id.append(int(splited_line[0]))
                            widget_text.append(int(splited_line[1]))
                        except ValueError:
                            try:
                                widget_text.append(float(splited_line[1]))
                            except ValueError:
                                widget_text.append(splited_line[1])
        

        for i, text in zip(widget_id, widget_text):
                text = self.str_to_bool(str(text))

                if not isinstance(text, bool):
                    list_line_edits[i].setText(text)
                else:
                    list_line_edits[i].setChecked(text)

        return


    def check_dilucion(self, estado):
        """
        Esta funcion desactiva los entries al desactivar el checkbox de la dilución.
        """
        if estado == 0:
            self.entry_diluc_min.setEnabled(False)
            self.entry_diluc_max.setEnabled(False)
            self.entry_diluc_step.setEnabled(False)
        else:
            self.entry_diluc_min.setEnabled(True)
            self.entry_diluc_max.setEnabled(True)
            self.entry_diluc_step.setEnabled(True)
        return


    def str_to_bool(self, text: str):
        """
        Esta función convierte un string en un bool (True o False).

        Input:
        * text: String que se quiere convertir

        Output:
        * True|False

        Ejemplo de uso
        >>> self.str_to_bool('false')
        False
        >>> self.str_to_bool('True')
        True
        >>> self.str_to_bool('Hola Mundo')
        'Hola Mundo'
        """
        true_list = [1, 'true', 'True', 'True\n']
        false_list = [0, 'false', 'False', 'False\n']

        if text in true_list:
            return True
        elif text in false_list:
            return False
        else:
            return text


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
        self.x_coordinate = self.combo_x_coordinate.currentText()
        self.x_coord = self.x_coordinate

        self.y_coordinate = self.combo_y_coordinate.currentText()
        self.y_coord = self.y_coordinate
        
        self.z_coordinate = self.combo_z_coordinate.currentText()
        self.z_coord = self.z_coordinate
        
        self.metal_grade = self.combo_metal_grade.currentText()
        self.metal_value = self.metal_grade
        return
    

    def start_iterations(self):
        """
        Esta función inicia el proceso de las iteraciones.
        """
        respuesta_iterations = self.alert_message_iterations()
        
        if respuesta_iterations == 1:
            self.button_iterate.setEnabled(False)
            self.iterations(test = False)
        elif respuesta_iterations == 2:
            self.button_iterate.setEnabled(False)
            self.iterations_study_cases()
        return
    

    def alert_message_iterations(self):
        """
        Esta función muestra una alerta a la hora de crear las iteraciones, ya que es un proceso que puede
        demorar mucho y generar muchos Gb en archivos.

        Retorna True o False.
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
        
        iterate_time = self.convert_time(self.iterations(test = True)*file_number)

        mensaje = QMessageBox(self)
        mensaje.setWindowTitle("Confirmación")
        mensaje.setText(
            f"¿Quieres generar todas las iteraciones?\n"
            f"({string_file_number} archivos | {string_files_size})\n"
            f"Demorará aproximadamente {iterate_time}")
        mensaje.setIcon(QMessageBox.Icon.Warning)
        mensaje.setStandardButtons(
            QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel)
        
        respuesta = mensaje.exec()

        if respuesta == QMessageBox.StandardButton.Ok:
            return 1
        if respuesta == QMessageBox.StandardButton.No:
            return 2
        if respuesta == QMessageBox.StandardButton.Cancel:
            return 0  


    def iterations_result_files(self):
        """
        Entrega el número de archivos que se crearán al realizar las iteraciones, además de un aproximado
        del peso de la carpeta que los contendrá.
        """
        self.list_entries = []
        self.list_entries_append()

        elements_in_range = []

        for elem in self.list_entries:
            elements_in_range.append(self.define_list(elem[0], elem[1], elem[2]))
        
        if self.check_diluc.isChecked():
            total_length = self.list_prod(
                [
                    len(elements_in_range[0]),
                    len(elements_in_range[1]),
                    len(elements_in_range[2]),
                    len(elements_in_range[3]),
                    len(elements_in_range[4]),
                    len(elements_in_range[5]),
                    len(elements_in_range[6])
                ]
            )
        else:
            total_length = self.list_prod(
                [
                    len(elements_in_range[0]),
                    len(elements_in_range[1]),
                    len(elements_in_range[2]),
                    len(elements_in_range[3]),
                    len(elements_in_range[4]),
                    len(elements_in_range[5])
                ]
            )

        return total_length, ((total_length + 5)*1200/1024)/1024


    def list_prod(self, lst):
        prod = 1
        for item in lst:
            prod *= item
        return prod


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

        >>> self.define_list(6, 3, 1)
        [3, 4, 5, 6]
        """
        if min == max:
            return [min]
        elif min > max:
            return np.arange(max, min + step, step)
        else:
            return np.arange(min, max + step, step)


    def list_entries_append(self):
        """
        Agrega las entradas a una lista para su posterior uso.
        """
        self.list_entries = []

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

        # Si se quiere hacer el cálculo con la dilución, se agregan las variables al algoritmo.
        if self.check_diluc.isChecked():
            self.list_entries.append([])
            self.list_entries[6].append(float(self.entry_diluc_min.text()))
            self.list_entries[6].append(float(self.entry_diluc_max.text()))
            self.list_entries[6].append(float(self.entry_diluc_step.text()))

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
    

    def update_progress(self, value):
        self.progress_bar.setValue(value = value)
        return
    

    def iterations(self, test: bool = False):
        """
        Proceso de iteraciones para el análisis de sensibilidad.
        """
        self.verify_folder()
        self.save_combobox()

        self.parameters_ranges = [
            self.define_list(self.list_entries[0][0], self.list_entries[0][1], self.list_entries[0][2]),
            self.define_list(self.list_entries[1][0], self.list_entries[1][1], self.list_entries[1][2]),
            self.define_list(self.list_entries[2][0], self.list_entries[2][1], self.list_entries[2][2]),
            self.define_list(self.list_entries[3][0], self.list_entries[3][1], self.list_entries[3][2]),
            self.define_list(self.list_entries[4][0], self.list_entries[4][1], self.list_entries[4][2]),
            self.define_list(self.list_entries[5][0], self.list_entries[5][1], self.list_entries[5][2])]
        
        if self.check_diluc.isChecked():
            self.parameters_ranges.append(self.define_list(self.list_entries[6][0], self.list_entries[6][1], self.list_entries[6][2]))
        else:
            self.parameters_ranges.append([0])

        self.combinations = self.create_combinations(self.parameters_ranges)

        self.total_files, total_folder_size = self.iterations_result_files()
        total_folder_size *= (1024*1024)
        aprox_file_size = 1200
        self.iteration_number = 0
        
        saved_data = {
                "x": self.loaded_dataframe[self.x_coordinate],
                "y": self.loaded_dataframe[self.y_coordinate],
                "z": self.loaded_dataframe[self.z_coordinate],
                "grade": self.loaded_dataframe[self.metal_grade],
                "period": self.loaded_dataframe["Period"],
                "antes_max": self.loaded_dataframe["antes_max"]
            }

        for price, m_cost, p_cost, discount, recov, sell_c, dilut in self.combinations:

            t1 = time.time()
            self.iteration_number += 1
            
            df_saved = pd.DataFrame(saved_data)
            volume = 1000

            df_saved["value"] = self.calculate_block_value(
                price = price,
                sell_cost = sell_c,
                volume = volume,
                density = 2.7,
                recovery = recov,
                grade = df_saved["grade"],
                mine_cost = m_cost,
                plant_cost = p_cost,
                dilution = dilut
            )
            df_saved["disc_value"] = df_saved["value"]/((1 + discount/100) ** df_saved["period"])
            df_saved = self.set_antes_max(df_saved)

            file_name = f'p{round(price, 1)}mc{round(m_cost, 1)}pc{round(p_cost, 1)}d{round(discount, 1)}r{round(recov, 1)}sc{round(sell_c, 1)}dil{round(dilut, 1)}.csv'

            case = self.set_study_case(self.parameters_ranges, price, m_cost, p_cost, discount, recov, sell_c, dilut)

            if case != '':
                self.save_file(df_saved, f"{case}.csv", normal = False)
                case = ""

            if test == True:
                self.save_file(df_saved, "test.csv", test = True)
                return time.time() - t1
            
            self.save_file(df_saved, file_name, normal = True)

            self.update_gui()
        
        self.progress_bar.setValue(100)
        self.finish_iterations()
        return
    

    def iterations_study_cases(self):
        """
        Proceso de iteraciones para el análisis de sensibilidad.
        """
        self.verify_folder()
        self.save_combobox()

        self.total_files = 5
        self.parameters_ranges = [
            self.define_list(self.list_entries[0][0], self.list_entries[0][1], self.list_entries[0][2]),
            self.define_list(self.list_entries[1][0], self.list_entries[1][1], self.list_entries[1][2]),
            self.define_list(self.list_entries[2][0], self.list_entries[2][1], self.list_entries[2][2]),
            self.define_list(self.list_entries[3][0], self.list_entries[3][1], self.list_entries[3][2]),
            self.define_list(self.list_entries[4][0], self.list_entries[4][1], self.list_entries[4][2]),
            self.define_list(self.list_entries[5][0], self.list_entries[5][1], self.list_entries[5][2])]
        file_names = [
            '1 best.csv',
            '2 mid75.csv',
            '3 mid50.csv',
            '4 mid25.csv',
            '5 worst.csv'
        ]

        if self.check_diluc.isChecked():
            self.parameters_ranges.append(self.define_list(self.list_entries[6][0], self.list_entries[6][1], self.list_entries[6][2]))
        else:
            self.parameters_ranges.append([0])
        
        saved_data = {
                "x": self.loaded_dataframe[self.x_coordinate],
                "y": self.loaded_dataframe[self.y_coordinate],
                "z": self.loaded_dataframe[self.z_coordinate],
                "grade": self.loaded_dataframe[self.metal_grade],
                "period": self.loaded_dataframe["Period"],
                "antes_max": self.loaded_dataframe["antes_max"]
            }
        iterations_values = []

        for item in self.parameters_ranges:
            iterations_values.append(self.list_percentage(item, (0, 25, 50, 75, 100)))
        
        iterations_params = [
            [iterations_values[0][4], iterations_values[1][0], iterations_values[2][0], iterations_values[3][0], iterations_values[4][4], iterations_values[5][0], iterations_values[6][0]],
            [iterations_values[0][3], iterations_values[1][1], iterations_values[2][1], iterations_values[3][1], iterations_values[4][3], iterations_values[5][1], iterations_values[6][1]],
            [iterations_values[0][2], iterations_values[1][2], iterations_values[2][2], iterations_values[3][2], iterations_values[4][2], iterations_values[5][2], iterations_values[6][2]],
            [iterations_values[0][1], iterations_values[1][3], iterations_values[2][3], iterations_values[3][3], iterations_values[4][1], iterations_values[5][3], iterations_values[6][3]],
            [iterations_values[0][0], iterations_values[1][4], iterations_values[2][4], iterations_values[3][4], iterations_values[4][0], iterations_values[5][4], iterations_values[6][4]]
        ]

        self.iteration_number = 0
        for it in iterations_params:
            df_saved = pd.DataFrame(saved_data)
            volume = 1000
            df_saved['value'] = self.calculate_block_value(
                price = it[0],
                sell_cost = it[5],
                volume = volume,
                density = 2.7,
                recovery = it[4],
                grade = df_saved['grade'],
                mine_cost = it[1],
                plant_cost = it[2],
                dilution = it[6]
            )
            df_saved["disc_value"] = df_saved["value"]/((1 + it[3]/100) ** df_saved["period"])
            df_saved = self.set_antes_max(df_saved)

            self.save_file(df_saved, file_names[self.iteration_number], normal = False)
            
            self.iteration_number += 1

        self.progress_bar.setValue(100)
        self.finish_iterations()
        return
    

    def verify_folder(self):
        """
        Esta funcion verifica que existan las carpetas donde guardar las iteraciones y los casos especiales.
        """
        folder_name_iterations = "Iteraciones"
        folder_name_cases = "Casos"

        path_iterations = os.path.join("reports", folder_name_iterations)
        path_cases = os.path.join("reports", folder_name_cases)

        if not os.path.exists(path_iterations):
            os.makedirs(path_iterations)
        else:
            self.clear_files(path_iterations)
        
        if not os.path.exists(path_cases):
            os.makedirs(path_cases)
        else:
            self.clear_files(path_cases)

        return
    

    def clear_files(self, path: str):
        """
        Elimina los archivos dentro de una carpeta.
        
        Inputs:
        * path: Directorio de la carpeta a la cual se le quieren eliminar los archivos.
        """
        files = os.listdir(path)

        if files:
            for folder_file in files:
                file_path = os.path.join(path, folder_file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        return
    

    def create_combinations(self, list_of_lists: list):
        """
        Crea combinaciones entre cada elemento de las listas que se ingresen.
        
        Inputs:
        lst: Cantidad cualquiera de listas.

        Output:
        Lista con combinaciones entre los elementos de las listas ingresadas.

        Ejemplo de uso:
            >>> self.create_combinations([1, 2], ["a", "b", "c"])
            [(1, "a"), (1, "b"), (1, "c"), (2, "a"), (2, "b"), (2, "c")]
        """
        if not list_of_lists:
            return []
        return list(product(*list_of_lists))
    

    def calculate_block_value(self, price:int|float, sell_cost:int|float, volume:int|float, density:int|float, recovery:int|float, grade:int|float, mine_cost:int|float, plant_cost:int|float, dilution = 0):
        """
        Esta funcion calcula el valor de un bloque dados los parámetros económicos.

        Inputs:
        * price: Precio del metal (usd/lb).
        * sell_cost: Precio de venta del metal (usd/lb).
        * volume: Volumen del bloque en el modelo de bloques (m3).
        * density: Densidad del material (t/m^3).
        * recovery: Recuperación de metal (%).
        * grade: Concentración de metal (%).
        * mine_cost: Costo de mina ($/t).
        * plant_cost: Costo de planta ($/t).
        * dilution: Dilución de la ley de los bloques (%)

        Outputs:
        * income - outcome: Valor del bloque

        Ejemplo de uso:
            >>> self.calculate_block_value(4, 1, 1000, 2.7, 85, 1, 19, 22)
            41,088.78
        """
        income = (price - sell_cost)*volume*density*(recovery/100)*(grade/100)*2204.63
        outcome = (mine_cost + plant_cost)*volume*density*(1 + dilution/100)
        return income - outcome
    

    def set_study_case(self, parameters_range:list, price:float, mine_cost:float, plant_cost:float, discount:int, recovery:int, sell_cost:float, dilution: int):
        """
        Esta funcion ayuda a seleccionar la iteración con la que se está trabajando, si corresponde al Best Case, Worst Case, o casos intermedios
        
        Inputs:
        * parameters_range: Lista que en cada elemento posee una lista, estos elementos son el rango en el que se moverá cada uno de los parámetros.
        * price: Precio del metal.
        * mine_cost: Costo de minado del metal.
        * plant_cost: Costo de planta del metal.
        * discount: Tasa de descuento.
        * recovery: Recuperación de metal.
        * sell_cost: Costo de venta del metal.

        Outputs:
        * -> strings: ['best', 'worst', 'mid25', 'mid50', 'mid75']
        """
        # Lista con parámetros actuales
        list_scenario = [price, mine_cost, plant_cost,
                         discount, recovery, sell_cost, dilution]
        
        # Recuperar minimos y máximos
        min_price,      max_price =         parameters_range[0][0], parameters_range[0][-1]
        min_mine_cost,  max_mine_cost =     parameters_range[1][0], parameters_range[1][-1]
        min_plant_cost, max_plant_cost =    parameters_range[2][0], parameters_range[2][-1]
        min_discount,   max_discount =      parameters_range[3][0], parameters_range[3][-1]
        min_recovery,   max_recovery =      parameters_range[4][0], parameters_range[4][-1]
        min_sell_cost,  max_sell_cost =     parameters_range[5][0], parameters_range[5][-1]

        # Recuperar casos intermedios
        price_25,       price_50,       price_75 =      self.list_percentage(parameters_range[0], (25, 50, 75))
        mine_cost_25,   mine_cost_50,   mine_cost_75 =  self.list_percentage(parameters_range[1], (25, 50, 75))
        plant_cost_25,  plant_cost_50,  plant_cost_75 = self.list_percentage(parameters_range[2], (25, 50, 75))
        discount_25,    discount_50,    discount_75 =   self.list_percentage(parameters_range[3], (25, 50, 75))
        recovery_25,    recovery_50,    recovery_75 =   self.list_percentage(parameters_range[4], (25, 50, 75))
        sell_cost_25,   sell_cost_50,   sell_cost_75 =  self.list_percentage(parameters_range[5], (25, 50, 75))

        if self.check_diluc.isChecked():
            min_dilution, max_dilution = parameters_range[6][0], parameters_range[6][-1]
            dilution_25, dilution_50, dilution_75 = self.list_percentage(parameters_range[6], (25, 50, 75))
        else:
            min_dilution = max_dilution = 0
            dilution_25 = dilution_50 = dilution_75 = 0

        list_best = [max_price, min_mine_cost, min_plant_cost,
                    min_discount, max_recovery, min_sell_cost, min_dilution]
        
        list_worst = [min_price, max_mine_cost, max_plant_cost,
                      max_discount, min_recovery, max_sell_cost, max_dilution]
        
        list_midcase_25 = [price_25, mine_cost_75, plant_cost_75,
                           discount_75, recovery_25, sell_cost_75, dilution_75]

        list_midcase_50 = [price_50, mine_cost_50, plant_cost_50,
                           discount_50, recovery_50, sell_cost_50, dilution_50]

        list_midcase_75 = [price_75, mine_cost_25, plant_cost_25,
                           discount_25, recovery_75, sell_cost_25, dilution_25]
        
        if list_scenario == list_best:
            return "1 best"
        elif list_scenario == list_worst:
            return "5 worst"
        elif list_scenario == list_midcase_25:
            return "4 mid25"
        elif list_scenario == list_midcase_50:
            return '3 mid50'
        elif list_scenario == list_midcase_75:
            return '2 mid75'
        
        return ""
    

    def list_percentage(self, lst: list, perc: tuple|int):
        """
        Esta funcion retorna el elemento en la posición del porcentaje dado.
        Si se selecciona perc = 50, retornará el elemento en la mitad de la lista.
        Si se selecciona perc = 0, retornará el primer elemento.
        Si se selecciona perc = 100, retornará el último elemento.

        Inputs:
        * lst: Lista con los elementos.
        * perc: Porcentaje de la lista al cual se quiere retorar el elemento. Debe estar en el rango [0, 100]

        Outputs:
        * num: Elemento en la posición seleccionada.

        Ejemplo de uso:
        >>> self.list_percentage([1, 2, 3, 4, 5, 6, 7, 8, 9], 50)
        5
        >>> self.list_percentage([1, 2, 3, 4, 5, 6, 7, 8, 9], 100)
        9
        >>> self.list_percentage([1, 2, 3, 4, 5, 6, 7, 8, 9], 0)
        1
        """
        if isinstance(perc, tuple):
            values = []
            for num in perc:
                if not (0 <= num <= 100):
                    raise ValueError(f'perc, must be in interval [0, 100]')

                if len(lst) == 0:
                    values.append(0)
                
                if num == 100:
                    values.append(lst[-1])
                else:
                    values.append(lst[len(lst)*num // 100])
            
            return values
        
        elif isinstance(perc, int):
            if not (0 <= perc <= 100):
                raise ValueError(f'perc, must be in interval [0, 100]')

            if len(lst) == 0:
                return 0
            
            if perc == 100:
                return lst[-1]
            else:
                return lst[len(lst)*perc // 100]
        return


    def set_antes_max(self, df):
        """
        Esta funcion modifica la columna 'antes_max' del dataframe.
        * Se hace un filtro en cada elemento, se agrupan los que tienen igual coordenada (x, y), de esta forma se aisla cada columna.
        * Se realiza la suma acumulada del valor descontado en cada columna.
        * Se identifica el valor máximo del valor acumulado en cada columna.
        * Se asigna el valor de 1 a cada fila de la columna, desde la base hasta el valor máximo encontrado.
        """
        column_dataframes = []

        try:
            df['antes_max'] = 0

            grouped = df.groupby(['x', 'y'])

            for _, group in grouped:
                column_dataframes.append(group)
                group['valor_acum'] = group['disc_value'].cumsum()
            
            for df in column_dataframes:
                max_valor_acum = df[df['valor_acum'] > 0]['valor_acum'].max()
                if pd.notna(max_valor_acum):
                    max_index = df[df['valor_acum'] == max_valor_acum].index[0]
                    df.loc[:max_index, 'antes_max'] = 1
        except Exception:
            QMessageBox.critical(
                self,
                "Error",
                "Error al cargar los archivos en 'casos'."
            )

        return pd.concat(column_dataframes, ignore_index = True)
    

    def save_file(self, df, name:str, normal = True, test = False):
        """
        Esta función guarda los dataframes creados en la carpeta iterations y cases dentro de la carpeta data.
        
        Inputs:
        * name: Nombre que tendrá el archivo (debe contener la extensión)
        * normal: Define si el archivo se creará en la carpeta iterations o en la carpeta cases. True es para una
        iteración normal, False es para los casos de estudio (best case, worst case, mid case)

        Outputs:
        * Se crea un archivo dentro de una de las carpetas iterations o cases (dependiendo del parámetro normal).
        """
        if test:
            path = os.path.join("reports")
            if not os.path.exists(path):
                os.makedirs(path)
            
            file_path = os.path.join(path, name)
            df.to_csv(file_path, index = False)
            return


        if normal:
            path = os.path.join("reports", "iteraciones")
            if not os.path.exists(path):
                os.makedirs(path)

            file_path = os.path.join(path, name)
            df.to_csv(file_path, index = False)
            return
        else:
            path = os.path.join("reports", "casos")
            if not os.path.exists(path):
                os.makedirs(path)

            file_path = os.path.join(path, name)
            df.to_csv(file_path, index = False)
            return


    def update_gui(self):
        QCoreApplication.processEvents()
        progress_index = int((self.iteration_number/self.total_files)*100)
        self.progress_bar.setValue(progress_index)
        return


    def finish_iterations(self):
        """
        Esta funcion establece las acciones que se llevarán a cabo una vez termine de ejecutarse el loop de las iteraciones.
        """
        QMessageBox.information(
            self,
            "Completado",
            "Se han completado las iteraciones",
            QMessageBox.StandardButton.Ok
        )
        
        self.progress_bar.setValue(0)

        self.button_iterate.setEnabled(True)
        self.button_stop.setEnabled(False)
        return


    def quit_app(self):
        """
        Esta función cierra la aplicación´.
        """
        self.close()
        return        