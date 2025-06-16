class TwoBitPredictor:
    def __init__(self):
        self.state = '00'  # Estados: 00 (Strong NT), 01 (Weak NT), 10 (Weak T), 11 (Strong T)
        self.history = {}

    def predict(self, pc):
        return self.state in ['11', '10']
