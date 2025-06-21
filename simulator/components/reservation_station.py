from typing import Optional

class ReservationStation:
    def __init__(self, rs_type):
        self.busy = False
        self.op = None
        self.vj: Optional[int] = None
        self.vk: Optional[int] = None
        self.qj: Optional[int] = None
        self.qk: Optional[int] = None
        self.dest: Optional[int] = None  # Pode ser int (índice do ROB) ou None
        self.cycles_remaining = 0
        self.ready = False
        self.result: Optional[int] = None

class ReservationStations:
    def __init__(self):
        self.stations = {
            'INT': [ReservationStation('INT') for _ in range(4)],
            'FP': [ReservationStation('FP') for _ in range(2)]
        }
