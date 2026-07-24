# 📁 Directory Structure & Development Architecture Guide
## TeleAgent AI: Deutsche Telekom Omnichannel Consumer Engine (Problem Statement 5)

---

## 📌 Master Directory Tree

```
D:\Hackthon\
│
├── 📂 backend/                             # Python FastAPI & LangGraph Multi-Agent Backend
│   ├── main.py                             # FastAPI REST API Endpoints & Server Entry Point
│   ├── config.py                           # LLM Provider Configuration & Fallback Engine
│   ├── 📂 agents/                          # LangGraph Multi-Agent Architecture
│   │   ├── __init__.py                     # Agent Package Initialization
│   │   ├── state.py                        # AgentState TypedDict (Shared Graph Memory Schema)
│   │   └── multi_agent_system.py           # StateGraph Supervisor, Worker Nodes & Checkpointer
│   └── 📂 tools/                           # Specialized Telecom Tools & RAG Engine
│       ├── __init__.py                     # Tools Package Initialization
│       └── telecom_tools.py                # DT Subscriber Data, ChromaDB RAG, Speedport Tools
│
├── 📂 frontend/                            # Web & Mobile Viewport User Interface
│   ├── index.html                          # Dashboard Markup, OneApp Shell, Drawers & Modals
│   ├── style.css                           # Glassmorphic Theme, Design Tokens & Mobile Shell Styles
│   └── app.js                              # Frontend Logic, Web Speech API, Fetch Handlers & State
│
├── 📂 .system_generated/                   # Task Execution Logs & Internal Metadata (Ignored in Git)
│
├── 📄 start_server.py                      # Local Development Server Launcher Script
├── 📄 test_live_demo.py                    # Automated Integration Test Suite (6 Live Demo Scenarios)
├── 📄 requirements.txt                     # Python Package Dependencies Manifest
├── 📄 Dockerfile                           # Docker Container Image Build Instructions
├── 📄 docker-compose.yml                   # Container Orchestration Setup
├── 📄 .gitignore                           # Git Excluded Files (.env, cache, temp logs)
├── 📄 .env.example                         # Environment Variables Template
├── 📄 README.md                            # Master Project Setup & Quickstart Guide
├── 📄 PROJECT_FUNCTIONALITIES_AND_ARCHITECTURE.md # Detailed Architectural Documentation
├── 📄 HACKATHON_DEMO_SUMMARY.md            # Live Demo Presentation Script & Q&A Pitch Strategy
├── 📄 PROBLEM_STATEMENT_5_EVALUATION.md    # Problem Statement 5 Evaluation & Capability Audit
└── 📄 BEGINNERS_GUIDE_AND_CODE_WALKTHROUGH.md # Educational Concepts & Line-by-Line Code Walkthrough
```

---

## 🛠️ Detailed Breakdown of Every Folder & Purpose

---

### 1. 📂 `backend/` — Server & Artificial Intelligence Layer

The `backend/` folder houses the entire Python server, multi-agent AI logic, database records, and vector search retrieval.

#### 📄 `backend/main.py`
* **Purpose**: The main application entry point and Web REST API server built with **FastAPI**.
* **Development Role**:
  * Initializes the FastAPI application instance.
  * Mounts static frontend files from `frontend/` to serve `index.html` at `http://localhost:8000`.
  * **Exposes REST Endpoints**:
    * `GET /api/health` — System health check & service status.
    * `POST /api/chat` — Accepts user messages, customer ID, and `ab_variant`, passes them into the LangGraph state machine, and returns AI responses, active agent telemetry, and execution logs.
    * `GET /api/cart/{customer_id}` — Returns optimized cart items, 19% VAT calculations, and MagentaEins bundle discounts.
    * `GET /api/explainable-ai/{product_id}` — Returns vector confidence scores (98.4%) and rule match justifications.
    * `POST /api/approve-action` — Executes approved Human-in-the-Loop SEPA credit refunds (€29.75).
    * `POST /api/feedback` — Accepts RLHF preference feedback signals (`like` / `dislike`) and logs reward scores (+1.0 / -1.0).
    * `GET /api/impact-summary` — Returns projected business outcomes metrics (-24.5% cart abandonment).

#### 📄 `backend/config.py`
* **Purpose**: Environment configuration and LLM model initialization.
* **Development Role**:
  * Loads environment variables from `.env` using `python-dotenv`.
  * Sets up primary LLM (**Groq Llama-3.3-70b-versatile**) with automatic fallback to secondary LLM (**Google Gemini 1.5 Flash**) in case of rate limits or network issues.

---

### 2. 📂 `backend/agents/` — Multi-Agent Intelligence Engine

The `backend/agents/` folder implements the core **LangGraph Multi-Agent State Machine**.

#### 📄 `backend/agents/state.py`
* **Purpose**: Defines `AgentState`, the shared memory schema passed between all graph nodes.
* **Development Role**:
  * Uses `TypedDict` and `Annotated[List[BaseMessage], add_messages]` to ensure chat history is appended atomically.
  * Tracks `active_agent`, `execution_logs`, `customer_id`, `ab_variant`, and HITL safety flags (`requires_human_approval`, `pending_tool_call`).

#### 📄 `backend/agents/multi_agent_system.py`
* **Purpose**: Builds and compiles the **LangGraph Supervisor StateGraph**.
* **Development Role**:
  * **Supervisor Node**: Analyzes incoming queries, checks keywords, tracks visited nodes, and routes queries to worker agents.
  * **Network Agent Node**: Specialized worker for Speedport WLAN diagnostics and reboots.
  * **Billing Agent Node**: Specialized worker for invoice line items, VAT calculations, and HITL refund checks.
  * **Plan Agent Node**: Specialized worker for Magenta catalog search, smart cart optimization, and XAI rationale.
  * **Variant-Aware Prompts**: Reads `state["ab_variant"]` to inject Variant A (Discount Focus) vs Variant B (Speed Focus) prompt rules.
  * **Checkpointer**: Attaches `MemorySaver()` keyed by `thread_id` for live omnichannel session state persistence.

---

### 3. 📂 `backend/tools/` — Specialized Telecom Tools & Vector RAG

The `backend/tools/` folder contains domain data, Python tools, and vector search.

#### 📄 `backend/tools/telecom_tools.py`
* **Purpose**: Defines tools, mock databases, and ChromaDB vector search.
* **Development Role**:
  * Stores mock Deutsche Telekom European subscriber records (`Alex Mercer - Bonn`, `Sarah Connor - Berlin`, `Lukas Weber - Frankfurt`).
  * Initializes **ChromaDB Vector Store Collection** (`dtdl_telecom_rag`) with 8 European technical manuals.
  * Uses `FastVectorEF` custom 64-dimensional embedding function for 0-latency offline vector search.
  * `@tool` functions: `check_router_diagnostics`, `reboot_router`, `fetch_billing_statement`, `apply_bill_credit`, `search_plan_catalog`, `get_explainable_recommendation`, `optimize_smart_cart`, and `retrieve_kb_articles`.

---

### 4. 📂 `frontend/` — Storefront UI & Mobile Viewport Shell

The `frontend/` folder houses the responsive glassmorphic user interface.

#### 📄 `frontend/index.html`
* **Purpose**: HTML structure for the web dashboard and mobile app frame.
* **Development Role**:
  * Header with channel switcher (`OneShop Web` vs `OneApp Mobile`), A/B AI engine switcher, subscriber selector, and cart button.
  * Left sidebar showing real-time agent telemetry, business ROI metrics panel, and execution logs.
  * Center chat area with Next Best Action (NBA) banner, quick prompt chips, HITL approval banner, and chat messages.
  * Slide-out Smart Cart Drawer and Explainable AI (XAI) Modal overlay.

#### 📄 `frontend/style.css`
* **Purpose**: Vanilla CSS styling system.
* **Development Role**:
  * Dark mode design tokens (Magenta `--dt-magenta: #E20074`, Cyan `--dt-cyan: #00F0FF`).
  * Responsive layout grid and pulse animations.
  * `body.mode-oneapp` styles transforming the chat section into a realistic **390px × 800px Smartphone Shell Container with an OLED Notch**.

#### 📄 `frontend/app.js`
* **Purpose**: Client-side JavaScript interactivity.
* **Development Role**:
  * Handles form submission and sends `POST /api/chat` requests with message, subscriber ID, and `ab_variant`.
  * Integrates **Web Speech API (`de-DE` locale)** for voice-enabled assistant input.
  * Manages Cart Drawer fetching (`GET /api/cart`), XAI modal rendering, and HITL approval confirmation (`POST /api/approve-action`).
  * Calls `window.handleFeedback` to record 👍/👎 ratings via `POST /api/feedback`.

---

### 5. 📂 Root Infrastructure & Documentation Files

* 📄 `start_server.py`: Script to launch `uvicorn backend.main:app --reload` on `http://localhost:8000`.
* 📄 `test_live_demo.py`: Automated integration test suite validating all 6 demo scenarios live.
* 📄 `requirements.txt`: Python package manifest (`fastapi`, `uvicorn`, `langchain`, `langgraph`, `chromadb`, `groq`).
* 📄 `Dockerfile` & `docker-compose.yml`: Containerized deployment configurations.
* 📄 `PROJECT_FUNCTIONALITIES_AND_ARCHITECTURE.md`: Complete technical system documentation.
* 📄 `HACKATHON_DEMO_SUMMARY.md`: Live demo script & judge Q&A pitch strategy.
* 📄 `PROBLEM_STATEMENT_5_EVALUATION.md`: Problem Statement 5 requirement audit matrix.
* 📄 `BEGINNERS_GUIDE_AND_CODE_WALKTHROUGH.md`: Educational concept guide & code explanation.

---

### 🚀 Summary Workflow Across Folders

```
[User Input in frontend/app.js]
              │
              ▼ (POST /api/chat payload: message, customer_id, ab_variant)
[backend/main.py (FastAPI Endpoint)]
              │
              ▼ (Invokes StateGraph with thread_id)
[backend/agents/multi_agent_system.py (LangGraph Supervisor)]
              │
              ├──► [backend/tools/telecom_tools.py (ChromaDB RAG & Speedport Tools)]
              │
              ▼ (Returns AI Response, Tool Cards, Execution Logs & HITL Flags)
[Rendered on frontend/index.html & synced across OneShop / OneApp]
```
