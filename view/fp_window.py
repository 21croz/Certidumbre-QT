from PyQt6 import QtWidgets, uic



class FootprintWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        uic.loadUi(r"ui\fp_window.ui", self)

        self.create_control_variables()

        self.define_widgets_variables()
        self.define_actions()

        self.define_dataframes()
        self.define_heights()


    def create_control_variables(self):
        return


    def define_widgets_variables(self):
        self.cota_z = self.findChild(QtWidgets.QComboBox, "combo_cota")

        self.check_best = self.findChild(QtWidgets.QCheckBox, "check_best")
        self.check_mid75 = self.findChild(QtWidgets.QCheckBox, "check_mid75")
        self.check_mid50 = self.findChild(QtWidgets.QCheckBox, "check_mid50")
        self.check_mid25 = self.findChild(QtWidgets.QCheckBox, "check_mid25")
        self.check_worst = self.findChild(QtWidgets.QCheckBox, "check_worst")

        self.button_refresh = self.findChild(QtWidgets.QPushButton, "button_guardar")
        return


    def define_actions(self):
        self.button_refresh.clicked.connect(self.refresh_plot)
        return


    def define_dataframes(self):
        return


    def define_heights(self):
        return


    def refresh_plot(self):
        return