#!/usr/bin/env python3
"""
Teste simples da OpenAI API
"""

from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_API_BASE

def test_simple():
    """Teste simples da API"""
    print("🔍 Teste Simples da OpenAI API")
    print("=" * 40)
    
    print(f"API Key: {OPENAI_API_KEY[:20]}...")
    print(f"API Base: {OPENAI_API_BASE}")
    
    if not OPENAI_API_KEY:
        print("❌ API Key não configurada")
        return
    
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )
    
    try:
        # Teste mais simples - apenas uma chamada básica
        print("\n📞 Testando chamada básica...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Diga apenas 'OK'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ Resposta: {result}")
        print("🎉 API funcionando!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        
        # Análise detalhada do erro
        error_str = str(e).lower()
        if "authentication" in error_str:
            print("🔍 Problema: Autenticação falhou")
            print("💡 Solução: Verifique se a API key está correta")
        elif "rate" in error_str:
            print("🔍 Problema: Limite de taxa excedido")
            print("💡 Solução: Aguarde um momento e tente novamente")
        elif "quota" in error_str:
            print("🔍 Problema: Cota excedida")
            print("💡 Solução: Verifique o saldo da sua conta OpenAI")
        elif "model" in error_str:
            print("🔍 Problema: Modelo não encontrado")
            print("💡 Solução: Verifique se o modelo está disponível")
        else:
            print("🔍 Problema: Erro desconhecido")
            print("💡 Solução: Verifique a documentação da OpenAI")

if __name__ == "__main__":
    test_simple()
