from PyQt6 import Qwt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class Plot( Qwt.QwtPlot):
    def __init__(self, parent=None):
        Qwt.QwtPlot.__init__(self, parent)
        self.setAutoReplot( False )
        self.setTitle( "TEAS Timescan" )
        canvas = Qwt.QwtPlotCanvas()
        canvas.setBorderRadius( 10 )
        self.setCanvas( canvas )
        self.setCanvasBackground( QColor( "MidnightBlue" ) )
        # legend
        legend = Qwt.QwtLegend()
        self.insertLegend( legend, Qwt.QwtPlot.LegendPosition.BottomLegend )

        # grid
        self.grid = Qwt.QwtPlotGrid()
        self.grid.enableXMin( True )
        self.grid.setMajorPen( Qt.GlobalColor.white, 0, Qt.PenStyle.DotLine )
        self.grid.setMinorPen( Qt.GlobalColor.gray, 0 , Qt.PenStyle.DotLine )
        self.grid.attach( self )

        # axes
        self.setAxisTitle( Qwt.QwtPlot.Axis.xBottom, "Time [sec]" )
        self.setAxisTitle( Qwt.QwtPlot.Axis.yLeft, "Intensity [arb. un.]" )

        self.setAxisMaxMajor( Qwt.QwtPlot.Axis.xBottom, 6 )
        self.setAxisMaxMinor( Qwt.QwtPlot.Axis.xBottom, 9 )

        # curves
        self.d_curve1 = Qwt.QwtPlotCurve( "Intensity" )
        self.d_curve1.setRenderHint( Qwt.QwtPlotItem.RenderHint.RenderAntialiased )
        self.d_curve1.setPen( Qt.GlobalColor.yellow )
        self.d_curve1.setLegendAttribute( Qwt.QwtPlotCurve.LegendAttribute.LegendShowLine )
        self.d_curve1.setYAxis( 0 ) #Qwt.QwtPlot.Axis.yLeft )
        self.d_curve1.attach( self )

        # marker
        self.d_marker1 = Qwt.QwtPlotMarker()
        self.d_marker1.setValue( 0.0, 0.0 )
        self.d_marker1.setLineStyle( Qwt.QwtPlotMarker.LineStyle.VLine )
        self.d_marker1.setLabelAlignment( Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
        self.d_marker1.setLinePen( Qt.GlobalColor.green, 0, Qt.PenStyle.DashDotLine )
        self.d_marker1.attach( self )

        self.setAutoReplot( True )

    def showData(self, x, y):
        self.d_curve1.setSamples(x, y)
        # Cambiar el eje x para que sea logaritmico y empezar en 0
        # self.d_curve2.setSamples( time, phase)
