import time
from events import *

class Logger():  # Singleton
    instance = None
    @staticmethod
    def get_instance():
        if Logger.instance == None:
            Logger()
        return Logger.instance

    def __init__(self, logpath = "./."+str(int(time.time()))+".log"):
        Logger.instance = self
        self.filepath = logpath
        self.identation = 0  # Identation level, used to organise the logs
        event_handler = EventHandler.get_instance()
        for event in list(Event):  # Default log all events
            event_handler.add_event_listener(event, lambda event=event: self.log_event(event))

    def increase_identation(self):
        self.identation += 1

    def decrease_identation(self):
        if self.identation >= 1:
            self.identation -= 1

    def log_event(self, event):
        with open(self.filepath, 'a') as log:
            log.write(f"\u001b[38;5;84m {self.identation * '    '}[Event] : {event}\n\u001b[30m")

    def log_info(self, info):
        with open(self.filepath, 'a') as log:
            log.write(f"\u001b[38;5;220m {self.identation * '    '}[Info] : {info}\n\u001b[30m")

    def log_warning(self, warning):
        with open(self.filepath, 'a') as log:
            log.write(f"\u001b[38;5;196m {self.identation * '    '}[Warning] : {warning}\n\u001b[30m")

    def log_action(self, descr):
        with open(self.filepath, 'a') as log:
            log.write(f"\u001b[38;5;141m {self.identation * '    '}[Action] : {descr}\n\u001b[30m")
