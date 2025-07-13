import React, { useState, useEffect } from 'react';
import { handleError, devLog } from '../utils/vite';

const GraphVisualization = ({ apiBase }) => {
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showGraph, setShowGraph] = useState(false);

  const loadGraphImage = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Gerar nova URL com timestamp para evitar cache
      const timestamp = new Date().getTime();
      const url = `${apiBase}/graph-image?t=${timestamp}`;
      setImageUrl(url);
      devLog('Graph image URL generated:', url);
    } catch (err) {
      setError('Erro ao carregar imagem do grafo');
      handleError(err, 'GraphVisualization.loadGraphImage');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (showGraph && !imageUrl) {
      loadGraphImage();
    }
  }, [showGraph]);

  const toggleGraph = () => {
    setShowGraph(!showGraph);
    if (!showGraph && !imageUrl) {
      loadGraphImage();
    }
  };

  return (
    <div className="graph-visualization">
      <div className="graph-header">
        <h3>📊 Visualização do Grafo LangGraph</h3>
        <button 
          className="toggle-graph-btn"
          onClick={toggleGraph}
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="spinner small"></div>
              Carregando...
            </>
          ) : (
            showGraph ? '🙈 Ocultar Grafo' : '👁️ Mostrar Grafo'
          )}
        </button>
      </div>

      {showGraph && (
        <div className="graph-content">
          {error ? (
            <div className="graph-error">
              <p>❌ {error}</p>
              <button onClick={loadGraphImage} className="retry-btn">
                🔄 Tentar Novamente
              </button>
            </div>
          ) : imageUrl ? (
            <div className="graph-image-container">
              <img 
                src={imageUrl} 
                alt="LangGraph Workflow Diagram"
                className="graph-image"
                onError={() => setError('Erro ao carregar a imagem')}
              />
              <div className="graph-actions">
                <button 
                  onClick={loadGraphImage}
                  className="refresh-btn"
                  disabled={loading}
                >
                  🔄 Atualizar
                </button>
                <a 
                  href={imageUrl}
                  download="langgraph-workflow.png"
                  className="download-btn"
                >
                  💾 Download
                </a>
              </div>
            </div>
          ) : (
            <div className="graph-loading">
              <div className="spinner"></div>
              <p>Gerando visualização do grafo...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GraphVisualization;