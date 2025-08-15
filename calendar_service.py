import re
import logging
from datetime import datetime
import google_api_service as gapi

class CalendarEvent:    
    DATETIMEFORMAT = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    DATETIMESTRFFORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, summary, starttime, endtime):
        self.summary = summary
        if re.search(self.DATETIMEFORMAT, starttime):
            starttime = re.search(self.DATETIMEFORMAT, starttime).group(0)
            self.starttime = datetime.fromisoformat(starttime)
        if re.search(self.DATETIMEFORMAT, endtime):
            endtime = re.search(self.DATETIMEFORMAT, endtime).group(0)
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
                    "timeZone": gapi.GoogleAPIService.TIMEZONE
                },
                "end": {
                    "dateTime": self.endtime.strftime(self.DATETIMESTRFFORMAT),
                    "timeZone": gapi.GoogleAPIService.TIMEZONE
                }
                }

class CalendarService:
    def __init__(self):
        self.service = gapi.GoogleCalendarAPIService()
        self.calendar_id:str = None
        self.events:list[CalendarEvent] = []
        self.logger = logging.getLogger(__name__)
    
    def _get_calendar_id(self, calendar_name):
        calendar_list = self.service.get_list_of_calendars()
        for calendar in calendar_list["items"]:
            if calendar["summary"] == calendar_name:
                self.calendar_id = calendar["id"]
        self.logger.info("Calendar id retreived: %s", self.calendar_id)
    
    def get_events(self, starttime:datetime, endtime:datetime):
        self.events.clear()
        if (self.calendar_id is None):
            self._get_calendar_id("KLM")
        self.events_list = self.service.get_events(self.calendar_id, starttime.strftime(CalendarEvent.DATETIMESTRFFORMAT) +"Z", endtime.strftime(CalendarEvent.DATETIMESTRFFORMAT) + "Z")
        self.logger.info("Existing events retreived")

        # Create CalendarEvents from acquired item list
        for item in self.events_list["items"]:
            if "dateTime" in item["start"] and "dateTime" in item["end"]:
                event = CalendarEvent(item["summary"], item["start"]["dateTime"], item["end"]["dateTime"])
                event.set_event_id(item["id"])
                self.events.append(event)
    
    def delete_overlapping_events(self, new_events:list[CalendarEvent]):
        for event in self.events:
            filteredEvents = filter(lambda x: x.starttime.date() == event.starttime.date(), new_events)
            for new_event in new_events:
                if event.compare_on_date(new_event):
                    self.service.delete_event(self.calendar_id, event.event_id)
                    self.logger.info("Deleting event: %s on %s", event.summary, event.starttime.date())
                    break
        self.logger.info("Overlapping events deleted")

    def insert_events(self, new_events:list[CalendarEvent]):
        self.delete_overlapping_events(new_events)
        for event in new_events:
            self.service.insert_event(self.calendar_id, event.to_dict())
            self.logger.info("Inserting event: %s on %s", event.summary, event.starttime.date())
        self.logger.info("Events inserted") 