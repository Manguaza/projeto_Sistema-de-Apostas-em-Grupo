import streamlit as st


def exibir_apostas(apostas):
    """Lista as apostas; substitui o template antigo de produtos."""
    st.header('Apostas')
    if not apostas:
        st.info('Nenhuma aposta cadastrada.')
        return
    st.dataframe([
        {
            'ID': aposta.id,
            'Título': aposta.titulo,
            'Entrada': f'R$ {aposta.valor_entrada:.2f}',
            'Grupo': aposta.grupo_id,
            'Opções': ' | '.join(aposta.opcoes),
            'Status': aposta.status,
        }
        for aposta in apostas
    ], width='stretch', hide_index=True)
