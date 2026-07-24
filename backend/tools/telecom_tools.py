import json
from typing import Any, cast
from langchain_core.tools import tool
try:
    import chromadb
    from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
    HAS_CHROMADB = True
except (ImportError, Exception):
    HAS_CHROMADB = False
    class EmbeddingFunction:
        def __init__(self):
            pass
    Documents = Any  # type: ignore
    Embeddings = Any  # type: ignore

# Database records for Deutsche Telekom European Subscribers (Bonn, Berlin, Frankfurt)
MOCK_CUSTOMERS = {
    "CUST-101": {
        "name": "Alex Mercer",
        "city": "Bonn, Germany (DT HQ Hub)",
        "provider": "Deutsche Telekom AG",
        "segment": "MagentaZuhause Fiber & Magenta TV",
        "plan": "MagentaZuhause XXL Fiber 500 Mbps",
        "router_model": "Speedport Smart 4 Mesh Gateway (5GHz)",
        "ip": "87.123.45.102",
        "status": "Online",
        "wifi_health": "Degraded",
        "connected_devices": 14,
        "wifi_channel_congestion": "High (Channel 6 congested)",
        "signal_strength": "-74 dBm (Poor in Master Bedroom)",
        "last_bill_amount": "€89.20 (incl. 19% German VAT)",
        "standard_bill": "€59.45 (€49.95 + 19% VAT)",
        "discrepancy": "€29.75 extra charge (€25.00 FIFA 4K Pass + €4.75 VAT)",
        "eligible_for_refund": True,
        "loyalty_tier": "MagentaEins Gold Member (3+ Years)",
        "iban_sepa": "DE89 3704 0044 0532 0130 00",
        "gdpr_consent": "Verified",
        "cart": [
            {"id": "ITEM-01", "name": "MagentaZuhause 500 Mbps Fiber Plan", "price": 49.95, "type": "Plan"},
            {"id": "ITEM-02", "name": "FIFA World Cup 4K Sports Pass", "price": 25.00, "type": "Add-on"}
        ]
    },
    "CUST-102": {
        "name": "Sarah Connor",
        "city": "Berlin, Germany",
        "provider": "Deutsche Telekom AG",
        "segment": "MagentaMobil 5G Unlimited",
        "plan": "MagentaMobil Speed XL Unlimited 5G",
        "router_model": "Speedport Smart 5G Mesh",
        "ip": "80.187.112.45",
        "status": "Online",
        "wifi_health": "Excellent",
        "connected_devices": 6,
        "wifi_channel_congestion": "Low",
        "signal_strength": "-42 dBm",
        "last_bill_amount": "€59.45 (incl. 19% German VAT)",
        "standard_bill": "€59.45",
        "discrepancy": "€0.00",
        "eligible_for_refund": False,
        "loyalty_tier": "MagentaEins Platinum Member (5+ Years)",
        "iban_sepa": "DE21 1005 0000 1067 4832 99",
        "gdpr_consent": "Verified",
        "cart": [
            {"id": "ITEM-03", "name": "MagentaMobil Unlimited Truly 5G", "price": 49.95, "type": "Plan"}
        ]
    },
    "CUST-103": {
        "name": "Lukas Weber",
        "city": "Frankfurt am Main, Germany",
        "provider": "Deutsche Telekom AG",
        "segment": "MagentaEins Gigabit Fiber Enterprise",
        "plan": "MagentaZuhause Giga 1 Gbps Fiber",
        "router_model": "Speedport Pro Plus Gaming Router",
        "ip": "217.89.201.12",
        "status": "Online",
        "wifi_health": "Optimal",
        "connected_devices": 22,
        "wifi_channel_congestion": "Low",
        "signal_strength": "-48 dBm",
        "last_bill_amount": "€95.14 (incl. 19% German VAT)",
        "standard_bill": "€95.14",
        "discrepancy": "€0.00",
        "eligible_for_refund": False,
        "loyalty_tier": "VIP Magenta Business Tier",
        "iban_sepa": "DE50 5001 0517 0648 4800 11",
        "gdpr_consent": "Verified",
        "cart": [
            {"id": "ITEM-04", "name": "MagentaZuhause Giga 1Gbps Fiber", "price": 79.95, "type": "Plan"}
        ]
    }
}

class FastVectorEF(EmbeddingFunction[Documents]):
    """
    Lightweight, dependency-free embedding function using hashed token counting.
    NOTE: This is NOT a semantic embedding model — it does not capture synonyms
    or contextual meaning. Used here for zero-latency demo purposes.
    Production upgrade path: sentence-transformers or an API-based embedding model.
    """
    def __init__(self):
        super().__init__()

    def __call__(self, input: Documents) -> Embeddings:
        vecs: Embeddings = []
        for text in input:
            tokens = str(text).lower().split()
            v = [0.0] * 64
            for tok in tokens:
                idx = int(hashlib.md5(tok.encode()).hexdigest(), 16) % 64
                v[idx] += 1.0
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            vecs.append([x / norm for x in v])
        return vecs

# Initialize ChromaDB Vector Store Client for Real Vector RAG Queries
_chroma_client = None
_chroma_collection = None

def _get_chroma_collection():
    global _chroma_client, _chroma_collection
    if not HAS_CHROMADB:
        return None
    if _chroma_collection is None:
        try:
            _chroma_client = chromadb.EphemeralClient()
            _chroma_collection = _chroma_client.get_or_create_collection(
                name="dtdl_telecom_rag",
                embedding_function=cast(Any, FastVectorEF())
            )

            if _chroma_collection.count() == 0:
                kb_docs = [
                    "If WiFi speeds drop below 50% of contracted rate, check Speedport 2.4GHz vs 5GHz channel congestion. Auto-tuning from Channel 6 to Channel 11 resolves 80% of local interference in urban European apartment blocks across Bonn, Berlin, and Frankfurt.",
                    "Under BNetzA regulation and GDPR Article 6, unconfirmed billing add-ons billed without explicit double-opt-in confirmation must be refunded within 24 hours via SEPA Direct Debit credit or invoice balance adjustment with full audit logging.",
                    "Magenta TV 4K UHD streaming requires a minimum 25 Mbps bandwidth. For multi-room setups, connect Speedport Smart 4 via Mesh WLAN pass-through or direct LAN cable.",
                    "MagentaZuhause Fiber 500 Mbps and 1 Gbps Gigabit installations include an ONT fiber modem setup with guaranteed sub-10ms ping SLA across Deutsche Telekom's European core network.",
                    "MagentaMobil Speed XL Unlimited 5G subscribers receive automatic 5G SA/NSA network prioritization, EU roaming incl. Switzerland & UK, and multi-SIM card support for tablets & smartwatches.",
                    "Per BNetzA guidelines, disputed bill line items under SEPA Direct Debit mandate must be placed in a provisional hold state during Human-in-the-Loop supervisor verification.",
                    "Speedport Smart 4 gateway supports WPA3 Enterprise encryption, dual-band Wi-Fi 6 (802.11ax) up to 6000 Mbps, and isolated Guest WLAN network setup via the Magenta app.",
                    "MagentaEins bundle discount combines fixed broadband and mobile post-paid accounts to unlock €10.00/month bill reduction, double mobile data volume, and free mobile-to-landline calls across Europe."
                ]
                kb_metadatas = [
                    {"title": "Speedport WiFi 6 Channel Auto-Tuning & 5GHz Setup", "category": "Broadband Diagnostics"},
                    {"title": "BNetzA Regulation & GDPR Compliant Refund SLA", "category": "Billing & Compliance"},
                    {"title": "Magenta TV 4K UHD Bandwidth & Hardware Requirements", "category": "Magenta TV OTT"},
                    {"title": "MagentaZuhause Fiber 500M & 1Gbps Installation SLA", "category": "Fiber Broadband"},
                    {"title": "MagentaMobil 5G Roaming & Unlimited Pass Terms", "category": "5G Mobile"},
                    {"title": "SEPA Direct Debit Chargeback & Dispute SLA", "category": "Billing & Compliance"},
                    {"title": "Speedport WPA3 Security & Guest WLAN Config", "category": "Hardware & Security"},
                    {"title": "MagentaEins Multi-Product Family Discount Rules", "category": "Magenta Bundles"}
                ]
                _chroma_collection.add(
                    documents=kb_docs,
                    metadatas=cast(Any, kb_metadatas),
                    ids=[f"doc-0{i+1}" for i in range(len(kb_docs))]
                )
        except Exception as e:
            print(f"[WARNING] ChromaDB Vector Store fallback active: {e}")
    return _chroma_collection


@tool
def check_router_diagnostics(customer_id: str = "CUST-101") -> str:
    """
    Pings the Speedport gateway router, inspects 5GHz WLAN channel congestion, 
    signal strength, packet loss, and connected device count across Deutsche Telekom networks.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    diagnostics = {
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "telecom_provider": customer["provider"],
        "location": customer.get("city", "Bonn, Germany"),
        "router_model": customer["router_model"],
        "status": customer["status"],
        "wifi_health": customer["wifi_health"],
        "connected_devices": customer["connected_devices"],
        "channel_congestion": customer["wifi_channel_congestion"],
        "signal_strength": customer["signal_strength"],
        "gdpr_status": customer.get("gdpr_consent", "Verified"),
        "next_best_action": {
            "title": "📡 WLAN Auto-Channel Tuning & Speedport Mesh Offer",
            "description": "Switch from congested Channel 6 to Channel 11. Add Speedport WiFi 6 Mesh Disc @ €4.95/mo (excl. VAT) to resolve bedroom signal drop.",
            "action_code": "RECOMMEND_MESH_EXTENDER"
        }
    }
    return json.dumps(diagnostics, indent=2)

@tool
def reboot_router(customer_id: str = "CUST-101") -> str:
    """
    Executes an automated remote soft reboot and Speedport WLAN channel auto-tuning for the subscriber's gateway.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    customer["wifi_health"] = "Optimal"
    customer["wifi_channel_congestion"] = "Low (Switched to Channel 11)"
    return json.dumps({
        "status": "Success",
        "message": f"Router ({customer['router_model']}) on Deutsche Telekom network successfully rebooted and optimized.",
        "new_channel": "Channel 11 (5GHz WLAN Band)",
        "new_wifi_health": "Optimal (100% Signal)",
        "latency_ms": 6
    }, indent=2)

@tool
def fetch_billing_statement(customer_id: str = "CUST-101") -> str:
    """
    Fetches detailed line-item breakdown of the monthly Deutsche Telekom invoice including 19% German VAT (MwSt.) breakdown.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    billing_data = {
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "provider": customer["provider"],
        "sepa_iban": customer.get("iban_sepa", "N/A"),
        "current_plan": customer["plan"],
        "base_plan_cost": customer["standard_bill"],
        "total_billed_with_vat": customer["last_bill_amount"],
        "vat_rate": "19% German VAT (MwSt.)",
        "unexpected_extra_charges": customer["discrepancy"],
        "dispute_reason": "Unrecognized FIFA 4K Streaming Pass Add-on (Billed without BNetzA double-opt-in consent)",
        "eligible_for_instant_sepa_credit": customer["eligible_for_refund"],
        "next_best_action": {
            "title": "💳 Apply €29.75 Instant SEPA Refund Credit (incl. 19% VAT)",
            "description": "MagentaEins Gold Member eligible for automated credit refund with Human Operations verification.",
            "action_code": "APPLY_BILL_REFUND"
        }
    }
    return json.dumps(billing_data, indent=2)

@tool
def apply_bill_credit(customer_id: str = "CUST-101", amount: float = 29.75, reason: str = "Billing error correction (BNetzA Compliance)") -> str:
    """
    Applies instant bill credit / SEPA refund in EUR (€) to the Deutsche Telekom subscriber account.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    customer["last_bill_amount"] = customer["standard_bill"]
    customer["discrepancy"] = "€0.00 (SEPA Refund Credited)"
    customer["eligible_for_refund"] = False

    customer["cart"] = [item for item in customer["cart"] if item["id"] != "ITEM-02"]

    return json.dumps({
        "status": "APPROVED",
        "transaction_id": "TXN-SEPA-DE-9982341",
        "credited_amount": f"€{amount:.2f}",
        "credited_to_iban": customer.get("iban_sepa", "SEPA Direct Debit"),
        "reason": reason,
        "new_balance_due": customer["last_bill_amount"],
        "gdpr_audit_logged": True
    }, indent=2)

@tool
def search_plan_catalog(query: str = "broadband 5G Magenta TV OTT passes") -> str:
    """
    Searches product catalog for Deutsche Telekom Magenta bundles (MagentaZuhause Fiber, MagentaMobil 5G, Speedport Mesh, Magenta TV 4K passes).
    """
    catalog = [
        {
            "id": "PROD-FIBER-1000",
            "name": "MagentaEins Giga Combo: 1Gbps Fiber + Unlimited Truly 5G",
            "speed": "1000 Mbps Gigabit Fiber + Unlimited 5G Mobile",
            "price": "€79.95/month (+ 19% VAT)",
            "perks": "Includes free Magenta TV 4K, Disney+, Apple TV+ & RTL+ Premium",
            "best_for": "Heavy streaming households & smart homes in Europe",
            "explainable_ai": {
                "match_score": "98.4%",
                "rationale": "High bandwidth demand detected (14 connected devices in Bonn home). Upgrading saves €20/month over separate TV subscriptions.",
                "vat_breakdown": "Base €79.95 + 19% VAT €15.19 = Total €95.14/mo"
            }
        },
        {
            "id": "PROD-FIFA-4K",
            "name": "FIFA World Cup 4K Live Sports Flex Pass",
            "price": "€25.00/month (+ 19% VAT)",
            "perks": "All live matches in 4K UHD HDR with German & English commentary",
            "best_for": "Live sports enthusiasts in Europe",
            "explainable_ai": {
                "match_score": "94.1%",
                "rationale": "Matched subscriber interest in 4K live sports broadcast events.",
                "vat_breakdown": "Base €25.00 + 19% VAT €4.75 = Total €29.75/mo"
            }
        },
        {
            "id": "PROD-MESH-BOOSTER",
            "name": "Speedport WiFi 6 Mesh Disc Extender",
            "price": "€4.95/month rental (+ 19% VAT)",
            "perks": "Penetrates thick walls in European apartment buildings",
            "best_for": "Master bedroom signal weak spots (-74 dBm)",
            "explainable_ai": {
                "match_score": "96.8%",
                "rationale": "Diagnosed -74 dBm signal drop in Master Bedroom. Mesh disc creates seamless roaming.",
                "vat_breakdown": "Base €4.95 + 19% VAT €0.94 = Total €5.89/mo"
            }
        },
        {
            "id": "PROD-IPHONE-TRADEIN",
            "name": "5G Smartphone Trade-in Offer (iPhone 15 / Galaxy S24)",
            "price": "€29.95/month 0% Finance Plan",
            "perks": "Up to €200 instant trade-in bonus + €0 downpayment with MagentaMobil 5G",
            "best_for": "5G smartphone upgrades",
            "explainable_ai": {
                "match_score": "91.2%",
                "rationale": "Subscriber on MagentaMobil Platinum tier with 5G cell tower coverage in Berlin.",
                "vat_breakdown": "Includes 1-year Deutsche Telekom device protection."
            }
        }
    ]
    return json.dumps({"catalog": catalog}, indent=2)

@tool
def get_explainable_recommendation(product_id: str = "PROD-FIBER-1000", customer_id: str = "CUST-101") -> str:
    """
    Explainable AI (XAI) Engine: Generates human-understandable justification for why 
    a specific Magenta plan, Speedport hardware booster, or OTT pass was recommended.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    explanations = {
        "PROD-FIBER-1000": {
            "product": "MagentaEins Giga Combo: 1Gbps Fiber + Unlimited Truly 5G",
            "confidence_score": 0.984,
            "matched_rules": [
                f"Connected Device Count ({customer['connected_devices']} devices) > 10 Threshold",
                "High 4K Video Bandwidth Usage (Magenta TV 4K / RTL+)",
                "MagentaEins Gold Loyalty Tier Discount Eligible (15% Off Base Rate)"
            ],
            "customer_benefit": "Eliminates evening buffering, includes free Magenta TV 4K & RTL+",
            "omnichannel_status": "Synced across OneShop Web and OneApp Mobile"
        },
        "PROD-MESH-BOOSTER": {
            "product": "Speedport WiFi 6 Mesh Disc Extender",
            "confidence_score": 0.968,
            "matched_rules": [
                f"Signal Strength in Master Bedroom ({customer['signal_strength']}) below -70 dBm threshold",
                "High wall density detected in European apartment layout"
            ],
            "customer_benefit": "Boosts room coverage to 100% full 5GHz speed",
            "omnichannel_status": "Ready for 1-click checkout"
        }
    }
    explanation = explanations.get(product_id, explanations["PROD-FIBER-1000"])
    return json.dumps(explanation, indent=2)

@tool
def optimize_smart_cart(customer_id: str = "CUST-101") -> str:
    """
    Smart Cart & Checkout Optimizer: Evaluates current cart items, 
    calculates 19% German VAT (MwSt.), applies MagentaEins bundle discounts, and returns final payable amounts.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    cart = customer.get("cart", [])

    base_subtotal = sum(item["price"] for item in cart)
    discount = 0.0
    bundle_nudge = None

    has_plan = any(item["type"] == "Plan" for item in cart)
    has_addon = any(item["type"] == "Add-on" for item in cart)

    if has_plan and has_addon:
        discount = 10.0
        bundle_nudge = "🎉 MagentaEins Bundle Discount Applied (-€10.00/mo)"

    net_base = max(0.0, base_subtotal - discount)
    vat_amount = net_base * 0.19
    grand_total = net_base + vat_amount

    return json.dumps({
        "customer_id": customer_id,
        "cart_items": cart,
        "subtotal_base": f"€{base_subtotal:.2f}",
        "bundle_discount": f"€{discount:.2f}",
        "vat_19_percent": f"€{vat_amount:.2f}",
        "total": f"€{grand_total:.2f}",
        "applied_nudge": bundle_nudge,
        "sepa_payment_ready": True
    }, indent=2)

@tool
def retrieve_kb_articles(query: str) -> str:
    """
    RAG Retriever: Queries ChromaDB vector store collection using vector embeddings
    over Deutsche Telekom knowledge base articles, BNetzA SLA terms, and streaming FAQs.
    """
    collection = _get_chroma_collection()
    if collection:
        try:
            results = collection.query(query_texts=[query], n_results=3)
            vector_docs = []
            if results and "documents" in results and results["documents"]:
                for i in range(len(results["documents"][0])):
                    doc_text = results["documents"][0][i]
                    metadata = results["metadatas"][0][i] if "metadatas" in results and results["metadatas"] else {}
                    distance = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                    vector_docs.append({
                        "title": metadata.get("title", "KB Article"),
                        "category": metadata.get("category", "General"),
                        "vector_similarity_score": f"{max(0.0, 1.0 - (distance / 2.0)):.3f}",
                        "vector_engine": "ChromaDB Vector Store (dtdl_telecom_rag)",
                        "content": doc_text
                    })
                return json.dumps({"rag_engine": "ChromaDB Vector Search Engine", "total_kb_documents": collection.count(), "kb_results": vector_docs}, indent=2)

        except Exception as e:
            print(f"ChromaDB query error: {e}")

    # Fallback keyword match if ChromaDB unavailable
    kb = [
        {
            "title": "Speedport WiFi 6 Channel Auto-Tuning & 5GHz Setup",
            "category": "Broadband Diagnostics",
            "content": "If WiFi speeds drop below 50% of contracted rate, check Speedport 2.4GHz vs 5GHz channel congestion. Auto-tuning from Channel 6 to Channel 11 resolves 80% of local interference in urban European apartment blocks."
        },
        {
            "title": "BNetzA Regulation & GDPR Compliant Refund SLA",
            "category": "Billing & Compliance",
            "content": "Under BNetzA regulation and GDPR Article 6, unconfirmed billing add-ons billed without explicit double-opt-in confirmation must be refunded within 24 hours via SEPA Direct Debit credit."
        }
    ]
    return json.dumps({"rag_engine": "ChromaDB Fallback Engine", "kb_results": kb}, indent=2)

# Tool collections grouped by agent domain
NETWORK_TOOLS = [check_router_diagnostics, reboot_router, retrieve_kb_articles]
BILLING_TOOLS = [fetch_billing_statement, apply_bill_credit, retrieve_kb_articles]
PLAN_TOOLS = [search_plan_catalog, get_explainable_recommendation, optimize_smart_cart, retrieve_kb_articles]
ALL_TOOLS = NETWORK_TOOLS + BILLING_TOOLS + PLAN_TOOLS
