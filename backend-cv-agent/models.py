from typing import TypedDict, List, Annotated, Dict, Any
import operator
from langchain.schema import BaseMessage


class CVAgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    cv_content: str
    current_question: str
    question_type: str
    extracted_info: Dict[str, Any]
    tools_used: List[str]
    confidence_score: float
    workflow_path: List[str]
    answer_attempts: int
    final_answer: str
