#!/bin/bash
# setup.sh - Script de setup completo do CV Agent

echo "🚀 Configurando CV Agent LangGraph..."

# Criar diretório do projeto
mkdir cv-agent-langgraph
cd cv-agent-langgraph

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python -m venv venv

# Ativar ambiente virtual
if [[ "$OSTYPE" == "msys" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Instalar dependências
echo "📚 Instalando dependências..."
pip install --upgrade pip
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0
pip install langgraph==0.0.55 langchain==0.1.0 langchain-openai==0.0.2
pip install openai==1.3.0 PyPDF2==3.0.1
pip install aiofiles==23.2.1 python-multipart==0.0.6
pip install python-dotenv==1.0.0

# Criar arquivo .env
echo "⚙️ Configurando variáveis de ambiente..."
cat > .env << EOL
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
EOL

# Criar main.py (será copiado do artifact)
echo "📄 Criando arquivo principal..."
echo "# Copie o conteúdo do artifact 'CV Agent Backend - LangGraph' aqui" > main.py

# Criar README
cat > README.md << EOL
# CV Agent - LangGraph

Sistema de análise de currículo usando LangGraph e OpenAI.

## Setup Rápido

1. Configure sua API key do OpenAI no arquivo .env
2. Execute: \`uvicorn main:app --reload\`
3. Acesse: http://localhost:8000

## Arquitetura

- **LangGraph**: Workflow agentic
- **OpenAI**: LLM para análise
- **FastAPI**: Backend assíncrono
- **React**: Frontend interativo

## Funcionalidades

- ✅ Upload de CV em PDF
- ✅ Classificação automática de perguntas
- ✅ Ferramentas especializadas por domínio
- ✅ Workflow visual em tempo real
- ✅ Validação automática de qualidade
- ✅ Score de confiança
- ✅ Self-healing system

## Para Entrevistas

Este projeto demonstra:
- **Cloud**: Deploy containerizado
- **LLM**: RAG avançado + Agent reasoning
- **Async**: Pipeline não-bloqueante
EOL

# Criar docker-compose para desenvolvimento
cat > docker-compose.yml << EOL
version: '3.8'

services:
  cv-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
    volumes:
      - ./main.py:/app/main.py
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  frontend:
    image: node:18-alpine
    working_dir: /app
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    command: ["npm", "start"]
    depends_on:
      - cv-agent
EOL

# Criar script de teste
cat > test_agent.py << EOL
#!/usr/bin/env python3
"""
Script de teste para o CV Agent
"""
import asyncio
import requests
import json

API_BASE = "http://localhost:8000"

async def test_agent():
    print("🧪 Testando CV Agent...")
    
    # Teste 1: Health check
    print("\n1. Health Check:")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Teste 2: Graph info
    print("\n2. Graph Info:")
    response = requests.get(f"{API_BASE}/graph-info")
    print(f"Nodes: {response.json()['nodes']}")
    print(f"Tools: {response.json()['tools']}")
    
    # Teste 3: Examples
    print("\n3. Example Questions:")
    response = requests.get(f"{API_BASE}/examples")
    examples = response.json()
    for category, questions in examples.items():
        print(f"{category}: {len(questions)} perguntas")

if __name__ == "__main__":
    asyncio.run(test_agent())
EOL

chmod +x test_agent.py

echo "✅ Setup completo!"
echo ""
echo "📋 Próximos passos:"
echo "1. Edite o arquivo .env com sua OpenAI API key"
echo "2. Copie o código do backend para main.py"
echo "3. Execute: uvicorn main:app --reload"
echo "4. Teste: python test_agent.py"
echo ""
echo "🌐 URLs:"
echo "- Backend: http://localhost:8000"
echo "- Docs: http://localhost:8000/docs"
echo "- Health: http://localhost:8000/health"