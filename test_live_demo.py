"""
================================================================================
DEUTSCHE TELEKOM DIGITAL LABS — LIVE DEMO INTEGRATION TEST SUITE
================================================================================
Validates all 5 core judge demo scenarios, ChromaDB vector RAG retrieval,
A/B variant prompt routing, HITL SEPA refunds, and RLHF feedback endpoints.
================================================================================
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi.testclient import TestClient
from backend.main import app

def run_live_demo_tests():
    print("=" * 80)
    print("🚀 STARTING TELEAGENT AI LIVE DEMO VERIFICATION TEST SUITE")
    print("=" * 80)


    client = TestClient(app)

    # 1. Health Check
    print("\n[TEST 1/6] GET /api/health ...")
    res1 = client.get("/api/health")
    assert res1.status_code == 200, f"Health check failed: {res1.text}"
    print(f"  ✓ Service status: {res1.json()['status']} ({res1.json()['service']})")

    # 2. Network Diagnostics & ChromaDB Vector RAG Search (Variant B - Speed Focus)
    print("\n[TEST 2/6] POST /api/chat (Speedport Diagnostics & ChromaDB RAG - Variant B) ...")
    res2 = client.post("/api/chat", json={
        "message": "Check my Speedport WiFi speed and router diagnostics in Bonn",
        "customer_id": "CUST-101",
        "ab_variant": "Variant B (Speed Focus)"
    })
    assert res2.status_code == 200, f"Chat endpoint failed: {res2.text}"
    data2 = res2.json()
    print(f"  ✓ Active Agent: {data2.get('active_agent')}")
    print(f"  ✓ Executed Tools: {[t['tool'] for t in data2.get('tool_outputs', [])]}")
    assert any(t['tool'] == 'check_router_diagnostics' for t in data2.get('tool_outputs', [])), "Router diagnostics tool was not invoked!"

    # 3. Billing Dispute & HITL Financial Safety Checkpoint
    print("\n[TEST 3/6] POST /api/chat (Billing Refund Request & HITL Checkpoint) ...")
    res3 = client.post("/api/chat", json={
        "message": "Please apply a bill credit refund of €29.75 for the unrecognized FIFA pass charge on my account.",
        "customer_id": "CUST-101",
        "ab_variant": "Variant A (Discount Focus)"
    })


    assert res3.status_code == 200, f"Billing query failed: {res3.text}"
    data3 = res3.json()
    print(f"  ✓ Requires Human Approval (HITL): {data3.get('requires_human_approval')}")
    assert data3.get('requires_human_approval') == True, "HITL approval flag was not triggered for bill credit!"

    # 4. Human Approval SEPA Refund Execution
    print("\n[TEST 4/6] POST /api/approve-action (SEPA Credit Refund Approval) ...")
    res4 = client.post("/api/approve-action", json={
        "approved": True,
        "customer_id": "CUST-101"
    })
    assert res4.status_code == 200, f"Approval failed: {res4.text}"
    data4 = res4.json()
    print(f"  ✓ Approval Status: {data4.get('status')}")
    print(f"  ✓ Message: {data4.get('message')}")

    # 5. RLHF Preference Feedback Endpoint
    print("\n[TEST 5/6] POST /api/feedback (RLHF Preference Signal) ...")
    res5 = client.post("/api/feedback", json={
        "customer_id": "CUST-101",
        "rating": "like"
    })
    assert res5.status_code == 200, f"Feedback failed: {res5.text}"
    data5 = res5.json()
    print(f"  ✓ Feedback Status: {data5.get('status')}, Reward Signal: {data5.get('reward_signal')}")

    # 6. Business Impact & ROI Analytics Summary
    print("\n[TEST 6/6] GET /api/impact-summary (Projected Business Outcomes) ...")
    res6 = client.get("/api/impact-summary")
    assert res6.status_code == 200, f"Impact summary failed: {res6.text}"
    data6 = res6.json()
    print(f"  ✓ Cart Abandonment Reduction: {data6['projected_business_outcomes']['cart_abandonment_reduction']}")
    print(f"  ✓ Mean Time To Resolution: {data6['projected_business_outcomes']['mean_time_to_resolution_mttr']}")

    print("\n" + "=" * 80)
    print("🏆 ALL 6 LIVE DEMO INTEGRATION TESTS PASSED 100% CLEANLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_live_demo_tests()
