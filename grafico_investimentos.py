import streamlit as st


def exibir_graficos_investimentos(apostas, grupos, participacoes):
    """Mostra o saldo atualmente bloqueado em apostas abertas."""
    abertas = {aposta.id: aposta for aposta in apostas if aposta.status == 'aberta'}
    por_aposta = {aposta_id: 0.0 for aposta_id in abertas}
    por_grupo = {grupo.id: 0.0 for grupo in grupos}

    for participacao in participacoes:
        aposta = abertas.get(participacao.aposta_id)
        if aposta is None:
            continue
        por_aposta[aposta.id] += participacao.valor_bloqueado
        por_grupo[aposta.grupo_id] = por_grupo.get(aposta.grupo_id, 0.0) + participacao.valor_bloqueado

    total = sum(por_aposta.values())
    st.subheader('Saldo investido em apostas abertas')
    st.metric('Total atualmente bloqueado', f'R$ {total:.2f}')
    coluna_aposta, coluna_grupo = st.columns(2)

    with coluna_aposta:
        st.markdown('#### Por aposta')
        dados = [{'Aposta': abertas[id_aposta].titulo, 'Saldo': valor}
                 for id_aposta, valor in por_aposta.items()]
        if dados:
            st.bar_chart(dados, x='Aposta', y='Saldo', horizontal=True,
                         x_label='Saldo (R$)', y_label='Aposta')
        else:
            st.info('Não há apostas abertas.')

    with coluna_grupo:
        st.markdown('#### Por grupo')
        nomes = {grupo.id: grupo.nome for grupo in grupos}
        dados = [{'Grupo': nomes.get(id_grupo, str(id_grupo)), 'Saldo': valor}
                 for id_grupo, valor in por_grupo.items()]
        if dados:
            st.bar_chart(dados, x='Grupo', y='Saldo', horizontal=True,
                         x_label='Saldo (R$)', y_label='Grupo')
        else:
            st.info('Não há grupos cadastrados.')
