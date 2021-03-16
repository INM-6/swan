"""
@author: Shashwat Sridhar
"""
import numpy as np
import pyqtgraph as pg
import colorcet


class DarkPalette(pg.QtGui.QPalette):
    """Class that inherits from pyqtgraph.QtGui.QPalette and renders dark colours for the application."""

    def __init__(self):
        super(DarkPalette, self).__init__()
        self.setup()

    def setup(self):
        self.setColor(pg.QtGui.QPalette.Window, pg.QtGui.QColor(53, 50, 47))
        self.setColor(pg.QtGui.QPalette.WindowText, pg.QtGui.QColor(255, 255, 255))
        self.setColor(pg.QtGui.QPalette.Base, pg.QtGui.QColor(30, 27, 24))
        self.setColor(pg.QtGui.QPalette.AlternateBase, pg.QtGui.QColor(53, 50, 47))
        self.setColor(pg.QtGui.QPalette.ToolTipBase, pg.QtGui.QColor(255, 255, 255))
        self.setColor(pg.QtGui.QPalette.ToolTipText, pg.QtGui.QColor(255, 255, 255))
        self.setColor(pg.QtGui.QPalette.Text, pg.QtGui.QColor(255, 255, 255))
        self.setColor(pg.QtGui.QPalette.Button, pg.QtGui.QColor(53, 50, 47))
        self.setColor(pg.QtGui.QPalette.ButtonText, pg.QtGui.QColor(255, 255, 255))
        self.setColor(pg.QtGui.QPalette.BrightText, pg.QtGui.QColor(255, 0, 0))
        self.setColor(pg.QtGui.QPalette.Link, pg.QtGui.QColor(42, 130, 218))
        self.setColor(pg.QtGui.QPalette.Highlight, pg.QtGui.QColor(42, 130, 218))
        self.setColor(pg.QtGui.QPalette.HighlightedText, pg.QtGui.QColor(0, 0, 0))


UNIT_COLORS = (np.array(colorcet.glasbey_bw_minc_20_minl_30) * 255).astype(np.int32)
