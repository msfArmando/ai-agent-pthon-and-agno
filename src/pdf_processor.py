"""
Processador de PDFs para o Agente de IA para Fobia Social
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF
from config.settings import TESSERACT_CMD
from src.utils import clean_text, split_text_into_chunks, generate_file_hash, validate_pdf_file

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Classe para processamento de PDFs com suporte a OCR
    """
    
    def __init__(self, tesseract_cmd: str = TESSERACT_CMD):
        """
        Inicializa o processador de PDFs
        
        Args:
            tesseract_cmd: Comando do Tesseract OCR
        """
        self.tesseract_cmd = tesseract_cmd
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
    def extract_text_from_pdf(self, pdf_path: Path) -> Tuple[str, Dict]:
        """
        Extrai texto de um PDF, usando OCR se necessário
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Tupla com (texto_extraído, metadados)
        """
        if not validate_pdf_file(pdf_path):
            raise ValueError(f"Arquivo PDF inválido: {pdf_path}")
        
        logger.info(f"Processando PDF: {pdf_path}")
        
        # Tenta extrair texto usando diferentes métodos
        text, metadata = self._try_text_extraction(pdf_path)
        
        if not text or len(text.strip()) < 50:
            logger.info(f"Texto insuficiente encontrado, tentando OCR: {pdf_path}")
            text, metadata = self._extract_text_with_ocr(pdf_path)
        
        # Limpa e normaliza o texto
        text = clean_text(text)
        
        # Adiciona metadados do arquivo
        metadata.update({
            'file_path': str(pdf_path),
            'file_size': pdf_path.stat().st_size,
            'file_hash': generate_file_hash(pdf_path),
            'text_length': len(text),
            'processing_method': metadata.get('method', 'unknown')
        })
        
        logger.info(f"PDF processado com sucesso: {pdf_path} - {len(text)} caracteres")
        
        return text, metadata
    
    def _try_text_extraction(self, pdf_path: Path) -> Tuple[str, Dict]:
        """
        Tenta extrair texto usando métodos padrão (sem OCR)
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Tupla com (texto_extraído, metadados)
        """
        text = ""
        metadata = {'method': 'standard_extraction'}
        
        try:
            # Método 1: PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata['pages'] = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Erro ao extrair texto da página {page_num}: {e}")
            
            if text.strip():
                return text, metadata
                
        except Exception as e:
            logger.warning(f"PyPDF2 falhou: {e}")
        
        try:
            # Método 2: pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                metadata['pages'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Erro ao extrair texto da página {page_num}: {e}")
            
            if text.strip():
                metadata['method'] = 'pdfplumber'
                return text, metadata
                
        except Exception as e:
            logger.warning(f"pdfplumber falhou: {e}")
        
        return text, metadata
    
    def _extract_text_with_ocr(self, pdf_path: Path) -> Tuple[str, Dict]:
        """
        Extrai texto usando OCR (Tesseract)
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Tupla com (texto_extraído, metadados)
        """
        text = ""
        metadata = {'method': 'ocr'}
        
        try:
            # Usa PyMuPDF para extrair imagens das páginas
            pdf_document = fitz.open(pdf_path)
            metadata['pages'] = len(pdf_document)
            
            for page_num in range(len(pdf_document)):
                try:
                    page = pdf_document.load_page(page_num)
                    
                    # Renderiza a página como imagem
                    mat = fitz.Matrix(2, 2)  # Aumenta a resolução
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Converte para PIL Image
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Aplica OCR
                    page_text = pytesseract.image_to_string(img, lang='por+eng')
                    
                    if page_text:
                        text += page_text + "\n"
                        
                except Exception as e:
                    logger.warning(f"Erro no OCR da página {page_num}: {e}")
            
            pdf_document.close()
            
        except Exception as e:
            logger.error(f"Erro no processamento OCR: {e}")
            raise
        
        return text, metadata
    
    def process_pdf_folder(self, folder_path: Path) -> List[Dict]:
        """
        Processa todos os PDFs em uma pasta
        
        Args:
            folder_path: Caminho para a pasta com PDFs
            
        Returns:
            Lista de dicionários com texto e metadados de cada PDF
        """
        if not folder_path.exists():
            logger.error(f"Pasta não encontrada: {folder_path}")
            return []
        
        pdf_files = list(folder_path.glob("*.pdf"))
        logger.info(f"Encontrados {len(pdf_files)} arquivos PDF em {folder_path}")
        
        results = []
        
        for pdf_file in pdf_files:
            try:
                text, metadata = self.extract_text_from_pdf(pdf_file)
                if text.strip():
                    results.append({
                        'file_path': str(pdf_file),
                        'text': text,
                        'metadata': metadata
                    })
                else:
                    logger.warning(f"Nenhum texto extraído de: {pdf_file}")
                    
            except Exception as e:
                logger.error(f"Erro ao processar {pdf_file}: {e}")
        
        logger.info(f"Processamento concluído: {len(results)} PDFs processados com sucesso")
        return results
    
    def split_pdf_content(self, pdf_content: Dict, max_chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """
        Divide o conteúdo de um PDF em chunks menores
        
        Args:
            pdf_content: Dicionário com conteúdo do PDF
            max_chunk_size: Tamanho máximo de cada chunk
            overlap: Sobreposição entre chunks
            
        Returns:
            Lista de chunks com metadados
        """
        text = pdf_content['text']
        metadata = pdf_content['metadata']
        
        chunks = split_text_into_chunks(text, max_chunk_size, overlap)
        
        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'chunk_id': f"{metadata['file_hash']}_{i}",
                'file_path': metadata['file_path'],
                'file_hash': metadata['file_hash'],
                'chunk_index': i,
                'total_chunks': len(chunks),
                'text': chunk,
                'metadata': metadata.copy()
            }
            result.append(chunk_data)
        
        return result
