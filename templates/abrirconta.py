import streamlit as st


def exibir_abertura_conta(cadastrar):
    """Exibe o formulario de cadastro de um cliente."""
    with st.form('cadastro'):
        nome = st.text_input('Nome')
        email = st.text_input('E-mail', key='email_novo')
        senha = st.text_input('Senha', type='password', key='senha_nova')
        enviar = st.form_submit_button('Cadastrar', width='stretch')

    if enviar:
        try:
            st.success(cadastrar(nome, email, senha))
        except ValueError as erro:
            st.error(str(erro))
