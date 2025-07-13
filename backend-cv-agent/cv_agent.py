import tempfile
import os
import json
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import PyPDF2
from datetime import datetime
import logging
from models import CVAgentState

logger = logging.getLogger(__name__)


class CVAgent:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.1, api_key=openai_api_key
        )
        self.cv_content = ""
        self.setup_tools()
        self.setup_graph()

    def setup_tools(self):
        """Ferramentas especializadas para análise de CV"""
        self.tools = {
            "extract_experience": Tool(
                name="extract_experience",
                description="Extrai experiência profissional detalhada do CV",
                func=self.extract_experience,
            ),
            "extract_skills": Tool(
                name="extract_skills",
                description="Extrai habilidades técnicas e competências",
                func=self.extract_skills,
            ),
            "extract_education": Tool(
                name="extract_education",
                description="Extrai formação acadêmica e certificações",
                func=self.extract_education,
            ),
            "extract_projects": Tool(
                name="extract_projects",
                description="Extrai projetos e realizações",
                func=self.extract_projects,
            ),
            "extract_personal_info": Tool(
                name="extract_personal_info",
                description="Extrai informações pessoais e contato",
                func=self.extract_personal_info,
            ),
            "analyze_career_progression": Tool(
                name="analyze_career_progression",
                description="Analisa progressão e crescimento profissional",
                func=self.analyze_career_progression,
            ),
        }

    def setup_graph(self):
        """Configura o grafo de execução do Agent"""
        workflow = StateGraph(CVAgentState)

        # Nodes do workflow
        workflow.add_node("classifier", self.classify_question)
        workflow.add_node("tool_selector", self.select_tools)
        workflow.add_node("information_extractor", self.extract_information)
        workflow.add_node("context_analyzer", self.analyze_context)
        workflow.add_node("answer_generator", self.generate_answer)
        workflow.add_node("quality_validator", self.validate_quality)
        workflow.add_node("confidence_calculator", self.calculate_confidence)

        # Fluxo do grafo
        workflow.set_entry_point("classifier")

        # Edges condicionais
        workflow.add_conditional_edges(
            "classifier",
            self.route_after_classification,
            {
                "need_extraction": "tool_selector",
                "direct_analysis": "context_analyzer",
                "simple_answer": "answer_generator",
            },
        )

        workflow.add_edge("tool_selector", "information_extractor")
        workflow.add_edge("information_extractor", "context_analyzer")
        workflow.add_edge("context_analyzer", "answer_generator")
        workflow.add_edge("answer_generator", "quality_validator")

        # Validação condicional
        workflow.add_conditional_edges(
            "quality_validator",
            self.route_after_validation,
            {
                "approved": "confidence_calculator",
                "retry": "context_analyzer",
                "reclassify": "classifier",
            },
        )

        workflow.add_edge("confidence_calculator", END)

        self.app = workflow.compile()

    # === NODES DO WORKFLOW ===

    def classify_question(self, state: CVAgentState) -> CVAgentState:
        """Classifica o tipo de pergunta e complexidade"""
        question = state["current_question"]

        classification_prompt = f"""
        Analise esta pergunta sobre um CV profissional e classifique:
        
        Pergunta: "{question}"
        
        Classifique em:
        1. TIPO:
           - experience: Sobre experiência profissional, cargos, empresas
           - skills: Sobre habilidades técnicas, competências
           - education: Sobre formação, cursos, certificações
           - projects: Sobre projetos realizados
           - personal: Sobre informações pessoais, contato
           - career: Sobre progressão, crescimento profissional
           - general: Pergunta geral sobre o perfil
        
        2. COMPLEXIDADE:
           - simple: Pergunta direta, informação específica
           - complex: Requer análise, comparação, síntese
           - analytical: Requer interpretação profunda, insights
        
        Retorne apenas: TIPO|COMPLEXIDADE
        """

        response = self.llm.invoke([HumanMessage(content=classification_prompt)])
        classification = response.content.strip().split("|")

        question_type = classification[0].lower()
        complexity = classification[1].lower() if len(classification) > 1 else "simple"

        state["question_type"] = question_type
        state["workflow_path"] = ["classifier"]
        state["extracted_info"] = {"complexity": complexity}

        return state

    def route_after_classification(self, state: CVAgentState) -> str:
        """Roteamento baseado na classificação"""
        question_type = state["question_type"]
        complexity = state["extracted_info"].get("complexity", "simple")

        if question_type in [
            "experience",
            "skills",
            "education",
            "projects",
            "personal",
        ]:
            return "need_extraction"
        elif complexity == "analytical":
            return "direct_analysis"
        else:
            return "simple_answer"

    def select_tools(self, state: CVAgentState) -> CVAgentState:
        """Seleciona ferramentas apropriadas para a pergunta"""
        question_type = state["question_type"]
        complexity = state["extracted_info"].get("complexity", "simple")

        tool_mapping = {
            "experience": ["extract_experience", "analyze_career_progression"],
            "skills": ["extract_skills"],
            "education": ["extract_education"],
            "projects": ["extract_projects"],
            "personal": ["extract_personal_info"],
            "career": ["extract_experience", "analyze_career_progression"],
            "general": ["extract_experience", "extract_skills", "extract_education"],
        }

        selected_tools = tool_mapping.get(question_type, ["extract_experience"])

        # Para perguntas complexas, adicionar mais ferramentas
        if complexity in ["complex", "analytical"]:
            if "analyze_career_progression" not in selected_tools:
                selected_tools.append("analyze_career_progression")

        state["tools_used"] = selected_tools
        state["workflow_path"].append("tool_selector")

        return state

    def extract_information(self, state: CVAgentState) -> CVAgentState:
        """Extrai informações usando as ferramentas selecionadas"""
        tools_to_use = state["tools_used"]
        extracted_data = {}

        for tool_name in tools_to_use:
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name].func(state["cv_content"])
                    extracted_data[tool_name] = result
                except Exception as e:
                    logger.error(f"Erro ao usar ferramenta {tool_name}: {e}")
                    extracted_data[tool_name] = f"Erro na extração: {str(e)}"

        state["extracted_info"].update(extracted_data)
        state["workflow_path"].append("information_extractor")

        return state

    def analyze_context(self, state: CVAgentState) -> CVAgentState:
        """Analisa o contexto e prepara informações relevantes"""
        question = state["current_question"]
        extracted_info = state["extracted_info"]

        # Filtrar informações relevantes para a pergunta
        relevant_info = {}
        for key, value in extracted_info.items():
            if key != "complexity" and value:
                relevant_info[key] = value

        context_analysis = f"""
        Pergunta: {question}
        Informações extraídas: {json.dumps(relevant_info, indent=2, ensure_ascii=False)}
        
        Contexto analisado e preparado para geração de resposta.
        """

        state["extracted_info"]["context_analysis"] = context_analysis
        state["workflow_path"].append("context_analyzer")

        return state

    def generate_answer(self, state: CVAgentState) -> CVAgentState:
        """Gera resposta baseada no contexto analisado"""
        question = state["current_question"]
        context = state["extracted_info"].get("context_analysis", "")
        question_type = state["question_type"]

        # Prompt especializado por tipo de pergunta
        specialized_prompts = {
            "experience": """
            Você é um especialista em análise de experiência profissional.
            Responda focando em: cargos, empresas, período, responsabilidades e conquistas.
            """,
            "skills": """
            Você é um especialista em análise de competências técnicas.
            Responda focando em: tecnologias, linguagens, frameworks, nível de experiência.
            """,
            "education": """
            Você é um especialista em análise de formação acadêmica.
            Responda focando em: cursos, instituições, período, certificações.
            """,
            "projects": """
            Você é um especialista em análise de projetos.
            Responda focando em: descrição, tecnologias, resultados, impacto.
            """,
            "career": """
            Você é um especialista em análise de progressão profissional.
            Responda focando em: crescimento, evolução, tendências.
            """,
        }

        system_prompt = specialized_prompts.get(
            question_type,
            "Você é um assistente especializado em análise de currículos profissionais.",
        )

        generation_prompt = f"""
        {system_prompt}
        
        Contexto disponível:
        {context}
        
        Pergunta: "{question}"
        
        Diretrizes para resposta:
        1. Seja preciso e objetivo
        2. Use informações específicas do CV quando disponível
        3. Se não houver informação suficiente, diga claramente
        4. Mantenha tom profissional mas acessível
        5. Estruture a resposta de forma clara
        
        Responda:
        """

        response = self.llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=generation_prompt),
            ]
        )

        state["final_answer"] = response.content
        state["workflow_path"].append("answer_generator")

        return state

    def validate_quality(self, state: CVAgentState) -> CVAgentState:
        """Valida a qualidade da resposta"""
        answer = state["final_answer"]
        question = state["current_question"]
        attempts = state.get("answer_attempts", 0)

        validation_prompt = f"""
        Avalie a qualidade desta resposta:
        
        Pergunta: "{question}"
        Resposta: "{answer}"
        
        Critérios de avaliação:
        1. Responde diretamente à pergunta? (sim/não)
        2. Usa informações específicas do CV? (sim/não)
        3. É clara e bem estruturada? (sim/não)
        4. Tem tamanho adequado? (sim/não)
        5. Mantém tom profissional? (sim/não)
        
        Retorne apenas: APROVADO ou REJEITAR_MOTIVO
        """

        response = self.llm.invoke([HumanMessage(content=validation_prompt)])
        validation_result = response.content.strip()

        state["answer_attempts"] = attempts + 1
        state["workflow_path"].append("quality_validator")

        # Limite de tentativas
        if attempts >= 2:
            state["extracted_info"]["validation"] = "APROVADO (limite de tentativas)"
            return state

        if validation_result.startswith("APROVADO"):
            state["extracted_info"]["validation"] = "APROVADO"
        else:
            state["extracted_info"]["validation"] = validation_result

        return state

    def route_after_validation(self, state: CVAgentState) -> str:
        """Roteamento após validação"""
        validation = state["extracted_info"].get("validation", "")
        attempts = state.get("answer_attempts", 0)

        if validation.startswith("APROVADO") or attempts >= 2:
            return "approved"
        elif "REJEITAR" in validation and attempts < 2:
            return "retry"
        else:
            return "reclassify"

    def calculate_confidence(self, state: CVAgentState) -> CVAgentState:
        """Calcula score de confiança da resposta"""
        validation = state["extracted_info"].get("validation", "")
        tools_used = len(state["tools_used"])
        workflow_completeness = len(state["workflow_path"])

        # Cálculo de confiança baseado em múltiplos fatores
        confidence = 0.0

        # Validação (40%)
        if "APROVADO" in validation:
            confidence += 0.4

        # Ferramentas usadas (30%)
        confidence += min(tools_used * 0.1, 0.3)

        # Completude do workflow (20%)
        confidence += min(workflow_completeness * 0.03, 0.2)

        # Tentativas (10% - penalidade por retries)
        attempts = state.get("answer_attempts", 1)
        confidence += max(0.1 - (attempts - 1) * 0.05, 0)

        state["confidence_score"] = min(confidence, 1.0)
        state["workflow_path"].append("confidence_calculator")

        return state

    # === FERRAMENTAS DE EXTRAÇÃO ===

    def extract_experience(self, cv_text: str) -> str:
        """Extrai experiência profissional"""
        prompt = f"""
        Extraia TODAS as experiências profissionais do CV:
        
        CV: {cv_text}
        
        Para cada experiência, extraia:
        - Cargo/Posição
        - Empresa
        - Período (início - fim)
        - Principais responsabilidades
        - Conquistas/resultados
        
        Formato: JSON com lista de experiências
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def extract_skills(self, cv_text: str) -> str:
        """Extrai habilidades técnicas"""
        prompt = f"""
        Extraia TODAS as habilidades técnicas do CV:
        
        CV: {cv_text}
        
        Categorize em:
        - Linguagens de programação
        - Frameworks/Libraries
        - Tecnologias/Ferramentas
        - Banco de dados
        - Cloud/DevOps
        - Outras competências técnicas
        
        Formato: JSON estruturado
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def extract_education(self, cv_text: str) -> str:
        """Extrai formação acadêmica"""
        prompt = f"""
        Extraia TODA a formação acadêmica do CV:
        
        CV: {cv_text}
        
        Extraia:
        - Graduação/Pós-graduação
        - Instituição
        - Período
        - Certificações
        - Cursos relevantes
        
        Formato: JSON estruturado
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def extract_projects(self, cv_text: str) -> str:
        """Extrai projetos"""
        prompt = f"""
        Extraia TODOS os projetos mencionados no CV:
        
        CV: {cv_text}
        
        Para cada projeto:
        - Nome/Descrição
        - Tecnologias utilizadas
        - Resultados/Impacto
        - Contexto (empresa, pessoal, acadêmico)
        
        Formato: JSON estruturado
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def extract_personal_info(self, cv_text: str) -> str:
        """Extrai informações pessoais"""
        prompt = f"""
        Extraia informações pessoais do CV:
        
        CV: {cv_text}
        
        Extraia:
        - Nome completo
        - Título profissional
        - Localização
        - Contatos (email, telefone, LinkedIn)
        - Resumo/Objetivo profissional
        
        Formato: JSON estruturado
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def analyze_career_progression(self, cv_text: str) -> str:
        """Analisa progressão profissional"""
        prompt = f"""
        Analise a progressão profissional no CV:
        
        CV: {cv_text}
        
        Analise:
        - Crescimento de responsabilidades
        - Evolução de cargos
        - Tempo de experiência total
        - Áreas de especialização
        - Tendências de carreira
        
        Formato: Análise estruturada
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    async def process_cv(self, file_content: bytes, filename: str) -> dict:
        """Processa CV e extrai texto"""
        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name

            # Extrair texto do PDF
            with open(tmp_file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

            self.cv_content = text

            # Limpeza
            os.unlink(tmp_file_path)

            return {
                "status": "success",
                "filename": filename,
                "text_length": len(text),
                "pages": len(pdf_reader.pages),
            }

        except Exception as e:
            logger.error(f"Erro no processamento do CV: {e}")
            raise Exception(f"Erro no processamento: {str(e)}")

    async def ask_question(self, question: str) -> dict:
        """Processa pergunta usando o grafo LangGraph"""
        if not self.cv_content:
            raise Exception("CV não foi processado ainda")

        try:
            # Estado inicial
            initial_state = CVAgentState(
                messages=[],
                cv_content=self.cv_content,
                current_question=question,
                question_type="",
                extracted_info={},
                tools_used=[],
                confidence_score=0.0,
                workflow_path=[],
                answer_attempts=0,
                final_answer="",
            )

            # Executar o grafo
            result = await self.app.ainvoke(initial_state)

            return {
                "question": question,
                "answer": result["final_answer"],
                "confidence": result["confidence_score"],
                "workflow_path": result["workflow_path"],
                "tools_used": result["tools_used"],
                "question_type": result["question_type"],
                "attempts": result["answer_attempts"],
                "extracted_info": {
                    k: v
                    for k, v in result["extracted_info"].items()
                    if k not in ["context_analysis"]
                },  # Reduzir payload
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro na consulta: {e}")
            raise Exception(f"Erro na consulta: {str(e)}")

    def get_tools(self) -> dict:
        """Retorna lista de ferramentas disponíveis"""
        return list(self.tools.keys())

    def is_cv_loaded(self) -> bool:
        """Verifica se CV foi carregado"""
        return bool(self.cv_content)

    def get_cv_length(self) -> int:
        """Retorna tamanho do texto do CV"""
        return len(self.cv_content) if self.cv_content else 0

    def is_ready(self) -> bool:
        """Verifica se o agent está pronto"""
        return self.app is not None

    def generate_graph_image(self) -> bytes:
        """Gera imagem PNG do grafo LangGraph"""
        try:
            # Gerar a imagem do grafo
            graph_image = self.app.get_graph().draw_mermaid_png()
            return graph_image
        except Exception as e:
            logger.error(f"Erro ao gerar imagem do grafo: {e}")
            # Retorna uma imagem vazia em caso de erro
            return b''

    def get_graph_mermaid(self) -> str:
        """Retorna o código Mermaid do grafo"""
        try:
            return self.app.get_graph().draw_mermaid()
        except Exception as e:
            logger.error(f"Erro ao gerar código Mermaid: {e}")
            return ""
