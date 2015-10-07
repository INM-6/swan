Getting started
===============

Here you can find out how to get started with swan.

|


Requirements
------------
    
Here is a list of packages needed by swan:

    * tkinter (should be part of python)
    * matplotlib
    * quantities
    * PyQt4
    * enum
    * pyqtgraph
    * lxml
    * python-neo
    * python-odml

The python version that is used is *2.7.6*.


Installing swan
---------------

Getting the packages
^^^^^^^^^^^^^^^^^^^^

If you are using Ubuntu - or any other Debian based machine - you can try to install
the packages via apt.

The command looks like this::

    $ sudo apt-get install <package_name>
    
For the other packages (and other operating systems) you have to use pip.

Here is the command for pip::

    $ pip install --user <package_name>
    
Look at the table to get the right package name:

    ==================  ==================  ================== 
    package             pip package         apt package
    ==================  ==================  ==================
    tkinter                                 python-tk
    matplotlib          matplotlib          python-matplotlib
    quantities          quantities          python-quantities
    PyQt4                                   python-qt4
    enum                enum                python-enum
    lxml                                    python-lxml
    pyqtgraph           pyqtgraph
    ==================  ==================  ==================

Getting Neo and odML
^^^^^^^^^^^^^^^^^^^^
    
The python-neo and python-odml repositories have to be git cloned::

    $ git clone https://github.com/INM-6/python-neo.git
    $ git clone https://github.com/G-Node/python-odml.git

Getting Swan
^^^^^^^^^^^^

To get the swan repository use the following command in your console::

    $ git clone https://github.com/INM-6/swan.git

Running swan
------------

Setting up the PYTHONPATH
^^^^^^^^^^^^^^^^^^^^^^^^^

To get swan runnable you have to adjust the PYTHONPATH with additional directories.

These entries should all be **absolute** paths.

This table shows which entries are added by the application itself
and which entries the user has to add:

    ==================  ===============
    Path entry          To be added by
    ==================  ===============
    swan                application
    swan/src            application
    swan/res            application
    python-neo          user
    python-odml         user
    ==================  ===============

Running
^^^^^^^

If you are in the ``swan/src`` directory, the command to start swan looks like this::

    $ python run.py [<home_dir>]

You can see that *<home_dir>* is optional.
If you are fine with the fact that swan saves all project files
in your home directory - which is usually ``~`` - you don't have to provide arguments.

But if you want to choose another directory you can just provide it as first argument.
