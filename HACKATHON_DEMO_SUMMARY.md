# 🏆 Deutsche Telekom Digital Labs — TeleAgent AI Context Summary
## Problem Statement 5: Omnichannel Consumer AI Engine for Digital Commerce

---

### 📌 Executive Overview
**TeleAgent AI** is an enterprise-grade, agentic omnichannel consumer intelligence engine built specifically for **Deutsche Telekom AG (Germany & Europe)**. It personalizes the subscriber journey, resolves network & billing issues autonomously with human safety gates, and synchronizes session state seamlessly across **OneShop (Web Storefront)** and **OneApp (Mobile Client)**.

---

### 🏗️ Technical Architecture & Key Capabilities

#### 1. Multi-Agent Supervisor Pattern (LangGraph)
* **Supervisor Agent Node**: Deterministic keyword-first routing with LLM fallback (Groq Llama 3.3 70B & Gemini 1.5 Flash). Routes queries to specialized domain workers.
* **Network & Diagnostics Agent**: Pings Speedport gateway routers, evaluates 5GHz WLAN channel congestion, and executes remote soft reboots.
* **Billing & Financial Resolution Agent**: Analyzes monthly invoice line items, 19% German VAT (MwSt.), BNetzA SLAs, and triggers **Human-in-the-Loop (HITL)** approval before issuing SEPA Direct Debit credit refunds.
* **Commerce & Plan Advisor Agent**: Queries Magenta product catalog, optimizes smart carts, and generates Explainable AI (XAI) rationale.

#### 2. Omnichannel Viewport & State Synchronization
* Dual-interface support: **OneShop (Web Storefront)** and **OneApp (Mobile Device Shell with OLED Notch)**.
* Continuous state checkpointing using LangGraph `MemorySaver` (`thread_id`), ensuring cart items and diagnostic states persist across channel switches.

#### 3. Real ChromaDB Vector Similarity RAG Engine
* In-memory **ChromaDB Vector Store Collection** (`dtdl_telecom_rag`) queried via `retrieve_kb_articles`.
* Zero-latency, keyless vector distance calculation (`FastVectorEF`), returning `vector_similarity_score` metrics for BNetzA regulation and Speedport technical manuals.

#### 4. Live A/B Testing & RLHF Preference Feedback
* Header toggle between **Variant A (Discount Focus)** and **Variant B (Speed Focus)**. Backend worker nodes dynamically adapt system prompts based on selected variant.
* **RLHF Preference Feedback Loop**: `POST /api/feedback` endpoint records subscriber 👍/👎 feedback into the reward signal log.

#### 5. Deutsche Telekom European Domain Fidelity
* **Currency**: EUR (€)
* **Tax**: 19% German VAT (MwSt.)
* **Regulators**: BNetzA (Federal Network Agency) & GDPR Article 6 consent compliance
* **Payment Rails**: SEPA Direct Debit / IBAN
* **Hardware & Products**: Speedport Smart 4, Speedport Pro Plus, MagentaZuhause Fiber 500M/1G, MagentaMobil Unlimited 5G, Magenta TV 4K Pass
* **European Subscribers & Cities**:
  * `Alex Mercer (CUST-101)`: Bonn, Germany *(DT Global HQ Hub)* — Fiber 500M + €29.75 FIFA 4K Pass Dispute
  * `Sarah Connor (CUST-102)`: Berlin, Germany — MagentaMobil Unlimited 5G
  * `Lukas Weber (CUST-103)`: Frankfurt am Main, Germany — MagentaZuhause Giga 1 Gbps Fiber

---

### 📊 Projected Business Impact (`GET /api/impact-summary`)

| Metric | Target Outcome | Driver |
| :--- | :--- | :--- |
| **Cart Abandonment** | **-24.5%** | Smart Cart Optimizer & MagentaEins bundle discount nudges |
| **Conversion Lift** | **+18.2%** | Explainable AI (XAI) rationale & rule matching |
| **First Contact Resolution (FCR)** | **+38.0%** | Automated Speedport channel reboot & BNetzA SEPA refunds |
| **Mean Time to Resolution (MTTR)**| **45 sec** (vs 48 hours) | Instant human-gated credit approval |

---

### 🎬 Live Demo Script (Step-by-Step for Judges)

1. **Omnichannel Viewport Switch**:
   - Start in `OneShop (Web)` mode with subscriber `Alex Mercer (Bonn)`.
   - Click `📱 OneApp (Mobile)` — point out the mobile smartphone shell with notch and state synchronization.
2. **Speedport WLAN Diagnostics**:
   - Click quick prompt: *"Check my Speedport WiFi speed and router diagnostics in Bonn right now."*
   - Show `Network Agent` activation log and click *"Apply Recommendation"* to trigger remote channel reboot.
3. **Billing Dispute & Human-In-The-Loop Approval**:
   - Click quick prompt: *"Why is my bill €29.75 higher this month?"*
   - Show `Billing Agent` flagging the unconfirmed FIFA 4K Pass and displaying the yellow **BNETZA HUMAN APPROVAL** banner.
   - Click *"Approve & Credit SEPA Refund"* — observe live credit application to SEPA IBAN.
4. **Explainable AI (XAI) & Smart Cart**:
   - Click *"Explainable AI Rationale"* chip to show 98.4% vector confidence score modal.
   - Open Cart Drawer to verify MagentaEins bundle discount (-€10.00) and 19% VAT calculation.
5. **Live A/B Engine Switcher**:
   - Switch header to `Variant B (Speed Focus)` and re-run a query to show prompt rationale shifting to 1 Gbps Gigabit speed and sub-6ms latency specs.

---

### 💬 Q&A Pitch Strategy

* **Q: How does your agent architecture handle routing?**
  * *A: "We use a deterministic keyword-first supervisor router backed by LangGraph with fallback to Llama 3.3 / Gemini 1.5. This guarantees sub-millisecond routing for common requests while keeping complex cases intelligent."*
* **Q: What embedding model are you using for RAG?**
  * *A: "For this demo, we built a keyless, zero-latency custom hashed vector embedding function (`FastVectorEF`) mapped to a 64-dimensional vector space inside ChromaDB. In production, it drops in directly with `sentence-transformers/all-MiniLM-L6-v2`."*
* **Q: How do you handle data privacy and financial safety?**
  * *A: "Financial actions like bill credits are gated behind an explicit Human-in-the-Loop approval barrier. Subscriber data models strictly enforce BNetzA regulatory SLAs and GDPR Article 6 data minimization."*

---

### 🔗 Git Repository
* **GitHub Remote**: [https://github.com/uniyalmanas/Lang-Chain-TeleAgent-AI](https://github.com/uniyalmanas/Lang-Chain-TeleAgent-AI)
