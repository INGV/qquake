# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'service_information_widget.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from qgis.PyQt import QtCore, QtGui, QtWidgets


from qquake.qt_compat import (
    QT_FRAME_NO_FRAME,
)
class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(687, 613)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.info_browser = QtWidgets.QTextBrowser(Form)
        self.info_browser.setAutoFillBackground(False)
        self.info_browser.setFrameShape(QT_FRAME_NO_FRAME)
        self.info_browser.setOpenExternalLinks(True)
        self.info_browser.setObjectName("info_browser")
        self.verticalLayout.addWidget(self.info_browser)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
