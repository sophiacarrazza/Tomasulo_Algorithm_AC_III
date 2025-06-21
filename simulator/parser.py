def parse_instruction(line):
    """Parse uma instrução MIPS"""
    parts = line.replace(',', ' ').split()
    if len(parts) < 1:
        return None
    
    opcode = parts[0]
    operands = parts[1:] if len(parts) > 1 else []
    
    return {
        'opcode': opcode,
        'operands': operands,
        'type': _get_instruction_type(opcode)
    }

def _get_instruction_type(opcode):
    """Retorna o tipo da instrução baseado no opcode"""
    instruction_types = {
        # Instruções aritméticas
        'ADD': 'INT',
        'SUB': 'INT', 
        'MUL': 'INT',
        'DIV': 'INT',
        
        # Instruções de imediato
        'ADDI': 'INT',
        'SUBI': 'INT',
        'MULI': 'INT',
        'DIVI': 'INT',
        'ANDI': 'INT',
        'ORI': 'INT',
        'XORI': 'INT',
        'SLTI': 'INT',  # Set Less Than Immediate
        'SLTIU': 'INT', # Set Less Than Immediate Unsigned
        
        # Instruções de memória
        'LW': 'MEM',
        'SW': 'MEM',
        'LBU': 'MEM',  # Load Byte Unsigned
        'LHU': 'MEM',  # Load Halfword Unsigned
        'SB': 'MEM',   # Store Byte
        'SH': 'MEM',   # Store Halfword
        
        # Instruções de branch
        'BEQ': 'BRANCH',
        'BNE': 'BRANCH',
        'BLT': 'BRANCH',  # Branch Less Than
        'BLE': 'BRANCH',  # Branch Less or Equal
        'BGT': 'BRANCH',  # Branch Greater Than
        'BGE': 'BRANCH',  # Branch Greater or Equal
        'J': 'BRANCH',
        'JAL': 'BRANCH',
        'JR': 'BRANCH',   # Jump Register
        'JALR': 'BRANCH', # Jump and Link Register
        
        # Instruções lógicas
        'AND': 'INT',
        'OR': 'INT',
        'XOR': 'INT',
        'NOR': 'INT',
        'SLL': 'INT',  # Shift Left Logical
        'SRL': 'INT',  # Shift Right Logical
        'SRA': 'INT',  # Shift Right Arithmetic
        'SLLI': 'INT', # Shift Left Logical Immediate
        'SRLI': 'INT', # Shift Right Logical Immediate
        'SRAI': 'INT', # Shift Right Arithmetic Immediate
    }
    return instruction_types.get(opcode, 'INT')
