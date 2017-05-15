# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mysql_login.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(371, 300)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 20, 311, 71))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.edt_user = QtWidgets.QLineEdit(Dialog)
        self.edt_user.setGeometry(QtCore.QRect(130, 160, 171, 20))
        self.edt_user.setObjectName("edt_user")
        self.edt_pw = QtWidgets.QLineEdit(Dialog)
        self.edt_pw.setGeometry(QtCore.QRect(130, 190, 171, 20))
        self.edt_pw.setText("")
        self.edt_pw.setFrame(True)
        self.edt_pw.setEchoMode(QtWidgets.QLineEdit.Password)
        self.edt_pw.setObjectName("edt_pw")
        self.edt_port = QtWidgets.QLineEdit(Dialog)
        self.edt_port.setGeometry(QtCore.QRect(130, 130, 171, 20))
        self.edt_port.setObjectName("edt_port")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(70, 130, 61, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(70, 160, 61, 20))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(70, 190, 61, 21))
        self.label_4.setObjectName("label_4")
        self.btn_connect = QtWidgets.QPushButton(Dialog)
        self.btn_connect.setGeometry(QtCore.QRect(70, 230, 231, 41))
        self.btn_connect.setObjectName("btn_connect")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "In order to create an SQL database, please make sure that a MySQL server is running on your localhost IP address and fill in the credentials below:"))
        self.edt_user.setText(_translate("Dialog", "root"))
        self.edt_port.setText(_translate("Dialog", "3306"))
        self.label_2.setText(_translate("Dialog", "Port:"))
        self.label_3.setText(_translate("Dialog", "Username:"))
        self.label_4.setText(_translate("Dialog", "Password:"))
        self.btn_connect.setText(_translate("Dialog", "Connect"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

