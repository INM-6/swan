"""
Created on Dec 12, 2013

@author: Christoph Gollan

In this module you can find the :class:`VirtualUnitMap` which is used to map
real units to virtual units. The virtual units can be swapped to have the 
same units in the same row.
"""
import numpy as np
from scipy.spatial.distance import cdist
from swan.automatic_mapping import SwanImplementation
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
        mapping = np.zeros((len(data.total_units_per_block), maximum_units), dtype=int).tolist()

        count = 1
        for s, session in enumerate(data.blocks):
            for pos in range(data.total_units_per_block[s]):
                mapping[s][pos] = 1
                count += 1

        self.total_units = maximum_units
        self.mapping = mapping
        self.visible = [[True for unit in session] for session in mapping]
        self.update_active()

    def set_map_from_dataframe(self, dataframe):
        if not dataframe.empty:
            vmap = np.zeros_like(np.array(self.mapping))
            for session_id in range(vmap.shape[0]):
                session_frame = dataframe.loc[dataframe.session == session_id]
                for global_unit_id, real_unit_id in zip(session_frame.label, session_frame.unit):
                    vmap[session_id][global_unit_id] = real_unit_id + 1

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
        real_unit = data.blocks[session_index].groups[virtual_unit - 1]
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

    def get_colour(self, global_unit_id, alpha=1.0):
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

    def swan_implementation(self, data, storage):
        swaps = 0
        # Retrieve mapping from base
        backup_mapping = np.array(storage.get_map().mapping.copy()).T
        pre_mapping = backup_mapping.copy()
        # loop over columns/sessions
        for s in range(pre_mapping.shape[1]):
            # initialize array of mean waveform max amplitudes
            averages = np.zeros((pre_mapping.shape[0]))

            # loop over rows/units
            for j in range(len(averages)):
                # ignore zeros in the map (correspond to non-existent units)
                if pre_mapping[j][s] != 0:
                    # Retrieve unit
                    runit = self.get_realunit(s, j, data)
                    # Retrieve mean waveform for the unit
                    wave = data.get_data("average", runit)
                    # Store max amplitude of mean waveform
                    averages[j] = np.amax(np.abs(wave))

            #
            # Sort the units in each session by max amplitude of mean waveform
            # and swap the corresponding units in the base.
            #

            # loop over rows/units
            for i in range(len(averages)):
                # retrieve index of max value in session
                max_index = np.argmax(averages[i:]) + i
                if max_index != i:
                    self.swap(s, i, max_index)
                    tmp = averages[max_index]
                    averages[max_index] = averages[i]
                    averages[i] = tmp
                    swaps += 1

        storage.change_map()
        # Refresh the mapping using the values in base
        mapping = np.array(storage.get_map().mapping.copy()).T

        # Initialize an array shaped like "mapping" and set all values to np.nan
        history = np.zeros_like(mapping, dtype=np.float)
        history[history == 0.0] = None
        print("Initial Mapping: {}".format(mapping))

        # Loop over all columns/sessions except the last one
        for i in range(mapping.shape[1] - 1):
            # Loop over all rows/units
            print("\nFirst loop: {}".format(i))
            for j in range(mapping.shape[0]):
                # ignore zeros in the map (correspond to non-existent units)
                print("\tSecond Loop: {}".format(j))
                if mapping[j][i] > 0:  # to avoid errors in float comparison
                    # Choose (j, i)th unit as the actor and obtain it's mean waveform
                    runit_actor = self.get_realunit(i, j, data)
                    actor_wave = data.get_data("average", runit_actor)
                    actor_rp = data.get_data("rate profile", runit_actor)

                    # Initialize matrix to store distances to the actor unit
                    distances_waves = np.zeros((mapping.shape[0], mapping.shape[1]))
                    distances_rp = np.zeros((mapping.shape[0], mapping.shape[1]))

                    # Loop over all columns/sessions again
                    for k in range(mapping.shape[1]):
                        # Loop over all rows/units again
                        print("\t\tThird Loop: {}".format(k))
                        for l in range(mapping.shape[0]):
                            if mapping[l][k] > 0:
                                # Choose (l, k)th units as the support and obtain it's mean waveform
                                print("\t\t\tFourth Loop {}\n".format(l))
                                runit_support = self.get_realunit(k, l, data)
                                support_wave = data.get_data("average", runit_support)
                                support_rp = data.get_data("rate profile", runit_support)
                                #
                                # Calculate and store the Euclidean distance to
                                # support from actor (multiplied by a distance
                                # factor)
                                #
                                distances_waves[l][k] = np.linalg.norm(
                                    np.subtract(actor_wave, support_wave))  # * np.exp(abs(k-i))
                                distances_rp[l][k] = np.linalg.norm(np.subtract(actor_rp, support_rp))
                    #                            if mapping[l][k] > 0:
                    #                                history[l][k] = distances[l][k]

                    # print("Distances:\n {}\n".format(distances))

                    #
                    # Extract the dataset corresponding to all distance measures
                    # with non-zero mapping values and calculate the reject threshold
                    #

                    distances = distances_waves  # + distances_rp

                    threshold_dataset = distances[mapping > 0]
                    dataset_reject_threshold = np.mean(threshold_dataset)
                    # dataset_std = np.std(threshold_dataset)
                    # threshold_range_L = threshold_mean + 0.5 * threshold_std
                    # dataset_reject_threshold = dataset_mean + 0.5 * dataset_std

                    # print("Threshold: {}\n".format(dataset_reject_threshold))

                    # 
                    # The following loop is the main part of the mapping algorithm,
                    # which uses the distances between units to rearrange (swap) them.
                    #

                    # Generate loop range for the loop
                    if mapping.shape[1] < 10:
                        loop_range = range(mapping.shape[1])
                    else:
                        loop_range = [x for x in range(i + 9) if (i + x) <= mapping.shape[1]]

                    # Start looping over sessions/columns
                    for k in loop_range:
                        # Find the argument of the minimum in the kth column
                        min_arg = np.argmin(distances[:, k])
                        print("i: {}, j: {}, k: {}, min_arg: {}\n".format(i, j, k, min_arg))
                        if min_arg == j:
                            # Do nothing if the minimum argument is the same as the row we're looping over
                            pass
                        elif distances[min_arg][k] <= dataset_reject_threshold:
                            # If the distance between the two waveforms falls within
                            # the threshold, we swap the two positions in the kth col
                            if np.isnan(history[min_arg][k]):
                                # If the unit has not been swapped earlier.
                                history[j][k] = distances[min_arg][k]
                                self.swap(k, min_arg, j)
                                # mapping = backup_mapping.copy()
                                swaps += 1
                            else:
                                # If the unit has been swapped earlier, swap only if
                                # the new distance is less than the old distance
                                prev_dist = history[min_arg][k]
                                curr_dist = distances[min_arg][k]
                                if curr_dist < prev_dist:
                                    history[j][k] = distances[min_arg][k]
                                    self.swap(k, min_arg, j)
                                    # mapping = backup_mapping.copy()
                                    swaps += 1
                        elif distances[min_arg][k] > dataset_reject_threshold:
                            # If the distance between the two waveforms is greater than
                            # the threshold, move the unit to the first available free
                            # plot
                            loc = 0
                            first_zero = np.where(mapping[:, k] == 0)[0][loc]

                            try:
                                while np.sum(mapping[first_zero]) > 0.5:
                                    loc += 1
                                    first_zero = np.where(mapping[:, k] == 0)[0][loc]
                            except IndexError:
                                first_zero = 0
                            self.swap(k, first_zero, min_arg)
                            history[min_arg][k] = np.nan
                            mapping = backup_mapping.copy()
                            swaps += 1
                            # print("Swapped {} with empty plot {} on day {}".format(min_arg, first_zero, k))
                            # print("Mapping: {}".format(mapping))
                        else:
                            # If none of the above cases yield true, something is wrong
                            print("Exception reached")
                            print(distances_waves)
                            print(distances_rp)
                            print(distances)
                            mapping = backup_mapping.copy()
        storage.change_map()
        print("Total swaps: {}\n".format(swaps))

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
            self.calculate_mapping_bu(data=data, storage=storage)

    def calculate_mapping_bu(self, data, storage):
        """
        Calculates a mapping for the units based on features like distance.
        
        The units will be compared pare-wise and sequential.
        
        **Arguments**
        
            *data* (:class:`src.neodata.NeoData`):
                This object is needed to get the data 
                which will be used to compare the units.
            
        """
        wave_length = data.get_wave_length()

        for i in range(len(data.blocks) - 1):
            sessions = np.zeros((sum(data.total_units_per_block), 2, wave_length))

            for j, val in enumerate(storage.get_map().mapping[i]):
                if val != 0:
                    runit = self.get_realunit(i, j, data)
                    avg = data.get_data("average", runit)
                    sessions[j][0] = avg / np.max(avg)
                else:
                    sessions[j][0] = np.zeros(wave_length)

            for j, val in enumerate(storage.get_map().mapping[i + 1]):
                if val != 0:
                    runit = self.get_realunit(i + 1, j, data)
                    avg = data.get_data("average", runit)
                    sessions[j][1] = avg / np.max(avg)
                else:
                    sessions[j][1] = np.zeros(wave_length)

            distances = cdist(sessions[:, 0], sessions[:, 1], metric='euclidean')
            threshold = np.mean(distances[distances > 0])
            print(threshold)
            extend = 0
            exclude = []
            for j, val in enumerate(storage.get_map().mapping[i + 1]):
                print("Executing this in session {}".format(i))
                print("J: {}, Val: {}".format(j, val))

                if val != 0:
                    print(distances[j])

                    min_arg = np.argmin(distances[j])
                    print("Min Arg: {}".format(min_arg))

                    if min_arg == j:
                        pass
                    elif distances[j, min_arg] < threshold and (j, min_arg) not in exclude:
                        print("Swapping {} and {}".format(j, min_arg))
                        self.swap(i + 1, j, min_arg)
                        exclude.append((j, min_arg))
                        exclude.append((min_arg, j))
                    elif distances[j, min_arg] >= threshold:
                        print("Swapping {} and {}".format(j, data.total_units_per_block[i + 1] + extend))
                        self.swap(i + 1, j, data.total_units_per_block[i + 1] + extend)
                        extend += 1
                        print(extend)
                    else:
                        print("Logic flawed, check again!")
            print(exclude)
        storage.change_map()

    """
    def calculate_mapping(self, data, base):
        
        Calculates a mapping for the units based on features like distance.
        
        The units will be compared pare-wise and sequential.
        
        **Arguments**
        
            *data* (:class:`src.neodata.NeoData`):
                This object is needed to get the data 
                which will be used to compare the units.
        
        
        print("Map being calculated")
        #dis = {}
        #for each block except the last one
        for i in range(len(data.blocks) - 1):
            swapped1 = []
            swapped2 = []
            
            #do it so often that each real unit can find a partner
            for n in range(data.total_units_per_block[i]):
                distances = []

                #for each unit in block i
                for j in range(self.maximum_units):
                    if self.mapping[i][j] != 0:
                        unit1 = self.get_realunit(i, j, data)
                        y1 = data.get_data("average", unit1)[0]
                        
                        #for each unit in block i+1
                        for k in range(self.maximum_units):
                            if self.mapping[i+1][k] != 0:
                                unit2 = self.get_realunit(i+1, k, data)
                                y2 = data.get_data("average", unit2)[0]
                                #calculates the distance between the average waveforms
                                distance = np.linalg.norm(np.subtract(y2, y1))

                                #calculate cross correlation {
                                #calculates the inter-spike-interval
                                isi1 = data.get_data("units", unit1)[0]
                                isi2 = data.get_data("units", unit2)[0]
                                len1 = len(isi1)
                                len2 = len(isi2)
                                if len1 > len2:
                                    isi1 = isi1[:len2]
                                else:
                                    isi2 = isi2[:len1]
                                cor1 = np.corrcoef(y1, y2)
                                cor2 = np.corrcoef(isi1, isi2)
                                c = ((cor1 + cor2) / 2.0)[1][0]
                                #print("unit {} vs. unit {} = {}, crosscorr = {}".format(j, k, distance, c))
                                # }

                                #calculate norm {
                                y = y1 + y2
                                isi = isi1 + isi2
                                av1 = np.mean(y)
                                std1 = np.std(y)
                                av2 = np.mean(isi)
                                std2 = np.std(isi)
                                yn1 = (y1 - av1) / std1
                                yn2 = (y2 - av1) / std1
                                isin1 = (isi1 - av2) / std2
                                isin2 = (isi2 - av2) / std2
                                #fig = plt.figure("dist: {}; corr: {}".format(distance, c))
                                #fig.add_subplot(111)
                                #plt.plot(yn1)
                                #plt.plot(yn2)
                                #plt.plot(isin1)
                                #plt.plot(isin2)
                                #plt.show()
                                #print("unit {} vs. unit {} = {}, y = {} {}, isi = {} {}".format(j, k, distance,
                                #                                                                yn1[:2], yn2[:2],
                                #                                                                isin1[:2], isin2[:2]))
                                #  }

                                if j not in swapped1 and k not in swapped2:
                                    distances.append((j, k, distance))
                                    #dis[c] = distance
                if distances:
                    #finds the min of the distances
                    mini = min(distances, key=lambda x: x[2])
                    #swap only if distance is under a threshold
                    if mini[2] < 200:
                        #swaps the units to have them in the same unit row                
                        self.swap(i+1, mini[0], mini[1])
                        swapped1.append(mini[0])
                        swapped2.append(mini[0])
                    #otherwise search for an empty row and swap there
                    #but only if the units are in the same row 
                    else:
                        if mini[0] == mini[1]:
                            for u, v in enumerate(self.mapping[i+1]):
                                testing = True
                                for l in range(i+2):
                                    if self.mapping[l][u] != 0:
                                        testing = False
                                if testing:
                                    self.swap(i+1, mini[1], u)
                                    swapped1.append(mini[0])
                                    swapped2.append(u)

        #plt.plot(dis.keys(), dis.values(), "o")
        #plt.show()
    """

    def reset(self):
        """
        Resets the mapping.
        
        """
        self.mapping = []
        self.visible = []
        self.active = []
        self.total_units = 0
