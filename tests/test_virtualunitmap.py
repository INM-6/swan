"""
Created on Sep 22, 2015

@author: Christoph Gollan

Unit test module for the :class:`src.virtualunitmap.VirtualUnitMap` class.
"""
import sys
from os.path import pardir, join, realpath, abspath
import unittest

p = abspath(join(realpath(__file__), pardir, pardir))
sys.path.insert(1, p)
sys.path.insert(1, join(p, "src"))
sys.path.insert(1, join(p, "resources"))
sys.path.insert(1, join(p, "python-neo"))
sys.path.insert(1, join(p, "python-odml"))

from src.virtualunitmap import VirtualUnitMap


class Test(unittest.TestCase):
    """
    Test class for testing :class:`src.virtualunitmap.VirtualUnitMap`.

    """

    def setUp(self):
        # creating a virtual unit map instance
        self.map = VirtualUnitMap()

    def test01_SetInitialMap(self):
        # setting up an initial map
        self.map.set_initial_map([2, 3])
        mapping = [[1, 2, None, None, None], [1, 2, 3, None, None]]
        # has to be equal to the manually created one
        self.assertListEqual(self.map.mapping, mapping)
        self.map.reset()
        # setting up an initial map
        self.map.set_initial_map([1, 1])
        mapping = [[1, None], [1, None]]
        # has to be equal to the manually created one
        self.assertListEqual(self.map.mapping, mapping)
        self.map.reset()
        # setting up an initial map
        self.map.set_initial_map([1, 0, 3])
        mapping = [[1, None, None, None], [None, None, None, None], [1, 2, 3, None]]
        # has to be equal to the manually created one
        self.assertListEqual(self.map.mapping, mapping)

    def test02_SetMap(self):
        # setting up a map
        m = {1:[("a", 1), ("b", 1)],
             2:[("a", 2), ("b", 2)],
             3:[("a", None), ("b", 3)],
             4:[("a", None), ("b", None)],
             5:[("a", None), ("b", None)],
             "channel":3,
        }
        self.map.set_map([2, 3], m)
        mapping = [[1, 2, None, None, None], [1, 2, 3, None, None]]
        # has to be equal to the manually created one
        self.assertListEqual(self.map.mapping, mapping)
        self.map.reset()
        # setting up a map
        m = {1:[("a", 1), ("b", 1)],
             2:[("a", None), ("b", None)],
             "channel":45,
        }
        self.map.set_map([1, 1], m)
        mapping = [[1, None], [1, None]]
        # has to be equal to the manually created one
        self.assertListEqual(self.map.mapping, mapping)
        self.map.reset()
        # setting up a map
        m = {1:[("a", 1), ("b", None), ("c", 1)],
             2:[("a", None), ("b", None), ("c", 2)],
             3:[("a", None), ("b", None), ("c", 3)],
             4:[("a", None), ("b", None), ("c", None)],
             "channel":99,
        }
        self.map.set_map([1, 0, 3], m)
        mapping = [[1, None, None, None], [None, None, None, None], [1, 2, 3, None]]
        # has to be equal to the manually created one
        self.assertListEqual(self.map.mapping, mapping)

    def test10_Swap(self):
        # setting up an initial map
        self.map.set_initial_map([2, 3])
        mapping = [[1, 2, None, None, None], [2, 1, 3, None, None]]
        # swapping two units
        self.map.swap(1, 0, 1)
        # mapping has to be changed, two unit ids are swapped
        self.assertListEqual(self.map.mapping, mapping)
        mapping = [[1, 2, None, None, None], [1, 2, 3, None, None]]
        # swapping the same two units again
        self.map.swap(1, 0, 1)
        # mapping has to be like after setting the initial map
        self.assertListEqual(self.map.mapping, mapping)

if __name__ == "__main__":
    unittest.main()