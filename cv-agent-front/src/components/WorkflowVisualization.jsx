import React from 'react';

const WorkflowVisualization = ({ workflowPath, questionType }) => {
  const allNodes = [
    {
      id: "classifier",
      label: "🏷️ Classificador",
      desc: "Analisa tipo de pergunta",
    },
    {
      id: "tool_selector",
      label: "🔧 Seletor de Ferramentas",
      desc: "Escolhe ferramentas apropriadas",
    },
    {
      id: "information_extractor",
      label: "📊 Extrator",
      desc: "Extrai informações específicas",
    },
    {
      id: "context_analyzer",
      label: "🧠 Analisador",
      desc: "Analisa contexto relevante",
    },
    {
      id: "answer_generator",
      label: "✍️ Gerador",
      desc: "Gera resposta especializada",
    },
    {
      id: "quality_validator",
      label: "✅ Validador",
      desc: "Valida qualidade da resposta",
    },
    {
      id: "confidence_calculator",
      label: "📈 Calculador",
      desc: "Calcula score de confiança",
    },
  ];

  return (
    <div className="workflow-visualization">
      <div className="workflow-header">
        <h3>🔄 Workflow LangGraph</h3>
        <div className="question-type-badge">
          Tipo: <span className="type-label">{questionType}</span>
        </div>
      </div>

      <div className="workflow-nodes">
        {allNodes.map((node, index) => {
          const isActive = workflowPath.includes(node.id);
          const isCompleted =
            workflowPath.indexOf(node.id) < workflowPath.length - 1;
          const isCurrent = workflowPath[workflowPath.length - 1] === node.id;

          return (
            <div
              key={node.id}
              className={`workflow-node ${isActive ? "active" : ""} ${
                isCompleted ? "completed" : ""
              } ${isCurrent ? "current" : ""}`}
            >
              <div className="node-header">
                <span className="node-label">{node.label}</span>
                {isCompleted && <span className="completion-check">✓</span>}
                {isCurrent && <span className="current-indicator">→</span>}
              </div>
              <div className="node-description">{node.desc}</div>
              {index < allNodes.length - 1 && (
                <div className={`node-arrow ${isActive ? "active" : ""}`}>
                  ↓
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WorkflowVisualization;