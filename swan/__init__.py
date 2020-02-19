"""
This module contains all the modules and subpackages required to run SWAN.

The contents are organized in five folders:

    * src: contains all the important scripts, including src.main
    * gui: contains code that renders the graphical aspects of the tool
    * base: contains important classes for data base and access
    * resources: contains miscellaneous resources to complete the tool's functionality
    * tools: contains additional tools that add functionality to SWAN

"""

from .version import version as swan_version

title = "SWAN - Sequential Waveform Analyzer"

description_short = 'Python based tool for tracking single units in spike sorted data across several ' \
                    'electrophysiological recording sessions. '

version = swan_version

author = "SWAN authors and contributors"

copy_right = "2013-2018"

about = """
        {0}
        
        {1}

        Features
        ========

        * Completely written in Python 3 and PyQt5.
        * Shows an overview of spike sorted data from one channel over multiple recording sessions.
        * Interactively displays various characteristics of single units in different graphical widgets, called views.
        * Provides a flexible and modular graphical user interface, ideal for multiple desktop systems.
        * Utilizes efficient plotting libraries to smoothly visualize large datasets.
        * Creates a virtual mapping of units across sessions which can be exported to csv and odml formats.
        * Calculates this virtual unit mapping automatically by home-grown and published algorithms.
        
        Version: {2}
        
        Copyright (c) {3}, {4}
        """.format(title, description_short, version, copy_right, author)