import signal

class SignalHandler:
    shutdown_requested = False

    def __init__(self):
        # Subscribe to different signals
        # - keyboard interrupt
        signal.signal(signal.SIGINT, self.request_shutdown)
        # - termination signal
        signal.signal(signal.SIGTERM, self.request_shutdown)

    def request_shutdown(self, *args):
        print('Shutting down roster service')
        self.shutdown_requested = True

    def is_running(self):
        return not self.shutdown_requested

# Entrypoint for the service.       
def main():
    signal_handler = SignalHandler()
    
    while signal_handler.is_running():
        print("Check for new roster")
        print("Parse PDF to text")
        print("Construct calendar events from text")
        print("Add calendar events to calendar")

if __name__ == "__main__":
    main()