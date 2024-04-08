import os.path

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleAPIService:
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

    def get_credentials(self):
        if os.path.exists("/home/pi/Roster/roster_data/token.json"):
            try:
                self.creds = Credentials.from_authorized_user_file("/home/pi/Roster/roster_data/token.json", self.scopes)
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
                    flow = InstalledAppFlow.from_client_secrets_file("/home/pi/Roster/roster_data/credentials.json", self.scopes)
                    self.creds = flow.run_local_server(port=0)
                except:
                    print("Unable to create credentials")
                    return False

            with open("/home/pi/Roster/roster_data/token.json", "w") as token:
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