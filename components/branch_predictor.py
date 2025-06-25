from collections import defaultdict

class OneBitPredictor:
    """
    Implementa um preditor de desvio dinâmico de 1 bit.
    Este preditor usa uma tabela (Branch History Table - BHT) para armazenar o último
    resultado de cada instrução de desvio.
    """
    def __init__(self):
        self.last_result = False  # bit global

    def predict(self, pc):
        """
        Prevê o resultado de um desvio com base no seu endereço (PC).
        Retorna True se a previsão for 'Tomado', False caso contrário.
        """
        return self.last_result

    def update(self, pc, taken):
        """
        Atualiza a BHT com o resultado real do desvio.
        'taken' é um booleano: True se o desvio foi tomado, False caso contrário.
        """
        self.last_result = taken

    def __str__(self):
        return "1-Bit Global Predictor"
