class Resultado:
    def __init__(self, id, aposta_id, vencedor_id, descricao,
                 vencedores_ids=None, opcao_vencedora=None):
        self.id = id
        self.aposta_id = aposta_id
        self.vencedor_id = vencedor_id
        self.descricao = descricao
        self.vencedores_ids = list(vencedores_ids or ([vencedor_id] if vencedor_id is not None else []))
        self.opcao_vencedora = opcao_vencedora

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Resultado(
            dados['id'], dados['aposta_id'], dados.get('vencedor_id'), dados['descricao'],
            dados.get('vencedores_ids'), dados.get('opcao_vencedora')
        )
