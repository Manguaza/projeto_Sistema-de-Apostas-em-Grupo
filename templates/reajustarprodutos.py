import streamlit as st


def exibir_resultados(resultados, nomes_usuarios=None, participacoes=None):
    """Exibe a opcao correta, vencedores e perdedores de cada aposta."""
    nomes_usuarios = nomes_usuarios or {}
    participacoes = participacoes or []
    st.header('Resultados')
    if not resultados:
        st.info('Nenhum resultado registrado.')
        return

    linhas = []
    for resultado in resultados:
        vencedores_ids = resultado.vencedores_ids or [resultado.vencedor_id]
        linhas.append({
            'Aposta': resultado.aposta_id,
            'Opção correta': resultado.opcao_vencedora or 'Não registrada',
            'Vencedores': ', '.join(
                nomes_usuarios.get(usuario_id, str(usuario_id))
                for usuario_id in vencedores_ids
            ),
            'Perdedores': ', '.join(
                nomes_usuarios.get(p.usuario_id, str(p.usuario_id))
                for p in participacoes
                if p.aposta_id == resultado.aposta_id
                and p.usuario_id not in vencedores_ids
            ) or 'Nenhum',
            'Descrição': resultado.descricao,
        })
    st.dataframe(linhas, width='stretch', hide_index=True)
