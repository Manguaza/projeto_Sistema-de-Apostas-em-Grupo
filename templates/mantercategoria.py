import streamlit as st


def exibir_grupos(grupos):
    """Lista os grupos de apostas cadastrados."""
    st.header('Grupos')
    if not grupos:
        st.info('Nenhum grupo cadastrado.')
        return
    st.dataframe([
        {
            'ID': grupo.id,
            'Nome': grupo.nome,
            'Descrição': grupo.descricao,
            'Clientes': len(grupo.usuarios_ids),
        }
        for grupo in grupos
    ], width='stretch', hide_index=True)
