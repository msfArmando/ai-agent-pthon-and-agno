"""
Gerenciador de embeddings usando PostgreSQL com pgvector
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime

from config.settings import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, 
    POSTGRES_PASSWORD, POSTGRES_SSLMODE, EMBEDDING_MODEL, TOP_K_RESULTS, 
    SIMILARITY_THRESHOLD
)
from src.utils import setup_logging

logger = logging.getLogger(__name__)      # e configurar uma vez no entry point


class PostgresEmbeddingManager:
    """Gerenciador de embeddings usando PostgreSQL com pgvector"""
    
    def __init__(self):
        self.connection_string = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
            f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
            f"?sslmode={POSTGRES_SSLMODE}"
        )
        self.embedding_model = EMBEDDING_MODEL
        self.top_k = TOP_K_RESULTS
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    # Criar extensão pgvector se não existir
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    
                    # Criar tabela de documentos
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS documents (
                            id SERIAL PRIMARY KEY,
                            filename VARCHAR(255) NOT NULL,
                            file_hash VARCHAR(64) NOT NULL,
                            chunk_id INTEGER NOT NULL,
                            content TEXT NOT NULL,
                            embedding vector(1536),
                            metadata JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(filename, chunk_id)
                        );
                    """)
                    
                    # Criar índice para busca por similaridade
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_documents_embedding 
                        ON documents 
                        USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100);
                    """)
                    
                    # Criar índice para busca por arquivo
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_documents_filename 
                        ON documents(filename);
                    """)
                    
                    conn.commit()
                    logger.info("Banco de dados PostgreSQL inicializado com sucesso")
                    
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def _get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return psycopg2.connect(self.connection_string)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para uma lista de textos usando OpenAI"""
        try:
            from openai import OpenAI
            from config.settings import OPENAI_API_KEY, OPENAI_API_BASE
            
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY não configurada")
            
            client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_API_BASE
            )
            
            embeddings = []
            for text in texts:
                response = client.embeddings.create(
                    input=text,
                    model=self.embedding_model
                )
                embeddings.append(response.data[0].embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Adiciona documentos ao banco de dados"""
        try:
            # Extrair textos para gerar embeddings
            texts = [doc['content'] for doc in documents]
            embeddings = self.generate_embeddings(texts)
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    for i, doc in enumerate(documents):
                        cursor.execute("""
                            INSERT INTO documents 
                            (filename, file_hash, chunk_id, content, embedding, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (filename, chunk_id) 
                            DO UPDATE SET 
                                content = EXCLUDED.content,
                                embedding = EXCLUDED.embedding,
                                metadata = EXCLUDED.metadata,
                                created_at = CURRENT_TIMESTAMP
                        """, (
                            doc['filename'],
                            doc['file_hash'],
                            doc['chunk_id'],
                            doc['content'],
                            embeddings[i],
                            json.dumps(doc.get('metadata', {}))
                        ))
                    
                    conn.commit()
            
            logger.info(f"Adicionados {len(documents)} documentos ao banco de dados")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")
            return False
    
    def search_similar(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Busca documentos similares usando similaridade de cosseno"""
        try:
            if not top_k:
                top_k = self.top_k
            
            # Gerar embedding da query
            query_embedding = self.generate_embeddings([query])[0]
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            id, filename, chunk_id, content, metadata,
                            1 - (embedding <=> %s) as similarity
                        FROM documents 
                        WHERE 1 - (embedding <=> %s) > %s
                        ORDER BY embedding <=> %s
                        LIMIT %s
                    """, (query_embedding, query_embedding, self.similarity_threshold, query_embedding, top_k))
                    
                    results = []
                    for row in cursor.fetchall():
                        result = dict(row)
                        result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                        results.append(result)
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Retorna informações sobre a coleção de documentos"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # Total de documentos
                    cursor.execute("SELECT COUNT(*) FROM documents;")
                    total_docs = cursor.fetchone()[0]
                    
                    # Arquivos únicos
                    cursor.execute("SELECT COUNT(DISTINCT filename) FROM documents;")
                    unique_files = cursor.fetchone()[0]
                    
                    # Lista de arquivos
                    cursor.execute("SELECT DISTINCT filename FROM documents ORDER BY filename;")
                    files = [row[0] for row in cursor.fetchall()]
                    
                    return {
                        'total_documents': total_docs,
                        'unique_files': unique_files,
                        'files': files
                    }
                    
        except Exception as e:
            logger.error(f"Erro ao obter informações da coleção: {e}")
            return {'total_documents': 0, 'unique_files': 0, 'files': []}
    
    def clear_collection(self) -> bool:
        """Remove todos os documentos da coleção"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM documents;")
                    conn.commit()
            
            logger.info("Coleção de documentos limpa com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar coleção: {e}")
            return False
    
    def update_document(self, filename: str, chunk_id: int, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Atualiza um documento específico"""
        try:
            # Gerar novo embedding
            embedding = self.generate_embeddings([content])[0]
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE documents 
                        SET content = %s, embedding = %s, metadata = %s, created_at = CURRENT_TIMESTAMP
                        WHERE filename = %s AND chunk_id = %s
                    """, (content, embedding, json.dumps(metadata or {}), filename, chunk_id))
                    
                    conn.commit()
            
            logger.info(f"Documento {filename} chunk {chunk_id} atualizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar documento: {e}")
            return False
    
    def delete_document(self, filename: str, chunk_id: Optional[int] = None) -> bool:
        """Remove um documento ou chunk específico"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    if chunk_id is not None:
                        cursor.execute("DELETE FROM documents WHERE filename = %s AND chunk_id = %s", (filename, chunk_id))
                    else:
                        cursor.execute("DELETE FROM documents WHERE filename = %s", (filename,))
                    
                    conn.commit()
            
            logger.info(f"Documento {filename} removido com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover documento: {e}")
            return False
    
    def get_document_chunks(self, filename: str) -> List[Dict[str, Any]]:
        """Retorna todos os chunks de um documento específico"""
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, chunk_id, content, metadata, created_at
                        FROM documents 
                        WHERE filename = %s 
                        ORDER BY chunk_id
                    """, (filename,))
                    
                    results = []
                    for row in cursor.fetchall():
                        result = dict(row)
                        result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
                        results.append(result)
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Erro ao obter chunks do documento: {e}")
            return []
