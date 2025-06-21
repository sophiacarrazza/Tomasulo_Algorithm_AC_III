#!/usr/bin/env python3
"""
Teste para demonstrar o funcionamento superescalar do algoritmo de Tomasulo
"""

from simulator.core import TomasuloCore

def test_superescalar_operation():
    """Testa operações superescalares"""
    print("=== Teste Superescalar - Algoritmo de Tomasulo ===")
    
    # Programa com múltiplas instruções independentes para demonstrar paralelismo
    program = """
    # Programa para demonstrar funcionamento superescalar
    # Múltiplas instruções independentes que podem ser executadas em paralelo
    ADDI R1, R0, 10    # R1 = 10
    ADDI R2, R0, 20    # R2 = 20
    ADDI R3, R0, 30    # R3 = 30
    ADDI R4, R0, 40    # R4 = 40
    ADD R5, R1, R2     # R5 = R1 + R2 (depende de R1 e R2)
    ADD R6, R3, R4     # R6 = R3 + R4 (depende de R3 e R4)
    SUB R7, R1, R3     # R7 = R1 - R3 (depende de R1 e R3)
    SUB R8, R2, R4     # R8 = R2 - R4 (depende de R2 e R4)
    ADD R9, R5, R6     # R9 = R5 + R6 (depende de R5 e R6)
    ADD R10, R7, R8    # R10 = R7 + R8 (depende de R7 e R8)
    """
    
    core = TomasuloCore()
    core.load_program(program)
    
    print(f"Programa carregado com {len(core.instructions)} instruções")
    print("Iniciando simulação superescalar...")
    print()
    
    # Executar ciclos
    max_cycles = 15
    for cycle in range(max_cycles):
        if not core.cycle_step():
            print(f"Simulação finalizada no ciclo {cycle}")
            break
            
        state = core.get_state()
        print(f"Ciclo {cycle}:")
        print(f"  Instruções completadas: {state['metrics']['completed_instructions']}")
        print(f"  IPC: {state['metrics']['ipc']:.2f}")
        print(f"  Stalls: {state['metrics']['stalls']}")
        print(f"  Instruções no ROB: {len(state['rob'])}")
        
        # Mostrar algumas estações de reserva ocupadas
        busy_rs = 0
        for rs_type, stations in state['reservation_stations'].items():
            busy_rs += len(stations)
        print(f"  Estações de reserva ocupadas: {busy_rs}")
        
        # Mostrar alguns registradores
        print("  Registradores:")
        for reg in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10']:
            if reg in state['registers']:
                reg_info = state['registers'][reg]
                tag_info = f" (tag: {reg_info['tag']})" if reg_info['tag'] is not None else ""
                print(f"    {reg}: {reg_info['value']}{tag_info}")
        
        print()
        
        # Parar se todas as instruções foram completadas
        if state['metrics']['completed_instructions'] >= len(core.instructions):
            print("Todas as instruções foram completadas!")
            break
    
    # Resultados finais
    final_state = core.get_state()
    print("=== Resultados Finais ===")
    print(f"Total de ciclos: {final_state['cycle']}")
    print(f"Instruções completadas: {final_state['metrics']['completed_instructions']}")
    print(f"IPC final: {final_state['metrics']['ipc']:.3f}")
    print(f"Total de stalls: {final_state['metrics']['stalls']}")
    print(f"Bubbles (branch mispredictions): {final_state['metrics']['bubbles']}")
    
    # Mostrar registradores finais
    print("\nRegistradores finais:")
    for reg in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10']:
        if reg in final_state['registers']:
            reg_info = final_state['registers'][reg]
            print(f"  {reg}: {reg_info['value']}")
    
    print("\n=== Análise Superescalar ===")
    print("Este teste demonstra:")
    print("1. Issue múltiplo: Até 4 instruções despachadas por ciclo")
    print("2. Execução paralela: Múltiplas unidades funcionais operando simultaneamente")
    print("3. Commit múltiplo: Até 4 instruções commitadas por ciclo")
    print("4. Buffer de reordenamento: 32 entradas para out-of-order execution")
    print("5. Estações de reserva expandidas: 6 INT, 4 FP, 3 MEM")
    print("6. Renomeação de registradores: Elimina dependências WAR e WAW")
    print("7. Paralelismo real: Observe como R5 e R6 são calculados em paralelo")
    print("8. Out-of-order execution: Instruções são executadas assim que os operandos estão disponíveis")

if __name__ == "__main__":
    test_superescalar_operation() 