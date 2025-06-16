import unittest
from simulator.core import TomasuloCore
from simulator.config import DEFAULT_CONFIG

class TestTomasuloCore(unittest.TestCase):
    def setUp(self):
        self.core = TomasuloCore(DEFAULT_CONFIG)
    
    def test_initial_state(self):
        self.assertEqual(self.core.cycle, 0)
        self.assertEqual(len(self.core.rob.entries), DEFAULT_CONFIG['rob_size'])
