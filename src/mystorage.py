"""
Created on Apr 4, 2014

@author: Christoph Gollan

In this module you can find the :class:`MyStorage`. It inherits
from :class:`stg.storage.Storage`.

This class represents the storage layer. It manages the project files,
the data loading and the data writing.

The data loading is called in the :class:`Task` which is a thread.
"""
from os import remove
from os.path import splitext, basename, exists, split, join
from PyQt5.QtCore import QThread, QMutex, QObject, pyqtSignal
from PyQt5.QtGui import QApplication
from stg.storage import Storage
from stg.project import Project
from src.neodata import NeoData
from src.virtualunitmap import VirtualUnitMap


class Task(QThread):
    """
    A thread that loads the data.
    
    **Arguments**
        
        *data* (:class:`src.neodata.NeoData`):
            Is needed because it has the loading routine.
        *files* (list of string):
            The list containing the file paths.
        *channel* (integer):
            The channel that has to be loaded.
                
    """
    
    #mutex = QMutex()
    
    def __init__(self, data, files, channel):
        """
        **Properties**
        
            *data* (:class:`src.neodata.NeoData`):
                Is needed because it has the loading routine.
            *files* (list of string):
                The list containing the file paths.
            *channel* (integer):
                The channel that has to be loaded.
        
        """
        super(QThread, self).__init__()
        self.data = data
        self.files = files
        self.channel = channel
    
    def run(self):
        """
        Runs the loading routine of 
        the :class:`src.neodata.NeoData` object.
        
        """
        #try:
            #Task.mutex.lock()
        self.data.load(self.files, self.channel)
        #finally:
            #Task.mutex.unlock()
        

class MyStorage(Storage, QObject):
    """
    The storage class.
        
    It manages the project files and the data.
    
    **Arguments**
    
        *_program_dir* (string):
            The path to the main program. It has to end with the top-level directory swan.
        *cache_dir* (string):
            The default path of the cache directory.
        
    """

    progress = pyqtSignal(int)
    """
    Progress signal to let the main program know
    how far the loading progress is.
    
    """
    
    def __init__(self, program_dir, cache_dir):
        """
        **Properties**
        
            *_project* (:class:`stg.project.Project`):
                The project object that manages project files.
            *_PNAME* (string):
                The default project name.
            *_program_dir* (string):
                The path to the main program. It has to end with the top-level directory swan.
            *_cache_dir* (string):
                The path to the cache directory.
            *_copy_i* (integer):
                An integer that is used to create the project name.
                If the default project name already exists, it will be changed by using
                this attribute.
            *_loading* (boolean):
                Whether or not something is loading at the moment.
        
        """
        super(MyStorage, self).__init__()
        super(QObject, self).__init__()
        
        #properties{
        self._project = None
        self._PNAME = "swan"
        self._program_dir = program_dir
        self._cache_dir = cache_dir
        self._copy_i = 1
        self._loading = False
        #}
        
        self.store("channel", 1)
        self.store("lastchannel", 1)
        
    
    def set_cache_dir(self, cache_dir):
        """
        Lets you change the cache directory.
        
        **Arguments**
    
            *cache_dir* (string):
                The new cache location.
        
        """
        self._cache_dir = cache_dir
        try:
            self.get_data().cdir = cache_dir
        except:
            pass
        
    def load_project(self, prodir, proname, channel, files=None):
        """
        Creates or loads a new project.
        
        It creates the project files and loads data from the
        project file or the given file list.
        
        **Arguments**
        
            *prodir* (string):
                The path to the project directory.
            *proname* (string):
                The project name. Will be the name of the project file.
            *channel* (integer):
                The current channel. It is just used to set the channel.
                No loading will be done here.
            *files* (list of string or None):
                The list containing the file paths.
                Set it to None if you want to load from a file.
                Default: None.
        
            **Returns**: boolean
                If the project loading succeeded. 
        
        """
        loadFiles = files is None
        
        #return if there is nothing to load
        if not loadFiles and len(files) == 0:
            return False
        
        #if something goes wrong, you can back to the old project
        tmp = self._project
        
        self.set_project(prodir)
        
        if not loadFiles:
            #checking if standard name is already existing
            #if so, the name will be changed 
            
            while (True):
                try:
                    self._project.add_file(self.get_pro_name(proname))
                    break
                except:
                    istr = str(self._copy_i)
                    l = len(istr)
                    if proname.endswith(")"):
                        proname = (splitext(proname)[0])[:-2-l] + "(" + istr + ")"
                    else:
                        proname = (splitext(proname)[0]) + "(" + istr + ")"
                    self._copy_i += 1
            
            self._project.add_file(self.get_vum_name(proname))
        else:
            self._project.add_file(self.get_pro_name(proname), None, False)
            self._project.add_file(self.get_vum_name(proname), None, False)
        
        try:
            #reading the file
            if loadFiles:
                files = self.read_file()
            self.store("files", files)
            
            #free the old data object
            try:
                dataToDelete = self.get_data()
                dataToDelete.delete_IOs()
            except:
                pass
            
            #creating the important NeoData object
            neodata = NeoData(self._cache_dir)
            neodata.progress.connect(self.setProgress)
            self.store("data", neodata)
            
            self.set_channel(channel)
            
            #create or load the dict for the virtual unit mappings
            #create or load a second one for backup
            try:
                vum_all = self.load_map()
                vum_all2 = self.load_map()
            except IOError:
                vum_all = {}
                vum_all2 = {}
            self.store("vum_all", vum_all)  
            self.store("vum_all2", vum_all2)
            
            self.save_file()
                
            return True
        except IOError:
            self._project = tmp
            return False
        
    def save_project(self):
        """
        Saves the project and the map.
        
        """
        if self.has_project():
            self.save_file()
            self.save_map()
    
    def save_project_as(self, filename):
        """
        Saves the project and the map but it changes the name of both of them.
        Existing project files with the same name will be removed.
        
        **Arguments**
        
            *filename* (string):
                The new filename.
        
        """
        (fdir, fname) = split(filename)
        if exists(filename):
            remove(filename)
        vumname = self.get_vum_name(fname)
        vumfull = join(fdir, vumname)
        if exists(vumfull):
            remove(vumfull)
        self.set_project(fdir)
        fname = self.get_pro_name(fname)
        self._project.add_file(fname)
        self._project.add_file(vumname)
        self.save_project()
                
    def set_project(self, prodir):
        """
        Creates and sets a new project.
        
        **Arguments**
        
            *prodir* (string):
                The path to the project directory.
        
        """
        p = Project(self._PNAME, prodir, False)
        self._project = p
        
    def set_channel(self, channel):
        """
        Sets the new channel and the last channel.
        
        **Arguments**
        
            channel (integer):
                The new channel.
        
        """
        last = self.get("channel")
        self.store("channel", channel)
        self.store("lastchannel", last)
    
    def get_project_path(self):
        """
        Wrapper for getting the absolute path to the project file.
        
            **Returns**: string
                The absolute path to the project file.
        
        """
        return self._project.get_file_path(self._project.get_file_list()[0])
    
    def get_map_path(self):
        """
        Wrapper for getting the absolute path to the map file.
        
            **Returns**: string
                The absolute path to the map file.
        
        """
        return self._project.get_file_path(self._project.get_file_list()[1])

    def has_project(self):
        """
            **Returns**: boolean
                If there is a project loaded.
        
        """
        return self._project is not None
    
    def get_pro_name(self, proname):
        """
        **Arguments**
        
            *proname* (string):
                The project file name.
        
            **Returns**: string
                A project file name with a .txt extension if it 
                was not already there.
        
        """
        if proname.endswith(".txt"):
            return proname
        else:
            proname = proname + ".txt"
            return proname
    
    def get_vum_name(self, proname):
        """
        **Arguments**
        
            *proname* (string):
                The project file name.
        
            **Returns**: string
                A map file name with a .vum extension that belongs
                to the project file name.
        
        """
        proname = self.get_pro_name(proname)
        proname = splitext(proname)[0]
        vumname = proname + "_vum.vum"
        return vumname
    
    def get_channel(self):
        """
        Wraps the channel getter.
        
            **Returns**: integer
                The channel.
        
        """
        return self.get("channel")
    
    def get_last_channel(self):
        """
        Wraps the lastchannel getter.
        
            **Returns**: integer
                The last channel.
        
        """
        return self.get("lastchannel")
    
    def get_files(self, asStr=False):
        """
        Wraps the files getter.
        
        **Arguments**
        
            *asStr* (boolean):
                If you want a string containing the file paths instead.
                Default: False.
        
            **Returns**: list of string or string:
                The file list or a string with the file paths.
        
        """
        files = self.get("files")
        if asStr:
            return "\n".join(files)
        return files
    
    def get_map(self):
        """
        Wraps the map getter.
        
            **Returns**: :class:`src.virtualunitmap.VirtualUnitMap`
                The current virtual unit mapping.
        
        """
        return self.get("vum")
    
    def get_data(self):
        """
        Wraps the data getter.
        
            **Returns**: :class:`src.neodata.NeoData`
                The current data object.
        
        """
        return self.get("data")

    def get_mappings(self):
        """
        Getter for the virtual unit map container dictionary.

            **Returns**: dictionary
                All saved virtual unit maps.

        """
        return self.get("vum_all")

    def get_map_backup(self):
        """
        Getter for the map backup.
        
            **Returns**: :class:`src.virtualunitmap.VirtualUnitMap`
                The map backup loaded from the backup dictionary.
        
        """
        channel = self.get_channel()
        name = "vum"+str(channel)
        try:
            vum_all2 = self.get("vum_all2")
            vum = vum_all2[name]
            return vum
        except KeyError:
            return None
        
    def get_tooltips(self):
        """
        Creates tool tips for the overview.
        
        **Returns**: list of string:
                The tool tips.
        
        """
        tips = []
        vum = self.get_map()
        files = self.get_files()
        data = self.get_data()
        spike_nums = []
        c = 0
        for i in range(len(data.blocks)):
            spike_nums.append([])
            for j in range(vum.n_):
                runit = vum.get_realunit(i, j, data)
                if "noise" not in runit.description.split() and "unclassified" not in runit.description.split():
                    spike_nums[c].append(data.get_data("n_spikes", runit))
                else:
                    spike_nums[c].append(0)
            c += 1
            
        c = 0
        for f, l, n in zip(files, vum.mapping, spike_nums):
            tips.append([])
            for u, v in zip(l, n):
                tooltip = "File: {}\nUnit: {}\nWaveforms: {}".format(basename(f), u, v)
                tips[c].append(tooltip)
            c += 1
        return tips
        
    def recalculate(self):
        """
        Recalculates the mapping and sets it.
        
        """
        vum = self.get_map()
#        vum.reset()
        data = self.get_data()
#        vum.set_initial_map(data.nums)
        vum.calculate_mapping(data)
        self.change_map()
    
    def revert(self):
        """
        Reverts the current mapping to the last saved one.
        
        """
        vumap = self.get_map()
        vumap.reset()
        vum = self.get_map_backup()
        data = self.get_data()
        if vum is not None:
            vumap.set_map(data.nums, vum)
        else:
            vumap.set_initial_map(data.nums)
        self.save_map()
        
    def swap(self, m, n1, n2):
        """
        Swaps the mapping of two entries in 
        the :class:`src.virtualunitmap.VirtualUnitMap`.
        
        **Arguments**
        
            *m* (integer):
                The session index.
            *n1* (integer):
                The unit index 1.
            *n2* (integer):
                The unit index 2.
        
        """
        self.get_map().swap(m, n1, n2)
        self.change_map()
    
    def load_channel(self, channel):
        """
        Loads a channel.
        
        **Arguments**
        
            *channel* (integer):
                The channel that should be loaded.
        
            **Returns**: tuple of integer
                The number of unit rows and the number of sessions.
        
        """
        self.set_channel(channel)
        data = self.get("data")
        files = self.get("files")
        
        #loading with a thread
        t = Task(data, files, channel)
        t.start()
        while t.isRunning():
            self._loading = t.isRunning()
            QApplication.processEvents()
        self._loading = False
        
        vum_all = self.get("vum_all")
        name = "vum" + str(channel)
        
        vumap = VirtualUnitMap()
        
        #load a mapping or set the default one
        try:
            vum = vum_all[name]
            vumap.set_map(data.nums, vum)
        except KeyError:
            vumap.set_initial_map(data.nums)
            
        self.store("vum", vumap)
        
        return sum(data.nums), len(vumap.mapping)
            
    def read_file(self):
        """
        Reads the project file and returns the lines without the
        newline character.
        
            **Returns**: list of string
                The input lines.
        
        """
        files = []
        try:
            with open(self.get_project_path(), "r") as fn:
                for f in fn:
                    if f.endswith("\n"):
                        files.append(f[:-1])
                    else:
                        files.append(f)
            return files
        except:
            raise IOError("Could not read project file")
        
    def save_file(self):
        """
        Writes the file paths of the loaded sessions to a file.
        
        """
        files = self.get("files")
        data = "\n".join(files)
        Storage.write(self.get_project_path(), data)
    
    def save_map(self):
        """
        Saves the dictionary containing all virtual unit mappings.
        
        """
        self.change_map()
        vum_all = self.get("vum_all")
        Storage.write(self.get_map_path(), vum_all, "pickle")
        self.store("vum_all2", self.load_map()) 
            
    def load_map(self):
        """
        Loads the dictionary containing all virtual unit mappings.
        
            **Returns**: dictionary
                The loaded map.
        
        """
        try:
            vum = Storage.read(self.get_map_path(), "pickle")
            return vum
        except:
            raise IOError("Could not read VUMap")
    
    def check_map(self, vum, files):
        """
        Checks if the map is correct.
        
        **Arguments**
        
            *vum* (:class:`src.virtualunitmap.VirtualUnitMap`):
                The mapping object that has to be checked.
            *files* (list of string):
                The file list containing the session names that
                should be in the map, too.
        
            **Returns**: boolean
                If the map is correct.
        
        """
        if not vum["files"] == files:
            return False
        return True
    
    def change_map(self):
        """
        Changes the current loaded map without saving it.
        
        """
        channel = self.get("channel")
        vum_all = self.get("vum_all")
        files = [basename(f) for f in self.get("files")]
        vum = self.get("vum")
        d = {}
        d["channel"] = channel
        
        for i in range(1, len(vum.mapping[0])+1):
            d[i] = []
        for name, vus in zip(files, vum.mapping):
            for i in range(len(vus)):
                d[i+1].append((basename(name), vus[i]))
        
        name = "vum" + str(channel)
        vum_all[name] = d
        vum_all["files"] = files

    def is_loading(self):
        """
        Getter for the loading information.
        
            **Returns**: boolean
                If there is something loading at the moment.
        
        """
        return self._loading

    def setProgress(self, i):
        """
        Emits a signal to the parent widget (the main program) 
        containing the loading progress.
        
        **Arguments**
        
            *i* (integer):
                The loading progress.
        
        """
        self.progress.emit(i)
