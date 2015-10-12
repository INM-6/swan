import sys
import os
from os.path import join, realpath, pardir, isfile, abspath
import py2exe
import matplotlib as mpl
from distutils.core import setup

#set the python path
p = abspath(join(realpath(__file__), pardir, pardir))
sys.path.insert(1, p)
sys.path.insert(1, join(p, "src"))
sys.path.insert(1, join(p, "res"))
sys.path.insert(1, join(p, "python-neo"))
sys.path.insert(1, join(p, "python-odml"))

from src import version, description_short, author

sys.setrecursionlimit(5000)

#get the html documentation files
dpath = join(p, "doc", "build", "html")

files = []
folders = {}

for name in os.listdir(dpath):
        if isfile(join(dpath, name)):
            files.append(join(dpath, name))
        else:
            folders[name] = []
            for f in os.listdir(join(dpath, name)):
                folders[name].append(join(dpath, name, f))


# set the data files
datafiles = list(mpl.get_py2exe_datafiles()) + [("data", [join(p, "data", "map_lilou.csv")]), 
                                                ("documentation", files)] + [(join("documentation", key), value) for key, value in folders.iteritems()]


setup(
        name="swan",
        version=version,
        description=description_short,
        author=author,

		data_files = datafiles,
		windows = [{"script":join(p, "src", "swan.py")}], 
		options = {"py2exe":{
		"includes":["sip", 
					"scipy.special._ufuncs_cxx",
					"scipy.sparse.csgraph._validation",
                    "matplotlib.backends.backend_tkagg",
                    "FileDialog"],			
        "excludes":["email",
                    "pdb",
                    "pyreadline",
                    "optparse",
                    "doctest",
                    "sqlite3",
                    "_ssl",
                    "simpy",
                    ],
        "compressed":True,
        "bundle_files":3,
        }},
)
