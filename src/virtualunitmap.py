"""
Created on Dec 12, 2013

@author: Christoph Gollan

In this module you can find the :class:`VirtualUnitMap` which is used to map
real units to virtual units. The virtual units can be swapped to have the 
same units in the same row.
"""
import numpy as np
np.set_printoptions(linewidth=150)
from scipy.spatial.distance import cdist
from copy import deepcopy

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
            *n_* (integer):
                The summary of the length of all unit lists.
            *colors* (list of tuple of integer):
                Contains colors for plotting the units in different colors.
                Format: (R, G, B) RGB = 0..255
            *coln* (integer):
                The length of the colors list.
        
        """
        self.mapping = []
        self.visible = []
        self.n_ = 0
        self.colors = [ (31,	   119,	180),
                        (255,   127,	14),
                        (44,	   160,	44),
                        (214,   39, 	40),
                        (148,   103,	189),
                        (140,   86, 	75),
                        (227,   119,	194),
                        (127,   127,	127),
                        (188,   189,	34),
                        (158,   218,	229),
                        (23,	   190,	207),
                        (174,   199,	232),
                        (255,   187,	120),
                        (152,   223,	138),
                        (255,   152,	150),
                        (197,   176,	213),
                        (196,   156,	148),
                        (247,   182,	210),
                        (199,   199,	199),
                        (219,   219,	141)]
        self.coln = len(self.colors)
        
        
    #### general methods ####    
        
    def set_initial_map(self, data):
        """
        Sets the default mapping.
        
        **Arguments**
        
            *nums* (list of integer):
                The number of units per block.
        
        """
        
        n_ = sum(data.nums)
        self.n_ = n_
        vmap = []
        for i in range(len(data.blocks)):
            vmap.append([])
            count = 1
            for j in range(self.n_):
                try:
                    unit_description = data.blocks[i].channel_indexes[0].units[j].description.split()
                    
                    if "unclassified" in unit_description:
                        vmap[i].append(0)
                    elif "noise" in unit_description:
                        vmap[i].append(0)
                    else:
                        vmap[i].append(count)
                        count += 1
                except:
                    vmap[i].append(0)
        
        self.mapping = vmap
        self.visible = [True for i in range(n_)]
        
    def set_map(self, nums, vum):
        """
        Sets the mapping given from the VUMap.
        
        **Arguments**
        
            *nums* (list of integer):
                The number of units per block.
            *vum* (dictionary):
                A dictionary containing the mappings and other information.
        
        """
        n_ = sum(nums)
        self.n_ = n_
        
        n = len(nums)
        
        for i in range(n):
            self.mapping.append([])
        
        for l in vum.values():
            if type(l) == list:
                for i in range(n):
                    unit = l[i][1]
                    self.mapping[i].append(unit)
                
        self.visible = [True for i in range(n_)]
        
    def get_realunit(self, i, j, data):
        """
        Returns the real unit for a virtual unit.
        
        **Arguments**
        
            *i* (integer):
                The session index.
            *j* (integer):
                The unit index.
            *data* (:class:`src.neodata.NeoData`):
                The data object that contains the real unit.
            
            **Returns**: :class:`neo.core.unit.Unit`
                The real unit.
        
        """
        vunit = self.mapping[i][j]
        if "unclassified" not in data.blocks[i].channel_indexes[0].units[0].description.split():
            runit = data.blocks[i].channel_indexes[0].units[vunit - 1]
        else:
            runit = data.blocks[i].channel_indexes[0].units[vunit]
        #runit = data.blocks[i].channel_indexes[0].units[vunit]
        return runit
    
    def swap(self, m, n1, n2):
        """
        Swaps two virtual units.
        
        **Arguments**
        
            *m* (integer):
                The session index.
            *n1* (integer):
                The unit index 1.
            *n2* (integer):
                The unit index 2.
        
        """
        tmp = self.mapping[m][n2]
        self.mapping[m][n2] = self.mapping[m][n1]
        self.mapping[m][n1] = tmp
        
    def set_visible(self, i, visible=True):
        """
        Sets a unit row as visible or not.
        
        **Arguments**
        
            *i* (integer):
                The unit row index.
            *visible* (boolean):
                Whether or not the unit row should be visible.
                Default: True.
        
        """
        self.visible[i] = visible
        
    def get_color(self, i, mpl=False, layer=None):
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
        if i >= self.coln:
            return (0, 0, 0)
        if mpl:
            col = (self.colors[i][0]/255., self.colors[i][1]/255., self.colors[i][2]/255.)
            if layer == "standard deviation":
                col = (col[0]/2., col[1]/2., col[2]/2.)
            elif layer == "session":
                col = (col[0]/2., col[1]/2., col[2]/2.)
        else:
            col = self.colors[i]
        return col
    
    def calculate_mapping(self, data, storage):
        """
        Calculates a mapping for the units based on features like distance.
        
        The units will be compared pare-wise and sequential.
        
        **Arguments**
        
            *data* (:class:`src.neodata.NeoData`):
                This object is needed to get the data 
                which will be used to compare the units.
            
            *storage* (:class:`stg.mystorage.MyStorage`):
                The class which handles the data and the project files.
        
        """
        print("Map being calculated")
        swaps = 0
        # Retrieve mapping from storage
        mapping = np.array(deepcopy(storage.get_map().mapping)).T
        
        # loop over columns/sessions
        for s in range(mapping.shape[1]):
            # initialize array of mean waveform max amplitudes
            averages = np.zeros((mapping.shape[0]))
            
            # loop over rows/units
            for j in range(len(averages)):
                # ignore zeros in the map (correspond to non-existent units)
                if mapping[j][s] != 0:
                    # Retrieve unit
                    runit = self.get_realunit(s, j, data)
                    # Retrieve mean waveform for the unit
                    wave = data.get_data("average", runit)
                    # Store max amplitude of mean waveform
                    averages[j] = np.amax(abs(wave))
            
            #
            # Sort the units in each session by max amplitude of mean waveform
            # and swaps the corresponding units in the storage.
            #
            
            # loop over rows/units
            for i in range(len(averages)):
                # retrieve index of max value in session
                max_index = np.argmax(averages[i:]) + i
                if max_index != i:
                    storage.swap(s, i, max_index)
                    tmp = averages[max_index]
                    averages[max_index] = averages[i]
                    averages[i] = tmp
                    swaps += 1
        
        # Refresh the mapping using the values in storage
        mapping = np.array(deepcopy(storage.get_map().mapping)).T
        # Initialize an array shaped like "mapping" and set all values to np.nan
        history = np.zeros_like(mapping, dtype = np.float)
        history[history == 0] = None
        #print("Initial Mapping: {}".format(mapping))
        
        # Loop over all columns/sessions except the last one
        for i in range(mapping.shape[1] - 1):
            # Loop over all rows/units
            for j in range(mapping.shape[0]):
                # ignore zeros in the map (correspond to non-existent units)
                if mapping[j][i] > 0: # to avoid errors in float comparison
                    # Choose (j, i)th unit as the actor and obtain it's mean waveform
                    runit_actor = self.get_realunit(i, j, data)
                    actor = data.get_data("average", runit_actor)
                    
                    # Initialize matrix to store distances to the actor unit
                    distances = np.zeros((mapping.shape[0], mapping.shape[1]))
                    
                    # Loop over all columns/sessions again
                    for k in range(mapping.shape[1]):
                        # Loop over all rows/units again
                        for l in range(mapping.shape[0]):
                            # Choose (l, k)th units as the support and obtain it's mean waveform
                            runit_support = self.get_realunit(k, l, data)
                            support = data.get_data("average", runit_support)
                            #
                            # Calculate and store the Euclidean distance to
                            # support from actor (multiplied by a distance
                            # factor)
                            #
                            distances[l][k] = np.linalg.norm(np.subtract(actor, support)) #* np.exp(abs(k-i))
                            
#                            if mapping[l][k] > 0:
#                                history[l][k] = distances[l][k]
                    
                    #print("Distances:\n {}\n".format(distances))
                    
                    #
                    # Extract the dataset corresponding to all distance measures
                    # with non-zero mapping values and calculate the reject threshold
                    #
                    threshold_dataset = distances[mapping > 0]
                    dataset_reject_threshold = np.mean(threshold_dataset)
                    #dataset_std = np.std(threshold_dataset)
                    #threshold_range_L = threshold_mean + 0.5 * threshold_std
                    #dataset_reject_threshold = dataset_mean + 0.5 * dataset_std
                    
                    #print("Threshold: {}\n".format(dataset_reject_threshold))
                    
                    # 
                    # The loop is the main part of the mapping algorithm, which
                    # uses the distances between units to rearrange (swap) them.
                    #
                    
                    # Generate loop range for the loop
                    if mapping.shape[1] < 10:
                        loop_range = range(mapping.shape[1])
                    else:
                        loop_range = [x for x in range(i+9) if (i+x) <= mapping.shape[1]]
                    
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
                                storage.swap(k, min_arg, j)
                                mapping = np.array(deepcopy(storage.get_map().mapping)).T
                                swaps += 1
                                #print("Swapped {} with {} on day {}\nDistance: {}\n".format(j, min_arg, k, history[j][k]))
                            else:
                                # If the unit has been swapped earlier, swap only if
                                # the new distance is less than the old distance
                                prev_dist = history[min_arg][k]
                                curr_dist = distances[min_arg][k]
                                if curr_dist < prev_dist:
                                    history[j][k] = distances[min_arg][k]
                                    storage.swap(k, min_arg, j)
                                    mapping = np.array(deepcopy(storage.get_map().mapping)).T
                                    swaps += 1
                                    #print("Swapped {} with {} on day {}\nDistance: {}\nPrev Dist: {}, Curr Dist: {}\n".format(j, min_arg, k, history[j][k], prev_dist, curr_dist))
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
                            storage.swap(k, first_zero, min_arg)
                            history[min_arg][k] =  np.nan
                            mapping = np.array(deepcopy(storage.get_map().mapping)).T
                            swaps += 1
                            #print("Swapped {} with empty plot {} on day {}".format(min_arg, first_zero, k))
                            #print("Mapping: {}".format(mapping))
                        else:
                            # If none of the above cases yield true, something is wrong
                            print("Exception reached")
                            print(distances)
        print("Total swaps: {}\n".format(swaps))
        
    def calculate_mapping_bu_2(self, data, storage):
        """
        Calculates a mapping for the units based on features like distance.
        
        The units will be compared pare-wise and sequential.
        
        **Arguments**
        
            *data* (:class:`src.neodata.NeoData`):
                This object is needed to get the data 
                which will be used to compare the units.
            
        """
        print("Map being calculated")
        
        for i in range(len(data.blocks) - 1):
            sessions = np.zeros((sum(data.nums), 2, data.wave_length))
            
            for j, val in enumerate(storage.get_map().mapping[i]):
                if val is not 0:
                    runit = self.get_realunit(i, j, data)
                    #sessions[j][0] = data.get_data("average", runit)
                    avg = data.get_data("average", runit)
                    sessions[j][0] = avg/np.max(avg)
                else:
                    sessions[j][0] = np.zeros(38)
            
            for j, val in enumerate(storage.get_map().mapping[i+1]):
                if val is not 0:
                    runit = self.get_realunit(i+1, j, data)
                    #sessions[j][1] = data.get_data("average", runit)
                    avg = data.get_data("average", runit)
                    sessions[j][1] = avg/np.max(avg)
                else:
                    sessions[j][1] = np.zeros(38)
            
            distances = cdist(sessions[:, 0], sessions[:, 1], metric='euclidean')
            threshold = np.mean(distances[distances > 0])
            print(threshold)
            extend = 0
            exclude = []
            for j, val in enumerate(storage.get_map().mapping[i+1]):
                print("Executing this in session {}".format(i))
                print("J: {}, Val: {}".format(j, val))

                if val is not 0:
                    print(distances[j])
                    
                    min_arg = np.argmin(distances[j])
                    print("Min Arg: {}".format(min_arg))
                    
                    if min_arg == j:
                        pass
                    elif distances[j, min_arg] < threshold and (j, min_arg) not in exclude:
                        print("Swapping {} and {}".format(j, min_arg))
                        storage.swap(i+1, j, min_arg)
                        exclude.append((j, min_arg))
                        exclude.append((min_arg, j))
                    elif distances[j, min_arg] >= threshold:
                        print("Swapping {} and {}".format(j, data.nums[i+1] + extend))
                        storage.swap(i+1, j, data.nums[i+1] + extend)
                        extend+=1
                        print(extend)
                    else:
                        print("Logic flawed, check again!")
            print(exclude)
        
    
    def calculate_mapping_bu(self, data, storage):
        """
        Calculates a mapping for the units based on features like distance.
        
        The units will be compared pare-wise and sequential.
        
        **Arguments**
        
            *data* (:class:`src.neodata.NeoData`):
                This object is needed to get the data 
                which will be used to compare the units.
            
        """
        print("Map being calculated")
        #dis = {}
        #for each block except the last one
        for i in range(len(data.blocks) - 1):
            swapped1 = []
            swapped2 = []
            
            #do it so often that each real unit can find a partner
            for n in range(data.nums[i]):
                distances = []

                #for each unit in block i
                for j in range(self.n_):
                    if self.mapping[i][j] != 0:
                        unit1 = self.get_realunit(i, j, data)
                        y1 = data.get_data("average", unit1)[0]
                        
                        #for each unit in block i+1
                        for k in range(self.n_):
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
    
    def reset(self):
        """
        Resets the mapping.
        
        """
        self.mapping = []
        self.visible = []
        self.n_ = 0
    
