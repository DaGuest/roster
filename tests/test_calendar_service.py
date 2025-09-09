import unittest
import calendar_service
from datetime import datetime
from datetime import timezone

class TestCalendarService(unittest.TestCase):
    def setUp(self):
        self.service = calendar_service.CalendarService()
        self.period_start = datetime(2024, 4, 8, 0, 0, tzinfo=timezone.utc)
        self.period_end = datetime(2024, 4, 9, 0, 0)
        self.event1 = calendar_service.CalendarEvent("KL1234 AMS", "2024-04-08T09:00:00Z", "2024-04-08T09:50:00Z")
        self.event2 = calendar_service.CalendarEvent("KL5678 AMS", "2024-04-08T10:00:00Z", "2024-04-08T10:50:00Z")
        self.event3 = calendar_service.CalendarEvent("KL4321 AMS", "2024-04-08T10:20:00Z", "2024-04-08T10:40:00Z")
        self.event4 = calendar_service.CalendarEvent("Reserve", "2024-04-08T09:00:00Z", "2024-04-08T20:30:00Z")
        self.event1copy = calendar_service.CalendarEvent("KL1234 AMS", "2024-04-08T09:00:00Z", "2024-04-08T09:50:00Z")
    
    def test_get_calendar_id(self):
        self.service._get_calendar_id("KLM")
        self.assertIsNotNone(self.service.calendar_id)

    def test_get_events(self):
        self.service.get_events(self.period_start, self.period_end)
        self.assertIsNotNone(self.service.existing_events)

    def test_delete_events(self):
        self.service._get_calendar_id("KLM")
        self.service.get_events(self.period_start, self.period_end)
        self.service.delete_overlapping_events([self.event1])
        self.service.get_events(self.period_start, self.period_end)
        self.assertEqual(len(self.service.existing_events), 0)
    
    def test_insert_events(self):
        self.service._get_calendar_id("KLM")
        self.service.get_events(self.event4.starttime, self.event4.endtime)
        self.service.delete_overlapping_events([self.event4])
        self.service.insert_events([self.event4])
        self.service.get_events(self.event1.starttime, self.event1.endtime)
        self.assertEqual(len(self.service.existing_events), 1)
        self.service.delete_overlapping_events([self.event4])

    def test_CalendarEvent(self):
        eventDict = {"summary": "KL1234 AMS", "start": {"dateTime": "2024-04-08T09:00:00", "timeZone": "Etc/UTC"}, "end": {"dateTime": "2024-04-08T09:50:00", "timeZone": "Etc/UTC"}}
        self.assertTrue(self.event1 < self.event2)
        self.assertTrue(self.event1 == self.event1copy)
        self.assertFalse(self.event1 == self.event2)
        self.assertFalse(self.event3 < self.event2)
        self.assertEqual(self.event1.to_dict(), eventDict)