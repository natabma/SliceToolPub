from PyQt6.QtWidgets import QFrame,QHBoxLayout,QWidget,QVBoxLayout,QLabel,QFileDialog,QPushButton,QMessageBox
from PyQt6.QtCore import Qt,pyqtSignal

class MeshImportDialog(QFileDialog):
    '''
    File Dialog to open a Mesh File
    '''
    selectedFileSignal=pyqtSignal(str)
    def __init__(self):
        super().__init__()  
        self.setWindowTitle("Open 3D Object File")
        self.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        self.setViewMode(QFileDialog.ViewMode.Detail)
        self.setNameFilters(["3D Objekte (*.stl *.ply *.obj)"])
        self.selectNameFilter("3D Objekte (*.stl *.ply *.obj)")

    def launch(self):
        print("launching MeshImportDialog")
        if self.exec():
            selected_file = self.selectedFiles()[0]
            self.selectedFileSignal.emit(selected_file)
            # self.main.working_widget.load_mesh(selected_file)
            # return selected_file

class ExcelExportDialog(QFileDialog):
    '''
    File Dialog to save an EXCEL File
    '''
    selectedFileSignal=pyqtSignal(str)
    def __init__(self): 
        super().__init__()  
        self.setWindowTitle("Select Export File")
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.setViewMode(QFileDialog.ViewMode.Detail)
        self.setNameFilters(["Microsoft Excel Sheet (*.xlsx)"])
        self.selectNameFilter("Microsoft Excel Sheet (*.xlsx)")

    def launch(self):
        if self.exec():
            selected_file = self.selectedFiles()[0]
            self.selectedFileSignal.emit(selected_file)

class CSVExportDialog(QFileDialog):
    '''
    File Dialog to save a CSV File
    '''
    selectedFileSignal=pyqtSignal(str)
    def __init__(self): 
        super().__init__()  
        self.setWindowTitle("Select CSV File")
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        self.setViewMode(QFileDialog.ViewMode.Detail)
        self.setNameFilters(["Comma Separated Values (*.csv)"])
        self.selectNameFilter("Comma Separated Values (*.csv)")

    def launch(self):
        if self.exec():
            selected_file = self.selectedFiles()[0]
            self.selectedFileSignal.emit(selected_file)

class ErrorDialog(QMessageBox):
        def __init__(self): 
            super().__init__()  
            self.setIcon(QMessageBox.Icon.Critical)
            self.setText("Error")
            self.setWindowTitle("SliceTool")
            self.setFixedWidth(200)