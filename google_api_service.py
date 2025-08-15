import os.path

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

class GoogleAPIService:
    HOMEPATH = os.getcwd() + "/etc/"
    TIMEZONE = "Etc/UTC"
    service_metadata = {"gmail": {"version":"v1","scope": "https://www.googleapis.com/auth/gmail.modify"}, 
               "calendar": {"version": "v3", "scope": "https://www.googleapis.com/auth/calendar"}}
    scopes:list[str] = [service_metadata["calendar"]["scope"], service_metadata["gmail"]["scope"]]
    scope:str = None
    version:str = None
    creds = None
    service_name:str = None
    service = None

    def __init__(self, service_name:str):
        """
        Initialize the GoogleAPIService with the specified service name (e.g., 'gmail' or 'calendar').
        Sets up the version, scope, and obtains credentials and service resource.
        """
        self.service_name:str = service_name
        self.version:str = self.service_metadata[service_name]["version"]
        self.scope:str = self.service_metadata[service_name]["scope"]
        self.get_credentials()
        self.get_service()

    def get_credentials(self) -> bool:
        """
        Obtain and refresh OAuth2 credentials for the Google API service.
        Loads credentials from token.json if available, otherwise initiates the OAuth2 flow.
        Returns True if credentials are successfully obtained, False otherwise.
        """
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
                except Exception as error:
                    print("Unable to create credentials, error: ", error)
                    return False

            with open(self.HOMEPATH + "token.json", "w") as token:
                token.write(self.creds.to_json())
        return True
        
    def get_service(self) -> Resource | None:
        """
        Build and return the Google API service resource using the credentials.
        Returns the service resource if successful, None otherwise.
        """
        if not self.service:
            try:
                self.service = build(self.service_name, self.version, credentials=self.creds)
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None
            except:
                print("Error with obtaining service")
                return None
        return self.service

class GoogleCalendarAPIService(GoogleAPIService):
    def __init__(self):
        """
        Initialize the GoogleCalendarAPIService for interacting with Google Calendar API.
        """
        super().__init__("calendar")

    def get_list_of_calendars(self) -> dict:
        """
        Retrieve a list of calendars accessible by the user.
        Returns a dictionary containing calendar list data.
        """
        try:
            return self.service.calendarList().list().execute()
        except HttpError as error:
            self.logger.error(f"An error occurred while fetching calendar list: {error}")
            return {"items": []}
    
    def get_events(self, calendar_id:str, starttime:str, endtime:str) -> dict:
        """
        Retrieve events from a specified calendar within a time range.
        Args:
            calendar_id: The ID of the calendar to fetch events from.
            starttime: The start time (RFC3339 timestamp) for events.
            endtime: The end time (RFC3339 timestamp) for events.
        Returns a dictionary containing event data.
        """
        try:
            return self.service.events().list(calendarId=calendar_id, timeMin=starttime, timeMax=endtime, timeZone=self.TIMEZONE, singleEvents=True, maxResults=250).execute()
        except HttpError as error:
            self.logger.error(f"An error occurred while fetching events: {error}")
            return {"items": []}
            
    def delete_event(self, calendar_id:str, event_id:str):
        """
        Delete an event from a specified calendar.
        Args:
            calendar_id: The ID of the calendar.
            event_id: The ID of the event to delete.
        """
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        except HttpError as error:
            self.logger.error(f"An error occurred while deleting event: {error}")
            return None

    def insert_event(self, calendar_id:str, body):
        """
        Insert a new event into a specified calendar.
        Args:
            calendar_id: The ID of the calendar.
            body: The event data to insert (dictionary).
        """
        try:
            self.service.events().insert(calendarId=calendar_id, body=body).execute()
        except HttpError as error:
            self.logger.error(f"An error occurred while inserting event: {error}")
            return None
    
class GoogleMailAPIService(GoogleAPIService):
    def __init__(self):
        """
        Initialize the GoogleMailAPIService for interacting with Gmail API.
        """
        super().__init__("gmail")

    def get_messages(self) -> list:
        """
        Retrieve a list of messages from the user's Gmail inbox matching a specific query.
        Returns a list of message metadata dictionaries.
        """
        try:
            return self.service.users().messages().list(userId="me", q="Duty from:noreply@klm.com", maxResults=10).execute().get('messages', [])
        except HttpError as error:
            self.logger.error(f"An error occurred while fetching messages: {error}")
            return []

    def get_message(self, message_id:str) -> dict:
        """
        Retrieve a specific message by its ID from the user's Gmail inbox.
        Args:
            message_id: The ID of the message to retrieve.
        Returns a dictionary containing the message data.
        """
        try:
            return self.service.users().messages().get(userId='me', id=message_id).execute()
        except HttpError as error:
            self.logger.error(f"An error occurred while fetching message: {error}")
            return {}
    
    def get_attachment(self, message_id:str, attachment_id:str) -> dict:
        """
        Retrieve an attachment from a specific message in the user's Gmail inbox.
        Args:
            message_id: The ID of the message containing the attachment.
            attachment_id: The ID of the attachment to retrieve.
        Returns a dictionary containing the attachment data.
        """
        try:
            return self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
        except HttpError as error:
            self.logger.error(f"An error occurred while fetching attachment: {error}")
            return {'data': ''}
        
    
    def delete_mail(self, message_id:str):
        """
        Move a specific message to trash in the user's Gmail inbox.
        Args:
            message_id: The ID of the message to delete (move to trash).
        """
        try:
            self.service.users().messsages().trash(userId='me', id=message_id).execute()
        except HttpError as error:
            self.logger.error(f"An error occurred while deleting mail: {error}")
            return None