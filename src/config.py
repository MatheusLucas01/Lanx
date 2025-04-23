import os

# Diretório base do projeto (a pasta que contém 'src', 'products.json', etc.)
# __file__ é o caminho para config.py
# dirname(__file__) é o diretório /src
# abspath(join(..., '..')) sobe um nível para /seu_projeto_lanchonete
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Caminho para os arquivos JSON na raiz do projeto
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")
SALES_FILE = os.path.join(BASE_DIR, "vendas.json")

# Caminho para os assets dentro de 'src'
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGIN_BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, "image.png")

# Você pode adicionar outras configurações aqui, como credenciais de API (com cuidado!)
# ou configurações padrão do sistema.

# Debug para verificar os caminhos (opcional)
# print(f"DEBUG [config.py]: BASE_DIR = {BASE_DIR}")
# print(f"DEBUG [config.py]: PRODUCTS_FILE = {PRODUCTS_FILE}")
# print(f"DEBUG [config.py]: SALES_FILE = {SALES_FILE}")
# print(f"DEBUG [config.py]: ASSETS_DIR = {ASSETS_DIR}")
# print(f"DEBUG [config.py]: LOGIN_BACKGROUND_IMAGE = {LOGIN_BACKGROUND_IMAGE}")