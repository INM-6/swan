"""
Created on Apr 1, 2014

@author: Christoph Gollan

This module contains a simple :class:`MBox` for showing messages.

This class is built with tkinter.
"""

import sys
    
if sys.version_info < (3,0):
    import Tkinter as tkinter
    import tkMessageBox as mbox
else:
    import tkinter
    import tkinter.messagebox as mbox


class MBox(object):
    """
    Message box class for showing message boxes.
    
    """
    
    @staticmethod
    def info(title, message):
        """
        Shows an information box.
        
        **Arguments**
        
            *title* (string):
                The title of the message box.
            *message* (string):
                The message to show.
        
        """
        window = tkinter.Tk()
        window.wm_withdraw()
        mbox.showinfo(title=title, message=message)
        window.destroy()