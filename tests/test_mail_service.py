import unittest
from mail_service import MailService

class TestMailService(unittest.TestCase):
    def setUp(self):
        self.service = MailService()

    def test_check_mail(self):
        self.assertIsNone(self.service.messages)
        self.service.check_mail()
        self.assertIsNotNone(self.service.messages)