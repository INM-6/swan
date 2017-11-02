#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 12:56:06 2017

@author: sridhar
"""

from src.mypgwidget import PyQtWidget3d
import numpy as np
from sklearn.decomposition import PCA
from copy import deepcopy
from itertools import chain

class pgWidgetPCA(PyQtWidget3d):
    
    def __init__(self, parent = None):
        
        PyQtWidget3d.__init__(self, parent = parent)
        self.positions = []
        self.means = []
        
        self.max_distance = 0
        self._first = True
        self.wave_length = 0 # Initial dummy value, later updated from data
    
    def addScatterPlot(self, plotItem = None, setGLOptions = 'opaque'):
        self.addScatterPlotItem(plotItem = plotItem, setGLOptions = setGLOptions)
        
    def clear_plot(self):
        self.reset_plot()
        self.positions = []
        self.means = []
    
    def do_plot(self, vum, data, layers):
        self.clear_plot()
        
        max_distance = 0
        
        self.wave_length = data.wave_length
        found = [False for n in range(vum.n_)]
        
        for i in range(np.shape(vum.mapping)[0]):
            for j in range(np.shape(vum.mapping)[1]):
                if vum.visible[j] and vum.mapping[i][j] != 0:
                    found[j] = True
        
        if np.any(found) and layers:
            nums = deepcopy(vum.mapping)
            for num in nums:
                try:
                    while not num[-1]:
                        num.pop()
                except IndexError:
                    num = [0]
            dom = np.argmax([np.count_nonzero(nu) for nu in nums])
            dom_channel = []
            
            for j in range(len(nums[dom])):
                runit = vum.get_realunit(dom, j, data)
                if vum.mapping[dom][j] != 0 and "noise"  not in runit.description.split() and "unclassified" not in runit.description.split():
                    dom_channel.append(data.get_data("all", runit))
                        
            m_dom_channel, lv_dom_channel = self.merge_channel(dom_channel)
            
            pca = PCA(n_components = 3)
            
            dom_pca = pca.fit_transform(m_dom_channel)
            dom_ch_pca = self.split_waves(dom_pca, lv_dom_channel, 'all')
            
            for layer in layers:
                if layer == "units":
                    for i in range(len(data.blocks)):
                        if i != dom:
                            channel = []
                            for j in range(len(nums[i])):
                                runit = vum.get_realunit(i, j, data)
                                if nums[i][j] != 0 and vum.visible[j] and "noise"  not in runit.description.split() and "unclassified" not in runit.description.split():
                                    channel.append(data.get_data("all", runit))
                            
                            merged_channel, len_vec = self.merge_channel(channel)
                            try:    
                                pca_channel = self.split_waves(pca.transform(merged_channel), len_vec, 'all')
                                
                                max_distance = self.return_max(pca_channel)
                                if max_distance > self.max_distance:
                                    self.max_distance = max_distance
                                
                                c = 0
                                for u in range(len(nums[i])):
                                    if found[u] and nums[i][u] != 0:
                                        col = vum.get_color(u, False, None, True)
                                        self.positions.append(self.createScatterPlotItem(pos = pca_channel[c], size = 1, color = col, pxMode=True))
                                        self.means.append(self.createScatterPlotItem(pos = pca_channel[c].mean(axis = 0), size = 15, color = col, pxMode=True))
                                        c += 1
                                
                                del channel
                                del merged_channel
                                del pca_channel
                            
                            except ValueError:
                                pass
                            
                        elif i == dom:
                            
                            max_distance = self.return_max(dom_ch_pca)
                            if max_distance > self.max_distance:
                                self.max_distance = max_distance
                            
                            c = 0
                            for u in range(len(nums[dom])):
                                if found[u] and nums[dom][u] != 0:
                                    col = vum.get_color(u, False, None, True)
                                    self.positions.append(self.createScatterPlotItem(pos = dom_ch_pca[c], size = 1, color = col, pxMode=True))
                                    self.means.append(self.createScatterPlotItem(pos = dom_ch_pca[c].mean(axis = 0), size = 15, color = col, pxMode=True))
                                    c += 1
                
#                if layer == "sessions":
#                    for i in range(len(data.blocks)):
#                        if i != dom:
#                            channel = []
#                            for j in range(len(nums[i])):
#                                runit = vum.get_realunit(i, j, data)
#                                if nums[i][j] != 0 and vum.visible[j] and "noise"  not in runit.description.split() and "unclassified" not in runit.description.split():
#                                    channel.append(data.get_data("all", runit))
#                                
#                            merged_channel, len_vec = self.merge_channel(channel)
                    
                del dom
                del dom_channel
                del dom_ch_pca
                del dom_pca
        if len(self.positions) == len(self.means):
            for item in self.positions:
                self.addScatterPlot(item, setGLOptions='translucent')
            for mean in self.means:
                self.addScatterPlot(mean, setGLOptions = 'opaque')
        else:
            print("Something is wrong!")
            print("Length of positions list: {}".format(len(self.positions)))
            print("Length of means list: {}".format(len(self.means)))
        
        self.cameraPosition(distance = 4*self.max_distance)
        
    def merge_channel(self, channel):
        total_length = 0
        length_vector = [0]
        
        for unit in channel:
            total_length += len(unit)
            length_vector.append(total_length)
        
        waves = np.zeros((total_length, self.wave_length))
        
        for u, unit in enumerate(channel):
            for wf, wave in enumerate(unit):
                waves[wf + length_vector[u]] = wave
        
        return waves, length_vector
    
    def split_waves(self, waves, length_vector, components):
        
        channel = []
        
        if components == 'all':
            for n in range(len(length_vector) - 1):
                channel.append(waves[length_vector[n]:length_vector[n+1]])
        else:
            for n in range(len(length_vector) - 1):
                channel.append(waves[length_vector[n]:length_vector[n+1], :components])
        
        return channel
    
    def return_max(self, nested_list):
        return np.amax(list(chain.from_iterable(nested_list)))
