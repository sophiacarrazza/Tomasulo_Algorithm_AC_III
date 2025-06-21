#!/usr/bin/env python3
"""
Teste para demonstrar o problema de renomeação de registradores
e dependências falsas no algoritmo de Tomasulo
"""

from simulator.core import TomasuloCore

def test_register_renaming():
    """Testa renomeação de registradores e eliminação de dependências falsas"""
    print("=== Teste de Renomeação de Registradores ===")
    
    # Programa com dependências falsas
    # ADD R1, R2, R3    # Instrução 1: R1 = R2 + R3
    # ADD R4, R1, R6    # Instrução 2: R4 = R1 + R6 (depende da 1)
    # ADD R6, R8, R7    # Instrução 3: R6 = R8 + R7 (dependência falsa com 2)
    # ADD R6, R8, R7    # Instrução 4: R6 = R8 + R7 (dependência falsa com 2 e 3)
    
    program = """
    # Programa para testar renomeação de registradores
    # Instrução 1: R1 = R2 + R3
    ADD R1, R2, R3
    
    # Instrução 2: R4 = R1 + R6 (depende da 1)
    ADD R4, R1, R6
    
    # Instrução 3: R6 = R8 + R7 (dependência falsa com 2)
    ADD R6, R8, R7
    
    # Instrução 4: R6 = R8 + R7 (dependência falsa com 2 e 3)
    ADD R6, R8, R7
    """
    
    core = TomasuloCore()
    
    # Inicializar registradores com valores conhecidos
    core.registers.values['R2'] = 10
    core.registers.values['R3'] = 20
    core.registers.values['R6'] = 30
    core.registers.values['R7'] = 40
    core.registers.values['R8'] = 50
    
    core.load_program(program)
    
    print(f"Programa carregado com {len(core.instructions)} instruções")
    print("Valores iniciais dos registradores:")
    for reg in ['R2', 'R3', 'R6', 'R7', 'R8']:
        print(f"  {reg}: {core.registers.values[reg]}")
    print()
    
    print("Iniciando simulação...")
    print("Esperado: Instruções 1, 3 e 4 podem executar em paralelo")
    print("         Instrução 2 deve esperar pela 1")
    print()
    
    # Executar ciclos
    max_cycles = 10
    for cycle in range(max_cycles):
        if not core.cycle_step():
            print(f"Simulação finalizada no ciclo {cycle}")
            break
            
        state = core.get_state()
        print(f"Ciclo {cycle}:")
        print(f"  Instruções completadas: {state['metrics']['completed_instructions']}")
        print(f"  Instruções no ROB: {len(state['rob'])}")
        
        # Mostrar estado das estações de reserva
        print("  Estações de reserva ocupadas:")
        for rs_type, stations in state['reservation_stations'].items():
            if stations:
                print(f"    {rs_type}: {len(stations)} estações ocupadas")
                for rs in stations:
                    print(f"      Op: {rs['op']}, Dest: {rs['dest']}, Ready: {rs['ready']}, Cycles: {rs['cycles_remaining']}")
                    print(f"      Vj: {rs['vj']}, Vk: {rs['vk']}, Qj: {rs['qj']}, Qk: {rs['qk']}")
        
        # Mostrar registradores
        print("  Registradores:")
        for reg in ['R1', 'R4', 'R6']:
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
    
    # Mostrar registradores finais
    print("\nRegistradores finais:")
    for reg in ['R1', 'R4', 'R6']:
        if reg in final_state['registers']:
            reg_info = final_state['registers'][reg]
            print(f"  {reg}: {reg_info['value']}")
    
    print("\n=== Análise ===")
    print("Problema identificado:")
    print("1. Instrução 2 (ADD R4, R1, R6) deveria esperar apenas pela instrução 1")
    print("2. Instruções 3 e 4 (ADD R6, R8, R7) deveriam executar em paralelo com 1")
    print("3. A renomeação de registradores não está eliminando dependências falsas")
    print("4. O ROB deveria permitir execução fora de ordem")

if __name__ == "__main__":
    test_register_renaming() 