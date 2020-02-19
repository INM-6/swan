"""
Created on Sep 22, 2015

@author: Christoph Gollan

Unit test module for the :class:`src.export.Export` class.
"""
import sys
from os import remove
from os.path import exists, pardir, join, realpath, abspath
import unittest

p = abspath(join(realpath(__file__), pardir, pardir))
sys.path.insert(1, p)
sys.path.insert(1, join(p, "src"))
sys.path.insert(1, join(p, "resources"))
sys.path.insert(1, join(p, "python-neo"))
sys.path.insert(1, join(p, "python-odml"))

from src.export import Export


class Test(unittest.TestCase):
    """
    Test class for testing :class:`src.export.Export`.

    """

    def setUp(self):
        # creating a virtual unit map container with virtual unit maps
        self.d = {
            "files":["a", "b"],
             "vum3":{
                 1:[("a", 1), ("b", 1)],
                 2:[("a", None), ("b", None)],
                 "channel":3,
             },
             "vum45":{
                 1:[("a", 1), ("b", 1)],
                 2:[("a", 2), ("b", None)],
                 3:[("a", None), ("b", None)],
                 "channel":45,
             }
        }

    def tearDown(self):
        if exists("testcsv.csv"):
            remove("testcsv.csv")
        if exists("testcsv.odml"):
            remove("testcsv.odml")

    def test01_Csv(self):
        # exporting the dictionary
        Export.export_csv("testcsv", self.d)
        # exporting has to create an output file
        self.assertTrue(exists("testcsv.csv"))
        # importing the exported dictionary
        result = Export.import_csv("testcsv.csv")
        # after importing the dictionary has to be same as before
        self.assertDictEqual(result, self.d)

    def test05_Odml(self):
        # exporting the dictionary
        Export.export_odml("testcsv", self.d)
        # exporting has to create an output file
        self.assertTrue(exists("testcsv.odml"))
        # importing the exported dictionary
        result = Export.import_odml("testcsv.odml")
        # after importing the dictionary has to be same as before
        self.assertDictEqual(result, self.d)

if __name__ == "__main__":
    unittest.main()
