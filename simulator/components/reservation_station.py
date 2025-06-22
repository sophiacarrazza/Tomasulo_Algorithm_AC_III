from typing import Optional

class ReservationStation:
    def __init__(self, rs_type):
        self.type = rs_type
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

    def reset(self):
        self.busy = False
        self.op = None
        self.vj = None
        self.vk = None
        self.qj = None
        self.qk = None
        self.dest = None
        self.cycles_remaining = 0
        self.ready = False
        self.result = None

class ReservationStations:
    def __init__(self):
        self.stations = {
            'INT': [ReservationStation('INT') for _ in range(6)],  # 2 ALUs + branches
            'FP': [ReservationStation('FP') for _ in range(4)],    # FP ALU + MUL + DIV
            'MEM': [ReservationStation('MEM') for _ in range(3)]   # Load/Store
        }
    
    def reset(self):
        """Reseta todas as estações de reserva para o estado inicial."""
        for station_type in self.stations:
            for station in self.stations[station_type]:
                station.reset()
