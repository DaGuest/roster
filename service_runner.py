import signal
import logging
from mail_service import MailService
from roster_parser import RosterParser
from calendar_service import CalendarService

class SignalHandler:
    shutdown_requested = False

    def __init__(self):
        # Subscribe to different signals
        # - keyboard interrupt
        signal.signal(signal.SIGINT, self.request_shutdown)
        # - termination signal
        signal.signal(signal.SIGTERM, self.request_shutdown)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename="etc/log.txt", format='%(asctime)s %(message)s', level=logging.INFO)

    def request_shutdown(self, *args):
        self.logger.info('Shutting down roster service')
        self.shutdown_requested = True

    def is_running(self):
        return not self.shutdown_requested

# Entrypoint for the service.       
def main():
    signal_handler = SignalHandler()
    
    while signal_handler.is_running():
        signal_handler.logger.info("Checking mail for attachement")
        mail_service = MailService()
        mail_service.get_attachment()
        signal_handler.logger.info("Parse PDF to text")
        roster_parser = RosterParser()
        roster_parser.parse_all_events()
        signal_handler.logger.info("Add calendar events to calendar")
        calendar_service = CalendarService()
        calendar_service.get_events(roster_parser.start_period, roster_parser.end_period)
        calendar_service.insert_events(roster_parser.events)
        signal_handler.request_shutdown()

if __name__ == "__main__":
    main()