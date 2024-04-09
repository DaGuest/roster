import google_api_service as gapi
import base64

class MailService:
    def __init__(self):
        self.service = gapi.GoogleMailAPIService()
        self.messages = None

    def check_mail(self):
        self.messages = self.service.get_messages()
        return len(self.messages) > 0
    
    def get_attachment(self):
        if not self.check_mail():
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
        return True