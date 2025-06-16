class ROBEntry:
    def __init__(self):
        self.state = 'Empty'
        self.instruction = None
        self.destination = None
        self.value = None
        self.ready = False

class ReorderBuffer:
    def __init__(self, size=32):
        self.entries = [ROBEntry() for _ in range(size)]
        self.head = 0
        self.tail = 0
