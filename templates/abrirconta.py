import streamlit as st
import time 
from View import View

class AbrirConta:
    def main():
        st.header("Abrir Conta")
        with st.form("abrir_Conta"):
            nome = st.text_input("nome")
            email = st.text_input("email")
            fone = st.text_input("fone")
            senha = st.text_input("senha", type= "password")
            confirmar = st.text_input("confirmar senha", type="password")
            enviar = st.form_Submit_button("abrir conta")

        if enviar:
            try:
                if senha != confirmar:
                    raise ValueError("SENHA DIFERENTE")

                View.cliente_inserir(nome,email, fone, senha)
                cliente = View.cliente_autenticar(email, senha)
                st.session_state["cliente_id"] = cliente["id"]
                st.session_state["cliente_nome"] = cliente["nome"]
                st.sessiom_state["cliente_email"] = cliente["email"]
                st.sucess("conta criada com sucesso")
                time.sleep(2)
                st.rerun()
            except Exception as erro:
                     st.error(erro)