from PyQt6.QtCore import QObject, pyqtSlot,Qt
from functools import partial

from STUi import STUi
from SliceTool import MainModel
from STSidebarViewModels import (
    ScaleWidgetViewModel,
    TrimWidgetViewModel,
    SlicingWidgetViewModel,
    ExportWidgetViewModel,
)
import vedo
import numpy as np
from PyQt6.QtWidgets import QApplication

class STController(QObject):
    """
    Controller Class for Slice Tool
    """
    def __init__(self, app:QApplication, model: MainModel, view: STUi):
        super().__init__()
        self._app=app
        self._model = model
        self._view = view
        self.scaleWidgetViewModel = ScaleWidgetViewModel(view)
        self.trimWidgetViewModel = TrimWidgetViewModel(view)
        self.slicingWidgetViewModel = SlicingWidgetViewModel(view)
        self.exportWidgetViewModel = ExportWidgetViewModel(view)
        self._connectSignalsAndSlots()

    @pyqtSlot(str)
    def _loadAndDisplayMesh(self, mesh_url):

        self._app.setOverrideCursor(Qt.CursorShape.BusyCursor)

        if not self._view.is_work_plotter_initialized:
            self._view.init_plotter_work()
            

        userMesh = self._model.loadMeshFromURL(mesh_url)
        self._view.vplt_work.add_or_replace_mesh_by_name(userMesh)

        self.scaleWidgetViewModel._load_mesh_dimensions(userMesh.bounds())

        self._view.vplt_work.add_or_replace_mesh_by_name(self._model.ScaledAxes)
        self._view.vplt_work.show(resetcam=True)
        
        self._view.pushButton_confirm_scale.setEnabled(True)
        self._view.toolBox_work.setCurrentIndex(0)

        self._view.tabWidget.setTabEnabled(1, True)
        self._switchToWorkingWidget()
        self._app.restoreOverrideCursor()
        

    def _onScaleChanged(self):
        selected_scale = self.scaleWidgetViewModel.conversion_factor

        self._model.scaleMesh(selected_scale)
        self._view.vplt_work.add_or_replace_mesh_by_name(self._model.ScaledAxes)
        self._view.vplt_work.show(resetcam=True)

        print(self._model._data.UserMesh.bounds(), selected_scale)

    def _onScalingFinished(self):
        self._view.vplt_work.remove("ScaledAxes")
        self._view.vplt_work.render()
        self._view.toolBox_work.setCurrentIndex(1)
        self._view.toolBox_work.setItemEnabled(0,False)

    def _onStartOrStopCutting(self):
        if self._view.pushButton_trim_mesh.isChecked():
            self._model.clearEverythingPostCutting()
            self._view.tabWidget.setTabEnabled(2,False)
            self._view.vplt_work.clear_everything_except(["UserMesh"])
            Cutter = self._model.startCutter()
            Cutter.add_to(self._view.vplt_work)
            Cutter.GetCurrentRenderer().Render()
            self._view.vplt_work.render()
        else:
            Cutter = self._model.stopCutter()
            if Cutter != None:
                Cutter.remove_from(self._view.vplt_work)
                Cutter.GetCurrentRenderer().Render()
                self._view.vplt_work.render()

    def _onInvertCutter(self):
        self._model.invertCutter()

    def _onResetCutter(self):
        self._model.resetCutter()

    def _onTrimFinished(self):
        if self._view.pushButton_trim_mesh.isChecked():
            Cutter = self._model.stopCutter()
            if Cutter != None:
                Cutter.remove_from(self._view.vplt_work)
                Cutter.render()
                self._view.vplt_work.render()
        self._view.toolBox_work.setCurrentIndex(2)

    def _toggleSetPoint(self, point_name):
        if point_name == "P1":
            if self._view.pushButton_add_p1.isChecked():
                self._connectCanvasEmitterToSetPoint(f"SlicingAxis{point_name}")
            else:
                self._disconnectCanvasEmitter()
        if point_name == "P2":
            if self._view.pushButton_add_p2.isChecked():
                self._connectCanvasEmitterToSetPoint(f"SlicingAxis{point_name}")
            else:
                self._disconnectCanvasEmitter()

    @pyqtSlot(str)
    def _connectCanvasEmitterToSetPoint(self, point_name):
        self._view.vplt_work.ClickedCoordinateEmitter.pt3d.connect(
            partial(self._onClickMakeSlicingAxisPoint, point_name)
        )

    def _disconnectCanvasEmitter(self):
        self._view.vplt_work.ClickedCoordinateEmitter.pt3d.disconnect()

    @pyqtSlot(np.ndarray)
    def _onClickMakeSlicingAxisPoint(self, point_name, pt3d):
        NewPoint = self._model.create_named_point(pt3d=pt3d, name=point_name)
        self.slicingWidgetViewModel._populate_input_fields(point_name, pt3d)
        self._view.vplt_work.add_or_replace_mesh_by_name(NewPoint)
        self._disconnectCanvasEmitter()
        self.slicingWidgetViewModel.uncheck_btn()

        if self._model.slicing_axis_can_be_drawn:
            self._createAndAddSlicingAxis()

    def _onInputMakeSlicingAxisPoint(self, point_name):
        """
        Called when the user inputs a point via the input fields.
        """
        if point_name == "SlicingAxisP1":
            pt3d = self.slicingWidgetViewModel.p3d_p1
        elif point_name == "SlicingAxisP2":
            pt3d = self.slicingWidgetViewModel.p3d_p2

        if pt3d is None:
            self._view.ErrorDialog.setInformativeText("Invalid Point Input")
            self._view.ErrorDialog.show()
            return

        NewPoint = self._model.create_named_point(pt3d=pt3d, name=point_name)
        self._view.vplt_work.add_or_replace_mesh_by_name(NewPoint)
        if self._model.slicing_axis_can_be_drawn:
            self._createAndAddSlicingAxis()

    def _createAndAddSlicingAxis(self):
        self._view.vplt_work.add_or_replace_mesh_by_name(self._model.SlicingArrow)
        slicing_axis_length_f = self._model.SlicingNormal.length()
        self.slicingWidgetViewModel.update_line_length_text(slicing_axis_length_f)
        self.slicingWidgetViewModel.slicing_input_validator.setTop(
            slicing_axis_length_f
        )
        self._eval_slicing_input()

    def _eval_slicing_input(self):
        """
        Evaluate (string) input of slicing height.
        """

        slicing_offset_p1_str = self._view.offsetFromP1LineEdit.text()
        if slicing_offset_p1_str == "":
            slicing_offset_p1_str = "0"
        slicing_offset_p1_f = float(slicing_offset_p1_str)
        is_valid_slicing_offset_p1 = slicing_offset_p1_f >= 0

        slicing_offset_p2_str = self._view.offsetFromP2LineEdit.text()
        if slicing_offset_p2_str == "":
            slicing_offset_p2_str = "0"
        slicing_offset_p2_f = float(slicing_offset_p2_str)
        is_valid_slicing_offset_p2 = slicing_offset_p2_f >= 0

        slicing_input_str = self._view.slicingIntervalLineEdit.text()
        if slicing_input_str == "":
            return
        slicing_input_f = float(slicing_input_str)
        is_valid_slicing_input = slicing_input_f > 0

        if (
            self._model.slicing_axis_can_be_drawn
            and is_valid_slicing_offset_p1
            and is_valid_slicing_offset_p2
            and is_valid_slicing_input
        ):
            slicing_axis_length_f = self._model.SlicingNormal.length()
            is_valid_slicing_params = (
                slicing_axis_length_f - (slicing_offset_p1_f + slicing_offset_p2_f)
            ) / slicing_input_f > 1
            if is_valid_slicing_params:
                self._model.setSlicingInputs(
                    slicing_offset_p1_f, slicing_offset_p2_f, slicing_input_f
                )
                self._sliceUserMeshAndShowSlices()

    def _sliceUserMeshAndShowSlices(self):
        SlicingResult = self._model.sliceUserMesh()
        if type(SlicingResult) == vedo.Assembly:
            self._view.vplt_work.add_or_replace_mesh_by_name(SlicingResult)
            self._view.pushButton_view_results.setEnabled(True)
        else:
            self._view.ErrorDialog.setInformativeText("Invalid Slicing Parameters")
            self._view.ErrorDialog.show()
            self._view.vplt_work.remove("SlicesAssembly")

    def _toggleUserMeshAlpha(self):
        self._model.toggleUserMeshAlpha()
        self._view.vplt_work.render()

    def _switchToResultWidget(self):
        self._updateResultWidget()
        self._view.tabWidget.setTabEnabled(2,True)
        self._view.tabWidget.setCurrentIndex(2)

    def _switchToWorkingWidget(self):
        self._view.tabWidget.setCurrentIndex(1)

    def _updateResultWidget(self):
        self._app.setOverrideCursor(Qt.CursorShape.BusyCursor)
        self.updateInputSectionThreshold()
        self._view.result_ax.clear_axes()
        # self._plotCircumferences()

        facecolors = self._model.section_facecolors
        print(f"Facecolors: {len(facecolors)}")
        slice_heights_arr = self._model.slice_heights_arr
        slice_lengths_arr = self._model.slice_lengths_arr

        print(
            f"Facecolors: {len(facecolors)}; Pairs: {len(self._model.pairwise_marked_section_indices)}"
        )

        for idx, pair in enumerate(self._model.pairwise_marked_section_indices):
            from_idx, to_idx = pair
            color = facecolors[idx]
            self._view.result_ax.fill_between(
                slice_heights_arr[from_idx : to_idx + 1],
                slice_lengths_arr[from_idx : to_idx + 1],
                facecolor=color,
            )

        self._view.result_ax.plot(slice_heights_arr, slice_lengths_arr, style="-")
        self._view.result_ax.plot(slice_heights_arr, slice_lengths_arr, style=".")
        if not self._view.is_result_plotter_initialized:
            self._view.init_plotter_results()
        self._view.vplt_results.add_or_replace_mesh_by_name(
            self._model.makeColoredAssembly()
        )
        self._view.vplt_results.show(camera=self._model.makeOrientedCameraForUserMesh())
        self._app.restoreOverrideCursor()

    def updateInputSectionThreshold(self):
        self._model.setSectionThreshold(self.exportWidgetViewModel.section_threshold)

    @pyqtSlot(str)
    def _exportToExcel(self, excel_file_url):
        self._model.saveSliceDataToExcel(excel_file_url)

    @pyqtSlot(str)
    def _CurvesToExcel(self, excel_file_url):
        self._model.saveSliceCurvesToExcel(excel_file_url)

    @pyqtSlot(str)
    def _exportToCSV(self, csv_file_url):
        self._model.saveSliceDataToCSV(csv_file_url)

    def _onClickExportSlices(self):
        self._view.ExcelExportDialog.selectedFileSignal.connect(self._exportToExcel)
        self._view.ExcelExportDialog.launch()
    def _onClickExportCurves(self):
        self._view.ExcelExportDialog.selectedFileSignal.connect(self._CurvesToExcel)
        self._view.ExcelExportDialog.launch()

    def _connectSignalsAndSlots(self):
        self._view.pushButton_load_mesh.pressed.connect(
            self._view.MeshImportDialog.launch
        )
        self._view.MeshImportDialog.selectedFileSignal.connect(self._loadAndDisplayMesh)

        self._view.comboBox_unit_scale.currentTextChanged.connect(self._onScaleChanged)
        self._view.pushButton_confirm_scale.pressed.connect(self._onScalingFinished)
        self._view.pushButton_trim_mesh.clicked.connect(self._onStartOrStopCutting)
        self._view.pushButton_invert_trim.clicked.connect(self._onInvertCutter)
        self._view.pushButton_reset_trim.clicked.connect(self._onResetCutter)
        self._view.pushButton_finished_trim.clicked.connect(self._onTrimFinished)

        self._view.pushButton_add_p1.clicked.connect(
            partial(self._toggleSetPoint, "P1")
        )
        self._view.pushButton_add_p2.clicked.connect(
            partial(self._toggleSetPoint, "P2")
        )
        self._view.slicingIntervalLineEdit.editingFinished.connect(
            self._eval_slicing_input
        )
        self._view.offsetFromP1LineEdit.editingFinished.connect(
            self._eval_slicing_input
        )
        self._view.offsetFromP2LineEdit.editingFinished.connect(
            self._eval_slicing_input
        )
        self._view.lineEdit_p1_x.editingFinished.connect(
            partial(self._onInputMakeSlicingAxisPoint, "SlicingAxisP1")
        )
        self._view.lineEdit_p1_y.editingFinished.connect(
            partial(self._onInputMakeSlicingAxisPoint, "SlicingAxisP1")
        )
        self._view.lineEdit_p1_z.editingFinished.connect(
            partial(self._onInputMakeSlicingAxisPoint, "SlicingAxisP1")
        )
        self._view.lineEdit_p2_x.editingFinished.connect(
            partial(self._onInputMakeSlicingAxisPoint, "SlicingAxisP2")
        )
        self._view.lineEdit_p2_y.editingFinished.connect(
            partial(self._onInputMakeSlicingAxisPoint, "SlicingAxisP2")
        )
        self._view.lineEdit_p2_z.editingFinished.connect(
            partial(self._onInputMakeSlicingAxisPoint, "SlicingAxisP2")
        )

        # self._view.WorkingWidget.Sidebar.SlicingWidget.CheckboxToggleAlpha.clicked.connect(
        #     self._toggleUserMeshAlpha
        # ) #TODO

        self._view.pushButton_view_results.pressed.connect(self._switchToResultWidget)

        self._view.markSectionsLineEdit.editingFinished.connect(
            self._updateResultWidget
        )
        self._view.pushButton_export_curve_lengths_xls.clicked.connect(
            self._onClickExportSlices
        )
        self._view.pushButton_export_curve_lengths_csv.clicked.connect(
            self._view.CSVExportDialog.launch
        )
        self._view.pushButton_export_curve_xls.clicked.connect(
            self._onClickExportCurves
        )

        self._view.CSVExportDialog.selectedFileSignal.connect(self._exportToCSV)
        # self._view.ExcelExportDialog
