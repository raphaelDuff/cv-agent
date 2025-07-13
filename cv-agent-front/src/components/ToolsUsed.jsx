import React from 'react';

const ToolsUsed = ({ tools }) => {
  const toolDescriptions = {
    extract_experience: { icon: "💼", desc: "Experiência Profissional" },
    extract_skills: { icon: "🛠️", desc: "Habilidades Técnicas" },
    extract_education: { icon: "🎓", desc: "Formação Acadêmica" },
    extract_projects: { icon: "🚀", desc: "Projetos" },
    extract_personal_info: { icon: "👤", desc: "Info Pessoal" },
    analyze_career_progression: {
      icon: "📈",
      desc: "Progressão Profissional",
    },
  };

  return (
    <div className="tools-used">
      <h4>🔧 Ferramentas Utilizadas</h4>
      <div className="tools-grid">
        {tools.map((tool) => {
          const toolInfo = toolDescriptions[tool] || {
            icon: "🔧",
            desc: tool,
          };
          return (
            <div key={tool} className="tool-badge">
              <span className="tool-icon">{toolInfo.icon}</span>
              <span className="tool-name">{toolInfo.desc}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ToolsUsed;