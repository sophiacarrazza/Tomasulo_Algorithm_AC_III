from components.branch_predictor import TwoBitPredictor
from components.cdb import CommonDataBus
#from components.register_bank import RegisterBank
from components.reorder_buffer import ReorderBuffer
from components.reservation_station import ReservationStations

class TomasuloCore:
    def __init__(self):
        self.cycle = 0
        self.instructions = []
        self.reservation_stations = ReservationStations()
        self.rob = ReorderBuffer(size=32)
        self.cdb = CommonDataBus()
        #self.registers = RegisterBank()
        self.bp = TwoBitPredictor()
        self.metrics = {
            'ipc': 0.0,
            'stalls': 0
        }

    def cycle_step(self):
        self._issue()
        self._execute()
        self._write_result()
        self._commit()
        self.cycle += 1
        self._update_metrics()

    def _issue(self):
        # Lógica de despacho de instruções
        pass
