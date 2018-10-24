"""
Created on Mar 31, 2014

@authors: Christoph Gollan and Shashwat Sridhar

Use this to run the program.
It adds some paths to *sys.path* and checks if there is something missing.

On default the home directory is *~*. Your project files will be
stored here.
If you want to choose another directory, you can just give it 
as first argument.

The command should look like this::

$ python run.py [<home_dir>]
"""

if __name__ == '__main__':
    import sys
    import tempfile
    import os
    from main import Main
    import pyqtgraph as pg
    from gui.palettes import DarkPalette

    if len(sys.argv) > 1:
        home = sys.argv[1]
    else:
        # should only work on windows and unix
        home = tempfile.gettempdir()

    p = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app = pg.QtGui.QApplication(sys.argv)
    app.setStyle("Fusion")

    if "--light-theme" not in sys.argv:

        app.setPalette(DarkPalette())
        app.setStyleSheet("QToolTip { color: #aeadac; background-color: #35322f; border: 1px solid #aeadac; }")
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'w')
        pg.setConfigOption('useOpenGL', True)

        dark = True

    else:
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('useOpenGL', True)

        dark = False

    m = Main(os.path.abspath(p), home, dark)
    m.show()
    sys.exit(app.exec_())
