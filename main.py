import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pymssql
import uuid
import json
from dotenv import load_dotenv
load_dotenv()

blobConnectionString = os.getenv('BLOB_CONNECTION_STRING')
blobContainerName = os.getenv('BLOB_CONTAINER_NAME')
blobaccountName = os.getenv('BLOB_ACCOUNT_NAME')

SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')

# Título 
st.title("Cadastro de Produto - Cloud")

# Formulário Cadastro do Produto
product_name = st.text_input("Nome do Produto")
product_price = st.number_input("Preço do Produto", min_value=0.0, format="%.2f")
product_description = st.text_area("Descrição do Produto")
product_image = st.file_uploader("Imagem do Produto", type=["png", "jpg", "jpeg"])

# Salvando img Blob
def upload_blob(file):
        blob_service_client = BlobServiceClient.from_connection_string(blobConnectionString)
        container_client = blob_service_client.get_container_client(blobContainerName)
        blob_name = f"{uuid.uuid4()}{os.path.splitext(file.name)[1]}"
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file.read(), overwrite=True)
        imagem_url = f"https://{blobaccountName}.blob.core.windows.net/{blobContainerName}/{blob_name}"
        return imagem_url
     

def insert_product_sql(product_name, product_price, product_description, product_image):
    try:
        imagem_url = upload_blob(product_image)          
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Produtos (nome, preco, descricao, imagem_url) VALUES (%s, %s, %s, %s)",
            (product_name, product_price, product_description, imagem_url)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir produto {e}")
        return False

 

if st.button('Cadastrar Produto'):
    if product_name and product_price and product_description and product_image:
        success = insert_product_sql(product_name, product_price, product_description, product_image)
        if success:
            st.success('Produto cadastrado com sucesso!')
    else:
        st.warning('Por favor, preencha todos os campos.')




st.header('Produtos cadastrados')


def list_products_sql():
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT nome, preco, descricao, imagem_url FROM Produtos")
        products = cursor.fetchall()
        conn.close()
        return products
    except Exception as e:
        st.error(f"Erro ao buscar produtos: {e}")
        return []
def list_produtos_screen():
    products = list_products_sql()
    if products:
        for product in products:
            product_name, product_price, product_description, imagem_url = product

            # Exibe os detalhes de cada produto
            st.subheader(product_name)
            st.write(f"Preço: R${product_price}")
            st.write(f"Descrição: {product_description}")
            st.image(imagem_url, width=200)  # Exibe a imagem a partir da URL do Azure Blob

    else:
        st.warning('Nenhum produto encontrado.')
               
if st.button("Listar Produtos"):
    list_produtos_screen()        