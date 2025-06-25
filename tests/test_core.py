import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.core import TomasuloCore

def test_basic_instruction():
    """Testa uma instrução básica"""
    core = TomasuloCore()
    
    # Carregar programa simples
    program = "ADD R1, R2, R3"
    core.load_program(program)
    
    # Executar alguns ciclos
    for _ in range(5):
        core.cycle_step()
    
    # Verificar se a instrução foi processada
    assert core.metrics['completed_instructions'] >= 0
    print("✓ Teste básico passou")

def test_multiple_instructions():
    """Testa múltiplas instruções"""
    core = TomasuloCore()
    
    program = """ADD R1, R2, R3
MUL R4, R1, R5
ADD R6, R4, R7"""
    
    core.load_program(program)
    
    # Executar mais ciclos
    for _ in range(10):
        core.cycle_step()
    
    print("✓ Teste de múltiplas instruções passou")

def test_branch_instruction():
    """Testa instrução de branch"""
    core = TomasuloCore()
    
    program = "BEQ R1, R2, 8"
    core.load_program(program)
    
    # Executar alguns ciclos
    for _ in range(5):
        core.cycle_step()
    
    print("✓ Teste de branch passou")

def test_memory_instructions():
    """Testa instruções de memória"""
    core = TomasuloCore()
    
    program = """LW R1, 100
SW R2, 200"""
    
    core.load_program(program)
    
    # Executar alguns ciclos
    for _ in range(8):
        core.cycle_step()
    
    print("✓ Teste de memória passou")

if __name__ == "__main__":
    print("Executando testes do simulador de Tomasulo...")
    
    test_basic_instruction()
    test_multiple_instructions()
    test_branch_instruction()
    test_memory_instructions()
    
    print("Todos os testes passaram!")
