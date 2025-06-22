#!/usr/bin/env python3
"""
Teste simples para isolar o problema dos desvios
"""

from simulator.core import TomasuloCore

def simple_branch_test():
    """Teste simples de desvio"""
    
    program = """# Teste simples
ADDI R1, R0, 5    # R1 = 5
BNE R1, R0, end   # Se R1 != R0, vai para end
ADDI R2, R0, 100  # Não deve ser executado
end:
ADDI R3, R0, 1    # R3 = 1"""

    print("=== Teste Simples de Desvio ===")
    print("Programa:")
    print(program)
    
    core = TomasuloCore()
    core.load_program(program)
    
    print(f"\nTotal de instruções: {core.metrics['total_instructions']}")
    print(f"Labels mapeados: {core.label_map}")
    
    # Executar passo a passo
    for cycle in range(8):
        print(f"\n--- Ciclo {cycle} ---")
        print(f"PC: {core.pc}")
        
        # Mostrar registradores
        print("Registradores:")
        for reg in ['R0', 'R1', 'R2', 'R3']:
            print(f"  {reg}: {core.registers.values[reg]}")
        
        # Mostrar ROB
        print("ROB:")
        for i, entry in enumerate(core.rob.entries):
            if entry.state != 'Empty':
                print(f"  [{i}] {entry.state}: {entry.instruction}")
        
        # Mostrar estações de reserva
        print("Estações de Reserva:")
        for rs_type, stations in core.reservation_stations.stations.items():
            for i, rs in enumerate(stations):
                if rs.busy:
                    print(f"  {rs_type}[{i}]: {rs.op} vj={rs.vj} vk={rs.vk} qj={rs.qj} qk={rs.qk}")
        
        if not core.cycle_step():
            print("Simulação terminou!")
            break
    
    print(f"\n=== Resultado Final ===")
    print("Registradores finais:")
    for reg in ['R0', 'R1', 'R2', 'R3']:
        print(f"  {reg}: {core.registers.values[reg]}")

if __name__ == "__main__":
    simple_branch_test() 