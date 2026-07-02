class Usuario:
    def __init__(self, id, nome, email, senha, perfil):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.perfil = perfil  # admin ou participante

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dados):
        return Usuario(dados['id'], dados['nome'], dados['email'], dados['senha'], dados['perfil'])
