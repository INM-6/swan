.. swan documentation master file, created by
   sphinx-quickstart on Tue Sep 16 09:08:16 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to swan's documentation!
================================

Swan (="sequential waveform analyzer") is a GUI application built with PyQt4.
For plotting it also uses matplotlib's qt aggregation classes and pyqtgraph's plot widget.
The calculation is done by numpy.

Swan is built to show reach-and-grasp data. It is possible to load multiple sessions to get an overview of all
units from all sessions for one selectable electrode. In advance you can compare the units by either looking at
the overview or by using the different views of the data, e.g. a 2d plot.
A special feature of swan is that you can create virtual units. Virtual units are a mapping of units from multiple
sessions that you define as the same unit.


Here is a list of the swan features:

* Show an overview of one electrode over many sessions.
* Show different views and layers of the data.
* Do a virtual unit mapping.
  Sometimes units are not mapped correctly so you can change
  the mapping virtually and save the mapping in a file.
* Calculate the mapping via algorithm or do it by hand
* Export the mapping to csv and odML

.. warning::

    This application is built on Linux and works on Linux. It *should* work on
    Windows as well but there could be some problems.

Contents:

.. toctree::
   :maxdepth: 1

   readme
   tutorial
   contents
   
|


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

