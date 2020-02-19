"""
This module contains resource files for the project.

=====
Icons
=====

So far, the only resources in this module are the icons. They are stored in the folder "icons", with the corresponding
python scripts stores in the parent folder. Any change in the icons or in the directory structure will require a
recompiling of the icons.qrc file. The step-by-step procedure to do this using PyQt5 is given here.

    1. Implement the required changes.
    2. Edit the icons.qrc file so that it reflects all required changes. The qresource prefix specifies the prefix to be
    prepended to the aliases when accessing the icon files from within the project. The alias does exactly what the term
    suggests - provides an alternative name to access the file with. The file location of the actual icon is specified
    between the <file></file> tags. The location of the icon is specified with respect to the icons.qrc file.

    For example:

        **dirctory structure**

            myproject
            |___ resources
                |___ foo
                    |___ bar_1.png
                    |___ bar_2.png
                |___ icons.qrc

        **icons.qrc**

            <RCC>
              <qresource prefix="icons">
                <file alias="alpha.png">foo/bar_1.png</file>
                <file alias="beta.png">foo/bar_2.png</file>
              </qresource>
            </RCC>

    3. In a terminal (or command prompt), navigate to the folder containing the final .qrc file and the execute the
    following command:

        pyrcc5 input.qrc -o output.py

    where input.qrc is the .qrc file and output.py is the compiled python file.

    4. Import the compiled python file anywhere within the project and load the icon file using the QPixmap function.

    For example (borrowing files from the earlier example):

        **dirctory structure**

            myproject
            |___ resources
                |___ foo
                    |___ bar_1.png
                    |___ bar_2.png
                |___ icons.py
                |___ icons.qrc
            |___ testfile.py

        **testfile.py**

            from PyQt5 import QtGui
            from os.path import sep
            from myproject.resources.foo import icons

            prefix = ":" + sep + "icons"
            icon_1 = QtGui.QIcon()
            icon_1.addPixmap(QtGui.QPixmap(prefix + "alpha.png"))
            icon_2 = QtGui.QIcon()
            icon_2.addPixmap(QtGui.QPixmap(prefix + "beta.png"))

"""