#!/usr/bin/env python3
"""
Teste para verificar se a contagem de bolhas está funcionando corretamente.
As bolhas devem ser contadas apenas quando há predição incorreta de "não desvio" 
que na verdade resultou em desvio.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import TomasuloCore

def test_bubble_counting():
    """Testa a contagem de bolhas para diferentes cenários de predição de branch"""
    
    # Programa de teste com branches
    test_program = """
    # Programa de teste para verificar contagem de bolhas
    ADD R1, R2, R3
    ADDI R4, R1, 5
    BEQ R1, R4, loop  # Este branch será tomado (R1 != R4)
    ADD R5, R1, R2
    ADD R6, R3, R4
loop:
    SUB R7, R1, R2
    BNE R7, R0, end   # Este branch será tomado (R7 != 0)
    ADD R8, R1, R3
end:
    ADD R9, R1, R4
    """
    
    core = TomasuloCore()
    core.load_program(test_program)
    
    print("=== Teste de Contagem de Bolhas ===")
    print("Programa de teste:")
    print(test_program)
    print("\nExecutando simulação...")
    
    # Executar alguns ciclos para ver o comportamento
    cycles_to_run = 20
    for i in range(cycles_to_run):
        if not core.cycle_step():
            break
        print(f"Ciclo {i+1}: Bolhas = {core.metrics['bubbles']}, Mispredictions = {core.metrics['mispredictions']}")
    
    print(f"\n=== Resultados Finais ===")
    print(f"Total de ciclos: {core.cycle}")
    print(f"Total de bolhas: {core.metrics['bubbles']}")
    print(f"Total de mispredictions: {core.metrics['mispredictions']}")
    print(f"Instruções completadas: {core.metrics['completed_instructions']}")
    print(f"IPC: {core.metrics['ipc']:.3f}")
    
    # Verificar se as bolhas foram contadas corretamente
    # Deve haver 2 bolhas por cada predição incorreta de "não desvio" que resultou em desvio
    expected_bubbles = core.metrics['mispredictions'] * 2
    if core.metrics['bubbles'] == expected_bubbles:
        print(f"\n✅ SUCESSO: Bolhas contadas corretamente!")
        print(f"   Esperado: {expected_bubbles}, Obtido: {core.metrics['bubbles']}")
    else:
        print(f"\n❌ ERRO: Contagem de bolhas incorreta!")
        print(f"   Esperado: {expected_bubbles}, Obtido: {core.metrics['bubbles']}")
    
    return core.metrics['bubbles'] == expected_bubbles

if __name__ == "__main__":
    success = test_bubble_counting()
    sys.exit(0 if success else 1) 