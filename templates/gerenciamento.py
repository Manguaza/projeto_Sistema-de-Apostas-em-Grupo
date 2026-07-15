import streamlit as st

from model.aposta import REQUISITOS_PADRAO
from persistencia.armazenamento_imagens import caminho_absoluto, salvar_imagem


def _executar(acao, mensagem):
    try:
        acao()
        st.success(mensagem)
        return True
    except ValueError as erro:
        st.error(str(erro))
        return False


def _salvar_upload(upload, prefixo):
    if upload is None:
        return None
    return salvar_imagem(upload.name, upload.getvalue(), upload.type, prefixo)


def _mostrar_imagem_atual(objeto):
    if getattr(objeto, 'imagem', None):
        st.image(caminho_absoluto(objeto.imagem), width=240,
                 caption='Imagem atual')


def gerenciar_clientes(service, admin):
    st.header('clientes')
    listar, inserir, atualizar, excluir = st.tabs(
        ['Listar e pesquisar', 'Inserir', 'Atualizar', 'Excluir'])
    with listar:
        termo = st.text_input('Pesquisar por nome ou e-mail', key='pesquisa_cliente')
        clientes = service.listar_clientes(termo)
        carteiras = {c.usuario_id: c.saldo for c in service.carteiras_repo.listar()}
        st.dataframe([{
            'ID': c.id, 'Nome': c.nome, 'E-mail': c.email,
            'Saldo': f'R$ {carteiras.get(c.id, 0):.2f}'
        } for c in clientes], width='stretch', hide_index=True)
    with inserir:
        with st.form('inserir_cliente_admin'):
            nome = st.text_input('Nome')
            email = st.text_input('E-mail')
            senha = st.text_input('Senha', type='password')
            saldo = st.number_input('Saldo inicial', min_value=0.0, value=100.0)
            enviar = st.form_submit_button('Inserir cliente')
        if enviar and _executar(
                lambda: service.criar_cliente(nome, email, senha, saldo),
                'Cliente inserido.'):
            st.rerun()
    clientes = service.listar_clientes()
    opcoes = {f'{c.id} — {c.nome} ({c.email})': c for c in clientes}
    with atualizar:
        if not opcoes:
            st.info('Nenhum cliente cadastrado.')
        else:
            rotulo = st.selectbox('Cliente', opcoes, key='cliente_atualizar')
            cliente = opcoes[rotulo]
            carteira = next((c for c in service.carteiras_repo.listar()
                              if c.usuario_id == cliente.id), None)
            with st.form('atualizar_cliente'):
                nome = st.text_input('Nome', value=cliente.nome)
                email = st.text_input('E-mail', value=cliente.email)
                senha = st.text_input('Senha', value=cliente.senha, type='password')
                saldo = st.number_input(
                    'Saldo fictício', min_value=0.0,
                    value=float(carteira.saldo if carteira else 0.0))
                enviar = st.form_submit_button('Salvar alterações')
            def salvar_cliente():
                service.atualizar_cliente(admin.id, cliente.id, nome, email, senha)
                service.atualizar_saldo_carteira(admin.id, cliente.id, saldo)
            if enviar and _executar(salvar_cliente, 'Cliente e carteira atualizados.'):
                st.rerun()
    with excluir:
        if not opcoes:
            st.info('Nenhum cliente cadastrado.')
        else:
            rotulo = st.selectbox('Cliente', opcoes, key='cliente_excluir')
            cliente = opcoes[rotulo]
            st.warning('Clientes com participações registradas não podem ser excluídos.')
            if st.button('Excluir cliente', type='primary') and _executar(
                    lambda: service.excluir_cliente(admin.id, cliente.id), 'Cliente excluído.'):
                st.rerun()


def gerenciar_grupos(service, admin):
    st.header('Grupos')
    listar, inserir, atualizar, excluir = st.tabs(
        ['Listar e pesquisar', 'Inserir', 'Atualizar', 'Excluir'])
    with listar:
        termo = st.text_input('Pesquisar por nome ou descrição', key='pesquisa_grupo')
        grupos = service.pesquisar_grupos(termo) if termo else service.listar_grupos()
        st.dataframe([{
            'ID': g.id, 'Nome': g.nome, 'Descrição': g.descricao,
            'Clientes': len(g.usuarios_ids)
        } for g in grupos], width='stretch', hide_index=True)
    with inserir:
        with st.form('inserir_grupo'):
            nome = st.text_input('Nome')
            descricao = st.text_area('Descrição')
            upload = st.file_uploader(
                'Imagem do grupo', type=['jpg', 'jpeg', 'png', 'webp'],
                key='imagem_inserir_grupo')
            enviar = st.form_submit_button('Inserir grupo')
        if enviar and _executar(
                lambda: service.criar_grupo(
                    admin.id, nome, descricao, _salvar_upload(upload, 'grupo')),
                'Grupo inserido.'):
            st.rerun()
    grupos = service.listar_grupos()
    opcoes = {f'{g.id} — {g.nome}': g for g in grupos}
    with atualizar:
        if not opcoes:
            st.info('Nenhum grupo cadastrado.')
        else:
            grupo = opcoes[st.selectbox('Grupo', opcoes, key='grupo_atualizar')]
            _mostrar_imagem_atual(grupo)
            with st.form('atualizar_grupo'):
                nome = st.text_input('Nome', value=grupo.nome)
                descricao = st.text_area('Descrição', value=grupo.descricao)
                upload = st.file_uploader(
                    'Substituir imagem', type=['jpg', 'jpeg', 'png', 'webp'],
                    key='imagem_atualizar_grupo')
                enviar = st.form_submit_button('Salvar alterações')
            if enviar and _executar(
                    lambda: service.atualizar_grupo(
                        admin.id, grupo.id, nome, descricao,
                        _salvar_upload(upload, 'grupo')), 'Grupo atualizado.'):
                st.rerun()
    with excluir:
        if not opcoes:
            st.info('Nenhum grupo cadastrado.')
        else:
            grupo = opcoes[st.selectbox('Grupo', opcoes, key='grupo_excluir')]
            st.warning('Um grupo que possui apostas não pode ser excluído.')
            if st.button('Excluir grupo', type='primary') and _executar(
                    lambda: service.excluir_grupo(admin.id, grupo.id), 'Grupo excluído.'):
                st.rerun()


def _opcoes_texto(aposta):
    return '\n'.join(aposta.opcoes)


def gerenciar_apostas(service, admin):
    st.header('apostas')
    listar, inserir, atualizar, excluir = st.tabs(
        ['Listar e pesquisar', 'Inserir', 'Atualizar', 'Excluir'])
    grupos = service.listar_grupos()
    grupos_opcoes = {f'{g.id} — {g.nome}': g.id for g in grupos}
    with listar:
        termo = st.text_input('Pesquisar por título ou descrição', key='pesquisa_aposta')
        status = st.selectbox('Situação', ['Todas', 'aberta', 'finalizada'])
        apostas = service.pesquisar_apostas(
            termo, status=None if status == 'Todas' else status)
        st.dataframe([{
            'ID': a.id, 'Título': a.titulo, 'Grupo': a.grupo_id,
            'Entrada': f'R$ {a.valor_entrada:.2f}', 'Status': a.status,
            'Opções': ' | '.join(a.opcoes)
        } for a in apostas], width='stretch', hide_index=True)
    with inserir:
        if not grupos_opcoes:
            st.info('Cadastre um grupo antes de inserir apostas.')
        else:
            with st.form('inserir_aposta'):
                grupo = st.selectbox('Grupo', grupos_opcoes)
                titulo = st.text_input('Título')
                descricao = st.text_area('Descrição')
                valor = st.number_input('Valor de entrada', min_value=0.01)
                requisitos = st.multiselect('Requisitos', REQUISITOS_PADRAO)
                opcoes_texto = st.text_area('Opções, uma por linha')
                upload = st.file_uploader(
                    'Imagem da aposta', type=['jpg', 'jpeg', 'png', 'webp'],
                    key='imagem_inserir_aposta')
                enviar = st.form_submit_button('Inserir aposta')
            alternativas = [o.strip() for o in opcoes_texto.splitlines() if o.strip()]
            if enviar and _executar(lambda: service.criar_aposta(
                    admin.id, grupos_opcoes[grupo], titulo, descricao, valor,
                    requisitos, alternativas, _salvar_upload(upload, 'aposta')),
                    'Aposta inserida.'):
                st.rerun()
    apostas = service.apostas_repo.listar()
    apostas_opcoes = {f'{a.id} — {a.titulo}': a for a in apostas}
    with atualizar:
        if not apostas_opcoes:
            st.info('Nenhuma aposta cadastrada.')
        else:
            aposta = apostas_opcoes[st.selectbox(
                'Aposta', apostas_opcoes, key='aposta_atualizar')]
            _mostrar_imagem_atual(aposta)
            requisitos_disponiveis = list(dict.fromkeys(
                REQUISITOS_PADRAO + aposta.requisitos))
            with st.form('atualizar_aposta'):
                titulo = st.text_input('Título', value=aposta.titulo)
                descricao = st.text_area('Descrição', value=aposta.descricao)
                valor = st.number_input('Valor de entrada', min_value=0.01,
                                        value=float(aposta.valor_entrada))
                requisitos = st.multiselect(
                    'Requisitos', requisitos_disponiveis, default=aposta.requisitos)
                opcoes_texto = st.text_area('Opções, uma por linha', value=_opcoes_texto(aposta))
                upload = st.file_uploader(
                    'Substituir imagem', type=['jpg', 'jpeg', 'png', 'webp'],
                    key='imagem_atualizar_aposta')
                enviar = st.form_submit_button('Salvar alterações')
            alternativas = [o.strip() for o in opcoes_texto.splitlines() if o.strip()]
            if enviar and _executar(lambda: service.atualizar_aposta(
                    admin.id, aposta.id, titulo, descricao, valor, requisitos,
                    alternativas, _salvar_upload(upload, 'aposta')),
                    'Aposta atualizada.'):
                st.rerun()
    with excluir:
        if not apostas_opcoes:
            st.info('Nenhuma aposta cadastrada.')
        else:
            aposta = apostas_opcoes[st.selectbox(
                'Aposta', apostas_opcoes, key='aposta_excluir')]
            st.warning('Apostas com participações não podem ser excluídas.')
            if st.button('Excluir aposta', type='primary') and _executar(
                    lambda: service.excluir_aposta(admin.id, aposta.id), 'Aposta excluída.'):
                st.rerun()


def gerenciar_participacoes(service, admin):
    st.header('Participações')
    termo = st.text_input('Pesquisar por cliente ou palpite')
    participacoes = service.listar_participacoes(termo)
    usuarios = {u.id: u.nome for u in service.usuarios_repo.listar()}
    apostas = {a.id: a.titulo for a in service.apostas_repo.listar()}
    st.dataframe([{
        'ID': p.id, 'Cliente': usuarios.get(p.usuario_id, p.usuario_id),
        'Aposta': apostas.get(p.aposta_id, p.aposta_id), 'Palpite': p.opcao_escolhida,
        'Valor': f'R$ {p.valor_bloqueado:.2f}'
    } for p in participacoes], width='stretch', hide_index=True)
    cancelaveis = [p for p in participacoes
                   if service.apostas_repo.buscar_por_id(p.aposta_id) is not None
                   and service.apostas_repo.buscar_por_id(p.aposta_id).status == 'aberta']
    opcoes = {f'{p.id} — {usuarios.get(p.usuario_id, p.usuario_id)} / '
              f'{apostas.get(p.aposta_id, p.aposta_id)}': p for p in cancelaveis}
    if opcoes:
        participacao = opcoes[st.selectbox('Participação para cancelar', opcoes)]
        if st.button('Cancelar e devolver saldo', type='primary') and _executar(
                lambda: service.cancelar_participacao(
                    participacao.usuario_id, participacao.id, admin.id),
                'Participação cancelada e saldo devolvido.'):
            st.rerun()


def gerenciar_minhas_participacoes(service, cliente):
    st.header('Minhas participações')
    participacoes = [p for p in service.listar_participacoes()
                     if p.usuario_id == cliente.id]
    apostas = {a.id: a for a in service.apostas_repo.listar()}
    if not participacoes:
        st.info('Você ainda não participa de nenhuma aposta.')
        return
    st.dataframe([{
        'ID': p.id,
        'Aposta': apostas[p.aposta_id].titulo if p.aposta_id in apostas else p.aposta_id,
        'Palpite': p.opcao_escolhida,
        'Valor': f'R$ {p.valor_bloqueado:.2f}',
        'Situação': apostas[p.aposta_id].status if p.aposta_id in apostas else 'indisponível'
    } for p in participacoes], width='stretch', hide_index=True)
    abertas = [p for p in participacoes if p.aposta_id in apostas
               and apostas[p.aposta_id].status == 'aberta']
    if not abertas:
        return
    opcoes = {f'{p.id} — {apostas[p.aposta_id].titulo}': p for p in abertas}
    participacao = opcoes[st.selectbox('Participação', opcoes)]
    aposta = apostas[participacao.aposta_id]
    novo_palpite = st.selectbox(
        'Alterar palpite', aposta.opcoes,
        index=aposta.opcoes.index(participacao.opcao_escolhida)
        if participacao.opcao_escolhida in aposta.opcoes else 0)
    coluna_alterar, coluna_cancelar = st.columns(2)
    with coluna_alterar:
        if st.button('Salvar novo palpite') and _executar(
                lambda: service.alterar_palpite(
                    cliente.id, participacao.id, novo_palpite), 'Palpite atualizado.'):
            st.rerun()
    with coluna_cancelar:
        if st.button('Cancelar participação', type='primary') and _executar(
                lambda: service.cancelar_participacao(cliente.id, participacao.id),
                'Participação cancelada e saldo devolvido.'):
            st.rerun()


def painel_administrador_grupo(service, cliente):
    st.header('Administração de grupos')
    if not getattr(cliente, 'administrador_grupo', False):
        st.info(
            'Este papel permite criar e administrar seus próprios grupos. '
            'O administrador central continua responsável por todo o sistema.')
        if st.button('Tornar-me administrador de grupos') and _executar(
                lambda: service.habilitar_admin_grupo(cliente.id),
                'Perfil de administrador de grupos ativado.'):
            st.rerun()
        return

    st.success('Você é administrador de grupos.')
    grupos = service.listar_grupos_administrados(cliente.id)
    listar, criar, editar, criar_aposta, finalizar = st.tabs([
        'Meus grupos', 'Criar grupo', 'Editar ou excluir', 'Criar aposta',
        'Finalizar aposta'])
    with listar:
        if not grupos:
            st.info('Você ainda não criou nenhum grupo.')
        else:
            st.dataframe([{
                'ID': g.id, 'Nome': g.nome, 'Descrição': g.descricao,
                'Participantes': len(g.usuarios_ids)
            } for g in grupos], width='stretch', hide_index=True)
    with criar:
        with st.form('cliente_criar_grupo'):
            nome = st.text_input('Nome')
            descricao = st.text_area('Descrição')
            upload = st.file_uploader(
                'Imagem do grupo', type=['jpg', 'jpeg', 'png', 'webp'],
                key='imagem_cliente_criar_grupo')
            enviar = st.form_submit_button('Criar meu grupo')
        if enviar and _executar(
                lambda: service.criar_grupo(
                    cliente.id, nome, descricao, _salvar_upload(upload, 'grupo')),
                'Grupo criado. Você foi adicionado como responsável e participante.'):
            st.rerun()
    opcoes_grupos = {f'{g.id} — {g.nome}': g for g in grupos}
    with editar:
        if not opcoes_grupos:
            st.info('Crie um grupo primeiro.')
        else:
            grupo = opcoes_grupos[st.selectbox(
                'Grupo', opcoes_grupos, key='meu_grupo_editar')]
            _mostrar_imagem_atual(grupo)
            with st.form('cliente_editar_grupo'):
                nome = st.text_input('Nome', value=grupo.nome)
                descricao = st.text_area('Descrição', value=grupo.descricao)
                upload = st.file_uploader(
                    'Substituir imagem', type=['jpg', 'jpeg', 'png', 'webp'],
                    key='imagem_cliente_editar_grupo')
                salvar = st.form_submit_button('Salvar alterações')
            if salvar and _executar(lambda: service.atualizar_grupo(
                    cliente.id, grupo.id, nome, descricao,
                    _salvar_upload(upload, 'grupo')), 'Grupo atualizado.'):
                st.rerun()
            st.warning('O grupo só pode ser excluído quando não possuir apostas.')
            if st.button('Excluir meu grupo', type='primary') and _executar(
                    lambda: service.excluir_grupo(cliente.id, grupo.id), 'Grupo excluído.'):
                st.rerun()
    with criar_aposta:
        if not opcoes_grupos:
            st.info('Crie um grupo primeiro.')
        else:
            with st.form('cliente_admin_criar_aposta'):
                grupo_rotulo = st.selectbox('Grupo', opcoes_grupos)
                titulo = st.text_input('Título')
                descricao = st.text_area('Descrição')
                valor = st.number_input('Valor de entrada', min_value=0.01)
                requisitos = st.multiselect('Requisitos', REQUISITOS_PADRAO)
                opcoes_texto = st.text_area('Opções de palpite, uma por linha')
                upload = st.file_uploader(
                    'Imagem da aposta', type=['jpg', 'jpeg', 'png', 'webp'],
                    key='imagem_cliente_criar_aposta')
                enviar = st.form_submit_button('Criar aposta no meu grupo')
            alternativas = [o.strip() for o in opcoes_texto.splitlines() if o.strip()]
            grupo = opcoes_grupos[grupo_rotulo]
            if enviar and _executar(lambda: service.criar_aposta(
                    cliente.id, grupo.id, titulo, descricao, valor,
                    requisitos, alternativas, _salvar_upload(upload, 'aposta')),
                    'Aposta criada no seu grupo.'):
                st.rerun()
    with finalizar:
        grupos_ids = {g.id for g in grupos}
        abertas = [a for a in service.apostas_repo.listar()
                   if a.grupo_id in grupos_ids and a.status == 'aberta']
        if not abertas:
            st.info('Não há apostas abertas nos seus grupos.')
        else:
            opcoes_apostas = {f'{a.id} — {a.titulo}': a for a in abertas}
            aposta = opcoes_apostas[st.selectbox(
                'Aposta', opcoes_apostas, key='cliente_admin_finalizar_aposta')]
            participacoes = service.listar_participacoes(aposta_id=aposta.id)
            if not participacoes:
                st.warning('Esta aposta ainda não possui participantes.')
            elif not aposta.opcoes:
                st.warning(
                    'Esta é uma aposta antiga sem opções cadastradas. '
                    'O administrador central deve finalizá-la.')
            else:
                palpites = {p.opcao_escolhida for p in participacoes
                            if p.opcao_escolhida}
                with st.form('cliente_admin_resultado_aposta'):
                    opcao_correta = st.selectbox('Resposta correta', aposta.opcoes)
                    st.caption('Respostas escolhidas: ' +
                               (', '.join(sorted(palpites)) or 'nenhuma'))
                    descricao = st.text_area('Descrição do resultado')
                    enviar = st.form_submit_button('Confirmar resposta e finalizar')
                if enviar and _executar(lambda: service.finalizar_aposta(
                        aposta.id, descricao=descricao, admin_id=cliente.id,
                        opcao_vencedora=opcao_correta),
                        'Resposta registrada, vencedores definidos e prêmio distribuído.'):
                    st.rerun()
def gerenciar_resultados(service, admin):
    st.header('resultados')
    listar, atualizar, excluir = st.tabs(['Listar e pesquisar', 'Atualizar', 'Excluir'])
    with listar:
        termo = st.text_input('Pesquisar por descrição ou opção correta')
        resultados = service.listar_resultados(termo)
        st.dataframe([{
            'ID': r.id, 'Aposta': r.aposta_id, 'Opção correta': r.opcao_vencedora,
            'Descrição': r.descricao
        } for r in resultados], width='stretch', hide_index=True)
    resultados = service.listar_resultados()
    opcoes = {f'{r.id} — Aposta {r.aposta_id}': r for r in resultados}
    with atualizar:
        if not opcoes:
            st.info('Nenhum resultado cadastrado.')
        else:
            resultado = opcoes[st.selectbox('Resultado', opcoes, key='resultado_atualizar')]
            with st.form('atualizar_resultado'):
                descricao = st.text_area('Descrição', value=resultado.descricao)
                enviar = st.form_submit_button('Salvar descrição')
            if enviar and _executar(lambda: service.atualizar_resultado(
                    admin.id, resultado.id, descricao), 'Resultado atualizado.'):
                st.rerun()
    with excluir:
        if not opcoes:
            st.info('Nenhum resultado cadastrado.')
        else:
            resultado = opcoes[st.selectbox('Resultado', opcoes, key='resultado_excluir')]
            st.warning('A exclusão devolve o prêmio dos vencedores e reabre a aposta.')
            if st.button('Anular resultado', type='primary') and _executar(
                    lambda: service.excluir_resultado(admin.id, resultado.id),
                    'Resultado anulado e aposta reaberta.'):
                st.rerun()
