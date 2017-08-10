"""
In this package are most of the modules this application uses.

Many of the modules are specific for this application.
The most important one is :mod:`src.main` which contains the
main window class. 
But :mod:`src.mystorage` is also important because it contains
classes to manage the loading and writing of data, creating
project files, deleting them, and many other important tasks.

"""

title = "Swan - Sequential Waveform Analyzer"

description_short = "Python based tool to analyse reach-and-grasp data."

version = "1.0.0"

author = "Swan authors and contributors"

copyr = "2013-2017"

about = """
        {}
        
        {}

        Features:

        * Show an overview of one electrode over many sessions.
        * Show different views and layers of the data.
        * Do a virtual unit mapping.
        * Save the mapping in a file.
        * Calculate the mapping via algorithm or do it by hand
        * Export the mapping to csv and odML
        
        Version: {}
        
        Copyright (c) {}, {}
        """.format(title, description_short, version, copyr, author)