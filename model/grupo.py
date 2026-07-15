class Grupo:
    def __init__(self, id, nome, descricao, usuarios_ids=None,
                 administrador_id=None, criador_id=None, imagem=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.usuarios_ids = usuarios_ids or []
        self.administrador_id = administrador_id
        # Em grupos antigos, o administrador registrado e considerado criador.
        self.criador_id = criador_id if criador_id is not None else administrador_id
        self.imagem = imagem

    def adicionar_usuario(self, usuario_id):
        if usuario_id not in self.usuarios_ids:
            self.usuarios_ids.append(usuario_id)

    def definir_administrador(self, usuario_id):
        if usuario_id is None:
            raise ValueError('O grupo precisa ter um administrador.')
        if self.criador_id is not None and usuario_id != self.criador_id:
            raise ValueError('Somente o criador pode ser administrador deste grupo.')
        self.criador_id = usuario_id
        self.administrador_id = usuario_id
        self.adicionar_usuario(usuario_id)

    def possui_administrador(self):
        return (self.administrador_id is not None
                and self.administrador_id == self.criador_id)

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Grupo(
            dados['id'], dados['nome'], dados['descricao'],
            dados.get('usuarios_ids', []), dados.get('administrador_id'),
            dados.get('criador_id'), dados.get('imagem')
        )
