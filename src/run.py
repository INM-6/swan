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
    from PyQt5.QtGui import QApplication
    
    app = QApplication(sys.argv)
    m = Main(abspath(p), home)
    m.show()
    sys.exit(app.exec_())