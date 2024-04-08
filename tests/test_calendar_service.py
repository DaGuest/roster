import unittest
import calendar_service

class TestCalendarService(unittest.TestCase):
    def setUp(self):
        self.service = calendar_service.CalendarService()
    
    def test_get_calendar_id(self):
        self.service._get_calendar_id("KLM")
        self.assertIsNotNone(self.service.calendar_id)

    def test_get_events(self):
        self.service.get_events("2024-04-08T08:00:00Z")
        self.assertIsNotNone(self.service.events)