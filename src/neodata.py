"""
Created on Dec 12, 2013

@author: Christoph Gollan

In this module you can find the :class:`NeoData` class which is
used to load data that are in neo format.

After loading you can get different data for the units.

This class works together with the :class:`src.virtualunitmap.VirtualUnitMap`.
"""
from os.path import join, split, exists
import gc
from numpy import min, max, mean, std, array
from numpy.linalg import norm
from PyQt5.QtCore import QObject, pyqtSignal
from neo.io.pickleio import PickleIO
from neo.io import BlackrockIO
from copy import deepcopy


class NeoData(QObject):
    """        
    This class makes it possible to load and manage neo data.
    
    **Arguments**
    
        *cache_dir* (string):
            The directory where the cached data will be stored
            and from where it will be loaded.

    """

    progress = pyqtSignal(int)
    """
    Progress signal to let the parent widget know how far 
    the loading progress is.
    
    """

    def __init__(self, cache_dir):
        """
        **Properties**
        
            *cdir* (string):
                The path to the cache directory.
            *blocks* (list of :class:`neo.core.block.Block`):
                The loaded neo Blocks. Will be cached after loading so 
                that they can be loaded faster next time.
            *nums* (list of integer):
                Contains the number of real units per blocks.
            *rgios* (list of :class:`neo.io.BlackrockIO`):
                Contains the IO class to load the neo blocks.
            
        """
        super(QObject, self).__init__()
        #properties{
        self.cdir = cache_dir
        self.blocks = []
        self.nums = []
        self.rgios = []
        #}
        
        
    #### general methods ####    
        
#     def load_rgIOs(self, files):
#         l = len(files)
#         step = int(50/l)
#         if not self.rgios:
#             for i, f in enumerate(files):
#                 rgIO = BlackrockIO(f)
#                 self.rgios.append(rgIO)
#                 self.progress.emit(step*(i+1))
#         return self.rgios

    def load(self, files, channel):
        """
        Loads the neo blocks from the given files and the given channel.
        
        If the blocks are cached the cached ones will be loaded, 
        if not, the normal loading routine of the IOs will be used 
        and after that the blocks will be cached.
        
        **Arguments**
        
            *files* (list of string):
                The files that should be loaded.
            *channel* (integer):
                The channel that should be loaded.
        
        """
        #information for the progress
        l = len(files)
#         if not self.rgios:
#             v = 50
#             step = int(50/l)
#         else:
#             v = 0
#             step = int(100/l)
        v = 0
        step = int(100/l)
        
        self.delete_blocks()
        blocks = []
        #loading the IOs
#         rgios = self.load_rgIOs(files)
        
        #loading the blocks
        for i, f in enumerate(files):
                name = join(self.cdir, split(f)[1] + "_" + str(channel) + ".pkl")
 
                if exists(name):
                    #load from cache
                    pIO = PickleIO(name)
                    block = pIO.read_block()
                else:
                    #loading
#                     rgIO = rgios[i]
                    rgIO = BlackrockIO(f)
                    block = rgIO.read_block(index=None, name=None, description=None, nsx_to_load='none',
                                            n_starts=None, n_stops=None, channels=channel, units='all',
                                            load_waveforms=True, load_events=True,
                                            lazy=False, cascade=True)
                    del rgIO
                    #caching
                    pIO = PickleIO(name)
                    pIO.write_block(block)
                 
                blocks.append(block)
                #emits a signal with the current progress
                #after loading a block
                self.progress.emit(v+step*(i+1))

        nums = [len([unit for unit in b.channel_indexes[0].units 
                     if "noise" not in unit.description.split()
                     and "unclassified" not in unit.description.split()]) 
                    for b in blocks]
        self.blocks = blocks
        self.nums = nums
        
    def get_data(self, layer, unit):
        """
        Returns the data for a specific layer.
        
        **Arguments**
        
            *layer* (string):
                The layer you need data for.
                The layers are defined at another place.
            *unit* (:class:`neo.core.unit.Unit`):
                The unit that contains the data.
                
            **Returns**: tuple of numpy arrays
                Returns always a tuple even if there
                is just one array with data.
                
             **Raises**: ValueError
                If the layer is not supported.
        
        """
        if layer == "average":
            return mean(unit.spiketrains[0].waveforms.magnitude, axis=0)
        elif layer == "standard deviation":
            means = mean(unit.spiketrains[0].waveforms.magnitude, axis=0)[0]
            stds = std(unit.spiketrains[0].waveforms.magnitude, axis=0)[0]
            return array([means-2*stds, means+2*stds])
        elif layer == "all":
            wforms = unit.spiketrains[0].waveforms.magnitude
            return wforms.reshape(wforms.shape[0], wforms.shape[-1])
        elif layer == "spiketrain":
            return unit.spiketrains[0].magnitude
        elif layer == "units":
            vek = deepcopy(unit.spiketrains[0])
            vek.units = "ms"
            vek.sort()
            d = vek[1:] - vek[:len(vek) - 1]
            d = d.magnitude
            return (d, )
        elif layer == "sessions":
            vek = deepcopy(unit.spiketrains[0])
            vek.units = "ms"
            vek.sort()
            d = vek[1:] - vek[:len(vek) - 1]
            d = d.magnitude
            return (d, )
        elif layer == "n_spikes":
            return len(unit.spiketrains[0].magnitude)
        else:
            raise ValueError("Layer not supported")
    
    def get_channel_lengths(self):
        """
        Returns list containing the number of units in the channel
        on each block.
        
        """
        return self.nums
        
    def get_yscale(self, layer = "all"):
        """
        Calculates the maximum y-range of the (absolute) y-ranges
        of all average waveforms.
        
            **Returns**: tuple of integer
                -maximum and +maximum
        
        """
        datas = []
        yranges0 = []
        yranges1 = []
        for block in self.blocks:
            for unit in block.channel_indexes[0].units:
                if "noise" not in unit.description.split() and "unclassified" not in unit.description.split():
                    datas.append(self.get_data(layer, unit))
        for data in datas:
            tmp0 = min(data)
            tmp1 = max(data)
            
            yranges0.append(tmp0)
            yranges1.append(tmp1)
        
        maxi = max(yranges1) + 20.0
        mini = min(yranges0) - 20.0
        return (mini, maxi)

    def get_distance(self, unit1, unit2):
        """
        Calculates the distance between the average waveforms
        of two units.

        **Arguments**

            *unit1* (:class:`neo.core.unit.Unit`):
                The first unit.
            *unit2* (:class:`neo.core.unit.Unit`):
                The second unit.

            **Returns**: float
                The distance

        """
        y1 = self.get_data("average", unit1)
        y2 = self.get_data("average", unit2)
        return norm((y1 - y2))
    
    def delete_blocks(self):
        """
        Deletes all blocks.
        
        """
        while self.blocks:
            block = self.blocks.pop()
            while block.segments:
                segment = block.segments.pop()
                del segment
            while block.channel_indexes:
                channel = block.channel_indexes.pop()
                while channel.units:
                    unit = channel.units.pop()
                    while unit.spiketrains:
                        spiketrain = unit.spiketrains.pop()
                        del spiketrain
                    del unit
                while channel.analogsignals:
                    signal = channel.analogsignals.pop()
                    del signal
                del channel
            del block
        gc.collect()
            
    def delete_IOs(self):
        """
        Deletes all IOs.
        
        """
        while self.rgios:
            rgio = self.rgios.pop()
            del rgio
        gc.collect()
