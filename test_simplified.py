#!/usr/bin/env python3
"""
Teste com instruções simplificadas
"""

from simulator.core import TomasuloCore

def test_simplified_program():
    """Testa o programa com instruções simplificadas"""
    core = TomasuloCore()
    
    # Programa com instruções simplificadas
    program = """# Programa com instruções simplificadas
ADD R1, R2, R3
MUL R4, R1, R5
ADDI R6, R4, 10
SUB R7, R6, R5
LW R8, 100
SW R7, 200
BEQ R1, R2, 8
BNE R3, R4, 12
DIV R9, R8, R1
ADD R10, R9, R6"""
    
    print("Carregando programa simplificado...")
    core.load_program(program)
    print(f"Total de instruções: {len(core.instructions)}")
    
    print("\nExecutando simulação...")
    cycle_count = 0
    max_cycles = 50  # Limite de segurança
    
    while cycle_count < max_cycles:
        if not core.cycle_step():
            print(f"Simulação terminou no ciclo {cycle_count}")
            break
        cycle_count += 1
        if cycle_count % 3 == 0:  # Mostrar progresso a cada 3 ciclos
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
    test_simplified_program() 