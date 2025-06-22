from typing import Optional, Dict, Any, Union

class ROBEntry:
    def __init__(self):
        self.state: str = 'Empty'
        self.instruction: Optional[Dict[str, Any]] = None
        self.destination: Optional[Union[str, int]] = None # Registrador de destino (str) ou índice do ROB para desvios (int)
        self.value: Optional[int] = None
        self.ready: bool = False
        # Campos para especulação de desvio
        self.pc: int = -1
        self.predicted_taken: Optional[bool] = None
        self.actual_outcome: Optional[bool] = None
        self.target_pc: int = -1
        self.old_tag: Optional[int] = None

class ReorderBuffer:
    def __init__(self, size=32):
        self.entries = [ROBEntry() for _ in range(size)]
        self.head = 0
        self.tail = 0
