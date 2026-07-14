from models.cliente import Cliente, ClienteDAO
from models.categoria import Categoria, CategoriaDAO
from models.produto import Produto, ProdutoDAO
from models.venda import Venda, VendasDAO
from models.vendaitem import VendaItem, VendaItemDAO
from models.promocao import Promocao, PromocaoDAO
from models.entregador import Entregador, EntregadorDAO
from datetime import datetime, date


class View:
    @staticmethod
    def cliente_criar_admin():
        for obj in View.cliente_listar():
            if obj.email == "admin":
                return
        View.cliente_inserir("admin", "admin", "(84)912345678", "1234")

    @staticmethod
    def cliente_autenticar(email, senha):
        email = str(email).strip().lower()
        senha = str(senha).strip()
        for obj in View.cliente_listar():
            if obj.email == email and obj.senha == senha:
                return {"id": obj.id, "nome": obj.nome, "email": obj.email}
        return None

    @staticmethod
    def cliente_inserir(nome, email, fone, senha):
        email = str(email).strip().lower()
        View.__validar_email_cliente(email)
        for obj in View.cliente_listar():
            if obj.email == email:
                raise ValueError("Ja existe um cliente com este e-mail")
        c = Cliente(0, nome, email, fone, senha)
        ClienteDAO().inserir(c)
        return c.id

    @staticmethod
    def cliente_listar():
        return ClienteDAO().listar()

    @staticmethod
    def cliente_listar_id(id):
        return ClienteDAO().listar_id(id)

    @staticmethod
    def cliente_atualizar(id, nome, email, fone, senha):
        id = int(id)
        email = str(email).strip().lower()
        View.__validar_email_cliente(email)
        if View.cliente_listar_id(id) is None:
            raise ValueError("Cliente nao encontrado")
        for obj in View.cliente_listar():
            if obj.email == email and obj.id != id:
                raise ValueError("Ja existe outro cliente com este e-mail")
        c = Cliente(id, nome, email, fone, senha)
        ClienteDAO().atualizar(c)

    @staticmethod
    def cliente_excluir(id):
        id = int(id)
        if View.cliente_listar_id(id) is None:
            raise ValueError("Cliente nao encontrado")
        if View.venda_listar_por_cliente(id):
            raise ValueError("Nao e possivel excluir cliente com vendas cadastradas")
        ClienteDAO().excluir(id)

    @staticmethod
    def categoria_inserir(descricao):
        descricao = str(descricao).strip()
        for obj in View.categoria_listar():
            if obj.descricao.lower() == descricao.lower():
                raise ValueError("Ja existe uma categoria com esta descricao")
        c = Categoria(0, descricao)
        CategoriaDAO().inserir(c)
        return c.id

    @staticmethod
    def categoria_listar():
        return CategoriaDAO().listar()

    @staticmethod
    def categoria_listar_id(id):
        return CategoriaDAO().listar_id(id)

    @staticmethod
    def categoria_atualizar(id, descricao):
        id = int(id)
        descricao = str(descricao).strip()
        if View.categoria_listar_id(id) is None:
            raise ValueError("Categoria nao encontrada")
        for obj in View.categoria_listar():
            if obj.descricao.lower() == descricao.lower() and obj.id != id:
                raise ValueError("Ja existe outra categoria com esta descricao")
        c = Categoria(id, descricao)
        CategoriaDAO().atualizar(c)

    @staticmethod
    def categoria_excluir(id):
        id = int(id)
        if View.categoria_listar_id(id) is None:
            raise ValueError("Categoria nao encontrada")
        for produto in View.produto_listar():
            if int(produto.idcategoria) == id:
                raise ValueError("Nao e possivel excluir categoria usada por produto")
        for promocao in View.promocao_listar():
            if int(promocao.idcategoria) == id:
                raise ValueError("Nao e possivel excluir categoria com promocao cadastrada")
        CategoriaDAO().excluir(id)

    @staticmethod
    def produto_listar():
        return ProdutoDAO().listar()

    @staticmethod
    def produto_listar_id(id):
        return ProdutoDAO().listar_id(id)

    @staticmethod
    def produto_inserir(descricao, preco, estoque, idcategoria, imagem=""):
        descricao, preco, estoque, idcategoria = View.__validar_produto(descricao, preco, estoque, idcategoria)
        p = Produto(0, descricao, preco, estoque, idcategoria, imagem)
        ProdutoDAO().inserir(p)
        return p.id

    @staticmethod
    def produto_atualizar(id, descricao, preco, estoque, idcategoria, imagem=None):
        id = int(id)
        produto_atual = View.produto_listar_id(id)
        if produto_atual is None:
            raise ValueError("Produto nao encontrado")
        descricao, preco, estoque, idcategoria = View.__validar_produto(descricao, preco, estoque, idcategoria)
        imagem = produto_atual.imagem if imagem is None else imagem
        p = Produto(id, descricao, preco, estoque, idcategoria, imagem)
        ProdutoDAO().atualizar(p)

    @staticmethod
    def produto_excluir(id):
        id = int(id)
        if View.produto_listar_id(id) is None:
            raise ValueError("Produto nao encontrado")
        for item in View.vendaitem_listar():
            if int(item.idproduto) == id:
                raise ValueError("Nao e possivel excluir produto que ja foi vendido")
        ProdutoDAO().excluir(id)

    @staticmethod
    def __validar_produto(descricao, preco, estoque, idcategoria):
        descricao = str(descricao).strip()
        preco = float(preco)
        estoque = int(estoque)
        idcategoria = int(idcategoria)
        if View.categoria_listar_id(idcategoria) is None:
            raise ValueError("Categoria do produto nao foi encontrada")
        return descricao, preco, estoque, idcategoria

    @staticmethod
    def promocao_inserir(idcategoria, inicio, fim, percentual):
        idcategoria, inicio, fim, percentual = View.__validar_promocao(idcategoria, inicio, fim, percentual)
        for promocao in View.promocao_listar():
            if promocao.idcategoria == idcategoria and not (fim < promocao.inicio or inicio > promocao.fim):
                raise ValueError("Ja existe promocao para esta categoria nesse periodo")
        p = Promocao(0, idcategoria, inicio, fim, percentual)
        PromocaoDAO().inserir(p)
        return p.id

    @staticmethod
    def promocao_listar():
        return PromocaoDAO().listar()

    @staticmethod
    def promocao_listar_id(id):
        return PromocaoDAO().listar_id(id)

    @staticmethod
    def promocao_atualizar(id, idcategoria, inicio, fim, percentual):
        id = int(id)
        if View.promocao_listar_id(id) is None:
            raise ValueError("Promocao nao encontrada")
        idcategoria, inicio, fim, percentual = View.__validar_promocao(idcategoria, inicio, fim, percentual)
        for promocao in View.promocao_listar():
            if promocao.id != id and promocao.idcategoria == idcategoria and not (fim < promocao.inicio or inicio > promocao.fim):
                raise ValueError("Ja existe outra promocao para esta categoria nesse periodo")
        p = Promocao(id, idcategoria, inicio, fim, percentual)
        PromocaoDAO().atualizar(p)

    @staticmethod
    def promocao_excluir(id):
        id = int(id)
        if View.promocao_listar_id(id) is None:
            raise ValueError("Promocao nao encontrada")
        PromocaoDAO().excluir(id)

    @staticmethod
    def promocao_ativa_produto(produto, data_base=None):
        data_base = data_base or date.today().isoformat()
        promocoes = [
            p for p in View.promocao_listar()
            if p.idcategoria == produto.idcategoria and p.inicio <= data_base <= p.fim
        ]
        if not promocoes:
            return None
        return max(promocoes, key=lambda p: p.percentual)

    @staticmethod
    def produto_preco_venda(produto):
        promocao = View.promocao_ativa_produto(produto)
        if promocao is None:
            return produto.preco, None
        preco = produto.preco * (1 - promocao.percentual / 100)
        return round(preco, 2), promocao

    @staticmethod
    def __validar_promocao(idcategoria, inicio, fim, percentual):
        idcategoria = int(idcategoria)
        if View.categoria_listar_id(idcategoria) is None:
            raise ValueError("Categoria da promocao nao foi encontrada")
        inicio = View.__normalizar_data(inicio)
        fim = View.__normalizar_data(fim)
        if inicio > fim:
            raise ValueError("Data inicial da promocao nao pode ser posterior a data final")
        percentual = float(percentual)
        return idcategoria, inicio, fim, percentual

    @staticmethod
    def entregador_inserir(nome, email, fone, veiculo):
        email = str(email).strip().lower()
        for obj in View.entregador_listar():
            if obj.email == email:
                raise ValueError("Ja existe um entregador com este e-mail")
        e = Entregador(0, nome, email, fone, veiculo)
        EntregadorDAO().inserir(e)
        return e.id

    @staticmethod
    def entregador_listar():
        return EntregadorDAO().listar()

    @staticmethod
    def entregador_listar_id(id):
        return EntregadorDAO().listar_id(id)

    @staticmethod
    def entregador_atualizar(id, nome, email, fone, veiculo):
        id = int(id)
        email = str(email).strip().lower()
        if View.entregador_listar_id(id) is None:
            raise ValueError("Entregador nao encontrado")
        for obj in View.entregador_listar():
            if obj.email == email and obj.id != id:
                raise ValueError("Ja existe outro entregador com este e-mail")
        e = Entregador(id, nome, email, fone, veiculo)
        EntregadorDAO().atualizar(e)

    @staticmethod
    def entregador_excluir(id):
        id = int(id)
        if View.entregador_listar_id(id) is None:
            raise ValueError("Entregador nao encontrado")
        for venda in View.venda_listar():
            if venda.id_entregador == id:
                raise ValueError("Nao e possivel excluir entregador alocado a pedido")
        EntregadorDAO().excluir(id)

    @staticmethod
    def venda_inserir(data, carrinho, total, idcliente, status="Finalizada"):
        if View.cliente_listar_id(idcliente) is None:
            raise ValueError("Cliente da venda nao encontrado")
        v = Venda(0, data, carrinho, total, idcliente, status)
        VendasDAO().inserir(v)
        return v.id

    @staticmethod
    def venda_listar():
        return [v for v in VendasDAO().listar() if v.idcliente > 0]

    @staticmethod
    def venda_listar_todas():
        return VendasDAO().listar()

    @staticmethod
    def venda_listar_id(id):
        return VendasDAO().listar_id(id)

    @staticmethod
    def venda_listar_por_cliente(idcliente):
        idcliente = int(idcliente)
        return [v for v in VendasDAO().listar() if v.idcliente > 0 and int(v.idcliente) == idcliente]

    @staticmethod
    def venda_alocar_entregador(idvenda, identregador):
        venda = View.venda_listar_id(idvenda)
        if venda is None:
            raise ValueError("Venda nao encontrada")
        if venda.status != "Finalizada":
            raise ValueError("Apenas vendas finalizadas podem receber entregador")
        if View.entregador_listar_id(identregador) is None:
            raise ValueError("Entregador nao encontrado")
        venda.id_entregador = int(identregador)
        if venda.status_entrega == "Aguardando alocacao":
            venda.status_entrega = "Preparando"
        VendasDAO().atualizar(venda)

    @staticmethod
    def venda_atualizar_status_entrega(idvenda, status_entrega):
        venda = View.venda_listar_id(idvenda)
        if venda is None:
            raise ValueError("Venda nao encontrada")
        if venda.id_entregador == 0 and status_entrega != "Aguardando alocacao":
            raise ValueError("Aloque um entregador antes de atualizar a entrega")
        venda.status_entrega = status_entrega
        VendasDAO().atualizar(venda)

    @staticmethod
    def vendaitem_inserir(quantidade, preco, idvenda, idproduto):
        if View.venda_listar_id(idvenda) is None:
            raise ValueError("Venda do item nao encontrada")
        if View.produto_listar_id(idproduto) is None:
            raise ValueError("Produto do item nao encontrado")
        vi = VendaItem(0, quantidade, preco, idvenda, idproduto)
        VendaItemDAO().inserir(vi)

    @staticmethod
    def vendaitem_listar():
        return [item for item in VendaItemDAO().listar() if item.idproduto > 0 and item.idvenda > 0]

    @staticmethod
    def vendaitem_listar_todos():
        return VendaItemDAO().listar()

    @staticmethod
    def vendaitem_listar_por_venda(idvenda):
        idvenda = int(idvenda)
        return [item for item in View.vendaitem_listar() if int(item.idvenda) == idvenda]

    @staticmethod
    def carrinho_obter_do_cliente(idcliente):
        venda = View.__carrinho_venda_do_cliente(idcliente)
        if venda is None:
            return {}
        return {int(k): int(v) for k, v in venda.carrinho.items()}

    @staticmethod
    def carrinho_salvar_do_cliente(idcliente, carrinho):
        idcliente = int(idcliente)
        if View.cliente_listar_id(idcliente) is None:
            raise ValueError("Cliente do carrinho nao encontrado")

        carrinho = {int(k): int(v) for k, v in carrinho.items() if int(v) > 0}
        total = 0
        if carrinho:
            _, total = View.carrinho_validar(carrinho)

        venda = View.__carrinho_venda_do_cliente(idcliente)
        if venda is None:
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            venda = Venda(0, data, carrinho, total, idcliente, "No carrinho")
            VendasDAO().inserir(venda)
            return venda.id

        venda.carrinho = carrinho
        venda.total = total
        VendasDAO().atualizar(venda)
        return venda.id

    @staticmethod
    def carrinho_limpar_do_cliente(idcliente):
        venda = View.__carrinho_venda_do_cliente(idcliente)
        if venda is not None:
            venda.carrinho = {}
            venda.total = 0
            VendasDAO().atualizar(venda)

    @staticmethod
    def carrinho_validar(carrinho):
        if not carrinho:
            raise ValueError("Carrinho vazio")
        total = 0
        itens = []
        for idproduto, quantidade in carrinho.items():
            idproduto = int(idproduto)
            quantidade = int(quantidade)
            produto = View.produto_listar_id(idproduto)
            if produto is None:
                raise ValueError(f"Produto {idproduto} nao encontrado")
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser maior que zero")
            if quantidade > produto.estoque:
                raise ValueError(f"Estoque insuficiente para {produto.descricao}")
            preco, promocao = View.produto_preco_venda(produto)
            subtotal = preco * quantidade
            total += subtotal
            itens.append({
                "produto": produto,
                "quantidade": quantidade,
                "preco": preco,
                "preco_original": produto.preco,
                "promocao": promocao,
                "subtotal": subtotal,
            })
        return itens, round(total, 2)

    @staticmethod
    def comprar_carrinho(idcliente, carrinho):
        idcliente = int(idcliente)
        itens, total = View.carrinho_validar(carrinho)
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        venda = View.__carrinho_venda_do_cliente(idcliente)
        if venda is None:
            idvenda = View.venda_inserir(data, {int(k): int(v) for k, v in carrinho.items()}, total, idcliente)
        else:
            venda.data = data
            venda.carrinho = {int(k): int(v) for k, v in carrinho.items()}
            venda.total = total
            venda.status = "Finalizada"
            venda.status_entrega = "Aguardando alocacao"
            VendasDAO().atualizar(venda)
            idvenda = venda.id
        for item in itens:
            produto = item["produto"]
            quantidade = item["quantidade"]
            View.vendaitem_inserir(quantidade, item["preco"], idvenda, produto.id)
            View.produto_atualizar(
                produto.id,
                produto.descricao,
                produto.preco,
                produto.estoque - quantidade,
                produto.idcategoria,
                produto.imagem,
            )
        return idvenda, total

    @staticmethod
    def __carrinho_venda_do_cliente(idcliente):
        idcliente = int(idcliente)
        for venda in VendasDAO().listar():
            if venda.idcliente == idcliente and venda.status == "No carrinho":
                return venda
        return None

    @staticmethod
    def __normalizar_data(valor):
        if hasattr(valor, "isoformat"):
            return valor.isoformat()
        valor = str(valor).strip()
        try:
            datetime.strptime(valor, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Data deve estar no formato AAAA-MM-DD")
        return valor

    @staticmethod
    def __validar_email_cliente(email):
        if email != "admin" and "@" not in email:
            raise ValueError("E-mail do cliente invalido")
