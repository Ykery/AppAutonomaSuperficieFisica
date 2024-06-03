from PyQt6 import Qwt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class Plot(Qwt.QwtPlot):
    """
    Clase para proporcionar una gráfica personalizada.
    """

    def __init__(
        self,
        title,
        axis_x_title,
        axis_y_title,
        parent=None,
        color=QColor("MidnightBlue"),
    ):
        """
        Inicializa una instancia de la clase Plot.

        Esta clase extiende Qwt.QwtPlot para proporcionar una gráfica personalizada.

        :param title: Título de la gráfica.
        :type title: str
        :param axis_x_title: Título del eje X.
        :type axis_x_title: str
        :param axis_y_title: Título del eje Y.
        :type axis_y_title: str
        :param parent: Widget padre de la gráfica. Por defecto, None.
        :type parent: QWidget, optional
        :param color: Color de fondo de la gráfica. Por defecto, "MidnightBlue".
        :type color: QColor, optional
        """
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
        self.setAxisTitle(Qwt.QwtPlot.Axis.xBottom, axis_x_title)
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
        """
        Muestra los datos en la gráfica.

        :param x: Datos del eje X.
        :type x: list
        :param y: Datos del eje Y.
        :type y: list
        """
        self.datos_grafica.setSamples(x, y)


class Zoomer(Qwt.QwtPlotZoomer):
    """
    Clase para proporcionar funcionalidad de zoom a una gráfica.
    """

    def __init__(self, xAxis, yAxis, canvas):
        """
        Inicializa una instancia de la clase Zoomer.

        Esta clase extiende Qwt.QwtPlotZoomer para proporcionar funcionalidad de zoom a una gráfica.

        :param xAxis: Eje X de la gráfica.
        :type xAxis: Qwt.QwtPlot.Axis
        :param yAxis: Eje Y de la gráfica.
        :type yAxis: Qwt.QwtPlot.Axis
        :param canvas: Lienzo de la gráfica.
        :type canvas: Qwt.QwtPlotCanvas
        """
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
