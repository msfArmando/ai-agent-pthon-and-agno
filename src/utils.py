"""
Utilitários para o Agente de IA para Fobia Social
"""

import logging
import re
from pathlib import Path
from typing import List, Optional
import hashlib

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configura o sistema de logging
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger configurado
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Limpa e normaliza o texto extraído dos PDFs
    
    Args:
        text: Texto bruto extraído
    
    Returns:
        Texto limpo e normalizado
    """
    if not text:
        return ""
    
    # Remove caracteres especiais e normaliza espaços
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]]', '', text)
    
    # Remove linhas vazias excessivas
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove espaços no início e fim
    text = text.strip()
    
    return text

def split_text_into_chunks(text: str, max_chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Divide o texto em chunks menores para processamento
    
    Args:
        text: Texto completo
        max_chunk_size: Tamanho máximo de cada chunk
        overlap: Sobreposição entre chunks
    
    Returns:
        Lista de chunks de texto
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # Se não é o último chunk, tenta quebrar em uma palavra
        if end < len(text):
            # Procura o último espaço antes do fim do chunk
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move o início para o próximo chunk com sobreposição
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def generate_file_hash(file_path: Path) -> str:
    """
    Gera um hash único para um arquivo
    
    Args:
        file_path: Caminho para o arquivo
    
    Returns:
        Hash MD5 do arquivo
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def ensure_directory_exists(directory: Path) -> None:
    """
    Garante que um diretório existe, criando-o se necessário
    
    Args:
        directory: Caminho do diretório
    """
    directory.mkdir(parents=True, exist_ok=True)

def get_safe_filename(filename: str) -> str:
    """
    Converte um nome de arquivo para um formato seguro
    
    Args:
        filename: Nome original do arquivo
    
    Returns:
        Nome de arquivo seguro
    """
    # Remove caracteres especiais e espaços
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    # Remove underscores múltiplos
    safe_name = re.sub(r'_+', '_', safe_name)
    # Remove underscores no início e fim
    safe_name = safe_name.strip('_')
    return safe_name

def format_conversation_history(history: List[dict]) -> str:
    """
    Formata o histórico de conversa para uso no prompt
    
    Args:
        history: Lista de mensagens da conversa
    
    Returns:
        Histórico formatado como string
    """
    if not history:
        return "Nenhuma conversa anterior."
    
    formatted = []
    for i, message in enumerate(history[-10:], 1):  # Últimas 10 mensagens
        role = "Usuário" if message["role"] == "user" else "Assistente"
        formatted.append(f"{i}. {role}: {message['content']}")
    
    return "\n".join(formatted)

def validate_pdf_file(file_path: Path) -> bool:
    """
    Valida se um arquivo é um PDF válido
    
    Args:
        file_path: Caminho para o arquivo
    
    Returns:
        True se for um PDF válido, False caso contrário
    """
    if not file_path.exists():
        return False
    
    if file_path.suffix.lower() != '.pdf':
        return False
    
    # Verifica se o arquivo não está vazio
    if file_path.stat().st_size == 0:
        return False
    
    return True

def sanitize_text_for_embedding(text: str) -> str:
    """
    Sanitiza o texto para geração de embeddings
    
    Args:
        text: Texto original
    
    Returns:
        Texto sanitizado
    """
    # Remove caracteres que podem causar problemas
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove caracteres não-ASCII
    text = re.sub(r'\s+', ' ', text)  # Normaliza espaços
    text = text.strip()
    
    # Limita o tamanho do texto
    if len(text) > 8000:  # Limite para embeddings
        text = text[:8000]
    
    return text
