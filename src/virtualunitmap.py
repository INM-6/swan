"""
Created on Dec 12, 2013

@author: Christoph Gollan

In this module you can find the :class:`VirtualUnitMap` which is used to map
real units to virtual units. The virtual units can be swapped to have the 
same units in the same row.
"""
import numpy as np
from scipy.spatial.distance import cdist

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
            
        """
        print("Map being calculated")
        
        for i in range(len(data.blocks) - 1):
            sessions = np.zeros((sum(data.nums), 2, data.wave_length))
            
            for j, val in enumerate(storage.get_map().mapping[i]):
                if val is not 0:
                    runit = self.get_realunit(i, j, data)
                    sessions[j][0] = data.get_data("average", runit)
            
            for j, val in enumerate(storage.get_map().mapping[i+1]):
                if val is not 0:
                    runit = self.get_realunit(i+1, j, data)
                    sessions[j][1] = data.get_data("average", runit)
            
            distances = cdist(sessions[:, 0], sessions[:, 1], metric='euclidean')
            threshold = np.mean(distances[distances > 0])
            print(threshold)
            extend = 0
            exclude = []
            for j, val in enumerate(storage.get_map().mapping[i+1]):
                print("Executing this at {}, {}".format(i, j))
                print(j, val)
                if val is not 0:
                    print(distances[j, j:])
                    min_arg = np.argmin(distances[j, j:]) + j
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
    
