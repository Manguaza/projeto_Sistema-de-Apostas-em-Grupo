class Grupo:
    def __init__(self, id, nome, descricao, usuarios_ids=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.usuarios_ids = usuarios_ids or []

    def adicionar_usuario(self, usuario_id):
        if usuario_id not in self.usuarios_ids:
            self.usuarios_ids.append(usuario_id)

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Grupo(dados['id'], dados['nome'], dados['descricao'], dados.get('usuarios_ids', []))
