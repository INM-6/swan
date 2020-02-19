"""
Created on Oct 16, 2014

@author: Christoph Gollan

Unit test module for the :class:`src.main.Main` class.
"""
import sys
from os import remove, pardir
from os.path import join, exists, abspath, split, realpath
import unittest
import csv
from PyQt4.QtGui import QApplication
# from PyQt4.QtCore import Qt
# from PyQt4.QtTest import QTest

p = abspath(join(realpath(__file__), pardir, pardir))
sys.path.insert(1, p)
sys.path.insert(1, join(p, "src"))
sys.path.insert(1, join(p, "resources"))
sys.path.insert(1, join(p, "python-neo"))
sys.path.insert(1, join(p, "python-odml"))

from src.main import Main
from src.virtualunitmap import VirtualUnitMap


class Test(unittest.TestCase):
    """
    Test class for testing :class:`src.main.Main`.

    """

    def setUp(self):
        # setting directories
        program_dir = abspath(join(realpath(__file__), pardir, pardir))
        home_dir = join(program_dir, "tests", "testdata")
        cache_dir = home_dir
        # creating the main instance
        self.app = QApplication(sys.argv)
        self.main = Main(program_dir, home_dir)
        # cache directory
        self.main._CACHEDIR = cache_dir
        self.main._preferences["cacheDir"] = cache_dir
        self.main._mystorage._cache_dir = cache_dir
        self.hdir = home_dir
        self.pdir = program_dir
        # project file names
        self.pname = join(self.hdir, "swan.txt")
        self.vname = join(self.hdir, "swan_vum.vum")
        # avoids segmentation fault
        self.app.deleteLater()
        
    def tearDown(self):
        # removing the created files
        if exists(self.pname):
            remove(self.pname)
        if exists(self.vname):
            remove(self.vname)
    
    def test01_NewProject_CreatingSuccess(self):
        # sessions to load
        files = [join(self.hdir, "l101015-001"),
                 join(self.hdir, "l101015-002")]
        channel = self.main._mystorage.get_channel()
        proname = self.main._preferences["defaultProName"]
        # has to successfully create the project
        success = self.main._mystorage.load_project(self.hdir, proname, channel, files)
        self.assertTrue(success)
    
    def test02_NewProject_CreatingFail(self):
        # no sessions given
        files = []
        channel = self.main._mystorage.get_channel()
        proname = self.main._preferences["defaultProName"]
        # has to fail creating the project
        success = self.main._mystorage.load_project(self.hdir, proname, channel, files)
        self.assertFalse(success)

    def test04_NewProject_SaveProject(self):
        # sessions to load
        files = [join(self.hdir, "l101015-001"),
                 join(self.hdir, "l101015-002")]
        channel = self.main._mystorage.get_channel()
        proname = self.main._preferences["defaultProName"]
        # has to successfully create the project files
        self.main._mystorage.load_project(self.hdir, proname, channel, files)
        # setting up a virtual unit map
        vumap = VirtualUnitMap()
        vumap.set_initial_map([1, 1])
        self.main._mystorage.store("vum", vumap)
        # has to successfully create the project files
        self.main.save_project()
        self.assertTrue(exists(self.pname))
        self.assertTrue(exists(self.vname))

    def test20_LoadConnectorMapSuccess(self):
        filename = join(self.hdir, "test_cmap_success.csv")
        # reading the channel ids from the file
        with open(filename, "rb") as cfile:
            creader = csv.reader(cfile, delimiter=',', quotechar='"')
            channels = [row[1] for row in creader]
        # is not allowed to raise an error
        self.main.load_connector_map(filename)
        # getting the channel ids
        channels_new = [item.channel for item in self.main.selector._items]
        i = 0
        tmp = channels
        channels = []
        for k in xrange(10):
            c = tmp[i:i+10]
            i += 10
            for el in reversed(c):
                channels.insert(0, int(el))
        # channels from program must be identical to the channel ids from the file
        self.assertListEqual(channels, channels_new)

    def test21_LoadConnectorMapFail(self):
        filename = join(self.hdir, "test_cmap_fail.csv")
        # getting the channel ids
        channels = [item.channel for item in self.main.selector._items]
        # must raise an error because the file could not be read
        self.assertRaises(ValueError, self.main.load_connector_map, filename)
        # getting the channel ids again
        channels_new = [item.channel for item in self.main.selector._items]
        # must be identical to the channel ids before calling the function
        self.assertListEqual(channels, channels_new)

    def test99_Quit(self):
        self.main.ui.action_Quit.trigger()


if __name__ == "__main__":
    unittest.main()