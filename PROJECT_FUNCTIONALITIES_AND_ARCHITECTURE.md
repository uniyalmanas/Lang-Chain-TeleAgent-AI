# 📘 Deutsche Telekom Digital Labs (DTDL)
## TeleAgent AI: Complete Functionalities & Architecture Guide
### Problem Statement 5: Omnichannel Consumer AI Engine for Digital Commerce

---

## 📌 1. Project Overview & Scope
**TeleAgent AI** is an enterprise-ready, multi-agent AI engine designed specifically for **Deutsche Telekom AG (Germany & Europe)**. Built to satisfy **Problem Statement 5**, the engine personalizes the customer discovery journey, resolves technical broadband and billing issues autonomously with human safety guardrails, and synchronizes active subscriber state in real time across **OneShop (Web Storefront)** and **OneApp (Mobile Client)**.

---

## 🛠️ 2. Core Functional Requirements Implemented

### 2.1 🌐 Omnichannel Storefront & Viewport Engine
* **Dual Viewport Interfaces**:
  * **OneShop (Web Storefront)**: Full-screen enterprise dashboard view designed for desktop broadband and plan discovery.
  * **OneApp (Mobile Client)**: Realistic **390px × 800px Smartphone Shell Container** featuring an OLED Notch, Mobile Nav Header, and Magenta Glow lighting.
* **Live Session State Checkpointing**: Powered by LangGraph `MemorySaver` (`thread_id`), active carts, diagnostic states, and conversation turns persist seamlessly when toggling between web and mobile viewports.

---

### 2.2 🧠 Multi-Agent Supervisor Architecture (LangGraph)
* **Supervisor Router Agent**: Deterministic keyword-first intent router backed by a LangGraph state machine with automatic fallback to Groq Llama 3.3 70B & Gemini 1.5 Flash.
* **Network & Diagnostics Agent**: Pings Speedport gateway routers, evaluates 5GHz WLAN channel congestion, packet loss, signal drop (-74 dBm), and executes automated remote soft reboots.
* **Billing & Financial Resolution Agent**: Inspects monthly invoices, calculates 19% German VAT (MwSt.), verifies BNetzA SLAs, and triggers **Human-in-the-Loop (HITL)** approval before issuing SEPA Direct Debit credit refunds.
* **Commerce & Plan Advisor Agent**: Queries the Magenta product catalog, optimizes smart carts, applies MagentaEins bundle discounts, and generates Explainable AI (XAI) confidence scores.

---

### 2.3 🛡️ Human-In-The-Loop (HITL) Financial Safety Guardrails
* Sensitive financial tools like `apply_bill_credit` flag `requires_human_approval = True`.
* The UI displays a prominent **BNETZA HUMAN APPROVAL REQUIRED** banner requiring explicit supervisor confirmation before any SEPA credit refund (€29.75) is executed.

---

### 2.4 ⚡ ChromaDB Vector Similarity Search RAG Engine
* **Local Collection**: `dtdl_telecom_rag` initialized in `backend/tools/telecom_tools.py`.
* **Zero-Latency Embedding Function**: `FastVectorEF` custom 64-dimensional hashed vector function running offline with zero network dependencies.
* **Provenance Metrics**: `retrieve_kb_articles` returns `vector_similarity_score` (e.g., `0.984`) and `ChromaDB Vector Store` metadata for BNetzA regulations and Speedport manuals.

---

### 2.5 🅰️/🅱️ Live A/B Recommendation Engine Switcher
* Header toggle between **Variant A (Discount Focus)** and **Variant B (Speed Focus)**.
* **End-to-End Backend Integration**: `ab_variant` payload is sent in `POST /api/chat`, dynamically injecting variant-specific prompt rules into worker agent system prompts (Variant A emphasizes VAT savings and discounts; Variant B emphasizes 1 Gbps speed and low latency).

---

### 2.6 👍/👎 Continuous Learning Loop (RLHF Feedback)
* Live REST endpoint `POST /api/feedback` accepting subscriber rating signals (`like` / `dislike`).
* Logs reward signals (`+1.0` / `-1.0`) into the backend RLHF preference optimization log.

---

### 2.7 🎙️ Voice-Enabled Shopping Assistant
* Integrated Web Speech API (`de-DE` locale) with an animated mic button and listening pulse animation for hands-free voice commands.

---

### 2.8 🇩🇪 Deutsche Telekom AG European Domain Alignment
* **Currency**: Euro (€)
* **Taxation**: 19% German Value Added Tax (MwSt.)
* **Regulatory Framework**: BNetzA (German Federal Network Agency) & GDPR Article 6 data minimization
* **Payment Rails**: SEPA Direct Debit / IBAN transactions (`DE89 3704 ...`)
* **Hardware & Products**: Speedport Smart 4, Speedport Pro Plus, MagentaZuhause Fiber 500M/1G, MagentaMobil Unlimited 5G, Magenta TV 4K Pass
* **European Subscriber Datasets**:
  * `Alex Mercer (CUST-101)`: **Bonn, Germany (DT Global HQ)** — MagentaZuhause 500M Fiber + €29.75 FIFA 4K Pass billing dispute.
  * `Sarah Connor (CUST-102)`: **Berlin, Germany** — MagentaMobil Speed XL Unlimited 5G.
  * `Lukas Weber (CUST-103)`: **Frankfurt am Main, Germany** — MagentaZuhause Giga 1 Gbps Fiber.

---

### 2.9 📊 Business Impact & Projected ROI Panel (`GET /api/impact-summary`)

| Business Metric | Target Outcome | Primary Driver |
| :--- | :--- | :--- |
| **Cart Abandonment** | **-24.5%** | Smart Cart Optimizer & MagentaEins bundle discount nudges |
| **Conversion Lift** | **+18.2%** | Explainable AI (XAI) confidence score rationale & rule matching |
| **First Contact Resolution (FCR)** | **+38.0%** | Automated Speedport channel reboot & BNetzA SEPA refunds |
| **Mean Time to Resolution (MTTR)**| **45 sec** (vs 48 hours) | Instant human-gated credit approval |

---

## 🏗️ 3. Complete Architectural System Diagram

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|   +---------------------------------------+   +-------------------------------+   |
|   |         OneShop Web Storefront        |   |       OneApp Mobile Shell     |   |
|   +-------------------+-------------------+   +---------------+---------------+   |
+-----------------------|-----------------------------------|-----------------------+
                        |                                   |
                        v                                   v
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND API                                |
|   POST /api/chat  |  GET /api/cart  |  POST /api/feedback  |  GET /api/impact-summary  |
+-----------------------|-----------------------------------------------------------+
                        v
+-----------------------------------------------------------------------------------+
|                          LANGGRAPH MULTI-AGENT ENGINE                            |
|                                                                                   |
|                               +------------------+                                |
|                               | Supervisor Agent |                                |
|                               +--------+---------+                                |
|                                        |                                          |
|            +---------------------------+---------------------------+              |
|            |                           |                           |              |
|            v                           v                           v              |
|   +-----------------+         +-----------------+         +-----------------+     |
|   | Network Agent   |         | Billing Agent   |         | Plan Agent      |     |
|   +--------+--------+         +--------+--------+         +--------+--------+     |
|            |                           |                           |              |
|            v                           v                           v              |
|   +-----------------+         +-----------------+         +-----------------+     |
|   | Speedport Tools |         | SEPA & MwSt.    |         | ChromaDB RAG    |     |
|   | Diagnostics     |         | HITL Refund Gate|         | Smart Cart      |     |
|   +-----------------+         +-----------------+         +-----------------+     |
+-----------------------------------------------------------------------------------+
```

---

## 📂 4. Repository Structure & Key Files

```
D:\Hackthon\
├── backend/
│   ├── main.py                     # FastAPI REST Endpoints & Application Initialization
│   ├── config.py                   # Multi-LLM Fallback Configuration (Groq & Gemini)
│   ├── agents/
│   │   ├── state.py                # AgentState Schema Definition (ab_variant, HITL flags)
│   │   └── multi_agent_system.py   # LangGraph Multi-Agent Supervisor & Worker Nodes
│   └── tools/
│       └── telecom_tools.py        # Speedport Tools, ChromaDB RAG, SEPA Refund Engine
├── frontend/
│   ├── index.html                  # Glassmorphic Omnichannel Dashboard & Mobile Viewport
│   ├── style.css                   # DT Dark/Magenta Theme & Mobile Device Shell Styles
│   └── app.js                      # Event Handlers, Voice API, A/B Switcher, Cart Drawer
├── PROJECT_FUNCTIONALITIES_AND_ARCHITECTURE.md # Full System Functionality Guide
├── HACKATHON_DEMO_SUMMARY.md       # Presentation Script & Q&A Strategy
├── start_server.py                 # Application Launcher Script
├── Dockerfile                      # Container Build Configuration
├── docker-compose.yml              # Multi-container Deployment Setup
└── requirements.txt                # Dependency Manifest (FastAPI, LangGraph, ChromaDB)
```

---

## 🚀 5. Quick Start Instructions
To run the complete application locally:
```bash
python start_server.py
```
Open browser at: `http://localhost:8000`
