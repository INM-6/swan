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

from numpy import mean, std, array, histogram, unique, where, subtract
from numpy import min as nmin
from numpy import max as nmax
from numpy.linalg import norm
from scipy.signal import filtfilt, butter
from PyQt5.QtCore import QObject, pyqtSignal
from neo.io.pickleio import PickleIO
from neo.io import blackrockio_v4
from itertools import chain
import quantities as pq
from src.isolationscore import calculate_isolation_scores


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
            *ios* (list of :class:`neo.io.BlackrockIO`):
                Contains the IO class to load the neo blocks.
            
        """
        super(QObject, self).__init__()
        # properties{
        self.cdir = cache_dir
        self.blocks = []
        self.nums = []
        self.ios = []
        self.wave_length = 0.
        self.segments = []
        self.units = []
        self.events = []
        self.unique_labels = []
        self.sampling_rate = 0.
        # }

    #### general methods ####

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
        # information for the progress
        l = len(files)
        v = 0
        step = int(100 / l)

        self.delete_blocks()
        blocks = []

        # loading the blocks
        for i, f in enumerate(files):
            name = join(self.cdir, split(f)[1] + "_" + str(channel) + ".pkl")

            if exists(name):
                # load from cache
                pIO = PickleIO(name)
                block = pIO.read_block()
            else:
                # loading
                BlackrockIO = blackrockio_v4.BlackrockIO(f)
                block = BlackrockIO.read_block(index=None, name=None, description=None, nsx_to_load='none',
                                               n_starts=None, n_stops=None, channels=channel, units='all',
                                               load_waveforms=True, load_events=True,
                                               lazy=False, cascade=True)
                del BlackrockIO
                # caching
                pIO = PickleIO(name)
                pIO.write_block(block)

            out = calculate_isolation_scores(channel_number=channel, block=block, lambda_value=8, speed=100)
            blocks.append(block)
            # emits a signal with the current progress
            # after loading a block
            self.progress.emit(v + step * (i + 1))

        self.blocks = blocks
        self.segments = [block.segments for block in self.blocks]
        nums = [len([unit for unit in b.channel_indexes[0].units
                     if "noise" not in unit.description.split()
                     and "unclassified" not in unit.description.split()])
                for b in self.blocks]
        self.units = [[unit for unit in b.channel_indexes[0].units
                       if "noise" not in unit.description.split()
                       and "unclassified" not in unit.description.split()]
                      for b in self.blocks]
        # self.spiketrains = self.create_spiketrains_dictionary(self.units)
        self.set_events_and_labels()
        self.nums = nums
        self.wave_length = len(self.blocks[0].channel_indexes[0].units[0].spiketrains[0].waveforms[0].magnitude[0])
        self.sampling_rate = self.blocks[0].channel_indexes[0].units[0].spiketrains[0].sampling_rate

    def get_data(self, layer, unit, **kwargs):
        """
        Returns the data for a specific layer.
        
        **Arguments**
        
            *layer* (string):
                The layer you need data for.
                The layers are defined at another place.
            *unit* (:class:`neo.core.unit.Unit`):
                The unit that contains the data.
                
            **Returns**: different types for different layers
                (N is the number of timepoints in each waveform and m is the
                total number of waveforms/timestamps in the unit)
            
                average: numpy array of shape (N,)
                standard deviation: numpy array of shape (N, 2)
                all: numpy array of shape (N, m)
                spiketrains: numpy array of shape (m,)
                units: tuple containing a numpy array of shape (m,)
                sessions: tuple containing a numpy array of shape (m,)
                rate profile: 
                
             **Raises**: ValueError
                If the layer is not supported.
        
        """
        if layer == "average":
            return mean(unit.spiketrains[0].waveforms.magnitude, axis=0)[0] * pq.uV
        elif layer == "standard deviation":
            means = mean(unit.spiketrains[0].waveforms.magnitude, axis=0)[0]
            stds = std(unit.spiketrains[0].waveforms.magnitude, axis=0)[0]
            return array([means - 2 * stds, means + 2 * stds]) * pq.uV
        elif layer == "all":
            wforms = unit.spiketrains[0].waveforms.magnitude
            return wforms.reshape(wforms.shape[0], wforms.shape[-1])
        elif layer == "spiketrain":
            return unit.spiketrains[0]
        elif layer == "units":
            vek = unit.spiketrains[0].copy().rescale(pq.s)
            vek.sort()
            d = vek[1:] - vek[:len(vek) - 1]
            d = d.magnitude
            return (d,)
        elif layer == "sessions":
            vek = unit.spiketrains[0].copy().rescale(pq.s)
            vek.sort()
            d = vek[1:] - vek[:len(vek) - 1]
            d = d.magnitude.tolist()
            return d
        elif layer == "n_spikes":
            return len(unit.spiketrains[0].magnitude)
        elif layer == "rate profile":
            order = kwargs.get("order", 4)
            Wn = kwargs.get("Wn", 0.008)
            bins = kwargs.get("bins", 4000)
            b, a = butter(order, Wn)
            hist, bin_edges = histogram(unit.spiketrains[0].magnitude, bins=bins)
            return filtfilt(b, a, hist)
        else:
            raise ValueError("Layer not supported")

    def get_channel_lengths(self):
        """
        Returns list containing the number of units in the channel
        on each block.
        
        """
        return self.nums

    def get_yscale(self, layer="average"):
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
            tmp0 = nmin(data)
            tmp1 = nmax(data)

            yranges0.append(tmp0)
            yranges1.append(tmp1)

        maxi = nmax(yranges1) + 20.0
        mini = nmin(yranges0) - 20.0
        return mini, maxi

    def get_dates(self):
        """
        Getter for the dates on which the sessions were recorded. This data is
        stored on each block under block.rec_datetime.date().
        
            **Returns**: list
                list of dates
        """
        return [block.rec_datetime.date() for block in self.blocks]

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
        x1 = self.get_data("average", unit1)
        x2 = self.get_data("average", unit2)
        return norm(subtract(x1, x2))

    def get_unique_labels(self):
        return self.unique_labels

    def get_events_dict(self):
        return self.events

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
        while self.ios:
            io = self.ios.pop()
            del io
        gc.collect()

    def create_spiketrains_dictionary(self, units):
        """
        Returns a dictionary of spiketrains to memeoy for easy retrieval.
        
        **Arguments**
            
            *units* (list):
                List of all units in the dataset,
                arranged as a list of units for every session loaded.
                
        **Returns**
            
            *spiketrains* (dict):
                A dictionary of spiketrains corresponding to each unit.
                Each key is the unit itself, for easy access. The
                corresponding value is the spiketrain.
        """

        spiketrains = {}

        for block in units:
            for unit in block:
                spiketrains[unit] = unit.spiketrains[0]

        return spiketrains

    def set_events_and_labels(self):
        """
        Returns a dictionary of event times to memory.
        
        **Arguments**
            
            *blocks* (list):
                List of loaded blocks (sessions)
        
        **Returns**
            
            *events_dict* (dict):
                A dictionary of time points corresponding to each
                event found in the whole dataset. The keys hold the
                event ids and the corresponding values are lists of
                lists. The list of lists preserve the neo structure:
                    
                    BLOCK > SEGMENT > EVENT
                
                The event list contains all the time points where the
                event occured in the corresponding block.
        """
        events = [[seg.events for seg in block.segments] for block in self.blocks]
        labels = [[[event.labels for event in segment] for segment in block] for block in events]
        times = [[[event.times for event in segment] for segment in block] for block in events]

        raveled_labels = list(chain.from_iterable(list(chain.from_iterable(list(chain.from_iterable(labels))))))
        unique_labels = unique(raveled_labels)

        event_dict = {}
        for label in unique_labels:
            temp_list = []
            for b in range(len(events)):
                temp_list.append([])
                for s in range(len(events[b])):
                    temp_list[b].append([])
                    for e in range(len(events[b][s])):
                        temp_list[b][s].append([])
                        t_points = times[b][s][e][where(labels[b][s][e] == label)]
                        temp_list[b][s][e] = t_points.rescale(pq.ms)
            event_dict[label] = temp_list

        self.unique_labels = unique_labels
        self.events = event_dict
