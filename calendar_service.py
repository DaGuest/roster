import re
from datetime import datetime
import google_api_service as gapi

class CalendarService:
    TIMEZONE = "Etc/UTC"

    def __init__(self):
        self.service = gapi.GoogleAPIService("calendar").get_service()
        self.calendar_id = None
        self.events = []
    
    def _get_calendar_id(self, calendar_name):
        calendar_list = self.service.calendarList().list().execute()
        for calendar in calendar_list["items"]:
            if calendar["summary"] == calendar_name:
                self.calendar_id = calendar["id"]
    
    def get_events(self, starttime, endtime):
        self.events.clear()
        if (self.calendar_id is None):
            self._get_calendar_id("KLM")
        try:
            self.events_list = self.service.events().list(calendarId=self.calendar_id, timeMin=starttime, timeMax=endtime, timeZone=self.TIMEZONE).execute()
        except:
            print("Unable to get events from calendar.")

        # Create CalendarEvents from acquired item list
        for item in self.events_list["items"]:
            if "dateTime" in item["start"] and "dateTime" in item["end"]:
                event = CalendarEvent(item["summary"], item["start"]["dateTime"], item["end"]["dateTime"])
                event.set_event_id(item["id"])
                self.events.append(event)
    
    def delete_overlapping_events(self, new_events):
        for event in self.events:
            for new_event in new_events:
                if event.starttime.date() == new_event.starttime.date():
                    self.service.events().delete(calendarId=self.calendar_id, eventId=event.event_id).execute()
                    break

    def insert_events(self, new_events):
        if new_events:
            for event in new_events:
                self.service.events().insert(calendarId=self.calendar_id, body=event.to_dict()).execute()

class CalendarEvent:    
    DATETIMEFORMAT = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    DATETIMESTRFFORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, summary, starttime, endtime):
        self.summary = summary
        if re.search(self.DATETIMEFORMAT, starttime):
            self.starttime = datetime.fromisoformat(starttime)
        if re.search(self.DATETIMEFORMAT, endtime):
            self.endtime = datetime.fromisoformat(endtime)
    
    def get_starttime_string(self):
        return self.starttime.strftime(self.DATETIMESTRFFORMAT) + "Z"
    
    def get_endtime_string(self):
        return self.endtime.strftime(self.DATETIMESTRFFORMAT) + "Z"

    def set_event_id(self, event_id):
        self.event_id = event_id

    def compare_on_date(self, other):
        return self.starttime.date() == other.starttime.date()
    
    def __eq__(self, other):
        return (self.starttime == other.starttime) and (self.endtime == other.endtime)
    
    def __lt__(self, other):
        return self.endtime < other.starttime
    
    def __gt__(self, other):
        return self.starttime > other.endtime
    
    def to_dict(self):
        return {"summary": self.summary, 
                "start": {
                    "dateTime": self.starttime.strftime(self.DATETIMESTRFFORMAT),
                    "timeZone": CalendarService.TIMEZONE
                },
                "end": {
                    "dateTime": self.endtime.strftime(self.DATETIMESTRFFORMAT),
                    "timeZone": CalendarService.TIMEZONE
                }
                } 