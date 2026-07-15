import os
import uuid


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_UPLOADS = os.path.join(BASE_DIR, 'data', 'uploads')
TIPOS_PERMITIDOS = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
}
TAMANHO_MAXIMO = 5 * 1024 * 1024


def salvar_imagem(nome_arquivo, conteudo, tipo_mime, prefixo):
    """Valida e persiste uma imagem, devolvendo um caminho relativo portavel."""
    if not conteudo:
        return None
    if tipo_mime not in TIPOS_PERMITIDOS:
        raise ValueError('Envie uma imagem JPG, PNG ou WEBP.')
    if len(conteudo) > TAMANHO_MAXIMO:
        raise ValueError('A imagem deve possuir no maximo 5 MB.')

    os.makedirs(PASTA_UPLOADS, exist_ok=True)
    extensao = TIPOS_PERMITIDOS[tipo_mime]
    nome_seguro = f'{prefixo}_{uuid.uuid4().hex}{extensao}'
    caminho_absoluto = os.path.join(PASTA_UPLOADS, nome_seguro)
    with open(caminho_absoluto, 'wb') as arquivo:
        arquivo.write(conteudo)
    return os.path.join('data', 'uploads', nome_seguro).replace('\\', '/')


def caminho_absoluto(caminho_relativo):
    if not caminho_relativo:
        return None
    if os.path.isabs(caminho_relativo):
        return caminho_relativo
    return os.path.join(BASE_DIR, caminho_relativo.replace('/', os.sep))
