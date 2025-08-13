#!/usr/bin/env python3
"""
Script para testar a conexão com a OpenAI API
"""

from openai import OpenAI
from config.settings import OPENAI_API_KEY, MODEL_NAME, EMBEDDING_MODEL

def test_openai_connection():
    """Testa a conexão com a OpenAI API"""
    print("🤖 Testando conexão com OpenAI API")
    print("=" * 50)
    
    # Verifica se a API key está configurada
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não configurada no arquivo .env")
        return False
    
    if OPENAI_API_KEY == "sua_chave_api_aqui":
        print("❌ OPENAI_API_KEY não foi configurada (ainda está com o valor padrão)")
        return False
    
    print(f"✅ API Key configurada: {OPENAI_API_KEY[:10]}...")
    
    # Cria cliente OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        # Teste 1: Verificar modelos disponíveis
        print("\n📋 Testando listagem de modelos...")
        models = client.models.list()
        print(f"✅ {len(models.data)} modelos disponíveis")
        
        # Teste 2: Testar geração de texto
        print("\n💬 Testando geração de texto...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "Olá! Por favor, responda apenas com 'Teste de conexão bem-sucedido!'"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        assistant_response = response.choices[0].message.content.strip()
        print(f"✅ Resposta recebida: {assistant_response}")
        
        # Teste 3: Testar geração de embeddings
        print("\n🔍 Testando geração de embeddings...")
        embedding_response = client.embeddings.create(
            input="Teste de embedding para fobia social",
            model=EMBEDDING_MODEL
        )
        
        embedding = embedding_response.data[0].embedding
        print(f"✅ Embedding gerado com {len(embedding)} dimensões")
        
        # Teste 4: Verificar uso da API
        print("\n📊 Verificando uso da API...")
        usage = response.usage
        print(f"✅ Tokens utilizados: {usage.total_tokens}")
        print(f"   - Prompt: {usage.prompt_tokens}")
        print(f"   - Completão: {usage.completion_tokens}")
        
        print("\n🎉 Todos os testes da OpenAI API passaram!")
        print("✅ A API key é válida e está funcionando corretamente")
        
        return True
        
    except Exception as e:
        error_message = str(e).lower()
        if "authentication" in error_message or "invalid" in error_message:
            print("❌ Erro de autenticação: API key inválida")
            print("   Verifique se a API key está correta no arquivo .env")
        elif "rate" in error_message or "limit" in error_message:
            print("❌ Erro de limite de taxa: Muitas requisições")
            print("   Aguarde um momento e tente novamente")
        else:
            print(f"❌ Erro da API OpenAI: {e}")
        return False

def test_embedding_manager():
    """Testa o gerenciador de embeddings"""
    print("\n🔍 Testando gerenciador de embeddings...")
    print("=" * 50)
    
    try:
        from src.embeddings import PostgresEmbeddingManager
        
        # Inicializa o gerenciador
        embedding_manager = PostgresEmbeddingManager()
        print("✅ PostgresEmbeddingManager inicializado")
        
        # Testa geração de embeddings
        test_texts = [
            "Fobia social é um transtorno de ansiedade",
            "Terapia cognitivo-comportamental é eficaz",
            "Técnicas de respiração ajudam no controle da ansiedade"
        ]
        
        embeddings = embedding_manager.generate_embeddings(test_texts)
        print(f"✅ {len(embeddings)} embeddings gerados com sucesso")
        
        # Testa busca por similaridade
        query = "Como tratar fobia social?"
        results = embedding_manager.search_similar(query, top_k=2)
        print(f"✅ Busca por similaridade retornou {len(results)} resultados")
        
        # Testa informações da coleção
        collection_info = embedding_manager.get_collection_info()
        print(f"✅ Informações da coleção: {collection_info['total_documents']} documentos")
        
        print("🎉 Gerenciador de embeddings funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no gerenciador de embeddings: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste Completo da OpenAI API")
    print("=" * 60)
    
    # Testa conexão com OpenAI
    openai_success = test_openai_connection()
    
    if openai_success:
        # Testa gerenciador de embeddings
        embedding_success = test_embedding_manager()
        
        if embedding_success:
            print("\n" + "=" * 60)
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ OpenAI API: Funcionando")
            print("✅ Embeddings: Funcionando")
            print("✅ PostgreSQL: Configurado")
            print("\n🚀 O sistema está pronto para uso!")
        else:
            print("\n⚠️  Alguns testes falharam")
            print("   Verifique as configurações do PostgreSQL")
    else:
        print("\n❌ Testes da OpenAI falharam")
        print("   Configure uma API key válida no arquivo .env")

if __name__ == "__main__":
    main()
