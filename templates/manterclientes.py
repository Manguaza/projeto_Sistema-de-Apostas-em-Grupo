import streamlit as st

from model.cliente import Cliente


def exibir_clientes(usuarios, carteiras):
    """Lista clientes e seus respectivos saldos ficticios."""
    clientes = [usuario for usuario in usuarios if isinstance(usuario, Cliente)]
    saldos = {carteira.usuario_id: carteira.saldo for carteira in carteiras}
    st.header('Clientes cadastrados')
    if not clientes:
        st.info('Nenhum cliente cadastrado.')
        return
    st.dataframe([
        {
            'ID': cliente.id,
            'Nome': cliente.nome,
            'E-mail': cliente.email,
            'Saldo fictício': f'R$ {saldos.get(cliente.id, 0.0):.2f}',
        }
        for cliente in clientes
    ], width='stretch', hide_index=True)
