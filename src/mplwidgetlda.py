"""
Created on Jul 7, 2017

@author: Shashwat Sridhar

In this module you can find the :class:`MplWidget3d` which inherits
from :class:`src.matplotlibwidget.MatplotlibWidget`.

It is extended by a 3d plot and the plotting methods.
"""
from src.matplotlibwidget import MatplotlibWidget
import numpy as np
from sklearn.decomposition import LinearDiscriminantAnalysis as LDA


class MplWidgetLDA(MatplotlibWidget):
    """
    A class with only one plot that shows 3d data.

    The *args* and *kwargs* are passed to :class:`src.matplotlibwidget.MatplotlibWidget`.
    
    """

    def __init__(self, *args, **kwargs):
        """
        **Properties**
        
            *_axes* (:class:`mpl_toolkits.mplot3d.Axes3d`):
                The 3d plot for this widget.
            *_kwargs* (dictionary):
                Plot parameters given as (key, value) pares.
        
        """
        MatplotlibWidget.__init__(self, *args, **kwargs)
        
        #properties{
        self._axes = None
        self._kwargs = {"grid":True, 
                        "set_xlabel":"Principal Component 1", 
                        "set_ylabel":"Principal Component 2", 
                        "set_zlabel":"Principal Component 3"}
        #}
        self.setup((1, 1), True, True)
        
        self._axes = self.get_axes()[0]
        self.clear_and_reset_axes(**self._kwargs)
        
    
    #### general methods ####    

    def plot(self, x, y, z, color, alpha = 1, s = 5, marker = '.'):
        """
        Plots data to the plot.
        
        **Arguments**
        
            *x* (1d iterable object):
                The x data that should be plotted.
            *y* (1d iterable object):
                The y data that should be plotted.
            *z* (1d iterable object):
                The z data that should be plotted.
            *color* (tuple of integer):
                The color of the lines.
        
        """
        patch = self._axes.scatter(xs = x, ys = y, zs = z, s = s, c = color, alpha = alpha, marker = marker)
        self.pca_draw(self._axes, patch)
        self.canvas.fig.tight_layout()

    def do_plot(self, vum, data, layers):
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
        #self.clear_and_reset_axes(**self._kwargs)
        
        found = [False for n in range(vum.n_)]
        
        for i in range(np.shape(vum.mapping)[0]):
            for j in range(np.shape(vum.mapping)[1]):
                if vum.visible[j] and vum.mapping[i][j] != 0:
                    found[j] = True
        
        if np.any(found) and layers:
            nums = [len(vum.mapping[i]) for i in range(len(vum.mapping))]
            
            while not nums[-1]:
                nums.pop()
            
            dom = np.argmax(nums)
            
            dom_channel = [data.get_data("all", vum.get_realunit(dom, j, data)) for j in range(nums[dom])]
            
            dom_channel = []
            
            for j in range(nums[dom]):
                runit = vum.get_realunit(dom, j, data)
                if vum.mapping[dom][j] != 0 and "noise"  not in runit.description.split() and "unclassified" not in runit.description.split():
                    dom_channel.append(data.get_data("all", runit))
            
            m_dom_channel, lv_dom_channel = self.merge_channel(dom_channel)
            
            lda = LDA(n_components = 3)
            
            dom_pca = pca.fit_transform(m_dom_channel)
            dom_ch_pca = self.split_waves(dom_pca, lv_dom_channel, 'all')
            
            self.canvas.draw()
            
            for layer in layers:
                if layer == "units":
                    for i in range(len(data.blocks)):
                        if i != dom:
                            channel = []
                            
                            for j in range(nums[i]):
                                runit = vum.get_realunit(i, j, data)
                                if vum.mapping[i][j] != 0 and vum.visible[j] and "noise"  not in runit.description.split() and "unclassified" not in runit.description.split():
                                    channel.append(data.get_data("all", runit))
                            
                            merged_channel, len_vec = self.merge_channel(channel)
                            pca_channel = self.split_waves(pca.transform(merged_channel), len_vec, 'all')
                            
                            axes = self.return_axes(pca_channel)
                            
                            c = 0
                            for u in range(nums[i]):
                                if vum.visible[u] and vum.mapping[i][u] != 0:
                                    col = vum.get_color(u, True, None)
                                    self.plot(axes[0][c], axes[1][c], axes[2][c], s = 1, color = col, alpha = 0.05, marker = '.')
                                    self.plot(np.mean(axes[0][c], axis = 0), np.mean(axes[1][c], axis = 0), np.mean(axes[2][c], axis = 0), s = 25, color = col, alpha = 1, marker = 'o')
                                    c += 1
                            
                            del channel
                            del merged_channel
                            del pca_channel
                            del axes
                        
                        elif i == dom:
                            axes = self.return_axes(dom_ch_pca)
                            
                            c = 0
                            for u in range(nums[dom]):
                                if vum.visible[u] and vum.mapping[dom][u] != 0:
                                    col = vum.get_color(u, True, None)
                                    self.plot(axes[0][c], axes[1][c], axes[2][c], s = 1, color = col, alpha = 0.05, marker = '.')
                                    self.plot(np.mean(axes[0][c], axis = 0), np.mean(axes[1][c], axis = 0), np.mean(axes[2][c], axis = 0), s = 25, color = col, alpha = 1, marker = 'o')
                                    c += 1
                            
                            del axes
        
                del dom
                del dom_channel
                del dom_ch_pca
                del dom_pca
                
        else:
            axes_list = self.canvas.fig.get_axes()
            for ax in axes_list:
                ax.cla()
    
    def merge_channel(self, channel):
        total_length = 0
        length_vector = [0]
        
        for unit in channel:
            total_length += len(unit)
            length_vector.append(total_length)
        
        waves = np.zeros((total_length, 38))
        
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
        
        return np.array(channel)
    
    def return_axes(self, filtered_channel):
        
        x = []
        y = []
        z = []
        for u in range(len(filtered_channel)):
            x.append([])
            y.append([])
            z.append([])
            for item in filtered_channel[u]:
                x[u].append(item[0])
                y[u].append(item[1])
                z[u].append(item[2])
        
        return x, y, z