import os
import re
import pypdf

class RosterParser:
    def convert_rosterpdf_to_text(self):
        reader = pypdf.PdfReader(os.getcwd() + "/etc/roster.pdf")
        page = reader.pages[0]
        self.text = page.extract_text()
        self.text = re.sub(r"\s+", "", self.text)
        return self.text
    
    def parse_flight_events(self):
        events = []
        pattern_AMS_event = r"([A-Z][a-z]{2}\d\dC\/I[A-Z]{3}\d{4}(?:\KL(\d{4}|\d{3})[A-Z]{3}\d{8}[A-Z]{3}(?:E7W|E90|\d{3}))*C\/O\d{4}[A-Z]{3}\[FDP\d\d:\d\d\]"
        events.append(re.findall(pattern_AMS_event, self.text))
        return events