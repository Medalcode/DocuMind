import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Settings, Send, Bot, User, Database, RefreshCw, X, FileText, PlusCircle, Trash2, Paperclip } from 'lucide-react';
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

  const handleIngest = async () => {
    try {
      await axios.post(`${API_URL}/ingest`);
      alert("Proceso de auto-ingesta iniciado en segundo plano.");
    } catch (err) {
      alert("Error iniciando ingesta.");
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
        api_key: provider !== 'ollama' ? apiKey : null
      });

      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: res.data.result, 
        sources: res.data.sources 
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
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      {msg.sources.map((src, i) => (
                        <span key={i} className="source-badge">
                          <FileText size={12} />
                          Pág: {src}
                        </span>
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
              accept=".pdf" 
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
              title="Subir PDFs"
            >
              {isUploading ? <div className="spinner" /> : <Paperclip size={18} />}
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
    </div>
  );
}

export default App;
