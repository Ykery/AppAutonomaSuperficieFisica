from PyQt6 import Qwt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class Plot(Qwt.QwtPlot):
    def __init__(
        self,
        title,
        asis_x_title,
        axis_y_title,
        parent=None,
        color=QColor("MidnightBlue"),
    ):
        Qwt.QwtPlot.__init__(self, parent)
        self.setAutoReplot(False)
        self.setTitle(title)
        canvas = Qwt.QwtPlotCanvas()
        canvas.setBorderRadius(10)
        self.setCanvas(canvas)
        self.setCanvasBackground(color)

        # grid
        self.grid = Qwt.QwtPlotGrid()
        self.grid.enableXMin(True)
        self.grid.setMajorPen(Qt.GlobalColor.white, 0, Qt.PenStyle.DotLine)
        self.grid.setMinorPen(Qt.GlobalColor.gray, 0, Qt.PenStyle.DotLine)
        self.grid.attach(self)

        # axes
        self.setAxisTitle(Qwt.QwtPlot.Axis.xBottom, asis_x_title)
        self.setAxisTitle(Qwt.QwtPlot.Axis.yLeft, axis_y_title)

        # curves
        self.datos_grafica = Qwt.QwtPlotCurve("Intensity")
        self.datos_grafica.setRenderHint(Qwt.QwtPlotItem.RenderHint.RenderAntialiased)
        self.datos_grafica.setPen(Qt.GlobalColor.yellow)
        self.datos_grafica.setLegendAttribute(
            Qwt.QwtPlotCurve.LegendAttribute.LegendShowLine
        )
        self.datos_grafica.setYAxis(0)  # Qwt.QwtPlot.Axis.yLeft )
        self.datos_grafica.attach(self)

        # marker
        self.marcador_inicio = Qwt.QwtPlotMarker()
        self.marcador_inicio.setValue(0.0, 0.0)
        self.marcador_inicio.setLineStyle(Qwt.QwtPlotMarker.LineStyle.VLine)
        self.marcador_inicio.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )
        self.marcador_inicio.setLinePen(
            Qt.GlobalColor.green, 0, Qt.PenStyle.DashDotLine
        )
        self.marcador_inicio.attach(self)

        self.setAutoReplot(True)

    def showData(self, x, y):
        self.datos_grafica.setSamples(x, y)


class Zoomer(Qwt.QwtPlotZoomer):
    def __init__(self, xAxis, yAxis, canvas):
        Qwt.QwtPlotZoomer.__init__(self, xAxis, yAxis, canvas)
        self.setTrackerMode(Qwt.QwtPicker.DisplayMode.AlwaysOff)
        self.setRubberBand(Qwt.QwtPicker.RubberBand.NoRubberBand)
        # Disable zoom out
        self.setMousePattern(
            Qwt.QwtEventPattern.MousePatternCode.MouseSelect2, Qt.MouseButton.NoButton
        )
        self.setRubberBand(Qwt.QwtPicker.RubberBand.RectRubberBand)
        self.setRubberBandPen(QColor(Qt.GlobalColor.green))
        self.setTrackerMode(Qwt.QwtPicker.DisplayMode.ActiveOnly)
        self.setTrackerPen(QColor(Qt.GlobalColor.white))
        self.setZoomBase(True)
