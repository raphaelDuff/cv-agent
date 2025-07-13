import React, { useState, useEffect } from "react";
import axios from "axios";
import WorkflowVisualization from "./components/WorkflowVisualization";
import ToolsUsed from "./components/ToolsUsed";
import ConfidenceIndicator from "./components/ConfidenceIndicator";
import ProcessingTime from "./components/ProcessingTime";
import FormattedResponse from "./components/FormattedResponse";
import GraphVisualization from "./components/GraphVisualization";
import { config, API_ENDPOINTS } from "./config";
import "./styles/CVAgent.css";

const CVAgent = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [examples, setExamples] = useState({});
  const [selectedCategory, setSelectedCategory] = useState("experience");
  const [graphInfo, setGraphInfo] = useState(null);

  useEffect(() => {
    // Carregar informações do grafo e exemplos
    Promise.all([
      axios.get(API_ENDPOINTS.graphInfo),
      axios.get(API_ENDPOINTS.examples),
    ])
      .then(([graphRes, examplesRes]) => {
        setGraphInfo(graphRes.data);
        setExamples(examplesRes.data);
      })
      .catch((error) => {
        console.error("Erro ao carregar dados iniciais:", error);
      });
  }, []);

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(API_ENDPOINTS.upload, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploaded(true);
      setFile(selectedFile);
      console.log("CV processado:", response.data);
    } catch (error) {
      alert("Erro no upload: " + error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;

    setAsking(true);
    const startTime = Date.now();

    try {
      const response = await axios.post(API_ENDPOINTS.ask, null, {
        params: { question },
      });

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      const newChat = {
        ...response.data,
        processing_time: processingTime,
        id: Date.now(),
      };

      setChatHistory([...chatHistory, newChat]);
      setQuestion("");
    } catch (error) {
      alert("Erro na consulta: " + error.message);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="cv-agent">
      <header className="agent-header">
        <h1>🤖 {config.appTitle}</h1>
        <p>
          Powered by <strong>Raphael Prates</strong> + OpenAI + LangGraph +
          Claude Code
        </p>
        {config.isDev && (
          <small style={{ opacity: 0.8 }}>
            v{config.appVersion} - {config.mode} mode
          </small>
        )}
        <div className="tech-badges">
          <span className="tech-badge">🔗 LangGraph</span>
          <span className="tech-badge">🤖 GPT-4</span>
          <span className="tech-badge">⚡ Async</span>
          <span className="tech-badge">☁️ Cloud Ready</span>
        </div>
      </header>

      {/* Upload Section */}
      <div className="upload-section">
        <div className="upload-card">
          <div className="upload-icon">📄</div>
          <h2>Upload do Currículo</h2>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            className="file-input"
            id="cv-upload"
          />
          <label
            htmlFor="cv-upload"
            className={`upload-button ${uploading ? "uploading" : ""}`}
          >
            {uploading ? (
              <>
                <div className="spinner"></div>
                Processando com LangGraph...
              </>
            ) : (
              "Escolher Arquivo PDF"
            )}
          </label>

          {uploaded && (
            <div className="upload-success">
              <div className="success-icon">✅</div>
              <div className="success-text">
                <strong>CV Processado com Sucesso!</strong>
                <br />
                <small>Arquivo: {file?.name}</small>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Agent Info */}
      {graphInfo && (
        <div className="agent-info">
          <h3>🧠 Arquitetura do Agent</h3>
          <div className="info-grid">
            <div className="info-card">
              <h4>📊 Nodes do Grafo</h4>
              <div className="node-count">{graphInfo.nodes.length}</div>
              <small>Etapas de processamento</small>
            </div>
            <div className="info-card">
              <h4>🔧 Ferramentas</h4>
              <div className="tool-count">{graphInfo.tools.length}</div>
              <small>Ferramentas especializadas</small>
            </div>
            <div className="info-card">
              <h4>🔄 Workflows</h4>
              <div className="workflow-count">
                {graphInfo.workflow_types.length}
              </div>
              <small>Tipos de fluxo</small>
            </div>
          </div>
        </div>
      )}

      {/* Graph Visualization */}
      <GraphVisualization apiBase={config.apiBaseUrl} />

      {uploaded && (
        <>
          {/* Question Categories */}
          <div className="question-categories">
            <h3>💡 Perguntas por Categoria</h3>
            <div className="category-tabs">
              {Object.keys(examples).map((category) => (
                <button
                  key={category}
                  className={`category-tab ${
                    selectedCategory === category ? "active" : ""
                  }`}
                  onClick={() => setSelectedCategory(category)}
                >
                  {category === "experience" && "💼"}
                  {category === "skills" && "🛠️"}
                  {category === "education" && "🎓"}
                  {category === "projects" && "🚀"}
                  {category === "career" && "📈"}
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>

            <div className="example-questions">
              {examples[selectedCategory]?.map((q, i) => (
                <button
                  key={i}
                  onClick={() => setQuestion(q)}
                  className="example-question"
                  disabled={asking}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Interface */}
          <div className="chat-interface">
            <h3>💬 Conversa com o Agent</h3>

            <div className="question-input-section">
              <div className="input-group">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Digite sua pergunta sobre o CV..."
                  disabled={asking}
                  onKeyPress={(e) => e.key === "Enter" && handleAsk()}
                  className="question-input"
                />
                <button
                  onClick={handleAsk}
                  disabled={asking || !question.trim()}
                  className="ask-button"
                >
                  {asking ? (
                    <>
                      <div className="spinner small"></div>
                      Processando...
                    </>
                  ) : (
                    "🔍 Perguntar"
                  )}
                </button>
              </div>
            </div>

            {/* Latest Response - Always at Top */}
            {chatHistory.length > 0 && (
              <div className="latest-response">
                <h3>🤖 Última Resposta</h3>
                <div className="latest-response-content">
                  {(() => {
                    const latestChat = chatHistory[chatHistory.length - 1];
                    return (
                      <div className="chat-item">
                        <div className="question-section">
                          <div className="question-header">
                            <h4>❓ Pergunta</h4>
                            <div className="question-meta">
                              <ProcessingTime
                                time={latestChat.processing_time}
                              />
                              <span className="timestamp">
                                {new Date(
                                  latestChat.timestamp
                                ).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                          <div className="question-text">
                            {latestChat.question}
                          </div>
                        </div>

                        <div className="response-section">
                          <div className="response-header">
                            <h4>🤖 Resposta do Agent</h4>
                            <ConfidenceIndicator
                              confidence={latestChat.confidence}
                              attempts={latestChat.attempts}
                            />
                          </div>

                          <FormattedResponse text={latestChat.answer} />

                          {/* Workflow Visualization */}
                          <WorkflowVisualization
                            workflowPath={latestChat.workflow_path}
                            questionType={latestChat.question_type}
                          />

                          {/* Tools Used */}
                          {latestChat.tools_used &&
                            latestChat.tools_used.length > 0 && (
                              <ToolsUsed tools={latestChat.tools_used} />
                            )}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
            )}

            {/* Chat History */}
            <div className="chat-history">
              <h3>📝 Histórico de Conversas</h3>
              {chatHistory
                .slice(0, -1)
                .reverse()
                .map((chat) => (
                  <div key={chat.id} className="chat-item">
                    <div className="question-section">
                      <div className="question-header">
                        <h4>❓ Pergunta</h4>
                        <div className="question-meta">
                          <ProcessingTime time={chat.processing_time} />
                          <span className="timestamp">
                            {new Date(chat.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                      <div className="question-text">{chat.question}</div>
                    </div>

                    <div className="response-section">
                      <div className="response-header">
                        <h4>🤖 Resposta do Agent</h4>
                        <ConfidenceIndicator
                          confidence={chat.confidence}
                          attempts={chat.attempts}
                        />
                      </div>

                      <FormattedResponse text={chat.answer} />

                      {/* Workflow Visualization */}
                      <WorkflowVisualization
                        workflowPath={chat.workflow_path}
                        questionType={chat.question_type}
                      />

                      {/* Tools Used */}
                      {chat.tools_used && chat.tools_used.length > 0 && (
                        <ToolsUsed tools={chat.tools_used} />
                      )}

                      {/* Technical Details */}
                      <details className="technical-details">
                        <summary>🔍 Detalhes Técnicos</summary>
                        <div className="details-content">
                          <div className="detail-item">
                            <strong>Tipo de Pergunta:</strong>{" "}
                            {chat.question_type}
                          </div>
                          <div className="detail-item">
                            <strong>Caminho do Workflow:</strong>{" "}
                            {chat.workflow_path.join(" → ")}
                          </div>
                          <div className="detail-item">
                            <strong>Ferramentas:</strong>{" "}
                            {chat.tools_used.join(", ")}
                          </div>
                          <div className="detail-item">
                            <strong>Tentativas:</strong> {chat.attempts}
                          </div>
                          <div className="detail-item">
                            <strong>Score de Confiança:</strong>{" "}
                            {(chat.confidence * 100).toFixed(1)}%
                          </div>
                        </div>
                      </details>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CVAgent;
