import os.path

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleAPIService:
    HOMEPATH = "/home/pi/roster/etc/"
    TIMEZONE = "Etc/UTC"
    service_metadata = {"gmail": {"version":"v1","scope": "https://www.googleapis.com/auth/gmail.modify"}, 
               "calendar": {"version": "v3", "scope": "https://www.googleapis.com/auth/calendar"}}
    scopes = [service_metadata["calendar"]["scope"], service_metadata["gmail"]["scope"]]
    scope = None
    version = None
    creds = None
    service_name = None
    service = None

    def __init__(self, service_name):
        self.service_name = service_name
        self.version = self.service_metadata[service_name]["version"]
        self.scope = self.service_metadata[service_name]["scope"]
        self.get_credentials()
        self.get_service()

    def get_credentials(self):
        if os.path.exists(self.HOMEPATH + "token.json"):
            try:
                self.creds = Credentials.from_authorized_user_file(self.HOMEPATH + "token.json", self.scopes)
            except:
                print("Unable to get credentials from existing token")
        
        if not self.creds or not self.creds.valid:
            # Credentials are expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except RefreshError:
                    print("Unable to refresh credentials", self.creds.expired)
                    return False
            
            # Credentials don't exist yet
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.HOMEPATH + "credentials.json", self.scopes)
                    self.creds = flow.run_local_server(port=0)
                except:
                    print("Unable to create credentials")
                    return False

            with open(self.HOMEPATH + "token.json", "w") as token:
                token.write(self.creds.to_json())
        return True
        
    def get_service(self):
        if not self.service:
            try:
                self.service = build(self.service_name, self.version, credentials=self.creds)
            except HttpError as error:
                print(f"An error occurred: {error}")
                return False
            except:
                print("Error with obtaining service")
                return False
        return self.service

class GoogleCalendarAPIService(GoogleAPIService):
    def __init__(self):
        super().__init__("calendar")

    def get_list_of_calendars(self):
        return self.service.calendarList().list().execute()
    
    def get_events(self, calendar_id, starttime, endtime):
        return self.service.events().list(calendarId=calendar_id, timeMin=starttime, timeMax=endtime, timeZone=self.TIMEZONE).execute()
    
    def delete_event(self, calendar_id, event_id):
        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    def insert_event(self, calendar_id, body):
        self.service.events().insert(calendarId=calendar_id, body=body).execute()
    
class GoogleMailAPIService(GoogleAPIService):
    def __init__(self):
        super().__init__("gmail")

    def get_messages(self):
        return self.service.users().messages().list(userId="me", q="Duty from:noreply@klm.com", maxResults=10).execute().get('messages', [])

    def get_message(self, message_id):
        return self.service.users().messages().get(userId='me', id=message_id).execute()
    
    def get_attachment(self, message_id, attachment_id):
        return self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
    
    def delete_mail(self, message_id):
        self.service.users().messsages().trash(userId='me', id=message_id).execute()