# server.py - FastAPI server implementation
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from cv_agent import CVAgent
import logging

logger = logging.getLogger(__name__)


class CVServer:
    def __init__(self, openai_api_key: str):
        self.app = FastAPI(title="CV Agent - LangGraph Powered")
        self.app.add_middleware(
            CORSMiddleware, allow_origins=["*"], allow_methods=["*"]
        )

        # Initialize CV Agent
        self.cv_agent = CVAgent(openai_api_key)

        # Setup routes
        self.setup_routes()

    def setup_routes(self):
        """Setup all FastAPI routes"""

        @self.app.post("/upload")
        async def upload_cv(file: UploadFile = File(...)):
            """Upload e processamento do CV"""
            if not file.filename.endswith(".pdf"):
                raise HTTPException(400, "Apenas arquivos PDF são aceitos")

            try:
                content = await file.read()
                result = await self.cv_agent.process_cv(content, file.filename)
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @self.app.post("/ask")
        async def ask_question(question: str):
            """Fazer pergunta usando LangGraph Agent"""
            try:
                result = await self.cv_agent.ask_question(question)
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @self.app.get("/health")
        async def health_check():
            """Status do sistema"""
            return {
                "status": "healthy",
                "cv_loaded": self.cv_agent.is_cv_loaded(),
                "cv_length": self.cv_agent.get_cv_length(),
                "agent_ready": self.cv_agent.is_ready(),
            }

        @self.app.get("/graph-info")
        async def get_graph_info():
            """Informações sobre o grafo LangGraph"""
            return {
                "nodes": [
                    "classifier",
                    "tool_selector",
                    "information_extractor",
                    "context_analyzer",
                    "answer_generator",
                    "quality_validator",
                    "confidence_calculator",
                ],
                "tools": self.cv_agent.get_tools(),
                "workflow_types": [
                    "need_extraction",
                    "direct_analysis",
                    "simple_answer",
                ],
            }

        @self.app.get("/examples")
        async def get_examples():
            """Perguntas de exemplo organizadas por tipo"""
            return {
                "experience": [
                    "Qual é a experiência profissional mais recente?",
                    "Quantos anos de experiência total possui?",
                    "Quais foram as principais responsabilidades no último cargo?",
                ],
                "skills": [
                    "Quais são as principais habilidades técnicas?",
                    "Tem experiência com Python?",
                    "Quais frameworks conhece?",
                ],
                "education": [
                    "Qual é a formação acadêmica?",
                    "Possui certificações relevantes?",
                    "Onde estudou?",
                ],
                "projects": [
                    "Quais projetos desenvolveu?",
                    "Qual foi o projeto mais desafiador?",
                    "Que tecnologias usou nos projetos?",
                ],
                "career": [
                    "Como foi a progressão profissional?",
                    "De forma resumida, qual é a experiência profissional do candidato?",
                    "Quais são os pontos fortes do candidato?",
                ],
            }

        @self.app.get("/graph-image")
        async def get_graph_image():
            """Retorna imagem PNG do grafo LangGraph"""
            try:
                image_data = self.cv_agent.generate_graph_image()
                if not image_data:
                    raise HTTPException(500, "Não foi possível gerar a imagem do grafo")

                return Response(
                    content=image_data,
                    media_type="image/png",
                    headers={"Content-Disposition": "inline; filename=langgraph.png"},
                )
            except Exception as e:
                raise HTTPException(500, f"Erro ao gerar imagem: {str(e)}")

        @self.app.get("/graph-mermaid")
        async def get_graph_mermaid():
            """Retorna código Mermaid do grafo"""
            try:
                mermaid_code = self.cv_agent.get_graph_mermaid()
                return {"mermaid": mermaid_code}
            except Exception as e:
                raise HTTPException(500, f"Erro ao gerar Mermaid: {str(e)}")

    def get_app(self):
        """Retorna a instância do FastAPI app"""
        return self.app
