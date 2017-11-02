"""
Created on Apr 3, 2014

@author: Christoph Gollan
"""
from os import mkdir, remove, rmdir
from os.path import join, isdir, exists, abspath


class ProjectError(ValueError):
    pass


class Project(object):
    """
    A simple project class for managing
    project files in applications.
    
    **Arguments**
            
            *pname* (string):
                The name of the project.
            *pdir* (string):
                The directory where the
                project is located.
            *create_dir* (boolean):
                Whether or not a directory under
                the given name should be created.    

    """

    def __init__(self, pname, pdir, create_dir):
        """
        **Properties**
            
            *_pname* (string):
                The name of the project.
            *_pdir* (string):
                The directory where the
                project is located.
            *_isDir* (boolean):
                If True, a directory under
                the given name will be created.
            *_sdirs* (dictionary):
                Maps the sub-directories to the file lists.
            
        """
        self._pname = pname
        self._pdir = pdir
        self._isDir = create_dir
        self._sdirs = {}
        
        self._sdirs["default"] = []
        
        if create_dir:
            mkdir(join(pdir, pname))
            
    
    def get_name(self):
        """
        Returns the project name.
        
            **Returns**: string
        
        """
        return self._pname
    
    def get_dir(self):
        """
        Returns the project's directory.
        
            **Returns**: string
        
        """
        return self._pdir
    
    def is_dir(self):
        """
        Returns True if the project is
        a directory, otherwise False.
        
            **Returns**: boolean
        
        """
        return self._isDir
        
    def get_full_name(self):
        """
        Returns the absolute path to
        the project.

            **Returns**: string

        """
        return abspath(join(self._pname, self._pdir))
    
    def get_file_path(self, filename, sdir=None):
        """
        Returns the absolute path to a file.
        
        **Arguments**
        
            *filename* (string):
                The file name.
            *sdir* (string or None):
                The sub-directory where the file 
                is located.
                Default: None.

            **Returns**: string
        
        """
        if sdir is None:
            sdir = "default"
            if self._isDir:
                fn = join(self._pdir, self._pname, filename)
            else:
                fn = join(self._pdir, filename)
        else:
            if self._isDir:
                fn = join(self._pdir, self._pname, sdir, filename)
            else:
                fn = join(self._pdir, sdir, filename)
        return abspath(fn)
    
    def get_subdir_path(self, sdir):
        """
        Returns the absolute path to a sub-directory.
        
        **Arguments**
        
            *sdir* (string):
                The sub-directory.
                
            **Returns**: string                
        
        """
        if sdir is None or sdir == "default":
            sn = join(self._pdir, self._pname)
        if self._isDir:
            sn = join(self._pdir, self._pname, sdir)
        else:
            raise ProjectError("Project is not a directory")
        return abspath(sn)
        
    def get_file_list(self, sdir=None):
        """
        Returns the file list to a given
        directory.
        
        **Arguments**
        
            *filename* (string):
                The file name.
            *sdir* (string or None):
                The sub-directory where the file 
                is located.
                Default: None.
                
            **Returns**: list of string
            
            **Raises**: :class:`ProjectError`
                If the sub-directory doesn't exist.
        
        """
        if sdir is None:
            return self._sdirs["default"]
        else:
            try:
                filelist = self._sdirs[sdir]
                return filelist
            except KeyError:
                raise ProjectError("Sub-directory {} doesn't exist".format(sdir))
            
    def has_file(self, filename, sdir=None):
        """
        Checks if the given file exists.
        
        **Arguments**
        
            *filename* (string):
                The file name.
            *sdir* (string):
                The sub-directory where the file 
                should be located.
                Default: None.
            
            **Returns**: boolean
                If the file exists.
        
        """
        try:
            return exists(self.get_file_path(filename, sdir))
        except ProjectError:
            return False
    
    def has_subdir(self, sdir):
        """
        Checks if the given path exists.
        
        **Arguments**
        
            *sdir* (string):
                The sub-directory.
                
            **Returns**: boolean
                If the sub-directory exists.
            
        """
        if sdir is None or sdir == "default":
            return False
        try:
            return isdir(self.get_subdir_path(sdir))
        except ProjectError:
            return False
    
    def add_subdir(self, sdir, create_dir=True):
        """
        Adds a sub-directory to the project.
        
        **Arguments**
        
            *sdir* (string):
                The sub-directory to add.
            *create_dir* (boolean):
                Whether or not you want to
                create the directory.
                Default: True.
                
            **Raises**: :class:`ProjectError`
                If the sub-directory already exists 
                or if the project is not a directory.
        
        """
        sn = self.get_subdir_path(sdir)
        if not isdir(sn) and create_dir:
            mkdir(sn)
            self._sdirs[sdir] = []
        elif isdir(sn) and not create_dir:
            self._sdirs[sdir] = []
        else:
            raise ProjectError("Subdir {} already exists".format(sdir))
        
    def add_file(self, filename, sdir=None, create_file=True):
        """
        Adds a file to a project.
        
        **Arguments**
        
            *filename* (string):
                The filename that should be
                added to the project.
            *sdir* (string):
                Adds the file to the given sub-directory.
                If None, it will be added
                to the default sub-directory
                (the project's directory).
            *create_file* (boolean):
                Whether or not you want to
                create the file.
                Default: True.
                
            **Raises**: :class:`ProjectError`
                If the sub-directory doesn't exist
                or if the file already exists.
        
        """
        fn = self.get_file_path(filename, sdir)
        if exists(fn) and create_file:
            raise ProjectError("File {} already exists".format(filename))
        if create_file:    
            open(fn, "w")
        filelist = self.get_file_list(sdir)
        filelist.append(filename)
            
        
    def remove_file(self, filename, sdir=None, remove_file=True):
        """
        Removes a file from the project.
        
        **Arguments**
        
            *filename* (string):
                The name of the file
                that should be removed.
            *sdir* (string):
                Removes the file from the given 
                sub-directory.
                If None, it will be removed from 
                the default sub-directory
                (the project's directory).
            *remove_file* (boolean):
                Whether or not you want to
                remove the file.
                Default: True.
                
            **Raises**: :class:`ProjectError`
                If the file doesn't exist or
                if the sub-directory doesn't exist.
        
        """
        fn = self.get_file_path(filename, sdir)
        
        filelist = self.get_file_list(sdir)
        try:
            filelist.index(filename)
            if remove_file:
                remove(fn)
            filelist.remove(filename)
        except ValueError:
            raise ProjectError("File {} doesn't exist".format(filename))
        
    def remove_subdir(self, sdir, remove_dir=True):
        """
        Removes a sub-directory from the project.
        The sub-directory has to be empty.
    
        **Arguments**
        
            *sdir* (string):
                The sub-directory that should be
                removed.
            *remove_dir* (boolean):
                Whether or not you want to
                remove the directory.
                Default: True.

            **Raises**: :class:`ProjectError`
                If the sub-directory doesn't exist
                or if it's not empty or if you are 
                trying to remove the project directory.
        
        """
        if sdir is None or sdir == "default":
            raise ProjectError("Cannot remove the project directory")
        
        filelist = self.get_file_list(sdir)
        if len(filelist) > 0:
            raise ProjectError("Sub-directory {} is not empty".format(sdir))
        sn = self.get_subdir_path(sdir)
        if remove_dir:
            rmdir(sn)
        del self._sdirs[sdir]
        
        
        
        
        
        