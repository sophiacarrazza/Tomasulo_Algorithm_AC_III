class ReservationStation:
    def __init__(self, rs_type):
        self.busy = False
        self.op = None
        self.vj = None
        self.vk = None
        self.qj = None
        self.qk = None
        self.dest = None
        self.cycles_remaining = 0

class ReservationStations:
    def __init__(self):
        self.stations = {
            'INT': [ReservationStation('INT') for _ in range(4)],
            'FP': [ReservationStation('FP') for _ in range(2)]
        }
