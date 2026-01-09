from PyQt6.QtWidgets import QFrame, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

class Axes(QFrame):
    '''
    Class for the XY Axes Diagram
    '''
    def __init__(self,parent):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.canvas = FigureCanvas(Figure())
        layout.addWidget(self.canvas)

        self._static_ax = self.canvas.figure.subplots()

    def set_title(self, title, xlabel="X", ylabel="Y"):
        self._static_ax.set_title(title)
        self._static_ax.set_xlabel(xlabel)
        self._static_ax.set_ylabel(ylabel)

    def plot(self,x_data,y_data,style="-"):
        self._static_ax.plot(x_data, y_data, style)
        self.canvas.draw()

    def fill_between(self,x_val,y_val,facecolor):
        self._static_ax.fill_between(x_val, y_val,facecolor=facecolor)
    
    def clear_axes(self):
        print("Clearing Plot")
        self._static_ax.cla()
        self.canvas.draw()