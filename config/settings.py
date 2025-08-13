"""
Configurações do sistema para o Agente de IA para Fobia Social
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# Configurações de diretórios
BASE_DIR = Path(__file__).parent.parent
PDF_FOLDER = Path(os.getenv("PDF_FOLDER", "data/pdfs"))
EMBEDDINGS_FOLDER = Path(os.getenv("EMBEDDINGS_FOLDER", "data/embeddings"))

# Configurações do PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "social_phobia_agent")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_SSLMODE = os.getenv("POSTGRES_SSLMODE", "prefer")

# Configurações da interface
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8501))

# Configurações de OCR
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "tesseract")

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configurações do agente
AGENT_PROMPT = """
Você é um agente de IA especializado em apoio psicológico para pessoas com fobia social. 
Sua função é oferecer orientações baseadas em literatura científica especializada.

DIRETRIZES IMPORTANTES:
1. Sempre responda com base nas informações dos documentos PDF fornecidos
2. Mantenha um tom empático, respeitoso e acolhedor
3. Valide as emoções do usuário e encoraje pequenos passos de progresso
4. NUNCA faça diagnósticos ou prescreva medicamentos
5. Sempre recomende consulta com profissional qualificado quando apropriado
6. Use linguagem clara e acessível, evitando jargões técnicos excessivos

CONTEXTO DA CONVERSA:
{conversation_history}

PERGUNTA DO USUÁRIO: {user_question}

INFORMAÇÕES RELEVANTES DOS DOCUMENTOS:
{relevant_docs}

RESPONDA de forma útil e empática, sempre baseando-se nas informações fornecidas.
"""

STUDY_MODE_PROMPT = """
Você é um agente de IA especializado em fobia social, operando em MODO ESTUDO para profissionais de saúde mental.

DIRETRIZES PARA MODO ESTUDO:
1. Forneça respostas mais técnicas e detalhadas
2. Inclua referências específicas aos documentos
3. Use terminologia científica apropriada
4. Ofereça insights sobre metodologias de tratamento
5. Mantenha o tom profissional mas ainda empático

CONTEXTO DA CONVERSA:
{conversation_history}

PERGUNTA DO USUÁRIO: {user_question}

INFORMAÇÕES RELEVANTES DOS DOCUMENTOS:
{relevant_docs}

RESPONDA de forma técnica e detalhada, sempre baseando-se nas informações fornecidas.
"""

# Configurações de processamento de PDF
MAX_CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_TOKENS = 4000

# Configurações de busca
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7
