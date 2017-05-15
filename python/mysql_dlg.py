import pymysql

from design import mysql_login

from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets



class MySQLDialog(QDialog, mysql_login.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_connect.clicked.connect(self.connect)

    def connect(self):
        port = int(self.edt_port.text())
        user = self.edt_user.text()
        pw = self.edt_pw.text()
        try:
            conn = pymysql.connect(host="localhost", port=port, user=user, passwd=pw, db="mysql", charset="utf8")

        except Exception as e:
            print(e)
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Failed to connect to MySQL server")
            msg.setInformativeText("Please make sure MySQL server is running and the credentials are correct")
            msg.setWindowTitle("MySQL connection error")
            msg.exec_()
            return

        conn.close()

        self.cred = (port, user, pw)

        self.accept()