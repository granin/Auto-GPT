
# tests/unit/test_input_processing.py - Contains unit tests for the process_input function in the input_processing module.

import unittest

from bot.input_capture import process_input


class TestInputProcessing(unittest.TestCase):

    def test_process_input_valid(self):
        self.assertEqual(process_input("hello"), "hello")
        self.assertEqual(process_input("  hello world  "), "hello world")

    def test_process_input_invalid(self):
        self.assertNotEqual(process_input("  hello world  "), "  hello world  ")

    def test_process_input_empty(self):
        self.assertEqual(process_input("  "), "")
        self.assertEqual(process_input(""), "")

if __name__ == '__main__':
    unittest.main()
