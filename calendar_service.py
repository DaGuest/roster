import re
import logging
from datetime import datetime
import google_api_service as gapi

class CalendarEvent:    
    DATETIMEFORMAT = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    DATETIMESTRFFORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, summary, starttime, endtime):
        """
        Initialize a CalendarEvent with summary, start time, and end time.
        Args:
            summary: The event summary or title.
            starttime: The start time string (ISO format or containing ISO format).
            endtime: The end time string (ISO format or containing ISO format).
        """
        self.summary = summary
        if re.search(self.DATETIMEFORMAT, starttime):
            starttime = re.search(self.DATETIMEFORMAT, starttime).group(0)
            self.starttime = datetime.fromisoformat(starttime)
        if re.search(self.DATETIMEFORMAT, endtime):
            endtime = re.search(self.DATETIMEFORMAT, endtime).group(0)
            self.endtime = datetime.fromisoformat(endtime)
    
    def get_starttime_string(self) -> str:
        """
        Return the start time as a string in the required format for Google Calendar API.
        """
        return self.starttime.strftime(self.DATETIMESTRFFORMAT) + "Z"
    
    def get_endtime_string(self) -> str:
        """
        Return the end time as a string in the required format for Google Calendar API.
        """
        return self.endtime.strftime(self.DATETIMESTRFFORMAT) + "Z"

    def set_event_id(self, event_id):
        """
        Set the event ID for this CalendarEvent.
        Args:
            event_id: The unique identifier for the event.
        """
        self.event_id = event_id

    def compare_on_date(self, other) -> bool:
        """
        Compare if this event and another event occur on the same date.
        Args:
            other: Another CalendarEvent instance.
        Returns True if both events are on the same date, False otherwise.
        """
        if isinstance(other, CalendarEvent):
            return (self.starttime.date() == other.starttime.date()) and (((self.starttime >= other.starttime) and (self.starttime <= other.endtime)) or (self.endtime <= other.endtime and self.endtime => other.starttime))
        return NotImplemented
    
    def __eq__(self, other) -> bool:
        """
        Check if two CalendarEvents are equal based on start and end times.
        """
        if isinstance(other, CalendarEvent):
            return (self.starttime == other.starttime) and (self.endtime == other.endtime) and (self.summary == other.summary)
        return NotImplemented
    
    def __lt__(self, other) -> bool:
        """
        Check if this event ends before another event starts.
        """
        if isinstance(other, CalendarEvent):
            return self.endtime < other.starttime
        return NotImplemented
    
    def __gt__(self, other) -> bool:
        """
        Check if this event starts after another event ends.
        """
        if isinstance(other, CalendarEvent):
            return self.starttime > other.endtime
        return NotImplemented
    
    def __hash__(self):
        """
        Return hash based on string combination summary, starttime and endtime.
        """
        return hash(self.summary + self.get_starttime_string() + self.get_endtime_string())
    
    def to_dict(self) -> dict:
        """
        Convert the CalendarEvent to a dictionary suitable for Google Calendar API.
        Returns a dictionary with summary, start, and end time information.
        """
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
        """
        Initialize the CalendarService, setting up the Google Calendar API service and event list.
        """
        self.service = gapi.GoogleCalendarAPIService()
        self.calendar_id:str = None
        self.events:set[CalendarEvent] = set()
        self.logger = logging.getLogger(__name__)
    
    def _get_calendar_id(self, calendar_name):
        """
        Retrieve and set the calendar ID for a given calendar name.
        Args:
            calendar_name: The name of the calendar to search for.
        """
        calendar_list = self.service.get_list_of_calendars()
        for calendar in calendar_list["items"]:
            if calendar["summary"] == calendar_name:
                self.calendar_id = calendar["id"]
        self.logger.info("Calendar id retreived: %s", self.calendar_id)
    
    def get_events(self, starttime:datetime, endtime:datetime):
        """
        Retrieve events from the calendar within a specified time range and populate the events list.
        Args:
            starttime: The start datetime for the event search.
            endtime: The end datetime for the event search.
        """
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
                self.events.add(event)
    
    def delete_overlapping_events(self, new_events:list[CalendarEvent], filteredEvents: filter):
        """
        Delete events from the calendar that overlap in date with any of the new events.
        Args:
            new_events: List of new CalendarEvent objects to compare against existing events.
        """
        for event in self.events:
            for new_event in filteredEvents:
                if event.compare_on_date(new_event):
                    self.service.delete_event(self.calendar_id, event.event_id)
                    self.logger.info("Deleting event: %s on %s", event.summary, event.starttime.date())
                    break
        self.logger.info("Overlapping events deleted")

    def insert_events(self, new_events:list[CalendarEvent]):
        """
        Insert new events into the calendar after deleting overlapping events.
        Args:
            new_events: List of CalendarEvent objects to insert.
        """
        filteredEvents = filter(lambda x: x not in self.events, new_events)
        self.delete_overlapping_events(new_events, filteredEvents)
        for event in filteredEvents:
            self.service.insert_event(self.calendar_id, event.to_dict())
            self.logger.info("Inserting event: %s on %s", event.summary, event.starttime.date())
        self.logger.info("Events inserted") 