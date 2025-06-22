#!/usr/bin/env python3
"""
Teste do preditor de desvio e execução especulativa
"""

from simulator.core import TomasuloCore

def test_branch_prediction():
    """Testa o preditor de desvio com um programa que tem desvios condicionais"""
    
    # Programa de teste com desvios
    program = """
# Programa para testar preditor de desvio
# R1 = 5, R2 = 3, R3 = 0
ADDI R1, R0, 5    # R1 = 5
ADDI R2, R0, 3    # R2 = 3
ADDI R3, R0, 0    # R3 = 0

# Primeiro desvio - deve ser tomado (R1 > R2)
BNE R1, R2, loop1 # Se R1 != R2, vai para loop1

# Instruções que não devem ser executadas se o desvio for tomado
ADDI R4, R0, 100  # R4 = 100 (não deve ser executado)
ADDI R5, R0, 200  # R5 = 200 (não deve ser executado)

loop1:
ADDI R3, R3, 1    # R3 = R3 + 1
SUB R1, R1, R2    # R1 = R1 - R2

# Segundo desvio - não deve ser tomado (R1 = 2, R2 = 3)
BNE R1, R2, loop1 # Se R1 != R2, volta para loop1

# Instruções que devem ser executadas
ADDI R6, R0, 300  # R6 = 300
ADDI R7, R0, 400  # R7 = 400
"""

    print("=== Teste do Preditor de Desvio ===")
    print("Programa:")
    print(program)
    
    # Criar e executar o simulador
    core = TomasuloCore()
    core.load_program(program)
    
    print(f"\nTotal de instruções: {core.metrics['total_instructions']}")
    print(f"Labels mapeados: {core.label_map}")
    
    # Executar passo a passo
    cycle = 0
    max_cycles = 50
    
    while cycle < max_cycles:
        if not core.cycle_step():
            break
        cycle += 1
        
        # Mostrar estado a cada 5 ciclos
        if cycle % 5 == 0:
            print(f"\n--- Ciclo {cycle} ---")
            print(f"PC: {core.pc}")
            print(f"Instruções completadas: {core.metrics['completed_instructions']}")
            print(f"Stalls: {core.metrics['stalls']}")
            print(f"Mispredictions: {core.metrics['mispredictions']}")
            print(f"IPC: {core.metrics['ipc']:.2f}")
    
    print(f"\n=== Resultado Final ===")
    print(f"Ciclos executados: {cycle}")
    print(f"Instruções completadas: {core.metrics['completed_instructions']}")
    print(f"Stalls: {core.metrics['stalls']}")
    print(f"Mispredictions: {core.metrics['mispredictions']}")
    print(f"IPC: {core.metrics['ipc']:.2f}")
    
    # Mostrar estado final dos registradores
    print(f"\nEstado final dos registradores:")
    for reg_name, value in core.registers.values.items():
        if value != 0:  # Só mostrar registradores não-zero
            print(f"{reg_name}: {value}")
    
    # Verificar se o preditor está funcionando
    print(f"\nPreditor de desvio: {core.bp}")
    print(f"Tabela de histórico do preditor: {dict(core.bp.branch_history_table)}")

if __name__ == "__main__":
    test_branch_prediction() 