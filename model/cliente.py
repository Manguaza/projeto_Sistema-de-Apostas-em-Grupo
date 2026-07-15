from model.usuario import Usuario


class Cliente(Usuario):
    """Usuario que pode entrar em grupos e participar de apostas."""

    def __init__(self, id, nome, email, senha, administrador_grupo=False):
        super().__init__(id, nome, email, senha, perfil='cliente')
        self.administrador_grupo = administrador_grupo

    @staticmethod
    def from_dict(dados):
        return Cliente(
            dados['id'], dados['nome'], dados['email'], dados['senha'],
            dados.get('administrador_grupo', False)
        )
