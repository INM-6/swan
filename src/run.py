"""
Created on Mar 31, 2014

@author: Christoph Gollan

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
    from os.path import curdir, split, abspath, expanduser, join, realpath, pardir
    
    if len(sys.argv) > 1:
        home = sys.argv[1]
    else:
        #should only work on windows and unix
        home = expanduser("~")
    
#     p = sys.path[0]
#     p = split(p)[0]
#     if not p:
#         p = curdir
    p = abspath(join(realpath(__file__), pardir, pardir))
    sys.path.insert(1, p)
    sys.path.insert(1, join(p, "src"))
    sys.path.insert(1, join(p, "res"))
    sys.path.insert(1, join(p, "python-neo"))
    sys.path.insert(1, join(p, "python-odml"))
    
    from src.main import Main
    import pyqtgraph as pg
    
    app = pg.QtGui.QApplication(sys.argv)
    app.setStyle("Fusion")
    
    if "--light-theme" not in sys.argv:
        dark_palette = pg.QtGui.QPalette()
        
        dark_palette.setColor(pg.QtGui.QPalette.Window, pg.QtGui.QColor(53, 50, 47))
        dark_palette.setColor(pg.QtGui.QPalette.WindowText, pg.QtGui.QColor(255, 255, 255))
        dark_palette.setColor(pg.QtGui.QPalette.Base, pg.QtGui.QColor(30, 27, 24))
        dark_palette.setColor(pg.QtGui.QPalette.AlternateBase, pg.QtGui.QColor(53, 50, 47))
        dark_palette.setColor(pg.QtGui.QPalette.ToolTipBase, pg.QtGui.QColor(255, 255, 255))
        dark_palette.setColor(pg.QtGui.QPalette.ToolTipText, pg.QtGui.QColor(255, 255, 255))
        dark_palette.setColor(pg.QtGui.QPalette.Text, pg.QtGui.QColor(255, 255, 255))
        dark_palette.setColor(pg.QtGui.QPalette.Button, pg.QtGui.QColor(53, 50, 47))
        dark_palette.setColor(pg.QtGui.QPalette.ButtonText, pg.QtGui.QColor(255, 255, 255))
        dark_palette.setColor(pg.QtGui.QPalette.BrightText, pg.QtGui.QColor(255, 0, 0))
        dark_palette.setColor(pg.QtGui.QPalette.Link, pg.QtGui.QColor(42, 130, 218))
        dark_palette.setColor(pg.QtGui.QPalette.Highlight, pg.QtGui.QColor(42, 130, 218))
        dark_palette.setColor(pg.QtGui.QPalette.HighlightedText, pg.QtGui.QColor(0, 0, 0))
        
        app.setPalette(dark_palette)
        
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
        
    m = Main(abspath(p), home, dark)
    m.show()
    sys.exit(app.exec_())