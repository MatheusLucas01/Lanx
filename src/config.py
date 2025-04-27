# src/config.py
import os

# NÃO calcule mais BASE_DIR ou ASSETS_DIR aqui usando __file__

# Defina os caminhos RELATIVOS a como eles estarão no bundle/dist
# (Vamos colocar tudo na raiz ou em subpastas simples no bundle)

PRODUCTS_FILE_REL = "products.json"
SALES_FILE_REL = "vendas.json"
LOGIN_BACKGROUND_IMAGE_REL = os.path.join("assets", "image.jpg") # Ou só 

# Você não precisa mais de BASE_DIR ou ASSETS_DIR calculados aqui