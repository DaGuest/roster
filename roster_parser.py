import os
import re
import pypdf

class RosterParser:
    def convert_rosterpdf_to_text(self):
        try:
            reader = pypdf.PdfReader(os.getcwd() + "/etc/roster.pdf")
            page = reader.pages[0]
            self.text = page.extract_text()
            self.text = re.sub(r"\s+", "", self.text)
            self.text = re.sub(r"\n", "", self.text)
            return True
        except Exception as error:
            print("Unable to convert pdf to text: ", error)
            return False
        
    def parse_flight_events(self):
        pattern_flight_events = r"[A-Z][a-z]{2}\d\d(?:PickUp|C\/I)(?:.*?)\[FDP\d\d:\d\d\]"
        return re.findall(pattern_flight_events, self.text)
    
    def parse_sby_events(self):
        pattern_SBY_event = r"[A-Z][a-z]{2}\d\dSBY\_[A-Z]{4}\d{8}\[FDP\d\d:\d\d\]"
        return re.findall(pattern_SBY_event, self.text)
    
    def parse_sim_events(self):
        pattern = r"[A-Z][a-z]{2}\d\dT(?:.*?)\[FDP\d\d:\d\d\]"
        return re.findall(pattern, self.text)
    
    def parse_medical_events(self):
        pattern = r"[A-Z][a-z]{2}\d\dMMCS(?:.*?)\[FDP\d\d:\d\d\]"
        return re.findall(pattern, self.text)