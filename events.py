from enum import Enum, auto

class Event(Enum):
    GAME_OVER = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    VALID = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    START_SELECTION = auto()
    END_SELECTION = auto()
    TURN_END = auto()
    MIDDLE_CARD_TAPPED = auto()
    CARD_USED = auto()
    CARD_TAPPED = auto()
    TEST = auto()  # Will be used to trigger an action to test

class EventHandler():
    instance = None
    @staticmethod
    def get_instance():
        if EventHandler.instance == None:
            EventHandler()
        return EventHandler.instance

    def __init__(self):
        EventHandler.instance = self
        self.listeners = {event : [] for event in (Event)}
        self.to_remove = []
        self.add_event_listener(Event.TURN_END, self.clean_listeners)

    def add_event_listener(self, event, callback):
        self.listeners[event].append(callback)

    def add_event_listener_turn(self, event, callback):  # Since cleaning listeners was such a pain, this should do it properly
        self.add_event_listener(event, callback)
        self.to_remove.append((event, callback))

    def add_event_listener_once(self, event, callback):  # To remove the listener once used once
        def fun():
            callback()
            self.remove_event_listener(event, fun)
        self.add_event_listener(event, fun)            

    def clean_listeners(self):
        for event, listener in self.to_remove:
            self.remove_event_listener(event, listener)
        self.to_remove = []

    def remove_event_listener(self, event, callback):
        self.listeners[event].remove(callback)

    def use_event(self, event):
        for listener in self.listeners[event]:
            try:
                listener()
            except Exception as e:
                from logger import Logger
                Logger.get_instance().log_event(event)
                Logger.get_instance().log_warning(e)
                raise e
