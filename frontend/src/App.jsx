import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Settings, Send, Bot, User, Database, RefreshCw, X, FileText, PlusCircle, Trash2, Paperclip, Globe, Clock, Info, ChevronDown, ChevronUp, Activity } from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [libraries, setLibraries] = useState([]);
  const [activeLib, setActiveLib] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  
  // Library creation state
  const [showCreateLib, setShowCreateLib] = useState(false);
  const [newLibName, setNewLibName] = useState('');
  const [isCreatingLib, setIsCreatingLib] = useState(false);
  
  // Settings state
  const [provider, setProvider] = useState('ollama');
  const [modelName, setModelName] = useState('llama3.1');
  const [apiKey, setApiKey] = useState('');
  
  // Dashboard state
  const [showDashboard, setShowDashboard] = useState(false);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchLibraries();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchLibraries = async () => {
    try {
      const res = await axios.get(`${API_URL}/libraries`);
      setLibraries(res.data);
      if (res.data.length > 0) setActiveLib(res.data[0].id);
    } catch (err) {
      console.error("Error fetching libraries:", err);
    }
  };

  const handleUrlIngest = async () => {
    if (!activeLib) return;
    const url = window.prompt("Introduce la URL web que quieres indexar (ej: https://es.wikipedia.org/wiki/...):");
    if (!url || url.trim() === '') return;

    setIsUploading(true);
    try {
      const response = await axios.post(`${API_URL}/libraries/${activeLib}/url`, { url: url.trim() });
      alert(response.data.message || "URL indexada con éxito.");
    } catch (err) {
      alert("Error indexando la URL: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsUploading(false);
    }
  };

  const handleIngest = async () => {
    try {
      await axios.post(`${API_URL}/ingest`);
      alert("Proceso de auto-ingesta iniciado en segundo plano.");
    } catch (err) {
      alert("Error iniciando ingesta.");
    }
  };

  const fetchDashboardData = async () => {
    try {
      const resStats = await axios.get(`${API_URL}/stats`);
      const resLogs = await axios.get(`${API_URL}/logs`);
      setStats(resStats.data);
      setLogs(resLogs.data);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !activeLib) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_URL}/chat`, {
        query: userMsg,
        library_id: activeLib,
        provider: provider,
        model_name: modelName,
        api_key: provider !== 'ollama' ? apiKey : null,
        chat_history: messages.slice(-10) // Enviamos el historial reciente
      });

      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: res.data.result, 
        sources: res.data.sources,
        metrics: res.data.metrics
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: "Error al comunicarse con el backend. Revisa que el servidor FastAPI esté corriendo y tu configuración sea correcta." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApiKeyChange = (e) => {
    const val = e.target.value;
    setApiKey(val);
    if (val.startsWith('gsk_')) {
      setProvider('groq');
      if (['llama3.1', 'gpt-4o-mini', 'gemini-1.5-flash'].includes(modelName)) setModelName('llama-3.1-8b-instant');
    } else if (val.startsWith('sk-')) {
      setProvider('openai');
      if (['llama3.1', 'llama-3.1-8b-instant', 'gemini-1.5-flash'].includes(modelName)) setModelName('gpt-4o-mini');
    } else if (val.startsWith('AIza')) {
      setProvider('gemini');
      if (['llama3.1', 'llama-3.1-8b-instant', 'gpt-4o-mini'].includes(modelName)) setModelName('gemini-1.5-flash');
    }
  };

  const handleCreateLibrary = async (e) => {
    e.preventDefault();
    if (!newLibName.trim()) return;
    setIsCreatingLib(true);
    
    const folderName = newLibName.trim().toLowerCase().replace(/[^a-z0-9]/g, '_');
    try {
      await axios.post(`${API_URL}/libraries`, {
        name: newLibName.trim(),
        folder_name: folderName
      });
      await fetchLibraries();
      setShowCreateLib(false);
      setNewLibName('');
    } catch (err) {
      alert("Error creando el cerebro.");
    } finally {
      setIsCreatingLib(false);
    }
  };

  const handleDeleteLibrary = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("¿Estás seguro de que quieres eliminar este cerebro de tu configuración? Tus PDFs no se borrarán del disco.")) return;
    
    try {
      await axios.delete(`${API_URL}/libraries/${id}`);
      if (activeLib === id) setActiveLib(null);
      await fetchLibraries();
    } catch (err) {
      alert("Error eliminando el cerebro.");
    }
  };

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !activeLib) return;
    
    setIsUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    
    try {
      await axios.post(`${API_URL}/libraries/${activeLib}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      // Iniciar ingesta automáticamente tras subir
      await handleIngest(); 
    } catch (err) {
      alert("Error subiendo archivos.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar glass-panel">
        <div className="logo-area">
          <Bot size={28} color="#60a5fa" />
          <span>DocuMind</span>
        </div>

        <div className="section-title">Cerebros de IA</div>
        <div className="scrollable" style={{ flex: 1 }}>
          {libraries.map(lib => (
            <div 
              key={lib.id} 
              className={`library-btn ${activeLib === lib.id ? 'active' : ''}`}
              onClick={() => setActiveLib(lib.id)}
              style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}
            >
              <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                <Database size={18} />
                <span style={{textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', maxWidth: '120px'}}>{lib.name}</span>
              </div>
              <button 
                onClick={(e) => handleDeleteLibrary(lib.id, e)}
                style={{background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '4px'}}
                title="Eliminar Cerebro"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
          <button 
            className="library-btn" 
            onClick={() => setShowCreateLib(true)} 
            style={{ marginTop: '0.5rem', justifyContent: 'center', border: '1px dashed var(--border-color)', background: 'transparent' }}
          >
            <PlusCircle size={18} />
            Nuevo Cerebro
          </button>
        </div>

        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <button className="library-btn" onClick={handleIngest}>
            <RefreshCw size={18} />
            Forzar Ingesta
          </button>
          <button className="library-btn" onClick={() => { setShowDashboard(true); fetchDashboardData(); }}>
            <Activity size={18} />
            Panel Diagnóstico
          </button>
          <button className="library-btn" onClick={() => setShowSettings(true)}>
            <Settings size={18} />
            Configuración IA
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-area">
        <div className="chat-header">
          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
            {libraries.find(l => l.id === activeLib)?.name || "Cargando..."}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Motor: <span style={{ color: 'var(--accent)' }}>{provider.toUpperCase()}</span> ({modelName})
          </div>
        </div>

        <div className="chat-history scrollable">
          {messages.length === 0 ? (
            <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Bot size={48} style={{ opacity: 0.2, margin: '0 auto 1rem' }} />
              <h3>Bienvenido a DocuMind</h3>
              <p style={{ marginTop: '0.5rem', opacity: 0.7 }}>Selecciona un cerebro y haz una pregunta sobre la documentación local.</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? <User size={20} color="#fff" /> : <Bot size={20} color="#60a5fa" />}
                </div>
                <div className="message-content">
                  <div className="message-bubble">
                    {msg.text}
                  </div>
                  {msg.metrics && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={12} />
                      Total: {msg.metrics.total_time_sec}s | Retrieval: {msg.metrics.retrieval_time_sec}s | Gen: {msg.metrics.generation_time_sec}s | Chunks: {msg.metrics.chunks_retrieved}
                    </div>
                  )}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources-container" style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Fuentes Recuperadas:</div>
                      {msg.sources.map((src, i) => (
                        <div key={i} className="source-card" style={{ background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '6px', fontSize: '0.8rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', color: 'var(--accent)' }}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <FileText size={14} />
                              {src.metadata?.source?.split(/[\\/]/).pop() || "Documento"} (Pág. {src.metadata?.page !== undefined ? src.metadata.page : "?"})
                            </span>
                            <span style={{ color: 'var(--text-secondary)' }}>Score: {src.score?.toFixed(2)}</span>
                          </div>
                          <div style={{ color: 'var(--text-secondary)', fontStyle: 'italic', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                            "{src.content}"
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="message ai">
              <div className="message-avatar">
                <Bot size={20} color="#60a5fa" />
              </div>
              <div className="message-content">
                <div className="message-bubble" style={{ display: 'flex', alignItems: 'center' }}>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container glass-panel">
          <form onSubmit={sendMessage} className="input-box">
            <input 
              type="file" 
              multiple 
              accept=".pdf,.docx,.txt,.md" 
              ref={fileInputRef} 
              style={{display: 'none'}} 
              onChange={handleFileUpload}
            />
            <button 
              type="button" 
              className="send-btn" 
              style={{background: 'transparent', color: 'var(--text-secondary)'}}
              onClick={() => fileInputRef.current?.click()}
              disabled={!activeLib || isLoading || isUploading}
              title="Subir Documentos"
            >
              {isUploading ? <div className="spinner" /> : <Paperclip size={18} />}
            </button>
            <button 
              type="button" 
              className="send-btn" 
              style={{background: 'transparent', color: 'var(--text-secondary)'}}
              onClick={handleUrlIngest}
              disabled={!activeLib || isLoading || isUploading}
              title="Añadir URL"
            >
              <Globe size={18} />
            </button>
            <input 
              type="text" 
              placeholder="Haz una pregunta sobre tus documentos..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading || isUploading}
            />
            <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>
              {isLoading ? <div className="spinner" /> : <Send size={18} />}
            </button>
          </form>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel">
            <div className="modal-header">
              <h2>Configuración del Motor de IA</h2>
              <button className="close-btn" onClick={() => setShowSettings(false)}>
                <X size={24} />
              </button>
            </div>
            
            <div className="form-group">
              <label>Proveedor de IA</label>
              <select value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="ollama">Ollama (Local)</option>
                <option value="openai">OpenAI</option>
                <option value="gemini">Google Gemini</option>
                <option value="groq">Groq</option>
              </select>
            </div>

            <div className="form-group">
              <label>Nombre del Modelo</label>
              <input 
                type="text" 
                value={modelName} 
                onChange={(e) => setModelName(e.target.value)}
                placeholder={provider === 'openai' ? 'gpt-4o-mini' : provider === 'gemini' ? 'gemini-1.5-flash' : provider === 'groq' ? 'llama-3.1-8b-instant' : 'llama3.1'}
              />
            </div>

            {provider !== 'ollama' && (
              <div className="form-group">
                <label>API Key ({provider.toUpperCase()})</label>
                <input 
                  type="password" 
                  value={apiKey} 
                  onChange={handleApiKeyChange}
                  placeholder="Ingresa tu API Key (Autodetecta IA)"
                />
              </div>
            )}

            <button className="btn-primary" onClick={() => setShowSettings(false)}>
              Guardar Configuración
            </button>
          </div>
        </div>
      )}

      {/* Create Library Modal */}
      {showCreateLib && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel">
            <div className="modal-header">
              <h2>Crear Nuevo Cerebro</h2>
              <button className="close-btn" onClick={() => setShowCreateLib(false)}>
                <X size={24} />
              </button>
            </div>
            
            <form onSubmit={handleCreateLibrary}>
              <div className="form-group">
                <label>Nombre del Cerebro</label>
                <input 
                  type="text" 
                  value={newLibName} 
                  onChange={(e) => setNewLibName(e.target.value)}
                  placeholder="Ej: Recursos Humanos, Física..."
                  autoFocus
                />
              </div>

              <button type="submit" className="btn-primary" disabled={isCreatingLib || !newLibName.trim()}>
                {isCreatingLib ? 'Creando...' : 'Crear Cerebro'}
              </button>
            </form>
          </div>
        </div>
      )}
      {/* Dashboard Modal */}
      {showDashboard && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel" style={{ maxWidth: '800px', width: '90%' }}>
            <div className="modal-header">
              <h2>Panel de Diagnóstico (RAG)</h2>
              <button className="close-btn" onClick={() => setShowDashboard(false)}>
                <X size={24} />
              </button>
            </div>
            
            {stats && (
              <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                <div className="stat-card" style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>{stats.total_queries}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Consultas</div>
                </div>
                <div className="stat-card" style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>{stats.avg_total_time}s</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Tiempo Medio Total</div>
                </div>
                <div className="stat-card" style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>{stats.avg_retrieval_time}s</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Retrieval Medio</div>
                </div>
                <div className="stat-card" style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>{stats.avg_generation_time}s</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Generación Media</div>
                </div>
              </div>
            )}

            <h3 style={{ marginBottom: '1rem' }}>Últimas Consultas</h3>
            <div className="scrollable" style={{ maxHeight: '400px', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                    <th style={{ padding: '8px' }}>Fecha</th>
                    <th style={{ padding: '8px' }}>Pregunta</th>
                    <th style={{ padding: '8px' }}>Tiempo</th>
                    <th style={{ padding: '8px' }}>Chunks</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '8px', color: 'var(--text-secondary)' }}>
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </td>
                      <td style={{ padding: '8px', maxWidth: '300px', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                        {log.query}
                      </td>
                      <td style={{ padding: '8px', color: 'var(--accent)' }}>
                        {log.metrics?.total_time_sec}s
                      </td>
                      <td style={{ padding: '8px' }}>
                        {log.metrics?.chunks_retrieved}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {logs.length === 0 && <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>No hay logs registrados aún.</div>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
