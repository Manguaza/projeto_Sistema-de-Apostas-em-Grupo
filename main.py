import os

import streamlit as st
from model.administrador import Administrador
from model.aposta import Aposta, REQUISITOS_PADRAO
from model.carteira import Carteira
from model.cliente import Cliente
from model.grupo import Grupo
from model.participacao_aposta import ParticipacaoAposta
from model.resultado import Resultado
from model.usuario import Usuario
from persistencia.repositorio_json import RepositorioJson
from persistencia.armazenamento_imagens import caminho_absoluto
from service.aposta_service import ApostaService
from templates.abrirconta import exibir_abertura_conta
from templates.loginUI import exibir_login
from templates.manterclientes import exibir_clientes
from templates.grafico_investimentos import exibir_graficos_investimentos
from templates.estilo import aplicar_estilo
from templates.reajustarprodutos import exibir_resultados
from templates.gerenciamento import (
    gerenciar_apostas,
    gerenciar_clientes,
    gerenciar_grupos,
    gerenciar_minhas_participacoes,
    gerenciar_participacoes,
    gerenciar_resultados,
    painel_administrador_grupo,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def caminho_dados(nome):
    return os.path.join(BASE_DIR, 'data', nome)


usuarios_repo = RepositorioJson(caminho_dados('usuarios.json'), Usuario)
carteiras_repo = RepositorioJson(caminho_dados('carteiras.json'), Carteira)
grupos_repo = RepositorioJson(caminho_dados('grupos.json'), Grupo)
apostas_repo = RepositorioJson(caminho_dados('apostas.json'), Aposta)
participacoes_repo = RepositorioJson(caminho_dados('participacoes.json'), ParticipacaoAposta)
resultados_repo = RepositorioJson(caminho_dados('resultados.json'), Resultado)
service = ApostaService(usuarios_repo, carteiras_repo, apostas_repo,
                        participacoes_repo, resultados_repo, grupos_repo)


def proximo_id(repo):
    return max((item.id for item in repo.listar()), default=0) + 1


def buscar_usuario_por_email(email):
    return next((u for u in usuarios_repo.listar()
                 if u.email.lower() == email.strip().lower()), None)


def buscar_carteira(usuario_id):
    return next((c for c in carteiras_repo.listar() if c.usuario_id == usuario_id), None)


def preparar_admin_inicial():
    if not any(isinstance(u, Administrador) for u in usuarios_repo.listar()):
        usuarios_repo.inserir(Administrador(
            proximo_id(usuarios_repo), 'Administrador', 'admin@email.com', 'admin'))


def autenticar(email, senha):
    return service.autenticar(email, senha)


def cadastrar_cliente(nome, email, senha):
    service.criar_cliente(nome, email, senha)
    return 'Conta criada com saldo fictício inicial de R$ 100,00.'


def grupos_do_cliente(usuario_id):
    return [g for g in grupos_repo.listar() if usuario_id in g.usuarios_ids]


def mostrar_grupos(grupos):
    if not grupos:
        st.info('Nenhum grupo encontrado.')
        return
    for inicio in range(0, len(grupos), 3):
        colunas = st.columns(3)
        for coluna, grupo in zip(colunas, grupos[inicio:inicio + 3]):
            with coluna:
                with st.container(border=True):
                    if grupo.imagem:
                        st.image(caminho_absoluto(grupo.imagem), width='stretch')
                    else:
                        st.markdown('<div class="image-placeholder">👥</div>',
                                    unsafe_allow_html=True)
                    st.subheader(grupo.nome)
                    st.caption(grupo.descricao or 'Sem descrição')
                    st.write(f'**{len(grupo.usuarios_ids)}** participante(s)')


def mostrar_apostas(apostas):
    if not apostas:
        st.info('Nenhuma aposta encontrada.')
        return
    for inicio in range(0, len(apostas), 3):
        colunas = st.columns(3)
        for coluna, aposta in zip(colunas, apostas[inicio:inicio + 3]):
            with coluna:
                with st.container(border=True):
                    if aposta.imagem:
                        st.image(caminho_absoluto(aposta.imagem), width='stretch')
                    else:
                        st.markdown('<div class="image-placeholder"></div>',
                                    unsafe_allow_html=True)
                    st.subheader(aposta.titulo)
                    st.caption(aposta.descricao or 'Sem descrição')
                    st.write(f'**Entrada:** R$ {aposta.valor_entrada:.2f}')
                    st.write(f'**Status:** {aposta.status}')
                    st.caption('Opções: ' + (' | '.join(aposta.opcoes) or 'Aposta antiga'))


def executar(acao):
    try:
        st.success(acao())
        return True
    except ValueError as erro:
        st.error(str(erro))
        return False


def tela_acesso():
    st.title('Sistema de Apostas em Grupo')
    aba_login, aba_cadastro = st.tabs(['Entrar', 'Criar conta'])
    with aba_login:
        usuario = exibir_login(autenticar)
        if usuario is not None:
            st.session_state.usuario_email = usuario.email
            st.rerun()
    with aba_cadastro:
        exibir_abertura_conta(cadastrar_cliente)


def painel_admin(admin):
    pagina = st.sidebar.radio('Administração',
        ['Visão geral', 'Clientes', 'Grupos', 'Apostas', 'Participações',
         'Resultados', 'Finalizar aposta'])
    if pagina == 'Visão geral':
        st.header('Grupos')
        mostrar_grupos(service.listar_grupos())
        st.header('Apostas')
        mostrar_apostas(apostas_repo.listar())
        exibir_graficos_investimentos(
            apostas_repo.listar(), grupos_repo.listar(), participacoes_repo.listar())
    elif pagina == 'Clientes':
        gerenciar_clientes(service, admin)
    elif pagina == 'Grupos':
        gerenciar_grupos(service, admin)
        return
    elif pagina == 'Apostas':
        gerenciar_apostas(service, admin)
        return
    elif pagina == 'Participações':
        gerenciar_participacoes(service, admin)
    elif pagina == 'Resultados':
        gerenciar_resultados(service, admin)
    else:
        st.header('Finalizar aposta')
        abertas = [a for a in apostas_repo.listar() if a.status == 'aberta']
        if not abertas:
            st.info('Não há apostas abertas.')
            return
        apostas_opcoes = {f'{a.id} — {a.titulo}': a for a in abertas}
        aposta = apostas_opcoes[st.selectbox('Aposta', apostas_opcoes)]
        ids = [p.usuario_id for p in participacoes_repo.listar() if p.aposta_id == aposta.id]
        participantes = [u for u in usuarios_repo.listar() if u.id in ids]
        if not participantes:
            st.warning('Esta aposta ainda não possui participantes.')
            return
        with st.form('finalizar_aposta'):
            if aposta.opcoes:
                palpites_feitos = {p.opcao_escolhida for p in participacoes_repo.listar()
                                   if p.aposta_id == aposta.id and p.opcao_escolhida}
                opcao_vencedora = st.selectbox(
                    'Opção correta', aposta.opcoes,
                    help='Os clientes que escolheram esta opção dividirão o prêmio.')
                st.caption('Opções escolhidas pelos participantes: ' +
                           (', '.join(sorted(palpites_feitos)) or 'nenhuma'))
                vencedor = None
            else:
                vencedores = {f'{u.id} — {u.nome}': u.id for u in participantes}
                vencedor_label = st.selectbox('Vencedor (aposta antiga)', vencedores)
                vencedor = vencedores[vencedor_label]
                opcao_vencedora = None
            descricao = st.text_area('Descrição do resultado')
            enviar = st.form_submit_button('Finalizar aposta')
        if enviar:
            executar(lambda: (service.finalizar_aposta(
                aposta.id, vencedor, descricao, admin.id, opcao_vencedora),
                'Aposta finalizada e prêmio dividido entre quem acertou.')[1])


def painel_cliente(cliente):
    carteira = buscar_carteira(cliente.id)
    saldo = carteira.saldo if carteira else 0.0
    st.sidebar.metric('Saldo fictício', f'R$ {saldo:.2f}')
    pagina = st.sidebar.radio('Área do cliente',
        ['Grupos', 'Administrar grupos', 'Apostas', 'Minhas participações', 'Investimentos',
         'Carteira', 'Resultados'])
    if pagina == 'Grupos':
        st.header('Grupos disponíveis')
        grupos = service.listar_grupos()
        mostrar_grupos(grupos)
        disponiveis = [g for g in grupos if cliente.id not in g.usuarios_ids]
        if disponiveis:
            opcoes = {f'{g.id} — {g.nome}': g.id for g in disponiveis}
            grupo = st.selectbox('Escolha um grupo para entrar', opcoes)
            if st.button('Entrar no grupo') and executar(lambda: (
                    service.entrar_em_grupo(opcoes[grupo], cliente.id), 'Você entrou no grupo.')[1]):
                st.rerun()
    elif pagina == 'Administrar grupos':
        painel_administrador_grupo(service, cliente)
    elif pagina == 'Apostas':
        st.header('Apostas dos meus grupos')
        apostas = [a for g in grupos_do_cliente(cliente.id)
                   for a in service.listar_apostas_por_grupo(g.id)]
        mostrar_apostas(apostas)
        participando = {p.aposta_id for p in participacoes_repo.listar()
                        if p.usuario_id == cliente.id}
        abertas = [a for a in apostas if a.status == 'aberta' and a.id not in participando]
        if abertas:
            opcoes = {f'{a.id} — {a.titulo} (R$ {a.valor_entrada:.2f})': a.id for a in abertas}
            escolha = st.selectbox('Aposta para participar', opcoes)
            aposta_escolhida = next(a for a in abertas if a.id == opcoes[escolha])
            st.markdown('**Requisitos para vencer:**')
            for requisito in aposta_escolhida.requisitos:
                st.write(f'• {requisito}')
            palpite = st.radio(
                'Qual opção você acha que está certa?',
                aposta_escolhida.opcoes,
                index=None,
            ) if aposta_escolhida.opcoes else None
            aceitou = st.checkbox(
                'Li e aceito cumprir todos os requisitos desta aposta.')
            if st.button('Participar da aposta') and executar(lambda: (
                    service.entrar_em_aposta(
                        opcoes[escolha], cliente.id, aceitou, palpite),
                    'Participação registrada e saldo bloqueado.')[1]):
                st.rerun()
    elif pagina == 'Minhas participações':
        gerenciar_minhas_participacoes(service, cliente)
    elif pagina == 'Investimentos':
        exibir_graficos_investimentos(
            apostas_repo.listar(), grupos_repo.listar(), participacoes_repo.listar())
    elif pagina == 'Carteira':
        st.header('Minha carteira')
        st.metric('Saldo atual', f'R$ {saldo:.2f}')
        with st.form('adicionar_saldo'):
            valor = st.number_input('Adicionar saldo(R$)', min_value=0.01, step=10.0)
            enviar = st.form_submit_button('Adicionar')
        if enviar:
            def adicionar():
                service.adicionar_saldo(cliente.id, valor)
                return 'Saldo fictício adicionado.'
            if executar(adicionar):
                st.rerun()
    else:
        resultados = resultados_repo.listar()
        if not resultados:
            st.info('Nenhum resultado registrado.')
        else:
            nomes = {u.id: u.nome for u in usuarios_repo.listar()}
            exibir_resultados(resultados, nomes, participacoes_repo.listar())


def main():
    st.set_page_config(page_title='Apostas em Grupo', page_icon='', layout='wide')
    aplicar_estilo()
    preparar_admin_inicial()
    usuario_email = st.session_state.get('usuario_email')
    usuario = buscar_usuario_por_email(usuario_email) if usuario_email else None
    if usuario is None:
        tela_acesso()
        return
    st.sidebar.title(f'Olá, {usuario.nome}')
    st.sidebar.caption('Administrador' if isinstance(usuario, Administrador) else 'Cliente')
    if st.sidebar.button('Sair', width='stretch'):
        del st.session_state.usuario_email
        st.rerun()
    st.title('Sistema de Apostas em Grupo')
    if isinstance(usuario, Administrador):
        painel_admin(usuario)
    elif isinstance(usuario, Cliente):
        painel_cliente(usuario)
    else:
        st.error('Tipo de usuário não reconhecido.')


if __name__ == '__main__':
    main()
