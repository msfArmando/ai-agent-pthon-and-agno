#!/usr/bin/env python3
"""
Script para configurar o PostgreSQL para o Agente de IA
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from config.settings import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, 
    POSTGRES_PASSWORD, POSTGRES_SSLMODE
)

def test_connection():
    """Testa a conexão com o PostgreSQL"""
    try:
        # Conecta ao banco de dados 'postgres' (banco padrão)
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database="postgres",  # Conecta ao banco padrão primeiro
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            sslmode=POSTGRES_SSLMODE
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print("✅ Conexão com PostgreSQL estabelecida")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com PostgreSQL: {e}")
        return None

def create_database(conn):
    """Cria o banco de dados se não existir"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}'")
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {POSTGRES_DB}")
                print(f"✅ Banco de dados '{POSTGRES_DB}' criado")
            else:
                print(f"✅ Banco de dados '{POSTGRES_DB}' já existe")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        return False

def setup_extension():
    """Configura a extensão pgvector"""
    try:
        # Conecta ao banco de dados específico
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            sslmode=POSTGRES_SSLMODE
        )
        
        with conn.cursor() as cursor:
            # Verifica se a extensão pgvector está disponível
            cursor.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")
            if cursor.fetchone():
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
                print("✅ Extensão pgvector configurada")
            else:
                print("❌ Extensão pgvector não está disponível")
                print("   Instale a extensão pgvector no PostgreSQL")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar extensão pgvector: {e}")
        return False

def main():
    """Função principal"""
    print("🐘 Configurando PostgreSQL para o Agente de IA")
    print("=" * 50)
    
    # Testa conexão
    conn = test_connection()
    if not conn:
        print("\n💡 Dicas para resolver problemas de conexão:")
        print("1. Verifique se o PostgreSQL está instalado e rodando")
        print("2. Confirme as credenciais no arquivo .env")
        print("3. Verifique se o usuário tem permissões adequadas")
        return
    
    # Cria banco de dados
    if not create_database(conn):
        conn.close()
        return
    
    conn.close()
    
    # Configura extensão pgvector
    if not setup_extension():
        return
    
    print("\n✅ PostgreSQL configurado com sucesso!")
    print("🎉 O sistema está pronto para usar")

if __name__ == "__main__":
    main()
