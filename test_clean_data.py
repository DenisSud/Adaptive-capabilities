import unittest
from clean_data import detect_dips

class TestDetectDips(unittest.TestCase):

    def test_detect_dips_normal(self):
        data = [1, 2, 3, 2, 5, 6]
        expected = [2]
        self.assertEqual(detect_dips(data), expected)

    def test_detect_dips_no_dips(self):
        data = [1, 2, 3, 4, 5] 
        self.assertIsNone(detect_dips(data))

    def test_detect_dips_small_dips_filtered(self):
        data = [1, 2, 3, 2.9, 5, 6]
        self.assertIsNone(detect_dips(data))

    def test_detect_dips_multiple_dips(self):
        data = [1, 2, 3, 2, 4, 2, 5, 6]
        expected = [2, 4]
        self.assertEqual(detect_dips(data), expected)


if __name__ == '__main__':
    unittest.main()