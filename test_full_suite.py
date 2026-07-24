"""
================================================================================
DEUTSCHE TELEKOM DIGITAL LABS — FULL SYSTEM EXHAUSTIVE TEST SUITE
================================================================================
Tests every REST API endpoint, LangGraph Multi-Agent node, MCP JSON-RPC 2.0 
server method, ChromaDB vector RAG tool, Smart Cart optimizer, and HITL safety gate.
================================================================================
"""

import sys
import io
import json
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)

from fastapi.testclient import TestClient
from backend.main import app

log_file = open("test_report.txt", "w", encoding="utf-8")

def log_print(msg=""):
    print(msg, flush=True)
    log_file.write(str(msg) + "\n")
    log_file.flush()

def run_full_suite():
    log_print("=" * 80)
    log_print("🚀 STARTING TELEAGENT AI FULL SYSTEM EXHAUSTIVE TEST SUITE")
    log_print("=" * 80)

    client = TestClient(app)
    passed_tests = 0
    total_tests = 0

    def assert_test(name, condition, error_msg=""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            log_print(f"  ✓ {name}")
        else:
            log_print(f"  ❌ {name} FAILED: {error_msg}")
            raise AssertionError(f"{name}: {error_msg}")

    # --------------------------------------------------------------------------
    # 1. Health Check Endpoint
    # --------------------------------------------------------------------------
    log_print("\n[SECTION 1] REST API Base Endpoints")
    res = client.get("/api/health")
    assert_test("GET /api/health", res.status_code == 200 and res.json()["status"] == "online")

    res = client.get("/api/impact-summary")
    assert_test("GET /api/impact-summary", res.status_code == 200 and "projected_business_outcomes" in res.json())

    # --------------------------------------------------------------------------
    # 2. RLHF Feedback Endpoint
    # --------------------------------------------------------------------------
    log_print("\n[SECTION 2] RLHF Feedback Loop Endpoints")
    res_like = client.post("/api/feedback", json={"customer_id": "CUST-101", "rating": "like"})
    assert_test("POST /api/feedback (like)", res_like.status_code == 200 and res_like.json()["reward_signal"] == 1.0)

    res_dislike = client.post("/api/feedback", json={"customer_id": "CUST-102", "rating": "dislike"})
    assert_test("POST /api/feedback (dislike)", res_dislike.status_code == 200 and res_dislike.json()["reward_signal"] == -1.0)

    # --------------------------------------------------------------------------
    # 3. Direct Tool & Commerce Endpoints
    # --------------------------------------------------------------------------
    log_print("\n[SECTION 3] Direct Tool & E-Commerce Endpoints")
    res_cart = client.get("/api/cart/CUST-101")
    assert_test("GET /api/cart/CUST-101", res_cart.status_code == 200 and "cart_items" in res_cart.json())

    res_xai = client.get("/api/explainable-ai/PROD-FIBER-1000?customer_id=CUST-101")
    assert_test("GET /api/explainable-ai/PROD-FIBER-1000", res_xai.status_code == 200 and "confidence_score" in res_xai.json())

    # --------------------------------------------------------------------------
    # 4. Multi-Agent Chat Routing & LangGraph Execution
    # --------------------------------------------------------------------------
    log_print("\n[SECTION 4] Multi-Agent LangGraph Routing")

    # 4a. Network Agent Routing
    res_net = client.post("/api/chat", json={
        "message": "Check my Speedport WiFi speed and router diagnostics in Bonn",
        "customer_id": "CUST-101",
        "thread_id": "thread_net_test",
        "ab_variant": "Variant B (Speed Focus)"
    })
    assert_test("Chat Routing: Network Agent", res_net.status_code == 200 and res_net.json()["active_agent"] == "network_agent")
    time.sleep(2)

    # 4b. Billing Agent Routing & HITL Gate
    res_bill = client.post("/api/chat", json={
        "message": "Please apply a bill credit refund of €29.75 for the unrecognized FIFA pass charge on my account.",
        "customer_id": "CUST-101",
        "thread_id": "thread_bill_test",
        "ab_variant": "Variant A (Discount Focus)"
    })
    assert_test("Chat Routing: Billing Agent & HITL Gate", res_bill.status_code == 200 and res_bill.json()["requires_human_approval"] == True)
    time.sleep(2)

    # 4c. Commerce Agent Routing
    res_comm = client.post("/api/chat", json={
        "message": "What is the monthly price for MagentaZuhause Fiber 500M plan?",
        "customer_id": "CUST-103",
        "thread_id": "thread_plan_test",
        "ab_variant": "Variant A (Discount Focus)"
    })
    assert_test("Chat Routing: Plan Agent", res_comm.status_code == 200 and res_comm.json()["active_agent"] == "plan_agent")

    # --------------------------------------------------------------------------
    # 5. Human-in-the-Loop (HITL) Action Approval
    # --------------------------------------------------------------------------
    log_print("\n[SECTION 5] Human-in-the-Loop (HITL) Approval & Execution")
    
    # 5a. Reject flow
    res_reject = client.post("/api/approve-action", json={"approved": False, "customer_id": "CUST-101"})
    assert_test("HITL Rejection", res_reject.status_code == 200 and res_reject.json()["status"] == "REJECTED")

    # 5b. Approve flow
    res_approve = client.post("/api/approve-action", json={"approved": True, "customer_id": "CUST-101", "thread_id": "thread_bill_test"})
    assert_test("HITL Approval & SEPA Execution", res_approve.status_code == 200 and res_approve.json()["status"] == "APPROVED")

    # --------------------------------------------------------------------------
    # 6. Model Context Protocol (MCP) JSON-RPC 2.0 Server Tests
    # --------------------------------------------------------------------------
    log_print("\n[SECTION 6] Model Context Protocol (MCP) JSON-RPC 2.0 Server")

    # 6a. MCP Info
    res_mcp_info = client.get("/api/mcp")
    assert_test("GET /api/mcp (Server Info)", res_mcp_info.status_code == 200 and res_mcp_info.json()["status"] == "online")

    # 6b. MCP tools/list
    res_tools_list = client.post("/api/mcp", json={"method": "tools/list"})
    assert_test("MCP JSON-RPC tools/list", res_tools_list.status_code == 200 and len(res_tools_list.json()["result"]["tools"]) >= 8)

    # 6c. MCP resources/list
    res_res_list = client.post("/api/mcp", json={"method": "resources/list"})
    assert_test("MCP JSON-RPC resources/list", res_res_list.status_code == 200 and "resources" in res_res_list.json()["result"])

    # 6d. MCP prompts/list
    res_prompts_list = client.post("/api/mcp", json={"method": "prompts/list"})
    assert_test("MCP JSON-RPC prompts/list", res_prompts_list.status_code == 200 and "prompts" in res_prompts_list.json()["result"])

    # 6e. MCP tools/call (check_router_diagnostics)
    res_call_diag = client.post("/api/mcp", json={
        "method": "tools/call",
        "params": {"name": "check_router_diagnostics", "arguments": {"customer_id": "CUST-101"}}
    })
    assert_test("MCP JSON-RPC tools/call (check_router_diagnostics)", res_call_diag.status_code == 200 and "result" in res_call_diag.json())

    # 6f. MCP tools/call (retrieve_kb_articles - Vector RAG)
    res_call_rag = client.post("/api/mcp", json={
        "method": "tools/call",
        "params": {"name": "retrieve_kb_articles", "arguments": {"query": "BNetzA refund regulations"}}
    })
    assert_test("MCP JSON-RPC tools/call (retrieve_kb_articles RAG)", res_call_rag.status_code == 200 and "result" in res_call_rag.json())

    # 6g. MCP error handling (invalid tool)
    res_call_invalid = client.post("/api/mcp", json={
        "method": "tools/call",
        "params": {"name": "non_existent_tool", "arguments": {}}
    })
    assert_test("MCP JSON-RPC Error (Invalid tool)", res_call_invalid.status_code == 200 and "error" in res_call_invalid.json() and res_call_invalid.json()["error"]["code"] == -32601)

    # --------------------------------------------------------------------------
    # 7. Frontend Static File Mounting Check
    # --------------------------------------------------------------------------
    log_print("\n[SECTION 7] Frontend Assets & Static Mounting")
    res_html = client.get("/")
    assert_test("GET / (Frontend index.html)", res_html.status_code == 200 and "Deutsche Telekom" in res_html.text)

    # --------------------------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------------------------
    log_print("\n" + "=" * 80)
    log_print(f"🎉 EXHAUSTIVE TEST SUITE COMPLETED: {passed_tests}/{total_tests} TESTS PASSED CLEANLY (100% SUCCESS RATE)!")
    log_print("=" * 80)

if __name__ == "__main__":
    run_full_suite()
