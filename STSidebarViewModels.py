from STUi import STUi
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QDoubleValidator
import numpy as np

class ScaleWidgetViewModel():
    def __init__(self, view:STUi):
        self._view = view
        self.conversion_dict_to_mm = {
            "mm": 1,
            "cm": 10,
            "m": 1000,
            "in": 25.4,
            "ft": 304.8,
        }

        self.mesh_size = [0, 0, 0]
        self.conversion_factor = 1
        self._connectSignalsAndSlots()

        self._view.comboBox_unit_scale.clear()
        self._view.comboBox_unit_scale.addItems(self.conversion_dict_to_mm.keys())
        self._view.comboBox_unit_scale.setCurrentText("mm")        

    def _load_mesh_dimensions(self,mesh_bounds):
        self.mesh_size=[abs(mesh_bounds[idx] - mesh_bounds[idx+1]) for idx, val in enumerate(mesh_bounds) if idx%2==0]
        self._scale_changed()

    def _refresh_import_labels(self):
        mesh_size_import_label_str=[str(round(dim,2)) for dim in self.mesh_size]

        for idx,label in enumerate(mesh_size_import_label_str):
            table_item=QTableWidgetItem(f"{label} {self._view.comboBox_unit_scale.currentText()}")
            self._view.tableWidget_import_units.setItem(0,idx,table_item)

    def _scale_changed(self):
        self._refresh_import_labels()
        try:
            self.conversion_factor=self.conversion_dict_to_mm[self._view.comboBox_unit_scale.currentText()]
        except KeyError:
            self.conversion_factor = 1
            
        target_units_at_current_scale_label_str=[str(round(dim*self.conversion_factor,2)) for dim in self.mesh_size]
        for idx,label in enumerate(target_units_at_current_scale_label_str):
            table_item=QTableWidgetItem(f"{label} mm")
            self._view.tableWidget_internal_units.setItem(0,idx,table_item)

    def _connectSignalsAndSlots(self):
        self._view.comboBox_unit_scale.currentTextChanged.connect(self._scale_changed)
        

class TrimWidgetViewModel():
    def __init__(self, view:STUi):
        self._view = view
        self._view.pushButton_invert_trim.setEnabled(False)
        self._view.pushButton_reset_trim.setEnabled(False)
        self._connectSignalsAndSlots()

    def _swich_trim_btn_text(self):
        if not self._view.pushButton_trim_mesh.isChecked():
            self._view.pushButton_trim_mesh.setText("Trim Mesh")
            self._view.pushButton_invert_trim.setEnabled(False)
            self._view.pushButton_reset_trim.setEnabled(False)
            # self._view.toolBox_work.setEnabled(False)
            # self._view.tabWidget.setEnabled(False)
        else:
            self._view.pushButton_trim_mesh.setText("Select Areas to remove.")
            self._view.pushButton_invert_trim.setEnabled(False)
            self._view.pushButton_reset_trim.setEnabled(False)
            # self._view.toolBox_work.setEnabled(True)
            # self._view.tabWidget.setEnabled(True)
    def _connectSignalsAndSlots(self):
        self._view.pushButton_trim_mesh.pressed.connect(self._swich_trim_btn_text)

class SlicingWidgetViewModel():
    def __init__(self, view:STUi):
        self._view = view
        self.PointInputValidator=QDoubleValidator(
                            decimals=2,
                            notation=QDoubleValidator.Notation.StandardNotation
                        )
        self.slicing_input_validator=QDoubleValidator(
                                bottom=0.0,
                                top=100,
                                decimals=2,
                                notation=QDoubleValidator.Notation.StandardNotation
                            )
        
        self._view.lineEdit_p2_z.setValidator(self.PointInputValidator)
        self._view.lineEdit_p2_y.setValidator(self.PointInputValidator)
        self._view.lineEdit_p2_x.setValidator(self.PointInputValidator)
        self._view.lineEdit_p1_z.setValidator(self.PointInputValidator)
        self._view.lineEdit_p1_y.setValidator(self.PointInputValidator)
        self._view.lineEdit_p1_x.setValidator(self.PointInputValidator)

        self._view.slicingIntervalLineEdit.setValidator(self.slicing_input_validator)
        self._view.offsetFromP1LineEdit.setValidator(self.slicing_input_validator)
        self._view.offsetFromP2LineEdit.setValidator(self.slicing_input_validator)

    def _populate_input_fields(self, point_name, pt3d):
        if point_name == "SlicingAxisP1":
            self._view.lineEdit_p1_x.setText(f"{pt3d[0]:.2f}")
            self._view.lineEdit_p1_y.setText(f"{pt3d[1]:.2f}")
            self._view.lineEdit_p1_z.setText(f"{pt3d[2]:.2f}")
        elif point_name == "SlicingAxisP2":
            self._view.lineEdit_p2_x.setText(f"{pt3d[0]:.2f}")
            self._view.lineEdit_p2_y.setText(f"{pt3d[1]:.2f}")
            self._view.lineEdit_p2_z.setText(f"{pt3d[2]:.2f}")

    def _check_btn_point_1(self):
        if self._view.pushButton_add_p1.isChecked():
            self._view.pushButton_add_p1.setText("Click on the Mesh to Select Point 1.")

    def _check_btn_point_2(self):
        if self._view.pushButton_add_p2.isChecked():
            self._view.pushButton_add_p2.setText("Click on the Mesh to Select Point 2.")
    
    def uncheck_btn(self):
        if self._view.pushButton_add_p1.isChecked():
            self._view.pushButton_add_p1.setChecked(False)
            self._view.pushButton_add_p1.setText("Add/Modify Point 1")
        if self._view.pushButton_add_p2.isChecked():
            self._view.pushButton_add_p2.setChecked(False)
            self._view.pushButton_add_p2.setText("Add/Modify Point 2")

    def update_line_length_text(self,new_length):
        self._view.label_slice_line_length.setText(f"Distance of P1 and P2: {str(round(new_length,2))}")

    @property
    def p3d_p1(self):
        try:
            return np.array([
                float(self._view.lineEdit_p1_x.text()),
                float(self._view.lineEdit_p1_y.text()),
                float(self._view.lineEdit_p1_z.text())
            ])
        except ValueError:
            return None
    @property
    def p3d_p2(self):
        try:
            return np.array([
                float(self._view.lineEdit_p2_x.text()),
                float(self._view.lineEdit_p2_y.text()),
                float(self._view.lineEdit_p2_z.text())
            ])
        except ValueError:
            return None

    def _connectSignalsAndSlots(self):
        self._view.pushButton_add_p1.pressed.connect(self._check_btn_point_1)
        self._view.pushButton_add_p2.pressed.connect(self._check_btn_point_2)
    
class ExportWidgetViewModel():
    def __init__(self, view:STUi):
        self._view = view

    @property
    def section_threshold(self):

        sect_treshold_str=self._view.markSectionsLineEdit.text()
        if sect_treshold_str == "":
            sect_treshold_str = "5"
            self._view.markSectionsLineEdit.setText(sect_treshold_str)

        sect_treshold_f=float(sect_treshold_str)
        
        sect_treshold_f = max(5.0,sect_treshold_f)
        sect_treshold_f = min(35.0,sect_treshold_f)

        return sect_treshold_f