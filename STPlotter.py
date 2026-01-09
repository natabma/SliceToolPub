from vedo import Plotter
import numpy as np
from PyQt6.QtCore import pyqtSignal,QObject


class ClickedCoordinateEmitter(QObject):
    # Define a custom signal with a value
    pt3d = pyqtSignal(np.ndarray)

class STPlotter(Plotter):
    '''
    Vedo Plotter with some additional Functionalities
    '''

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.add_callback('mouse click',self.pick_coordinate)
        self.ClickedCoordinateEmitter = ClickedCoordinateEmitter()
    
    def add_or_replace_mesh_by_name(self,obj):  
        """
        Receives a new mesh; checks whether it already exists and either replaces the previous version or just adds it.
        """
        if obj.name in [obj.name for obj in self.objects]:
            self.remove(obj.name)
        self.add(obj)
        self.render()

    def clear_everything_except(self,white_list):
        """
        removes everything from the Plotter except the Items in the list
        """
        for obj in [obj for obj in self.objects if obj.name not in white_list]:
            self.remove(obj.name)
            
    def pick_coordinate(self,evt):
        """
        Pick a coordinate on the user Mesh.
        """
        pt2d = evt.picked2d
        if len(pt2d) != 2:
            return
        obj_name_list=[obj.name for obj in self.objects]
        if "UserMesh" in obj_name_list:
            obj_idx=obj_name_list.index("UserMesh")
            pt3d=self.compute_world_coordinate(pt2d, objs=[self.objects[obj_idx]])
            if (pt3d != np.array([0,0,0])).all():
                self.ClickedCoordinateEmitter.pt3d.emit(pt3d)
