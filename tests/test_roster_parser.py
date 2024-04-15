import unittest
import re
from roster_parser import RosterParser

class TestRosterParser(unittest.TestCase):
    def setUp(self):
        self.roster_parser = RosterParser()

    def test_convert_pdf_to_text(self):
        self.assertTrue(self.roster_parser.convert_rosterpdf_to_text())
        self.assertCountEqual(re.findall(r"\s", self.roster_parser.text), [])

    def test_parse_period(self):
        self.roster_parser.convert_rosterpdf_to_text()
        self.roster_parser.parse_period()
        self.assertIsNotNone(self.roster_parser.start_period)

    def test_parse_flight_events(self):
        self.roster_parser.convert_rosterpdf_to_text()
        self.roster_parser.parse_period()
        self.roster_parser.parse_flight_events()
        self.assertTrue(len(self.roster_parser.events) > 0)

    def test_construct_events(self):
        self.roster_parser.convert_rosterpdf_to_text()
        self.roster_parser.parse_period()
        events = ["Thu11SBY_EAMS08302030[FDP00:00]"]
        self.roster_parser.construct_events(events, "Reserve")
        self.assertTrue(len(self.roster_parser.events) > 0)
