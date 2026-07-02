import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.usuario import Usuario
from persistencia.repositorio_json import RepositorioJson

repo = RepositorioJson('data/usuarios.json', Usuario)

usuario = Usuario(1, 'Matheus', 'matheus@email.com', '123', 'participante')
repo.inserir(usuario)

usuarios = repo.listar()

print('Usuários salvos no arquivo:')
for u in usuarios:
    print(u.id, u.nome, u.email, u.perfil)
