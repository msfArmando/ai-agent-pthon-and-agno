# 🚀 Guia de Início Rápido

## Instalação e Configuração

### 1. Pré-requisitos
- Python 3.8 ou superior
- Tesseract OCR (para PDFs digitalizados)

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 3. Configuração
1. Configure o ambiente:
```bash
python setup_env.py
```

2. Configure o PostgreSQL:
```bash
python setup_postgres.py
```

2. Edite o arquivo `.env` e adicione sua chave da OpenAI:
```env
OPENAI_API_KEY=sua_chave_api_aqui
```

### 4. Teste o Sistema
```bash
python test_system.py
```

## Uso Básico

### 1. Adicione PDFs
Coloque seus PDFs com informações sobre fobia social na pasta `data/pdfs/`

### 2. Processe os PDFs
```bash
python main.py --process-pdfs
```

### 3. Execute a Interface
```bash
python main.py
```

### 4. Acesse a Interface
Abra seu navegador em `http://localhost:8501`

## Comandos Úteis

```bash
# Verificar status do sistema
python main.py --status

# Processar PDFs sem abrir interface
python main.py --process-pdfs --no-interface

# Configurar diretórios
python main.py --setup
```

## Estrutura do Projeto

```
ai-agent-pthon-and-agno/
├── src/                    # Código fonte
│   ├── agent.py           # Lógica do agente de IA
│   ├── embeddings.py      # Sistema de embeddings
│   ├── interface.py       # Interface web
│   ├── pdf_processor.py   # Processamento de PDFs
│   └── utils.py           # Utilitários
├── config/                # Configurações
│   └── settings.py        # Configurações do sistema
├── data/                  # Dados
│   ├── pdfs/             # PDFs de entrada
│   └── embeddings/       # Base vetorial
├── main.py               # Ponto de entrada
├── requirements.txt      # Dependências
└── README.md            # Documentação completa
```

## Funcionalidades Principais

### 🤖 Agente de IA
- Respostas baseadas em literatura científica
- Tom empático e acolhedor
- Modo estudo para profissionais
- Histórico de conversas

### 📄 Processamento de PDFs
- Suporte a PDFs normais e digitalizados
- OCR automático quando necessário
- Divisão inteligente em chunks
- Extração de metadados

### 🔍 Busca Semântica
- Embeddings com OpenAI
- Armazenamento em PostgreSQL com pgvector
- Busca por similaridade
- Resultados relevantes

### 🌐 Interface Web
- Design moderno e responsivo
- Chat em tempo real
- Modo escuro/claro
- Exportação de conversas

## Exemplos de Perguntas

- "Quais são os sintomas mais comuns da fobia social?"
- "Como funciona a terapia cognitivo-comportamental?"
- "Quais técnicas de respiração posso usar?"
- "Como me preparar para uma situação social difícil?"
- "Quais são os benefícios da exposição gradual?"

## Solução de Problemas

### Erro de API Key
```
❌ OPENAI_API_KEY não configurada
```
**Solução:** Configure sua chave no arquivo `.env`

### Erro de Dependências
```
❌ Módulo não encontrado
```
**Solução:** Execute `pip install -r requirements.txt`

### PDFs não processados
```
⚠️ Nenhum PDF encontrado
```
**Solução:** Adicione PDFs na pasta `data/pdfs/`

### OCR não funciona
```
⚠️ Tesseract OCR não disponível
```
**Solução:** Instale o Tesseract OCR no seu sistema

## Suporte

Para dúvidas ou problemas:
1. Verifique o arquivo `README.md` completo
2. Execute `python test_system.py` para diagnóstico
3. Consulte os logs em `app.log`

---

**⚠️ Aviso Legal:** Este sistema é uma ferramenta educacional e não substitui o acompanhamento profissional de saúde mental.
