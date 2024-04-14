import unittest
from google_api_service import GoogleAPIService, GoogleCalendarAPIService, GoogleMailAPIService

class TestGoogleApiService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = GoogleAPIService("gmail")
        self.calendar_service = GoogleCalendarAPIService()
        self.mail_service = GoogleMailAPIService()

    def test_get_credentials(self):
        self.assertTrue(self.service.get_credentials())
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.creds)

    def test_get_service(self):
        self.assertTrue(self.service.get_credentials())
        self.assertIsNotNone(self.service.get_service())

    def test_get_messages(self):
        self.assertIsNotNone(self.mail_service.get_messages())

    def test_get_list_calendars(self):
        self.assertIsNotNone(self.calendar_service.get_list_of_calendars())