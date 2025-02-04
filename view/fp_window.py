import os                                                                                   # 
import pandas as pd                                                                         # 
import matplotlib.pyplot as plt                                                             # Importa la librería de graficación.

from PyQt6 import QtWidgets, uic                                                            # 
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QGraphicsScene                        # Paquetes parte de PyQt6 > QtWidgets que ayudan a 
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from matplotlib.figure import Figure                                                        # 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas            # 



class FootprintWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi(r"ui\fp_window.ui", self)

        self.create_control_variables()

        self.define_widgets_variables()
        self.define_actions()

        self.define_dataframes()
        self.define_heights()

        self.create_plot_window()

        self.define_table()


    def create_control_variables(self):
        """
        Esta función crea las variables de control que se usarán en la ventana.
        """
        # Variables generales de la ventana.
        self.dataframes =   []
        self.coordinates =  []
        self.heights =      []
        self.states =       []

        # Variables para el gráfico.
        self.plot_labels =  ["Best case", "Mid case (75%)", "Mid case (50%)", "Mid case (25%)", "Worst case"]
        self.plot_colors =  ['#00b894', '#ffeaa7', '#0984e3', '#ff7675', '#636e72']
        self.plot_sizes =   [375, 300, 225, 150, 75]

        # Variables generales para la tabla
        self.table_data =       []
        self.table_van =        []
        self.table_column_q =   []
        self.table_tonnage =    []
        self.table_grade =      []
        return


    def define_widgets_variables(self):
        """
        Esta función define variables que se enlazan a los widgets puestos en Qt Designer.
        """
        self.cota_z = self.findChild(QtWidgets.QComboBox, "combo_cota")

        self.check_best = self.findChild(QtWidgets.QCheckBox, "check_best")
        self.check_mid75 = self.findChild(QtWidgets.QCheckBox, "check_mid75")
        self.check_mid50 = self.findChild(QtWidgets.QCheckBox, "check_mid50")
        self.check_mid25 = self.findChild(QtWidgets.QCheckBox, "check_mid25")
        self.check_worst = self.findChild(QtWidgets.QCheckBox, "check_worst")

        self.checkboxes = [self.check_best, self.check_mid75, self.check_mid50, self.check_mid25, self.check_worst]

        self.button_refresh = self.findChild(QtWidgets.QPushButton, "button_guardar")

        self.stats_table = self.findChild(QtWidgets.QTableView, "table_statistics")
        return


    def define_actions(self):
        """
        Esta función define las acciones que se llevarán a cabo al presionar botones de la interfaz.
        """
        self.button_refresh.clicked.connect(self.refresh_button)
        return


    def define_dataframes(self):
        """
        Esta funcion importa los dataframes de la carpeta 'Casos' en la variable >>> self.dataframes.
        """
        folder_path = os.path.join("reports", "Casos")
        try:
            csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

            for file in csv_files:
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path)
                self.dataframes.append(df[df['antes_max'] == 1])

        except Exception:
            QMessageBox.critical(
                self,
                "Error",
                "Error al cargar la carpeta 'Casos'")
        return


    def define_heights(self):
        """
        Esta funcion define las alturas que se mostrarán en el menú desplegable.
        """
        list_heights = []
        for df in self.dataframes:
            list_heights += df['z'].tolist()
        
        list_heights_ordered = sorted(list(set(list_heights)))
        self.cota_z.addItems(str(item) for item in list_heights_ordered)
        return


    def create_plot_window(self):
        """
        Estsa función crea la ventana donde se hará el gráfico del Footprint.
        """
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        return


    def refresh_button(self):
        """
        Esta función corresponde a la acción que se llevará a cabo al presionar el botón.
        """
        self.get_check_state()
        self.refresh_plot()
        return
    

    def get_check_state(self):
        """
        Esta función obtiene el estado de los checkbox de la interfaz, ya sea True o False.
        """
        self.states = []

        self.states = [cb.isChecked() for cb in self.checkboxes if cb]
        return


    def refresh_plot(self):
        """
        Esta función crea el gráfico.
        """
        self.define_coordinates()

        self.graphicsView.setScene(None)

        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        self.ax.clear()

        for i, show in enumerate(self.states):
            if show:
                self.ax.scatter(
                    self.coordinates[i]['x'].tolist(),
                    self.coordinates[i]['y'].tolist(),
                    label = self.plot_labels[i],
                    c = self.plot_colors[i],
                    s = self.plot_sizes[i]
                )
        
        self.ax.set_title("Gráfico Footprint")
        self.ax.legend()
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")

        self.escena = QGraphicsScene()
        self.escena.addWidget(self.canvas)

        self.graphicsView.setScene(self.escena)
        return
    

    def define_coordinates(self):
        """
        Esta función crea la variable self.coordinates, la cual contiene los dataframes filtrados por el combobox self.cota_z.
        """
        self.coordinates = []
        for df in self.dataframes:
            self.coordinates.append(df[df['z'] == int(self.cota_z.currentText())])
        return
    

    def define_table(self):
        """
        Esta función crea la tabla donde se mostrarán los datos estadísticos
        de cada caso de estudio.
        Para este caso, las columnas serán:
        * Nombre.
        * VAN.
        * Q Columnas.
        * Tonelaje.
        * Ley promedio.
        """
        self.model = QStandardItemModel(5, 5)
        self.model.setHorizontalHeaderLabels(["Caso", "VAN [MUSD]", "Nro. Columnas", "Tonelaje [Mt]", "Ley promedio [%]"])

        self.define_table_params()
        self.params_to_table()

        for row_index, row in enumerate(self.table_data):
            for col_index, value in enumerate(row):
                item = QStandardItem(str(value))
                self.model.setItem(row_index, col_index, item)
        
        self.stats_table.setModel(self.model)
        return
    

    def define_table_params(self):
        """
        Esta función define los parámetros estadísticos que se obtendrán en cada uno de los casos de estudio.
        """
        for df in self.dataframes:
            column_dataframes = []
            column_sum = []
            grouped = df.groupby(['x', 'y'])
            ton = 1000*2.7

            for _, group in grouped:
                column_dataframes.append(group)
                group['valor_acum'] = group['disc_value'].cumsum()
                max_van = group['valor_acum'].max()
                column_sum.append(max_van)
            
            case_van = round(sum(column_sum) / 1_000_000, 2)
            self.table_van.append(case_van)

            case_column_q = len(grouped)
            self.table_column_q.append(case_column_q)

            case_tonnage = round(df.shape[0]*ton/1_000_000, 2)
            self.table_tonnage.append(case_tonnage)

            case_grade = round(df['grade'].sum()/df.shape[0], 5)
            self.table_grade.append(case_grade)
        return
    

    def params_to_table(self):
        """
        Esta función define la variable table_data, agregando los valores obtenidos por la función >>> self.define_table_params().
        """
        self.table_data = []
        for name, van, q, ton, g in zip(self.plot_labels, self.table_van, self.table_column_q, self.table_tonnage, self.table_grade):
            self.table_data.append([name, van, q, ton, g])
        return