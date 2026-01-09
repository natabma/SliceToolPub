from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import pyqtSignal, QSize,QTimer
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk import vtkRenderer,vtkPropPicker


class QVTKRenderWindowInteractorMod(QVTKRenderWindowInteractor):
    '''
    Slightly modified QVTKRenderWindowInteractor. Allows for modification of the SizeHint, which defaults to 400x400.
    see: https://github.com/naucoin/VTKSlicerWidgets/blob/master/Wrapping/Python/vtk/qt4/QVTKRenderWindowInteractor.py
    '''

    def __init__(self,parent):
        super().__init__(parent)
        self.sizeHintQsize=QSize(400, 400)
    def sizeHint(self):
        return self.sizeHintQsize
    
class STVTKFrame(QFrame):
    '''
    Modified QFrame to encapsulate the vtk Render Window
    Written to fix a Bug where the VTK Window would not resize with the App.
    '''
    resizeEventSignal = pyqtSignal(QSize)

    def __init__(self, parent):
        super().__init__(parent)

        self.is_vtk_initialized=False

        self.qvtk_widget = None
        self.qvtk_render_window = None

        self.ren = vtkRenderer()
        self.setStyleSheet(
            "QFrame {background-color: yellow; border: 1px solid black;}"
        )

    def lazy_init_vtk(self):
        '''
        lazy loading of vtk stuff
        '''
        if self.is_vtk_initialized:
            return
        
        self.qvtk_widget = QVTKRenderWindowInteractorMod(self)
        self.qvtk_render_window = self.qvtk_widget.GetRenderWindow()
        self.is_vtk_initialized = True

        size=self.size()
        scaling_factor = self.devicePixelRatio()
        h = size.height() * scaling_factor
        w = size.width() * scaling_factor
        h = int(h)
        w = int(w)
        self.qvtk_widget.sizeHintQsize = size
        self.qvtk_render_window.SetSize(w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size=event.size()
        # print(f"Resize Event {event.size()}")

        if not self.is_vtk_initialized:
            return

        scaling_factor = self.devicePixelRatio()
        h = size.height() * scaling_factor
        w = size.width() * scaling_factor
        h = int(h)
        w = int(w)
        self.qvtk_widget.sizeHintQsize = event.size()
        self.qvtk_render_window.SetSize(w, h)
        
        
