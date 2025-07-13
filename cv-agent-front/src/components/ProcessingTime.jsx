import React from 'react';

const ProcessingTime = ({ time }) => {
  const seconds = (time / 1000).toFixed(2);
  
  const getSpeedText = () => {
    if (time < 2000) return "Muito Rápido";
    if (time < 5000) return "Rápido";
    return "Processamento Complexo";
  };

  return (
    <div className="processing-time">
      ⏱️ {seconds}s ({getSpeedText()})
    </div>
  );
};

export default ProcessingTime;