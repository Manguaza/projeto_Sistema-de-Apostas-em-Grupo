from model.aposta import Aposta
from model.carteira import Carteira
from model.cliente import Cliente
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

    def _exigir_gerente_grupo(self, usuario_id, grupo_id):
        usuario = self._buscar_usuario(usuario_id)
        grupo = self.grupos_repo.buscar_por_id(grupo_id)
        if grupo is None:
            raise ValueError('Grupo nao encontrado.')
        if usuario.perfil == 'admin':
            return usuario, grupo
        if (usuario.perfil in ('cliente', 'participante')
                and getattr(usuario, 'administrador_grupo', False)
                and grupo.administrador_id == usuario.id
                and grupo.criador_id == usuario.id):
            return usuario, grupo
        raise ValueError('Apenas o administrador central ou o responsavel pelo grupo pode executar esta acao.')

    def habilitar_admin_grupo(self, usuario_id):
        cliente = self._exigir_cliente(usuario_id)
        cliente.administrador_grupo = True
        self.usuarios_repo.atualizar(cliente)
        return cliente

    def listar_grupos_administrados(self, usuario_id):
        usuario = self._buscar_usuario(usuario_id)
        if usuario.perfil == 'admin':
            return self.listar_grupos()
        return [g for g in self.listar_grupos()
                if g.administrador_id == usuario_id and g.criador_id == usuario_id]

    def _exigir_repo_grupos(self):
        if self.grupos_repo is None:
            raise ValueError('Repositorio de grupos nao configurado.')

    def _buscar_carteira_por_usuario(self, usuario_id):
        for carteira in self.carteiras_repo.listar():
            if carteira.usuario_id == usuario_id:
                return carteira
        return None

    def _validar_email_unico(self, email, ignorar_id=None):
        email = email.strip().lower()
        if '@' not in email:
            raise ValueError('Informe um e-mail valido.')
        for usuario in self.usuarios_repo.listar():
            if usuario.email.lower() == email and usuario.id != ignorar_id:
                raise ValueError('Ja existe um usuario com esse e-mail.')
        return email

    # CRUD e pesquisa de clientes
    def criar_cliente(self, nome, email, senha, saldo_inicial=100.0):
        nome = nome.strip()
        if not nome or not senha:
            raise ValueError('Nome e senha sao obrigatorios.')
        email = self._validar_email_unico(email)
        cliente = Cliente(self._proximo_id(self.usuarios_repo.listar()), nome, email, senha)
        self.usuarios_repo.inserir(cliente)
        carteira = Carteira(
            self._proximo_id(self.carteiras_repo.listar()), cliente.id, float(saldo_inicial))
        self.carteiras_repo.inserir(carteira)
        return cliente

    def listar_clientes(self, termo=''):
        termo = termo.strip().lower()
        return [u for u in self.usuarios_repo.listar()
                if u.perfil in ('cliente', 'participante')
                and (not termo or termo in u.nome.lower() or termo in u.email.lower())]

    def atualizar_cliente(self, admin_id, cliente_id, nome, email, senha):
        self._exigir_admin(admin_id)
        cliente = self._exigir_cliente(cliente_id)
        nome = nome.strip()
        if not nome or not senha:
            raise ValueError('Nome e senha sao obrigatorios.')
        cliente.nome = nome
        cliente.email = self._validar_email_unico(email, cliente_id)
        cliente.senha = senha
        self.usuarios_repo.atualizar(cliente)
        return cliente

    def excluir_cliente(self, admin_id, cliente_id):
        self._exigir_admin(admin_id)
        self._exigir_cliente(cliente_id)
        if any(p.usuario_id == cliente_id for p in self.participacoes_repo.listar()):
            raise ValueError('Nao e possivel excluir cliente com participacoes registradas.')
        if self.grupos_repo is not None:
            for grupo in self.grupos_repo.listar():
                if cliente_id in grupo.usuarios_ids:
                    grupo.usuarios_ids.remove(cliente_id)
                    self.grupos_repo.atualizar(grupo)
        carteira = self._buscar_carteira_por_usuario(cliente_id)
        if carteira:
            self.carteiras_repo.excluir(carteira.id)
        self.usuarios_repo.excluir(cliente_id)

    def autenticar(self, email, senha):
        email = email.strip().lower()
        return next((u for u in self.usuarios_repo.listar()
                     if u.email.lower() == email and u.senha == senha), None)

    # A carteira e criada e excluida junto com o cliente; estas operacoes
    # completam sua consulta e atualizacao dentro da camada de servico.
    def listar_carteiras(self, termo=''):
        termo = termo.strip().lower()
        usuarios = {u.id: u for u in self.usuarios_repo.listar()}
        return [c for c in self.carteiras_repo.listar()
                if not termo or (c.usuario_id in usuarios
                                 and termo in usuarios[c.usuario_id].nome.lower())]

    def adicionar_saldo(self, usuario_id, valor):
        self._exigir_cliente(usuario_id)
        carteira = self._buscar_carteira_por_usuario(usuario_id)
        if carteira is None:
            raise ValueError('Carteira nao encontrada.')
        carteira.adicionar_saldo(float(valor))
        self.carteiras_repo.atualizar(carteira)
        return carteira

    def atualizar_saldo_carteira(self, admin_id, usuario_id, novo_saldo):
        self._exigir_admin(admin_id)
        carteira = self._buscar_carteira_por_usuario(usuario_id)
        if carteira is None:
            raise ValueError('Carteira nao encontrada.')
        novo_saldo = float(novo_saldo)
        if novo_saldo < 0:
            raise ValueError('O saldo nao pode ser negativo.')
        carteira.saldo = novo_saldo
        self.carteiras_repo.atualizar(carteira)
        return carteira

    def criar_grupo(self, admin_id, nome, descricao, imagem=None):
        self._exigir_repo_grupos()
        usuario = self._buscar_usuario(admin_id)
        if usuario.perfil != 'admin':
            usuario = self._exigir_cliente(admin_id)
            if not getattr(usuario, 'administrador_grupo', False):
                usuario = self.habilitar_admin_grupo(admin_id)
        if not nome.strip():
            raise ValueError('O nome do grupo e obrigatorio.')

        grupo = Grupo(
            id=self._proximo_id(self.grupos_repo.listar()),
            nome=nome.strip(),
            descricao=descricao.strip(),
            usuarios_ids=[usuario.id] if usuario.perfil != 'admin' else [],
            administrador_id=usuario.id,
            criador_id=usuario.id,
            imagem=imagem
        )
        if usuario.perfil != 'admin' and not grupo.possui_administrador():
            raise ValueError('Todo grupo criado por cliente precisa ter um administrador.')
        self.grupos_repo.inserir(grupo)
        return grupo

    def listar_grupos(self):
        self._exigir_repo_grupos()
        return self.grupos_repo.listar()

    def pesquisar_grupos(self, termo):
        termo = termo.strip().lower()
        return [g for g in self.listar_grupos()
                if termo in g.nome.lower() or termo in g.descricao.lower()]

    def atualizar_grupo(self, admin_id, grupo_id, nome, descricao, imagem=None):
        self._exigir_repo_grupos()
        _, grupo = self._exigir_gerente_grupo(admin_id, grupo_id)
        if not nome.strip():
            raise ValueError('O nome do grupo e obrigatorio.')
        grupo.nome = nome.strip()
        grupo.descricao = descricao.strip()
        if imagem is not None:
            grupo.imagem = imagem
        self.grupos_repo.atualizar(grupo)
        return grupo

    def excluir_grupo(self, admin_id, grupo_id):
        self._exigir_repo_grupos()
        self._exigir_gerente_grupo(admin_id, grupo_id)
        if any(a.grupo_id == grupo_id for a in self.apostas_repo.listar()):
            raise ValueError('Exclua as apostas do grupo antes de excluir o grupo.')
        self.grupos_repo.excluir(grupo_id)

    def entrar_em_grupo(self, grupo_id, usuario_id):
        self._exigir_repo_grupos()
        self._exigir_cliente(usuario_id)

        grupo = self.grupos_repo.buscar_por_id(grupo_id)
        if grupo is None:
            raise ValueError('Grupo nao encontrado.')

        grupo.adicionar_usuario(usuario_id)
        self.grupos_repo.atualizar(grupo)
        return grupo

    def sair_do_grupo(self, grupo_id, usuario_id):
        self._exigir_repo_grupos()
        self._exigir_cliente(usuario_id)
        grupo = self.grupos_repo.buscar_por_id(grupo_id)
        if grupo is None:
            raise ValueError('Grupo nao encontrado.')
        if any(p.usuario_id == usuario_id and
               self.apostas_repo.buscar_por_id(p.aposta_id) is not None and
               self.apostas_repo.buscar_por_id(p.aposta_id).grupo_id == grupo_id
               for p in self.participacoes_repo.listar()):
            raise ValueError('Cancele as participacoes do grupo antes de sair.')
        if usuario_id in grupo.usuarios_ids:
            grupo.usuarios_ids.remove(usuario_id)
            self.grupos_repo.atualizar(grupo)
        return grupo

    def criar_aposta(self, admin_id, grupo_id, titulo, descricao, valor_entrada,
                     requisitos, opcoes=None, imagem=None):
        self._exigir_gerente_grupo(admin_id, grupo_id)
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
            opcoes=opcoes,
            imagem=imagem
        )
        self.apostas_repo.inserir(aposta)
        return aposta

    def listar_apostas_por_grupo(self, grupo_id, apenas_abertas=False):
        apostas = [aposta for aposta in self.apostas_repo.listar() if aposta.grupo_id == grupo_id]
        if apenas_abertas:
            apostas = [aposta for aposta in apostas if aposta.status == 'aberta']
        return apostas

    def pesquisar_apostas(self, termo='', grupo_id=None, status=None):
        termo = termo.strip().lower()
        apostas = self.apostas_repo.listar()
        if termo:
            apostas = [a for a in apostas
                       if termo in a.titulo.lower() or termo in a.descricao.lower()]
        if grupo_id is not None:
            apostas = [a for a in apostas if a.grupo_id == grupo_id]
        if status:
            apostas = [a for a in apostas if a.status == status]
        return apostas

    def atualizar_aposta(self, admin_id, aposta_id, titulo, descricao,
                         valor_entrada, requisitos, opcoes, imagem=None):
        aposta = self.apostas_repo.buscar_por_id(aposta_id)
        if aposta is None:
            raise ValueError('Aposta nao encontrada.')
        self._exigir_gerente_grupo(admin_id, aposta.grupo_id)
        if aposta.status != 'aberta':
            raise ValueError('Apenas apostas abertas podem ser atualizadas.')
        if any(p.aposta_id == aposta_id for p in self.participacoes_repo.listar()):
            raise ValueError('Aposta com participantes nao pode ser alterada.')
        if not titulo.strip() or valor_entrada <= 0 or not requisitos:
            raise ValueError('Informe titulo, valor positivo e requisitos.')
        opcoes = list(dict.fromkeys(o.strip() for o in opcoes if o.strip()))
        if len(opcoes) < 2:
            raise ValueError('Informe pelo menos duas opcoes diferentes.')
        aposta.titulo = titulo.strip()
        aposta.descricao = descricao.strip()
        aposta.valor_entrada = float(valor_entrada)
        aposta.requisitos = list(requisitos)
        aposta.opcoes = opcoes
        if imagem is not None:
            aposta.imagem = imagem
        self.apostas_repo.atualizar(aposta)
        return aposta

    def excluir_aposta(self, admin_id, aposta_id):
        aposta = self.apostas_repo.buscar_por_id(aposta_id)
        if aposta is None:
            raise ValueError('Aposta nao encontrada.')
        self._exigir_gerente_grupo(admin_id, aposta.grupo_id)
        if any(p.aposta_id == aposta_id for p in self.participacoes_repo.listar()):
            raise ValueError('Aposta com participacoes nao pode ser excluida.')
        if any(r.aposta_id == aposta_id for r in self.resultados_repo.listar()):
            raise ValueError('Exclua o resultado antes de excluir a aposta.')
        self.apostas_repo.excluir(aposta_id)

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

    def listar_participacoes(self, termo='', aposta_id=None):
        termo = termo.strip().lower()
        usuarios = {u.id: u for u in self.usuarios_repo.listar()}
        participacoes = self.participacoes_repo.listar()
        if aposta_id is not None:
            participacoes = [p for p in participacoes if p.aposta_id == aposta_id]
        if termo:
            participacoes = [p for p in participacoes
                             if termo in (usuarios[p.usuario_id].nome.lower()
                                          if p.usuario_id in usuarios else '')
                             or termo in str(p.opcao_escolhida or '').lower()]
        return participacoes

    def alterar_palpite(self, usuario_id, participacao_id, opcao_escolhida):
        participacao = self.participacoes_repo.buscar_por_id(participacao_id)
        if participacao is None or participacao.usuario_id != usuario_id:
            raise ValueError('Participacao nao encontrada.')
        aposta = self.apostas_repo.buscar_por_id(participacao.aposta_id)
        if aposta is None or aposta.status != 'aberta':
            raise ValueError('O palpite so pode ser alterado com a aposta aberta.')
        if opcao_escolhida not in aposta.opcoes:
            raise ValueError('Escolha uma opcao valida.')
        participacao.opcao_escolhida = opcao_escolhida
        self.participacoes_repo.atualizar(participacao)
        return participacao

    def cancelar_participacao(self, usuario_id, participacao_id, admin_id=None):
        if admin_id is not None:
            self._exigir_admin(admin_id)
        participacao = self.participacoes_repo.buscar_por_id(participacao_id)
        if participacao is None:
            raise ValueError('Participacao nao encontrada.')
        if admin_id is None and participacao.usuario_id != usuario_id:
            raise ValueError('Voce nao pode cancelar esta participacao.')
        aposta = self.apostas_repo.buscar_por_id(participacao.aposta_id)
        if aposta is None or aposta.status != 'aberta':
            raise ValueError('Apenas participacoes de apostas abertas podem ser canceladas.')
        carteira = self._buscar_carteira_por_usuario(participacao.usuario_id)
        if carteira is None:
            raise ValueError('Carteira nao encontrada.')
        carteira.creditar(participacao.valor_bloqueado)
        self.carteiras_repo.atualizar(carteira)
        self.participacoes_repo.excluir(participacao_id)

    def finalizar_aposta(self, aposta_id, vencedor_id=None, descricao='', admin_id=None,
                         opcao_vencedora=None):
        aposta = self.apostas_repo.buscar_por_id(aposta_id)
        if aposta is None:
            raise ValueError('Aposta nao encontrada.')
        if admin_id is not None:
            self._exigir_gerente_grupo(admin_id, aposta.grupo_id)
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
        carteiras_vencedores = [self._buscar_carteira_por_usuario(uid)
                                for uid in vencedores_ids]
        if any(carteira is None for carteira in carteiras_vencedores):
            raise ValueError('Carteira de um vencedor nao encontrada.')
        for carteira_vencedor in carteiras_vencedores:
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

    def listar_resultados(self, termo=''):
        termo = termo.strip().lower()
        return [r for r in self.resultados_repo.listar()
                if not termo or termo in r.descricao.lower()
                or termo in str(r.opcao_vencedora or '').lower()]

    def atualizar_resultado(self, admin_id, resultado_id, descricao):
        resultado = self.resultados_repo.buscar_por_id(resultado_id)
        if resultado is None:
            raise ValueError('Resultado nao encontrado.')
        aposta = self.apostas_repo.buscar_por_id(resultado.aposta_id)
        if aposta is None:
            raise ValueError('Aposta do resultado nao encontrada.')
        self._exigir_gerente_grupo(admin_id, aposta.grupo_id)
        if not descricao.strip():
            raise ValueError('A descricao do resultado e obrigatoria.')
        resultado.descricao = descricao.strip()
        self.resultados_repo.atualizar(resultado)
        return resultado

    def excluir_resultado(self, admin_id, resultado_id):
        resultado = self.resultados_repo.buscar_por_id(resultado_id)
        if resultado is None:
            raise ValueError('Resultado nao encontrado.')
        aposta = self.apostas_repo.buscar_por_id(resultado.aposta_id)
        if aposta is None:
            raise ValueError('Aposta do resultado nao encontrada.')
        self._exigir_gerente_grupo(admin_id, aposta.grupo_id)
        participacoes = [p for p in self.participacoes_repo.listar()
                         if p.aposta_id == resultado.aposta_id]
        premio_total = sum(p.valor_bloqueado for p in participacoes)
        vencedores = resultado.vencedores_ids or [resultado.vencedor_id]
        premio_individual = premio_total / len(vencedores) if vencedores else 0
        carteiras = [self._buscar_carteira_por_usuario(uid) for uid in vencedores]
        if any(c is None or c.saldo < premio_individual for c in carteiras):
            raise ValueError('Nao e possivel anular: um vencedor nao possui saldo para devolver o premio.')
        for carteira in carteiras:
            carteira.debitar(premio_individual)
            self.carteiras_repo.atualizar(carteira)
        for participacao in participacoes:
            participacao.requisito_cumprido = None
            self.participacoes_repo.atualizar(participacao)
        if aposta:
            aposta.abrir()
            aposta.vencedor_id = None
            aposta.opcao_vencedora = None
            self.apostas_repo.atualizar(aposta)
        self.resultados_repo.excluir(resultado_id)
