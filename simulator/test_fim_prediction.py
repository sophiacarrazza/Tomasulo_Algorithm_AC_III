#!/usr/bin/env python3
"""
Teste para verificar se o bit de predição é resetado para 0 quando "FIM" é encontrado.
"""

import sys
import os

# Adicionar o diretório do simulador ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import TomasuloCore

def test_fim_prediction_reset():
    """Testa se o bit de predição é resetado para 0 quando 'FIM' é encontrado."""
    
    # Criar uma instância do simulador
    core = TomasuloCore()
    
    # Definir o bit de predição inicialmente como True (1)
    core.bp.last_result = True
    print(f"Bit de predição inicial: {core.bp.last_result}")
    
    # Programa de teste sem "FIM"
    program_without_fim = """
    ADD R1, R2, R3
    BEQ R1, R2, label1
    ADD R4, R5, R6
    label1:
    ADD R7, R8, R9
    """
    
    # Carregar programa sem "FIM"
    core.load_program(program_without_fim)
    print(f"Bit de predição após programa sem FIM: {core.bp.last_result}")
    
    # Verificar que o bit não foi alterado
    assert core.bp.last_result == True, "Bit de predição não deveria ter sido alterado"
    
    # Programa de teste com "FIM"
    program_with_fim = """
    ADD R1, R2, R3
    BEQ R1, R2, label1
    ADD R4, R5, R6
    label1:
    ADD R7, R8, R9
    FIM
    """
    
    # Carregar programa com "FIM"
    core.load_program(program_with_fim)
    print(f"Bit de predição após programa com FIM: {core.bp.last_result}")
    
    # Verificar que o bit foi resetado para False (0)
    assert core.bp.last_result == False, "Bit de predição deveria ter sido resetado para False"
    
    print("✅ Teste passou! O bit de predição foi resetado corretamente quando 'FIM' foi encontrado.")

def test_fim_prediction_case_insensitive():
    """Testa se a detecção de 'FIM' é case-insensitive."""
    
    core = TomasuloCore()
    core.bp.last_result = True
    
    # Testar diferentes variações de "FIM"
    variations = ["fim", "Fim", "FIM", "FiM"]
    
    for variation in variations:
        program = f"""
        ADD R1, R2, R3
        {variation}
        """
        
        core.load_program(program)
        print(f"Bit de predição após '{variation}': {core.bp.last_result}")
        
        assert core.bp.last_result == False, f"Bit de predição deveria ter sido resetado para False com '{variation}'"
    
    print("✅ Teste case-insensitive passou!")

if __name__ == "__main__":
    print("Executando testes para verificar reset do bit de predição...")
    print("=" * 60)
    
    test_fim_prediction_reset()
    print()
    test_fim_prediction_case_insensitive()
    
    print("\n🎉 Todos os testes passaram!") 