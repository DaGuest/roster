import os
import re
import pypdf
import logging
from datetime import datetime, timedelta
from calendar_service import CalendarEvent

class RosterParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.events = []
        self.period_set = False

    def convert_rosterpdf_to_text(self):
        try:
            reader = pypdf.PdfReader(os.getcwd() + "/etc/roster.pdf")
            page = reader.pages[0]
            self.text = page.extract_text()
            self.text = re.sub(r"\s+", "", self.text)
            self.text = re.sub(r"\n", "", self.text)
            self.logger.info("Converted roster to text")
            return True
        except Exception as error:
            self.logger.error("Something went wrong converting PDF to text")
            return False
        
    def parse_period(self):
        pattern_period_text = r"(?<=Period:)(\d{2}[A-Z][a-z]{2}\d{2}-\d{2}[A-Z][a-z]{2}\d{2})"
        pattern_single_period = r"\d\d[A-z]{3}\d\d"
        pattern_datetime = "%d%b%y"

        period_text = re.search(pattern_period_text, self.text).group(0)
        periods = re.findall(pattern_single_period, period_text)
        
        self.start_period = datetime.strptime(periods[0], pattern_datetime)
        self.end_period = datetime.strptime(periods[1], pattern_datetime)
        self.period_set = True
        self.logger.info("Parsed period")
        
    def parse_flight_events(self):
        pattern_flight_events = r"[A-Z][a-z]{2}\d\d(?:PickUp|C\/I)(?:.*?)\[FDP\d\d:\d\d\]"
        pattern_single_event = r"KL(?:\d{4}|\d{3})[A-Z]{3}\d{8}[A-Z]{3}"
        pattern_title = r"KL(?:\d{4}|\d{3})"
        pattern_dest = r"(?<=\d{8})[A-Z]{3}"

        days_text = re.findall(pattern_flight_events, self.text)
        self.events = []
        for day_text in days_text:
            date = self.get_date(day_text)
            events_text = re.findall(pattern_single_event, day_text)
            for event in events_text:
                dates = self.get_datetimes(event, date)
                summary = re.search(pattern_title, event).group(0)
                summary += " " + re.search(pattern_dest, event).group(0)
                self.events.append(self.construct_calendar_event(summary, dates[0], dates[1]))
        self.logger.info("Parsed flight events")
    
    def parse_sby_events(self):
        pattern_SBY_event = r"[A-Z][a-z]{2}\d\dSBY\_[A-Z]{4}\d{8}\[FDP\d\d:\d\d\]"
        events_text = re.findall(pattern_SBY_event, self.text)
        self.construct_events(events_text, "Reserve")
        self.logger.info("Parsed sby events")

    def parse_pickup_events(self):
        # Pick up events
        pattern_pickup_events = r"[A-Z][a-z]{2}\d\d(?:PickUp)(?:.*?)\d{4}"
        events_text = re.findall(pattern_pickup_events, self.text)
        events_text = [x + x[-4:] for x in events_text]
        self.construct_events(events_text, "Pick Up")
        # Aanmeld events
        pattern_ciams_events = r"[A-Z][a-z]{2}\d\d(?:C\/IAMS)(?:.*?)\d{4}"
        events_text = re.findall(pattern_ciams_events, self.text)
        events_text = [x + x[-4:] for x in events_text]
        self.construct_events(events_text, "Aanmelden")
    
    def parse_sim_events(self):
        pattern = r"[A-Z][a-z]{2}\d\dT(?:.*?)\[FDP\d\d:\d\d\]"
        pattern_title = r"(?<=[A-z]{3}\d\d)T.*?(?=[A-Z]\d_[A-Z]\d)"
        sim_times = {"TSLOE": 74, "TSTR": 119, "TSLPC": 74}
        offset = 1
        events_text = re.findall(pattern, self.text)
        for event in events_text:
            date = self.get_date(event)
            summary = re.search(pattern_title, event).group(0)
            for training_id in sim_times.keys():
                reg_match = re.search(training_id, summary)
                if reg_match is not None:
                    offset += sim_times[reg_match.group(0)]
            dates = self.get_datetimes(event, date, offset)
            self.events.append(self.construct_calendar_event(summary, dates[0], dates[1]))
        self.logger.info("Parsed sim events")
    
    def parse_medical_events(self):
        pattern = r"[A-Z][a-z]{2}\d\dMMCS(?:.*?)\[FDP\d\d:\d\d\]"
        events_text = re.findall(pattern, self.text)
        self.construct_events(events_text, "Medical")
        self.logger.info("Parsed medical events")

    def parse_layover_events(self):
        pattern = r"[A-Z][a-z]{2}\d\dXH\d[A-Z]{3}"
        events_text = re.findall(pattern, self.text)
        events_text = [text + "09002100" for text in events_text]
        self.construct_events(events_text, "Dagover")
        self.logger.info("Parsed layover events")

    def parse_all_events(self):
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
        if (not self.period_set):
            self.parse_period()
        pattern_regex_date = r"[A-z]{3}\d\d"
        pattern_datetime_date = "%d%b%y"

        date_text = re.search(pattern_regex_date, date_line_text).group(0)

        month_year_start = self.start_period.strftime("%b%y")
        month_year_end = self.end_period.strftime("%b%y")
        
        day_num_text = re.search(r"\d\d", date_text).group(0)
        weekday_text = re.search(r"[A-z]{3}", date_text).group(0)
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        return_date = datetime.strptime(day_num_text + month_year_start, pattern_datetime_date)

        # Check if date is in end month of period
        if int(day_num_text) <= self.end_period.day and int(day_num_text) < self.start_period.day:
            return_date = datetime.strptime(day_num_text + month_year_end, pattern_datetime_date)
        return return_date
    
    def get_datetimes(self, event_text, date, offset=None):
        times_together = re.search(r"\d{8}", event_text).group(0)
        times = re.findall(r"\d{4}", times_together)
        dates = []
        for time in times:
            hours = int(time[0:2])
            min = int(time[2:4])
            dates.append(date + timedelta(hours=hours, minutes=min))
        if offset is not None:
            dates[0] -= timedelta(minutes=offset)
        return dates
    
    def construct_calendar_event(self, summary, starttime, endtime):
        return CalendarEvent(summary, starttime.strftime(CalendarEvent.DATETIMESTRFFORMAT)+"Z", endtime.strftime(CalendarEvent.DATETIMESTRFFORMAT)+"Z")
    
    def construct_events(self, events, summary):
        for event in events:
            date = self.get_date(event)
            dates = self.get_datetimes(event, date)
            self.events.append(self.construct_calendar_event(summary, dates[0], dates[1]))