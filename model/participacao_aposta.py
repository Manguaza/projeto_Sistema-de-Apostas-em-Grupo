class ParticipacaoAposta:
    def __init__(self, id, aposta_id, usuario_id, requisitos_aceitos=False, valor_bloqueado=0.0):
        self.id = id
        self.aposta_id = aposta_id
        self.usuario_id = usuario_id
        self.requisitos_aceitos = requisitos_aceitos
        self.valor_bloqueado = valor_bloqueado

    def aceitar_requisitos(self):
        self.requisitos_aceitos = True

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return ParticipacaoAposta(
            dados['id'], dados['aposta_id'], dados['usuario_id'],
            dados.get('requisitos_aceitos', False), dados.get('valor_bloqueado', 0.0)
        )
