"""
Created on Dec 12, 2013

@author: Christoph Gollan

In this module you can find the :class:`VirtualUnitMap` which is used to map
real units to virtual units. The virtual units can be swapped to have the 
same units in the same row.
"""
import numpy as np
from swan.automatic_mapping import SwanImplementation, calculate_mapping_bu
from swan.gui.palettes import UNIT_COLORS


class VirtualUnitMap(object):
    """        
    A class for mapping real units to virtual units.
    
    """

    def __init__(self):
        """
        **Properties**
        
            *mapping* (list of list of integer):
                A 2d array with integers that give you in a column the numbers 
                of the units from the same session and in the row
                the same unit id for the sessions.
            *visible* (list of boolean):
                Whether or not the unit rows should be visible.
                Contains one boolean for each unit row.
            *maximum_units* (integer):
                The summary of the length of all unit lists.
            *colors* (list of tuple of integer):
                Contains colors for plotting the units in different colors.
                Format: (R, G, B) RGB = 0..255
            *coln* (integer):
                The length of the colors list.
        
        """
        self.mapping = []
        self.visible = []
        self.active = []
        self.total_units = 0
        self.colors = UNIT_COLORS
        self.number_of_colors = len(self.colors)

    def set_initial_map(self, data):
        """
        Sets the default mapping.
        
        **Arguments**
        
            *total_units_per_block* (list of integer):
                The number of units per block.
        
        """
        maximum_units = sum(data.total_units_per_block)
        self.total_units = maximum_units
        mapping = []
        for session in range(len(data.blocks)):
            mapping.append([])
            count = 1
            for global_unit_id in range(maximum_units):
                try:
                    unit_description = data.blocks[session].channel_indexes[0].units[global_unit_id].description.split()

                    if "unclassified" in unit_description or "noise" in unit_description:
                        mapping[session].append(0)
                    else:
                        mapping[session].append(count)
                        count += 1
                except IndexError:
                    mapping[session].append(0)

        self.mapping = mapping
        self.visible = [[True for unit in session] for session in mapping]
        self.update_active()

    def set_map_from_dataframe(self, dataframe):
        if not dataframe.empty:
            vmap = np.zeros_like(np.array(self.mapping))
            for session_id in range(vmap.shape[0]):
                session_frame = dataframe.loc[dataframe.session == session_id]
                for global_unit_id, real_unit_id in zip(session_frame.label, session_frame.unit):
                    vmap[session_id][global_unit_id] = real_unit_id

            self.mapping = vmap.astype(np.int32).tolist()
            self.visible = [[True for unit in session] for session in vmap]
            self.update_active()

    def set_map(self, total_units_per_block, virtual_unit_map):
        """
        Sets the mapping given from the VUMap.
        
        **Arguments**
        
            *total_units_per_block* (list of integer):
                The number of units per block.
            *vum* (dictionary):
                A dictionary containing the mappings and other information.
        
        """
        total_units = sum(total_units_per_block)
        self.total_units = total_units

        total_sessions = len(total_units_per_block)

        for session in range(total_sessions):
            self.mapping.append([])

        for l in virtual_unit_map.values():
            if type(l) == list:
                for session in range(total_sessions):
                    unit = l[session][1]
                    self.mapping[session].append(unit)

        self.visible = [[True for j in range(len(self.mapping[i]))] for i in range(len(self.mapping))]
        self.update_active()

    def get_realunit(self, session_index, unit_index, data):
        """
        Returns the real unit for a virtual unit.
        
        **Arguments**
        
            *session_index* (integer):
                The session index.
            *unit_index* (integer):
                The unit index.
            *data* (:class:`src.neodata.NeoData`):
                The data object that contains the real unit.
            
            **Returns**: :class:`neo.core.unit.Unit`
                The real unit.
        
        """
        virtual_unit = self.mapping[session_index][unit_index]
        if "unclassified" not in data.blocks[session_index].channel_indexes[0].units[0].description.split():
            real_unit = data.blocks[session_index].channel_indexes[0].units[virtual_unit - 1]
        else:
            real_unit = data.blocks[session_index].channel_indexes[0].units[virtual_unit]
        # real_unit = data.blocks[session_index].channel_indexes[0].units[virtual_unit]
        return real_unit

    def swap(self, session_index, first_unit_index, second_unit_index):
        """
        Swaps two virtual units.
        
        **Arguments**
        
            *session_index* (integer):
                The session_index index.
            *first_unit_index* (integer):
                The unit index 1.
            *second_unit_index* (integer):
                The unit index 2.
        
        """
        self.mapping[session_index][first_unit_index], self.mapping[session_index][second_unit_index] = \
            self.mapping[session_index][second_unit_index], self.mapping[session_index][first_unit_index]
        # second_unit = self.mapping[session_index][second_unit_index]
        # self.mapping[session_index][second_unit_index] = self.mapping[session_index][first_unit_index]
        # self.mapping[session_index][first_unit_index] = second_unit
        self.update_active()

    def set_visible(self, session_id, global_unit_id, visible=True):
        """
        Sets a unit row as visible or not.
        
        **Arguments**
        
            *i* (integer):
                The column (session) index.
            *j* (integer):
                The row (unit) index.
            *visible* (boolean):
                Whether or not the unit row should be visible.
                Default: True.
        
        """
        self.visible[session_id][global_unit_id] = visible
        self.update_active()

    def update_active(self):
        """
        Updates the active mapping.
        
        The active mapping is a list of N lists, where N is the
        number of loaded sessions. Each nested list consists of
        zeros or ones. Ones signify that a unit is occupying
        that position in the mapping and is not hidden. Zeros
        signify that either no unit is occupying that position in the
        mapping or is hidden/disabled.
        
        Since the number of lists corresponds to the number of
        loaded sessions, remember that the first index when 
        looping over active corresponds to the sessions, while
        the second index corresponds to the units.
        
        """
        checkmap = np.array(self.mapping)
        checkmap[checkmap > 0] = 1
        #
        # Converts the boolean visible array to a corresponding
        # matrix of zeros and ones (inner multiply). Then, creates
        # active mapping by taking the element-wise product of the
        # mapping and the checkmap array (outer multiply). Effectively,
        # combines information contained in visibility and mapping.
        #
        active = np.multiply(checkmap, np.multiply(self.visible, 1))

        # Strips trailing zeros
        # for n, num in enumerate(active):
        #     active[n] = np.trim_zeros(num, 'b')
        #     if not active[n]:
        #         active[n] = [0]

        self.active = active

    def get_mapping(self):
        return self.mapping

    def get_visible(self):
        return self.visible

    def get_active(self):
        return self.active

    def get_color_list(self):
        return self.colors

    def get_colour(self, global_unit_id):
        """
        Returns the color for the given unit row.
        
        **Arguments**
        
            *i* (integer):
                The unit row index.
            *mpl* (boolean):
                Whether or not you need the color for matplotlib.
                Mpl uses another rgb format.
                Default: False.
            *layer* (string):
                If mpl is True, you can specify a layer 
                that needs a modified color.
                Default: None.
            
            **Returns**: tuple of integer
                The rgb color.
    
        """
        global_unit_id = global_unit_id % self.number_of_colors
        col = (
            self.colors[global_unit_id][0],
            self.colors[global_unit_id][1],
            self.colors[global_unit_id][2],
        )
        return col

    def calculate_mapping(self, data, storage, automatic_mapping=0, parent=None):
        """
        Calculates a mapping for the units based on features like distance.
        
        The units will be compared pare-wise and sequential.
        
        **Arguments**
        
            *data* (:class:`src.neodata.NeoData`):
                This object is needed to get the data 
                which will be used to compare the units.
            
            *base* (:class:`base.mystorage.MyStorage`):
                The class which handles the data and the project files.
        
        """
        if automatic_mapping == 0:
            # self.swan_implementation(data=data, base=base)
            algorithm = SwanImplementation(neodata=data, parent=parent)
            self.set_map_from_dataframe(algorithm.result)

        elif automatic_mapping == 1:
            calculate_mapping_bu(virtual_unit_map=self, data=data, storage=storage)

    def reset(self):
        """
        Resets the mapping.
        
        """
        self.mapping = []
        self.visible = []
        self.active = []
        self.total_units = 0
