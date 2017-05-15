import classes
from classes.CIM_reader import CIM_reader
from classes.SQL_db import SQL_thread
from classes.Y_matrix import Y_matrix

import design
from mysql_dlg import MySQLDialog
from design.GUI_assignment1 import Ui_MainWindow

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

class MyGUI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setup_initial_values()
        self.update_buttons()
        self.define_event_handlers()

    # Connect the buttons and text labels to the functions
    def define_event_handlers(self):
        self.btn_browse_EQ.clicked.connect(self.browse_EQ)
        self.btn_browse_SSH.clicked.connect(self.browse_SSH)
        self.btn_parse_xml.clicked.connect(self.parse_xml)

        self.btn_create_db.clicked.connect(self.create_db)

        self.btn_calc_Y_bus.clicked.connect(self.calc_adm_matrix)
        self.btn_export_csv.clicked.connect(self.export_csv)

        self.edt_eq_path.textChanged.connect(self.update_buttons)
        self.edt_ssh_path.textChanged.connect(self.update_buttons)
        self.edt_db_name.textChanged.connect(self.update_buttons)

    # Select the path of the EQ file
    def browse_EQ(self):
        eq_file, _ = QFileDialog.getOpenFileName(self, caption="Browse CIM equipment (EQ) file", filter="*.xml")
        self.edt_eq_path.setText(eq_file)

    # Select the path of the SSH file
    def browse_SSH(self):
        ssh_file, _ = QFileDialog.getOpenFileName(self, caption="Browse CIM steady state hypothesis (SSH) file",
                                                       filter="*.xml")
        self.edt_ssh_path.setText(ssh_file)

    # Executes the CIM_reader class processing methods (Meaning that this merge the EQ and SSH XML files)
    def parse_xml(self):
        self.setup_initial_values()
        eq_file = self.edt_eq_path.text()
        ssh_file = self.edt_ssh_path.text()
        try:
            cr = CIM_reader(eq_file, ssh_file)
            self.ps_objs = cr.process_xml()
        except IOError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("XML files could not be found")
            msg.setInformativeText("Please select paths to existing EQ and SSH files")
            msg.setWindowTitle("XML IO error")
            msg.exec_()
            return
        except Exception as e:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("XML files could not be parsed")
            msg.setInformativeText("Please select legitimate EQ and SSH files")
            msg.setWindowTitle("XML parsing error")
            msg.setDetailedText(str(e))
            msg.exec_()
            return

        # Calls and auxiliary method to create a tree from the objects list
        self.write_objs_to_tree(self.ps_objs)
        self.update_buttons()

    # Auxiliary Method to populate the tree Window (Where the parsed XML is shown)
    def write_objs_to_tree(self, objs):
        tree = self.tree_xml
        model = QtGui.QStandardItemModel()

        model.setHorizontalHeaderLabels(["Power System Objects and Attributes"])
        tree.setModel(model)
        for obj_id, obj in objs.items():
            parent = QtGui.QStandardItem("{} - (\"{}\")".format(obj.__name__, obj_id))
            for attr in dir(obj):
                if attr[:2] + attr[-2:] != "____":
                    val = getattr(obj, attr)
                    child = QtGui.QStandardItem("{}: {}".format(attr, getattr(obj, attr)))
                    parent.appendRow(child)

            model.appendRow(parent)

    # Executes the SQL_db class processing methods (Meaning that it creates the whole database)
    def create_db(self):
        dlg = MySQLDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.sql_thread = SQL_thread(self.ps_objs, dlg.cred, self.edt_db_name.text())
            self.sql_thread.status.connect(self.update_prog_bar)
            self.sql_thread.error.connect(self.sql_error)
            self.sql_thread.finished.connect(self.update_buttons)
            self.disable_buttons()

            self.sql_thread.start()

    # Executes the Y-matrix class processing methods (Meaning that this creates the Y-matrix)
    def calc_adm_matrix(self):
        self.y = Y_matrix(self.ps_objs)
        self.Y = self.y.build()

        self.print_table(self.Y)

        self.update_buttons()

    # Auxiliary method to populate the Table in the GUI showing the Y-matrix
    def print_table(self, matrix):
        try:
            table = self.tbl_Y_bus
            table.setRowCount(len(matrix))
            table.setColumnCount(len(matrix[0]))
            for i, row in enumerate(matrix):
                for j, val in enumerate(row):
                    table.setItem(i, j, QtWidgets.QTableWidgetItem("{:.2}".format(val)))
        except Exception as e:
            print(e)

    # Exports a CSV file once the Y-matrix is created
    def export_csv(self):

        p, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save admittance matrix in CSV file", filter="*.csv", directory="../output/adm_matrix")
        if p != "":
            with open(p, "w") as f:
                self.y.export_csv(f)
            f.close()

    # Change the status of the buttons while different processes are executed (Meaning that removes the grey buttons)
    def update_buttons(self):
        self.edt_db_name.setEnabled(True)
        self.edt_eq_path.setEnabled(True)
        self.edt_ssh_path.setEnabled(True)
        self.btn_browse_EQ.setEnabled(True)
        self.btn_browse_SSH.setEnabled(True)

        if self.edt_eq_path.text() and self.edt_ssh_path.text():
            self.btn_parse_xml.setEnabled(True)
        else:
            self.btn_parse_xml.setEnabled(False)

        if self.ps_objs:
            self.btn_calc_Y_bus.setEnabled(True)
        else:
            self.btn_calc_Y_bus.setEnabled(False)

        if self.ps_objs and self.edt_db_name.text():
            self.btn_create_db.setEnabled(True)
        else:
            self.btn_create_db.setEnabled(False)

        if self.Y:
            self.btn_export_csv.setEnabled(True)
        else:
            self.btn_export_csv.setEnabled(False)

    # Initialization of variables (that the methods will work with) and predefined text labels for the GUI
    def setup_initial_values(self):
        self.eq_file = self.ssh_file = ""
        self.ps_objs = set()
        if not (self.edt_eq_path.text() or self.edt_ssh_path.text()):
            self.edt_eq_path.setText("../data/Total_MG_T1_EQ_V2.xml")
            self.edt_ssh_path.setText("../data/Total_MG_T1_SSH_V2.xml")
        self.Y = []
        self.tbl_Y_bus.clear()
        self.tbl_Y_bus.setRowCount(0)
        self.tbl_Y_bus.setColumnCount(0)

    # Refresh the progress bar during the creation of the tables or databases
    def update_prog_bar(self, stat):
        self.prog_SQL_db.setValue(stat)

    # Initialization of the buttons to minimize user error
    def disable_buttons(self):
        self.btn_parse_xml.setEnabled(False)
        self.btn_calc_Y_bus.setEnabled(False)
        self.btn_create_db.setEnabled(False)
        self.btn_export_csv.setEnabled(False)
        self.btn_browse_EQ.setEnabled(False)
        self.btn_browse_SSH.setEnabled(False)

        self.edt_eq_path.setEnabled(False)
        self.edt_ssh_path.setEnabled(False)
        self.edt_db_name.setEnabled(False)

    # Auxiliary function to show the error of the database
    def sql_error(self, e):
        self.sql_thread.terminate()

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error while creating database:")
        msg.setInformativeText(e)
        msg.setWindowTitle("SQL Error")
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyGUI()
    window.show()
    sys.exit(app.exec_())
