from model.aposta import Aposta
from model.grupo import Grupo
from model.participacao_aposta import ParticipacaoAposta
from model.resultado import Resultado


class ApostaService:
    def __init__(
        self,
        usuarios_repo,
        carteiras_repo,
        apostas_repo,
        participacoes_repo,
        resultados_repo,
        grupos_repo=None
    ):
        self.usuarios_repo = usuarios_repo
        self.carteiras_repo = carteiras_repo
        self.apostas_repo = apostas_repo
        self.participacoes_repo = participacoes_repo
        self.resultados_repo = resultados_repo
        self.grupos_repo = grupos_repo

    def _proximo_id(self, lista):
        if not lista:
            return 1
        return max(item.id for item in lista) + 1

    def _buscar_usuario(self, usuario_id):
        usuario = self.usuarios_repo.buscar_por_id(usuario_id)
        if usuario is None:
            raise ValueError('Usuario nao encontrado.')
        return usuario

    def _exigir_admin(self, usuario_id):
        usuario = self._buscar_usuario(usuario_id)
        if usuario.perfil != 'admin':
            raise ValueError('Apenas administradores podem executar esta acao.')
        return usuario

    def _exigir_cliente(self, usuario_id):
        usuario = self._buscar_usuario(usuario_id)
        if usuario.perfil not in ('cliente', 'participante'):
            raise ValueError('Apenas clientes podem executar esta acao.')
        return usuario

    def _exigir_repo_grupos(self):
        if self.grupos_repo is None:
            raise ValueError('Repositorio de grupos nao configurado.')

    def _buscar_carteira_por_usuario(self, usuario_id):
        for carteira in self.carteiras_repo.listar():
            if carteira.usuario_id == usuario_id:
                return carteira
        return None

    def criar_grupo(self, admin_id, nome, descricao):
        self._exigir_repo_grupos()
        self._exigir_admin(admin_id)
        if not nome.strip():
            raise ValueError('O nome do grupo e obrigatorio.')

        grupo = Grupo(
            id=self._proximo_id(self.grupos_repo.listar()),
            nome=nome.strip(),
            descricao=descricao.strip(),
            usuarios_ids=[]
        )
        self.grupos_repo.inserir(grupo)
        return grupo

    def listar_grupos(self):
        self._exigir_repo_grupos()
        return self.grupos_repo.listar()

    def entrar_em_grupo(self, grupo_id, usuario_id):
        self._exigir_repo_grupos()
        self._exigir_cliente(usuario_id)

        grupo = self.grupos_repo.buscar_por_id(grupo_id)
        if grupo is None:
            raise ValueError('Grupo nao encontrado.')

        grupo.adicionar_usuario(usuario_id)
        self.grupos_repo.atualizar(grupo)
        return grupo

    def criar_aposta(self, admin_id, grupo_id, titulo, descricao, valor_entrada,
                     requisitos, opcoes=None):
        self._exigir_admin(admin_id)
        if valor_entrada <= 0:
            raise ValueError('O valor de entrada deve ser positivo.')
        if not titulo.strip():
            raise ValueError('O titulo da aposta e obrigatorio.')
        if not requisitos:
            raise ValueError('Selecione pelo menos um requisito para a aposta.')
        opcoes = list(dict.fromkeys(opcao.strip() for opcao in (opcoes or []) if opcao.strip()))
        if opcoes and len(opcoes) < 2:
            raise ValueError('Informe pelo menos duas opcoes diferentes para a aposta.')
        if self.grupos_repo is not None and self.grupos_repo.buscar_por_id(grupo_id) is None:
            raise ValueError('Grupo nao encontrado.')

        aposta = Aposta(
            id=self._proximo_id(self.apostas_repo.listar()),
            titulo=titulo.strip(),
            descricao=descricao.strip(),
            valor_entrada=valor_entrada,
            requisitos=requisitos,
            grupo_id=grupo_id,
            opcoes=opcoes
        )
        self.apostas_repo.inserir(aposta)
        return aposta

    def listar_apostas_por_grupo(self, grupo_id, apenas_abertas=False):
        apostas = [aposta for aposta in self.apostas_repo.listar() if aposta.grupo_id == grupo_id]
        if apenas_abertas:
            apostas = [aposta for aposta in apostas if aposta.status == 'aberta']
        return apostas

    def entrar_em_aposta(self, aposta_id, usuario_id, requisitos_aceitos=False,
                         opcao_escolhida=None):
        self._exigir_cliente(usuario_id)
        aposta = self.apostas_repo.buscar_por_id(aposta_id)
        if aposta is None:
            raise ValueError('Aposta nao encontrada.')
        if aposta.status != 'aberta':
            raise ValueError('A aposta nao esta aberta.')
        if not requisitos_aceitos:
            raise ValueError('Aceite todos os requisitos antes de participar.')
        if aposta.opcoes and opcao_escolhida not in aposta.opcoes:
            raise ValueError('Escolha uma das opcoes disponiveis para participar.')
        if self.grupos_repo is not None:
            grupo = self.grupos_repo.buscar_por_id(aposta.grupo_id)
            if grupo is None:
                raise ValueError('Grupo da aposta nao encontrado.')
            if usuario_id not in grupo.usuarios_ids:
                raise ValueError('Entre no grupo antes de participar da aposta.')

        carteira = self._buscar_carteira_por_usuario(usuario_id)
        if carteira is None:
            raise ValueError('Carteira nao encontrada.')

        for participacao in self.participacoes_repo.listar():
            if participacao.aposta_id == aposta_id and participacao.usuario_id == usuario_id:
                raise ValueError('Usuario ja participa dessa aposta.')

        carteira.debitar(aposta.valor_entrada)
        self.carteiras_repo.atualizar(carteira)

        nova_participacao = ParticipacaoAposta(
            id=self._proximo_id(self.participacoes_repo.listar()),
            aposta_id=aposta_id,
            usuario_id=usuario_id,
            requisitos_aceitos=requisitos_aceitos,
            valor_bloqueado=aposta.valor_entrada,
            opcao_escolhida=opcao_escolhida
        )
        self.participacoes_repo.inserir(nova_participacao)
        return nova_participacao

    def finalizar_aposta(self, aposta_id, vencedor_id=None, descricao='', admin_id=None,
                         opcao_vencedora=None):
        if admin_id is not None:
            self._exigir_admin(admin_id)

        aposta = self.apostas_repo.buscar_por_id(aposta_id)
        if aposta is None:
            raise ValueError('Aposta nao encontrada.')
        if aposta.status == 'finalizada':
            raise ValueError('A aposta ja foi finalizada.')

        participacoes = [p for p in self.participacoes_repo.listar() if p.aposta_id == aposta_id]
        if not participacoes:
            raise ValueError('A aposta nao possui participantes.')

        if aposta.opcoes:
            if opcao_vencedora not in aposta.opcoes:
                raise ValueError('Selecione uma opcao vencedora valida.')
            vencedores = [p for p in participacoes if p.opcao_escolhida == opcao_vencedora]
            if not vencedores:
                raise ValueError('Nenhum participante escolheu essa opcao. Selecione uma opcao com palpites.')
        else:
            vencedores = [p for p in participacoes if p.usuario_id == vencedor_id]
            if not vencedores:
                raise ValueError('O vencedor precisa participar da aposta.')

        premio_total = sum(p.valor_bloqueado for p in participacoes)
        premio_individual = premio_total / len(vencedores)
        vencedores_ids = [p.usuario_id for p in vencedores]
        for id_vencedor in vencedores_ids:
            carteira_vencedor = self._buscar_carteira_por_usuario(id_vencedor)
            if carteira_vencedor is None:
                raise ValueError('Carteira de um vencedor nao encontrada.')
            carteira_vencedor.creditar(premio_individual)
            self.carteiras_repo.atualizar(carteira_vencedor)

        # O vencedor cumpriu os requisitos; os demais passam a constar como
        # perdedores para que o resultado possa ser apresentado claramente.
        for participacao in participacoes:
            participacao.requisito_cumprido = participacao.usuario_id in vencedores_ids
            self.participacoes_repo.atualizar(participacao)

        aposta.finalizar(vencedores_ids[0], opcao_vencedora)
        self.apostas_repo.atualizar(aposta)

        resultado = Resultado(
            id=self._proximo_id(self.resultados_repo.listar()),
            aposta_id=aposta_id,
            vencedor_id=vencedores_ids[0],
            descricao=descricao,
            vencedores_ids=vencedores_ids,
            opcao_vencedora=opcao_vencedora
        )
        self.resultados_repo.inserir(resultado)
        return resultado
