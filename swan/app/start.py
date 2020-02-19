# system imports
import sys
import tempfile
import os
import pyqtgraph as pg

# swan-specific imports
from swan.main import Main
from swan.gui.palettes import DarkPalette


def launch():
    if len(sys.argv) > 1:
        home = sys.argv[1]
    else:
        home = tempfile.gettempdir()

    p = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app = pg.QtGui.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    app.setStyleSheet("QToolTip { color: #aeadac;"
                      "background-color: #35322f;"
                      "border: 1px solid #aeadac; }")

    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')
    pg.setConfigOption('useOpenGL', True)

    m = Main(p, home)
    m.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch()
