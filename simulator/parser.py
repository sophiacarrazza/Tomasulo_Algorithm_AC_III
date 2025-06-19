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
        'ADD': 'INT',
        'SUB': 'INT', 
        'MUL': 'INT',
        'DIV': 'INT',
        'LW': 'MEM',
        'SW': 'MEM',
        'BEQ': 'BRANCH',
        'BNE': 'BRANCH',
        'J': 'BRANCH',
        'JAL': 'BRANCH'
    }
    return instruction_types.get(opcode, 'INT')
