"""
Ponto de entrada principal do Agente de IA para Fobia Social (Agno)
"""

import argparse
import logging
import sys
from pathlib import Path

from src.utils import setup_logging, ensure_directory_exists
from src.pdf_processor import PDFProcessor
from src.embeddings import PostgresEmbeddingManager
from src.agent import SocialPhobiaAgent
from config.settings import PDF_FOLDER, EMBEDDINGS_FOLDER, LOG_LEVEL

def setup_directories():
    """
    Configura os diretórios necessários
    """
    ensure_directory_exists(PDF_FOLDER)
    ensure_directory_exists(EMBEDDINGS_FOLDER)
    print(f"✅ Diretórios configurados:")
    print(f"   - PDFs: {PDF_FOLDER}")
    print(f"   - Embeddings: {EMBEDDINGS_FOLDER}")

def process_pdfs():
    """
    Processa todos os PDFs na pasta configurada
    """
    print("🔄 Iniciando processamento de PDFs...")
    
    try:
        # Inicializa componentes
        pdf_processor = PDFProcessor()
        embedding_manager = PostgresEmbeddingManager()
        
        # Processa PDFs
        pdf_contents = pdf_processor.process_pdf_folder(PDF_FOLDER)
        
        if not pdf_contents:
            print("⚠️  Nenhum PDF encontrado para processar")
            print(f"   Coloque seus PDFs na pasta: {PDF_FOLDER}")
            return
        
        print(f"📄 {len(pdf_contents)} PDFs encontrados")
        
        # Divide em chunks
        all_chunks = []
        for pdf_content in pdf_contents:
            chunks = pdf_processor.split_pdf_content(pdf_content)
            all_chunks.extend(chunks)
        
        print(f"📝 {len(all_chunks)} chunks criados")
        
        # Adiciona à base vetorial
        embedding_manager.add_documents(all_chunks)
        
        # Mostra informações da coleção
        collection_info = embedding_manager.get_collection_info()
        print(f"✅ Processamento concluído!")
        print(f"   - Documentos na base: {collection_info.get('total_documents', 0)}")
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        logging.error(f"Erro no processamento de PDFs: {e}")
        sys.exit(1)

def run_interface():
    """
    Executa a interface web Agno
    """
    print("🌐 Iniciando interface web Agno...")
    
    try:
        # Importa aqui para evitar problemas de dependência
        from src.interface import main as run_agno_interface
        run_agno_interface()
        
    except ImportError as e:
        print(f"❌ Erro ao importar interface: {e}")
        print("   Certifique-se de que o Agno está instalado: pip install agno")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro na interface: {e}")
        logging.error(f"Erro na interface web: {e}")
        sys.exit(1)

def show_status():
    """
    Mostra o status atual do sistema
    """
    print("📊 Status do Sistema")
    print("=" * 50)
    
    try:
        # Verifica diretórios
        pdf_count = len(list(PDF_FOLDER.glob("*.pdf")))
        print(f"📁 PDFs disponíveis: {pdf_count}")
        
        # Verifica base vetorial
        embedding_manager = PostgresEmbeddingManager()
        collection_info = embedding_manager.get_collection_info()
        print(f"🧠 Documentos processados: {collection_info.get('total_documents', 0)}")
        
        # Verifica configurações
        from config.settings import MODEL_NAME, EMBEDDING_MODEL
        print(f"🤖 Modelo de IA: {MODEL_NAME}")
        print(f"🔍 Modelo de embeddings: {EMBEDDING_MODEL}")
        
        if pdf_count == 0:
            print("\n⚠️  Nenhum PDF encontrado!")
            print(f"   Adicione PDFs na pasta: {PDF_FOLDER}")
        
        if collection_info.get('total_documents', 0) == 0:
            print("\n⚠️  Nenhum documento processado!")
            print("   Execute: python main.py --process-pdfs")
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def main():
    """
    Função principal
    """
    # Configura logging
    logger = setup_logging(LOG_LEVEL)
    
    # Configura parser de argumentos
    parser = argparse.ArgumentParser(
        description="Agente de IA para Tratamento Psicológico em Fobia Social (Agno)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                    # Executa a interface web Agno
  python main.py --process-pdfs     # Processa PDFs apenas
  python main.py --status           # Mostra status do sistema
  python main.py --setup            # Configura diretórios
        """
    )
    
    parser.add_argument(
        '--process-pdfs',
        action='store_true',
        help='Processa PDFs da pasta configurada'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Mostra status atual do sistema'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Configura diretórios necessários'
    )
    
    parser.add_argument(
        '--no-interface',
        action='store_true',
        help='Não executa a interface web (útil com --process-pdfs)'
    )
    
    args = parser.parse_args()
    
    # Executa ações baseadas nos argumentos
    if args.setup:
        setup_directories()
        return
    
    if args.status:
        show_status()
        return
    
    if args.process_pdfs:
        process_pdfs()
        if args.no_interface:
            return
    
    # Por padrão, executa a interface web
    if not args.no_interface:
        run_interface()

if __name__ == "__main__":
    main()
