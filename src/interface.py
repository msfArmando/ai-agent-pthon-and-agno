"""
Interface web para o Agente de IA para Fobia Social
"""

import streamlit as st
import logging
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

from src.agent import SocialPhobiaAgent
from src.embeddings import PostgresEmbeddingManager
from src.pdf_processor import PDFProcessor
from src.utils import setup_logging
from config.settings import PDF_FOLDER, EMBEDDINGS_FOLDER

logger = setup_logging()

class WebInterface:
    """
    Interface web para o Agente de IA usando Streamlit
    """
    
    def __init__(self):
        """
        Inicializa a interface web
        """
        self.setup_page_config()
        self.initialize_session_state()
        
        # Inicializa componentes
        try:
            self.embedding_manager = PostgresEmbeddingManager()
            self.agent = SocialPhobiaAgent(self.embedding_manager)
            self.pdf_processor = PDFProcessor()
        except Exception as e:
            st.error(f"Erro ao inicializar componentes: {e}")
            st.stop()
    
    def setup_page_config(self):
        """
        Configura a página do Streamlit
        """
        st.set_page_config(
            page_title="Agente de IA - Fobia Social",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # CSS personalizado
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid;
        }
        .user-message {
            background-color: #e3f2fd;
            border-left-color: #2196f3;
        }
        .assistant-message {
            background-color: #f3e5f5;
            border-left-color: #9c27b0;
        }
        .sidebar-info {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online {
            background-color: #4caf50;
        }
        .status-offline {
            background-color: #f44336;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """
        Inicializa o estado da sessão
        """
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'study_mode' not in st.session_state:
            st.session_state.study_mode = False
        
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def render_header(self):
        """
        Renderiza o cabeçalho da aplicação
        """
        st.markdown('<h1 class="main-header">🧠 Agente de IA para Fobia Social</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.1rem; color: #666;">
                Apoio psicológico baseado em literatura científica especializada
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """
        Renderiza a barra lateral
        """
        with st.sidebar:
            st.header("⚙️ Configurações")
            
            # Modo de estudo
            study_mode = st.checkbox(
                "📚 Modo Estudo (Profissionais)",
                value=st.session_state.study_mode,
                help="Ativa respostas mais técnicas e detalhadas"
            )
            st.session_state.study_mode = study_mode
            
            st.divider()
            
            # Informações do sistema
            st.subheader("📊 Informações do Sistema")
            
            try:
                agent_info = self.agent.get_agent_info()
                
                st.markdown(f"""
                <div class="sidebar-info">
                    <p><strong>Modelo:</strong> {agent_info['model_name']}</p>
                    <p><strong>Documentos:</strong> {agent_info['documents_available']}</p>
                    <p><strong>Mensagens:</strong> {agent_info['conversation_length']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Status do sistema
                st.markdown("""
                <div style="margin-top: 1rem;">
                    <span class="status-indicator status-online"></span>
                    <span>Sistema Online</span>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erro ao obter informações: {e}")
            
            st.divider()
            
            # Ações
            st.subheader("🛠️ Ações")
            
            if st.button("🗑️ Limpar Conversa", type="secondary"):
                self.clear_conversation()
            
            if st.button("📥 Exportar Conversa", type="secondary"):
                self.export_conversation()
            
            if st.button("🔄 Processar PDFs", type="secondary"):
                self.process_pdfs()
            
            st.divider()
            
            # Aviso legal
            st.markdown("""
            <div style="font-size: 0.8rem; color: #666; margin-top: 2rem;">
                <strong>⚠️ Aviso Legal:</strong><br>
                Este sistema é uma ferramenta educacional e não substitui 
                o acompanhamento profissional de saúde mental.
            </div>
            """, unsafe_allow_html=True)
    
    def render_chat_interface(self):
        """
        Renderiza a interface de chat
        """
        # Container principal do chat
        chat_container = st.container()
        
        with chat_container:
            # Área de mensagens
            messages_container = st.container()
            
            with messages_container:
                # Exibe mensagens existentes
                for message in st.session_state.messages:
                    self.display_message(message)
            
            # Área de entrada
            input_container = st.container()
            
            with input_container:
                st.markdown("---")
                
                # Campo de entrada
                user_input = st.text_area(
                    "💬 Digite sua pergunta:",
                    placeholder="Ex: Quais são as principais técnicas para lidar com ansiedade social?",
                    height=100,
                    key="user_input"
                )
                
                # Botões de ação
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if st.button("🚀 Enviar", type="primary", use_container_width=True):
                        if user_input.strip():
                            self.process_user_input(user_input.strip())
                
                with col2:
                    if st.button("❓ Exemplo", use_container_width=True):
                        self.show_example_questions()
                
                with col3:
                    if st.button("🆘 Ajuda", use_container_width=True):
                        self.show_help()
    
    def display_message(self, message: dict):
        """
        Exibe uma mensagem no chat
        
        Args:
            message: Dicionário com a mensagem
        """
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 Você:</strong><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistente:</strong><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
    
    def process_user_input(self, user_input: str):
        """
        Processa a entrada do usuário
        
        Args:
            user_input: Texto da pergunta do usuário
        """
        # Adiciona mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Mostra indicador de carregamento
        with st.spinner("🤔 Pensando..."):
            try:
                # Gera resposta
                response = self.agent.generate_response(
                    user_input, 
                    study_mode=st.session_state.study_mode
                )
                
                # Adiciona resposta do assistente
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Limpa o campo de entrada
                st.rerun()
                
            except Exception as e:
                error_msg = f"Desculpe, ocorreu um erro: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()
    
    def clear_conversation(self):
        """
        Limpa a conversa atual
        """
        st.session_state.messages = []
        self.agent.clear_conversation_history()
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.success("Conversa limpa com sucesso!")
        st.rerun()
    
    def export_conversation(self):
        """
        Exporta a conversa atual
        """
        if not st.session_state.messages:
            st.warning("Nenhuma conversa para exportar")
            return
        
        # Prepara dados para exportação
        export_data = {
            'conversation_id': st.session_state.conversation_id,
            'timestamp': datetime.now().isoformat(),
            'study_mode': st.session_state.study_mode,
            'messages': st.session_state.messages
        }
        
        # Converte para JSON
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Cria arquivo para download
        st.download_button(
            label="📥 Baixar Conversa (JSON)",
            data=json_str,
            file_name=f"conversa_fobia_social_{st.session_state.conversation_id}.json",
            mime="application/json"
        )
    
    def process_pdfs(self):
        """
        Processa PDFs da pasta configurada
        """
        try:
            with st.spinner("📄 Processando PDFs..."):
                # Processa PDFs
                pdf_contents = self.pdf_processor.process_pdf_folder(PDF_FOLDER)
                
                if not pdf_contents:
                    st.warning("Nenhum PDF encontrado para processar")
                    return
                
                # Divide em chunks
                all_chunks = []
                for pdf_content in pdf_contents:
                    chunks = self.pdf_processor.split_pdf_content(pdf_content)
                    all_chunks.extend(chunks)
                
                # Adiciona à base vetorial
                self.embedding_manager.add_documents(all_chunks)
                
                st.success(f"✅ {len(pdf_contents)} PDFs processados com sucesso!")
                
        except Exception as e:
            st.error(f"Erro ao processar PDFs: {e}")
    
    def show_example_questions(self):
        """
        Mostra exemplos de perguntas
        """
        examples = [
            "Quais são os sintomas mais comuns da fobia social?",
            "Como funciona a terapia cognitivo-comportamental para fobia social?",
            "Quais técnicas de respiração posso usar durante uma crise de ansiedade?",
            "Como posso me preparar para uma situação social difícil?",
            "Quais são os benefícios da exposição gradual?",
            "Como identificar pensamentos negativos automáticos?",
            "Quais exercícios de relaxamento são mais eficazes?",
            "Como posso ajudar alguém com fobia social?"
        ]
        
        st.info("💡 **Exemplos de perguntas que você pode fazer:**")
        for i, example in enumerate(examples, 1):
            st.write(f"{i}. {example}")
    
    def show_help(self):
        """
        Mostra informações de ajuda
        """
        st.info("""
        **🤝 Como usar o Agente de IA:**
        
        • **Faça perguntas específicas** sobre fobia social e ansiedade
        • **Use o Modo Estudo** para respostas mais técnicas (profissionais)
        • **Seja específico** em suas perguntas para respostas mais precisas
        • **Consulte um profissional** para diagnóstico e tratamento adequados
        
        **📚 O sistema utiliza:**
        • Literatura científica sobre fobia social
        • Técnicas de terapia cognitivo-comportamental
        • Estratégias de manejo da ansiedade
        • Informações sobre tratamento profissional
        """)
    
    def run(self):
        """
        Executa a interface web
        """
        try:
            self.render_header()
            self.render_sidebar()
            self.render_chat_interface()
            
        except Exception as e:
            st.error(f"Erro na interface: {e}")
            logger.error(f"Erro na interface web: {e}")

def main():
    """
    Função principal para executar a interface
    """
    try:
        interface = WebInterface()
        interface.run()
    except Exception as e:
        st.error(f"Erro ao inicializar a aplicação: {e}")
        logger.error(f"Erro fatal na aplicação: {e}")

if __name__ == "__main__":
    main()
