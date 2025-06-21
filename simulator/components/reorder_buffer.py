from typing import Optional

class ROBEntry:
    def __init__(self):
        self.state = 'Empty'
        self.instruction = None
        self.destination: Optional[int] = None
        self.value: Optional[int] = None
        self.ready = False

class ReorderBuffer:
    def __init__(self, size=32):
        self.entries = [ROBEntry() for _ in range(size)]
        self.head = 0
        self.tail = 0
