from PyQt5 import QtWidgets
from probeinterface import get_probe
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
from swan.gui.selector_widget_ui import Ui_Form

class ProbeSelectorWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(ProbeSelectorWidget, self).__init__(*args, **kwargs)
        self.ui = Ui_Form()
        self.ui.setupUi(self)


        manufacturer = 'neuronexus'
        probe_name = 'A1x32-Poly3-10mm-50-177'
        probe = get_probe(manufacturer, probe_name)

        self.graphWidget = pg.PlotWidget()

        # plot data: x, y values
        self.graphWidget.plot(probe.contact_positions, pen=None, symbol='o', symbolSize=10)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = ProbeSelectorWidget()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()