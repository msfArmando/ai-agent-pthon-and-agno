#!/usr/bin/env python3
"""
Script para listar modelos disponíveis na API customizada
"""

from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_API_BASE

def list_models():
    """Lista os modelos disponíveis"""
    print("🔍 Listando modelos disponíveis na API")
    print("=" * 50)
    
    print(f"API Base: {OPENAI_API_BASE}")
    
    if not OPENAI_API_KEY:
        print("❌ API Key não configurada")
        return
    
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )
    
    try:
        print("\n📋 Buscando modelos disponíveis...")
        models = client.models.list()
        
        print(f"✅ {len(models.data)} modelos encontrados:")
        print("-" * 30)
        
        for model in models.data:
            print(f"• {model.id}")
            if hasattr(model, 'created'):
                print(f"  Criado em: {model.created}")
            if hasattr(model, 'owned_by'):
                print(f"  Proprietário: {model.owned_by}")
            print()
        
        # Sugere o primeiro modelo para teste
        if models.data:
            first_model = models.data[0].id
            print(f"💡 Sugestão: Use '{first_model}' para testes")
            
            # Testa o primeiro modelo
            print(f"\n🧪 Testando modelo: {first_model}")
            response = client.chat.completions.create(
                model=first_model,
                messages=[{"role": "user", "content": "Diga apenas 'OK'"}],
                max_tokens=10
            )
            
            result = response.choices[0].message.content
            print(f"✅ Resposta: {result}")
            print("🎉 Modelo funcionando!")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"Tipo do erro: {type(e).__name__}")

if __name__ == "__main__":
    list_models()
