import os
import re
import pypdf
import logging
from datetime import datetime, timedelta
from calendar_service import CalendarEvent

class RosterParser:
    def __init__(self):
        """
        Initialize the RosterParser, setting up logger, events list, and period flag.
        """
        self.logger = logging.getLogger(__name__)
        self.events = []
        self.period_set = False

    def convert_rosterpdf_to_text(self):
        """
        Convert the roster PDF to text, removing whitespace and newlines.
        Returns True if successful, False otherwise.
        """
        try:
            reader = pypdf.PdfReader(os.getcwd() + "/etc/roster.pdf")
            page = reader.pages[0]
            self.text = page.extract_text()
            self.text = re.sub(r"\s+", "", self.text)
            self.text = re.sub(r"\n", "", self.text)
            self.logger.info("Converted roster to text")
            return True
        except Exception as error:
            self.logger.error("Something went wrong converting PDF to text %s", error)
            return False
        
    def parse_period(self):
        """
        Parse the period (start and end dates) from the roster text and set the period attributes.
        """
        pattern_period_text = r"(?<=Period:)(\d{2}[A-Z][a-z]{2}\d{2}-\d{2}[A-Z][a-z]{2}\d{2})"
        pattern_single_period = r"\d\d[A-z]{3}\d\d"
        pattern_datetime = "%d%b%y"

        period_text_match:re.Match[str]|None = re.search(pattern_period_text, self.text)
        period_text:str = period_text_match.group(0) if period_text_match is not None else "" 
        periods:list[str] = re.findall(pattern_single_period, period_text)
        
        self.start_period = datetime.strptime(periods[0], pattern_datetime)
        self.end_period = datetime.strptime(periods[1], pattern_datetime)
        self.period_set = True
        self.logger.info("Parsed period")
        
    def parse_flight_events(self):
        """
        Parse flight events from the roster text and add them to the events list.
        """
        pattern_flight_events = r"[A-Z][a-z]{2}\d\d(?:PickUp|C\/I)(?:.*?)\[FDP\d\d:\d\d\]"
        pattern_single_event = r"KL(?:\d{4}|\d{3})[A-Z]{3}\d{8}[A-Z]{3}"
        pattern_title = r"KL(?:\d{4}|\d{3})"
        pattern_dest = r"(?<=\d{8})[A-Z]{3}"

        days_text:list[str] = re.findall(pattern_flight_events, self.text)
        self.events = []
        for day_text in days_text:
            date = self.get_date(day_text)
            events_text:list[str] = re.findall(pattern_single_event, day_text)
            for event in events_text:
                dates = self.get_datetimes(event, date)
                
                title_match:re.Match[str]|None = re.search(pattern_title, event)
                dest_match:re.Match[str]|None = re.search(pattern_dest, event)
                
                summary = title_match.group(0) if title_match is not None else ""
                summary += " " + dest_match.group(0) if dest_match is not None else ""
                
                self.events.append(self.construct_calendar_event(summary, dates[0], dates[1]))
        self.logger.info("Parsed flight events")
    
    def parse_sby_events(self):
        """
        Parse standby (SBY) events from the roster text and add them to the events list.
        """
        pattern_SBY_event = r"[A-Z][a-z]{2}\d\dSBY\_[A-Z]{4}\d{8}\[FDP\d\d:\d\d\]"
        events_text:list[str] = re.findall(pattern_SBY_event, self.text)
        self.construct_events(events_text, "Reserve")
        self.logger.info("Parsed sby events")

    def parse_pickup_events(self):
        """
        Parse pickup and check-in (Aanmeld) events from the roster text and add them to the events list.
        """
        # Pick up events
        pattern_pickup_events = r"[A-Z][a-z]{2}\d\d(?:PickUp)(?:.*?)\d{4}"
        events_text:list[str] = re.findall(pattern_pickup_events, self.text)
        events_text:list[str] = [x + x[-4:] for x in events_text]
        self.construct_events(events_text, "Pick Up")
        # Aanmeld events
        pattern_ciams_events = r"[A-Z][a-z]{2}\d\d(?:C\/IAMS)(?:.*?)\d{4}"
        events_text:list[str] = re.findall(pattern_ciams_events, self.text)
        events_text:list[str] = [x + x[-4:] for x in events_text]
        self.construct_events(events_text, "Aanmelden")
    
    def parse_sim_events(self):
        """
        Parse simulator (SIM) events from the roster text and add them to the events list.
        """
        pattern = r"[A-Z][a-z]{2}\d\dT(?:.*?)\[FDP\d\d:\d\d\]"
        pattern_title = r"(?<=[A-z]{3}\d\d)T.*?(?=[A-Z]\d_[A-Z]\d)"
        sim_times = {"TSLOE": 74, "TSTR": 119, "TSLPC": 74}
        offset = 1
        events_text:list[str] = re.findall(pattern, self.text)
        for event in events_text:
            date = self.get_date(event)
            title_match:re.Match[str]|None = re.search(pattern_title, event)
            summary = title_match.group(0) if title_match is not None else ""
            for training_id in sim_times.keys():
                reg_match = re.search(training_id, summary)
                if reg_match is not None:
                    offset += sim_times[reg_match.group(0)]
            dates = self.get_datetimes(event, date, offset)
            self.events.append(self.construct_calendar_event(summary, dates[0], dates[1]))
        self.logger.info("Parsed sim events")
    
    def parse_medical_events(self):
        """
        Parse medical events from the roster text and add them to the events list.
        """
        pattern = r"[A-Z][a-z]{2}\d\dMMCS(?:.*?)\[FDP\d\d:\d\d\]"
        events_text:list[str] = re.findall(pattern, self.text)
        self.construct_events(events_text, "Medical")
        self.logger.info("Parsed medical events")

    def parse_layover_events(self):
        """
        Parse layover (Dagover) events from the roster text and add them to the events list.
        """
        pattern = r"[A-Z][a-z]{2}\d\dXH\d[A-Z]{3}"
        events_text:list[str] = re.findall(pattern, self.text)
        events_text:list[str] = [text + "09002100" for text in events_text] # Add whole day times
        self.construct_events(events_text, "Dagover")
        self.logger.info("Parsed layover events")

    def parse_all_events(self):
        """
        Parse all event types from the roster PDF and populate the events list.
        """
        self.convert_rosterpdf_to_text()
        self.parse_period()
        self.parse_flight_events()
        self.parse_pickup_events()
        self.parse_medical_events()
        self.parse_sby_events()
        self.parse_sim_events()
        self.parse_layover_events()
    
    ### Constructs a datetime from a weekday-day string that fits inside the period
    ### Arg: 
    ###     date_line_text: string that represents a work day line
    ###
    def get_date(self, date_line_text):
        """
        Construct a datetime object from a weekday-day string that fits inside the period.
        Args:
            date_line_text: String that represents a work day line.
        Returns a datetime object for the event date.
        """
        if (not self.period_set):
            self.parse_period()
        pattern_regex_date = r"[A-z]{3}\d\d"
        pattern_datetime_date = "%d%b%y"

        date_match:re.Match[str]|None = re.search(pattern_regex_date, date_line_text)
        date_text = date_match.group(0) if date_match is not None else ""

        month_year_start = self.start_period.strftime("%b%y")
        month_year_end = self.end_period.strftime("%b%y")
        
        day_num_match:re.Match[str]|None = re.search(r"\d\d", date_text)
        day_num_text = day_num_match.group(0) if day_num_match is not None else ""
    
        return_date = datetime.strptime(day_num_text + month_year_start, pattern_datetime_date)

        # Check if date is in end month of period
        if int(day_num_text) <= self.end_period.day and int(day_num_text) < self.start_period.day:
            return_date = datetime.strptime(day_num_text + month_year_end, pattern_datetime_date)
        return return_date
    
    def get_datetimes(self, event_text:str, date:datetime, offset:float|None = None):
        """
        Construct start and end datetime objects for an event from its text and date.
        Args:
            event_text: The event string containing time information.
            date: The base date for the event.
            offset: Optional offset in minutes to adjust the start time.
        Returns a list of two datetime objects: [start, end].
        """
        times_together_match:re.Match[str]|None = re.search(r"\d{8}", event_text)
        times_together = times_together_match.group(0) if times_together_match is not None else ""
        times = re.findall(r"\d{4}", times_together)
        dates = []
        for time in times:
            hours = int(time[0:2])
            min = int(time[2:4])
            dates.append(date + timedelta(hours=hours, minutes=min))
        if offset is not None:
            dates[0] -= timedelta(minutes=offset)
        return dates
    
    def construct_calendar_event(self, summary:str, starttime:datetime, endtime:datetime):
        """
        Construct a CalendarEvent object from summary, start time, and end time.
        Args:
            summary: The event summary or title.
            starttime: The event start time (datetime object).
            endtime: The event end time (datetime object).
        Returns a CalendarEvent instance.
        """
        return CalendarEvent(summary, starttime.strftime(CalendarEvent.DATETIMESTRFFORMAT)+"Z", endtime.strftime(CalendarEvent.DATETIMESTRFFORMAT)+"Z")
    
    def construct_events(self, events:list[str], summary:str):
        """
        Construct and append CalendarEvent objects for a list of event strings with a given summary.
        Args:
            events: List of event strings.
            summary: The summary/title for the events.
        """
        for event in events:
            date = self.get_date(event)
            dates = self.get_datetimes(event, date)
            self.events.append(self.construct_calendar_event(summary, dates[0], dates[1]))