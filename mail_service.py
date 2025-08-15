import google_api_service as gapi
import base64
import logging

class MailService:
    def __init__(self):
        """
        Initialize the MailService, setting up the Google Mail API service and logger.
        """
        self.logger = logging.getLogger(__name__)
        self.service = gapi.GoogleMailAPIService()
        self.messages = None

    def check_mail(self) -> bool:
        """
        Check if there are any roster messages in the user's Gmail inbox..
        Returns True if messages are found, False otherwise.
        """
        if not (self.service or self.service.get_service()):
            return False
        self.messages = self.service.get_messages()
        return len(self.messages) > 0
    
    def get_attachment(self) -> bool:
        """
        Download the first attachment from the first message found in the user's Gmail inbox.
        Returns True if an attachment is successfully downloaded, False otherwise.
        """
        if not self.check_mail():
            self.logger.info("No roster in e-mail")
            return False
        message_id = self.messages[0]['id']
        message = self.service.get_message(message_id)
        for part in message['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    msg_id = message['id']
                    attachment_id = part['body']['attachmentId']
                    attachment = self.service.get_attachment(msg_id, attachment_id)
                    data = attachment['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = self.service.HOMEPATH + "roster.pdf"

                with open(path, 'wb') as f:
                    f.write(file_data)
                    f.close()
        self.logger.info("Attachment downloaded")
        return True