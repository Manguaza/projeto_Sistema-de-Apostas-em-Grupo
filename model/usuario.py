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
        perfil = dados.get('perfil', 'cliente')
        if perfil == 'admin':
            from model.administrador import Administrador
            return Administrador(dados['id'], dados['nome'], dados['email'], dados['senha'])
        if perfil in ('cliente', 'participante'):
            from model.cliente import Cliente
            return Cliente(
                dados['id'], dados['nome'], dados['email'], dados['senha'],
                dados.get('administrador_grupo', False)
            )
        return Usuario(dados['id'], dados['nome'], dados['email'], dados['senha'], perfil)
