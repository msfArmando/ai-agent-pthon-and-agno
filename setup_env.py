#!/usr/bin/env python3
"""
Script para configurar o arquivo .env
"""

import os

def create_env_file():
    """Cria o arquivo .env com as configurações necessárias"""
    
    env_content = """# Configuração da API OpenAI
OPENAI_API_KEY=sua_chave_api_aqui

# Configurações do modelo
MODEL_NAME=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002

# Diretórios
PDF_FOLDER=data/pdfs
EMBEDDINGS_FOLDER=data/embeddings

# Configurações do PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=social_phobia_agent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_SSLMODE=prefer

# Configurações da interface
HOST=localhost
PORT=8501

# Configurações de OCR
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

# Configurações de logging
LOG_LEVEL=INFO

# Configurações de processamento
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=2000
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")
    print("📝 Lembre-se de configurar sua OPENAI_API_KEY no arquivo .env")

if __name__ == "__main__":
    create_env_file()
