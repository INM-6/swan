#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 11:34:16 2018

@author: sridhar
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

class myGLWidget(gl.GLViewWidget):
    
    unitClicked = QtCore.pyqtSignal(object)
    
    """ Override GLViewWidget with enhanced behavior

    """
    def __init__(self, app=None):

        super(myGLWidget,self).__init__()
        self.clickable = False
        self._downpos = []
        self.means = []
    
    def setMeans(self, means):
        self.means = means
        
    def setClickable(self, choice):
        self.clickable = choice

    def mousePressEvent(self, ev):
        """ Store the position of the mouse press for later use.

        """
        super(myGLWidget, self).mousePressEvent(ev)
        self._downpos = self.mousePos

    def mouseReleaseEvent(self, ev):
        """ Allow for single click to move and right click for context menu.

        Also emits a sigUpdate to refresh listeners.
        """
        super(myGLWidget, self).mouseReleaseEvent(ev)
        if self._downpos == ev.pos() and self.clickable:
            if ev.button() == 1:
                self.mPosition()
        self._prev_zoom_pos = None
        self._prev_pan_pos = None

    def mPosition(self):
        #This function is called by a mouse event
        ## Get mouse coordinates saved when the mouse is clicked( incase dragging)
        mx = self._downpos.x()
        my = self._downpos.y()
        self.Candidates = [] #Initiate a list for storing indices of picked points
        #Get height and width of 2D Viewport space
        view_w = self.width()
        view_h = self.height()
        #Convert pixel values to normalized coordinates
        x = 2.0 * mx / view_w - 1.0
        y = 1.0 - (2.0 * my / view_h)
        # Convert projection and view matrix to numpy types and inverse them
        PMi = self.projectionMatrix().inverted()[0]
        VMi = self.viewMatrix().inverted()[0]
        #Move to clip coordinates by chosing z= -1 and w 1 (Dont understand this part)
        ray_clip = QtGui.QVector4D(x, y, -1.0, 1.0) # get transpose for matrix multiplication
        # Convert to eye space by view matrix
        ray_eye = PMi * ray_clip
        ray_eye.setZ(-1)
        ray_eye.setW(0)
        #Convert to world coordinates
        ray_world = VMi * ray_eye
        ray_world = QtGui.QVector3D(ray_world.x(), ray_world.y(), ray_world.z()) # get transpose for matrix multiplication
        ray_world.normalize()
        # Now I 'll use the ray intersection with spheres. I assume every point is a sphere with a radius
        #Please see http://antongerdelan.net/opengl/raycasting.html scroll down to spehere intersection
        O = np.matrix(self.cameraPosition())  # camera position should be starting point of the ray
        ray_world = np.matrix([ray_world.x(), ray_world.y(), ray_world.z()])
        overlaps = []
        for mean in self.means: # Iterate over all means
            OC = O - np.array(mean.pos)
            b = np.inner(ray_world, OC)
            b = b.item(0)
            c = np.inner(OC, OC)
            c = c.item(0) - (mean.size)**2
            bsqr = np.square(b)
            overlap = bsqr - c
            if overlap >= 0: # means intersection
                self.Candidates.append(mean)
                overlaps.append(overlap)
        
        if overlaps:
            winner = self.Candidates[np.argmin(overlaps)]
            self.unitClicked.emit(winner)