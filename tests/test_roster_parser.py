import unittest
import re
from roster_parser import RosterParser

class TestRosterParser(unittest.TestCase):
    def setUp(self):
        self.roster_parser = RosterParser()

    def test_convert_pdf_to_text(self):
        self.assertTrue(self.roster_parser.convert_rosterpdf_to_text())
        self.assertCountEqual(re.findall(r"\s", self.roster_parser.text), [])