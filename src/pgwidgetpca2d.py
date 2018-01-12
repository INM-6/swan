"""
Created on Nov 16, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`pgWidget2d` which inherits
from :class:`src.mypgwidget.PyQtWidget2d`.

It is extended by a 2d plot and the plotting methods.
"""
from src.mypgwidget import PyQtWidget2d
from numpy import shape, count_nonzero, argmax, zeros, any as np_any, mean as mn, array
from sklearn.decomposition import PCA
from copy import deepcopy

class pgWidgetPCA2d(PyQtWidget2d):
    """
    A class with only one plot that shows 2d PCA scatter plots.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`matplotlib.axes.Axes`):
                The 2d plot for this widget.
        
        """
        PyQtWidget2d.__init__(self)
        
        layers = ["units", "sessions"]
        self.toolbar.setupRadioButtons(layers)
        self.toolbar.doLayer.connect(self.triggerRefresh)
        
        self._plotItem = self.pgCanvas.getPlotItem()
        self._plotItem.enableAutoRange()
        
        self._means = []
        self._positions = []
        
        self.showGrid()
    
    #### general methods ####
    
    def plotMean(self, x, y, size, color, name, pxMode = True):
        x = [x]
        y = [y]
        self._means.append(self.createScatterPlotItem(x = x, y = y, size = size, color = color, name = name, pxMode = pxMode))
    
    def plotPoints(self, pos, size, color, name, pxMode = True):
        pos = array(pos)
        x = pos[:, 0]
        y = pos[:, 1]
        self._positions.append(self.createScatterPlotItem(x = x, y = y, size = size, color = color, name = name, pxMode = pxMode, autoDownsample = True, antialias = False))
    
    def do_plot(self, vum, data):
        """
        Plots data for every layer and every visible unit.
        
        **Arguments**
        
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                Is needed to get the unit indexes.
            *data* (:class:`src.neodata.NeoData`):
                Is needed to get the units.
            *layers* (list of string):
                The layers that are visible.
        
        """
        self.clear_plots()
        
        if self.toolbar.layers.isChecked():
            
            layers = self.toolbar.getCheckedLayers()
            
            self.wave_length = data.wave_length
            found = [False for n in range(vum.n_)]
            
            for i in range(shape(vum.mapping)[0]):
                for j in range(shape(vum.mapping)[1]):
                    if vum.visible[j] and vum.mapping[i][j] != 0:
                        found[j] = True
            
            if np_any(found) and layers:
                nums = deepcopy(vum.mapping)
                for num in nums:
                    try:
                        while not num[-1]:
                            num.pop()
                    except IndexError:
                        num = [0]
                dom = argmax([count_nonzero(nu) for nu in nums])
                dom_channel = []
                
                for j in range(len(nums[dom])):
                    runit = vum.get_realunit(dom, j, data)
                    if vum.mapping[dom][j] != 0 and "noise"  not in runit.description.split() and "unclassified" not in runit.description.split():
                        dom_channel.append(data.get_data("all", runit))
                            
                m_dom_channel, lv_dom_channel = self.merge_channel(dom_channel)
                
                pca = PCA(n_components = 2)
                
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
                                    
                                    c = 0
                                    for u in range(len(nums[i])):
                                        if found[u] and nums[i][u] != 0:
                                            col = vum.get_color(u, False, layer, False)
                                            self.plotPoints(pos = pca_channel[c], size = 1, color = col, name = "".format(i, u))
                                            self.plotMean(x = mn(pca_channel[c][:, 0], axis = 0), y = mn(pca_channel[c][:, 1], axis = 0), size = 15, color = col, name = "".format(i, u))
                                            c += 1
                                    
                                    del channel
                                    del merged_channel
                                    del pca_channel
                                
                                except ValueError:
                                    pass
                                
                            elif i == dom:
                                c = 0
                                for u in range(len(nums[dom])):
                                    if found[u] and nums[dom][u] != 0:
                                        col = vum.get_color(u, False, layer, False)
                                        self.plotPoints(pos = dom_ch_pca[c], size = 1, color = col, name = "".format(i, u))
                                        self.plotMean(x = mn(dom_ch_pca[c][:, 0], axis = 0), y = mn(dom_ch_pca[c][:, 1], axis = 0), size = 15, color = col, name = "".format(i, u))
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
            else:
                print("Something is wrong!")
                print("Length of positions list: {}".format(len(self._positions)))
                print("Length of means list: {}".format(len(self._means)))
    
    def merge_channel(self, channel):
        total_length = 0
        length_vector = [0]
        
        for unit in channel:
            total_length += len(unit)
            length_vector.append(total_length)
        
        waves = zeros((total_length, self.wave_length))
        
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
    
    def connectPlots(self):
        for item in self._means:
            item.curve.setClickable(True, width = 5)
            item.sigClicked.connect(self.getItem)
        
    def clear_plots(self):
        self._means = []
        for item in self._positions:
            self.pgCanvas.removeItem(item)
        self._positions = []
        self.clearAll()