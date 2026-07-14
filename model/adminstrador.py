from model.usuario import Usuario


class Administrador(Usuario):
    """Usuario responsavel por grupos, apostas e resultados."""

    def __init__(self, id, nome, email, senha):
        super().__init__(id, nome, email, senha, perfil='admin')

    @staticmethod
    def from_dict(dados):
        return Administrador(dados['id'], dados['nome'], dados['email'], dados['senha'])
