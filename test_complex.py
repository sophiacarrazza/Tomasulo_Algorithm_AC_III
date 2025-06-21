#!/usr/bin/env python3
"""
Teste com programa complexo para verificar finalização
"""

from simulator.core import TomasuloCore

def test_complex_program():
    """Testa o programa complexo da GUI"""
    core = TomasuloCore()
    
    # Programa complexo da GUI
    program = """# Programa de exemplo para demonstrar o algoritmo de Tomasulo
# Instruções básicas
ADD R1, R2, R3
MUL R4, R1, R5

# Instruções de imediato
ADDI R6, R4, 10
SUBI R7, R6, 5
ANDI R8, R7, 0xFF
ORI R9, R8, 0x100

# Instruções lógicas
AND R10, R9, R8
OR R11, R10, R7
XOR R12, R11, R6

# Instruções de shift
SLLI R13, R12, 2
SRLI R14, R13, 1

# Instruções de memória
LW R15, 100
SW R14, 200

# Instruções de branch
BEQ R1, R2, 8
BNE R3, R4, 12
BLT R5, R6, 16

# Instruções de comparação
SLTI R16, R15, 50
SLTIU R17, R16, 100"""
    
    print("Carregando programa complexo...")
    core.load_program(program)
    print(f"Total de instruções: {len(core.instructions)}")
    
    print("\nExecutando simulação...")
    cycle_count = 0
    max_cycles = 100  # Limite de segurança
    
    while cycle_count < max_cycles:
        if not core.cycle_step():
            print(f"Simulação terminou no ciclo {cycle_count}")
            break
        cycle_count += 1
        if cycle_count % 5 == 0:  # Mostrar progresso a cada 5 ciclos
            print(f"Ciclo {cycle_count}: Instrução {core.current_instruction}, Completadas: {core.metrics['completed_instructions']}")
    
    if cycle_count >= max_cycles:
        print("ERRO: Simulação não terminou dentro do limite de ciclos!")
    else:
        print(f"Sucesso! Simulação terminou em {cycle_count} ciclos")
        print(f"Métricas finais:")
        print(f"  IPC: {core.metrics['ipc']:.3f}")
        print(f"  Stalls: {core.metrics['stalls']}")
        print(f"  Bubbles: {core.metrics['bubbles']}")
        print(f"  Instruções completadas: {core.metrics['completed_instructions']}")

if __name__ == "__main__":
    test_complex_program() 