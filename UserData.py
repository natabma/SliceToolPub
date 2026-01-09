# Data Class for storing the Users Inputs

from vedo import Mesh

class UserData():
    # Original Mesh loaded by the User
    UserMesh:Mesh=None
    
    point_dict:dict={}

    #Slicing Input
    offset_p0:float
    offset_p1:float
    slicing_interval:float

    # Slicing Output
    slice_lines_list:list

    #Group Sections
    section_threshold_f:float