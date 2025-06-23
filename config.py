# Configurações do simulador de Tomasulo

# Configurações do ROB
ROB_SIZE = 32

# Configurações das estações de reserva
RESERVATION_STATIONS = {
    'INT': 4,  # 4 estações para instruções inteiras
    'FP': 2    # 2 estações para instruções de ponto flutuante
}

# Latências das instruções (em ciclos)
INSTRUCTION_LATENCIES = {
    'ADD': 1,
    'ADDI': 0,
    'SUB': 1,
    'MUL': 3,
    'DIV': 10,
    'LW': 2,
    'SW': 1,
    'BEQ': 1,
    'BNE': 1,
    'J': 1,
    'JAL': 1
}

# Penalidade de branch misprediction
BRANCH_PENALTY = 10

# Configurações da GUI
GUI_REFRESH_RATE = 500  # ms entre atualizações da GUI
GUI_WINDOW_SIZE = "1400x900"
