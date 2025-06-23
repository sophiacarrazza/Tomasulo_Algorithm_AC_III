def parse_instruction(line):
    """Parse uma instrução MIPS, ignorando comentários."""
    # Remove comentários da linha
    line_without_comments = line.split('#')[0].strip()
    
    parts = line_without_comments.replace(',', ' ').split()
    if not parts or not parts[0]:
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
        
        # Instruções de memória
        'LW': 'MEM',
        'SW': 'MEM',
        
        # Instruções de branch
        'BEQ': 'BRANCH',
        'BNE': 'BRANCH'
    }
    return instruction_types.get(opcode, 'INT')
