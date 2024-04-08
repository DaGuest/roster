import unittest
import calendar_service

class TestCalendarService(unittest.TestCase):
    def setUp(self):
        self.service = calendar_service.CalendarService()
        self.event1 = calendar_service.CalendarEvent("KL1234 AMS", "2024-04-08T09:00:00Z", "2024-04-08T09:50:00Z")
        self.event2 = calendar_service.CalendarEvent("KL5678 AMS", "2024-04-08T10:00:00Z", "2024-04-08T10:50:00Z")
        self.event3 = calendar_service.CalendarEvent("KL4321 AMS", "2024-04-08T10:20:00Z", "2024-04-08T10:40:00Z")
        self.event4 = calendar_service.CalendarEvent("Reserve", "2024-04-08T08:30:00Z", "2024-04-08T20:30:00Z")
        self.event1copy = calendar_service.CalendarEvent("KL8765 AMS", "2024-04-08T09:00:00Z", "2024-04-08T09:50:00Z")
    
    def test_get_calendar_id(self):
        self.service._get_calendar_id("KLM")
        self.assertIsNotNone(self.service.calendar_id)

    def test_get_events(self):
        self.service.get_events("2024-04-08T08:00:00Z", "2024-04-26T08:00:00Z")
        self.assertIsNotNone(self.service.events)

    def test_delete_events(self):
        self.service._get_calendar_id("KLM")
        self.service.get_events("2024-04-08T07:00:00Z", "2024-04-09T07:00:00Z")
        self.service.delete_overlapping_events([self.event1])
        self.service.get_events("2024-04-08T07:00:00Z", "2024-04-09T07:00:00Z")
        self.assertEqual(len(self.service.events), 0)
    
    def test_insert_events(self):
        self.service._get_calendar_id("KLM")
        self.service.get_events(self.event4.get_starttime_string(), self.event4.get_endtime_string())
        self.service.delete_overlapping_events([self.event4])
        self.service.insert_events([self.event4])
        self.service.get_events(self.event1.get_starttime_string(), self.event1.get_endtime_string())
        self.assertEqual(len(self.service.events), 1)

    def test_CalendarEvent(self):
        eventDict = {"summary": "KL1234 AMS", "start": {"dateTime": "2024-04-08T09:00:00", "timeZone": "Etc/UTC"}, "end": {"dateTime": "2024-04-08T09:50:00", "timeZone": "Etc/UTC"}}
        self.assertTrue(self.event1 < self.event2)
        self.assertTrue(self.event1 == self.event1copy)
        self.assertFalse(self.event1 == self.event2)
        self.assertFalse(self.event3 < self.event2)
        self.assertEqual(self.event1.to_dict(), eventDict)