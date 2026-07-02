class Resultado:
    def __init__(self, id, aposta_id, vencedor_id, descricao):
        self.id = id
        self.aposta_id = aposta_id
        self.vencedor_id = vencedor_id
        self.descricao = descricao

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Resultado(dados['id'], dados['aposta_id'], dados['vencedor_id'], dados['descricao'])
