import json
import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from backend.tools.telecom_tools import MOCK_CUSTOMERS, optimize_smart_cart

CONVERSION_EVENTS: list[dict] = []
ABANDONMENT_EVENTS: list[dict] = []

PaymentMethod = Literal["upi", "card", "netbanking"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_cart_summary(customer_id: str) -> dict:
    raw = optimize_smart_cart.invoke({"customer_id": customer_id})
    return json.loads(raw)


def get_checkout_preview(customer_id: str) -> dict:
    """Step 1 + 2: cart review + bundle optimization."""
    customer = MOCK_CUSTOMERS.get(customer_id)
    if not customer:
        raise ValueError(f"Unknown customer_id: {customer_id}")

    cart_summary = _parse_cart_summary(customer_id)
    items = cart_summary.get("cart_items", [])

    if not items:
        return {
            "step": "cart_review",
            "customer_id": customer_id,
            "status": "empty_cart",
            "message": "Cart is empty. Add a plan or add-on before checkout.",
            "cart_summary": cart_summary,
        }

    suggestions = []
    has_plan = any(i["type"] == "Plan" for i in items)
    has_addon = any(i["type"] == "Add-on" for i in items)

    if has_plan and not has_addon:
        suggestions.append({
            "type": "bundle_nudge",
            "message": "Add Smart WiFi Mesh Extender (₹149/mo) to unlock ₹150 bundle discount.",
            "product_id": "PROD-MESH-BOOSTER",
        })
    if has_plan and has_addon:
        suggestions.append({
            "type": "already_optimized",
            "message": "Cart already qualifies for bundle pricing.",
        })

    return {
        "step": "bundle_optimization",
        "customer_id": customer_id,
        "status": "ready",
        "subscriber": {
            "name": customer["name"],
            "loyalty_tier": customer.get("loyalty_tier", "Standard"),
            "upi_id": customer.get("upi_id"),
        },
        "cart_summary": cart_summary,
        "bundle_suggestions": suggestions,
        "checkout_steps": ["cart_review", "bundle_optimization", "payment", "confirmation"],
    }


def complete_checkout(
    customer_id: str,
    payment_method: PaymentMethod = "upi",
    upi_id: Optional[str] = None,
    channel: str = "OneShop Web",
) -> dict:
    """Step 3 + 4: mock payment + confirmation + clear cart."""
    preview = get_checkout_preview(customer_id)
    if preview.get("status") == "empty_cart":
        raise ValueError("Cannot checkout with an empty cart")

    customer = MOCK_CUSTOMERS[customer_id]
    cart_summary = preview["cart_summary"]
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    txn_id = f"TXN-UPI-{uuid.uuid4().hex[:8].upper()}"

    resolved_upi = upi_id or customer.get("upi_id", "customer@upi")

    payment_result = {
        "status": "SUCCESS",
        "payment_method": payment_method,
        "upi_id": resolved_upi if payment_method == "upi" else None,
        "transaction_id": txn_id,
        "amount_paid": cart_summary.get("total", "₹0.00"),
        "timestamp": _now_iso(),
    }

    purchased_items = list(customer.get("cart", []))
    customer["cart"] = []

    event = {
        "event_type": "conversion",
        "order_id": order_id,
        "customer_id": customer_id,
        "channel": channel,
        "items_purchased": purchased_items,
        "payment": payment_result,
        "cart_total": cart_summary.get("total"),
        "timestamp": _now_iso(),
    }
    CONVERSION_EVENTS.append(event)

    return {
        "step": "confirmation",
        "status": "completed",
        "order_id": order_id,
        "message": f"Order {order_id} confirmed! Payment of {cart_summary.get('total')} received.",
        "payment": payment_result,
        "purchased_items": purchased_items,
        "conversion_event": event,
    }


def log_abandonment_nudge(
    customer_id: str,
    channel: str = "OneShop Web",
    seconds_open: int = 30,
) -> dict:
    """Log cart abandonment + return proactive NBA nudge."""
    preview = get_checkout_preview(customer_id)
    cart_summary = preview.get("cart_summary", {})
    total = cart_summary.get("total", "₹0.00")

    nudge = {
        "title": "Complete your order and save!",
        "message": (
            f"Your cart ({total}) is waiting. "
            "Complete checkout now to lock in bundle pricing before it expires."
        ),
        "action": "resume_checkout",
        "discount_hint": "Extra ₹50 off if you checkout in the next 10 minutes (demo nudge).",
    }

    event = {
        "event_type": "cart_abandonment_nudge",
        "customer_id": customer_id,
        "channel": channel,
        "seconds_in_cart": seconds_open,
        "cart_total": total,
        "nudge": nudge,
        "timestamp": _now_iso(),
    }
    ABANDONMENT_EVENTS.append(event)

    return {"status": "nudge_sent", "nudge": nudge, "event": event}


def get_checkout_events(customer_id: Optional[str] = None) -> dict:
    """Debug/testing helper."""
    conversions = CONVERSION_EVENTS
    abandonments = ABANDONMENT_EVENTS
    if customer_id:
        conversions = [e for e in conversions if e["customer_id"] == customer_id]
        abandonments = [e for e in abandonments if e["customer_id"] == customer_id]
    return {
        "conversions": conversions,
        "abandonments": abandonments,
        "conversion_count": len(conversions),
        "abandonment_count": len(abandonments),
    }
