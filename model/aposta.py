class Aposta:
    def __init__(self, id, titulo, descricao, valor_entrada, requisitos, grupo_id, status='aberta', vencedor_id=None):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.valor_entrada = valor_entrada
        self.requisitos = requisitos
        self.grupo_id = grupo_id
        self.status = status
        self.vencedor_id = vencedor_id

    def abrir(self):
        self.status = 'aberta'

    def finalizar(self, vencedor_id):
        self.status = 'finalizada'
        self.vencedor_id = vencedor_id

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Aposta(
            dados['id'], dados['titulo'], dados['descricao'], dados['valor_entrada'],
            dados['requisitos'], dados['grupo_id'], dados.get('status', 'aberta'), dados.get('vencedor_id')
        )
