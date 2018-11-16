#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets, uic
from file_operations import VleFileOperations
from os import path

qtMainWindow = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainWindow)


class VleGui(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        file_ops = VleFileOperations(self, app)
        self.setupUi(self)

        #self.status.setReadOnly(True)

        self.btn_psv_dir.clicked.connect(self.browse_psv_directory)
        self.btn_out_dir.clicked.connect(self.browse_output_directory)
        self.btn_exp_strip.clicked.connect(lambda: file_ops.strip_psv())

    def browse_psv_directory(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        'Browse',
                                                        path.expanduser(self.lne_psv_dir.text()),
                                                        'PSV files (*.psv)',
                                                        options=QtWidgets.QFileDialog.ReadOnly)
        if file:
            self.lne_psv_dir.setText(file)

    def browse_output_directory(self):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                        caption='Select output file',
                                                        directory=path.expanduser(self.lne_out_dir.text()),
                                                        filter='PSV files (*.psv)')

        if file:
            if str(file).endswith('.psv'):
                self.lne_out_dir.setText(file)
            else:
                self.lne_out_dir.setText(file + '.psv')

    def get_psv_directory(self):
        if self.lne_psv_dir.text():
            return str(self.lne_psv_dir.text())
        else:
            return None

    def get_output_directory(self):
        if self.lne_out_dir.text():
            return str(self.lne_out_dir.text())
        else:
            return None
