import json
from langchain_core.tools import tool

# Database records for Indian Enterprise Telecom & Digital Commerce (Airtel, Jio, Tata, DTDL India Hub)
MOCK_CUSTOMERS = {
    "CUST-101": {
        "name": "Rahul Sharma",
        "city": "Gurugram, Haryana (Delhi NCR)",
        "provider": "DTDL / Airtel Xstream Fiber",
        "segment": "Fiber Broadband & OTT Heavy Streaming",
        "plan": "Magenta Ultra / Airtel Black 500 Mbps Fiber",
        "router_model": "Smart WiFi 6 Dual-Band Mesh Router",
        "ip": "49.207.182.102",
        "status": "Online",
        "wifi_health": "Degraded",
        "connected_devices": 14,
        "wifi_channel_congestion": "High (Channel 6 congested)",
        "signal_strength": "-74 dBm (Poor in Master Bedroom)",
        "last_bill_amount": "₹1,768.82 (incl. 18% GST)",
        "standard_bill": "₹1,178.82 (₹999 + 18% GST)",
        "discrepancy": "₹590.00 extra charge (₹500 FIFA World Cup 4K Pass + ₹90 GST)",
        "eligible_for_refund": True,
        "loyalty_tier": "Gold Subscriber (3+ Years)",
        "upi_id": "rahul.sharma@okicici",
        "cart": [
            {"id": "ITEM-01", "name": "500 Mbps Fiber Broadband Plan", "price": 999.0, "type": "Plan"},
            {"id": "ITEM-02", "name": "FIFA World Cup 4K Sports Pass", "price": 500.0, "type": "Add-on"}
        ]
    },
    "CUST-102": {
        "name": "Priya Patel",
        "city": "Bengaluru, Karnataka",
        "provider": "DTDL / Reliance Jio Truly 5G",
        "segment": "Truly 5G Mobile & Enterprise IT",
        "plan": "Unlimited 5G Postpaid Family Plan",
        "router_model": "JioAirFiber 5G Gateway",
        "ip": "157.33.210.45",
        "status": "Online",
        "wifi_health": "Excellent",
        "connected_devices": 6,
        "wifi_channel_congestion": "Low",
        "signal_strength": "-42 dBm",
        "last_bill_amount": "₹942.82 (incl. 18% GST)",
        "standard_bill": "₹942.82",
        "discrepancy": "₹0.00",
        "eligible_for_refund": False,
        "loyalty_tier": "Platinum Subscriber (5+ Years)",
        "upi_id": "priya.patel@upi",
        "cart": [
            {"id": "ITEM-03", "name": "Unlimited Truly 5G Family Pack", "price": 799.0, "type": "Plan"}
        ]
    },
    "CUST-103": {
        "name": "Vikram Malhotra",
        "city": "Mumbai, Maharashtra",
        "provider": "Tata Play Fiber / DTDL India",
        "segment": "Enterprise High-Speed Broadband",
        "plan": "Tata Play Fiber 1 Gbps Ultra Pack",
        "router_model": "Nokia ONT WiFi 6 Router",
        "ip": "115.240.98.12",
        "status": "Online",
        "wifi_health": "Optimal",
        "connected_devices": 22,
        "wifi_channel_congestion": "Low",
        "signal_strength": "-48 dBm",
        "last_bill_amount": "₹2,358.82 (incl. 18% GST)",
        "standard_bill": "₹2,358.82",
        "discrepancy": "₹0.00",
        "eligible_for_refund": False,
        "loyalty_tier": "VIP Corporate Tier",
        "upi_id": "vikram@paytm",
        "cart": [
            {"id": "ITEM-04", "name": "1 Gbps Enterprise Fiber Plan", "price": 1999.0, "type": "Plan"}
        ]
    }
}

@tool
def check_router_diagnostics(customer_id: str = "CUST-101") -> str:
    """
    Pings the home broadband gateway router, inspects WiFi channel congestion, 
    signal strength, packet loss, and connected device count across Indian networks.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    diagnostics = {
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "telecom_provider": customer["provider"],
        "location": customer.get("city", "Gurugram, Haryana"),
        "router_model": customer["router_model"],
        "status": customer["status"],
        "wifi_health": customer["wifi_health"],
        "connected_devices": customer["connected_devices"],
        "channel_congestion": customer["wifi_channel_congestion"],
        "signal_strength": customer["signal_strength"],
        "next_best_action": {
            "title": "📡 WiFi Auto-Channel Tuning & Smart Mesh Offer",
            "description": "Switch from congested Channel 6 to Channel 11. Add Smart WiFi 6 Mesh Extender @ ₹149/mo (excl. GST) to fix master bedroom dead zone.",
            "action_code": "RECOMMEND_MESH_EXTENDER"
        }
    }
    return json.dumps(diagnostics, indent=2)

@tool
def reboot_router(customer_id: str = "CUST-101") -> str:
    """
    Executes an automated remote soft reboot and WiFi channel auto-tuning for the Indian customer's router.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    customer["wifi_health"] = "Optimal"
    customer["wifi_channel_congestion"] = "Low (Switched to Channel 11)"
    return json.dumps({
        "status": "Success",
        "message": f"Router ({customer['router_model']}) on {customer['provider']} successfully rebooted and optimized.",
        "new_channel": "Channel 11 (5GHz Band)",
        "new_wifi_health": "Optimal (100% Signal)",
        "latency_ms": 8
    }, indent=2)

@tool
def fetch_billing_statement(customer_id: str = "CUST-101") -> str:
    """
    Fetches detailed line-item breakdown of the Indian customer's monthly bill including 18% GST tax breakdown.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    billing_data = {
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "provider": customer["provider"],
        "upi_linked": customer.get("upi_id", "N/A"),
        "current_plan": customer["plan"],
        "base_plan_cost": customer["standard_bill"],
        "total_billed_with_gst": customer["last_bill_amount"],
        "gst_rate": "18% (CGST 9% + SGST 9%)",
        "unexpected_extra_charges": customer["discrepancy"],
        "dispute_reason": "Unrecognized FIFA 4K Streaming Pass Add-on (Billed without SMS consent per TRAI norms)",
        "eligible_for_instant_upi_credit": customer["eligible_for_refund"],
        "next_best_action": {
            "title": "💳 Apply ₹590 Instant UPI Refund Credit (via PhonePe/GPay)",
            "description": "Gold Subscriber eligible for automated credit refund with Human Operations verification.",
            "action_code": "APPLY_BILL_REFUND"
        }
    }
    return json.dumps(billing_data, indent=2)

@tool
def apply_bill_credit(customer_id: str = "CUST-101", amount: float = 590.0, reason: str = "Billing error correction (TRAI Compliance)") -> str:
    """
    Applies instant bill credit / UPI refund in INR (₹) to the customer's Indian telecom balance.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    customer["last_bill_amount"] = customer["standard_bill"]
    customer["discrepancy"] = "₹0.00 (UPI Refund Credited)"
    customer["eligible_for_refund"] = False

    customer["cart"] = [item for item in customer["cart"] if item["id"] != "ITEM-02"]

    return json.dumps({
        "status": "APPROVED",
        "transaction_id": "TXN-UPI-IND-9982341",
        "credited_amount": f"₹{amount:.2f}",
        "credited_to_upi": customer.get("upi_id", "GPay/PhonePe"),
        "reason": reason,
        "new_balance_due": customer["last_bill_amount"],
        "trai_receipt_sent": True
    }, indent=2)

@tool
def search_plan_catalog(query: str = "broadband 5G OTT passes Indian market") -> str:
    """
    Searches product catalog for Indian telecom & entertainment bundles (Jio, Airtel Xstream, DTDL, Tata Play, Disney+ Hotstar, JioCinema Premium, SonyLIV, Amazon Prime).
    """
    catalog = [
        {
            "id": "PROD-FIBER-1000",
            "name": "Indian Super Combo: 1Gbps Fiber + Unlimited Truly 5G",
            "speed": "1000 Mbps Fiber + Truly Unlimited 5G Mobile",
            "price": "₹1,499/month (+ 18% GST)",
            "perks": "Includes free Disney+ Hotstar, SonyLIV, JioCinema Premium & Magenta TV 4K",
            "best_for": "Heavy streaming households & smart homes in India",
            "explainable_ai": {
                "match_score": "98.4%",
                "rationale": "High bandwidth demand detected (14 connected devices in Gurugram). Upgrading saves ₹650/month over separate OTT subscriptions.",
                "gst_breakdown": "Base ₹1,499 + GST ₹269.82 = Total ₹1,768.82/mo"
            }
        },
        {
            "id": "PROD-FIFA-4K",
            "name": "FIFA World Cup 4K Live Sports Flex Pass",
            "price": "₹299/month (+ GST)",
            "perks": "All live matches in 4K UHD with Hindi, English, Tamil & Telugu commentary",
            "best_for": "Sports enthusiasts in India",
            "explainable_ai": {
                "match_score": "94.1%",
                "rationale": "Matched subscriber preference for multi-language 4K live sports events.",
                "gst_breakdown": "Base ₹299 + GST ₹53.82 = Total ₹352.82/mo"
            }
        },
        {
            "id": "PROD-MESH-BOOSTER",
            "name": "Smart WiFi 6 Mesh Extender (Indian Apartments Special)",
            "price": "₹149/month rental (+ GST)",
            "perks": "Penetrates thick brick & concrete walls in Indian flats",
            "best_for": "Master bedroom signal weak spots (-74 dBm)",
            "explainable_ai": {
                "match_score": "96.8%",
                "rationale": "Diagnosed -74 dBm signal drop in Master Bedroom. Mesh eliminates dead zones without cabling.",
                "gst_breakdown": "Base ₹149 + GST ₹26.82 = Total ₹175.82/mo"
            }
        },
        {
            "id": "PROD-IPHONE-TRADEIN",
            "name": "5G Smartphone Trade-in Offer (iPhone 15 / Galaxy S24)",
            "price": "₹2,199/month No-Cost EMI via UPI / Credit Card",
            "perks": "Up to ₹10,000 instant trade-in bonus + 0 downpayment with Truly 5G Plan",
            "best_for": "5G mobile upgrades in Metro cities",
            "explainable_ai": {
                "match_score": "91.2%",
                "rationale": "Subscriber on Platinum 5G mobile tier with 5G NSA/SA coverage in Bengaluru.",
                "gst_breakdown": "Includes 1-year screen protection insurance."
            }
        }
    ]
    return json.dumps({"catalog": catalog}, indent=2)

@tool
def get_explainable_recommendation(product_id: str = "PROD-FIBER-1000", customer_id: str = "CUST-101") -> str:
    """
    Explainable AI (XAI) Engine: Generates human-understandable justification for why 
    a specific Indian telecom plan, hardware booster, or OTT pass was recommended.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    explanations = {
        "PROD-FIBER-1000": {
            "product": "Indian Super Combo: 1Gbps Fiber + Unlimited Truly 5G",
            "confidence_score": 0.984,
            "matched_rules": [
                f"Connected Device Count ({customer['connected_devices']} devices) > 10 Threshold",
                "High 4K Video Bandwidth Usage (Hotstar / SonyLIV / JioCinema)",
                "Gold Loyalty Tier Discount Eligible (15% Off Base Tariff)"
            ],
            "customer_benefit": "Eliminates evening buffering, includes free Disney+ Hotstar & SonyLIV",
            "omnichannel_status": "Synced across OneShop Web and OneApp Mobile"
        },
        "PROD-MESH-BOOSTER": {
            "product": "Smart WiFi 6 Mesh Extender (Indian Apartments Special)",
            "confidence_score": 0.968,
            "matched_rules": [
                f"Signal Strength in Master Bedroom ({customer['signal_strength']}) below -70 dBm threshold",
                "High wall density detected in Indian apartment layout"
            ],
            "customer_benefit": "Boosts room coverage to 100% full 5GHz speed",
            "omnichannel_status": "Ready for 1-click UPI checkout"
        }
    }
    explanation = explanations.get(product_id, explanations["PROD-FIBER-1000"])
    return json.dumps(explanation, indent=2)

@tool
def optimize_smart_cart(customer_id: str = "CUST-101") -> str:
    """
    Smart Cart & Checkout Optimizer: Evaluates current cart items for Indian subscribers, 
    calculates 18% GST, applies bundle discounts, and returns final payable amounts.
    """
    customer = MOCK_CUSTOMERS.get(customer_id, MOCK_CUSTOMERS["CUST-101"])
    cart = customer.get("cart", [])

    base_subtotal = sum(item["price"] for item in cart)
    discount = 0.0
    bundle_nudge = None

    has_plan = any(item["type"] == "Plan" for item in cart)
    has_addon = any(item["type"] == "Add-on" for item in cart)

    if has_plan and has_addon:
        discount = 150.0
        bundle_nudge = "🎉 Multi-Product Bundle Discount Applied (-₹150.00/mo)"

    net_base = max(0.0, base_subtotal - discount)
    gst_amount = net_base * 0.18
    grand_total = net_base + gst_amount

    return json.dumps({
        "customer_id": customer_id,
        "cart_items": cart,
        "subtotal_base": f"₹{base_subtotal:.2f}",
        "bundle_discount": f"₹{discount:.2f}",
        "gst_18_percent": f"₹{gst_amount:.2f}",
        "total": f"₹{grand_total:.2f}",
        "applied_nudge": bundle_nudge,
        "upi_payment_ready": True
    }, indent=2)

import chromadb
import hashlib
import math
from chromadb.api.types import EmbeddingFunction

class FastVectorEF(EmbeddingFunction):
    def __init__(self):
        super().__init__()
    def name(self):
        return "dtdl_fast_vector_ef"
    def __call__(self, input):
        vecs = []
        for text in input:
            tokens = text.lower().split()
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
    if _chroma_collection is None:
        try:
            _chroma_client = chromadb.Client()
            _chroma_collection = _chroma_client.get_or_create_collection(
                name="dtdl_telecom_rag",
                embedding_function=FastVectorEF()
            )
            if _chroma_collection.count() == 0:
                kb_docs = [
                    "If speeds fall below 50% of subscribed rate, inspect 2.4GHz vs 5GHz channel interference. Switching from Channel 6 to Channel 11 resolves 80% of local congestion in high-density urban apartments across Delhi NCR, Mumbai, and Bengaluru.",
                    "Per TRAI regulations, value-added services billed without explicit double-opt-in SMS confirmation must be refunded within 24 hours via instant UPI credit (GPay / PhonePe / Paytm) or bill balance adjustment.",
                    "Minimum 25 Mbps broadband bandwidth required for 4K UHD HDR streaming. Connect Smart TV Box via direct Ethernet cable or 5GHz WiFi Mesh."
                ]
                kb_metadatas = [
                    {"title": "WiFi Speed Optimization & 5GHz Channel Setup in Indian Apartments", "category": "Broadband Diagnostics"},
                    {"title": "TRAI Consent Guidelines & Instant UPI Refund SLA", "category": "Billing & Compliance"},
                    {"title": "Hotstar, SonyLIV & Magenta TV 4K UHD Streaming Requirements", "category": "OTT Entertainment"}
                ]
                _chroma_collection.add(
                    documents=kb_docs,
                    metadatas=kb_metadatas,
                    ids=["doc-01", "doc-02", "doc-03"]
                )
        except Exception as e:
            print(f"[WARNING] ChromaDB Vector Store fallback active: {e}")
    return _chroma_collection

@tool
def retrieve_kb_articles(query: str) -> str:
    """
    RAG Retriever: Queries ChromaDB vector store collection using vector embeddings
    over Indian Telecom knowledge base articles, TRAI SLA terms, and streaming FAQs.
    """
    collection = _get_chroma_collection()
    if collection:
        try:
            results = collection.query(query_texts=[query], n_results=2)
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
                return json.dumps({"rag_engine": "ChromaDB Vector Search Engine", "kb_results": vector_docs}, indent=2)
        except Exception as e:
            print(f"ChromaDB query error: {e}")

    # Fallback keyword match if ChromaDB unavailable
    kb = [
        {
            "title": "WiFi Speed Optimization & 5GHz Channel Setup in Indian Apartments",
            "category": "Broadband Diagnostics",
            "content": "If speeds fall below 50% of subscribed rate, inspect 2.4GHz vs 5GHz channel interference. Switching from Channel 6 to Channel 11 resolves 80% of local congestion in high-density urban apartments across Delhi NCR, Mumbai, and Bengaluru."
        },
        {
            "title": "TRAI Consent Guidelines & Instant UPI Refund SLA",
            "category": "Billing & Compliance",
            "content": "Per TRAI regulations, value-added services billed without explicit double-opt-in SMS confirmation must be refunded within 24 hours via instant UPI credit (GPay / PhonePe / Paytm) or bill balance adjustment."
        }
    ]
    return json.dumps({"rag_engine": "ChromaDB Fallback Engine", "kb_results": kb}, indent=2)


# Tool collections grouped by agent domain
NETWORK_TOOLS = [check_router_diagnostics, reboot_router, retrieve_kb_articles]
BILLING_TOOLS = [fetch_billing_statement, apply_bill_credit, retrieve_kb_articles]
PLAN_TOOLS = [search_plan_catalog, get_explainable_recommendation, optimize_smart_cart, retrieve_kb_articles]
ALL_TOOLS = NETWORK_TOOLS + BILLING_TOOLS + PLAN_TOOLS



