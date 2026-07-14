import streamlit as st
import pandas as pd
from View import View
from pathlib import Path


class ManterProdutoUI:
    def main():
        st.header("Cadastro de Produtos")
        tab1, tab2, tab3, tab4 = st.tabs(["Listar", "Inserir", "Atualizar", "Excluir"])
        with tab1: ManterProdutoUI.listar()
        with tab2: ManterProdutoUI.inserir()
        with tab3: ManterProdutoUI.atualizar()
        with tab4: ManterProdutoUI.excluir()

    def listar():
        produtos = View.produto_listar()
        if len(produtos) == 0:
            st.write("Nenhum produto cadastrado")
        else:
            st.dataframe(pd.DataFrame([ManterProdutoUI.__produto_json(p) for p in produtos]), hide_index=True)

    def inserir():
        categorias = View.categoria_listar()
        if len(categorias) == 0:
            st.warning("Cadastre uma categoria antes de cadastrar produtos")
            return
        descricao = st.text_input("Descricao", key="produto_inserir_descricao")
        preco = st.number_input("Preco", min_value=0.0, step=0.01, key="produto_inserir_preco")
        estoque = st.number_input("Estoque", min_value=0, step=1, key="produto_inserir_estoque")
        categoria = st.selectbox("Categoria", categorias, key="produto_inserir_categoria")
        imagem = st.file_uploader("Imagem", type=["png", "jpg", "jpeg", "webp"], key="produto_inserir_imagem")
        if st.button("Inserir produto"):
            try:
                caminho_imagem = ManterProdutoUI.__salvar_imagem(imagem)
                View.produto_inserir(descricao, preco, estoque, categoria.id, caminho_imagem)
                st.success("Produto inserido com sucesso")
                st.rerun()
            except Exception as erro:
                st.error(erro)

    def atualizar():
        produtos = View.produto_listar()
        categorias = View.categoria_listar()
        if len(produtos) == 0:
            st.write("Nenhum produto cadastrado")
        elif len(categorias) == 0:
            st.warning("Cadastre uma categoria antes de atualizar produtos")
        else:
            produto = st.selectbox("Produto", produtos, key="produto_atualizar_produto")
            descricao = st.text_input("Nova descricao", produto.descricao, key="produto_atualizar_descricao")
            preco = st.number_input("Novo preco", min_value=0.0, step=0.01, value=float(produto.preco), key="produto_atualizar_preco")
            estoque = st.number_input("Novo estoque", min_value=0, step=1, value=int(produto.estoque), key="produto_atualizar_estoque")
            indice = next((i for i, c in enumerate(categorias) if c.id == produto.idcategoria), 0)
            categoria = st.selectbox("Categoria", categorias, index=indice, key="produto_atualizar_categoria")
            if produto.imagem:
                st.image(produto.imagem, width=180)
            imagem = st.file_uploader("Nova imagem", type=["png", "jpg", "jpeg", "webp"], key="produto_atualizar_imagem")
            if st.button("Atualizar produto"):
                try:
                    caminho_imagem = ManterProdutoUI.__salvar_imagem(imagem) if imagem else None
                    View.produto_atualizar(produto.id, descricao, preco, estoque, categoria.id, caminho_imagem)
                    st.success("Produto atualizado com sucesso")
                    st.rerun()
                except Exception as erro:
                    st.error(erro)

    def excluir():
        produtos = View.produto_listar()
        if len(produtos) == 0:
            st.write("Nenhum produto cadastrado")
        else:
            produto = st.selectbox("Produto para excluir", produtos, key="produto_excluir_produto")
            if st.button("Excluir produto"):
                try:
                    View.produto_excluir(produto.id)
                    st.success("Produto excluido com sucesso")
                    st.rerun()
                except Exception as erro:
                    st.error(erro)

    def __produto_json(produto):
        categoria = View.categoria_listar_id(produto.idcategoria)
        dados = produto.to_json()
        dados["categoria"] = categoria.descricao if categoria else "Sem categoria"
        return dados

    def __salvar_imagem(imagem):
        if imagem is None:
            return ""
        pasta = Path("projeto02") / "uploads" / "produtos"
        pasta.mkdir(parents=True, exist_ok=True)
        nome = f"{pd.Timestamp.now().strftime('%Y%m%d%H%M%S%f')}_{imagem.name}"
        caminho = pasta / nome
        caminho.write_bytes(imagem.getbuffer())
        return str(caminho)
