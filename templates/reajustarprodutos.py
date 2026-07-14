import streamlit as st
from View import View


class ReajustarProdutoUI:
    def main():
        st.header("Reajustar Precos de Produtos")
        produtos = View.produto_listar()
        if len(produtos) == 0:
            st.write("Nenhum produto cadastrado")
            return

        percentual = st.number_input("Percentual de reajuste", step=1.0, value=0.0)
        if st.button("Aplicar reajuste"):
            try:
                fator = 1 + percentual / 100
                for produto in produtos:
                    View.produto_atualizar(
                        produto.id,
                        produto.descricao,
                        produto.preco * fator,
                        produto.estoque,
                        produto.idcategoria,
                    )
                st.success("Precos reajustados com sucesso")
                st.rerun()
            except Exception as erro:
                st.error(erro) 
