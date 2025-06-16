def parse_instruction(line):
    parts = line.replace(',', ' ').split()
    return {
        'opcode': parts[0],
        'operands': parts[1:],
        'type': _get_instruction_type(parts[0])
    }

def _get_instruction_type(opcode):
    instruction_types = {
        'ADD': 'INT',
        'LW': 'MEM',
        'BEQ': 'BRANCH'
    }
    return instruction_types.get(opcode, 'UNKNOWN')
