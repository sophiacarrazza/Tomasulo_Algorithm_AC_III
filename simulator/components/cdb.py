class CommonDataBus:
    def __init__(self):
        self.busy = False
        self.current_value = None
        self.source = None
        self.listeners = []

    def broadcast(self, value, tag):
        self.busy = True
        self.current_value = value
        self.source = tag
        for listener in self.listeners:
            listener.notify(tag, value)
        self.busy = False
