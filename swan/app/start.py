import sys
import tempfile
import os
from swan.src.main import Main
import pyqtgraph as pg
from swan.gui.palettes import DarkPalette


def main():
    if len(sys.argv) > 1:
        home = sys.argv[1]
    else:
        # should only work on windows and unix
        home = tempfile.gettempdir()

    p = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app = pg.QtGui.QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setPalette(DarkPalette())
    app.setStyleSheet("QToolTip { color: #aeadac; background-color: #35322f; border: 1px solid #aeadac; }")
    pg.setConfigOption('background', 'k')
    pg.setConfigOption('foreground', 'w')
    pg.setConfigOption('useOpenGL', True)

    dark = True

    m = Main(os.path.abspath(p), home, dark)
    m.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()