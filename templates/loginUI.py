import streamlit as st


def exibir_login(autenticar):
    """Exibe o login e devolve o usuario autenticado."""
    with st.form('login'):
        email = st.text_input('E-mail')
        senha = st.text_input('Senha', type='password')
        entrar = st.form_submit_button('Entrar', width='stretch')

    if not entrar:
        return None
    usuario = autenticar(email, senha)
    if usuario is None:
        st.error('E-mail ou senha inválidos.')
    return usuario
