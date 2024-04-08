import google_api_service as gapi

class CalendarService:
    def __init__(self):
        self.service = gapi.GoogleAPIService("calendar").get_service()
        self.calendar_id = None
        self.events = None
    
    def _get_calendar_id(self, calendar_name):
        calendar_list = self.service.calendarList().list().execute()
        for calendar in calendar_list["items"]:
            if calendar["summary"] == calendar_name:
                self.calendar_id = calendar["id"]
    
    def get_events(self, starttime):
        if (self.calendar_id is None):
            self._get_calendar_id("KLM")
        try:
            self.events = self.service.events().list(calendarId=self.calendar_id, timeMin=starttime).execute()
        except:
            print("Unable to get events from calendar.")
    
    # function that compares current to new events

    # function that inserts events