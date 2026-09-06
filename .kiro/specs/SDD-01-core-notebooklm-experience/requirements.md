# SDD-01 — Core NotebookLM Experience

## 1. Product Definition & Vision

**DocuMind** is a local document-intelligence application that allows a user to create a knowledge library from their own documents and interact with that knowledge using AI, prioritizing privacy, local processing, grounded answers, and source visibility.

**Primary Value Proposition:**
> "Bring your documents to your own machine and talk to them using your own/local AI."

The application centers conceptually around local AI (via Ollama). Cloud providers remain optional alternatives that must not redefine the product's private, local-first identity.

### 1.1 Product Priority Order
1. Core NotebookLM-like experience
2. Local/private AI experience
3. RAG quality and grounding
4. Source/citation transparency
5. User experience
6. Reliability
7. Performance
8. Security appropriate to a local application
9. Extensibility
10. Enterprise scalability

### 1.2 Non-Goals for SDD-01
- Enterprise authentication (OAuth/JWT)
- Multi-user architecture / enterprise multi-tenancy
- Kubernetes, microservices, distributed deployment
- Cloud-first architecture
- Enterprise observability (Prometheus/Grafana)
- Billing / SaaS infrastructure
- Advanced permissions / complex document versioning
- Advanced analytics, audio generation, multimodal features, or mobile apps
- Large-scale distributed vector databases

---

## 2. Requirements

### 2.1 Knowledge Library

#### REQ-1.1: Library Creation and Isolation
- **User story / intent**: As a user, I want to create a distinct library for a specific topic or project so that my questions are only answered using those specific documents without cross-contamination.
- **Acceptance criteria**: 
  - User can create a new library by name.
  - Documents uploaded to Library A are entirely invisible to queries made in Library B.
  - The UI clearly displays which library is currently active.
- **Functional behavior**: The system separates vector indices and raw documents into isolated physical or logical buckets per library.
- **Relevant existing implementation**: Partially implemented. `DocuMindEngine.add_library()` creates isolated `data/` and `db/` folders per library. `config.yaml` tracks them.
- **Dependencies**: Existing FastAPI `/libraries` endpoints.
- **Validation approach**: Integration test verifying a query in Library A does not return a document ingested only in Library B.

---

### 2.2 Document Ingestion

#### REQ-2.1: Local Document Upload & Processing
- **User story / intent**: As a user, I want to upload my PDF, DOCX, TXT, and Markdown files so that the AI can read them.
- **Acceptance criteria**:
  - The system accepts supported file formats.
  - The user sees visual feedback during upload and processing (chunking/embedding).
  - The system successfully indexes the documents into the active library.
  - Failed documents display an error without crashing the entire ingestion process.
- **Functional behavior**: Files are saved to the library's `data/` folder. A background task reads, chunks, embeds, and stores them in ChromaDB. 
- **Relevant existing implementation**: Implemented. `/libraries/{lib_id}/upload` and `/ingest` trigger `engine.auto_ingesta()`.
- **Dependencies**: LangChain document loaders, HuggingFace embeddings, ChromaDB.
- **Validation approach**: E2E test uploading a sample PDF and asserting that the `indexed_files.json` updates and the UI shows a "Ready" state.

---

### 2.3 Retrieval-Augmented Conversation

#### REQ-3.1: Grounded Q&A
- **User story / intent**: As a user, I want to ask questions and receive answers based *only* on the documents in my active library.
- **Acceptance criteria**:
  - If the library contains the answer, the LLM provides it.
  - If the library does not contain the answer, the LLM clearly states that it does not know or the context is insufficient, rather than hallucinating.
- **Functional behavior**: The query is embedded, relevant chunks are retrieved via vector search, and a strict prompt instructs the LLM to rely solely on the context.
- **Relevant existing implementation**: Implemented. `CustomQAChain.invoke()` uses a prompt explicitly instructing the LLM: "Si no sabes la respuesta, di claramente que no la sabes, no inventes información."
- **Dependencies**: ChromaDB retriever, LLM provider.
- **Validation approach**: Integration test asking a question entirely unrelated to the library content and verifying the model declines to answer.

---

### 2.4 Source / Citation Experience

#### REQ-4.1: Transparent Source Visibility
- **User story / intent**: As a user, I want to see exactly which documents and pages the AI used to generate its answer, so I can trust the information and verify it myself.
- **Acceptance criteria**:
  - Every answer derived from the library must expose the list of source files used.
  - Where available, the specific page number or section must be visible.
  - The UI must render these sources alongside or below the chat bubble.
- **Functional behavior**: The backend returns the `detailed_sources` array containing filename, score, and page metadata for every chunk passed to the LLM. The frontend parses and displays this array.
- **Relevant existing implementation**: Partially implemented. Backend returns `detailed_sources` in the `/chat` JSON response. UI needs to properly expose this to the user.
- **Dependencies**: LangChain document loaders (for metadata extraction).
- **Validation approach**: E2E test verifying that a successful answer UI component contains clickable or visible source pills mapping to the uploaded document.

---

### 2.5 Local AI (Ollama)

#### REQ-5.1: First-Class Local AI Support
- **User story / intent**: As a user, I want to run inference entirely on my local machine using Ollama, guaranteeing absolute privacy.
- **Acceptance criteria**:
  - "Ollama" is the default or prominently featured provider.
  - If Ollama is not running, the system gracefully catches the connection error and prompts the user to start Ollama.
- **Functional behavior**: The backend attempts to connect to the local Ollama instance (e.g., `http://localhost:11434`). Timeouts or connection refused errors are caught and translated into actionable UI error messages.
- **Relevant existing implementation**: Partially implemented. `ChatOllama` is supported, but explicit error handling for "Ollama not running" might be weak.
- **Dependencies**: Local Ollama installation, LangChain `ChatOllama`.
- **Validation approach**: Manual/Integration test attempting a chat query with the Ollama service stopped, verifying the API returns a standard 503/Bad Gateway or similar, and UI shows a helpful message.

---

### 2.6 Conversation Experience

#### REQ-6.1: Contextual Chat History
- **User story / intent**: As a user, I want to ask follow-up questions in a conversation thread without repeating myself.
- **Acceptance criteria**:
  - The UI maintains a visual chat history for the current session.
  - Previous questions and answers are sent to the backend as context.
  - The user can clear the chat to start a new conversation.
- **Functional behavior**: The frontend maintains an array of messages and sends `chat_history` in the `/chat` payload. The backend injects this into the LLM prompt.
- **Relevant existing implementation**: Implemented. `ChatRequest` accepts `chat_history` and `CustomQAChain` formats it into the prompt.
- **Dependencies**: Frontend state management.
- **Validation approach**: E2E test asking "What is X?", followed by "Tell me more about it", verifying the LLM understands "it" refers to X.

---

### 2.7 Minimum UX States

#### REQ-7.1: UI State Representation
- **User story / intent**: As a user, I need to always know what the system is doing, especially during slow operations like embedding or local LLM generation.
- **Acceptance criteria**: The frontend MUST visually represent the following states:
  - **Empty Library**: Clear call to action to upload documents.
  - **Uploading/Processing**: Visual indicator that documents are being indexed (spinner/progress).
  - **Ready**: Indication that the library is active and ready for queries.
  - **Generating Answer**: A loading state (skeleton or spinner) while waiting for the local LLM to respond.
  - **Answer with Sources**: The chat bubble containing the markdown response and source chips.
  - **Error States**: Clear banners/toasts for "Ingestion Failure", "Model Unavailable" (Ollama down), and "Generation Failure".
- **Functional behavior**: Frontend maps API HTTP statuses and background polling/promises to UI components.
- **Relevant existing implementation**: Missing/Needs review in frontend implementation.
- **Dependencies**: React component states.
- **Validation approach**: E2E UI tests or visual QA verifying the presence of loading indicators and error toasts.

---

## 3. Testing Requirements

Validation for SDD-01 prioritizes the critical user journey.

1. **Unit Tests**: Deterministic logic (e.g., config loading, `CustomQAChain` prompt construction).
2. **Integration Tests**: Boundary tests between FastAPI endpoints and the RAG engine (e.g., uploading a file creates the ChromaDB index; missing Ollama returns proper error).
3. **E2E Validation (The Main Scenario)**:
   - **Step 1**: CREATE/OPEN LIBRARY
   - **Step 2**: ADD DOCUMENT
   - **Step 3**: DOCUMENT PROCESSED (verify UI ready state)
   - **Step 4**: ASK QUESTION
   - **Step 5**: RECEIVE GROUNDED ANSWER
   - **Step 6**: VIEW SOURCE (verify citation metadata matches the uploaded document)

---

## 4. Definition of Done (DoD) for SDD-01

This specification is complete when:
- The core NotebookLM user journey is explicitly defined.
- Existing capabilities have been mapped, and missing ones (like strict UX error handling for Ollama) are identified.
- Requirements are testable without requiring heavy enterprise testing frameworks.
- Local AI is treated as a primary, first-class capability.
- Source grounding/citations are strictly required for the output UX.
- Library isolation is preserved.
- Non-goals strictly prevent enterprise scope creep (no k8s, no OAuth).
- The specification is aligned with the SDD-00 baseline.
- **No implementation code has been modified during the definition of this spec.**
