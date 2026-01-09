from ui_SliceTool import Ui_MainWindow
from STDialogs import MeshImportDialog,ExcelExportDialog,ErrorDialog,CSVExportDialog

from STPlotter import STPlotter
from PyQt6.QtCore import Qt



class STUi(Ui_MainWindow):
    '''
    Class to initialize and hold all UI Elements, Dialogs etc.
    '''
    def __init__(self,main_window):

        

        super().__init__()
        
        self.setupUi(main_window)
        self.result_ax.set_title("Slice Circumferences","Slice Height","Circumference")

        self.MeshImportDialog = MeshImportDialog()
        self.ExcelExportDialog = ExcelExportDialog()
        self.CSVExportDialog = CSVExportDialog()
        self.ErrorDialog= ErrorDialog()

        # Deactivate Tabs exept Welcome Tab on startup
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabEnabled(1,False)
        self.tabWidget.setTabEnabled(2,False)

        self.pushButton_trim_mesh.setCheckable(True)
        self.pushButton_add_p1.setCheckable(True)
        self.pushButton_add_p2.setCheckable(True)
        self.is_work_plotter_initialized=False
        self.is_result_plotter_initialized=False
        
    def init_plotter_work(self):
        if self.is_work_plotter_initialized:
            return
        self.vtk_frame_working_widget.lazy_init_vtk()
        self.vplt_work=STPlotter(qt_widget=self.vtk_frame_working_widget.qvtk_widget)
        self.is_work_plotter_initialized=True
        
        
    def init_plotter_results(self):
        if self.is_result_plotter_initialized:
            return
        self.vtk_frame_results.lazy_init_vtk()
        self.vplt_results=STPlotter(qt_widget=self.vtk_frame_results.qvtk_widget)
        self.is_result_plotter_initialized=True