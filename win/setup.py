from distutils.core import setup
from src import version, description_short, author
import py2exe, sys
import matplotlib as mpl

sys.setrecursionlimit(5000)

sys.path.append(r".")
sys.path.append(r".\src")
sys.path.append(r".\res")
sys.path.append(r"..\python-neo")
sys.path.append(r"..\python-odml")

datafiles = list(mpl.get_py2exe_datafiles()) + [("data", [r"data\map_lilou.csv"])]

# copy the doc folder manually

setup(
        name="swan",
        version=version,
        description=description_short,
        author=author,

		data_files = datafiles,
		windows = [{"script":r"src\swan.py"}], 
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
