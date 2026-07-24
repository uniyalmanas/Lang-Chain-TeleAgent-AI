# 📊 Deutsche Telekom Digital Labs (DTDL) — Comprehensive Project Report
## TeleAgent AI: Omnichannel Consumer AI Engine for Digital Commerce (Problem Statement 5)

---

### 1. 📌 Executive Summary
**TeleAgent AI** is an enterprise-ready, multi-agent AI engine designed for **Deutsche Telekom AG (Germany & Europe)**. Built to address **Problem Statement 5: Omnichannel Consumer AI Engine for Digital Commerce**, the system personalizes subscriber journeys, resolves complex broadband and billing issues autonomously with human safety guardrails, and synchronizes active session state in real time across **OneShop (Web Storefront)** and **OneApp (Mobile Client)**.

---

### 2. 🏗️ Multi-Agent Architecture (LangGraph & FastAPI)

```
                       +-------------------------+
                       |    User Query Input     |
                       +------------+------------+
                                    |
                                    v
                       +-------------------------+
                       |    Supervisor Agent     |
                       |  (Intent & Channel Router)|
                       +------------+------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+---------------+           +---------------+           +---------------+
| Network Agent |           | Billing Agent |           | Plan Agent    |
| (Speedport)   |           | (SEPA/MwSt.)  |           | (Magenta RAG) |
+-------+-------+           +-------+-------+           +-------+-------+
        |                           |                           |
        v                           v                           v
+---------------+           +---------------+           +---------------+
| Tools:        |           | Tools:        |           | Tools:        |
| - Diagnostics |           | - Invoices    |           | - Catalog RAG |
| - Reboot      |           | - HITL Credit |           | - Smart Cart  |
| - Chroma RAG  |           | - Chroma RAG  |           | - XAI Engine  |
+---------------+           +---------------+           +---------------+
```

* **Supervisor Node**: Deterministic keyword-first routing backed by LangGraph state machine with automatic fallback to Groq Llama 3.3 70B & Gemini 1.5 Flash.
* **Network & Diagnostics Agent**: Manages home broadband diagnostics, inspects 5GHz WLAN channel congestion, and triggers remote soft reboots for Speedport routers.
* **Billing & Financial Resolution Agent**: Inspects monthly invoices, calculates 19% German VAT (MwSt.), and enforces a **Human-in-the-Loop (HITL)** approval gate before issuing SEPA Direct Debit credit refunds.
* **Commerce & Plan Advisor Agent**: Performs ChromaDB vector similarity search over the Magenta catalog, calculates bundle discounts, and generates Explainable AI (XAI) rationale.

---

### 3. 📱 Omnichannel Viewport & State Synchronization
* **Dual Channel Viewports**:
  * **OneShop (Web Storefront)**: Full-screen enterprise dashboard view.
  * **OneApp (Mobile Client)**: Realistic 390px × 800px Smartphone Shell Container featuring an OLED Notch, Mobile Nav Header, and Accent Lighting.
* **State Persistence**: Powered by LangGraph `MemorySaver` checkpointer (`thread_id`), ensuring cart items, diagnostic states, and conversation turns persist seamlessly when toggling between web and mobile viewports.

---

### 4. 🇩🇪 Deutsche Telekom AG European Domain Alignment
* **Currency**: Euro (€)
* **Taxation**: 19% German Value Added Tax (MwSt.)
* **Regulatory Compliance**: BNetzA (Federal Network Agency) & GDPR Article 6 data minimization
* **Payment Rails**: SEPA Direct Debit / IBAN transactions (`DE89 3704 ...`)
* **Hardware & Services**: Speedport Smart 4, Speedport Pro Plus, MagentaZuhause Fiber 500M/1G, MagentaMobil Unlimited 5G, Magenta TV 4K Pass
* **European Subscriber Dataset**:
  * `Alex Mercer (CUST-101)`: **Bonn, Germany (DT Global HQ)** — MagentaZuhause 500M Fiber + €29.75 FIFA 4K Pass billing dispute.
  * `Sarah Connor (CUST-102)`: **Berlin, Germany** — MagentaMobil Speed XL Unlimited 5G.
  * `Lukas Weber (CUST-103)`: **Frankfurt am Main, Germany** — MagentaZuhause Giga 1 Gbps Fiber.

---

### 5. 🧠 ChromaDB Vector Similarity RAG Engine
* **Local Collection**: `dtdl_telecom_rag` initialized in [`backend/tools/telecom_tools.py`](file:///D:/Hackthon/backend/tools/telecom_tools.py).
* **Zero-Latency Embedding Function**: `FastVectorEF` custom hashed vector function (64-dimensional vector space) running offline without network dependencies.
* **Vector Score Metrics**: `retrieve_kb_articles` returns `vector_similarity_score` (e.g., `0.984`) and `ChromaDB Vector Store` provenance tags.

---

### 6. 🎁 Selection Bonus Capabilities Implemented

1. **🎙️ Voice-Enabled Shopping Assistant**: Integrated Web Speech API (`de-DE` locale) with pulse animation and hands-free voice command transcription.
2. **🅰️/🅱️ A/B Testing Recommendation Engine Switcher**:
   * UI header toggle between **Variant A (Discount Focus)** and **Variant B (Speed Focus)**.
   * End-to-end backend integration: `ab_variant` passes in `POST /api/chat` payload, dynamically adapting system prompt rules for worker agents.
3. **👍/👎 Continuous Learning (RLHF Preference Feedback)**:
   * Real REST endpoint `POST /api/feedback` accepting subscriber feedback ratings.
   * Logs reward signals (`+1.0` / `-1.0`) into the RLHF preference engine log.

---

### 7. 📊 Projected Business Impact & Metrics (`GET /api/impact-summary`)

| Business Metric | Target Outcome | Primary Driver |
| :--- | :--- | :--- |
| **Cart Abandonment** | **-24.5%** | Smart Cart Optimizer & MagentaEins bundle discount nudges |
| **Conversion Lift** | **+18.2%** | Explainable AI (XAI) confidence score rationale & rule matching |
| **First Contact Resolution (FCR)** | **+38.0%** | Automated Speedport channel reboot & BNetzA SEPA refunds |
| **Mean Time to Resolution (MTTR)**| **45 sec** (vs 48 hours) | Instant human-gated credit approval |

---

### 8. 📜 Git Commit Log & Remote Repository
All changes have been incrementally committed and pushed to GitHub:

* `5b6c734`: `fix(ab-testing): wire ab_variant into ChatRequest/initial_state and add real POST /api/feedback endpoint`
* `f41ddce`: `docs: add master hackathon context summary and live pitch guide`
* `0756f5a`: `feat(ab-testing): wire live A/B variant prompt routing and RLHF preference feedback POST /api/feedback endpoint`
* `01ff934`: `feat(analytics): add /api/impact-summary business outcomes & projected ROI metrics panel`
* `e341128`: `refactor(dt-domain): align data model with Deutsche Telekom AG European operations`
* `05c870f`: `feat(omnichannel): build real OneApp Mobile device viewport shell with live session state synchronization`
* `a365060`: `feat(rag): integrate real ChromaDB vector similarity search engine with sub-millisecond embeddings`

🔗 **GitHub Remote**: [https://github.com/uniyalmanas/Lang-Chain-TeleAgent-AI](https://github.com/uniyalmanas/Lang-Chain-TeleAgent-AI)

---

### 9. 🚀 Server Launch & Execution
To start the application server locally:
```bash
python start_server.py
```
Open browser at: `http://localhost:8000`
