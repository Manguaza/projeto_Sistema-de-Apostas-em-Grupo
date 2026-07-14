import tempfile
import unittest
from pathlib import Path

from model.administrador import Administrador
from model.aposta import Aposta
from model.carteira import Carteira
from model.cliente import Cliente
from model.grupo import Grupo
from model.participacao_aposta import ParticipacaoAposta
from model.resultado import Resultado
from model.usuario import Usuario
from persistencia.repositorio_json import RepositorioJson
from service.aposta_service import ApostaService


class TesteOpcoesAposta(unittest.TestCase):
    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        pasta = Path(self.pasta_temporaria.name)
        self.usuarios = RepositorioJson(str(pasta / 'usuarios.json'), Usuario)
        self.carteiras = RepositorioJson(str(pasta / 'carteiras.json'), Carteira)
        self.apostas = RepositorioJson(str(pasta / 'apostas.json'), Aposta)
        self.participacoes = RepositorioJson(str(pasta / 'participacoes.json'), ParticipacaoAposta)
        self.resultados = RepositorioJson(str(pasta / 'resultados.json'), Resultado)
        self.grupos = RepositorioJson(str(pasta / 'grupos.json'), Grupo)
        self.usuarios.salvar([
            Administrador(1, 'Admin', 'admin@teste.com', '123'),
            Cliente(2, 'Ana', 'ana@teste.com', '123'),
            Cliente(3, 'Bruno', 'bruno@teste.com', '123'),
        ])
        self.carteiras.salvar([Carteira(1, 2, 100), Carteira(2, 3, 100)])
        self.grupos.salvar([Grupo(1, 'Grupo', 'Teste', [2, 3])])
        self.service = ApostaService(
            self.usuarios, self.carteiras, self.apostas, self.participacoes,
            self.resultados, self.grupos)

    def tearDown(self):
        self.pasta_temporaria.cleanup()

    def criar_aposta(self):
        return self.service.criar_aposta(
            1, 1, 'Final', 'Quem vence?', 20,
            ['Acertar o resultado'], ['Time A', 'Time B'])

    def test_palpite_define_vencedor_e_premio(self):
        aposta = self.criar_aposta()
        self.service.entrar_em_aposta(aposta.id, 2, True, 'Time A')
        self.service.entrar_em_aposta(aposta.id, 3, True, 'Time B')
        resultado = self.service.finalizar_aposta(
            aposta.id, descricao='Time B venceu.', admin_id=1,
            opcao_vencedora='Time B')

        self.assertEqual(resultado.vencedores_ids, [3])
        self.assertEqual(resultado.opcao_vencedora, 'Time B')
        self.assertEqual(self.carteiras.buscar_por_id(1).saldo, 80)
        self.assertEqual(self.carteiras.buscar_por_id(2).saldo, 120)
        situacoes = {p.usuario_id: p.requisito_cumprido
                     for p in self.participacoes.listar()}
        self.assertEqual(situacoes, {2: False, 3: True})

    def test_palpite_e_obrigatorio(self):
        aposta = self.criar_aposta()
        with self.assertRaisesRegex(ValueError, 'Escolha uma das opcoes'):
            self.service.entrar_em_aposta(aposta.id, 2, True)


if __name__ == '__main__':
    unittest.main()
