from UserData import UserData
import vedo
import numpy as np
from vtk import vtkPlanes
import pandas as pd
import itertools


class MainModel:
    """
    Class for Providing Slice Tool's Functionalities
    """

    def __init__(self, data: UserData):
        super().__init__()
        self._data = data
        self.Cutter = None

    def loadMeshFromURL(self, mesh_url):
        """
        Loads the 3D object from the passed url.
        """
        # TODO Import Error Handling and better Import Success Validation

        self._data.UserMesh = vedo.load(mesh_url)
        self._data.UserMesh.name = "UserMesh"
        return self._data.UserMesh

    # Scaling

    @property
    def ScaledAxes(self):
        ScaledAxesUserMesh = vedo.Axes(
            obj=self._data.UserMesh,
            c=None,
            xygrid=False,
            xtitle="x [mm]",
            ytitle="y [mm]",
            ztitle="z [mm]",
            xtitle_color="red",
            ytitle_color="green",
            ztitle_color="blue",
        )
        ScaledAxesUserMesh.name = "ScaledAxes"
        return ScaledAxesUserMesh

    def scaleMesh(self, new_scaling_factor):
        current_scale_factors = self._data.UserMesh.scale()
        self._data.UserMesh.scale(new_scaling_factor / current_scale_factors)

    # Cutter

    def startCutter(self):
        if self.Cutter == None:
            self.Cutter = vedo.BoxCutter(self._data.UserMesh)
            return self.Cutter
        if not self.Cutter.widget.enabled:
            self.Cutter.on()
            return self.Cutter

    def resetCutter(self):
        if self.Cutter != None:
            self.Cutter.set_bounds(self.Cutter._init_bounds)
            self.Cutter.widget.PlaceWidget()
            self.Cutter.render()

    def invertCutter(self):
        if self.Cutter != None:
            self.Cutter.invert()
            self.Cutter.render()

    def stopCutter(self):
        if self.Cutter != None:
            if self.Cutter.widget.enabled:
                planes = vtkPlanes()
                self.Cutter.widget.GetPlanes(planes)
                origins = np.array(
                    [
                        planes.GetPoints().GetPoint(i)
                        for i in range(planes.GetPoints().GetNumberOfPoints())
                    ]
                )
                normals = np.array(
                    [
                        planes.GetPlane(i).GetNormal()
                        for i in range(planes.GetNumberOfPlanes())
                    ]
                )

                self.Cutter.off()
                # self.Cutter.remove_from(self.vplt)
                self._data.UserMesh.cut_closed_surface(origins, normals)
                self._data.UserMesh.cap()
                self._data.UserMesh.name = "UserMesh"
            return self.Cutter
    
    def clearEverythingPostCutting(self):
        """
        Clears all Cutting Results if the User re-cuts the mesh after slicing.
        """
        self._data.point_dict={}
        self._data.slice_lines_list=[]
        

    # Placing Points

    def create_named_point(self, pt3d, name):
        point = vedo.Point(pt3d)
        point.name = name
        self._data.point_dict[name] = pt3d
        return point

    @property
    def p0(self):
        return self._data.point_dict["SlicingAxisP1"]

    @property
    def p1(self):
        return self._data.point_dict["SlicingAxisP2"]

    @property
    def p0_with_offset(self):
        return self.p0 + self.slicing_vector_normalized * self._data.offset_p0

    @property
    def p1_with_offset(self):
        return self.p1 - self.slicing_vector_normalized * self._data.offset_p1

    @property
    def slicing_axis_can_be_drawn(self):
        existing_point_names = self._data.point_dict.keys()
        return (
            "SlicingAxisP2" in existing_point_names
            and "SlicingAxisP1" in existing_point_names
        )

    @property
    def SlicingArrow(self):
        p0 = self.p0
        p1 = self.p1

        slicing_normal = p1 - p0
        line_coordinate_0 = p0 - slicing_normal * 0.3
        line_coordinate_1 = p1 + slicing_normal * 0.3
        SlicingNormalArrow = vedo.Arrow(
            start_pt=line_coordinate_0,
            end_pt=line_coordinate_1,
            s=0.3,
            head_length=0.05,
        )
        SlicingNormalArrow.name = "SlicingNormalArrow"
        return SlicingNormalArrow

    @property
    def SlicingNormal(self):
        p0 = self.p0
        p1 = self.p1
        return vedo.Line(p0=p0, p1=p1)

    @property
    def slicing_vector_normalized(self):
        p0 = self.p0
        p1 = self.p1
        slicing_vector_normalized = (p1 - p0) / np.linalg.norm(p1 - p0)
        return slicing_vector_normalized

    def setSlicingInputs(self, offset_p0, offset_p1, slicing_interval):
        self._data.offset_p0 = offset_p0
        self._data.offset_p1 = offset_p1
        self._data.slicing_interval = slicing_interval

    @property
    def InterpolatedSlicingNormal(self):
        SlicingNormalLineWithOffset = vedo.Line(
            self.p0_with_offset, self.p1_with_offset
        )
        return self._interpolate_line_by_distance(
            SlicingNormalLineWithOffset, self._data.slicing_interval
        )

    @property
    def slice_heights_arr(self):
        return np.array(
            [
                np.linalg.norm(vertex - self.InterpolatedSlicingNormal.vertices[0])
                for vertex in self.InterpolatedSlicingNormal.vertices
            ]
        )

    @property
    def slice_lengths_arr(self):
        return np.array([line.length() for line in self._data.slice_lines_list])

    def sliceUserMesh(self):

        InterpolatedSlicingNormalTangents = self.InterpolatedSlicingNormal.tangents()
        slice_lines = []

        for point, vec in zip(
            self.InterpolatedSlicingNormal.vertices, InterpolatedSlicingNormalTangents
        ):  
            try:
                line = self._data.UserMesh.intersect_with_plane(origin=point, normal=vec)
                line = line.join()
                line = line.vertices[line.lines[0]]
                line = vedo.Line(line)
                slice_lines.append(line)
            except Exception as e:
                return e

        self._data.slice_lines_list = slice_lines

        slice_lengths_arr = self.slice_lengths_arr

        min_intersection_length = min(slice_lengths_arr)
        max_intersection_length = max(slice_lengths_arr)

        for line in slice_lines:
            line.linecolor(
                vedo.color_map(
                    line.length(),
                    "winter",
                    min_intersection_length,
                    max_intersection_length,
                )
            )

        SliceLinesAssembly = vedo.Assembly(*slice_lines)
        SliceLinesAssembly.name = "SlicesAssembly"

        return SliceLinesAssembly

    def _interpolate_line_by_distance(self, line, distance):
        """Interpolate vertices of an even distance along a line."""
        x = line.vertices[:, 0]
        y = line.vertices[:, 1]
        z = line.vertices[:, 2]

        # compute the distances, ds, between points
        dx, dy, dz = x[+1:] - x[:-1], y[+1:] - y[:-1], z[+1:] - z[:-1]
        ds = np.array((0, *np.sqrt(dx**2 + dy**2 + dz**2)))

        # compute the total distance from the 1st point, measured on the curve
        s = np.cumsum(ds)

        xinter = np.interp(np.arange(0, s[-1], distance), s, x)
        yinter = np.interp(np.arange(0, s[-1], distance), s, y)
        zinter = np.interp(np.arange(0, s[-1], distance), s, z)

        point_list_resampled = list(zip(xinter, yinter, zinter))
        InterpolatedLine = vedo.Line(point_list_resampled, closed=True)

        return InterpolatedLine
    
    def _interpolate_line_by_points(self, line, number_of_points):
        """Interpolate vertices of a specified number of vertices along a line."""
        x = line.vertices[:, 0]
        y = line.vertices[:, 1]
        z = line.vertices[:, 2]

        # compute the distances, ds, between points
        dx, dy, dz = x[+1:] - x[:-1], y[+1:] - y[:-1], z[+1:] - z[:-1]
        ds = np.array((0, *np.sqrt(dx**2 + dy**2 + dz**2)))

        # compute the total distance from the 1st point, measured on the curve
        s = np.cumsum(ds)

        xinter = np.interp(np.linspace(0,s[-1], number_of_points), s, x)
        yinter = np.interp(np.linspace(0,s[-1], number_of_points), s, y)
        zinter = np.interp(np.linspace(0,s[-1], number_of_points), s, z)
        
        point_list_resampled = list(zip(xinter, yinter, zinter))
        InterpolatedLine = vedo.Line(point_list_resampled[0:-1], closed=True)

        return InterpolatedLine


    def toggleUserMeshAlpha(self):
        """
        Toggle the alpha of the mesh.
        """
        if self._data.UserMesh.alpha() == 1:
            self._data.UserMesh.alpha(0.5)
        else:
            self._data.UserMesh.alpha(1)

    def setSectionThreshold(self, section_threshold_f):
        self._data.section_threshold_f = section_threshold_f

    @property
    def marked_section_indices(self):
        marked_indices = []
        last_index = 0

        threshold = self._data.section_threshold_f
        slice_lengths_arr = self.slice_lengths_arr

        for idx, y_val in enumerate(slice_lengths_arr):

            last_y = slice_lengths_arr[last_index]
            percentage = y_val / last_y

            if abs(percentage - 1) > (threshold / 100):
                marked_indices.append(idx)
                last_index = idx

        if marked_indices[0] != 0:
            marked_indices.insert(0, 0)

        if marked_indices[-1] != len(slice_lengths_arr) - 1:
            marked_indices.append(len(slice_lengths_arr) - 1)

        return marked_indices

    def _pairwise(self, a):
        return list(zip(a, a[1:]))

    @property
    def pairwise_marked_section_indices(self):
        return self._pairwise(self.marked_section_indices)

    @property
    def mean_section_circumferences(self):
        # print(self.pairwise_marked_section_indices)
        return [
            np.mean(self.slice_lengths_arr[from_idx:to_idx])
            for from_idx, to_idx in self.pairwise_marked_section_indices
            if len(self.slice_lengths_arr[from_idx:to_idx])
        ]
    
    @property
    def min_section_circumferences(self):
        # print(self.pairwise_marked_section_indices)
        return [
            np.min(self.slice_lengths_arr[from_idx:to_idx])
            for from_idx, to_idx in self.pairwise_marked_section_indices
            if len(self.slice_lengths_arr[from_idx:to_idx])
        ]
    

    @property
    def section_facecolors(self):
        return [
            vedo.color_map(
                mean_section_circumference,
                name="coolwarm",
                vmin=min(self.slice_lengths_arr),
                vmax=max(self.slice_lengths_arr),
            )
            for mean_section_circumference in self.mean_section_circumferences
        ]

    def makeColoredAssembly(self):
        User_Mesh_Sections = self._data.UserMesh.copy()

        p0 = self.p0_with_offset
        p1 = self.p1_with_offset
        slicing_vector_normalized = self.slicing_vector_normalized
        slice_heights = self.slice_heights_arr
        facecolors = self.section_facecolors
        SectionAssembly = vedo.Assembly()
        SectionAssembly.name = "Section Assembly"

        for idx, pair_idxs in enumerate(self.pairwise_marked_section_indices):
            from_idx, to_idx = pair_idxs

            slicing_from = p0 + slicing_vector_normalized * slice_heights[from_idx]
            slicing_to = p0 + slicing_vector_normalized * slice_heights[to_idx]

            section = User_Mesh_Sections.copy().cut_with_planes(
                origins=[slicing_from, slicing_to],
                normals=[-slicing_vector_normalized, slicing_vector_normalized],
                invert=True,
            )
            section.alpha(1)
            section.c(facecolors[idx])
            SectionAssembly.add(section)

        slicing_from = p0 + slicing_vector_normalized * slice_heights[0]
        slicing_to = p0 + slicing_vector_normalized * slice_heights[-1]

        section = User_Mesh_Sections.copy().cut_with_planes(
            origins=[slicing_from, slicing_to],
            normals=[-slicing_vector_normalized, slicing_vector_normalized],
            invert=False,
        )
        section.alpha(0.7)
        section.c("black")
        SectionAssembly.add(section)

        return SectionAssembly

    def makeOrientedCameraForUserMesh(self):

        p0 = self.p0
        p1 = self.p1
        slice_heights = self.slice_heights_arr

        slicing_vector_normalized = (p1 - p0) / np.linalg.norm(p1 - p0)

        k = -slicing_vector_normalized
        center = p0 + (p1 - p0) / 2

        x = center + [1, 0, 0]
        x -= x.dot(k) * k  # make it orthogonal to k
        x /= np.linalg.norm(x)  # normalize it
        y = np.cross(k, x)

        up_vector = x
        backoff_vector = y
        backoff = slice_heights[-1] * 2

        OrientedCamera = vedo.oriented_camera(
            center, up_vector, backoff_vector, backoff
        )
        return OrientedCamera


    def _prepareDataForExport(self):
        threshold = self._data.section_threshold_f
        marked_indices = self.marked_section_indices
        slice_heights = self.slice_heights_arr
        slice_lengths = self.slice_lengths_arr

        idx_list = list(
            itertools.chain(
                *[
                    [idx] * (section_touple[1] - section_touple[0])
                    for idx, section_touple in enumerate(self._pairwise(marked_indices))
                ]
            )
        )
        idx_list.insert(0, 0)

        slices_df = pd.DataFrame()
        slices_df["Slice Heights"] = slice_heights
        slices_df["Curve Lengths"] = slice_lengths
        slices_df[f"Sections ({str(round(threshold,2))} Percent)"] = idx_list

        sections_df = [
            [idx, slice_heights[idx], slice_lengths[idx]] for idx in marked_indices
        ]
        sections_df = pd.DataFrame(
            sections_df, columns=["Slice Index", "Height", "Circumference"]
        )
        return slices_df,sections_df

    def saveSliceDataToExcel(self, excel_file_url):
        
        slices_df,sections_df = self._prepareDataForExport()
        
        try:
            with pd.ExcelWriter(excel_file_url) as writer:
                slices_df.to_excel(writer, sheet_name="Slices", index=False)
                sections_df.to_excel(writer, sheet_name="Sections", index=False)

        except Exception as e:
            print(e)

    def saveSliceDataToCSV(self, csv_file_url:str):

        slices_df,sections_df = self._prepareDataForExport()
        csv_file_url_sections = csv_file_url.replace(".csv","") + "_sections.csv"

        try:
            slices_df.to_csv(csv_file_url,index=False)
            sections_df.to_csv(csv_file_url_sections, index=False)

        except Exception as e:
            print(e)