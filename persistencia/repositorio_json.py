import json
import os

class RepositorioJson:
    def __init__(self, caminho, classe_modelo):
        self.caminho = caminho
        self.classe_modelo = classe_modelo
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        if not os.path.exists(caminho):
            with open(caminho, 'w', encoding='utf-8') as arquivo:
                json.dump([], arquivo)

    def salvar(self, lista):
        with open(self.caminho, 'w', encoding='utf-8') as arquivo:
            json.dump([obj.to_dict() for obj in lista], arquivo, indent=4, ensure_ascii=False)

    def listar(self):
        with open(self.caminho, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        return [self.classe_modelo.from_dict(item) for item in dados]

    def inserir(self, objeto):
        lista = self.listar()
        lista.append(objeto)
        self.salvar(lista)

    def atualizar(self, objeto):
        lista = self.listar()
        for i, item in enumerate(lista):
            if item.id == objeto.id:
                lista[i] = objeto
                self.salvar(lista)
                return
        raise ValueError('Objeto não encontrado.')

    def excluir(self, id):
        lista = self.listar()
        nova_lista = [item for item in lista if item.id != id]
        self.salvar(nova_lista)

    def buscar_por_id(self, id):
        for item in self.listar():
            if item.id == id:
                return item
        return None

    def pesquisar(self, campo, termo):
        termo = termo.lower()
        resultado = []
        for item in self.listar():
            valor = str(getattr(item, campo, '')).lower()
            if termo in valor:
                resultado.append(item)
        return resultado
