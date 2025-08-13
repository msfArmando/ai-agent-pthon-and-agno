# Agente de IA para Tratamento Psicológico em Fobia Social

## Descrição

Este projeto implementa um agente de inteligência artificial especializado no apoio psicológico a pessoas com fobia social. O sistema utiliza documentos PDF fornecidos pelo administrador para oferecer interações úteis, embasadas e respeitosas, com foco em ajudar o usuário a compreender e aplicar técnicas de tratamento e manejo da condição.

## Características Principais

- **Processamento de PDFs**: Suporte a PDFs com e sem OCR
- **Busca Semântica**: Utiliza embeddings para encontrar informações relevantes
- **Interface Intuitiva**: Interface web limpa e focada na função principal
- **Tom Empático**: Comunicação calma, respeitosa e acolhedora
- **Base Científica**: Respostas sempre fundamentadas no material dos PDFs
- **Modo Estudo**: Opção para profissionais com respostas mais técnicas

## Estrutura do Projeto

```
ai-agent-pthon-and-agno/
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py      # Processamento de PDFs
│   ├── embeddings.py         # Geração e busca de embeddings
│   ├── agent.py             # Lógica do agente de IA
│   ├── interface.py         # Interface web
│   └── utils.py             # Utilitários
├── data/
│   ├── pdfs/                # Pasta para PDFs de entrada
│   └── embeddings/          # Armazenamento de embeddings
├── config/
│   └── settings.py          # Configurações do sistema
├── requirements.txt
├── .env.example
└── main.py                  # Ponto de entrada da aplicação
```

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd ai-agent-pthon-and-agno
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

5. Instale o Tesseract OCR (para PDFs digitalizados):
   - **Windows**: Baixe e instale de https://github.com/UB-Mannheim/tesseract/wiki
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **Mac**: `brew install tesseract`

## Uso

1. **Preparação dos PDFs**:
   - Coloque os PDFs com informações sobre fobia social na pasta `data/pdfs/`

2. **Processamento inicial**:
```bash
python main.py --process-pdfs
```

3. **Executar a aplicação**:
```bash
python main.py
```

4. **Acessar a interface**:
   - Abra o navegador em `http://localhost:8501`

## Configuração

### Variáveis de Ambiente (.env)

```env
# OpenAI API
OPENAI_API_KEY=sua_chave_api_aqui

# Configurações do sistema
PDF_FOLDER=data/pdfs
EMBEDDINGS_FOLDER=data/embeddings
MODEL_NAME=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002

# Configurações da interface
HOST=localhost
PORT=8501
```

## Funcionalidades

### 1. Processamento de PDFs
- Extração de texto de PDFs normais e digitalizados
- Aplicação de OCR quando necessário
- Pré-processamento e limpeza do texto

### 2. Sistema de Embeddings
- Geração de embeddings usando OpenAI
- Armazenamento em PostgreSQL com pgvector
- Busca semântica eficiente

### 3. Agente de IA
- Respostas baseadas no conteúdo dos PDFs
- Tom empático e acolhedor
- Modo estudo para profissionais
- Histórico de conversas

### 4. Interface Web
- Interface limpa e intuitiva
- Chat em tempo real
- Modo escuro/claro
- Responsiva para diferentes dispositivos

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Aviso Legal

Este sistema é uma ferramenta de apoio educacional e não substitui o acompanhamento profissional de saúde mental. Sempre consulte um profissional qualificado para diagnóstico e tratamento adequados.
