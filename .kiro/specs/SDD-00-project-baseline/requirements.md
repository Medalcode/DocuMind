# SDD-00: Project Baseline & Architecture Foundation

## 1. Document Purpose
This document establishes the official architectural and functional baseline for DocuMind based on Spec-Driven Development (SDD) principles. Its purpose is to objectively describe what the system currently is, how it is structured, what its limits are, and the principles that must govern its future evolution. 

This document does not aim to solve technical problems, fix bugs, or define a detailed roadmap. It serves solely as a verifiable, maintainable, and professional representation of the current state of DocuMind, ensuring that all future Specs share a common ground truth.

---

## 2. Product Definition
DocuMind is a Retrieval-Augmented Generation (RAG) application designed to allow users to ingest, index, and query information from documents and web URLs.

- **Problem solved**: It bridges the gap between static documents/web pages and conversational AI by allowing users to ask natural language questions grounded in their own provided context.
- **Target audience**: Individual users or developers seeking a local-first, lightweight RAG tool for personal knowledge management, document analysis, and research.
- **Value proposition**: Provides an isolated, privacy-respecting (local-first design), and modular way to create specialized knowledge bases (Libraries/Cerebros) that can be queried using various Large Language Models (LLMs).
- **Current capabilities**: Ingests files (PDF, DOCX, TXT, MD) and URLs, indexes them into a vector store, and provides a chat interface to query the indexed data.
- **What it does NOT currently intend to do**: It does not intend to be an enterprise-scale document management system, a multi-tenant SaaS application, or a highly distributed cloud-native architecture.

---

## 3. Current Scope
The following functionalities are verified as currently present in the system:

- **Document Upload**: Support for parsing and ingesting PDF, DOCX, TXT, and Markdown files.
- **URL Ingestion**: Capability to fetch and process content from web URLs.
- **Document Indexing**: Chunking and embedding of ingested text into a vector store.
- **Multiple Libraries (Cerebros)**: Logical separation of documents and vectors into distinct knowledge bases.
- **RAG Chat**: Conversational interface augmented with context retrieved from the selected library.
- **Multiple LLM Providers**: Support for switching between different underlying LLM backends for generation.
- **Chat History**: Persistence and retrieval of past chat interactions.
- **Metrics & Logging**: Basic tracking of operation timings and application logs.
- **Dashboard/Benchmarking**: Interface for viewing basic system metrics or performance data.
- **Skills**: Modular extensions or specific capabilities integrated into the pipeline.
- **Containerization**: Docker support for simplified deployment.
- **CLI / Legacy Functionality**: Command-line interfaces for specific backend tasks.
- **Continuous Integration**: GitHub Actions configured for automated workflows.

---

## 4. System Context
The high-level flow of the application is:
`User` -> `React Frontend` -> `FastAPI API` -> `DocuMindEngine` -> `RAG Pipeline` -> `Vector Store / Embeddings / LLM Provider`

- **Internal Components**: 
  - `Frontend`: React-based web interface.
  - `API`: FastAPI HTTP presentation layer.
  - `Engine`: Core orchestration logic bridging the API and the RAG pipeline.
- **External Dependencies**: 
  - Underlying OS filesystem.
  - External LLM APIs (when not using local models).
- **User-Controlled Inputs**: 
  - Document uploads, URL strings, chat queries, library creation requests.
- **Persisted Data**: 
  - Vector embeddings, indexed file metadata, chat history logs, system configuration.
- **External Services**: 
  - Selected LLM providers (e.g., OpenAI, Anthropic, etc. depending on configuration).

---

## 5. Architecture

### Frontend
- **Responsibilities**: Render the user interface, handle user interactions, manage local UI state, and communicate with the backend API via HTTP requests. Does not contain business logic or RAG operations.

### Backend/API
- **Responsibilities**: Define HTTP endpoints, validate incoming requests/payloads (Pydantic), handle authentication/CORS boundaries, and map HTTP requests to Engine function calls.

### Engine (DocuMindEngine)
- **Responsibilities**: Act as the central orchestrator. It receives validated requests from the API, coordinates document loading, interacts with the RAG pipeline, and manages the logical boundaries of Libraries/Cerebros.

### RAG Pipeline
- **Responsibilities**: Execute the core AI workflow: Document Loading -> Text Splitting (Chunking) -> Embedding Generation -> Vector Storage -> Retrieval -> Prompt Formatting -> LLM Generation.

### Persistence
- **Responsibilities**: Safely store and retrieve application data. This includes the vector store representations, JSON-based file metadata, chat histories, and configuration files.

### Skills
- **Responsibilities**: Provide isolated, specialized functionality that can be invoked during the RAG process or via distinct endpoints without polluting the core engine logic.

---

## 6. Architectural Boundaries
- **UI Agnosticism**: The Frontend must not contain RAG orchestration logic or direct database connection strings.
- **API Isolation**: The API layer must not access the vector store or file system directly; all operations must pass through the Engine.
- **Engine Centralization**: The Engine encapsulates the orchestration of the RAG pipeline, shielding the API from the complexities of LangChain or ChromaDB.
- **Persistence Encapsulation**: Data storage mechanisms (vector db, JSON files) must remain isolated from the presentation layer.

*(These are principles of separation, not mere descriptions of file names).*

---

## 7. Architectural Principles

### 7.1 Separation of Concerns
Frontend, API, and RAG Engine have strictly differentiated responsibilities. Changes in the UI should not force changes in the RAG logic, and vice versa.

### 7.2 Persistence Isolation
Access to the vector store and metadata files is encapsulated. The HTTP/presentation layer operates on abstractions, not direct data layer access.

### 7.3 Library Isolation
Each library represents an isolated knowledge space. Queries and indexing operations must not bleed context across different libraries.

### 7.4 Observability
Relevant RAG operations (retrieval, generation) must produce sufficient telemetry (logs/timings) to measure and understand their behavior.

### 7.5 Evolution Without Unnecessary Coupling
The architecture must allow the internal swapping of components (e.g., changing the vector database or the LLM provider) without propagating unnecessary dependencies across layers.

### 7.6 Local-First
DocuMind is designed for local operation. It does not require cloud infrastructure (like Kubernetes, managed databases, or cloud storage) for its core functionality.

*(Note: Specific technologies like ChromaDB, LangChain, React 19, or specific chunk sizes are part of the current state, not permanent architectural principles).*

---

## 8. Current Technology Baseline
*(These are the current technologies in use, subject to change via future Specs if justified, and are not immutable rules).*

- **Frontend**: React, Vite, Axios.
- **Backend**: Python, FastAPI, Pydantic.
- **RAG Orchestration**: LangChain.
- **Vector Database**: ChromaDB.
- **Embeddings**: HuggingFace embeddings.
- **LLM**: Various currently configured LLM providers.
- **Testing**: pytest.
- **CI**: GitHub Actions.
- **Containerization**: Docker.

---

## 9. RAG Baseline
Current pipeline flow:
`Document Loading` -> `Chunking` -> `Embeddings` -> `Vector Store` -> `Retrieval` -> `Prompt` -> `LLM` -> `Response` -> `Metrics / Logging`

**CURRENT IMPLEMENTATION VALUES:**
*(These parameters represent the current state and are expected to evolve through future optimization Specs)*
- **Chunk Size**: Current configured chunk size.
- **Chunk Overlap**: Current configured chunk overlap.
- **Retrieval 'k'**: Current number of retrieved documents per query.
- **Embedding Model**: Current configured HuggingFace model (e.g., all-MiniLM-L6-v2).

---

## 10. Data & Persistence Baseline
- **Library Configuration**: Logical separation structures.
- **Vector Persistence**: Handled via ChromaDB local persistence mechanisms.
- **Metadata**: `indexed_files.json` for tracking ingested documents.
- **Chat Logs**: `chat_logs.jsonl` for conversational history.
- **Configuration**: Existing configuration files mapping environments and system defaults.
*Note: No active database migrations or strict versioning mechanisms are currently enforced.*

---

## 11. Security Baseline
The system is currently designed around local-usage assumptions. 
- **API Keys**: Managed via environment variables or local configuration.
- **Upload Inputs**: File uploads are processed locally.
- **URL Ingestion**: Constitutes an external entry surface that requires destination validation before being considered suitable for environments less trusted than local, single-user operation.
- **CORS**: Configured for current frontend-backend communication.
- **Authentication**: Operates without enterprise-grade authentication structures.

*(Enterprise features like mandatory JWT, OAuth, rate limiting, key rotation, or encryption at rest are currently outside the baseline scope).*

---

## 12. Testing Baseline
- **Framework**: pytest.
- **Current Coverage**: Covers specific unit tests and basic integration paths.
- **Omissions**: Comprehensive end-to-end (E2E), property-based testing, and strict mutation testing are not currently enforced.
*(Strict coverage percentages and advanced testing paradigms will be defined in future testing strategies, not mandated here).*

---

## 13. Observability Baseline
- **Current Capability**: 
  - Standard application logs.
  - Basic metrics tracking.
  - Chat logs persistence.
  - Timing metrics (retrieval timing, generation timing, total timing).
  - Tracking of chunks retrieved.
  - Dashboard for metric visualization.
- **Future Observability Improvement**: Advanced distributed tracing or external metric export (e.g., Prometheus/Grafana integration) are considered future improvements.

---

## 14. Current Constraints
*(These are actual current constraints, not permanent architectural impossibilities)*
- **Local-first constraint**: Primarily optimized for local execution.
- **Single-user constraint**: Lacks multi-tenant data isolation.
- **File-based persistence constraint**: Relies on flat files (JSON/JSONL) and local ChromaDB rather than a centralized RDBMS.
- **Format constraint**: Limited to currently supported document formats (PDF, DOCX, TXT, MD, URL).
- **Deployment constraint**: Current Docker setup is for single-node deployment, not distributed orchestration.

---

## 15. Technical Debt
*(Verifiable debt that impacts current maintenance, prioritized for future Specs)*
- **mtime-based Indexing**: Relying on file modification times for indexing updates is fragile and can lead to inconsistent state. (Impact: Moderate, Requires future Spec).
- **Upload Validation**: Lack of deep validation on uploaded files beyond extension checks. (Impact: Moderate, Requires future Spec).
- **URL Validation**: Ingestion of URLs lacks robust sanitization and destination validation. (Impact: High for non-local environments, Requires future Spec).
- **State Rollback**: Insufficient transactionality/rollback mechanisms if document ingestion fails halfway. (Impact: Moderate, Requires future Spec).
- **Health/Telemetry Endpoints**: Need for standardized health check and metrics export endpoints. (Impact: Low, Requires future Spec).

---

## 16. Risk Register
**Confirmed concerns**:
- Incomplete URL validation poses a SSRF/content-injection risk if deployed publicly.
- `indexed_files.json` concurrency: Potential race conditions on simultaneous file ingestions.

**Potential risks**:
- Vector store synchronization: Metadata JSON and ChromaDB could drift out of sync during unexpected crashes.

**Theoretical risks**:
- API Key leakage through overly verbose debug logging (no direct evidence, but theoretically possible).
- Data loss through ChromaDB corruption under heavy concurrent load (hypothetical).

---

## 17. Non-Goals
*(Out of scope for the current system architecture; these may change in the distant future but are not current objectives)*
- Enterprise authentication (SSO, Active Directory, OAuth).
- True multi-user/multi-tenant architecture.
- Kubernetes or cloud-native microservices orchestration.
- Distributed vector databases (e.g., Milvus/Pinecone clusters).
- Cloud-first deployment models.

---

## 18. Evolution Rules
The following rules dictate how future Specs must be created and integrated:
1. **Requirements first**: New features must have clearly defined requirements.
2. **Design reviews**: Significant architectural changes require explicit design documentation and review.
3. **Justification**: Architectural and stack decisions must be justified (no hype-driven development).
4. **No enterprise bloat**: Do not introduce unnecessary enterprise complexity for a local-first tool.
5. **Migration strategy**: Breaking changes to data or APIs require a documented migration strategy.
6. **Objective validation**: RAG pipeline improvements must be objectively verifiable (e.g., via benchmarking).
7. **Dependency justification**: New external dependencies must justify their inclusion in the footprint.
8. **Preserve observability**: Modifying the RAG pipeline must not break existing metrics and logs.
9. **Respect boundaries**: Architectural layers (Frontend, API, Engine, Persistence) must remain decoupled.
10. **State distinction**: Future Specs must clearly distinguish between *current behavior* and *target behavior*.

---

## 19. Quality Baseline
*(These are baseline assessments derived from initial audits. They are not acceptance criteria, but starting points for improvement)*
- **Architecture**: Functional but exhibits tight coupling in certain edge cases.
- **Code Quality**: Adequate, with areas requiring better typing and abstraction.
- **Testing**: Exists, but lacks comprehensive integration/E2E coverage.
- **Security**: Suitable for local-first; requires hardening for public deployment.
- **Observability**: Good baseline timings, lacks advanced tracing.
- **RAG Quality**: Functional baseline, requires benchmark-driven tuning.
- **Scalability**: Limited to vertical scaling (single-node).
- **Maintainability**: Fair; highly dependent on adhering to SDD for future clarity.
- **Documentation**: SDD-00 establishes the new baseline.
- **Developer Experience**: Dockerized, but lacks structured local development tooling boundaries.

---

## 20. Definition of Done (DoD) for Future Specs
Future Specs are considered "Done" when:
- Requirements are formally approved.
- Design is reviewed (when applicable).
- Implementation tasks are fully defined and completed.
- Tests are passing, and new coverage is added where relevant.
- Acceptance criteria defined in the Spec are validated.
- Associated documentation is updated.
- There is no regression of existing verified baseline behavior.

---

## 21. Traceability
Future Specs must trace back to elements defined in SDD-00 or subsequent Specs:
- Requirements must link to specific user needs or identified Technical Debt.
- Implementations (PRs/Commits) must reference the corresponding Spec ID (e.g., `feat: implement SDD-01`).
- Tests must validate the explicit acceptance criteria of their parent Spec.

---

## 22. Out of Scope for SDD-00
The following actions are explicitly excluded from this document:
- Implementation of any new code or features.
- Refactoring of existing architecture.
- Security hardening or patching.
- RAG pipeline optimization or parameter tuning.
- User Interface redesign.
- Changing LLM or Vector DB providers.
- Database migrations.
- Performance optimization.

---

## 23. Acceptance Criteria for SDD-00
SDD-00 is complete because:
1. The current system can be understood without inspecting the source code.
2. Core component responsibilities are documented.
3. Architectural boundaries are clearly defined.
4. Core principles are separated from implementation details and specific parameters.
5. Risks are correctly classified (Confirmed vs. Potential vs. Theoretical).
6. Technical debt is isolated from future features.
7. Current constraints are documented as constraints, not permanent impossibilities.
8. Non-goals are clearly established.
9. Rules for future evolution (Specs) are defined.
10. No critical claim relies on an unverified assumption.
