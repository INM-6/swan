"""
Created on May 6, 2014

@author: Christoph Gollan

Can run the application just like :mod:`src.run` but it doesn't do 
additions and checks for the *sys.path*.

Don't use this to run the application.
This is only used by *py2exe*.
"""

if __name__ == '__main__':
    import sys
    from os.path import curdir, split, abspath, expanduser
    
    if len(sys.argv) > 1:
        home = sys.argv[1]
    else:
        #should only work on windows and unix
        home = expanduser("~")
    
    p = sys.path[0]
    p = split(p)[0]
    if not p:
        p = curdir

    from src.main import Main
    from PyQt4.QtGui import QApplication
    
    app = QApplication(sys.argv)
    m = Main(abspath(p), home)
    m.show()
    sys.exit(app.exec_())