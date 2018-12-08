====
SWAN
====

Sequential Waveform Analyzer
-----------------------------

**SWAN** (Sequential Waveform Analyzer) is an open-source graphical tool being developed for tracking single units across several sessions of electrophysiological data collected using chronically implanted electrodes and/or arrays. The tool is written entirely in Python3 and `PyQt5 <http://pyqt.sourceforge.net/Docs/PyQt5/>`_, and makes use of efficient libraries for plotting (`pyqtgraph <http://www.pyqtgraph.org/>`_), number crunching (`numpy <http://www.numpy.org/>`_), data I/O (`pickle <https://docs.python.org/3/library/pickle.html>`_) and storage (`neo <https://neo.readthedocs.io/en/latest/>`_). The Graphical User Interface (GUI) is designed to be flexible and modular, making use of pyqtgraph's `enhanced QWidget classes <http://www.pyqtgraph.org/documentation/introduction.html#what-can-it-do>`_.

While it is currently used to analyze `reach-to-grasp data <https://web.gin.g-node.org/INT/multielectrode_grasp>`_ at the `Institute of Neuroscience and Medicine - 6 (INM-6), Forschungszentrum Jülich <http://www.fz-juelich.de/inm/inm-6/EN/Home/home_node_INM6.html>`_, it is, in principle, capable of loading and analyzing any such data that is provided in the appropriate neo-compatible format (details to follow soon).

Features:

- Completely written in Python3 and PyQt5.
- Shows an overview of spike sorted data from one channel over multiple recording sessions.
- Interactively displays various characteristics of single units in different graphical widgets, called views.
- Provides a flexible and modular graphical user interface, ideal for multiple desktop systems.
- Utilizes efficient plotting libraries to smoothly visualize large datasets.
- Creates a virtual mapping of units across sessions which can be exported to csv and odml formats.
- Calculates this virtual unit mapping automatically by both, home-grown and published algorithms.