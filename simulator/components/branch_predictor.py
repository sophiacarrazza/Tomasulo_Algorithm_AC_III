from collections import defaultdict

class OneBitPredictor:
    """
    Implementa um preditor de desvio dinâmico de 1 bit.
    Este preditor usa uma tabela (Branch History Table - BHT) para armazenar o último
    resultado de cada instrução de desvio.
    """
    def __init__(self):
        # A BHT armazena o último resultado (True para Tomado, False para Não Tomado).
        # O padrão é False (Não Tomado) para desvios nunca vistos antes.
        self.branch_history_table = defaultdict(lambda: False)

    def predict(self, pc):
        """
        Prevê o resultado de um desvio com base no seu endereço (PC).
        Retorna True se a previsão for 'Tomado', False caso contrário.
        """
        return self.branch_history_table[pc]

    def update(self, pc, taken):
        """
        Atualiza a BHT com o resultado real do desvio.
        'taken' é um booleano: True se o desvio foi tomado, False caso contrário.
        """
        self.branch_history_table[pc] = taken

    def __str__(self):
        return "1-Bit Dynamic Predictor"
