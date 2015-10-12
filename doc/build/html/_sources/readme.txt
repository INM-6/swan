Getting started
===============

Here you can find out how to get started with swan.

|


Requirements
------------
    
Here is a list of packages needed by swan:

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

If you are using Ubuntu - or any other Debian based machine - you can install
some of the packages via apt.

The command looks like this::

    $ sudo apt-get install <package_name>
    
For the other packages (and other operating systems) you have to use pip.

Here is the command for pip::

    $ pip install --user <package_name>
    
Look at the table to get the right package name:

    ==================  ==================  ================== 
    package             pip package         apt package
    ==================  ==================  ==================
    matplotlib          matplotlib          python-matplotlib
    quantities          quantities          python-quantities
    PyQt4                                   python-qt4
    enum                enum                python-enum
    lxml                lxml                python-lxml
    pyqtgraph           pyqtgraph
    ==================  ==================  ==================
    
In the top-level directory of swan you can find the file ``install.sh`` in which the commands for installing the packages can be found.
You can use this file for installing the packages (this will only work on machines which support ``apt-get install``)::

	$ ./install.sh

Getting Swan
^^^^^^^^^^^^

To get the swan repository use the following command in your console::

    $ git clone --recursive https://github.com/INM-6/swan.git

The ``--recursive`` is very **important** because swan depends on other repositories.

Running swan
------------

If you are in the ``swan/src`` directory, the command to start swan looks like this::

    $ python run.py [<home_dir>]

You can see that *<home_dir>* is optional.
If you are fine with the fact that swan saves all project files
in your home directory - which is usually ``~`` - you don't have to provide arguments.

But if you want to choose another directory you can just provide it as first argument.
