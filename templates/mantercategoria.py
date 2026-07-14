import streamlit as st
import pandas as pd
from View import View


class ManterCategoriaUI:
    def main():
        st.header("Cadastro de Categorias")
        tab1, tab2, tab3, tab4 = st.tabs(["Listar", "Inserir", "Atualizar", "Excluir"])
        with tab1: ManterCategoriaUI.listar()
        with tab2: ManterCategoriaUI.inserir()
        with tab3: ManterCategoriaUI.atualizar()
        with tab4: ManterCategoriaUI.excluir()

    def listar():
        categorias = View.categoria_listar()
        if len(categorias) == 0:
            st.write("Nenhuma categoria cadastrada")
        else:
            st.dataframe(pd.DataFrame([c.to_json() for c in categorias]), hide_index=True)

    def inserir():
        descricao = st.text_input("Descricao")
        if st.button("Inserir categoria"):
            try:
                View.categoria_inserir(descricao)
                st.success("Categoria inserida com sucesso")
                st.rerun()
            except Exception as erro:
                st.error(erro)

    def atualizar():
        categorias = View.categoria_listar()
        if len(categorias) == 0:
            st.write("Nenhuma categoria cadastrada")
        else:
            op = st.selectbox("Categoria", categorias)
            descricao = st.text_input("Nova descricao", op.descricao)
            if st.button("Atualizar categoria"):
                try:
                    View.categoria_atualizar(op.id, descricao)
                    st.success("Categoria atualizada com sucesso")
                    st.rerun()
                except Exception as erro:
                    st.error(erro)

    def excluir():
        categorias = View.categoria_listar()
        if len(categorias) == 0:
            st.write("Nenhuma categoria cadastrada")
        else:
            op = st.selectbox("Categoria para excluir", categorias)
            if st.button("Excluir categoria"):
                try:
                    View.categoria_excluir(op.id)
                    st.success("Categoria excluida com sucesso")
                    st.rerun()
                except Exception as erro:
                    st.error(erro)
