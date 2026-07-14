REQUISITOS_PADRAO = [
    'Acertar o resultado previsto',
    'Atingir a meta definida na descrição',
    'Concluir o desafio dentro do prazo',
    'Obter a maior pontuação entre os participantes',
    'Apresentar comprovação ao administrador',
]


class Aposta:
    def __init__(self, id, titulo, descricao, valor_entrada, requisitos, grupo_id,
                 status='aberta', vencedor_id=None, opcoes=None, opcao_vencedora=None):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.valor_entrada = valor_entrada
        if isinstance(requisitos, str):
            self.requisitos = [item.strip() for item in requisitos.split(';') if item.strip()]
        else:
            self.requisitos = list(requisitos or [])
        self.grupo_id = grupo_id
        self.status = status
        self.vencedor_id = vencedor_id
        self.opcoes = list(opcoes or [])
        self.opcao_vencedora = opcao_vencedora

    def abrir(self):
        self.status = 'aberta'

    def finalizar(self, vencedor_id=None, opcao_vencedora=None):
        self.status = 'finalizada'
        self.vencedor_id = vencedor_id
        self.opcao_vencedora = opcao_vencedora

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Aposta(
            dados['id'], dados['titulo'], dados['descricao'], dados['valor_entrada'],
            dados['requisitos'], dados['grupo_id'], dados.get('status', 'aberta'),
            dados.get('vencedor_id'), dados.get('opcoes', []), dados.get('opcao_vencedora')
        )
