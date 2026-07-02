import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.usuario import Usuario
from model.carteira import Carteira
from model.aposta import Aposta
from persistencia.repositorio_json import RepositorioJson
from service.aposta_service import ApostaService
from model.participacao_aposta import ParticipacaoAposta
from model.resultado import Resultado

# Repositórios
usuarios_repo = RepositorioJson('data/usuarios.json', Usuario)
carteiras_repo = RepositorioJson('data/carteiras.json', Carteira)
apostas_repo = RepositorioJson('data/apostas.json', Aposta)
participacoes_repo = RepositorioJson('data/participacoes.json', ParticipacaoAposta)
resultados_repo = RepositorioJson('data/resultados.json', Resultado)

# Limpa os dados para teste
usuarios_repo.salvar([])
carteiras_repo.salvar([])
apostas_repo.salvar([])
participacoes_repo.salvar([])
resultados_repo.salvar([])

# Criação de usuários e carteiras
usuarios_repo.inserir(Usuario(1, 'Ana', 'ana@email.com', '123', 'participante'))
usuarios_repo.inserir(Usuario(2, 'Bruno', 'bruno@email.com', '123', 'participante'))

carteiras_repo.inserir(Carteira(1, 1, 100.0))
carteiras_repo.inserir(Carteira(2, 2, 100.0))

# Criação da aposta
apostas_repo.inserir(Aposta(1, 'Quem vence o jogo?', 'Aposta entre amigos', 20.0, 'Aceitar regras do grupo', 1))

service = ApostaService(usuarios_repo, carteiras_repo, apostas_repo, participacoes_repo, resultados_repo)

# Dois usuários entram na aposta e têm R$20 fictícios bloqueados
service.entrar_em_aposta(1, 1)
service.entrar_em_aposta(1, 2)

# Bruno vence e recebe R$40 fictícios
service.finalizar_aposta(1, 2, 'Bruno acertou o resultado.')

print('Carteiras após finalizar aposta:')
for carteira in carteiras_repo.listar():
    print('Usuário:', carteira.usuario_id, 'Saldo:', carteira.saldo)
