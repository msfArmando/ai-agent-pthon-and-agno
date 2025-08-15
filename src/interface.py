"""
Interface web para o Agente de IA para Fobia Social usando Agno
"""

import agno
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

from src.agent import SocialPhobiaAgent
from src.embeddings import PostgresEmbeddingManager
from src.pdf_processor import PDFProcessor
from src.utils import setup_logging
from config.settings import PDF_FOLDER, EMBEDDINGS_FOLDER

logger = setup_logging()

class AgnoInterface:
    """
    Interface web para o Agente de IA usando Agno
    """
    
    def __init__(self):
        """
        Inicializa a interface Agno
        """
        # Inicializa componentes
        try:
            self.embedding_manager = PostgresEmbeddingManager()
            self.agent = SocialPhobiaAgent(self.embedding_manager)
            self.pdf_processor = PDFProcessor()
            self.conversation_history = []
            self.study_mode = False
        except Exception as e:
            logger.error(f"Erro ao inicializar componentes: {e}")
            raise
    
    @agno.agent
    def chat_with_agent(self, message: str, study_mode: bool = False) -> str:
        """
        Chat com o agente de IA para fobia social
        
        Args:
            message: Mensagem do usuário
            study_mode: Se True, ativa modo estudo para profissionais
            
        Returns:
            Resposta do agente
        """
        try:
            # Atualiza modo de estudo
            self.study_mode = study_mode
            
            # Obtém resposta do agente
            response = self.agent.get_response(message, study_mode=study_mode)
            
            # Adiciona à conversa
            self.conversation_history.append({
                "user": message,
                "assistant": response,
                "timestamp": datetime.now().isoformat(),
                "study_mode": study_mode
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no chat: {e}")
            return f"Desculpe, ocorreu um erro: {str(e)}"
    
    @agno.agent
    def process_pdfs(self) -> str:
        """
        Processa PDFs da pasta configurada
        
        Returns:
            Status do processamento
        """
        try:
            # Processa PDFs
            pdf_contents = self.pdf_processor.process_pdf_folder(PDF_FOLDER)
            
            if not pdf_contents:
                return "⚠️ Nenhum PDF encontrado para processar. Coloque seus PDFs na pasta data/pdfs/"
            
            # Divide em chunks
            all_chunks = []
            for pdf_content in pdf_contents:
                chunks = self.pdf_processor.split_pdf_content(pdf_content)
                all_chunks.extend(chunks)
            
            # Adiciona à base vetorial
            self.embedding_manager.add_documents(all_chunks)
            
            # Mostra informações da coleção
            collection_info = self.embedding_manager.get_collection_info()
            
            return f"✅ {len(pdf_contents)} PDFs processados com sucesso! Documentos na base: {collection_info.get('total_documents', 0)}"
            
        except Exception as e:
            logger.error(f"Erro no processamento de PDFs: {e}")
            return f"❌ Erro no processamento: {str(e)}"
    
    @agno.agent
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtém status atual do sistema
        
        Returns:
            Informações do sistema
        """
        try:
            # Verifica diretórios
            pdf_count = len(list(PDF_FOLDER.glob("*.pdf")))
            
            # Verifica base vetorial
            collection_info = self.embedding_manager.get_collection_info()
            
            # Informações do agente
            agent_info = self.agent.get_agent_info()
            
            return {
                "pdfs_available": pdf_count,
                "documents_processed": collection_info.get('total_documents', 0),
                "model_name": agent_info['model_name'],
                "conversation_length": len(self.conversation_history),
                "study_mode": self.study_mode,
                "system_online": True
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {"error": str(e)}
    
    @agno.agent
    def clear_conversation(self) -> str:
        """
        Limpa o histórico de conversa
        
        Returns:
            Confirmação
        """
        self.conversation_history = []
        return "✅ Conversa limpa com sucesso!"
    
    @agno.agent
    def export_conversation(self) -> str:
        """
        Exporta a conversa atual
        
        Returns:
            Conversa em formato JSON
        """
        if not self.conversation_history:
            return "Nenhuma conversa para exportar"
        
        conversation_data = {
            "conversation_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "export_date": datetime.now().isoformat(),
            "messages": self.conversation_history
        }
        
        return json.dumps(conversation_data, indent=2, ensure_ascii=False)
    
    @agno.agent
    def get_example_questions(self) -> List[str]:
        """
        Retorna exemplos de perguntas que podem ser feitas
        
        Returns:
            Lista de perguntas de exemplo
        """
        return [
            "Quais são os sintomas mais comuns da fobia social?",
            "Como funciona a terapia cognitivo-comportamental para fobia social?",
            "Quais técnicas de respiração posso usar durante uma crise de ansiedade?",
            "Como posso me preparar para uma situação social difícil?",
            "Quais são os benefícios da exposição gradual?",
            "Como identificar pensamentos negativos automáticos?",
            "Quais exercícios de relaxamento são mais eficazes?",
            "Como posso ajudar alguém com fobia social?"
        ]
    
    @agno.agent
    def toggle_study_mode(self, enabled: bool) -> str:
        """
        Ativa/desativa o modo estudo
        
        Args:
            enabled: True para ativar modo estudo
            
        Returns:
            Confirmação
        """
        self.study_mode = enabled
        mode = "ativado" if enabled else "desativado"
        return f"✅ Modo estudo {mode} com sucesso!"

def main():
    """
    Função principal para executar a interface Agno
    """
    try:
        interface = AgnoInterface()
        
        # Configura o Agno
        agno.run(
            interface,
            title="🧠 Agente de IA para Fobia Social",
            description="Apoio psicológico baseado em literatura científica especializada",
            port=8501,
            host="localhost"
        )
        
    except Exception as e:
        logger.error(f"Erro fatal na aplicação: {e}")
        raise

if __name__ == "__main__":
    main()
