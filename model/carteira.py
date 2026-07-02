class Carteira:
    def __init__(self, id, usuario_id, saldo=0.0):
        self.id = id
        self.usuario_id = usuario_id
        self.saldo = saldo

    def adicionar_saldo(self, valor):
        if valor <= 0:
            raise ValueError('O valor deve ser positivo.')
        self.saldo += valor

    def debitar(self, valor):
        if valor <= 0:
            raise ValueError('O valor deve ser positivo.')
        if self.saldo < valor:
            raise ValueError('Saldo insuficiente.')
        self.saldo -= valor

    def creditar(self, valor):
        if valor <= 0:
            raise ValueError('O valor deve ser positivo.')
        self.saldo += valor

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Carteira(dados['id'], dados['usuario_id'], dados['saldo'])
