import unittest
from google_api_service import GoogleAPIService

class TestGoogleApiService(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.service = GoogleAPIService("calendar")
        return super().setUpClass()

    def test_get_credentials(self):
        self.assertTrue(self.service.get_credentials())
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service.creds)

    def test_get_service(self):
        self.assertTrue(self.service.get_credentials())
        self.assertIsNotNone(self.service.get_service())