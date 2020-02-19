"""
Created on Apr 3, 2014

@author: Christoph Gollan
"""
try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl


class StorageError(ValueError):
    pass


class Storage(object):
    """
    A basic base class for storing objects
    and read/write files.

    """
    
    def __init__(self):
        """
        **Properties**
        
            *_data* (dictionary):
                The dictionary containing
                all objects.
        
        """
        self._data = {}
    
    
    def store(self, name, obj):
        """
        Stores an object.
        
        **Arguments**
        
            *name* (string):
                The key name to access this
                object.
            *obj* (object):
                The object to store.
        
        """
        self._data[name] = obj
        
    def remove(self, name):
        """
        Removes an object from the base.
        
        **Arguments**
        
            *name* (string):
                The key name under which the object
                is accessible.
        
        """
        if self.is_stored(name):
            del self._data[name]
    
    def is_stored(self, name):
        """
        Checks if the given name is stored.
        
        **Arguments**
        
            *name* (string):
                The key name under which the object
                is accessible.
                
            **Returns**: boolean
                Whether there is an entry or not.
        
        """
        try:
            self.get(name)
            return True
        except StorageError:
            return False
    
    def get(self, name):
        """
        Returns the value for the given name.
        
        **Arguments**
        
            *name* (string):
                The key name under which the object
                is accessible.
        
            **Returns**: object
                The object that is stored.
                
            **Raises**: :class:`StorageError`
                If the key doesn't exist.
                
        """ 
        try:
            value = self._data[name]
            return value
        except KeyError:
            raise StorageError("No value for {}".format(name))
        
    
    @staticmethod 
    def write(filename, data, method="text"):
        """
        Writes data to a file.
        
        **Arguments**
        
            *filename* (string):
                The file name where to write.
            *data* (object):
                The data to write.
            *method* (string):
                The method that should be used.
                Default: text.
                
                Supported are:
                
                ==========  ========================
                Name        Description
                ==========  ========================
                text        Writing to a text file
                pickle      Writing to a pickle file
                ==========  ========================
                
            **Raises**: :class:`StorageError`
                If the method is not supported.
        
        """
        if method == "text":
            mode = "w"
            with open(filename, mode) as f:
                f.write(data)
        elif method == "pickle":
            mode = "wb"
            with open(filename, mode) as f:
                pkl.dump(data, f)
        else:
            raise StorageError("Writing method {} not supported".format(method))
              
    @staticmethod           
    def read(filename, method="text"):
        """
        Reads data from a file.
        
        **Arguments**
        
            *filename* (string):
                The file name where to read from.
            *method* (string):
                The method that should be used.
                Default: text.
                
                Supported are:
                
                ==========  ========================
                Name        Description
                ==========  ========================
                text        Reading a text file
                pickle      Reading a pickle file
                ==========  ========================
                
            **Returns**: object
                The data that was read.
                
            **Raises**: :class:`StorageError`
                If the method is not supported.
        
        """
        if method == "text":
            mode = "r"
            with open(filename, mode) as f:
                data = f.read()
        elif method == "pickle":
            mode = "rb"
            with open(filename, mode) as f:
                data = pkl.load(f)
        else:
            raise StorageError("Reading method {} not supported".format(method))
        return data
        
        
        
        
        
        
