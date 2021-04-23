"""
Created on Dec 12, 2013

@author: Christoph Gollan

In this module you can find the :class:`NeoData` class which is
used to load data that are in neo format.

After loading you can get different data for the units.

This class works together with the :class:`src.virtualunitmap.VirtualUnitMap`.
"""
import gc
from itertools import chain
from neo.io.pickleio import PickleIO
from neo.io import get_io
from neo import Group, SpikeTrain
import numpy as np
from numpy.linalg import norm
from os.path import join, split, exists
from PyQt5.QtCore import QObject, pyqtSignal
import quantities as pq
from scipy.signal import filtfilt, butter


def unit_in_channel(unit, channel):
    channel_id = unit.annotations.get("channel_id", None)
    if channel_id is not None:
        if channel_id == channel:
            return True
        else:
            return False
    else:
        return False


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
            *total_units_per_block* (list of integer):
                Contains the number of real units per block.
            *rgios* (list of :class:`neo.io.BlackrockIO`):
                Contains the IO class to load the neo blocks.
            
        """
        super(QObject, self).__init__()
        self.cdir = cache_dir
        self.blocks = []
        self.total_units_per_block = []
        self.rgios = []
        self._wave_length = 0
        self.segments = []
        self.units = []
        self.events = []
        self.unique_labels = []
        self.sampling_rate = 0.
        self.current_channel = 0

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
        num_of_files = len(files)

        count = 0
        step = int(100 / num_of_files)

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

                session = get_io(f)
                block = session.read_block()

                del session

                # caching
                # pIO = PickleIO(name)
                # pIO.write_block(block)

            blocks.append(block)
            # emits a signal with the current progress
            # after loading a block
            self.progress.emit(count + step * (i + 1))

        self.blocks = []
        self.segments = []
        self.units = []
        nums = []
        for b, block in enumerate(blocks):
            self.units.append([])
            for s, segment in enumerate(block.segments):

                # count spiketrains and save units as neo.Group objects
                num_spiketrains = 0
                for spiketrain in segment.spiketrains:
                    if spiketrain.annotations["channel_id"] == channel and len(spiketrain) > 2:
                        unit = Group(
                            objects=[spiketrain],
                            name=spiketrain.name,
                            description=f"Unit channel_id: {spiketrain.annotations['channel_id']}, "
                                        f"unit_id: {spiketrain.annotations['unit_id']}",
                            file_origin=spiketrain.file_origin,
                            allowed_types=[SpikeTrain],
                            **spiketrain.annotations,
                        )
                        self.units[b].append(unit)
                        num_spiketrains += 1

                nums.append(num_spiketrains)

            block.groups = sorted(self.units[b], key=lambda x: int(x.annotations["unit_id"]))
            self.segments.append(block.segments)
            self.blocks.append(block)

        self.set_events_and_labels()
        self.total_units_per_block = nums

        waveform_sizes = []
        for block in blocks:
            for unit in block.groups:
                waveform_sizes.append(unit.spiketrains[0].waveforms.shape[-1])

        assert np.unique(waveform_sizes).size == 1, "spike_widths across blocks must be equal"

        self._wave_length = np.unique(waveform_sizes)[0]

        try:
            self.sampling_rate = self.blocks[0].annotations["sampling_rate"]
        except (KeyError, IndexError):
            self.sampling_rate = 30000. * pq.Hz

        self.current_channel = channel

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
            return np.mean(unit.spiketrains[0].waveforms.magnitude, axis=0)[0] * pq.uV
        elif layer == "standard deviation":
            means = np.mean(unit.spiketrains[0].waveforms.magnitude, axis=0)[0]
            stds = np.std(unit.spiketrains[0].waveforms.magnitude, axis=0)[0]
            return np.array([means - 2 * stds, means + 2 * stds]) * pq.uV
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
            return d,
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
            hist, bin_edges = np.histogram(unit.spiketrains[0].magnitude, bins=bins)
            return filtfilt(b, a, hist)
        else:
            raise ValueError("Layer not supported")

    def get_channel_lengths(self):
        """
        Returns list containing the number of units in the channel
        on each block.
        
        """
        return self.total_units_per_block

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
            for unit in block.groups:
                if unit_in_channel(unit, self.current_channel):
                    datas.append(self.get_data(layer, unit))

        for data in datas:
            tmp0 = np.min(data)
            tmp1 = np.max(data)

            yranges0.append(tmp0)
            yranges1.append(tmp1)

        maxi = np.max(yranges1) + 20.0
        mini = np.min(yranges0) - 20.0
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
        y1 = self.get_data("average", unit1)
        y2 = self.get_data("average", unit2)
        return norm(np.subtract(y1 - y2))

    def get_unique_labels(self):
        return self.unique_labels

    def get_events_dict(self):
        return self.events

    def get_wave_length(self):
        return self._wave_length

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
        unique_labels = np.unique(raveled_labels)

        event_dict = {}
        for label in unique_labels:
            temp_list = []
            for b in range(len(events)):
                temp_list.append([])
                for s in range(len(events[b])):
                    temp_list[b].append([])
                    for e in range(len(events[b][s])):
                        temp_list[b][s].append([])
                        t_points = times[b][s][e][np.where(labels[b][s][e] == label)[0]]
                        temp_list[b][s][e] = t_points.rescale(pq.ms)
            event_dict[label] = temp_list

        self.unique_labels = unique_labels
        self.events = event_dict
