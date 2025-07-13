import React from 'react';

const ConfidenceIndicator = ({ confidence, attempts }) => {
  const percentage = Math.round(confidence * 100);
  
  const getColor = () => {
    if (percentage >= 80) return "#4CAF50";
    if (percentage >= 60) return "#FF9800";
    return "#f44336";
  };

  const getQualityText = () => {
    if (percentage >= 80) return "Alta Qualidade";
    if (percentage >= 60) return "Boa Qualidade";
    return "Qualidade Moderada";
  };

  return (
    <div className="confidence-indicator">
      <div className="confidence-header">
        <span className="confidence-label">
          📊 Confiança: {percentage}% ({getQualityText()})
        </span>
        {attempts > 1 && (
          <span className="attempts-badge">🔄 {attempts} tentativas</span>
        )}
      </div>
      <div className="confidence-bar">
        <div
          className="confidence-fill"
          style={{
            width: `${percentage}%`,
            backgroundColor: getColor(),
            transition: "width 0.5s ease-in-out",
          }}
        />
      </div>
    </div>
  );
};

export default ConfidenceIndicator;