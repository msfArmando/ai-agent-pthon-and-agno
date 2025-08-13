"""
Script de teste para verificar se o sistema está funcionando corretamente
"""

import sys
import os
from pathlib import Path

def test_imports():
    """
    Testa se todas as dependências estão instaladas
    """
    print("🔍 Testando imports...")
    
    try:
        import streamlit
        print("✅ Streamlit")
    except ImportError:
        print("❌ Streamlit não encontrado")
        return False
    
    try:
        import openai
        print("✅ OpenAI")
    except ImportError:
        print("❌ OpenAI não encontrado")
        return False
    
    try:
        import psycopg2
        print("✅ psycopg2 (PostgreSQL)")
    except ImportError:
        print("❌ psycopg2 não encontrado")
        return False
    
    try:
        import pgvector
        print("✅ pgvector")
    except ImportError:
        print("❌ pgvector não encontrado")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2")
    except ImportError:
        print("❌ PyPDF2 não encontrado")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber")
    except ImportError:
        print("❌ pdfplumber não encontrado")
        return False
    
    try:
        import pytesseract
        print("✅ pytesseract")
    except ImportError:
        print("❌ pytesseract não encontrado")
        return False
    
    try:
        import fitz
        print("✅ PyMuPDF")
    except ImportError:
        print("❌ PyMuPDF não encontrado")
        return False
    
    return True

def test_configuration():
    """
    Testa se as configurações estão corretas
    """
    print("\n⚙️  Testando configurações...")
    
    try:
        from config.settings import OPENAI_API_KEY, PDF_FOLDER, EMBEDDINGS_FOLDER
        
        if not OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY não configurada")
        else:
            print("✅ OPENAI_API_KEY configurada")
        
        print(f"✅ PDF_FOLDER: {PDF_FOLDER}")
        print(f"✅ EMBEDDINGS_FOLDER: {EMBEDDINGS_FOLDER}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_modules():
    """
    Testa se os módulos do projeto podem ser importados
    """
    print("\n📦 Testando módulos do projeto...")
    
    try:
        from src.utils import setup_logging
        print("✅ src.utils")
    except Exception as e:
        print(f"❌ src.utils: {e}")
        return False
    
    try:
        from src.pdf_processor import PDFProcessor
        print("✅ src.pdf_processor")
    except Exception as e:
        print(f"❌ src.pdf_processor: {e}")
        return False
    
    try:
        from src.embeddings import EmbeddingManager
        print("✅ src.embeddings")
    except Exception as e:
        print(f"❌ src.embeddings: {e}")
        return False
    
    try:
        from src.agent import SocialPhobiaAgent
        print("✅ src.agent")
    except Exception as e:
        print(f"❌ src.agent: {e}")
        return False
    
    return True

def test_directories():
    """
    Testa se os diretórios necessários existem
    """
    print("\n📁 Testando diretórios...")
    
    from config.settings import PDF_FOLDER, EMBEDDINGS_FOLDER
    
    if PDF_FOLDER.exists():
        print(f"✅ PDF_FOLDER existe: {PDF_FOLDER}")
    else:
        print(f"⚠️  PDF_FOLDER não existe: {PDF_FOLDER}")
    
    if EMBEDDINGS_FOLDER.exists():
        print(f"✅ EMBEDDINGS_FOLDER existe: {EMBEDDINGS_FOLDER}")
    else:
        print(f"⚠️  EMBEDDINGS_FOLDER não existe: {EMBEDDINGS_FOLDER}")
    
    return True

def test_ocr():
    """
    Testa se o Tesseract OCR está disponível
    """
    print("\n🔤 Testando OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR disponível: {version}")
        return True
    except Exception as e:
        print(f"⚠️  Tesseract OCR não disponível: {e}")
        print("   Para PDFs digitalizados, instale o Tesseract OCR")
        return False

def main():
    """
    Executa todos os testes
    """
    print("🧪 Iniciando testes do sistema...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_modules,
        test_directories,
        test_ocr
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Resumo dos testes:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Testes aprovados: {passed}/{total}")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está pronto para uso.")
        print("\n📋 Próximos passos:")
        print("1. Configure sua OPENAI_API_KEY no arquivo .env")
        print("2. Adicione PDFs na pasta data/pdfs/")
        print("3. Execute: python main.py --process-pdfs")
        print("4. Execute: python main.py")
    else:
        print("⚠️  Alguns testes falharam. Verifique as dependências e configurações.")
        print("\n🔧 Para instalar dependências:")
        print("pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
