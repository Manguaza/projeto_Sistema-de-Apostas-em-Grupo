from model.participacao_aposta import ParticipacaoAposta
from model.resultado import Resultado

class ApostaService:
    def __init__(self, usuarios_repo, carteiras_repo, apostas_repo, participacoes_repo, resultados_repo):
        self.usuarios_repo = usuarios_repo
        self.carteiras_repo = carteiras_repo
        self.apostas_repo = apostas_repo
        self.participacoes_repo = participacoes_repo
        self.resultados_repo = resultados_repo

    def _proximo_id(self, lista):
        if not lista:
            return 1
        return max(item.id for item in lista) + 1

    def _buscar_carteira_por_usuario(self, usuario_id):
        for carteira in self.carteiras_repo.listar():
            if carteira.usuario_id == usuario_id:
                return carteira
        return None

    def entrar_em_aposta(self, aposta_id, usuario_id):
        aposta = self.apostas_repo.buscar_por_id(aposta_id)
        if aposta is None:
            raise ValueError('Aposta não encontrada.')
        if aposta.status != 'aberta':
            raise ValueError('A aposta não está aberta.')

        carteira = self._buscar_carteira_por_usuario(usuario_id)
        if carteira is None:
            raise ValueError('Carteira não encontrada.')

        for participacao in self.participacoes_repo.listar():
            if participacao.aposta_id == aposta_id and participacao.usuario_id == usuario_id:
                raise ValueError('Usuário já participa dessa aposta.')

        carteira.debitar(aposta.valor_entrada)
        self.carteiras_repo.atualizar(carteira)

        nova_participacao = ParticipacaoAposta(
            id=self._proximo_id(self.participacoes_repo.listar()),
            aposta_id=aposta_id,
            usuario_id=usuario_id,
            requisitos_aceitos=True,
            valor_bloqueado=aposta.valor_entrada
        )
        self.participacoes_repo.inserir(nova_participacao)
        return nova_participacao

    def finalizar_aposta(self, aposta_id, vencedor_id, descricao):
        aposta = self.apostas_repo.buscar_por_id(aposta_id)
        if aposta is None:
            raise ValueError('Aposta não encontrada.')
        if aposta.status == 'finalizada':
            raise ValueError('A aposta já foi finalizada.')

        participacoes = [p for p in self.participacoes_repo.listar() if p.aposta_id == aposta_id]
        if not participacoes:
            raise ValueError('A aposta não possui participantes.')

        vencedor_participa = any(p.usuario_id == vencedor_id for p in participacoes)
        if not vencedor_participa:
            raise ValueError('O vencedor precisa participar da aposta.')

        premio_total = sum(p.valor_bloqueado for p in participacoes)
        carteira_vencedor = self._buscar_carteira_por_usuario(vencedor_id)
        if carteira_vencedor is None:
            raise ValueError('Carteira do vencedor não encontrada.')

        carteira_vencedor.creditar(premio_total)
        self.carteiras_repo.atualizar(carteira_vencedor)

        aposta.finalizar(vencedor_id)
        self.apostas_repo.atualizar(aposta)

        resultado = Resultado(
            id=self._proximo_id(self.resultados_repo.listar()),
            aposta_id=aposta_id,
            vencedor_id=vencedor_id,
            descricao=descricao
        )
        self.resultados_repo.inserir(resultado)
        return resultado
