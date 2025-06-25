#!/usr/bin/env python3
"""
Teste para verificar se os desvios estão funcionando corretamente
"""

from simulator.core import TomasuloCore

def test_branch_fix():
    """Testa se os desvios estão sendo executados corretamente"""
    
    program = """# Programa para testar desvios
ADDI R1, R0, 5    # R1 = 5
ADDI R2, R0, 3    # R2 = 3
ADDI R3, R0, 0    # R3 = 0

# Primeiro desvio - deve ser tomado (R1 != R2)
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
ADDI R7, R0, 400  # R7 = 400"""

    print("=== Teste de Correção dos Desvios ===")
    print("Programa:")
    print(program)
    
    # Criar e executar o simulador
    core = TomasuloCore()
    core.load_program(program)
    
    print(f"\nTotal de instruções: {core.metrics['total_instructions']}")
    print(f"Labels mapeados: {core.label_map}")
    
    # Executar até o fim
    cycle = 0
    max_cycles = 30
    
    while cycle < max_cycles:
        if not core.cycle_step():
            break
        cycle += 1
        
        # Mostrar estado a cada 5 ciclos
        if cycle % 5 == 0:
            print(f"\n--- Ciclo {cycle} ---")
            print(f"PC: {core.pc}")
            print(f"Instruções completadas: {core.metrics['completed_instructions']}")
            print(f"Mispredictions: {core.metrics['mispredictions']}")
    
    print(f"\n=== Resultado Final ===")
    print(f"Ciclos executados: {cycle}")
    print(f"Instruções completadas: {core.metrics['completed_instructions']}")
    print(f"Mispredictions: {core.metrics['mispredictions']}")
    
    # Mostrar estado final dos registradores
    print(f"\nEstado final dos registradores:")
    for reg_name, value in core.registers.values.items():
        if value != 0:  # Só mostrar registradores não-zero
            print(f"{reg_name}: {value}")
    
    # Verificar se os desvios funcionaram
    print(f"\n=== Análise dos Desvios ===")
    print(f"R1 final: {core.registers.values['R1']} (esperado: 2)")
    print(f"R2 final: {core.registers.values['R2']} (esperado: 3)")
    print(f"R3 final: {core.registers.values['R3']} (esperado: 1)")
    print(f"R4 final: {core.registers.values['R4']} (esperado: 0 - não executado)")
    print(f"R5 final: {core.registers.values['R5']} (esperado: 0 - não executado)")
    print(f"R6 final: {core.registers.values['R6']} (esperado: 300)")
    print(f"R7 final: {core.registers.values['R7']} (esperado: 400)")
    
    # Verificar se o preditor funcionou
    print(f"\nPreditor de desvio: {core.bp}")
    print(f"Tabela de histórico: {dict(core.bp.branch_history_table)}")

    # No método _execute, ao finalizar o branch:
    if rob_entry.instruction and rob_entry.instruction['type'] == 'BRANCH':
        actual_taken = bool(result)
        # Atualize o último branch no histórico:
        if self.branch_history and self.branch_history[-1]['pc'] == rob_entry.pc and self.branch_history[-1]['actual'] is None:
            self.branch_history[-1]['actual'] = actual_taken

if __name__ == "__main__":
   