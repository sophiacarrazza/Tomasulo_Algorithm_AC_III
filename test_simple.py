#!/usr/bin/env python3
"""
Teste simples para verificar se a simulação termina corretamente
"""

from simulator.core import TomasuloCore

def test_simple_program():
    """Testa um programa simples para verificar finalização"""
    core = TomasuloCore()
    
    # Programa muito simples
    program = """ADD R1, R2, R3
ADDI R4, R1, 5"""
    
    print("Carregando programa...")
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
        print(f"Ciclo {cycle_count}: Instrução {core.current_instruction}, Completadas: {core.metrics['completed_instructions']}")
    
    if cycle_count >= max_cycles:
        print("ERRO: Simulação não terminou dentro do limite de ciclos!")
    else:
        print(f"Sucesso! Simulação terminou em {cycle_count} ciclos")
        print(f"Métricas finais:")
        print(f"  IPC: {core.metrics['ipc']:.3f}")
        print(f"  Stalls: {core.metrics['stalls']}")
        print(f"  Bubbles: {core.metrics['bubbles']}")

if __name__ == "__main__":
    test_simple_program() 