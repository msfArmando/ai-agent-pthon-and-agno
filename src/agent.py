"""
Agente de IA para Fobia Social
"""

import logging
from typing import List, Dict, Optional
from openai import OpenAI
from config.settings import (
    OPENAI_API_KEY, 
    OPENAI_API_BASE,
    MODEL_NAME, 
    AGENT_PROMPT, 
    STUDY_MODE_PROMPT,
    MAX_TOKENS
)
from src.embeddings import PostgresEmbeddingManager
from src.utils import format_conversation_history

logger = logging.getLogger(__name__)

class SocialPhobiaAgent:
    """
    Agente de IA especializado em apoio psicológico para fobia social
    """
    
    def __init__(self):
        """
        Inicializa o agente
        """
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        self.embedding_manager = PostgresEmbeddingManager()
        self.conversation_history = []
        
        logger.info("Agente de IA para Fobia Social inicializado")
    
    def add_to_history(self, role: str, content: str) -> None:
        """
        Adiciona uma mensagem ao histórico de conversa
        
        Args:
            role: 'user' ou 'assistant'
            content: Conteúdo da mensagem
        """
        self.conversation_history.append({
            'role': role,
            'content': content
        })
        
        # Mantém apenas as últimas 20 mensagens
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_relevant_documents(self, query: str) -> List[Dict]:
        """
        Busca documentos relevantes para a consulta
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            relevant_docs = self.embedding_manager.search_similar(query)
            return relevant_docs
        except Exception as e:
            logger.error(f"Erro ao buscar documentos relevantes: {e}")
            return []
    
    def format_documents_for_prompt(self, documents: List[Dict]) -> str:
        """
        Formata documentos para uso no prompt
        
        Args:
            documents: Lista de documentos relevantes
            
        Returns:
            String formatada com os documentos
        """
        if not documents:
            return "Nenhuma informação específica encontrada nos documentos."
        
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            content = doc['content'][:500]  # Limita o tamanho
            similarity = doc['similarity']
            filename = doc['filename']
            chunk_id = doc['chunk_id']
            
            formatted_docs.append(
                f"Documento {i} (Similaridade: {similarity:.2f}, Arquivo: {filename}, Chunk: {chunk_id}):\n{content}\n"
            )
        
        return "\n".join(formatted_docs)
    
    def generate_response(self, user_question: str, study_mode: bool = False) -> str:
        """
        Gera uma resposta para a pergunta do usuário
        
        Args:
            user_question: Pergunta do usuário
            study_mode: Se True, usa modo estudo para profissionais
            
        Returns:
            Resposta gerada pelo agente
        """
        try:
            # Busca documentos relevantes
            relevant_docs = self.get_relevant_documents(user_question)
            
            # Formata documentos para o prompt
            documents_text = self.format_documents_for_prompt(relevant_docs)
            
            # Formata histórico de conversa
            conversation_history = format_conversation_history(self.conversation_history)
            
            # Escolhe o prompt apropriado
            if study_mode:
                prompt_template = STUDY_MODE_PROMPT
            else:
                prompt_template = AGENT_PROMPT
            
            # Monta o prompt final
            prompt = prompt_template.format(
                conversation_history=conversation_history,
                user_question=user_question,
                relevant_docs=documents_text
            )
            
            # Gera resposta usando OpenAI
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.7,
                top_p=0.9
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Adiciona à conversa
            self.add_to_history('user', user_question)
            self.add_to_history('assistant', assistant_response)
            
            logger.info(f"Resposta gerada para: {user_question[:50]}...")
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            error_message = (
                "Desculpe, ocorreu um erro ao processar sua pergunta. "
                "Por favor, tente novamente ou reformule sua questão."
            )
            return error_message
    
    def get_conversation_summary(self) -> Dict:
        """
        Obtém um resumo da conversa atual
        
        Returns:
            Dicionário com informações da conversa
        """
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len([m for m in self.conversation_history if m['role'] == 'user']),
            'assistant_messages': len([m for m in self.conversation_history if m['role'] == 'assistant']),
            'recent_topics': self._extract_recent_topics()
        }
    
    def _extract_recent_topics(self) -> List[str]:
        """
        Extrai tópicos recentes da conversa
        
        Returns:
            Lista de tópicos identificados
        """
        if not self.conversation_history:
            return []
        
        # Palavras-chave relacionadas à fobia social
        keywords = [
            'ansiedade', 'social', 'medo', 'timidez', 'exposição', 'terapia',
            'tratamento', 'sintomas', 'técnicas', 'respiração', 'relaxamento',
            'cognitivo', 'comportamental', 'psicólogo', 'profissional'
        ]
        
        recent_text = " ".join([m['content'] for m in self.conversation_history[-5:]])
        recent_text = recent_text.lower()
        
        found_topics = []
        for keyword in keywords:
            if keyword in recent_text:
                found_topics.append(keyword)
        
        return found_topics[:5]  # Limita a 5 tópicos
    
    def clear_conversation_history(self) -> None:
        """
        Limpa o histórico de conversa
        """
        self.conversation_history = []
        logger.info("Histórico de conversa limpo")
    
    def export_conversation(self) -> List[Dict]:
        """
        Exporta o histórico de conversa
        
        Returns:
            Lista com todas as mensagens da conversa
        """
        return self.conversation_history.copy()
    
    def get_agent_info(self) -> Dict:
        """
        Obtém informações sobre o agente
        
        Returns:
            Dicionário com informações do agente
        """
        collection_info = self.embedding_manager.get_collection_info()
        
        return {
            'model_name': MODEL_NAME,
            'conversation_length': len(self.conversation_history),
            'documents_available': collection_info.get('total_documents', 0),
            'collection_name': collection_info.get('collection_name', 'N/A')
        }
