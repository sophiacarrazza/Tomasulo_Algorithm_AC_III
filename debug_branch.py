#!/usr/bin/env python3
"""
Debug para verificar a execução dos desvios
"""

from simulator.core import TomasuloCore

def debug_branch():
    """Debug da execução dos desvios"""
    
    program = """# Debug de desvios
ADDI R1, R0, 5    # R1 = 5
ADDI R2, R0, 3    # R2 = 3
BNE R1, R2, loop1 # Se R1 != R2, vai para loop1
ADDI R4, R0, 100  # Não deve ser executado
loop1:
ADDI R3, R0, 1    # R3 = 1"""

    print("=== Debug de Desvios ===")
    print("Programa:")
    print(program)
    
    core = TomasuloCore()
    core.load_program(program)
    
    print(f"\nTotal de instruções: {core.metrics['total_instructions']}")
    print(f"Labels mapeados: {core.label_map}")
    
    # Executar passo a passo
    for cycle in range(10):
        print(f"\n--- Ciclo {cycle} ---")
        print(f"PC antes: {core.pc}")
        
        # Mostrar estado dos registradores
        print("Registradores:")
        for reg in ['R0', 'R1', 'R2', 'R3', 'R4']:
            print(f"  {reg}: {core.registers.values[reg]}")
        
        # Mostrar estado do ROB
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
        
        print(f"PC depois: {core.pc}")
    
    print(f"\n=== Resultado Final ===")
    print("Registradores finais:")
    for reg in ['R0', 'R1', 'R2', 'R3', 'R4']:
        print(f"  {reg}: {core.registers.values[reg]}")

if __name__ == "__main__":
    debug_branch() 