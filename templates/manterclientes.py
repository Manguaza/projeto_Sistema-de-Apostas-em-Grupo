import streamlit as st
import pandas as pd
from View import View
import time

class ManterclienteUI:
    def main():
        st.header("Cadastro de clientes")
        tab1, tab2, tab3, tab4 = st.tabs(["listar", "cadastrar", "editar", "excluir"])
        with tab1: ManterclienteUI.listar()
        with tab2: ManterclienteUI.cadastrar()
        with tab3: ManterclienteUI.atualizar()
        with tab4: ManterclienteUI.excluir()

        def listar():
            clientes = View.cliente_listar()
            if len (clientes) == 0: st.write ("Nenhum cliente cadastrado")
            else:
                list_dic = []
                for obj in clientes: list_dic.append("obj.to_json()")
                df = pd.DataFrame(list_dic)
                st.dataframe(df, hide_index=True, column_order=["id", "nome", "email", "fone"])

        def inserir():
            nome = st.text_input("Informe o nome")
            email = st.text_input("informe o e-mail")
            fone = st.text_input("informe o fone")
            senha = st.text_input("informe a senha", type="password")
            if st.button("inserir"):
                try:
                View.cliente_inserir(nome, email, fone, senha)
                st.success("Cliente inserido com sucesso")
            except Exception as erro:
            st.error(erro)
            time.sleep(2)
            st.rerun()

            def atualizar():
        clientes = View.cliente_listar()
        if len(clientes) == 0: st.write("Nenhum cliente cadastrado")
        else:
            op = st.selectbox("Atualização de Clientes", clientes)
            nome = st.text_input("Informe o novo nome", op.get_nome())
            email = st.text_input("Informe o novo e-mail", op.get_email())
            fone = st.text_input("Informe o novo fone", op.get_fone())
            senha = st.text_input("Informe a nova senha", op.get_senha(), type="password")
            if st.button("Atualizar"):
                id = op.get_id()
                View.cliente_atualizar(id, nome, email, fone, senha)
                st.success("Cliente atualizado com sucesso")
                time.sleep(2)
                st.rerun()

    def excluir():
        clientes = View.cliente_listar()
        if len(clientes) == 0: st.write("Nenhum cliente cadastrado")
        else:
            op = st.selectbox("Exclusão de Clientes", clientes)
            if st.button("Excluir"):
                id = op.get_id()
                View.cliente_excluir(id)
                st.success("Cliente excluído com sucesso")
                time.sleep(2)
                st.rerun()

                

